"""
Custom authentication and authorization exception classes.

Provides HTTP exceptions for authentication and authorization failures.
"""

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Raised when authentication fails (invalid credentials)."""

    def __init__(self, detail: str = "Invalid credentials"):
        """
        Initialize authentication error.

        Args:
            detail: Error message to return to client.
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Raised when user lacks required permissions."""

    def __init__(self, detail: str = "Insufficient permissions"):
        """
        Initialize authorization error.

        Args:
            detail: Error message to return to client.
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class InactiveUserError(AuthenticationError):
    """Raised when attempting to authenticate with an inactive user account."""

    def __init__(self) -> None:
        """Initialize inactive user error."""
        super().__init__(detail="Inactive user account")


class InvalidTokenError(AuthenticationError):
    """Raised when token validation fails."""

    def __init__(self, detail: str = "Invalid or expired token"):
        """
        Initialize invalid token error.

        Args:
            detail: Error message to return to client.
        """
        super().__init__(detail=detail)
