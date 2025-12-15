"""
CRUD operations for the User model.

Provides database query operations for user creation, retrieval, and updates.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.users.models import User
from src.users.schemas import UserCreate


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session.
        user_create: User creation schema with email and password.

    Returns:
        Created User object.
    """
    hashed_password = hash_password(user_create.password)
    db_user = User(email=user_create.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.flush()  # Flush to get the ID without committing
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Retrieve a user by email address.

    Args:
        db: Database session.
        email: User email to search for.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Retrieve a user by ID.

    Args:
        db: Database session.
        user_id: User ID to search for.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
