---
id: TASK-LOG-004
title: Integrate logging with FastAPI app
task_type: feature
parent_review: TASK-REV-CABA
feature_id: FEAT-LOG
status: pending
priority: high
wave: 2
implementation_mode: direct
complexity: 3
dependencies:
  - TASK-LOG-001
  - TASK-LOG-002
  - TASK-LOG-003
tags: [logging, fastapi, integration]
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Integrate logging with FastAPI app

## Description
Wire the logging configuration and middleware into the FastAPI application entry point (`src/main.py`), ensuring logging is initialized at startup and middleware is registered.

## Requirements
1. In `src/main.py` (create or modify):
   - Call `setup_logging()` during app initialization with settings values
   - Register `RequestLoggingMiddleware` on the FastAPI app
   - Add startup log message confirming logging initialized
   - Configure lifespan or startup event to initialize logging before first request

2. Ensure stdlib logging interop:
   - Third-party library logs (uvicorn, sqlalchemy, httpx) routed through structlog
   - Uvicorn access logs configured to use structured format
   - SQLAlchemy echo logs respect the configured log level

3. Add structlog dependency to `pyproject.toml` / `requirements/base.txt` if not present

## Acceptance Criteria
- [ ] `setup_logging()` called before app serves requests
- [ ] `RequestLoggingMiddleware` registered on FastAPI app
- [ ] Startup log message emitted in structured format
- [ ] Third-party library logs appear in structured format
- [ ] Uvicorn access log format consistent with app logs
- [ ] `structlog` listed in project dependencies

## Technical Notes
- Use FastAPI lifespan context manager for initialization
- Configure uvicorn logging by setting `log_config=None` and routing through structlog
- Order middleware registration correctly (logging middleware should be outermost)

## Files to Create/Modify
- `src/main.py` (modify or create)
- `pyproject.toml` or `requirements/base.txt` (modify if needed)
