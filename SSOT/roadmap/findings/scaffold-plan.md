# CORTEX 7.0 Scaffold Plan

**Date:** 2026-01-14  
**Purpose:** Clean folder structure from scratch  
**Source:** `__backup/` folder (to be deleted after migration)

---

## Target Structure (AR-010 Compliant)

```
CORTEX/
├── cortex-brain/                    # Governance + Knowledge
│   ├── tier0/                       # IMMUTABLE - SKULL rules
│   │   ├── governance/              # Core governance YAML
│   │   └── schemas/                 # JSON schemas
│   ├── tier1/                       # Business rules + tracking
│   │   ├── acceptance-criteria/     # AC-INDEX.yaml
│   │   ├── governance/              # Business rules YAML
│   │   └── tracking/                # Progress tracker
│   ├── tier2/                       # Engineering standards
│   │   ├── response-templates/      # Response template system
│   │   └── templates/               # Code templates
│   ├── tier3/                       # Knowledge (advisory)
│   ├── audit-logs/                  # Audit trail storage
│   ├── config/                      # Configuration files
│   ├── registry/                    # Orchestrator registry
│   └── state/                       # State persistence
│
├── src/                             # Source code
│   ├── core/                        # Shared utilities (NEW)
│   │   ├── __init__.py
│   │   ├── interfaces.py            # Abstract base classes
│   │   ├── result.py                # Result[T] pattern
│   │   ├── config.py                # Unified config loader
│   │   ├── path_resolver.py         # Portable path resolution
│   │   └── yaml_loader.py           # Single YAML implementation
│   ├── infrastructure/              # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── audit_logger.py          # EnhancedAuditLogger
│   │   ├── hash_chain.py            # Hash chain integrity
│   │   └── governance_registry.py   # GovernanceRegistry
│   ├── orchestrators/               # Orchestrator layer
│   │   ├── core/                    # Core orchestrators
│   │   ├── domain/                  # Domain orchestrators
│   │   └── custom/                  # Plugin orchestrators
│   ├── mcp/                         # MCP tools
│   │   ├── __init__.py
│   │   ├── decorator.py             # @mcp_tool decorator
│   │   ├── registry.py              # OrchestratorRegistry
│   │   └── tools/                   # Individual tools
│   ├── tools/                       # CLI tools
│   │   ├── __init__.py
│   │   └── toolkit.py               # Unified entry point
│   └── __init__.py
│
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   ├── fixtures/                    # Test fixtures
│   ├── conftest.py                  # Pytest configuration
│   └── pytest.ini                   # Pytest settings
│
├── SSOT/                            # Single Source of Truth
│   ├── roadmap/                     # Roadmap documents
│   │   ├── roadmap.yaml             # Machine SSOT
│   │   ├── roadmap.md               # Human roadmap
│   │   └── findings/                # Analysis findings
│   └── analysis/                    # Analysis files
│
├── .github/                         # GitHub configuration
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
└── README.md                        # Project README
```

---

## Migration Strategy

### Phase 1: Create Empty Structure
Create all directories with `__init__.py` files.

### Phase 2: Migrate Essential Files Only

**From `__backup/cortex-brain/tier0/`:**
- `governance/core-rules.yaml` → Core SKULL rules
- `governance-schema.sql` → Database schema
- `schemas/` → JSON validation schemas

**From `__backup/cortex-brain/tier1/`:**
- `acceptance-criteria/AC-INDEX.yaml` → AC tracking
- `tracking/progress-tracker.json` → Progress state

**From `__backup/src/infrastructure/`:**
- `enhanced_audit_logger.py` → Audit logging (rename to audit_logger.py)

**From `__backup/src/mcp/`:**
- `mcp_decorator.py` → MCP tool decorator (rename to decorator.py)
- `registry.py` → Orchestrator registry

**From `__backup/src/orchestrators/`:**
- `master_orchestrator.py` → Master orchestrator (refactor hardcoded paths)

**From `__backup/tests/`:**
- `conftest.py` → Pytest configuration
- `pytest.ini` → Pytest settings

### Phase 3: Create New Core Module
New files following SOLID/DRY principles:
- `src/core/interfaces.py` - Abstract base classes
- `src/core/result.py` - Result[T] pattern
- `src/core/config.py` - Unified configuration
- `src/core/path_resolver.py` - Portable paths
- `src/core/yaml_loader.py` - Single YAML loader

### Phase 4: Delete __backup
After verification, remove `__backup/` folder entirely.

---

## Files NOT to Migrate

The following are intentionally excluded:
- All files with hardcoded `/Users/asifhussain` paths (fix first or exclude)
- Duplicate implementations
- Legacy CORTEX 5.x code
- Temporary/generated files
- Archive folders
- Dashboard HTML files (regenerate later)

---

## Acceptance Criteria

- [ ] `cortex-brain/` exists with tier0-3 subfolders
- [ ] `src/` exists with clean module structure
- [ ] `src/core/` contains shared utilities
- [ ] `tests/` exists with conftest.py and pytest.ini
- [ ] Zero hardcoded paths in migrated files
- [ ] All `__init__.py` files created
- [ ] `__backup/` folder deleted
- [ ] `python -c "import src"` succeeds
