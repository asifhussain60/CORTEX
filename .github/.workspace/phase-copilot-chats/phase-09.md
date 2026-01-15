# PHASE-09: Developer Governance Tooling

**Started:** 2026-01-15  
**Status:** IN_PROGRESS  
**Prerequisites:** PHASE-08-CORE-ORCHESTRATORS ✅ COMPLETED

---

## Phase Overview

**Objective:** Make governance utilities discoverable and usable through:
- CLI commands (query, validate)
- Agent prompts integration (2/2 DONE)
- Pre-commit hooks
- VS Code IDE integration
- Dashboard visualization

---

## Acceptance Criteria (8 AC-IDs)

### Completed (2/8)
| AC-ID | Title | Status |
|-------|-------|--------|
| GV-002-01 | Builder Prompt Integration | ✅ COMPLETED |
| GV-002-02 | Planner Prompt Integration | ✅ COMPLETED |

### Remaining (6/8)
| AC-ID | Title | Priority | Status |
|-------|-------|----------|--------|
| GV-001-01 | CLI Query Interface | HIGH | NOT_STARTED |
| GV-001-02 | CLI Validate Interface | HIGH | NOT_STARTED |
| GV-003-01 | Pre-Commit Hook | MEDIUM | NOT_STARTED |
| GV-003-02 | VS Code Integration | MEDIUM | NOT_STARTED |
| GV-004-01 | Governance Dashboard | HIGH | NOT_STARTED |
| GV-004-02 | Phase Readiness Checker | HIGH | NOT_STARTED |

---

## Implementation Plan

### Block 1: CLI Tools (GV-001-01, GV-001-02)

```bash
# Target: cortex-governance CLI
scripts/cortex-governance.py
  - query: cortex-governance query <rule-id|domain|phase>
  - validate: cortex-governance validate <path> [--phase] [--ac-id]
```

**Requirements:**
- Query returns rule details in <100ms
- Validate respects phase context
- Exit code reflects validation result

### Block 2: Pre-Commit (GV-003-01)

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: cortex-governance
      name: CORTEX Governance Validation
      entry: python scripts/cortex-governance.py validate
      language: python
      types: [python]
```

### Block 3: VS Code Integration (GV-003-02)

**Options:**
1. Language Server Protocol (LSP) extension
2. VS Code diagnostics via tasks
3. Custom extension with diagnostic provider

### Block 4: Dashboard & Readiness (GV-004-01, GV-004-02)

- Compliance heatmap by domain
- AC-ID coverage visualization
- 4-stage readiness checker:
  1. Governance validation
  2. Audit completeness
  3. Test coverage
  4. Documentation status

---

## Test Requirements

Each AC-ID requires:
- Unit tests in `tests/unit/tools/` or `tests/unit/dashboard/`
- Integration tests in `tests/integration/`
- Test count target: ~60 tests for phase

---

## Session Log

### 2026-01-15: Phase Preparation
- ✅ Reviewed phase-09.yaml requirements
- ✅ Confirmed PHASE-08 completion
- ✅ Fixed blocking test failures (recommendation engine, dashboard)
- ✅ 320 tests passing
- ⏳ Ready to begin GV-001-01 implementation

---

© 2025-2026 Asif Hussain. All rights reserved.
