# Feature: Structured JSON Logging

**Feature ID**: FEAT-LOG
**Parent Review**: TASK-REV-CABA
**Status**: Planned
**Complexity**: 6/10

## Problem Statement

The FastAPI application lacks structured logging infrastructure. Without it:
- No request correlation IDs for tracing requests across services
- No standardized log format for machine parsing and aggregation
- No per-environment log configuration (verbose dev, minimal prod)
- No automatic request/response logging middleware

## Solution Approach

Implement **structlog** with FastAPI middleware for structured JSON logging:

1. **structlog processor pipeline** - Configurable chain of processors that enrich, filter, and render log events
2. **contextvars-based correlation IDs** - Request IDs that flow automatically across async `await` boundaries
3. **Environment-aware rendering** - JSON in production, colored console in development
4. **Middleware-based request logging** - Automatic request/response logging with timing

### Why structlog?

- First-class async context propagation via Python `contextvars`
- Already listed in template `pyproject.toml` dependencies
- Active maintenance (v25.5.0, Oct 2025) by proven maintainer
- 2.6x throughput improvement over alternatives in async workloads
- Native OpenTelemetry/Datadog/Sentry integration

## Subtasks

| ID | Title | Complexity | Wave | Mode | Dependencies |
|---|---|---|---|---|---|
| TASK-LOG-001 | Create logging configuration module | 4 | 1 | task-work | - |
| TASK-LOG-003 | Create logging settings configuration | 3 | 1 | direct | - |
| TASK-LOG-002 | Create correlation ID middleware | 5 | 2 | task-work | LOG-001, LOG-003 |
| TASK-LOG-004 | Integrate logging with FastAPI app | 3 | 2 | direct | LOG-001, LOG-002, LOG-003 |
| TASK-LOG-005 | Add logging tests | 4 | 3 | task-work | LOG-004 |

## Execution Strategy

- **Wave 1** (parallel): LOG-001 + LOG-003 (config module + settings, no file conflicts)
- **Wave 2** (parallel): LOG-002 + LOG-004 (middleware + app integration, after Wave 1)
- **Wave 3** (sequential): LOG-005 (tests require all implementation complete)

## Files Created

```
src/core/logging.py       - structlog configuration and setup
src/core/config.py        - Logging settings (LOG_LEVEL, LOG_FORMAT, etc.)
src/core/middleware.py     - RequestLoggingMiddleware with correlation IDs
src/main.py               - App integration (lifespan, middleware registration)
tests/core/test_logging.py      - Logging config tests
tests/core/test_middleware.py    - Middleware tests
tests/core/test_config_logging.py - Settings validation tests
```

## Next Steps

```bash
# Start implementation with Wave 1
/task-work TASK-LOG-001
/task-work TASK-LOG-003

# After Wave 1 completes, Wave 2
/task-work TASK-LOG-002
/task-work TASK-LOG-004

# Finally, tests
/task-work TASK-LOG-005

# Check progress
/task-status --filter=feature:FEAT-LOG
```
