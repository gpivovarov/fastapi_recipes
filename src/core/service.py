from sqlalchemy import insert, select, delete, update
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

    async def update(self, model: Type[BaseModel], values: dict, pk: int):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        stmt = update(model).where(model.id == pk).values(values).returning(model)
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

    async def get_one(self, model: Type[BaseModel], filter: dict):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        res = False
        stmt = select(model).filter_by(**filter)
        async with async_session() as session:
            row = await session.execute(stmt)
            try:
                res = row.scalar_one()
            except Exception:
                return False
        return res

    async def get_list(self, model: Type[BaseModel]):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        res = []
        stmt = select(model)
        async with async_session() as session:
            row = await session.execute(stmt)
            try:
                res = row.scalars().all()
            except Exception:
                return []
        return res

    async def delete(self, model: Type[BaseModel], pk: int):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        stmt = delete(model).where(model.id == pk)
        result = False
        async with async_session() as session:
            try:
                await session.execute(stmt)
                result = True
            except Exception:
                await session.rollback()
            else:
                await session.commit()
        await engine.dispose()
        return result

