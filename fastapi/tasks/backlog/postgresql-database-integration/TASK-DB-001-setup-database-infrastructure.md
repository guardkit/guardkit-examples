---
id: TASK-DB-001
title: Set up database infrastructure
task_type: scaffolding
parent_review: TASK-REV-A405
feature_id: FEAT-A405
status: pending
priority: high
wave: 1
implementation_mode: task-work
complexity: 6
dependencies: []
tags: [database, postgresql, sqlalchemy, docker]
---

# Task: Set up database infrastructure

## Description

Create the core database infrastructure layer for PostgreSQL integration using SQLAlchemy 2.0 async with asyncpg driver. This includes engine configuration, session management, base model, application settings, and Docker Compose for local development.

## Scope

### Files to Create
- `src/db/__init__.py` - Package init
- `src/db/base.py` - SQLAlchemy DeclarativeBase class
- `src/db/session.py` - Async engine, session factory, and `get_db()` dependency
- `docker-compose.yml` - PostgreSQL 16 service for local development
- `.env.example` - Environment variable template with DATABASE_URL

### Files to Modify
- `src/core/config.py` - Add DATABASE_URL setting with PostgresDsn validation
- `pyproject.toml` - Add sqlalchemy[asyncio], asyncpg, alembic dependencies
- `src/main.py` - Add lifespan handler for engine disposal on shutdown

## Technical Requirements

### Engine Configuration
- Use `create_async_engine` with `postgresql+asyncpg://` connection string
- Connection pooling: `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=3600`
- SQL echo enabled when `DEBUG=True`

### Session Factory
- Use `async_sessionmaker` with `expire_on_commit=False`, `autocommit=False`, `autoflush=False`
- `get_db()` generator dependency with auto-commit on success, rollback on exception

### Docker Compose
- PostgreSQL 16 Alpine image
- Named volume for data persistence
- Port 5432 exposed
- Default credentials matching `.env.example`

### DeclarativeBase
- Use SQLAlchemy 2.0 `DeclarativeBase` pattern (not legacy `declarative_base()`)

## Acceptance Criteria
- [ ] `docker compose up -d db` starts PostgreSQL successfully
- [ ] SQLAlchemy engine connects to PostgreSQL via asyncpg
- [ ] `get_db()` dependency yields async session with auto-commit/rollback
- [ ] Connection pool configured with specified parameters
- [ ] Settings load DATABASE_URL from environment/.env file
- [ ] Engine properly disposed on application shutdown

## Testing Notes
- Standard testing depth (quality gates, 80% coverage target)
- Test engine creation and session factory configuration
- Test `get_db()` dependency yields and cleanup behavior

## Library Context
```yaml
library_context:
  - name: sqlalchemy
    import: "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker"
  - name: asyncpg
    import: "# Installed as driver, no direct import needed"
  - name: pydantic-settings
    import: "from pydantic_settings import BaseSettings"
```
