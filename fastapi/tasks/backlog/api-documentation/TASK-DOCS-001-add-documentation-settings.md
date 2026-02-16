---
id: TASK-DOCS-001
title: Add API documentation settings to config
task_type: scaffolding
parent_review: TASK-REV-AB87
feature_id: FEAT-DOCS
status: pending
priority: high
complexity: 2
wave: 1
implementation_mode: direct
dependencies: []
tags: [documentation, config, openapi]
---

# Task: Add API documentation settings to config

## Description

Extend `src/core/config.py` (Pydantic BaseSettings) with API documentation configuration fields. These settings will be consumed by the OpenAPI schema customization module, middleware, and FastAPI app initialization.

## Prerequisites

- FEAT-HLTH (health app) must be implemented first, providing the base `src/core/config.py` with `Settings` class.

## Acceptance Criteria

- [ ] `Settings` class includes `API_TITLE`, `API_VERSION`, `API_DESCRIPTION` fields
- [ ] `Settings` class includes `DOCS_URL`, `REDOC_URL`, `OPENAPI_URL` fields with defaults (`/docs`, `/redoc`, `/openapi.json`)
- [ ] `Settings` class includes `API_VERSION_HEADER` field (default: `X-API-Version`)
- [ ] `Settings` class includes `API_TAGS_METADATA` as a list of tag definition dicts
- [ ] All fields have sensible defaults for development
- [ ] `.env.example` updated with new documentation-related environment variables
- [ ] Type annotations complete (mypy strict compatible)

## Implementation Notes

```python
# Extend existing Settings in src/core/config.py
class Settings(BaseSettings):
    # ... existing fields ...

    # API Documentation
    API_TITLE: str = "FastAPI Application"
    API_DESCRIPTION: str = "A production-ready FastAPI application"
    API_VERSION: str = "0.1.0"

    # Documentation URLs
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    # Versioning
    API_VERSION_HEADER: str = "X-API-Version"
```

## Files to Create/Modify

- `src/core/config.py` (modify - add documentation settings)
- `.env.example` (modify - add documentation env vars)
