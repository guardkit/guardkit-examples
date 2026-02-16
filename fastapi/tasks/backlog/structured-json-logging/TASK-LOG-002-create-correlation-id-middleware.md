---
id: TASK-LOG-002
title: Create correlation ID middleware
task_type: feature
parent_review: TASK-REV-CABA
feature_id: FEAT-LOG
status: pending
priority: high
wave: 2
implementation_mode: task-work
complexity: 5
dependencies:
  - TASK-LOG-001
  - TASK-LOG-003
tags: [logging, middleware, correlation-id]
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Create correlation ID middleware

## Description
Create FastAPI middleware that generates/extracts request correlation IDs, binds them to structlog context, and logs request/response details automatically.

## Requirements
1. Create `src/core/middleware.py` with a `RequestLoggingMiddleware` class:
   - Extract `X-Request-ID` header from incoming requests (if present)
   - Generate a UUID4 request ID if header not present
   - Clear structlog contextvars at request start
   - Bind `request_id`, `method`, `path`, `client_ip` to structlog context
   - Log request start with method, path, query params
   - Log request completion with status code and duration (ms)
   - Add `X-Request-ID` response header for client correlation
   - Handle exceptions gracefully (log error, re-raise)

2. Request/response logging should include:
   - `request_id`: UUID correlation ID
   - `method`: HTTP method (GET, POST, etc.)
   - `path`: Request path
   - `status_code`: Response status code
   - `duration_ms`: Request processing time in milliseconds
   - `client_ip`: Client IP address (from `request.client.host`)

3. Sensitive paths should be configurable for reduced logging (e.g., health checks)

## Acceptance Criteria
- [ ] `src/core/middleware.py` exists with `RequestLoggingMiddleware`
- [ ] Correlation ID generated when `X-Request-ID` header absent
- [ ] Correlation ID extracted when `X-Request-ID` header present
- [ ] `X-Request-ID` header added to all responses
- [ ] Request start and completion logged with structured fields
- [ ] Duration calculated correctly in milliseconds
- [ ] structlog contextvars cleared between requests (no context leakage)
- [ ] Exception handling logs errors without swallowing them
- [ ] Type hints on all public interfaces

## Technical Notes
- Use `starlette.middleware.base.BaseHTTPMiddleware` as base class
- Use `structlog.contextvars.clear_contextvars()` and `bind_contextvars()`
- Use `time.perf_counter()` for duration measurement
- Consider using `uuid.uuid4()` for ID generation

## Files to Create/Modify
- `src/core/middleware.py` (new)
