---
id: TASK-LOG-001
title: Create logging configuration module
task_type: scaffolding
parent_review: TASK-REV-CABA
feature_id: FEAT-LOG
status: pending
priority: high
wave: 1
implementation_mode: task-work
complexity: 4
dependencies: []
tags: [logging, structlog, configuration]
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Create logging configuration module

## Description
Create `src/core/logging.py` with structlog processor pipeline configuration. This is the foundation module that all other logging tasks depend on.

## Requirements
1. Configure structlog with the following processor pipeline:
   - `structlog.contextvars.merge_contextvars` (merge request-scoped context)
   - `structlog.stdlib.filter_by_level` (respect log level settings)
   - `structlog.stdlib.add_logger_name` (include logger name)
   - `structlog.processors.add_log_level` (include level in output)
   - `structlog.processors.TimeStamper(fmt="iso", utc=True)` (ISO timestamps)
   - `structlog.processors.StackInfoRenderer()` (stack traces)
   - `structlog.processors.format_exc_info` (exception formatting)
   - `structlog.processors.UnicodeDecoder()` (unicode handling)
   - Environment-based renderer (JSON for production, Console for development)

2. Create a `setup_logging()` function that:
   - Accepts environment name and log level as parameters
   - Configures structlog with appropriate renderer
   - Configures stdlib logging integration (for third-party libraries)
   - Sets root log level based on configuration
   - Returns configured logger

3. Provide a `get_logger()` convenience function that returns a bound structlog logger

## Acceptance Criteria
- [ ] `src/core/logging.py` exists with `setup_logging()` and `get_logger()` functions
- [ ] JSON output in production environment (structlog.processors.JSONRenderer)
- [ ] Colored console output in development (structlog.dev.ConsoleRenderer)
- [ ] stdlib logging integration configured (third-party lib logs captured)
- [ ] Type hints on all public functions
- [ ] Module imports without errors

## Technical Notes
- Use `structlog.stdlib.BoundLogger` as wrapper class
- Use `structlog.stdlib.LoggerFactory()` as logger factory
- Set `cache_logger_on_first_use=True` for performance
- Configure stdlib logging to route through structlog processors

## Files to Create/Modify
- `src/core/logging.py` (new)
