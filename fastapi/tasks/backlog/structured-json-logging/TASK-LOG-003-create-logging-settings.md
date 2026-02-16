---
id: TASK-LOG-003
title: Create logging settings configuration
task_type: scaffolding
parent_review: TASK-REV-CABA
feature_id: FEAT-LOG
status: pending
priority: high
wave: 1
implementation_mode: direct
complexity: 3
dependencies: []
tags: [logging, configuration, settings]
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Create logging settings configuration

## Description
Add logging-related configuration fields to the application settings, enabling per-environment log level control and logging behavior customization.

## Requirements
1. Add logging fields to `src/core/config.py` Settings class (or create if not exists):
   - `LOG_LEVEL`: str = "INFO" (configurable: DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - `LOG_FORMAT`: str = "json" (options: "json", "console")
   - `LOG_INCLUDE_TIMESTAMP`: bool = True
   - `LOG_EXCLUDE_PATHS`: list[str] = ["/health", "/ready"] (paths with reduced logging)

2. Environment-based defaults:
   - `development`: LOG_LEVEL="DEBUG", LOG_FORMAT="console"
   - `staging`: LOG_LEVEL="INFO", LOG_FORMAT="json"
   - `production`: LOG_LEVEL="WARNING", LOG_FORMAT="json"

3. All settings loadable from environment variables (Pydantic BaseSettings)

## Acceptance Criteria
- [ ] Logging settings fields added to Settings class
- [ ] LOG_LEVEL validates against allowed values
- [ ] LOG_FORMAT validates against "json" and "console"
- [ ] Environment variables override defaults (e.g., LOG_LEVEL=DEBUG)
- [ ] LOG_EXCLUDE_PATHS configurable as comma-separated string or JSON array
- [ ] Type hints and field descriptions on all settings

## Technical Notes
- Use Pydantic field validators for LOG_LEVEL validation
- Use `field_validator` for parsing LOG_EXCLUDE_PATHS from comma-separated env var
- Follow existing Settings pattern from config.py template

## Files to Create/Modify
- `src/core/config.py` (modify or create)
