from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models import Base


class RecipeCategoryValue(Base):
    __tablename__ = 'recipes_categories_values'

    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipes.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('recipes_categories.id'), primary_key=True)
