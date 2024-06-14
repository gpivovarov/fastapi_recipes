from pydantic import BaseModel


class RecipeCategory(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
