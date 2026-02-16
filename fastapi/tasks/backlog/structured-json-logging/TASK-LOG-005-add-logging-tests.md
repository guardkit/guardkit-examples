---
id: TASK-LOG-005
title: Add logging tests
task_type: testing
parent_review: TASK-REV-CABA
feature_id: FEAT-LOG
status: pending
priority: high
wave: 3
implementation_mode: task-work
complexity: 4
dependencies:
  - TASK-LOG-004
tags: [logging, testing, pytest]
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Add logging tests

## Description
Create comprehensive tests for the logging infrastructure: configuration, middleware, correlation ID propagation, and environment switching.

## Requirements
1. Create `tests/core/test_logging.py`:
   - Test `setup_logging()` configures structlog correctly
   - Test JSON output format in production mode
   - Test console output format in development mode
   - Test log level filtering (DEBUG messages filtered at INFO level)
   - Test `get_logger()` returns bound structlog logger

2. Create `tests/core/test_middleware.py`:
   - Test correlation ID generated when no `X-Request-ID` header
   - Test correlation ID extracted from `X-Request-ID` header
   - Test `X-Request-ID` header present in response
   - Test request start/completion log events emitted
   - Test duration_ms calculated and included in log output
   - Test context cleared between requests (no leakage)
   - Test excluded paths produce reduced logging
   - Test exception handling logs error and re-raises

3. Create `tests/core/test_config_logging.py`:
   - Test LOG_LEVEL validation (valid and invalid values)
   - Test LOG_FORMAT validation
   - Test LOG_EXCLUDE_PATHS parsing from environment variable
   - Test environment variable overrides

## Acceptance Criteria
- [ ] `tests/core/test_logging.py` exists with >= 5 test cases
- [ ] `tests/core/test_middleware.py` exists with >= 7 test cases
- [ ] `tests/core/test_config_logging.py` exists with >= 4 test cases
- [ ] All tests pass with `pytest`
- [ ] Tests use async fixtures where appropriate (`pytest-asyncio`)
- [ ] Test coverage >= 80% for logging module
- [ ] Tests verify JSON structure of log output (parse and validate fields)

## Technical Notes
- Use `structlog.testing.capture_logs()` for capturing log events in tests
- Use `httpx.AsyncClient` with FastAPI TestClient for middleware tests
- Use `monkeypatch` for environment variable testing
- Mock `uuid.uuid4()` for deterministic correlation ID testing

## Files to Create/Modify
- `tests/core/test_logging.py` (new)
- `tests/core/test_middleware.py` (new)
- `tests/core/test_config_logging.py` (new)
