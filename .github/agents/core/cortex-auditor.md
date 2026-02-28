# CORTEX Auditor

**Purpose:** 19-Point Production Readiness Scanning (Checks #1–#19)
**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`

**SSOT:** The canonical 19-Point audit checklist is defined in `.github/prompts/CORTEX.prompt.md` § 19-Point Production Readiness Audit.

**Stage:** `/audit fix` Stage 2

**Entry Point:** `AuditCoordinator` → `EnforcementOrchestrator`

**Trigger:** `/audit`, "scan", "check", "health"

**Scope:** Source code health — stale imports, stubs, duplicates, CORE rule violations, test quality, file hygiene, SQLite activity log health.

**Relationship to other agents:**
- `cortex-meta-auditor.md` — audits governance artifacts (prompts, agents, templates), NOT source code
- `architecture-integrity-agent.md` — validates wiring.yaml ↔ implementation alignment (L1→L3)
- `cortex-holistic-validator.md` — pre-implementation validation gate (CORE-048)

**Auto-Fix:** Stages 7–8 convergence loop repairs P0/P1 violations autonomously (via `detect-fix-rescan-loop.yaml` primitive).

**Activity Log:** Every stage → `.cortex-runtime/traces/orchestrator-traces.db`
...