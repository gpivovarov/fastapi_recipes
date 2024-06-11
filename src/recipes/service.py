from fastapi import Depends, HTTPException
from src.core.service import BaseService
from src.recipes.models import Recipe
from src.recipes.schemas import RecipeCreateRequest
from src.users.service import user_service, oauth2_scheme

class RecipesService(BaseService):
    async def add_recipe(self, data: RecipeCreateRequest, token: str = Depends(oauth2_scheme)):
        user = await user_service.get_current(token=token)
        if not user:
            raise HTTPException(status_code=500, detail='Unknown error on recipe service')
        values = data.model_dump()
        values.update({'author_id': user.id})
        result = await self.create(model=Recipe, values=values)
        if result:
            return result
        raise HTTPException(status_code=500, detail='Unknown error on recipe service')

    async def list(self):
        res = await self.get_list(model=Recipe)
        return res

    async def get_by_id(self, recipe_id: int):
        recipe = await self.get_one(model=Recipe, filter={'id': recipe_id})
        print(recipe.__dict__)
        return recipe

    # async def login(self, data: UserLogin):
    #     user = await self.get_one(model=User, filter={'email': data.email})
    #     if not user:
    #         raise HTTPException(status_code=404, detail='User not found')
    #     if argon2.verify(data.password, user.password):
    #         return {'access_token': self.create_access_token(data=data.model_dump())}
    #     raise HTTPException(status_code=200, detail='Wrong password')
    #
    # async def get_current(self, token: str = Depends(oauth2_scheme)):
    #     try:
    #         token_data = self.decode_access_token(token)
    #     except jwt.ExpiredSignatureError:
    #         raise HTTPException(status_code=401, detail='Access token has expired')
    #     except Exception as e:
    #         raise HTTPException(status_code=401, detail=f'Token error: {repr(e)}')
    #
    #     user = await self.get_one(model=User, filter={'email': token_data['email']})
    #     return user


recipes_service = RecipesService()
