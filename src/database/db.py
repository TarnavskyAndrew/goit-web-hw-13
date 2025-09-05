from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
import contextlib
from contextlib import asynccontextmanager

from src.conf.config import settings

engine = create_async_engine(settings.async_db_url, future=True, echo=True)
SessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@contextlib.asynccontextmanager
async def session():
    async with SessionLocal() as s:
        try:
            yield s
        except:
            await s.rollback()
            raise
        finally:
            await s.close()


async def get_db():
    async with session() as s:
        yield s
