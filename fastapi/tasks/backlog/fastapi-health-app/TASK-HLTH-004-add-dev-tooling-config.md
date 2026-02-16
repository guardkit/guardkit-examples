---
id: TASK-HLTH-004
title: "Add dev tooling configuration"
task_type: scaffolding
parent_review: TASK-REV-2214
feature_id: FEAT-HLTH
status: pending
created: 2026-02-16T14:30:00Z
priority: normal
wave: 2
implementation_mode: direct
complexity: 2
dependencies: [TASK-HLTH-001]
tags: [tooling, ruff, mypy, config]
---

# Task: Add dev tooling configuration

## Description

Configure development tooling for code quality: linter (ruff), type checker (mypy), and environment variable template. This ensures consistent code quality from the start.

## Files to Create

### 1. `.env.example`
- PROJECT_NAME=FastAPI App
- VERSION=0.1.0
- DEBUG=true
- API_V1_PREFIX=/api/v1

### 2. `.gitignore`
- Python patterns: __pycache__/, *.pyc, .venv/, *.egg-info/
- Environment: .env
- IDE: .vscode/, .idea/
- Testing: .coverage, htmlcov/
- OS: .DS_Store

### 3. Verify `pyproject.toml` tool sections (created in TASK-HLTH-001)
- `[tool.ruff]` - line-length=88, target-version="py39"
- `[tool.ruff.lint]` - select appropriate rules
- `[tool.mypy]` - strict=true, plugins for pydantic
- `[tool.pytest.ini_options]` - asyncio_mode="auto"

## Acceptance Criteria

- [ ] `.env.example` documents all environment variables
- [ ] `.gitignore` covers Python/IDE/OS patterns
- [ ] `ruff check src/` runs without configuration errors
- [ ] `mypy src/` runs without configuration errors

## Implementation Notes

- Reference `.claude/rules/code-style.md` for ruff configuration
- Keep .gitignore focused on what's actually in the project
- Ruff and mypy config should be in pyproject.toml (not separate files)
