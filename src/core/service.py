from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import async_sessionmaker

from typing import Type

from src.core.models import Base as BaseModel
from src.db.engine import engine
from src.core.meta import base_metadata


class BaseService:

    async def create(self, model: Type[BaseModel], values: dict):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        res = False
        stmt = insert(model).values(values).returning(model)
        async with async_session() as session:
            async with session.begin():
                try:
                    res = await session.execute(stmt)
                except Exception:
                    await session.rollback()
                else:
                    await session.commit()
        await engine.dispose()
        if res:
            return res.scalar_one()
        return res

