from pydantic import BaseModel
from src.users.schemas import User


class RecipeCreateRequest(BaseModel):
    # id: int | None = None
    title: str
    description: str
    cooking_time: int


class RecipeCreateResponse(BaseModel):
    id: int | None = None


class RecipeResponse(RecipeCreateRequest, RecipeCreateResponse):
    author: User
    pass
