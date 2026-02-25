# ADR-004: Package Separation (cortex/ vs cortex_brain/)

> Architecture Decision Record

**Status:** Accepted  
**Date:** 2026-01-19  
**Deciders:** CORTEX Architecture Team  
**Technical Story:** PHASE-ARCH-ALIGNMENT-001

## Context

CORTEX originally had code spread across multiple locations (`src/`, `cortex/`, `cortex_brain/`, `cortex_toolkit/`). A decision was needed on canonical package structure.

## Decision

Establish two canonical packages with distinct responsibilities:

### Package Structure

```
cortex/                    # Application code (413 files)
├── api/                   # API layer
├── core/                  # Core business logic
├── mcp/                   # MCP server and tools
├── orchestrators/         # Domain orchestrators
└── ...

cortex_brain/              # State and governance (41 files)
├── tier0/                 # Core governance rules
├── tier1/                 # Domain rules
├── tier2/                 # Context rules
├── tier3/                 # Runtime rules
├── state/                 # governance.db + runtime state
└── governance/            # Governance utilities
```

### Separation Principle

| Package | Responsibility | Persistence |
|---------|---------------|-------------|
| `cortex/` | Business logic, APIs, tools | Code only |
| `cortex_brain/` | State, governance, rules | Data + code |

### Forbidden Patterns

```yaml
forbidden_patterns:
  - "cortex_toolkit/"      # Deleted
  - "src/"                 # Consolidated to cortex/
  - "Multiple impl folders"
```

## Consequences

### Positive

- Clear separation of concerns
- Single source of truth for code (`cortex/`)
- Single source of truth for state (`cortex_brain/`)
- Easier backup/restore of state
- Cleaner import paths

### Negative

- Migration effort from old structure
- Some circular dependency risk between packages
- Two packages to manage instead of one

### Migration Impact

| Old Location | New Location | Files Moved |
|--------------|--------------|-------------|
| `src/core/` | `cortex/core/` | ~150 |
| `src/orchestrators/` | `cortex/orchestrators/` | ~50 |
| `cortex_toolkit/` | Deleted | N/A |

## Alternatives Considered

1. **Single package** - Rejected: Mixes code with state
2. **Three packages** - Rejected: Unnecessary complexity
3. **Keep src/** - Rejected: Python convention is package at root

## Verification

```bash
# Verify no forbidden patterns
find . -type d -name "cortex_toolkit" | wc -l  # Should be 0
find . -type d -name "src" -not -path "./.git/*" | wc -l  # Should be 0
```

## Related

- [Architecture Overview](../_diagrams/architecture-overview.mmd)
- `cortex-impl-map.yaml` architecture section
- Phase consolidation-001-src-cleanup
