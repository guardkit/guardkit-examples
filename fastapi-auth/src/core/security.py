"""
Security utilities for JWT token generation, validation, and password hashing.

Provides functions for:
- Creating and validating JWT tokens (access and refresh)
- Hashing and verifying passwords
"""

from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from .config import settings

# Password hashing context - use argon2 (OWASP recommended, bcrypt compatible API)
# Note: argon2 is preferred over bcrypt in modern applications
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str  # user_id as string (JWT spec requirement)
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    type: Literal["access", "refresh"]  # token type


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for the given user.

    Args:
        user_id: The ID of the user to create the token for.

    Returns:
        JWT access token as string.

    Raises:
        JWTError: If token creation fails.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),  # JWT spec requires subject to be string
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token for the given user.

    Args:
        user_id: The ID of the user to create the token for.

    Returns:
        JWT refresh token as string.

    Raises:
        JWTError: If token creation fails.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user_id),  # JWT spec requires subject to be string
        "exp": int(expires_at.timestamp()),
        "iat": int(now.timestamp()),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(
    token: str, expected_type: Literal["access", "refresh"]
) -> TokenPayload:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode.
        expected_type: Expected token type ("access" or "refresh").

    Returns:
        TokenPayload with decoded token claims.

    Raises:
        JWTError: If token is invalid, expired, malformed, or wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}") from e

    # Validate token structure and type
    try:
        token_payload = TokenPayload(**payload)
    except ValidationError as e:
        raise JWTError(f"Invalid token payload: {str(e)}") from e

    # Validate token type
    if token_payload.type != expected_type:
        raise JWTError(
            f"Invalid token type. Expected {expected_type}, got {token_payload.type}"
        )

    return token_payload


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to verify against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
