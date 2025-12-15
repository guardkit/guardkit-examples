"""
Dependency injection functions for common request patterns.

Provides reusable dependencies for database sessions, authentication, and authorization.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_token
from src.db.session import get_async_session
from src.users.crud import get_user_by_id
from src.users.models import User

# OAuth2 scheme for extracting token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session for route handlers.

    Yields:
        AsyncSession: Database session for the request.
    """
    async for session in get_async_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from token.

    Validates the JWT token and retrieves the associated user from the database.

    Args:
        token: JWT access token from Authorization header.
        db: Database session.

    Returns:
        User object for the authenticated user.

    Raises:
        InvalidTokenError: If token is invalid or expired.
        HTTPException: If user not found in database.
    """
    try:
        token_payload = decode_token(token, expected_type="access")
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user_id = int(token_payload.sub)  # Convert string back to int
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user.

    Validates that the current user's account is active.

    Args:
        user: Current authenticated user.

    Returns:
        User object if account is active.

    Raises:
        HTTPException: If user account is inactive.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user
