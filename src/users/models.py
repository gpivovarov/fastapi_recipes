from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    recipes: Mapped[list['Recipe']] = relationship(back_populates='author', lazy='selectin')
