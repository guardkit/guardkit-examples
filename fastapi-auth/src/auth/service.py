"""
Authentication business logic service.

Provides high-level authentication operations like user authentication and token generation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import AuthenticationError, InactiveUserError
from src.core.schemas import Token
from src.core.security import create_access_token, create_refresh_token, verify_password
from src.users.crud import get_user_by_email
from src.users.models import User


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """
    Authenticate a user by email and password.

    Args:
        db: Database session.
        email: User email address.
        password: Plain text password.

    Returns:
        User object if authentication succeeds, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    """
    Authenticate user and generate tokens.

    Verifies user credentials and checks that the account is active before
    generating access and refresh tokens.

    Args:
        db: Database session.
        email: User email address.
        password: Plain text password.

    Returns:
        Token object containing access and refresh tokens.

    Raises:
        AuthenticationError: If credentials are invalid.
        InactiveUserError: If user account is inactive.
    """
    user = await authenticate_user(db, email, password)

    if not user:
        raise AuthenticationError(detail="Invalid email or password")

    if not user.is_active:
        raise InactiveUserError()

    # Create tokens
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    return Token(access_token=access_token, refresh_token=refresh_token)
