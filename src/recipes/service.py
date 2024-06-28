import re
from fastapi import Depends, HTTPException
from sqlalchemy import delete, select, func, alias
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Optional
from src.db.engine import engine
from src.core.service import BaseService
from src.recipes.models import Recipe
from src.recipes.schemas import RecipeCreateRequest, RecipeUpdateRequest
from src.users.service import user_service, oauth2_scheme
from src.recipes.categories.models import RecipeCategory
from src.recipes.ingredients.models import RecipeIngredient
from src.recipes.categories.values.models import RecipeCategoryValue
from src.recipes.ingredients.values.models import RecipeIngredientValue


HTML_CLEANER_REGEX = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6}|\\t);')


class RecipesService(BaseService):

    async def add_recipe(self, data: RecipeCreateRequest, token: str = Depends(oauth2_scheme)):
        user = await user_service.get_current(token=token)
        if not user:
            raise HTTPException(status_code=500, detail='Unknown error on recipe service')
        values = data.model_dump()

        values.update({'author_id': user.id})

        categories = values['categories']
        ingredients = values['ingredients']
        del values['categories']
        del values['ingredients']

        searchable_text = values['title'].lower() + ' ' + re.sub(HTML_CLEANER_REGEX, '', values['description'].lower())
        if categories:
            categories_rows = await super().get_list(model=RecipeCategory)
            if categories_rows:
                searchable_text += ' '.join(row.name.lower() for row in categories_rows if row.id in categories)
        if ingredients:
            ingredients_rows = await super().get_list(model=RecipeIngredient)
            if ingredients_rows:
                searchable_text += ' '.join(row.name.lower() for row in ingredients_rows if row.id in ingredients)

        values.update({'searchable_content': searchable_text})

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

    async def list(self, page: int = 1, page_size: int = 10):
        res = await self.get_list(
            limit=page_size,
            offset=(page - 1) * page_size
        )
        return res

    async def get_list(self, filters: dict | None = None, limit: int = 10, offset: int = 0):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        res = []
        total_rows = 0
        subquery = select(func.count()).order_by(None).select_from(Recipe)
        stmt = select(Recipe)
        if filters:
            if filters['categories']:
                stmt = stmt.filter(Recipe.categories.any(RecipeCategoryValue.category_id.in_(filters['categories'])))
                subquery = subquery.filter(Recipe.categories.any(RecipeCategoryValue.category_id.in_(filters['categories'])))
            if filters['cooking_time']:
                stmt = stmt.filter(Recipe.cooking_time == filters['cooking_time'])
                subquery = subquery.filter(Recipe.cooking_time == filters['cooking_time'])
            if filters['query']:
                stmt = stmt.filter(func.to_tsvector('russian', Recipe.searchable_content).bool_op('@@')(
                    func.to_tsquery('russian', filters['query'].lower())
                ))
                subquery = subquery.filter(func.to_tsvector('russian', Recipe.searchable_content).bool_op('@@')(
                    func.to_tsquery('russian', filters['query'].lower())
                ))
        stmt = stmt.limit(limit).offset(offset)

        async with async_session() as session:
            # TODO: make a subquery
            rs_total = await session.execute(subquery)
            total_rows = rs_total.scalar()

            rs = await session.execute(stmt)
            items = []
            try:
                res = rs.scalars()
                if res:
                    for row in res:
                        row.description = f'{row.description[:25]}...'
                        items.append(row)
            except Exception:
                pass
        return {
            'items': items,
            'total': total_rows
        }

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

    async def filter(self, time: int | None = None, categories: Optional[list] = None, q: str | None = None, page: int = 1, page_size: int = 10):
        res = await self.get_list(filters={
            'cooking_time': time,
            'categories': categories,
            'query': q
            },
            limit=page_size,
            offset=(page - 1) * page_size
        )
        return res

    async def delete_recipe(self, recipe_id: int, token: str = Depends(oauth2_scheme)):
        user = await user_service.get_current(token=token)
        if not user:
            raise HTTPException(status_code=401, detail='Unauthorized')

        row = await self.get_by_id(recipe_id=recipe_id)
        if not row:
            raise HTTPException(status_code=404, detail='Recipe not found')

        if user.id != row.author_id:
            raise HTTPException(status_code=403, detail='Access denied')

        res = await self.delete(model=Recipe, pk=recipe_id)

        return {'success': res}


recipes_service = RecipesService()
