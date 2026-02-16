---
id: TASK-DOCS-004
title: Add response examples to Pydantic schemas
task_type: feature
parent_review: TASK-REV-AB87
feature_id: FEAT-DOCS
status: pending
priority: normal
complexity: 3
wave: 2
implementation_mode: task-work
dependencies: [TASK-DOCS-001]
tags: [documentation, schemas, examples, pydantic]
---

# Task: Add response examples to Pydantic schemas

## Description

Enhance existing Pydantic schemas with `model_config` containing `json_schema_extra` for response examples. Create a shared error response schema with examples. Add OpenAPI-specific examples using `openapi_examples` parameter on route definitions. This ensures Swagger UI and ReDoc show realistic example responses for all endpoints.

## Prerequisites

- TASK-DOCS-001 (documentation settings).
- FEAT-HLTH health endpoint with `HealthResponse` schema must exist.

## Acceptance Criteria

- [ ] `HealthResponse` schema includes `model_config` with `json_schema_extra` examples
- [ ] Shared error response schemas created in `src/core/schemas.py` (ErrorResponse, ValidationErrorResponse)
- [ ] Error schemas include realistic examples
- [ ] Route definitions include `responses` parameter with error examples (404, 422, 500)
- [ ] Swagger UI "Example Value" section shows realistic data for all endpoints
- [ ] ReDoc shows example responses in documentation
- [ ] Pattern documented for future feature schemas to follow

## Implementation Notes

### Schema Examples (Pydantic model_config)

```python
# src/health/schemas.py
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "0.1.0",
                    "environment": "development",
                }
            ]
        }
    }
```

### Error Response Schemas

```python
# src/core/schemas.py
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "Resource not found"},
                {"detail": "Internal server error"},
            ]
        }
    }
```

### Route-Level Response Examples

```python
# In router.py files
@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
```

## Files to Create/Modify

- `src/health/schemas.py` (modify - add examples)
- `src/core/schemas.py` (create - shared error schemas)
- `src/health/router.py` (modify - add responses parameter)
