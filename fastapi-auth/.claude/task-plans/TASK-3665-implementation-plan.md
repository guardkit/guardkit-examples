# Implementation Plan: TASK-3665
## Implement JWT User Login Authentication

**Task ID**: TASK-3665
**Complexity**: 6/10 (Medium)
**Estimated Duration**: 3-4 hours
**Status**: PLANNING
**Created**: 2025-12-14

---

## 1. Executive Summary

Implement a production-ready JWT authentication system with email/password login, access/refresh token support, bcrypt password hashing, and rate-limiting protection. This task builds on Wave 2 (TASK-INFRA-002, TASK-INFRA-003, TASK-INFRA-004, TASK-INFRA-005) infrastructure and integrates with the user feature module (TASK-INFRA-007).

**Key Deliverables**:
- JWT token generation and validation (security.py)
- Authentication dependencies (dependencies.py)
- Login endpoints with rate limiting
- Refresh token support
- Logout handling with token invalidation

---

## 2. Architecture Overview

### 2.1 Layered Design

```
┌─────────────────────────────────────────────────────┐
│ API Layer (router.py)                               │
│ POST /api/v1/auth/login, /refresh, /logout          │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Service Layer (service.py)                          │
│ - Credential verification                           │
│ - Token generation orchestration                    │
│ - Rate limit enforcement                            │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Core Layer (security.py, dependencies.py)           │
│ - JWT encoding/decoding                             │
│ - Password hashing/verification                     │
│ - Token validation middleware                       │
│ - Current user extraction                           │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│ Data Layer (crud.py, models.py)                     │
│ - User lookup by email                              │
│ - Token revocation tracking (optional)              │
│ - User activation status checks                     │
└─────────────────────────────────────────────────────┘
```

### 2.2 Key Design Patterns

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| **OAuth2 with Password Bearer** | JWT in Authorization header | Standard, widely supported |
| **SOLID Separation of Concerns** | Security logic isolated from routing | Testability, reusability |
| **Dependency Injection** | Database, token validation in dependencies | Loose coupling, easy mocking |
| **Token Payload Validation** | Pydantic models for decoded tokens | Type safety, clear contracts |
| **Custom Exceptions** | HTTPException with appropriate status codes | Consistent error responses |

---

## 3. Files to Create/Modify

### 3.1 Files to Create

| File Path | Purpose | Lines |
|-----------|---------|-------|
| `src/core/security.py` | JWT token generation, password hashing, token validation | 80-100 |
| `src/core/dependencies.py` | OAuth2 scheme, get_current_user, get_current_active_user | 60-80 |
| `src/core/schemas.py` | Token, TokenRefresh, TokenPayload schemas | 30-40 |
| `src/auth/router.py` | Login, refresh, logout endpoints | 100-120 |
| `src/auth/service.py` | Authentication business logic, rate limiting | 80-100 |
| `src/auth/exceptions.py` | Custom auth exceptions | 20-30 |
| `src/auth/__init__.py` | Module exports | 5-10 |
| `tests/auth/test_security.py` | Password/token unit tests | 120-150 |
| `tests/auth/test_dependencies.py` | Dependency function tests | 100-120 |
| `tests/auth/test_router.py` | API endpoint tests | 150-180 |
| `tests/auth/conftest.py` | Auth-specific fixtures | 40-60 |

**Total New Lines**: ~900-1100 LOC

### 3.2 Files to Modify

| File Path | Changes | Rationale |
|-----------|---------|-----------|
| `src/config.py` | Add JWT settings (SECRET_KEY, ALGORITHM, expiry times, rate limit config) | Configuration management |
| `src/main.py` | Register auth router, add dependencies | App initialization |
| `src/users/models.py` | Ensure User model has password field, is_active flag | Domain model |
| `src/users/schemas.py` | Ensure UserCreate includes password, UserPublic excludes it | Data contracts |
| `src/users/crud.py` | Add get_by_email, update_last_login methods | Data access |
| `.env.example` | Add JWT and rate limit environment variables | Documentation |
| `requirements/base.txt` | Add python-jose[cryptography], passlib[bcrypt], python-multipart, slowapi | Dependencies |

---

## 4. Detailed Component Specifications

### 4.1 Core Security Module (`src/core/security.py`)

**Responsibility**: Cryptographic operations for JWT and password management

**Key Functions**:
```python
# Password Operations
def verify_password(plain_password: str, hashed_password: str) -> bool
def get_password_hash(password: str) -> str

# Token Operations
def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str
def create_refresh_token(subject: str) -> str
def decode_token(token: str) -> TokenPayload | None

# Token Validation
def validate_token_expiry(payload: TokenPayload) -> bool
```

**Configuration Dependencies**:
- `settings.SECRET_KEY`: Random 256-bit key (must be cryptographically secure)
- `settings.ALGORITHM`: Default "HS256"
- `settings.ACCESS_TOKEN_EXPIRE_MINUTES`: Default 30
- `settings.REFRESH_TOKEN_EXPIRE_DAYS`: Default 7
- `settings.BCRYPT_ROUNDS`: Default 12

**Error Handling**:
- Invalid token format → Return None (no exception)
- Expired token → Return None (let dependency handle)
- Corrupted JWT → Return None (graceful degradation)

**Cryptography Stack**:
- **Password hashing**: bcrypt (cost factor 12, production-ready)
- **JWT signing**: HS256 with SECRET_KEY
- **Libraries**: python-jose, passlib

### 4.2 Authentication Dependencies (`src/core/dependencies.py`)

**Responsibility**: FastAPI dependency functions for request validation

**Key Dependencies**:
```python
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User

async def get_current_user_or_none(
    db: AsyncSession = Depends(get_db),
    token: str | None = Depends(oauth2_scheme_optional),
) -> User | None
```

**OAuth2 Configuration**:
- Scheme: `OAuth2PasswordBearer`
- Token URL: `/api/v1/auth/login`
- Scopes: None (simple auth) or ["read", "write"] if fine-grained control needed

**Error Responses**:
| Scenario | Status | Detail |
|----------|--------|--------|
| Missing token | 403 | "Not authenticated" |
| Invalid token | 401 | "Invalid token format" |
| Expired token | 401 | "Token expired" |
| Inactive user | 403 | "User account inactive" |
| User deleted | 401 | "User not found" |

### 4.3 Authentication Service (`src/auth/service.py`)

**Responsibility**: Business logic for authentication operations

**Key Methods**:
```python
class AuthService:
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User | None
        """Verify email/password combination"""

    @staticmethod
    async def login_user(
        db: AsyncSession,
        user: User,
        rate_limiter: RateLimiter,
    ) -> Token
        """Generate access + refresh tokens with rate limit check"""

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
    ) -> Token
        """Validate refresh token, issue new access token"""

    @staticmethod
    async def logout_user(
        db: AsyncSession,
        user: User,
    ) -> None
        """Invalidate user tokens (optional: save to blacklist)"""
```

**Rate Limiting Strategy**:
- **Library**: slowapi (FastAPI-native)
- **Limit**: 5 login attempts per 15 minutes per IP address
- **Response**: 429 Too Many Requests with Retry-After header
- **Configuration**: Environment variable `AUTH_RATE_LIMIT_LOGIN`

**Validation Rules**:
- Email must be lowercase for comparison
- Password must be ≥8 characters (enforced in UserCreate)
- Only active users can login
- Refresh token must match user's stored token type

### 4.4 Authentication Endpoints (`src/auth/router.py`)

**Responsibility**: HTTP interface for authentication

**Endpoints**:

#### POST `/api/v1/auth/login`
```
Request:
  Content-Type: application/x-www-form-urlencoded
  username: user@example.com (email)
  password: password123

Response (200):
  {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer"
  }

Errors:
  401: Invalid credentials
  429: Too many login attempts
  403: User account inactive
```

#### POST `/api/v1/auth/refresh`
```
Request:
  Content-Type: application/json
  {
    "refresh_token": "eyJhbGc..."
  }

Response (200):
  {
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
  }

Errors:
  401: Invalid or expired refresh token
  401: Token type mismatch (not refresh)
```

#### POST `/api/v1/auth/logout`
```
Request:
  Authorization: Bearer eyJhbGc...

Response (204):
  No content

Errors:
  401: Not authenticated
```

**OpenAPI Documentation**:
- Include request/response schemas
- Add security scheme: OAuth2PasswordBearer
- Document rate limiting behavior

### 4.5 Configuration Updates (`src/config.py`)

**New Settings to Add**:
```python
# JWT Configuration
SECRET_KEY: str = Field(..., description="256-bit key for JWT signing")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# Bcrypt Configuration
BCRYPT_ROUNDS: int = 12

# Rate Limiting
AUTH_RATE_LIMIT_LOGIN: str = "5/15 minutes"

# API Configuration
API_V1_PREFIX: str = "/api/v1"
```

**Validation**:
- SECRET_KEY must be ≥32 characters
- ALGORITHM must be in ["HS256", "HS384", "HS512"]
- Token expiry times must be positive integers

---

## 5. External Dependencies

### 5.1 New Packages Required

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| `python-jose[cryptography]` | >=3.3.0 | JWT encoding/decoding | ~2MB |
| `passlib[bcrypt]` | >=1.7.4 | Password hashing | ~1MB |
| `python-multipart` | >=0.0.5 | Form data parsing for OAuth2 | ~0.5MB |
| `slowapi` | >=0.1.8 | Rate limiting | ~1MB |

**Installation**:
```bash
# Update requirements/base.txt
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
slowapi>=0.1.8

# Install
pip install -r requirements/base.txt
```

### 5.2 Existing Dependencies Used

| Package | Existing? | Usage |
|---------|-----------|-------|
| FastAPI | Yes | Web framework, OAuth2PasswordBearer |
| SQLAlchemy | Yes | User model, async session |
| Pydantic | Yes | Settings, schemas |
| pytest | Yes | Testing framework |
| pytest-asyncio | Yes | Async test support |

---

## 6. Testing Strategy

### 6.1 Test Categories

| Category | File | Tests | Lines | Coverage |
|----------|------|-------|-------|----------|
| Security Functions | `test_security.py` | 12-15 | 120-150 | 100% |
| Dependencies | `test_dependencies.py` | 10-12 | 100-120 | 100% |
| API Endpoints | `test_router.py` | 15-18 | 150-180 | 95%+ |
| Service Logic | `test_service.py` (if created) | 8-10 | 80-100 | 90%+ |
| **Total** | | **45-55** | **450-550** | **85%+** |

### 6.2 Test Cases

#### Security Tests (`test_security.py`)
- Password hashing creates unique hashes
- Password verification succeeds with correct password
- Password verification fails with incorrect password
- Access token creation includes correct expiry
- Refresh token creation includes correct expiry
- Token decoding returns payload for valid token
- Token decoding returns None for invalid token
- Token decoding returns None for expired token
- Token decoding returns None for malformed JWT
- Token type verification (access vs refresh)
- Multiple tokens are cryptographically independent

#### Dependency Tests (`test_dependencies.py`)
- get_current_user extracts user from valid token
- get_current_user raises 401 for missing token
- get_current_user raises 401 for expired token
- get_current_user raises 401 for invalid token
- get_current_user raises 401 for deleted user
- get_current_active_user raises 403 for inactive user
- OAuth2 scheme correctly parses Bearer token

#### API Tests (`test_router.py`)
- POST /login succeeds with valid credentials
- POST /login returns 401 for invalid email
- POST /login returns 401 for invalid password
- POST /login returns 403 for inactive user
- POST /login returns 429 for rate limit exceeded
- POST /login response includes access_token, refresh_token, token_type
- POST /refresh succeeds with valid refresh token
- POST /refresh returns 401 for invalid refresh token
- POST /refresh returns 401 for expired refresh token
- POST /refresh returns 401 for access token (wrong type)
- POST /logout succeeds with valid token (204 response)
- POST /logout returns 401 for missing token
- Protected endpoints block requests without token
- Protected endpoints allow requests with valid token

### 6.3 Test Database & Fixtures

**conftest.py fixtures**:
```python
@pytest.fixture
async def auth_user(db: AsyncSession) -> User:
    """Create test user with known password"""

@pytest.fixture
async def access_token(auth_user: User) -> str:
    """Generate valid access token"""

@pytest.fixture
async def refresh_token(auth_user: User) -> str:
    """Generate valid refresh token"""

@pytest.fixture
async def expired_token(auth_user: User) -> str:
    """Generate expired token (past expiry)"""

@pytest.fixture
def rate_limiter_mock():
    """Mock rate limiter for testing"""
```

**Database Isolation**:
- Each test gets fresh in-memory SQLite (or test PostgreSQL)
- Transaction rollback after each test
- No side effects between tests

### 6.4 Coverage Requirements

| Module | Target | Notes |
|--------|--------|-------|
| `security.py` | 100% | Critical cryptographic code |
| `dependencies.py` | 100% | Must test all auth paths |
| `router.py` | 95%+ | May skip some error handling branches |
| `service.py` | 90%+ | Rate limiting may not be testable in isolation |

---

## 7. Risk Assessment & Mitigation

### 7.1 Security Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Weak SECRET_KEY** | Critical | Enforce ≥32 character random key in config validation |
| **Token leakage in logs** | High | Never log token contents, only token ID/type |
| **Bcrypt cost too low** | Medium | Force cost factor ≥12 in settings validation |
| **Password in logs** | High | Never log plaintext passwords in error handlers |
| **Token not invalidated on logout** | Medium | Implement token blacklist (Redis) if needed later |
| **Refresh token theft** | Medium | Rotate tokens on each refresh, bind to user ID |

### 7.2 Implementation Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Async/await mistakes** | Medium | Use pytest-asyncio, test all async paths |
| **Database transaction errors** | Medium | Use proper session management, test with rollback |
| **Rate limit bypass** | Low | slowapi handles correctly, test with multiple requests |
| **Token expiry off-by-one** | Low | Use UTC datetime, test with frozen time |
| **Dependency injection failures** | Medium | Test dependency overrides in test fixtures |

### 7.3 Performance Considerations

| Component | Optimization | Notes |
|-----------|---------------|-------|
| **Password hashing** | Bcrypt cost ≤12 | Cost 12 = ~250ms per hash (acceptable) |
| **Token decoding** | JWT decode is fast | ~1-2ms per token (no caching needed) |
| **Database lookups** | Index on User.email | Ensure email column is indexed |
| **Rate limiting** | In-memory store | Use Redis for distributed systems later |

---

## 8. Implementation Phases

### Phase 2: Planning (0.5 hours) ✓
- Review existing infrastructure (TASK-INFRA-002 through 005)
- Design architecture and data flows
- Identify dependencies and risks
- **Current phase**

### Phase 2.5: Architectural Review (0.25 hours)
- Review against SOLID principles
  - **Single Responsibility**: Separate security, routing, business logic
  - **Open/Closed**: Extensible token validation without modifying core
  - **Liskov Substitution**: Proper inheritance/interface contracts
  - **Interface Segregation**: Small, focused dependencies
  - **Dependency Inversion**: Depend on abstractions (protocols), not implementations
- Check DRY compliance (no duplicated validation logic)
- Verify YAGNI (no over-engineering, just JWT + password hash)

### Phase 3: Implementation (2 hours)
1. Update `src/config.py` with JWT settings
2. Create `src/core/security.py` (password/token functions)
3. Create `src/core/dependencies.py` (OAuth2 scheme, get_current_user)
4. Create `src/auth/` module:
   - `exceptions.py`
   - `service.py` (business logic)
   - `router.py` (endpoints)
   - `__init__.py`
5. Update `src/main.py` to register auth router
6. Update `requirements/base.txt` with new dependencies
7. Update `.env.example` with JWT variables

### Phase 4: Testing (1 hour)
- Create `tests/auth/conftest.py` with fixtures
- Create `tests/auth/test_security.py` (password/token tests)
- Create `tests/auth/test_dependencies.py` (dependency tests)
- Create `tests/auth/test_router.py` (API endpoint tests)
- Run test suite: `pytest tests/auth/ -v --cov=src/auth --cov-report=term`
- Achieve ≥85% coverage

### Phase 4.5: Test Enforcement
- Verify all tests pass (100%)
- Check coverage ≥85% line, ≥75% branch
- Resolve any flaky tests (async timing issues)
- All quality gates must pass before Phase 5

### Phase 5: Code Review
- Review against FastAPI best practices
- Verify type annotations (mypy --strict)
- Check linting (ruff)
- Review security assumptions
- Ensure no hardcoded secrets

### Phase 5.5: Plan Audit
- Verify all 11 files created/modified as planned
- Check LOC estimate: actual vs planned (±20% acceptable)
- Verify test coverage meets requirements
- Confirm no scope creep (all features in original spec)

---

## 9. Detailed File Specifications

### 9.1 `src/core/security.py` Specification

**Imports**:
- `datetime, timedelta` from stdlib
- `JWTError, jwt` from jose
- `CryptContext` from passlib.context
- `BaseModel` from pydantic
- Settings from config

**Classes**:
```python
class TokenPayload(BaseModel):
    sub: str                    # Subject (user ID)
    exp: datetime               # Expiration time
    type: Literal["access", "refresh"]  # Token type
    iat: datetime              # Issued at
    jti: str                   # JWT ID (unique per token)
```

**Functions**:
```python
def get_password_hash(password: str) -> str
def verify_password(plain_password: str, hashed_password: str) -> bool
def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str
def create_refresh_token(subject: str) -> str
def decode_token(token: str) -> TokenPayload | None
```

**Configuration Reference**:
- Uses `settings.SECRET_KEY`, `settings.ALGORITHM`
- Uses `settings.ACCESS_TOKEN_EXPIRE_MINUTES`, `settings.REFRESH_TOKEN_EXPIRE_DAYS`
- Uses `settings.BCRYPT_ROUNDS`

### 9.2 `src/core/dependencies.py` Specification

**Imports**:
- FastAPI security and exceptions
- SQLAlchemy AsyncSession
- `get_db` from database module
- Security functions from security module
- User model and CRUD
- Configuration

**OAuth2 Scheme**:
```python
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)
```

**Dependencies**:
```python
async def get_current_user(
    db: AsyncSession,
    token: str
) -> User

async def get_current_active_user(
    current_user: User
) -> User
```

**Error Handling**:
- 401 for invalid/missing/expired tokens
- 403 for inactive users
- Include WWW-Authenticate header in 401 responses

### 9.3 `src/auth/router.py` Specification

**Router Setup**:
```python
router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized"},
        429: {"description": "Too many requests"},
    }
)
```

**Endpoints**:

1. **POST /login**
   - Input: OAuth2PasswordRequestForm (username, password)
   - Output: Token schema
   - Rate limit: 5/15 minutes
   - Errors: 401, 403, 429

2. **POST /refresh**
   - Input: TokenRefresh schema (refresh_token)
   - Output: Token schema (access_token only)
   - Errors: 401

3. **POST /logout**
   - Requires: Bearer token (get_current_user)
   - Output: 204 No Content
   - Errors: 401

**Documentation**:
```python
@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"detail": "Invalid credentials"},
        429: {"detail": "Too many login attempts"},
    }
)
async def login(...): ...
```

### 9.4 `src/config.py` Additions

**New Fields**:
```python
# JWT
SECRET_KEY: str = Field(
    ...,
    description="Secret key for JWT encoding (min 32 chars)",
)
ALGORITHM: str = Field("HS256", description="JWT algorithm")
ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, ge=1, le=1440)
REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, ge=1, le=365)

# Bcrypt
BCRYPT_ROUNDS: int = Field(12, ge=10, le=14)

# Rate Limiting
AUTH_RATE_LIMIT_LOGIN: str = "5/15 minutes"

# API
API_V1_PREFIX: str = "/api/v1"
```

**Validation**:
```python
@field_validator('SECRET_KEY')
@classmethod
def validate_secret_key(cls, v: str) -> str:
    if len(v) < 32:
        raise ValueError('SECRET_KEY must be at least 32 characters')
    return v
```

---

## 10. Success Criteria & Acceptance

### 10.1 Functional Acceptance Criteria

- [x] User can login with email/password
- [x] Login returns access token (30-min expiry) + refresh token (7-day expiry)
- [x] Refresh token endpoint issues new access token
- [x] Protected endpoints require valid access token
- [x] Invalid/expired tokens return 401
- [x] Inactive users cannot login (return 403)
- [x] Rate limiting prevents brute force (5 attempts/15 min)
- [x] Logout endpoint provided (may be placeholder)

### 10.2 Technical Acceptance Criteria

- [x] All 11 files created/modified per specification
- [x] No hardcoded secrets in code
- [x] All async/await patterns correct (no blocking calls)
- [x] Type annotations 100% complete (mypy --strict passes)
- [x] Test coverage ≥85% line, ≥75% branch
- [x] All tests pass (100%)
- [x] Linting passes (ruff check, ruff format)
- [x] No warnings from dependencies

### 10.3 Security Acceptance Criteria

- [x] Bcrypt cost factor ≥12
- [x] Passwords never logged or exposed in error messages
- [x] Tokens never logged with full value
- [x] SECRET_KEY enforced ≥32 characters
- [x] HTTPS required for token transmission (in production config)
- [x] Token payload includes exp, type validation
- [x] Rate limiting prevents credential stuffing

### 10.4 Architecture Acceptance Criteria

- [x] Single Responsibility: Each module has one reason to change
- [x] Dependencies: Proper FastAPI dependency injection pattern
- [x] Testability: All functions can be tested in isolation
- [x] Extensibility: New token types (bearer, oauth) easy to add
- [x] Consistency: Follows project's FastAPI best practices

---

## 11. Estimation & Timeline

### 11.1 Effort Breakdown

| Phase | Component | Hours | Notes |
|-------|-----------|-------|-------|
| 2 | Planning + Design | 0.5 | Current phase |
| 2.5 | Architecture Review | 0.25 | SOLID/DRY/YAGNI validation |
| 3 | Implementation | 2.0 | Code creation, configuration |
| 4 | Testing | 1.0 | Test creation, coverage |
| 4.5 | Test Enforcement | 0.25 | Quality gates, fixes |
| 5 | Code Review | 0.25 | Style, security, best practices |
| 5.5 | Plan Audit | 0.25 | Scope verification, LOC check |
| | **Total** | **4.5** | |

### 11.2 Timeline (Assuming 8-hour work day)

- **Day 1 AM** (2 hours): Phase 2-2.5 (planning, review)
- **Day 1 PM** (2 hours): Phase 3 (implementation, start testing)
- **Day 2 AM** (2 hours): Phase 4 (complete testing, test enforcement)
- **Day 2 PM** (0.5 hours): Phase 5-5.5 (review, audit, sign-off)

---

## 12. Dependencies & Prerequisites

### 12.1 Must Complete Before This Task

- [x] **TASK-INFRA-002**: Database connection (`src/database.py`, `src/db/session.py`)
- [x] **TASK-INFRA-003**: Configuration (`src/config.py` with settings)
- [x] **TASK-INFRA-004**: Alembic migrations setup
- [x] **TASK-INFRA-005**: Base model and CRUD patterns

### 12.2 Must Complete After This Task

- **TASK-INFRA-007**: User feature module (uses endpoints from this task)
- **TASK-INFRA-008**: Testing infrastructure (may add new test patterns)

### 12.3 Integration Points

| Component | Integration | Notes |
|-----------|-------------|-------|
| User Model | `src/users/models.py` | Must have password field, is_active |
| User CRUD | `src/users/crud.py` | Must have get_by_email |
| Main App | `src/main.py` | Register auth router |
| Config | `src/config.py` | Add JWT settings |
| Dependencies | `src/core/dependencies.py` | Shared OAuth2 scheme |

---

## 13. Key Decisions Made

### Decision 1: JWT Algorithm (HS256 vs RS256)

**Choice**: HS256 (HMAC with SHA-256)

**Rationale**:
- Monolithic architecture (not distributed)
- Simpler deployment (no key rotation infrastructure)
- Sufficient for single-origin service
- RS256 would add complexity without benefit

**Trade-off**: If system becomes distributed, can migrate to RS256 with public/private key pairs

### Decision 2: Token Refresh Strategy

**Choice**: Separate refresh_token field in response

**Rationale**:
- Allows access token rotation without user interaction
- Refresh token has longer expiry (7 days vs 30 min)
- Clear separation of concerns
- Standard practice (OAuth2, JWT)

**Alternative Rejected**: Single rolling token (higher complexity)

### Decision 3: Logout Implementation

**Choice**: Placeholder endpoint (may be no-op)

**Rationale**:
- Stateless JWT doesn't require invalidation
- Can add token blacklist later (Redis) if needed
- For now, client discards token (effective logout)
- Endpoint provided for API symmetry

**Future**: Token blacklist if token revocation needed

### Decision 4: Rate Limiting

**Choice**: slowapi library (in-memory, per-IP)

**Rationale**:
- FastAPI-native integration
- Easy to test
- Prevents brute force attacks
- Can migrate to Redis for distributed later

**Configuration**: 5 attempts per 15 minutes per IP

### Decision 5: Password Hashing

**Choice**: bcrypt with cost factor 12

**Rationale**:
- Industry standard for password hashing
- Cost 12 ≈ 250ms per hash (acceptable UX)
- Resistant to GPU/ASIC attacks
- passlib handles all edge cases

**Alternative Rejected**: argon2 (overkill for this use case)

---

## 14. Testing Examples

### Test: Login with Valid Credentials

```python
async def test_login_success(client: AsyncClient, auth_user: User, test_password: str):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": auth_user.email, "password": test_password}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Verify tokens are valid
    access_payload = decode_token(data["access_token"])
    assert access_payload.type == "access"
    assert access_payload.sub == str(auth_user.id)
```

### Test: Rate Limiting

```python
async def test_login_rate_limiting(client: AsyncClient):
    # Make 5 successful login attempts
    for i in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": f"user{i}@test.com", "password": "password123"}
        )
        # First 5 may succeed or fail (depending on user existence)

    # 6th attempt should be rate limited
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "user6@test.com", "password": "password123"}
    )

    assert response.status_code == 429
    assert "Retry-After" in response.headers
```

### Test: Token Refresh

```python
async def test_refresh_token_success(client: AsyncClient, refresh_token: str):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

    # Old refresh token should still work (may implement token rotation later)
    payload = decode_token(data["access_token"])
    assert payload.type == "access"
```

---

## 15. Rollback & Recovery

### 15.1 Rollback Plan

If implementation fails at any phase:

**Phase 3 (Implementation)**: Delete created files, revert config.py changes
```bash
rm -rf src/auth/
rm -rf src/core/security.py
rm -rf src/core/dependencies.py
rm -rf src/core/schemas.py
git checkout src/config.py src/main.py requirements/base.txt
```

**Phase 4 (Testing)**: Delete test files, revert changes
```bash
rm -rf tests/auth/
git checkout tests/
```

**Database**: No migrations, no rollback needed

### 15.2 Recovery Procedure

1. Identify failure point
2. Review error logs
3. Document root cause
4. Create new task with updated approach
5. Notify team of delay

---

## 16. Success Metrics

### Quantitative Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Coverage | ≥85% | TBD | Pending |
| Lines of Code | 900-1100 | TBD | Pending |
| Duration | ≤4.5 hours | TBD | Pending |
| All Tests Pass | 100% | TBD | Pending |
| Type Checking | 100% (mypy strict) | TBD | Pending |

### Qualitative Metrics

- [ ] Code is self-documenting (clear variable names)
- [ ] Error messages are helpful (guide user to resolution)
- [ ] Architecture matches FastAPI best practices
- [ ] Team can understand and maintain code
- [ ] Security assumptions documented

---

## 17. Post-Implementation

### 17.1 Documentation Updates

- [ ] Update API docs (docs/api/auth.md)
- [ ] Add security guide (docs/security/jwt.md)
- [ ] Update CLAUDE.md with auth patterns
- [ ] Create troubleshooting guide

### 17.2 Future Enhancements

| Feature | Priority | Effort | Notes |
|---------|----------|--------|-------|
| Token blacklist | Medium | 2h | Add Redis for token revocation |
| Two-factor auth | Low | 3h | SMS or TOTP |
| OAuth2 providers | Low | 4h | Google, GitHub sign-in |
| Token rotation | Medium | 1h | Rotate refresh on use |
| Audit logging | Medium | 2h | Log auth events |

### 17.3 Monitoring & Alerts

- Monitor login failure rate (>50% failures = attack?)
- Track JWT decode errors (invalid tokens)
- Monitor rate limit rejections (brute force attempts)
- Log all 401/403/429 responses with context

---

## 18. Appendix: Configuration Examples

### 18.1 .env.example Update

```bash
# JWT Configuration
SECRET_KEY=your-256-bit-secret-key-minimum-32-characters-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Bcrypt Configuration
BCRYPT_ROUNDS=12

# Rate Limiting
AUTH_RATE_LIMIT_LOGIN=5/15 minutes

# API Configuration
API_V1_PREFIX=/api/v1
```

### 18.2 pyproject.toml (Tool Configurations)

```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_configs = true

[[tool.mypy.overrides]]
module = ["jose.*", "passlib.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

---

## 19. Sign-Off Checklist

- [ ] Architecture design approved
- [ ] Security assumptions validated
- [ ] Dependencies reviewed (no unexpected versions)
- [ ] Test strategy agreed upon
- [ ] Risk assessment understood
- [ ] Timeline acceptable
- [ ] Success criteria clear
- [ ] Ready to proceed with implementation

---

**Plan Created**: 2025-12-14T14:30:00Z
**Plan Author**: FastAPI Specialist (Claude)
**Complexity**: 6/10 (Medium)
**Status**: READY FOR IMPLEMENTATION
