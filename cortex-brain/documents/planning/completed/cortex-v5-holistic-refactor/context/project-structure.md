# CORTEX v5 Project Structure

**Created:** January 2, 2026  
**Phase:** 0 - Foundation Setup  
**Purpose:** Document new directory organization for v5 architecture

---

## New Directory Structure

### Source Code (`src/`)

```
src/
├── mcp/                         # MCP protocol layer (Phase 1)
│   ├── server.py               # MCP v1.0 protocol server
│   ├── registry.py             # Orchestrator registration
│   └── tools/                  # MCP tools
│       └── invoke_orchestrator.py
│
├── database/                    # SQLite state management (Phase 2)
│   ├── planning_state_db.py    # Database manager class
│   ├── planning_state_schema.sql
│   ├── migration_runner.py
│   └── migrations/             # Version-controlled migrations
│       └── 001_initial_schema.sql
│
├── orchestrators/
│   ├── base_orchestrator_v4_1.py    # Config-driven base (Phase 3)
│   ├── planning_orchestrator_v5.py  # Pure autonomous planning (Phase 4)
│   └── ...existing orchestrators...
│
└── utils/
    └── file_name.py            # Filename validation (≤20 chars, kebab-case)
```

### Configuration (`cortex-brain/`)

```
cortex-brain/
├── database/                    # SQLite database files
│   └── planning_state.db
│
├── config/
│   └── mcp-server.yaml         # MCP server configuration
│
└── templates/                   # Jinja2 templates (Phase 4)
    └── planning/
        ├── master-plan.jinja2
        ├── progress-tracker.json.jinja2
        └── context-summary.md.jinja2
```

### Tests (`tests/`)

```
tests/
├── mcp/                        # MCP protocol tests
│   ├── test_server.py
│   ├── test_registry.py
│   └── test_invoke_orchestrator.py
│
├── database/                   # Database layer tests
│   ├── test_planning_state_db.py
│   └── test_migrations.py
│
├── orchestrators/
│   ├── test_base_orchestrator_v4_1.py
│   └── test_planning_v5.py
│
├── utils/
│   └── test_file_name.py       # Filename validation tests
│
└── integration/                # End-to-end tests
    ├── test_planning_workflow.py
    ├── test_orchestrator_migrations.py
    └── test_mcp_invocation.py
```

---

## Design Principles

### Separation of Concerns
- **MCP layer**: Protocol communication only
- **Database layer**: State persistence with ACID guarantees
- **Orchestrator layer**: Business logic execution
- **Utils layer**: Shared utilities (filename validation, etc.)

### Configuration-Driven
- Manifests contain only data structures (YAML)
- Python code contains all execution logic
- Templates for content generation (Jinja2)

### Testability
- Each layer has dedicated test suite
- Integration tests verify end-to-end workflows
- 100% coverage requirement for new code

---

## Migration Strategy

### Phase 0 (Current)
- Create empty directory structure
- Add `.gitkeep` files for version control
- Document organization

### Phase 1-4 (Bootstrap)
- Incrementally populate directories
- Build Planning System v5 first
- Use v5 to plan remaining migrations

### Phase 5+ (Migrations)
- Use Planning System v5 to generate detailed plans
- Execute orchestrator migrations systematically
- Maintain parallel structure during transition

---

## File Naming Standards

**Enforced by:** `src/utils/file_name.py`

### Rules
- Maximum 20 characters (excluding extension)
- Kebab-case format: `word-word-word`
- No special characters except hyphens
- Descriptive but concise names

### Examples
```
✅ plan-orch-v5.py
✅ mcp-server.yaml
✅ file-name.py

❌ planning_orchestrator_version_5.py (too long, uses underscores)
❌ MCPServer.yaml (wrong case)
❌ filename@v2.py (special character)
```

---

## Integration Points

### BaseOrchestrator v4.1
- Loads config from manifests
- Uses MCP for invocation
- Stores state in database
- Renders templates for output

### Planning System v5
- Pure Python implementation
- Config-only manifest
- Database state tracking
- Template-driven plans

### Agent Layer
- Queries planning state database
- Invokes orchestrators via MCP
- Configuration externalized to YAML

---

**Status:** ✅ Task 0.1 Complete - Directory structure created
**Next:** Task 0.2 - Implement filename validation utility
