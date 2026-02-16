# Implementation Guide: API Documentation

**Feature**: Add comprehensive API documentation with Swagger UI, ReDoc, and OpenAPI schema customization
**Feature ID**: FEAT-DOCS
**Parent Review**: TASK-REV-AB87
**Approach**: Option 1 - Centralized OpenAPI Configuration Module
**Total Complexity**: 5/10
**Estimated Effort**: 5 tasks across 3 waves

---

## Data Flow: Read/Write Paths

This is the most important diagram - it shows every write and read path for this feature.

```mermaid
flowchart LR
    subgraph Writes["Write Paths"]
        W1["Client HTTP Request\nAny API endpoint"]
        W2["App Startup\nFastAPI initialization"]
    end

    subgraph Config["Configuration"]
        C1[("Settings\nsrc/core/config.py\n(Pydantic BaseSettings)")]
    end

    subgraph Processing["Processing Layer"]
        P1["APIVersionMiddleware\nsrc/core/middleware.py"]
        P2["custom_openapi()\nsrc/core/openapi.py"]
        P3["Pydantic Schemas\nmodel_config examples"]
    end

    subgraph Reads["Read Paths"]
        R1["API Response\nX-API-Version header"]
        R2["GET /docs\nSwagger UI HTML"]
        R3["GET /redoc\nReDoc HTML"]
        R4["GET /openapi.json\nCustomized OpenAPI schema"]
    end

    W1 -->|"every request"| P1
    P1 -->|"reads API_VERSION"| C1
    P1 -->|"adds header"| R1

    W2 -->|"on first /docs access"| P2
    P2 -->|"reads title, version, desc"| C1
    P2 -->|"merges examples from"| P3
    P2 -->|"generates schema"| R4

    R4 -->|"rendered by"| R2
    R4 -->|"rendered by"| R3

    style W1 fill:#cfc,stroke:#090
    style W2 fill:#cfc,stroke:#090
    style R1 fill:#cfc,stroke:#090
    style R2 fill:#cfc,stroke:#090
    style R3 fill:#cfc,stroke:#090
    style R4 fill:#cfc,stroke:#090
```

_All paths are connected. No disconnections detected. Settings flow from config to middleware and OpenAPI module. The OpenAPI JSON schema feeds both Swagger UI and ReDoc renderers._

---

## Integration Contracts

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant MW as APIVersionMiddleware
    participant Router as FastAPI Router
    participant Schema as Pydantic Schema
    participant OA as custom_openapi()
    participant Settings as Settings

    Note over Client,Settings: Standard API Request Flow
    Client->>MW: GET /api/v1/health
    MW->>Settings: read API_VERSION
    MW->>Router: dispatch(request)
    Router->>Schema: validate response
    Schema-->>Router: HealthResponse (with examples in schema)
    Router-->>MW: Response
    MW-->>Client: Response + X-API-Version header

    Note over Client,Settings: Documentation Request Flow
    Client->>Router: GET /docs
    Router->>OA: app.openapi() (first call)
    OA->>Settings: read API_TITLE, API_VERSION, API_DESCRIPTION
    OA->>Router: get routes for schema
    OA-->>Router: Customized OpenAPI JSON (cached)
    Router-->>Client: Swagger UI HTML (renders schema)

    Note over Client,Settings: Schema includes response examples
    Client->>Router: GET /openapi.json
    Router->>OA: app.openapi() (cached)
    OA-->>Router: Cached schema with examples
    Router-->>Client: OpenAPI JSON with examples + tags + metadata
```

---

## Task Dependency Graph

```mermaid
graph TD
    T1["TASK-DOCS-001\nAdd documentation settings\n(scaffolding, complexity: 2)"] --> T2["TASK-DOCS-002\nCreate OpenAPI customization\n(feature, complexity: 4)"]
    T1 --> T3["TASK-DOCS-003\nAdd versioning middleware\n(feature, complexity: 3)"]
    T1 --> T4["TASK-DOCS-004\nAdd response examples\n(feature, complexity: 3)"]
    T2 --> T5["TASK-DOCS-005\nDocumentation tests\n(testing, complexity: 3)"]
    T3 --> T5
    T4 --> T5

    style T2 fill:#cfc,stroke:#090
    style T3 fill:#cfc,stroke:#090
    style T4 fill:#cfc,stroke:#090
```

_Tasks with green background (TASK-DOCS-002, TASK-DOCS-003, TASK-DOCS-004) can run in parallel in Wave 2._

---

## Execution Strategy

### Wave 1: Configuration Foundation (Sequential - must complete first)

| Task | Name | Mode | Complexity |
|------|------|------|-----------|
| TASK-DOCS-001 | Add documentation settings | direct | 2 |

Modifies: `src/core/config.py`, `.env.example`

### Wave 2: Feature Implementation (Parallel - no file conflicts)

| Task | Name | Mode | Complexity |
|------|------|------|-----------|
| TASK-DOCS-002 | Create OpenAPI schema customization | task-work | 4 |
| TASK-DOCS-003 | Add API versioning middleware | task-work | 3 |
| TASK-DOCS-004 | Add response examples to schemas | task-work | 3 |

- TASK-DOCS-002 creates: `src/core/openapi.py`, modifies `src/main.py`
- TASK-DOCS-003 creates: `src/core/middleware.py`, modifies `src/main.py`
- TASK-DOCS-004 creates: `src/core/schemas.py`, modifies `src/health/schemas.py`, `src/health/router.py`
- **Note**: TASK-DOCS-002 and TASK-DOCS-003 both modify `src/main.py` but touch different sections (OpenAPI config vs middleware registration). If using parallel execution, the last task to merge should resolve any conflicts in `src/main.py`.

### Wave 3: Testing (Sequential - depends on all Wave 2 tasks)

| Task | Name | Mode | Complexity |
|------|------|------|-----------|
| TASK-DOCS-005 | Add documentation and versioning tests | task-work | 3 |

Creates: `tests/core/test_openapi.py`, `tests/core/test_middleware.py`

---

## Architecture Notes

### Project Structure (After Implementation)

```
src/
├── core/
│   ├── config.py           # Extended with docs settings (TASK-DOCS-001)
│   ├── openapi.py          # Custom OpenAPI schema (TASK-DOCS-002)
│   ├── middleware.py        # API versioning middleware (TASK-DOCS-003)
│   └── schemas.py          # Shared error response schemas (TASK-DOCS-004)
├── health/
│   ├── router.py           # Updated with response examples (TASK-DOCS-004)
│   └── schemas.py          # Updated with model_config examples (TASK-DOCS-004)
└── main.py                 # Updated to wire OpenAPI + middleware (TASK-DOCS-002, 003)

tests/
└── core/
    ├── test_openapi.py     # OpenAPI schema + docs tests (TASK-DOCS-005)
    └── test_middleware.py   # Versioning header tests (TASK-DOCS-005)
```

### Key Design Decisions

1. **Centralized OpenAPI module** - Single `custom_openapi()` function in `src/core/openapi.py` for all schema customization. Uses FastAPI's native `get_openapi()` utility with caching.
2. **Settings-driven config** - All documentation values (title, version, URLs) configurable via environment variables through Pydantic BaseSettings.
3. **Middleware for versioning** - `X-API-Version` header applied globally via ASGI middleware, not per-route. Ensures consistency across all endpoints.
4. **Co-located examples** - Response examples defined in Pydantic `model_config` alongside the schema definition, not in separate files. Keeps examples in sync with schema changes.
5. **No external dependencies** - All features use FastAPI/Starlette built-in capabilities. Zero new packages required.

### Extension Points

When adding new features:
- Add tag metadata to `Settings.API_TAGS_METADATA` for new endpoint groups
- Follow the `model_config` + `json_schema_extra` pattern for response examples on new schemas
- Add `responses` parameter to routes for error documentation
- The versioning middleware automatically covers all new endpoints
