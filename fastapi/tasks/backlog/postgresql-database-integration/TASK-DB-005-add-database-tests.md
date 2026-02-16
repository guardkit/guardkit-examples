---
id: TASK-DB-005
title: Add database integration tests
task_type: testing
parent_review: TASK-REV-A405
feature_id: FEAT-A405
status: pending
priority: high
wave: 4
implementation_mode: task-work
complexity: 5
dependencies: [TASK-DB-004]
tags: [testing, database, pytest, async]
---

# Task: Add database integration tests

## Description

Create comprehensive test infrastructure for async database operations including shared fixtures, CRUD operation tests, and API endpoint tests. Target 80% code coverage.

## Scope

### Files to Create
- `tests/conftest.py` - Shared async test fixtures (test DB engine, session override, client)
- `tests/users/` - Test directory
- `tests/users/__init__.py` - Package init
- `tests/users/test_crud.py` - CRUD operation tests
- `tests/users/test_router.py` - API endpoint tests
- `tests/users/test_schemas.py` - Schema validation tests

## Technical Requirements

### Test Database Strategy
- Use separate test PostgreSQL database (or SQLite async for CI speed)
- Create all tables before tests, drop after
- Each test function gets a fresh session with rollback

### Shared Fixtures (conftest.py)
```python
# Key fixtures:
# - test_engine: create_async_engine for test database
# - test_session: AsyncSession with per-test rollback
# - override_get_db: Override app dependency with test session
# - client: httpx.AsyncClient using test app
# - sample_user: Factory fixture for creating test users
```

### CRUD Tests (test_crud.py)
- test_create_user: Create and verify all fields
- test_get_user: Retrieve by ID
- test_get_user_not_found: Returns None for missing ID
- test_get_by_email: Retrieve by email address
- test_get_multi: Paginated list with skip/limit
- test_update_user: Partial update
- test_delete_user: Hard delete
- test_count: Total record count

### API Tests (test_router.py)
- test_create_user_endpoint: POST /users/ returns 201
- test_create_user_duplicate_email: Returns 400/409
- test_list_users: GET /users/ with pagination
- test_get_user_endpoint: GET /users/{id} returns user
- test_get_user_not_found: GET /users/{id} returns 404
- test_update_user_endpoint: PUT /users/{id} updates fields
- test_delete_user_endpoint: DELETE /users/{id} removes user
- test_health_with_db: Health endpoint includes db_status

### Schema Tests (test_schemas.py)
- test_user_create_valid: Valid creation data passes
- test_user_create_invalid_email: Invalid email rejected
- test_user_public_excludes_password: Password not in response

## Acceptance Criteria
- [ ] All tests pass with `pytest -v`
- [ ] Code coverage >= 80% for src/users/ and src/db/
- [ ] Async tests work with pytest-asyncio
- [ ] Test database isolated from development database
- [ ] Tests clean up after themselves (no leftover data)
- [ ] CI-compatible (can run without Docker PostgreSQL if using SQLite)

## Testing Notes
- Standard testing depth
- Use `pytest --cov=src --cov-report=term` for coverage
- Use `@pytest.mark.asyncio` for all async tests
