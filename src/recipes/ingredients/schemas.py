from pydantic import BaseModel


class RecipeIngredient(BaseModel):
    id: int
    name: str
