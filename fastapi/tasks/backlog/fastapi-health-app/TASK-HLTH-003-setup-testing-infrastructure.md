---
id: TASK-HLTH-003
title: "Set up testing infrastructure and health tests"
task_type: testing
parent_review: TASK-REV-2214
feature_id: FEAT-HLTH
status: pending
created: 2026-02-16T14:30:00Z
priority: high
wave: 3
implementation_mode: task-work
complexity: 2
dependencies: [TASK-HLTH-001, TASK-HLTH-002]
tags: [testing, pytest, health]
---

# Task: Set up testing infrastructure and health tests

## Description

Create the testing infrastructure with pytest fixtures and write tests for the health endpoint. Ensure tests can run with `pytest` from the project root.

## Files to Create

### 1. `tests/__init__.py`
- Empty init file

### 2. `tests/conftest.py`
- AsyncClient fixture using httpx
- Uses `ASGITransport` with the FastAPI app
- Base URL: "http://test"
- Fixture scope: function (fresh client per test)

### 3. `tests/health/__init__.py`
- Empty init file

### 4. `tests/health/test_router.py`
- `test_health_endpoint_returns_200` - verify status code
- `test_health_endpoint_returns_correct_schema` - verify response fields (status, version, environment)
- `test_health_endpoint_status_is_healthy` - verify status="healthy"
- `test_health_endpoint_version_matches_config` - verify version matches settings

## Acceptance Criteria

- [ ] `pytest` runs successfully from project root
- [ ] All health endpoint tests pass
- [ ] Tests use async client (httpx AsyncClient)
- [ ] Test coverage for health module >= 80%

## Implementation Notes

- Use `pytest.mark.asyncio` or configure `asyncio_mode = "auto"` in pyproject.toml
- Reference `.claude/rules/testing.md` for test patterns
- Reference `.claude/templates/testing/conftest.py.template` for fixture patterns
- Use `httpx.ASGITransport` for async test client (not deprecated TestClient pattern)
