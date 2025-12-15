# TASK-3665: JWT User Login Authentication

## Quick Start

**Task ID**: TASK-3665
**Status**: PLANNING COMPLETE - READY FOR IMPLEMENTATION
**Complexity**: 6/10 (Medium)
**Duration**: 4.5 hours (3-4 hours coding + reviews)
**Files Created**: 4 comprehensive planning documents

---

## Planning Documents

This task includes 4 detailed planning documents to guide implementation:

### 1. TASK-3665-SUMMARY.md (9.1 KB)
**Read this first** - Quick reference guide with:
- What we're building (high-level overview)
- Architecture at a glance
- Files checklist (8 new, 3 modified)
- Key decisions and risk mitigation
- Phase timeline
- Success criteria

**Use for**: Getting oriented, quick lookups, communicating with team

### 2. TASK-3665-implementation-plan.md (32 KB, 1053 lines)
**Comprehensive technical specification** including:
- Executive summary
- Detailed architecture (layered design, patterns)
- All 11 files with specifications
- External dependencies (4 new packages)
- Testing strategy (26+ test cases)
- Risk assessment and mitigation
- Implementation phases (5 phases, 4.5 hours total)
- Detailed component specifications (security.py, dependencies.py, etc.)
- Configuration examples
- Post-implementation guidance

**Use for**: Implementation details, component specifications, testing strategy

### 3. TASK-3665-CODE-OUTLINE.md (23 KB)
**Detailed code structure** for each file:
- Imports and class organization
- Function signatures with docstrings
- Pydantic model definitions
- Test file organization
- Type annotations
- Configuration templates
- Dependency graph

**Use for**: Writing code, understanding structure, following patterns

### 4. TASK-3665-ARCHITECTURE-DIAGRAM.txt (18 KB)
**Visual architecture reference** with:
- Data flow diagrams (login, protected routes)
- Module dependency graphs
- Request validation pipeline
- Security architecture
- Component interaction matrix
- Token structure (JWT payload)
- Error codes and meanings
- Deployment checklist
- Future enhancement roadmap

**Use for**: Understanding system design, debugging, architecture questions

---

## Files to Create/Modify

### New Files (8 files)

| File | Purpose | Size |
|------|---------|------|
| `src/core/security.py` | JWT crypto, password hashing | 80-100 LOC |
| `src/core/dependencies.py` | OAuth2 scheme, get_current_user | 60-80 LOC |
| `src/core/schemas.py` | Token, TokenRefresh Pydantic models | 30-40 LOC |
| `src/auth/router.py` | Login, refresh, logout endpoints | 100-120 LOC |
| `src/auth/service.py` | Authentication business logic | 80-100 LOC |
| `src/auth/exceptions.py` | Custom auth exceptions | 20-30 LOC |
| `src/auth/__init__.py` | Module exports | 5-10 LOC |
| `tests/auth/conftest.py` | Test fixtures | 40-60 LOC |

### Test Files (3 files)

| File | Purpose | Tests |
|------|---------|-------|
| `tests/auth/test_security.py` | Password/token crypto unit tests | 12-15 |
| `tests/auth/test_dependencies.py` | Dependency function tests | 10-12 |
| `tests/auth/test_router.py` | API endpoint integration tests | 15-18 |

### Modified Files (3 files)

| File | Changes |
|------|---------|
| `src/config.py` | Add JWT settings (SECRET_KEY, expiry times, bcrypt config) |
| `src/main.py` | Register auth router |
| `requirements/base.txt` | Add: python-jose, passlib, python-multipart, slowapi |

**Total**: 11 files, ~900-1100 LOC

---

## Reading Path

**By Role**:

**Product Manager / Stakeholder**:
1. TASK-3665-SUMMARY.md (overview + timeline)
2. TASK-3665-ARCHITECTURE-DIAGRAM.txt (data flows, security)

**Backend Developer**:
1. TASK-3665-SUMMARY.md (quick reference)
2. TASK-3665-implementation-plan.md (detailed specs)
3. TASK-3665-CODE-OUTLINE.md (code structure)
4. TASK-3665-ARCHITECTURE-DIAGRAM.txt (troubleshooting)

**Tech Lead / Architect**:
1. TASK-3665-implementation-plan.md (sections 2, 7, 12-13: architecture, risks, decisions)
2. TASK-3665-ARCHITECTURE-DIAGRAM.txt (full architecture)
3. TASK-3665-CODE-OUTLINE.md (security.py, dependencies.py sections)

**QA Engineer**:
1. TASK-3665-SUMMARY.md (success criteria)
2. TASK-3665-implementation-plan.md (section 6: testing strategy)
3. TASK-3665-CODE-OUTLINE.md (test file organization)

---

## Key Architecture Decisions

### 1. JWT Algorithm: HS256 (not RS256)
**Why**: Monolithic architecture, simpler deployment
**Trade-off**: Can migrate to RS256 if system becomes distributed

### 2. Dual-Token System
**Why**: Allows access token rotation without user interaction
**Access Token**: 30 minutes (short-lived)
**Refresh Token**: 7 days (long-lived, rotates access token)

### 3. Bcrypt Cost Factor: 12
**Why**: ~250ms per hash (acceptable UX, resistant to GPU attacks)
**Enforced**: Validation in config.py ensures ≥10, ≤14

### 4. Rate Limiting: slowapi
**Why**: FastAPI-native, easy to test, prevent brute force
**Limit**: 5 login attempts per 15 minutes per IP

### 5. No Logout Token Blacklist (Phase 1)
**Why**: Stateless JWT, client discards token (effective logout)
**Future**: Add Redis blacklist if token revocation needed

---

## Implementation Phases

| Phase | Duration | Checkpoint |
|-------|----------|-----------|
| **2** | 0.5h | Planning & Design (DONE) |
| **2.5** | 0.25h | Architectural Review (SOLID/DRY/YAGNI) |
| **3** | 2h | Implementation (create 11 files) |
| **4** | 1h | Testing (write 26+ test cases) |
| **4.5** | 0.25h | Test Enforcement (gates pass, coverage ≥85%) |
| **5** | 0.25h | Code Review (style, security, best practices) |
| **5.5** | 0.25h | Plan Audit (scope verification, LOC check) |
| | **4.5h** | **TOTAL** |

---

## Success Criteria

### Functional
- [ ] User can login with email/password
- [ ] Login returns access (30 min) + refresh (7 day) tokens
- [ ] Refresh endpoint issues new access token
- [ ] Protected routes require valid access token
- [ ] Invalid/expired tokens return 401
- [ ] Inactive users cannot login (403)
- [ ] Rate limiting prevents brute force (5/15 min)

### Technical
- [ ] All 11 files created per specification
- [ ] Type annotations 100% (mypy --strict)
- [ ] Test coverage ≥85% line, ≥75% branch
- [ ] All tests pass (100%)
- [ ] Linting passes (ruff)
- [ ] No security warnings

### Architecture
- [ ] Single Responsibility principle followed
- [ ] Proper FastAPI dependency injection
- [ ] Extensible design
- [ ] Follows project best practices

---

## Configuration

### Environment Variables Required

```bash
# JWT
SECRET_KEY=<256-bit key, min 32 chars, random>
ALGORITHM=HS256                          # Options: HS256, HS384, HS512
ACCESS_TOKEN_EXPIRE_MINUTES=30           # Typically 15-60 minutes
REFRESH_TOKEN_EXPIRE_DAYS=7              # Typically 7-30 days

# Bcrypt
BCRYPT_ROUNDS=12                         # Options: 10-14

# Rate Limiting
AUTH_RATE_LIMIT_LOGIN=5/15 minutes

# API
API_V1_PREFIX=/api/v1
```

### Example .env

```bash
# Copy to .env (never commit this!)
SECRET_KEY=your-super-secret-key-minimum-32-characters-xxxxxxxx
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
AUTH_RATE_LIMIT_LOGIN=5/15 minutes
API_V1_PREFIX=/api/v1
```

---

## Dependencies

### Prerequisites (Must Complete First)
- TASK-INFRA-002: Database connection setup
- TASK-INFRA-003: Configuration infrastructure
- TASK-INFRA-004: Alembic migrations
- TASK-INFRA-005: Base model & CRUD

### New Packages
```bash
pip install python-jose[cryptography]>=3.3.0
pip install passlib[bcrypt]>=1.7.4
pip install python-multipart>=0.0.5
pip install slowapi>=0.1.8
```

### Dependent Tasks
- TASK-INFRA-007: User feature module (uses auth endpoints)
- TASK-INFRA-008: Testing infrastructure

---

## API Endpoints

### POST `/api/v1/auth/login`
```
Request:
  Content-Type: application/x-www-form-urlencoded
  username: user@example.com
  password: password123

Response (200):
  {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer"
  }

Errors:
  401: Invalid credentials
  403: User inactive
  429: Rate limited (5+ attempts in 15 min)
```

### POST `/api/v1/auth/refresh`
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
  401: Invalid/expired refresh token
```

### POST `/api/v1/auth/logout`
```
Request:
  Authorization: Bearer eyJhbGc...

Response (204): No Content

Errors:
  401: Not authenticated
```

### Using Protected Routes
```
GET /api/v1/users/me
  Authorization: Bearer eyJhbGc...

Response (200):
  {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true
  }

Errors:
  401: Not authenticated / Token expired
```

---

## Testing Overview

### Test Structure
```
tests/auth/
├── conftest.py          # Shared fixtures (auth_user, tokens)
├── test_security.py     # Unit tests (password, JWT crypto)
├── test_dependencies.py # Dependency tests (get_current_user)
└── test_router.py       # Integration tests (API endpoints)
```

### Test Categories

| Category | Count | Coverage |
|----------|-------|----------|
| Password hashing | 3 | 100% |
| Token operations | 6 | 100% |
| Dependencies | 5 | 100% |
| API endpoints | 12 | 95%+ |
| **Total** | **26+** | **85%+** |

### Running Tests

```bash
# Run all auth tests
pytest tests/auth/ -v

# Run with coverage
pytest tests/auth/ -v --cov=src/auth --cov-report=term

# Run single test
pytest tests/auth/test_security.py::test_verify_password_correct -v

# Run with output
pytest tests/auth/ -v -s
```

---

## Common Patterns

### Using Protected Routes

```python
from fastapi import Depends
from src.core.dependencies import get_current_user
from src.users.models import User

@router.get("/api/v1/users/me")
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> UserPublic:
    """Get current authenticated user's profile"""
    return current_user
```

### Verifying User is Active

```python
from src.core.dependencies import get_current_active_user

@router.post("/api/v1/posts")
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user)
) -> PostPublic:
    """Create post (requires active user)"""
    # ...
```

### Getting Optional User

```python
from src.core.dependencies import get_current_user_optional

@router.get("/api/v1/posts/{post_id}")
async def get_post(
    post_id: int,
    current_user: User | None = Depends(get_current_user_optional)
) -> PostPublic:
    """Get post (works with or without auth)"""
    # ...
```

---

## Troubleshooting

### Invalid SECRET_KEY Error
**Problem**: Config validation fails on startup
**Solution**: Set SECRET_KEY to random string ≥32 characters
```bash
# Generate secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Token Expired 401 Error
**Problem**: Access token valid when issued, then 401
**Solution**: Token expired (default 30 minutes)
**Fix**: Use refresh endpoint to get new access token

### Rate Limit 429 Error
**Problem**: Getting 429 after only a few login attempts
**Solution**: Rate limit is per IP address
**Debug**: Check X-RateLimit headers in response

### User Not Found 401 Error
**Problem**: Valid token but user not found
**Cause**: User was deleted after token issued
**Solution**: This is expected behavior (security)

---

## Next Steps

1. **Phase 2.5**: Conduct architectural review
   - Check SOLID principles (all docs provided)
   - Validate security assumptions
   - Get stakeholder approval

2. **Phase 3**: Begin implementation
   - Start with `src/core/security.py` (no dependencies)
   - Follow sequence in TASK-3665-CODE-OUTLINE.md
   - Use docstring templates from outline

3. **Phase 4**: Write tests
   - Use fixtures from conftest.py
   - Run tests frequently during implementation
   - Achieve ≥85% coverage

4. **Phase 5-5.5**: Review and audit
   - Security review (no hardcoded secrets, password safety)
   - Architecture review (SOLID principles)
   - Plan audit (scope verification)

---

## References

### FastAPI Documentation
- [Security & JWT](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with Password](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Cryptography
- [python-jose Documentation](https://python-jose.readthedocs.io/)
- [passlib Documentation](https://passlib.readthedocs.io/)
- [JWT.io - JWT Debugger](https://jwt.io/)

### Project Standards
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

## Document Versions

| Document | Size | Created | Status |
|----------|------|---------|--------|
| TASK-3665-SUMMARY.md | 9.1 KB | 2025-12-14 | FINAL |
| TASK-3665-implementation-plan.md | 32 KB | 2025-12-14 | FINAL |
| TASK-3665-CODE-OUTLINE.md | 23 KB | 2025-12-14 | FINAL |
| TASK-3665-ARCHITECTURE-DIAGRAM.txt | 18 KB | 2025-12-14 | FINAL |
| TASK-3665-README.md | This file | 2025-12-14 | FINAL |

**Total Planning Documentation**: 82+ KB, 2000+ lines

---

## Sign-Off Checklist

- [ ] Reviewed TASK-3665-SUMMARY.md (5 min)
- [ ] Reviewed TASK-3665-implementation-plan.md (20 min)
- [ ] Reviewed TASK-3665-ARCHITECTURE-DIAGRAM.txt (10 min)
- [ ] Architecture approved by team lead
- [ ] No questions on security assumptions
- [ ] Dependencies understood and available
- [ ] Ready to start Phase 3 implementation

---

**Status**: PLANNING COMPLETE
**Next Action**: Begin Phase 3 Implementation
**Questions?**: Review relevant section in documentation above

