"""
Authentication domain schemas for request/response validation.

Defines Pydantic models for authentication API operations.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "your-secure-password",
            }
        }


class RefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }
