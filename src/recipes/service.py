from fastapi import Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Optional
from src.db.engine import engine
from src.core.service import BaseService
from src.recipes.models import Recipe
from src.recipes.schemas import RecipeCreateRequest, RecipeUpdateRequest
from src.users.service import user_service, oauth2_scheme
from src.recipes.categories.values.models import RecipeCategoryValue
from src.recipes.ingredients.values.models import RecipeIngredientValue


class RecipesService(BaseService):
    async def add_recipe(self, data: RecipeCreateRequest, token: str = Depends(oauth2_scheme)):
        user = await user_service.get_current(token=token)
        if not user:
            raise HTTPException(status_code=500, detail='Unknown error on recipe service')
        values = data.model_dump()
        categories = values['categories']
        ingredients = values['ingredients']

        values.update({'author_id': user.id})
        del values['categories']
        del values['ingredients']

        result = await self.create(model=Recipe, values=values)
        if result:
            for i in categories:
                await self.create(model=RecipeCategoryValue, values={
                    'recipe_id': result.id,
                    'category_id': i
                })
            for i in ingredients:
                await self.create(model=RecipeIngredientValue, values={
                    'recipe_id': result.id,
                    'ingredient_id': i
                })
            return result
        raise HTTPException(status_code=500, detail='Unknown error on recipe service')

    async def list(self):
        res = await self.get_list()
        return res

    async def get_list(self, filters: dict | None = None):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        res = []
        stmt = select(Recipe)
        if filters:
            if filters['categories']:
                stmt = stmt.filter(Recipe.categories.any(RecipeCategoryValue.category_id.in_(filters['categories'])))
            if filters['cooking_time']:
                stmt = stmt.filter(Recipe.cooking_time == filters['cooking_time'])
        async with async_session() as session:
            row = await session.execute(stmt)
            try:
                res = row.scalars()
            except Exception:
                return []
        return res

    async def get_by_id(self, recipe_id: int):
        recipe = await self.get_one(model=Recipe, filter={'id': recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail='Recipe not found')
        return recipe

    async def delete_category(self, recipe_id: int, cat_id: int):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        stmt = (delete(RecipeCategoryValue)
                .where(RecipeCategoryValue.recipe_id == recipe_id)
                .where(RecipeCategoryValue.category_id == cat_id)
                )
        async with async_session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete_ingredient(self, recipe_id: int, ingr_id: int):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        stmt = (delete(RecipeIngredientValue)
                .where(RecipeIngredientValue.recipe_id == recipe_id)
                .where(RecipeIngredientValue.ingredient_id == ingr_id)
                )
        async with async_session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_recipe(self, recipe_id: int, data: RecipeUpdateRequest, token: str = Depends(oauth2_scheme)):
        current_recipe = await self.get_by_id(recipe_id=recipe_id)
        user = await user_service.get_current(token=token)
        if not user:
            raise HTTPException(status_code=401, detail='Unauthorized')
        if user.id != current_recipe.author_id:
            raise HTTPException(status_code=403, detail='Access denied. You can edit only your own recipes')

        values = data.model_dump()
        new_values = {}
        current_categories = list(map(lambda item: item.id, current_recipe.categories))
        current_ingredients = list(map(lambda item: item.id, current_recipe.ingredients))
        for field in values:
            if not values[field]:
                continue

            if field == 'categories':
                for i in values[field]:
                    if i in current_categories:
                        continue
                    await self.create(model=RecipeCategoryValue, values={
                        'recipe_id': recipe_id,
                        'category_id': i
                    })

                for i in current_categories:
                    if i in values[field]:
                        continue
                    await self.delete_category(recipe_id=recipe_id, cat_id=i)

            elif field == 'ingredients':
                for i in values[field]:
                    if i in current_ingredients:
                        continue
                    await self.create(model=RecipeIngredientValue, values={
                        'recipe_id': recipe_id,
                        'ingredient_id': i
                    })

                for i in current_ingredients:
                    if i in values[field]:
                        continue
                    await self.delete_ingredient(recipe_id=recipe_id, ingr_id=i)

            else:
                new_values[field] = values[field]

        if new_values:
            return await self.update(model=Recipe, pk=recipe_id, values=new_values)
        raise HTTPException(status_code=500, detail='Server error')

    async def filter(self, time: int | None = None, categories: Optional[list] = None):
        res = await self.get_list(filters={
            'cooking_time': time,
            'categories': categories
        })
        return res


recipes_service = RecipesService()
