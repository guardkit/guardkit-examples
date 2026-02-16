---
id: TASK-DB-004
title: Create Users CRUD API endpoints and health check DB integration
task_type: feature
parent_review: TASK-REV-A405
feature_id: FEAT-A405
status: pending
priority: high
wave: 3
implementation_mode: task-work
complexity: 6
dependencies: [TASK-DB-002, TASK-DB-003]
tags: [api, users, endpoints, health-check]
---

# Task: Create Users CRUD API endpoints and health check DB integration

## Description

Build the Users API router with full CRUD endpoints (Create, Read, Update, Delete, List) and integrate database connectivity checking into the health endpoint.

## Scope

### Files to Create
- `src/users/router.py` - Users CRUD API endpoints
- `src/users/dependencies.py` - User-specific dependencies (get_user_or_404)

### Files to Modify
- `src/main.py` - Register users router under API prefix
- `src/health/router.py` - Add database health check to existing health endpoint
- `src/health/schemas.py` - Extend HealthResponse with db_status field

## Technical Requirements

### Users API Endpoints
| Method | Path | Description | Response |
|--------|------|-------------|----------|
| POST | `/api/v1/users/` | Create a new user | 201 + UserPublic |
| GET | `/api/v1/users/` | List users (paginated) | 200 + List[UserPublic] |
| GET | `/api/v1/users/{user_id}` | Get user by ID | 200 + UserPublic |
| PUT | `/api/v1/users/{user_id}` | Update user | 200 + UserPublic |
| DELETE | `/api/v1/users/{user_id}` | Delete user | 200 + UserPublic |

### Endpoint Patterns
- Use `AsyncSession = Depends(get_db)` for database injection
- Use `response_model=UserPublic` for response serialization
- Use `status_code=status.HTTP_201_CREATED` for creation
- Return 404 with detail message for missing users
- Support `skip` and `limit` query params for list endpoint
- Use `APIRouter(prefix="/users", tags=["users"])`

### Health Check DB Integration
- Add `db_status` field to HealthResponse: "connected" or "disconnected"
- Execute `SELECT 1` query to verify connectivity
- Measure and report latency in milliseconds
- Health endpoint should NOT fail if DB is down (degrade gracefully)

### Dependencies
- `get_user_or_404(user_id, db)`: Fetch user or raise HTTPException(404)

## Acceptance Criteria
- [ ] All 5 CRUD endpoints work correctly
- [ ] Proper HTTP status codes returned (201, 200, 404)
- [ ] Pagination works with skip/limit parameters
- [ ] Health endpoint reports database status and latency
- [ ] Health endpoint degrades gracefully when DB is unavailable
- [ ] Users router registered under `/api/v1` prefix
- [ ] Swagger UI shows all endpoints with schemas

## Testing Notes
- Standard testing depth
- Test each endpoint with httpx AsyncClient
- Test 404 handling for non-existent users
- Test health endpoint with and without DB connectivity
