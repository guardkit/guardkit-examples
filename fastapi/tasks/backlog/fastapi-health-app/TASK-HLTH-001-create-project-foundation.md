---
id: TASK-HLTH-001
title: "Create project foundation"
task_type: scaffolding
parent_review: TASK-REV-2214
feature_id: FEAT-HLTH
status: pending
created: 2026-02-16T14:30:00Z
priority: high
wave: 1
implementation_mode: task-work
complexity: 3
dependencies: []
tags: [foundation, setup, fastapi]
---

# Task: Create project foundation

## Description

Set up the core project files needed to run a FastAPI application. This creates the minimal foundation that all other tasks depend on.

## Files to Create

### 1. `pyproject.toml`
- Project metadata (name, version, description)
- Dependencies: fastapi>=0.104.0, uvicorn[standard], pydantic-settings>=2.0.0
- Dev dependencies: pytest>=7.4.0, pytest-asyncio>=0.21.0, httpx>=0.25.0, pytest-cov
- Ruff and mypy configuration sections
- pytest configuration (asyncio_mode = "auto")

### 2. `src/__init__.py`
- Empty init file for the src package

### 3. `src/core/__init__.py`
- Empty init file

### 4. `src/core/config.py`
- Pydantic BaseSettings class `Settings`
- Fields: PROJECT_NAME, VERSION, API_V1_PREFIX="/api/v1", DEBUG=False
- Environment variable loading from .env file
- Singleton `settings = Settings()` instance

### 5. `src/main.py`
- FastAPI app initialization with title, version from settings
- CORS middleware configuration
- Include health router under API prefix
- Root endpoint redirecting to docs (optional)

### 6. `requirements/base.txt`
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- pydantic-settings>=2.0.0

### 7. `requirements/dev.txt`
- -r base.txt
- pytest>=7.4.0
- pytest-asyncio>=0.21.0
- httpx>=0.25.0
- pytest-cov>=4.1.0
- ruff>=0.1.0
- mypy>=1.7.0

## Acceptance Criteria

- [ ] `pyproject.toml` exists with correct dependencies and tool config
- [ ] `src/main.py` creates a FastAPI app instance
- [ ] `src/core/config.py` loads settings from environment
- [ ] `requirements/base.txt` and `requirements/dev.txt` are populated
- [ ] App can be imported without errors: `from src.main import app`

## Implementation Notes

- Follow the template patterns in `.claude/templates/`
- Use Pydantic v2 syntax (model_config = SettingsConfigDict)
- Keep config minimal - no database, auth, or redis settings yet
- Reference `.claude/rules/code-style.md` for naming conventions
