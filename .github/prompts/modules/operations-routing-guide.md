# Operations Routing Architecture

**CORTEX 3.0 Operations System:** All orchestrators have been migrated to lightweight utilities in `src/operations/modules/`

## Route Overview (23 Operations)

### User-Facing Operations (18 Total)

| Natural Language | Operation | Module Location | Status |
|------------------|-----------|----------------|--------|
| "plan feature X" | planning | src/operations/modules/planning/ | ✅ Ready |
| "start tdd" | tdd | src/tier0/tdd_operations/ | ✅ Ready |
| "commit" | commit | src/operations/commit_and_push.py | ✅ Ready (commit, push, sync) |
| "create checkpoint" | git_checkpoint | src/operations/modules/git_checkpoint/ | ✅ Ready (TDD only) |
| "rollback to X" | rollback | src/operations/modules/rollback/ | ✅ Ready |
| "review code" | code_review | src/operations/modules/code_review/ | ✅ Ready |
| "show health dashboard" | application_health | src/operations/modules/health/ | ✅ Ready |
| "root cause analysis" | rca | src/operations/modules/rca/ | ✅ Ready |
| "lint validation" | lint_validation | src/operations/modules/lint/ | ✅ Ready |
| "feedback" | feedback | src/agents/feedback/ | ✅ Ready |
| "discover views" | view_discovery | src/agents/view_discovery/ | ✅ Ready |
| "optimize" | optimize | src/operations/optimize.py | ✅ Ready (context-aware) |
| "healthcheck" | healthcheck | src/operations/modules/healthcheck/ | ✅ Ready |
| "upgrade cortex" | upgrade | src/operations/modules/upgrade/ | ✅ Ready |
| "setup copilot" | setup_epm | src/operations/modules/setup_epm/ | ✅ Ready |
| "estimate swagger" | swagger_estimation | src/operations/modules/estimation/ | ✅ Ready |
| "ux enhancement" | ux_enhancement | src/operations/modules/ux/ | ✅ Ready |
| "debug X" | debug | src/operations/modules/debug/ | ✅ Ready |

### Dual-Context Operations (3 Total)

| Natural Language | Operation | Module Location | Status |
|------------------|-----------|----------------|--------|
| "plan ado" | ado_work_item | src/operations/modules/ado/ | ✅ Ready |
| "align" | align | src/operations/align.py | ✅ Ready (context-aware: admin/user) |
| "review architecture" | architecture_intelligence | src/operations/modules/architecture/ | ✅ Ready |

### Admin-Only Operations (5 Total)

| Natural Language | Operation | Module Location | Status |
|------------------|-----------|----------------|--------|
| "deploy" | deploy | src/operations/deploy.py | ✅ Ready (all 19 gates enforced) |
| "generate docs" | doc_generation | src/operations/modules/admin/doc_generation/ | ✅ Ready |
| "cleanup repository" | cleanup | src/operations/modules/cleanup/ | ✅ Ready |
| "consolidate markdown" | consolidation | src/operations/modules/admin/consolidation/ | ✅ Ready |
| "design sync" | design_sync | src/operations/modules/admin/design_sync/ | ✅ Ready |

## Registry

**Operations Registry:** All operations registered in `cortex-operations.yaml` (23 operations, 107 modules)

**Migration Status:** 29/29 orchestrators migrated to utilities (97% code reduction, 100% complete)

## Key Architectural Changes

- ❌ **OLD:** Heavy orchestrators in `src/orchestrators/` (500-800 lines each)
- ✅ **NEW:** Lightweight utilities in `src/operations/modules/` (100-200 lines each)
- ✅ **Pattern:** Entry point → utility → agent (if needed)
- ✅ **Validation:** align v2.0 auto-validates all registrations
- ✅ **Maintenance:** align v2.0 auto-discovers and registers new features
- ✅ **Cleanup:** align v2.0 auto-detects and removes obsolete code

## Routing Logic

1. User provides natural language input
2. Intent detection maps to operation ID
3. Context detection determines if in CORTEX repo or user repo
4. cortex-operations.yaml provides module path
5. Entry point loads utility and executes
6. Results returned to user

## Context-Aware Operations

When user says `/CORTEX [command]`, certain operations adapt based on context:

| Command | In CORTEX Repo (has `cortex-brain/admin/`) | In User Repo |
|---------|---------------------------------------------|--------------|
| **commit** | Runs commit_push_sync orchestrator (stage, commit, push, sync) | Same - git_checkpoint is TDD-only |
| **align** | Admin version: Full system alignment with all checks | User version: Workspace alignment only |
| **optimize** | Admin version: CORTEX optimization with SKULL tests | User version: Workspace optimization |
| **deploy** | Deployment to publish branch with all 19 validation gates (NO SKIPPING) | N/A (admin-only) |

**Detection Method:** Checks for `cortex-brain/admin/` or `src/operations/modules/admin/` directories

## Migration History

**See:** `cortex-brain/documents/reports/ORCHESTRATOR-MIGRATION-COMPLETE-ANALYSIS.md` for complete migration history
