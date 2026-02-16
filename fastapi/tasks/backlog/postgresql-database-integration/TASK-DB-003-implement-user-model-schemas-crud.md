---
id: TASK-DB-003
title: Implement User model, schemas, and CRUD
task_type: feature
parent_review: TASK-REV-A405
feature_id: FEAT-A405
status: pending
priority: high
wave: 2
implementation_mode: task-work
complexity: 5
dependencies: [TASK-DB-001]
tags: [database, users, crud, schemas]
---

# Task: Implement User model, schemas, and CRUD

## Description

Create the User SQLAlchemy model, Pydantic schemas (Create, Update, Public), generic CRUD base class, and User-specific CRUD operations following established project patterns.

## Scope

### Files to Create
- `src/users/__init__.py` - Package init
- `src/users/models.py` - User SQLAlchemy model
- `src/users/schemas.py` - UserBase, UserCreate, UserUpdate, UserPublic Pydantic schemas
- `src/crud/__init__.py` - Package init
- `src/crud/base.py` - Generic CRUDBase class (from template)
- `src/users/crud.py` - CRUDUser extending CRUDBase

## Technical Requirements

### User Model (SQLAlchemy)
```
users table:
  - id: Integer, primary_key, indexed
  - email: String, unique, indexed, not null
  - username: String, unique, indexed, not null
  - hashed_password: String, not null
  - full_name: String, nullable
  - is_active: Boolean, default=True
  - is_superuser: Boolean, default=False
  - created_at: DateTime, server_default=now()
  - updated_at: DateTime, server_default=now(), onupdate=now()
```

### Pydantic Schemas
- `UserBase`: Shared fields (email, username, full_name)
- `UserCreate`: UserBase + password (plain text input)
- `UserUpdate`: Optional fields for partial update
- `UserPublic`: UserBase + id, is_active, created_at (response model, no password)
- All schemas use `from_attributes = True` for ORM compatibility

### Generic CRUD Base
- Follow template from `.claude/templates/crud/crud_base.py.template`
- Generic[ModelType, CreateSchemaType, UpdateSchemaType]
- Methods: get, get_multi, create, update, delete, exists, count
- Use `flush()` not `commit()` (auto-commit via get_db dependency)

### User CRUD
- Extend CRUDBase with `get_by_email(db, email)` method
- Hash passwords before storing (use simple hash for now, security feature later)

## Acceptance Criteria
- [ ] User model defines all columns with correct types and constraints
- [ ] Pydantic schemas validate input and serialize output correctly
- [ ] CRUDBase provides generic CRUD operations with type safety
- [ ] CRUDUser extends base with email lookup
- [ ] All schemas use `from_attributes = True`
- [ ] CRUD methods use flush() not commit()

## Testing Notes
- Standard testing depth
- Unit test schema validation (valid/invalid inputs)
- Unit test CRUD operations against test database
