# TASK-3665 Code Structure Outline
## Detailed File Specifications and Code Organization

---

## 1. Core Security Module: `src/core/security.py`

### Purpose
Cryptographic operations for JWT token management and password hashing.

### Structure
```python
# Imports
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from src.config import settings

# Password context configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)

# 1. Token Payload Model
class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: str                                    # Subject (user ID)
    exp: int                                    # Expiration (unix timestamp)
    type: str                                   # Token type: "access" or "refresh"
    iat: int                                    # Issued at (unix timestamp)
    jti: str                                    # JWT ID (unique identifier)

    class Config:
        frozen = True  # Immutable

# 2. Password Management Functions
def get_password_hash(password: str) -> str:
    """Hash plaintext password using bcrypt"""
    # Returns hashed password string

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against hash"""
    # Returns True/False

# 3. JWT Token Functions
def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate JWT access token (30 min default)"""
    # Returns token string

def create_refresh_token(subject: str) -> str:
    """Generate JWT refresh token (7 days)"""
    # Returns token string

def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate JWT token"""
    # Returns TokenPayload or None on error (no exceptions)
```

### Key Principles
- Never raise exceptions for token validation (return None)
- Always use UTC timezone for expiry calculations
- Include jti (JWT ID) for token uniqueness
- Bcrypt cost factor enforced from settings

---

## 2. Core Dependencies: `src/core/dependencies.py`

### Purpose
FastAPI dependency functions for authentication and authorization.

### Structure
```python
# Imports
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.core.security import decode_token
from src.users.models import User
from src.users import crud as user_crud
from src.config import settings

# 1. OAuth2 Scheme Setup
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    description="JWT token from login endpoint"
)

# 2. Current User Dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate JWT token and return authenticated user.

    Raises:
        HTTPException(401): Invalid/expired token or user not found
    """
    # Decode token
    # Look up user
    # Return or raise 401

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure current user is active.

    Raises:
        HTTPException(403): User inactive
    """
    # Check current_user.is_active
    # Return or raise 403

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Optional authentication - returns user or None if no token.
    Useful for endpoints that work with or without auth.
    """
    # Decode token or return None
    # Return user or None

# 3. Optional OAuth2 Scheme
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)
```

### Response Headers & Error Codes
- 401 Unauthorized: Include WWW-Authenticate: Bearer header
- 403 Forbidden: User is inactive
- Invalid token format vs expired token: Both 401

---

## 3. Core Schemas: `src/core/schemas.py`

### Purpose
Pydantic models for token request/response validation.

### Structure
```python
# Imports
from pydantic import BaseModel, Field

# 1. Token Response Model
class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Long-lived refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }

# 2. Access Token Only (for refresh endpoint)
class AccessToken(BaseModel):
    """Access token response for refresh endpoint"""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

# 3. Refresh Request Model
class TokenRefresh(BaseModel):
    """Request to refresh access token"""
    refresh_token: str = Field(..., description="Refresh token from login")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }

# 4. Credentials (if custom form validation needed)
class Credentials(BaseModel):
    """User credentials for login"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
```

### Integration
- Used in router.py response_model
- Pydantic automatically validates response structure
- json_schema_extra for OpenAPI documentation

---

## 4. Authentication Router: `src/auth/router.py`

### Purpose
HTTP endpoints for authentication operations.

### Structure
```python
# Imports
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.config import settings
from src.core.schemas import Token, AccessToken, TokenRefresh
from src.core.dependencies import get_current_user, get_current_active_user
from src.users.models import User
from src.auth.service import AuthService
from src.auth.exceptions import InvalidCredentials, UserInactive, TokenExpired

# 1. Router Setup
router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized - invalid or expired token"},
        403: {"description": "Forbidden - user inactive"},
        429: {"description": "Too Many Requests - rate limit exceeded"},
    },
)

# 2. Login Endpoint
@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user with email and password. Returns access and refresh tokens.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid email or password"},
        403: {"description": "User account is inactive"},
        429: {"description": "Too many login attempts (rate limited)"},
    },
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    User login endpoint.

    OAuth2 standard form data:
    - username: User email address
    - password: User password
    """
    # Validate credentials
    # Check rate limit
    # Generate tokens
    # Return Token response

# 3. Refresh Token Endpoint
@router.post(
    "/refresh",
    response_model=AccessToken,
    summary="Refresh access token",
    description="Use refresh token to get new access token.",
    responses={
        200: {"description": "Refresh successful"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh(
    payload: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> AccessToken:
    """
    Refresh access token using refresh token.

    Request body:
    - refresh_token: JWT refresh token from login
    """
    # Validate refresh token
    # Check user still exists and is active
    # Generate new access token
    # Return AccessToken response

# 4. Logout Endpoint
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Logout current user (optional - client should discard token).",
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Logout endpoint (placeholder).

    Client should discard token. Optional: implement token blacklist.
    """
    # Optional: Add token to blacklist
    # Optional: Update user last_logout
    # Return 204

# 5. Get Current User Endpoint (Optional)
@router.get(
    "/me",
    response_model=dict,  # or UserPublic schema
    summary="Get current user",
    description="Get information about authenticated user.",
    responses={
        200: {"description": "User profile"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get current authenticated user's information"""
    # Return user profile (excluding sensitive fields)
```

### Response Schemas
- Login: Token (access_token, refresh_token, token_type)
- Refresh: AccessToken (access_token, token_type)
- Logout: 204 No Content
- Get Me: UserPublic (id, email, name, is_active, created_at)

### OpenAPI Integration
- Automatic from response_model
- Includes all status codes and descriptions
- OAuth2 security scheme automatically applied

---

## 5. Authentication Service: `src/auth/service.py`

### Purpose
Business logic for authentication operations.

### Structure
```python
# Imports
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_password, create_access_token, create_refresh_token
from src.users.models import User
from src.users import crud as user_crud
from src.auth.exceptions import InvalidCredentials, UserInactive, RateLimitExceeded

# 1. Authentication Service
class AuthService:
    """Centralized authentication business logic"""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate user by email and password.

        Returns:
            User if credentials valid, None otherwise
        """
        # Look up user by email (case-insensitive)
        # Verify password
        # Return user or None

    @staticmethod
    async def login_user(
        db: AsyncSession,
        user: User,
    ) -> dict:
        """
        Generate tokens for authenticated user.

        Returns:
            {access_token, refresh_token, token_type}
        """
        # Create access token
        # Create refresh token
        # Update user.last_login
        # Return token dict

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
    ) -> dict:
        """
        Issue new access token using refresh token.

        Returns:
            {access_token, token_type}

        Raises:
            TokenExpired: If refresh token expired
            InvalidToken: If token malformed
        """
        # Decode refresh token
        # Verify token type is "refresh"
        # Look up user
        # Create new access token
        # Return token dict

    @staticmethod
    async def logout_user(
        db: AsyncSession,
        user: User,
    ) -> None:
        """
        Logout user (optional - placeholder).

        Could implement:
        - Token blacklist entry
        - User.last_logout update
        - Event logging
        """
        # Optional: Update user.last_logout = now()
        # Optional: Add to token blacklist
        # Optional: Log logout event

# 2. Rate Limiting (if implemented in service)
class RateLimiter:
    """Rate limiter for login attempts"""

    @staticmethod
    async def check_login_limit(
        ip_address: str,
        max_attempts: int = 5,
        window_minutes: int = 15,
    ) -> None:
        """
        Check if IP address exceeded login attempt limit.

        Raises:
            RateLimitExceeded: If limit exceeded
        """
        # Check attempt count for IP in last window_minutes
        # Increment counter
        # Raise if exceeded
```

### Integration Points
- Called by router.py endpoints
- Uses security.py for crypto operations
- Accesses database via crud
- Raises custom exceptions (caught by router)

---

## 6. Custom Exceptions: `src/auth/exceptions.py`

### Purpose
Domain-specific authentication exceptions.

### Structure
```python
# Imports
from fastapi import HTTPException, status

# Base Authentication Exception
class AuthenticationException(HTTPException):
    """Base class for authentication errors"""
    pass

# Specific Exceptions
class InvalidCredentials(AuthenticationException):
    """Raised when email or password invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

class UserInactive(AuthenticationException):
    """Raised when user account is inactive"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

class TokenExpired(AuthenticationException):
    """Raised when token has expired"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

class InvalidToken(AuthenticationException):
    """Raised when token is malformed or invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

class RateLimitExceeded(AuthenticationException):
    """Raised when rate limit exceeded"""
    def __init__(self, retry_after: int = 900):  # 15 minutes
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts, please try again later",
            headers={"Retry-After": str(retry_after)},
        )
```

### Usage Pattern
- Raised in service.py or dependencies.py
- FastAPI automatically converts to HTTP response
- Includes appropriate status codes and headers

---

## 7. Module Init: `src/auth/__init__.py`

### Purpose
Export public API from auth module.

### Structure
```python
"""Authentication module - JWT token and login management"""

from src.auth.router import router
from src.auth.service import AuthService
from src.auth.exceptions import (
    AuthenticationException,
    InvalidCredentials,
    UserInactive,
    TokenExpired,
    InvalidToken,
    RateLimitExceeded,
)

__all__ = [
    "router",
    "AuthService",
    "AuthenticationException",
    "InvalidCredentials",
    "UserInactive",
    "TokenExpired",
    "InvalidToken",
    "RateLimitExceeded",
]
```

---

## 8. Test Structure: `tests/auth/`

### Purpose
Comprehensive test coverage for authentication module.

### Files

#### `tests/auth/conftest.py` - Shared Fixtures
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import create_access_token, create_refresh_token, get_password_hash
from src.users.models import User
from src.users import crud as user_crud

@pytest.fixture
async def auth_user(db: AsyncSession) -> User:
    """Create test user with known credentials"""
    # Create user with email, hashed password
    # Return user

@pytest.fixture
def test_password() -> str:
    """Known test password"""
    return "TestPassword123!"

@pytest.fixture
async def access_token(auth_user: User) -> str:
    """Generate valid access token for auth_user"""
    return create_access_token(str(auth_user.id))

@pytest.fixture
async def refresh_token(auth_user: User) -> str:
    """Generate valid refresh token for auth_user"""
    return create_refresh_token(str(auth_user.id))

@pytest.fixture
async def expired_access_token(auth_user: User) -> str:
    """Generate expired access token"""
    # Create token with past expiry
    return create_access_token(str(auth_user.id), expires_delta=timedelta(hours=-1))
```

#### `tests/auth/test_security.py` - Unit Tests
```python
# Test password hashing
async def test_password_hash_creates_unique_hashes():
    # Same password should create different hashes
    pass

async def test_verify_password_correct():
    # Correct password should verify
    pass

async def test_verify_password_incorrect():
    # Incorrect password should not verify
    pass

# Test token creation
async def test_create_access_token_includes_expiry():
    # Token should include exp claim
    pass

async def test_create_refresh_token_longer_expiry():
    # Refresh token should have longer expiry
    pass

# Test token validation
async def test_decode_valid_token():
    # Valid token should decode to payload
    pass

async def test_decode_expired_token():
    # Expired token should return None
    pass

async def test_decode_invalid_token():
    # Malformed token should return None
    pass

async def test_decode_wrong_signature():
    # Token with wrong secret should return None
    pass
```

#### `tests/auth/test_dependencies.py` - Dependency Tests
```python
# Test get_current_user dependency
async def test_get_current_user_valid_token(access_token: str):
    # Should extract user from valid token
    pass

async def test_get_current_user_invalid_token():
    # Should raise 401
    pass

async def test_get_current_user_expired_token(expired_token: str):
    # Should raise 401
    pass

async def test_get_current_user_nonexistent_user():
    # Should raise 401 if user deleted
    pass

# Test get_current_active_user
async def test_get_current_active_user_inactive():
    # Should raise 403 if user.is_active = False
    pass
```

#### `tests/auth/test_router.py` - Integration Tests
```python
# Test login endpoint
async def test_login_success(client: AsyncClient, auth_user: User, test_password: str):
    # POST /login should return tokens
    pass

async def test_login_invalid_email(client: AsyncClient):
    # Invalid email should return 401
    pass

async def test_login_invalid_password(client: AsyncClient):
    # Invalid password should return 401
    pass

async def test_login_inactive_user(client: AsyncClient):
    # Inactive user should return 403
    pass

async def test_login_rate_limited(client: AsyncClient):
    # More than 5 attempts should return 429
    pass

# Test refresh endpoint
async def test_refresh_success(client: AsyncClient, refresh_token: str):
    # POST /refresh should return new access token
    pass

async def test_refresh_invalid_token(client: AsyncClient):
    # Invalid refresh token should return 401
    pass

async def test_refresh_access_token_rejected(client: AsyncClient, access_token: str):
    # Using access token instead of refresh should return 401
    pass

# Test logout endpoint
async def test_logout_success(client: AsyncClient, access_token: str):
    # POST /logout should return 204
    pass

async def test_logout_unauthenticated(client: AsyncClient):
    # No token should return 401
    pass

# Test protected routes
async def test_protected_route_requires_token(client: AsyncClient):
    # Without token should return 401
    pass

async def test_protected_route_with_token(client: AsyncClient, access_token: str):
    # With token should work
    pass
```

---

## 9. Configuration Updates: `src/config.py`

### Additions
```python
# JWT Configuration
SECRET_KEY: str = Field(
    ...,
    min_length=32,
    description="Secret key for JWT signing (minimum 32 characters)",
)
ALGORITHM: str = Field(
    default="HS256",
    description="JWT signing algorithm",
)
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
    default=30,
    ge=1,
    le=1440,
    description="Access token expiration in minutes",
)
REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
    default=7,
    ge=1,
    le=365,
    description="Refresh token expiration in days",
)

# Bcrypt Configuration
BCRYPT_ROUNDS: int = Field(
    default=12,
    ge=10,
    le=14,
    description="bcrypt cost factor",
)

# Rate Limiting
AUTH_RATE_LIMIT_LOGIN: str = Field(
    default="5/15 minutes",
    description="Rate limit for login endpoint",
)

# API Configuration
API_V1_PREFIX: str = Field(
    default="/api/v1",
    description="API version 1 path prefix",
)

# Validators
@field_validator('SECRET_KEY')
@classmethod
def validate_secret_key(cls, v: str) -> str:
    if len(v) < 32:
        raise ValueError('SECRET_KEY must be at least 32 characters')
    return v
```

---

## 10. Requirements Update: `requirements/base.txt`

### New Packages
```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
slowapi>=0.1.8
```

---

## Architecture Dependency Graph

```
router.py
  └─ depends on:
      - service.py (business logic)
      - dependencies.py (authentication)
      - schemas.py (validation)
      - exceptions.py (error handling)

service.py
  └─ depends on:
      - security.py (crypto)
      - user crud.py (data access)
      - exceptions.py

dependencies.py
  └─ depends on:
      - security.py (token validation)
      - user crud.py (user lookup)

security.py
  └─ depends only on:
      - config.py (settings)
      - stdlib (datetime, cryptography)

config.py
  └─ no dependencies
```

---

## Code Quality Standards

### Type Annotations
- 100% of functions must have return type hints
- All parameters must be type-annotated
- Use Optional[T] for nullable values
- Use Union[T1, T2] for multiple types

### Docstrings
- All public functions must have docstrings
- Include description, parameters, returns, raises
- Example: Use for complex logic

### Testing
- All functions covered by tests
- Target: 85%+ line coverage
- All test names start with test_
- Organize by function/feature

### Security
- Never log passwords or full tokens
- Never hardcode secrets
- Always validate input
- Use type hints to enforce contracts

---

**This outline provides the exact structure that will be implemented in Phase 3.**

**Total Expected Code**: 900-1100 lines across 11 files
**Test Coverage**: 26+ test cases achieving 85%+ coverage
**Implementation Time**: ~2-3 hours for coding + testing
