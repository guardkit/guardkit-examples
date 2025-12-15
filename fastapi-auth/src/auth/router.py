"""
Authentication router with JWT login, refresh, and logout endpoints.

Provides API endpoints for user authentication and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginRequest, RefreshRequest
from src.auth.service import login_user
from src.core.config import settings
from src.core.schemas import Token
from src.core.security import decode_token
from src.core.dependencies import get_db
from src.users.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# OAuth2 scheme for token extraction
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_for_logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user for protected endpoints."""
    try:
        token_payload = decode_token(token, expected_type="access")
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    from src.users.crud import get_user_by_id

    user = await get_user_by_id(db, int(token_payload.sub))  # Convert string to int
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password, returns access and refresh tokens",
)
@limiter.limit(
    f"{settings.RATE_LIMIT_LOGIN_REQUESTS}/{settings.RATE_LIMIT_LOGIN_PERIOD_MINUTES}m"
)
async def login(
    request: Request,
    request_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate user and return JWT tokens.

    Rate limited to prevent brute force attacks:
    - {RATE_LIMIT_LOGIN_REQUESTS} requests per {RATE_LIMIT_LOGIN_PERIOD_MINUTES} minutes per IP

    Args:
        request: HTTP request object (required for rate limiting).
        request_data: Login credentials (email and password).
        db: Database session.

    Returns:
        Token object with access and refresh tokens.

    Raises:
        AuthenticationError: If credentials are invalid or user is inactive.
    """
    token = await login_user(db, email=request_data.email, password=request_data.password)
    return token


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Generate new access token using refresh token",
)
async def refresh(
    request_data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Generate new access token using a refresh token.

    Args:
        request_data: Refresh request with refresh token.
        db: Database session.

    Returns:
        Token object with new access token.

    Raises:
        InvalidTokenError: If refresh token is invalid or expired.
    """
    from src.core.security import create_access_token

    try:
        token_payload = decode_token(request_data.refresh_token, expected_type="refresh")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from e

    # Verify user still exists
    from src.users.crud import get_user_by_id

    user = await get_user_by_id(db, int(token_payload.sub))  # Convert string to int
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists or is inactive",
        )

    # Generate new access token
    new_access_token = create_access_token(user_id=user.id)

    return Token(access_token=new_access_token, refresh_token=request_data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User Logout",
    description="Logout user (stateless - client should discard tokens)",
)
async def logout(
    user: User = Depends(get_current_user_for_logout),
) -> Response:
    """
    Logout user endpoint.

    This is a stateless endpoint. The client is responsible for discarding the tokens.
    Future requests with discarded tokens will be rejected during authentication.

    Args:
        user: Current authenticated active user.

    Returns:
        Empty response with 204 No Content status.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
