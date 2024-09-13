import logging
from typing import AsyncGenerator

import asyncpg
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database.database import get_async_session
from src.database.models.base import Base
from src.main import app

logger = logging.getLogger(__name__)

DB = settings.DB
DB_URL = f"postgresql://{DB.USERNAME_TEST}:{DB.PASSWORD_TEST}@{DB.HOST_TEST}:{DB.PORT_TEST}"
DB_URL_TEST = f"postgresql+asyncpg://{DB.USERNAME_TEST}:{DB.PASSWORD_TEST}@{DB.HOST_TEST}:{DB.PORT_TEST}/{DB.NAME_TEST}"

engine_test = create_async_engine(DB_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test
client = TestClient(app)


async def create_database():
    conn = await asyncpg.connect(DB_URL)
    try:
        await conn.execute(f"CREATE DATABASE test")
    except asyncpg.DuplicateDatabaseError:
        logger.info("Database already exists")
    finally:
        await conn.close()


async def drop_database():
    conn = await asyncpg.connect(DB_URL)
    try:
        await conn.execute(f"DROP DATABASE IF EXISTS test")
    finally:
        await conn.close()


async def override_get_async_session() -> AsyncSession | None:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    await create_database()
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await drop_database()


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver"
    ) as ac:
        yield ac
