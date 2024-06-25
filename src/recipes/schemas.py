from pydantic import BaseModel
from src.users.schemas import User
from src.recipes.categories.schemas import RecipeCategory
from src.recipes.ingredients.schemas import RecipeIngredient


class RecipeCreateRequest(BaseModel):
    title: str
    description: str
    cooking_time: int
    categories: list[int]
    ingredients: list[int]


class RecipeCreateResponse(BaseModel):
    id: int | None = None


class RecipeResponse(RecipeCreateRequest, RecipeCreateResponse):
    author: User
    categories: list[RecipeCategory]
    ingredients: list[RecipeIngredient]


class RecipeUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    cooking_time: int | None = None
    categories: list[int] | None = None
    ingredients: list[int] | None = None


class RecipeDeleteResponse(BaseModel):
    success: bool
