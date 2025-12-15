"""
Shared test configuration and fixtures.

Provides database fixtures, test client, and common test data.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.security import hash_password
from src.db.base import Base
from src.main import app
from src.users.models import User


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        # Rollback any pending transactions
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client with overridden dependencies."""
    from src.core.dependencies import get_db

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        hashed_password=hash_password("SecurePass"),
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_inactive_user(test_session: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("SecurePass"),
        is_active=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user_token(test_user: User) -> str:
    """Create a test access token for test user."""
    from src.core.security import create_access_token

    return create_access_token(user_id=test_user.id)


@pytest_asyncio.fixture(scope="function")
async def test_refresh_token(test_user: User) -> str:
    """Create a test refresh token for test user."""
    from src.core.security import create_refresh_token

    return create_refresh_token(user_id=test_user.id)
