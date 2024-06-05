from sqlalchemy.ext.asyncio import create_async_engine
from src.db.config import config
from src.core.meta import base_metadata

engine = create_async_engine(
    url=config.url(),
    echo=True
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(base_metadata.drop_all)
        await conn.run_sync(base_metadata.create_all)
