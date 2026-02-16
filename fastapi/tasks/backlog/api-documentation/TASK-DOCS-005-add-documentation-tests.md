---
id: TASK-DOCS-005
title: Add documentation and versioning tests
task_type: testing
parent_review: TASK-REV-AB87
feature_id: FEAT-DOCS
status: pending
priority: normal
complexity: 3
wave: 3
implementation_mode: task-work
dependencies: [TASK-DOCS-002, TASK-DOCS-003, TASK-DOCS-004]
tags: [documentation, testing, openapi]
---

# Task: Add documentation and versioning tests

## Description

Create comprehensive tests for all API documentation features: OpenAPI schema correctness, Swagger UI accessibility, ReDoc accessibility, API versioning headers, and response example validation. Tests should verify that the documentation configuration works end-to-end.

## Prerequisites

- TASK-DOCS-002 (OpenAPI customization module)
- TASK-DOCS-003 (versioning middleware)
- TASK-DOCS-004 (response examples)

## Acceptance Criteria

- [ ] Test: OpenAPI schema endpoint returns valid JSON with custom metadata
- [ ] Test: OpenAPI schema contains correct title, version, description from settings
- [ ] Test: OpenAPI schema contains tag metadata
- [ ] Test: Swagger UI endpoint returns 200 OK with HTML content
- [ ] Test: ReDoc endpoint returns 200 OK with HTML content
- [ ] Test: All API responses include `X-API-Version` header
- [ ] Test: `X-API-Version` header value matches `settings.API_VERSION`
- [ ] Test: Response examples present in OpenAPI schema for health endpoint
- [ ] Test: Error response schemas present in OpenAPI schema
- [ ] All tests pass with `pytest -v`
- [ ] Tests use async client pattern (httpx.AsyncClient + ASGITransport)

## Implementation Notes

```python
# tests/core/test_openapi.py
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.config import settings


@pytest.mark.asyncio
async def test_openapi_schema_has_custom_metadata():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(settings.OPENAPI_URL)
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == settings.API_TITLE
        assert schema["info"]["version"] == settings.API_VERSION


@pytest.mark.asyncio
async def test_swagger_ui_accessible():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(settings.DOCS_URL)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_api_version_header():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert settings.API_VERSION_HEADER in response.headers
        assert response.headers[settings.API_VERSION_HEADER] == settings.API_VERSION
```

## Files to Create

- `tests/core/__init__.py` (create)
- `tests/core/test_openapi.py` (create)
- `tests/core/test_middleware.py` (create)
