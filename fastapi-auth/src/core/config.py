"""
Core configuration for the application.

Includes JWT settings, database configuration, and other global settings.
"""

import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production-minimum-32-characters-required",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Application Settings
    APP_NAME: str = "FastAPI Auth API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "DEBUG" if DEBUG else "INFO"
    )

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname"
    )

    # Security
    BCRYPT_ROUNDS: int = 12

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_REQUESTS: int = 5
    RATE_LIMIT_LOGIN_PERIOD_MINUTES: int = 15

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True

    def __init__(self, **data):
        """Initialize settings and validate SECRET_KEY."""
        super().__init__(**data)
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long. "
                "Set SECRET_KEY environment variable."
            )


settings = Settings()
