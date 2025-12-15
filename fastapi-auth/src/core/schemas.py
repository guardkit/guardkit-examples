"""
Core schemas used across the application.

Includes token responses and shared data models.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT token response model."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: int = Field(..., description="Subject (user_id)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    type: Literal["access", "refresh"] = Field(..., description="Token type")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "sub": 1,
                "exp": 1704067200,
                "iat": 1704063600,
                "type": "access",
            }
        }
