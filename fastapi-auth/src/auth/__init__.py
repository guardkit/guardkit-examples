"""
Authentication module for JWT-based user authentication.

Provides user login, token refresh, and logout endpoints with rate limiting.
"""

from src.auth.exceptions import AuthenticationError, AuthorizationError
from src.auth.router import router
from src.auth.schemas import LoginRequest, RefreshRequest
from src.auth.service import authenticate_user, login_user

__all__ = [
    "router",
    "authenticate_user",
    "login_user",
    "LoginRequest",
    "RefreshRequest",
    "AuthenticationError",
    "AuthorizationError",
]
