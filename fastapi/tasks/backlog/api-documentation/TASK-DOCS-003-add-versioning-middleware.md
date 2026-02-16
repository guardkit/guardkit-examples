---
id: TASK-DOCS-003
title: Add API versioning header middleware
task_type: feature
parent_review: TASK-REV-AB87
feature_id: FEAT-DOCS
status: pending
priority: normal
complexity: 3
wave: 2
implementation_mode: task-work
dependencies: [TASK-DOCS-001]
tags: [documentation, versioning, middleware]
---

# Task: Add API versioning header middleware

## Description

Create `src/core/middleware.py` with ASGI middleware that adds an `X-API-Version` response header to all API responses. The version value is read from application settings. Update `src/main.py` to register the middleware. Also annotate the versioning header in the OpenAPI schema so it appears in Swagger UI documentation.

## Prerequisites

- TASK-DOCS-001 (documentation settings with `API_VERSION` and `API_VERSION_HEADER`).
- FEAT-HLTH project foundation (`src/main.py`).

## Acceptance Criteria

- [ ] `src/core/middleware.py` exists with `APIVersionMiddleware` class
- [ ] All API responses include `X-API-Version` header with current version from settings
- [ ] Header name is configurable via `API_VERSION_HEADER` setting
- [ ] Middleware is registered in `src/main.py`
- [ ] Middleware is async-compatible (does not block event loop)
- [ ] OpenAPI schema documents the `X-API-Version` response header
- [ ] Header visible in Swagger UI "Try it out" responses

## Implementation Notes

```python
# src/core/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.config import settings


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Add API version header to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers[settings.API_VERSION_HEADER] = settings.API_VERSION
        return response
```

### OpenAPI Header Annotation

The versioning header should be documented in the OpenAPI schema. This can be done by adding a global response header in the `custom_openapi()` function or via route-level `responses` parameter.

## Files to Create/Modify

- `src/core/middleware.py` (create)
- `src/main.py` (modify - register middleware)
