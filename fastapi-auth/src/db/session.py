"""
Database session management and connection setup.

Provides async database session factory and session generator.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.

    Yields:
        AsyncSession: Database session that will be closed automatically.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Alias for get_async_session for convenience.

    Yields:
        AsyncSession: Database session.
    """
    async for session in get_async_session():
        yield session
