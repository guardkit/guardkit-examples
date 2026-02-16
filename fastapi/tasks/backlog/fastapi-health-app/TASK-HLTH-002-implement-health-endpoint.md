---
id: TASK-HLTH-002
title: "Implement health endpoint"
task_type: feature
parent_review: TASK-REV-2214
feature_id: FEAT-HLTH
status: pending
created: 2026-02-16T14:30:00Z
priority: high
wave: 2
implementation_mode: task-work
complexity: 2
dependencies: [TASK-HLTH-001]
tags: [health, endpoint, api]
---

# Task: Implement health endpoint

## Description

Create the health check endpoint following FastAPI best practices. The endpoint should return application status information useful for monitoring and load balancer health checks.

## Files to Create

### 1. `src/health/__init__.py`
- Empty init file

### 2. `src/health/schemas.py`
- `HealthResponse` Pydantic model with fields:
  - `status: str` (e.g., "healthy")
  - `version: str` (from settings)
  - `environment: str` (e.g., "development", "production")

### 3. `src/health/router.py`
- APIRouter with prefix="/health" and tags=["health"]
- `GET /` endpoint returning HealthResponse
  - Returns status="healthy", version from settings, environment based on DEBUG flag
- Response model: HealthResponse

### 4. Update `src/main.py`
- Include health router: `app.include_router(health_router, prefix=settings.API_V1_PREFIX)`

## Acceptance Criteria

- [ ] `GET /api/v1/health` returns 200 with JSON body
- [ ] Response includes `status`, `version`, and `environment` fields
- [ ] Response model validated by Pydantic schema
- [ ] Health endpoint is visible in auto-generated docs at `/docs`

## Implementation Notes

- Follow feature-based organization pattern from CLAUDE.md
- Use `response_model=HealthResponse` on the route decorator
- Reference `.claude/rules/api/routing.md` for routing patterns
- Keep the endpoint simple - no database check at this stage
