from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import Base

class RecipeIngredient(Base):
    __tablename__ = 'recipes_ingredients'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    recipes: Mapped[list['Recipe']] = relationship(
        back_populates='ingredients',
        secondary='recipes_ingredients_values',
        lazy='selectin'
    )
