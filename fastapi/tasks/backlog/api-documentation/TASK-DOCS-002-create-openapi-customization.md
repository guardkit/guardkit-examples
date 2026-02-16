---
id: TASK-DOCS-002
title: Create OpenAPI schema customization module
task_type: feature
parent_review: TASK-REV-AB87
feature_id: FEAT-DOCS
status: pending
priority: high
complexity: 4
wave: 2
implementation_mode: task-work
dependencies: [TASK-DOCS-001]
tags: [documentation, openapi, swagger, redoc]
---

# Task: Create OpenAPI schema customization module

## Description

Create `src/core/openapi.py` with a `custom_openapi()` function that overrides FastAPI's default OpenAPI schema generation. This module centralizes all OpenAPI metadata, tag definitions, API info, and schema extensions. Update `src/main.py` to use the custom OpenAPI function and configure Swagger UI / ReDoc URLs from settings.

## Prerequisites

- TASK-DOCS-001 (documentation settings) must be complete.
- FEAT-HLTH project foundation must exist (`src/main.py`, `src/core/config.py`).

## Acceptance Criteria

- [ ] `src/core/openapi.py` exists with `custom_openapi()` function
- [ ] OpenAPI schema includes custom title, version, description from settings
- [ ] OpenAPI schema includes tag metadata with descriptions for endpoint grouping
- [ ] OpenAPI schema includes `x-logo` extension in info section
- [ ] OpenAPI schema includes contact info and license info
- [ ] `src/main.py` assigns `app.openapi = custom_openapi` (or equivalent)
- [ ] `src/main.py` configures `docs_url`, `redoc_url`, `openapi_url` from settings
- [ ] Swagger UI accessible at configured URL with custom metadata
- [ ] ReDoc accessible at configured URL with custom metadata
- [ ] OpenAPI JSON at configured URL returns customized schema
- [ ] Schema is cached after first generation (performance)

## Implementation Notes

```python
# src/core/openapi.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.core.config import settings


def custom_openapi(app: FastAPI) -> dict:
    """Generate customized OpenAPI schema with API metadata."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )

    # Add custom extensions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com",
    }

    # Add tag metadata
    openapi_schema["tags"] = settings.API_TAGS_METADATA

    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

### Tag Metadata Pattern

```python
# In settings or openapi.py
TAGS_METADATA = [
    {
        "name": "health",
        "description": "Health check endpoints for monitoring and load balancers.",
    },
    {
        "name": "users",
        "description": "User management operations.",
    },
]
```

## Files to Create/Modify

- `src/core/openapi.py` (create)
- `src/main.py` (modify - wire up custom OpenAPI + docs URLs)

## Library Context

- `fastapi.openapi.utils.get_openapi` - generates OpenAPI schema dict from routes
- `FastAPI(docs_url=, redoc_url=, openapi_url=)` - constructor params for doc URLs
