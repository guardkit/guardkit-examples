"""
User domain schemas for request/response validation.

Defines Pydantic models for user-related API operations.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for user creation requests."""

    password: str = Field(
        ..., min_length=8, description="User password (minimum 8 characters)"
    )


class UserPublic(UserBase):
    """Schema for public user responses."""

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2024-12-14T12:00:00+00:00",
            }
        }


class UserInDB(UserBase):
    """Schema for user data as stored in database."""

    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True
