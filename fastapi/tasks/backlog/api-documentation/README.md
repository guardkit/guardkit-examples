# Feature: API Documentation

**Feature ID**: FEAT-DOCS
**Parent Review**: TASK-REV-AB87
**Approach**: Centralized OpenAPI Configuration Module
**Total Complexity**: 5/10
**Total Tasks**: 5

## Problem Statement

The FastAPI application needs comprehensive API documentation beyond the framework defaults. This includes customized OpenAPI schema metadata, organized tag-based endpoint grouping, API versioning headers, and realistic response examples visible in both Swagger UI and ReDoc.

## Solution Approach

Create a centralized OpenAPI configuration module (`src/core/openapi.py`) that customizes the generated schema using FastAPI's native `get_openapi()` hook. Add lightweight ASGI middleware for API versioning response headers. Enhance Pydantic schemas with `model_config` for response examples. All configuration is driven by Pydantic `Settings` for environment-based control.

**Key Design Decisions**:
- Uses FastAPI's native `custom_openapi()` pattern (no external dependencies)
- Configuration centralized in `src/core/config.py` (consistent with project patterns)
- Response examples co-located with Pydantic schemas (maintainability)
- Versioning via middleware (applies to all responses automatically)

## Dependencies

This feature depends on **FEAT-HLTH** (FastAPI Health App) being implemented first, as it requires the project foundation (`src/main.py`, `src/core/config.py`, `src/health/schemas.py`).

## Task Summary

| Wave | Task | Name | Mode | Complexity |
|------|------|------|------|-----------|
| 1 | TASK-DOCS-001 | Add documentation settings | direct | 2 |
| 2 | TASK-DOCS-002 | Create OpenAPI schema customization | task-work | 4 |
| 2 | TASK-DOCS-003 | Add versioning middleware | task-work | 3 |
| 2 | TASK-DOCS-004 | Add response examples to schemas | task-work | 3 |
| 3 | TASK-DOCS-005 | Add documentation and versioning tests | task-work | 3 |

## Getting Started

```bash
# Start with Wave 1
/task-work TASK-DOCS-001

# Then Wave 2 (parallel)
/task-work TASK-DOCS-002
/task-work TASK-DOCS-003
/task-work TASK-DOCS-004

# Finally Wave 3
/task-work TASK-DOCS-005
```
