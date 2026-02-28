# CORTEX Auditor

**Purpose:** 20-Point Production Readiness Scanning (Checks #1–#20)
**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`

**SSOT:** The canonical 20-Point audit checklist is defined in `.github/prompts/cortex-architect.prompt.md` § 20-Point Production Readiness Audit.

**Stage:** `/audit fix` Stage 2

**Entry Point:** `AuditCoordinator` → `EnforcementOrchestrator`

**Trigger:** `/audit`, "scan", "check", "health"

**Scope:** Source code health — stale imports, stubs, duplicates, CORE rule violations, test quality, file hygiene, SQLite activity log health, **Workflow Composer pipeline health** (Check #20).

**Check #20 — Workflow Composer Pipeline Health:**
- WorkflowComposer importable from `cortex.orchestrators.workflow.workflow_composer`
- TemplateComposer functional from `cortex.orchestrators.workflow.template_composer`
- ConvergenceLoopExecutor wired via workflow primitives
- ToolchainExecutor maps ≥8 file extensions (.py, .cs, .ts, .tsx, .js, .jsx, .html, .css)
- Template auto-discovery coverage ≥50% (currently 9/96 = 9% — P1 gap)
- tree-sitter version ≥0.21.0 (aligned with requirements.txt)
- WORKFLOW_COMPOSE IntentType wired in IntentRouter.operation_type_mappings
- WorkflowComplexityRouter._select_orchestrator() includes `workflow_compose` key

**Relationship to other agents:**
- `cortex-meta-auditor.md` — audits governance artifacts (prompts, agents, templates), NOT source code
- `architecture-integrity-agent.md` — validates wiring.yaml ↔ implementation alignment (L1→L3)
- `cortex-holistic-validator.md` — pre-implementation validation gate (CORE-048)

**Auto-Fix:** Stages 7–8 convergence loop repairs P0/P1 violations autonomously (via `detect-fix-rescan-loop.yaml` primitive).

**Activity Log:** Every stage → `.cortex-runtime/traces/orchestrator-traces.db`
...