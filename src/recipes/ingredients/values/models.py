from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models import Base


class RecipeIngredientValue(Base):
    __tablename__ = 'recipes_ingredients_values'

    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipes.id'), primary_key=True, nullable=False)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('recipes_ingredients.id'), primary_key=True, nullable=False)
