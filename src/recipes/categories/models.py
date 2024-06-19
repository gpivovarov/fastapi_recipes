from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import Base

class RecipeCategory(Base):
    __tablename__ = 'recipes_categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    recipes: Mapped[list['Recipe']] = relationship(
        back_populates='categories',
        secondary='recipes_categories_values',
        lazy='selectin'
    )
