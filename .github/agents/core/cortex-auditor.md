# CORTEX Auditor

**Purpose:** 24-Point Production Readiness Scanning (Checks #1–#24)
**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`

**SSOT:** The canonical 24-Point audit checklist is defined in `.github/prompts/cortex-architect.prompt.md` § 24-Point Production Readiness Audit.

**Stage:** `/audit fix` Stage 2

**Entry Point:** `AuditCoordinator` → `EnforcementOrchestrator`

**Trigger:** `/audit`, "scan", "check", "health"

**Scope:** Source code health — stale imports, stubs, duplicates, CORE rule violations, test quality, file hygiene, SQLite activity log health, **Workflow Composer pipeline health** (Check #20), **F811 duplicate method definitions** (Check #22), **F401 unused import sweep** (Check #23), **OS artifact contamination** (Check #24).

**Check #20 — Workflow Composer Pipeline Health:**
- WorkflowComposer importable from `cortex.orchestrators.workflow.workflow_composer`
- TemplateComposer functional from `cortex.orchestrators.workflow.template_composer`
- ConvergenceLoopExecutor wired via workflow primitives
- ToolchainExecutor maps ≥8 file extensions (.py, .cs, .ts, .tsx, .js, .jsx, .html, .css)
- Template auto-discovery coverage ≥50% (currently 9/96 = 9% — P1 gap)
- tree-sitter version ≥0.21.0 (aligned with requirements.txt)
- WORKFLOW_COMPOSE IntentType wired in IntentRouter.operation_type_mappings
- WorkflowComplexityRouter._select_orchestrator() includes `workflow_compose` key

**Check #22 — F811 Duplicate Method Definitions:**
- `python3 -m ruff check cortex/ --select=F811 --output-format=concise` must return `All checks passed!`
- Python silently uses the last definition; earlier defs are invisible dead code
- Auto-fix: remove the first (dead) definition, retain the second (Python-active) one

**Check #23 — F401 Unused Import Sweep:**
- `python3 -m ruff check cortex/ --select=F401 --fix` (auto-safe for non-`__init__.py` files)
- Residual non-init violations must be manually triaged as intentional (mock-dependent / try-except guarded)
- Target: 0 non-intentional unused imports

**Check #24 — OS Artifact Contamination:**
- `.DS_Store`, `.ds-store`, `Thumbs.db`, `desktop.ini`: `find . -name ".DS_Store" -o -name "Thumbs.db" | wc -l` → must be 0
- `.NET bin/obj` under `cortex/`: `find cortex/ -type d \( -name "bin" -o -name "obj" \) | wc -l` → must be 0
- Auto-fix: `VacuumOrchestrator.run_os_artifact_cleanup()` + `run_build_artifact_cleanup()` — both invoked automatically in `/vacuum`

**Relationship to other agents:**
- `cortex-meta-auditor.md` — audits governance artifacts (prompts, agents, templates), NOT source code
- `architecture-integrity-agent.md` — validates wiring.yaml ↔ implementation alignment (L1→L3)
- `cortex-holistic-validator.md` — pre-implementation validation gate (CORE-048)

**Auto-Fix:** Stages 7–8 convergence loop repairs P0/P1 violations autonomously (via `detect-fix-rescan-loop.yaml` primitive).

**Activity Log:** Every stage → `.cortex-runtime/traces/orchestrator-traces.db`
...