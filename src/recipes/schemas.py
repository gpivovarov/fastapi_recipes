from pydantic import BaseModel
from src.users.schemas import User
from src.recipes.categories.schemas import RecipeCategory
from src.recipes.ingredients.schemas import RecipeIngredient


class RecipeCreateRequest(BaseModel):
    title: str
    description: str
    cooking_time: int


class RecipeCreateResponse(BaseModel):
    id: int | None = None


class RecipeResponse(RecipeCreateRequest, RecipeCreateResponse):
    author: User
    categories: list[RecipeCategory]
    ingredients: list[RecipeIngredient]
