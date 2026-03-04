---
scope: non-production-admin
---
# CORTEX Auditor

**Purpose:** 41-Point Production Readiness Scanning (Checks #1–#29 source code + Checks #30–#41 production hardening)
**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`

**SSOT:** The canonical 41-Point audit checklist is defined in `.github/prompts/cortex-architect.prompt.md` § 29-Point Production Readiness Audit + § Extended Hardening Checks (Phase 126).

**Stage:** `/audit fix` Stage 2 (Checks #1–#29) + Stage 8 extended convergence (Checks #30–#41)

**Entry Point:** `AuditCoordinator` → `EnforcementOrchestrator`

**Trigger:** `/audit`, "scan", "check", "health"

**Scope:** Source code health — stale imports, stubs, duplicates, CORE rule violations, test quality, file hygiene, SQLite activity log health, **Workflow Composer pipeline health** (Check #20), **F811 duplicate method definitions** (Check #22), **F401 unused import sweep** (Check #23), **OS artifact contamination** (Check #24). PLUS Phase 126 hardening: Windows boot wiring (Check #30), architecture runtime connectivity (Check #31), stub/mock/blank eradication (Check #32), YAML reader no-bypass (Check #33), no versioning anywhere (Check #34), repo hygiene/purity (Check #35), prompt/governance determinism (Check #36), response template golden snapshot (Check #37), cortex-registry cohesion (Check #38), sync non-production markers (Check #39), production readiness orchestrator (Check #40), drift lock system (Check #41).

**Evidence Requirement (non-negotiable):** Every check MUST produce a verifiable artifact before PASS is recorded. Accepted evidence types:
- Grep output (0 lines = pass)
- Test run stdout (pytest exit 0 = pass)
- Python3 assertion script printing OK
- JSON evidence report at `.cortex-runtime/traces/production-readiness-evidence.json`
Self-attestation ("I believe this passes") is REFUSED by the audit pipeline.

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

**Check #30 — Windows Boot Wiring (Phase 126):**
- `grep -rn 'os\.path\.' cortex/ --include='*.py' | grep -v 'pathlib\|test_\|#.*intentional' | wc -l` → must be `0`
- `python3 scripts/setup-mcp.py --dry-run` → exit 0
- `python3 -m cortex --help` → exit 0, canonical commands present
- Drift lock: `cortex-registry/governance/drift-locks/check-30-windows-boot-lock.yaml`

**Check #31 — Architecture Runtime Connectivity (Phase 126):**
- `python3 -c "from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator; io=InteractionOrchestrator(); r=io.health_check(); assert r.get('status')=='healthy'; print('OK')"` → must print `OK`
- Full chain (IO → LENS → IntelligenceFacade → registry YAML → WorkflowComposer) returns live non-stub data
- Drift lock: `cortex-registry/governance/drift-locks/check-31-arch-connectivity-lock.yaml`

**Check #32 — Stub/Mock/Blank Eradication (Phase 126):**
- `grep -rn "TODO\|FIXME\|raise NotImplementedError\|return {}\|return \[\]" cortex/ --include="*.py" | grep -v "test_\|#.*intentional\|abstract"` → must return `0` lines
- `grep -rn "disabled.*=.*True\|enabled.*=.*False" cortex/ --include="*.py" | grep -v test_` → must return `0` lines
- Drift lock: `cortex-registry/governance/drift-locks/check-32-stub-eradication-lock.yaml`

**Check #33 — YAML Reader No-Bypass (Phase 126):**
- `grep -rn "yaml\.safe_load\|yaml\.load(" cortex/ --include="*.py" | grep -v "registry\|yaml_reader\|test_\|#.*intentional"` → must return `0` lines
- Drift lock: `cortex-registry/governance/drift-locks/check-33-yaml-reader-no-bypass-lock.yaml`

**Check #34 — No Versioning Anywhere (Phase 126):**
- `grep -rn "\"version\":\|version:\s\|release:\s\|\bv1\b\|\bv2\b" cortex-registry/ .github/ --include="*.yaml" --include="*.md" | grep -v "Python 3\|pytest\|tree-sitter\|requirements\|__version__\|>=\|==\|#.*intentional"` → must return `0` lines
- Builds BLOCK and merges are BLOCKED if any versioning language found
- Drift lock: `cortex-registry/governance/drift-locks/check-34-no-versioning-lock.yaml`

**Check #35 — Repo Hygiene/Production Purity (Phase 126):**
- `find . -name "*.backup" -o -name "*.bak" -o -name "*.old" | grep -v ".git" | wc -l` → must be `0`
- `find . -name "*.log" | grep -v ".cortex-runtime" | wc -l` → must be `0`
- Drift lock: `cortex-registry/governance/drift-locks/check-35-repo-hygiene-lock.yaml`

**Check #36 — Prompt/Governance Determinism (Phase 126):**
- `grep -rn "\bmay\b\|\bmight\b\|\bcould\b\|\boptionally\b" .github/agents/ .github/prompts/ | grep -v "test_\|#\|cortex-sync"` → must return `0` lines
- Drift lock: `cortex-registry/governance/drift-locks/check-36-prompt-determinism-lock.yaml`

**Check #37 — Response Template Golden Snapshot (Phase 126):**
- `python3 -m pytest tests/golden/test_response_template_format_canon.py -p no:xdist` → must be `100% GREEN`
- Drift lock: `cortex-registry/governance/drift-locks/check-37-response-template-lock.yaml`

**Check #38 — cortex-registry Cohesion (Phase 126):**
- `python3 -c "from cortex.repositories.yaml_reader import RegistryYAMLReader; r=RegistryYAMLReader(); rep=r.validate_integrity(); assert rep['orphans']==0 and rep['broken_refs']==0; print('OK')"` → must print `OK`
- Drift lock: `cortex-registry/governance/drift-locks/check-38-registry-cohesion-lock.yaml`

**Check #39 — cortex-sync Non-Production Markers (Phase 126):**
- Every non-production prompt/agent frontmatter contains `scope: non-production-admin`
- `cortex-sync.prompt.md` has `production_files` exclusion list
- Drift lock: `cortex-registry/governance/drift-locks/check-39-sync-marker-lock.yaml`

**Check #40 — Production Readiness Orchestrator Green Gate (Phase 126):**
- `python3 scripts/run_tests.py preflight` → ≥258 tests, all GREEN, runtime < 120s
- Evidence JSON at `.cortex-runtime/traces/production-readiness-evidence.json`
- Drift lock: `cortex-registry/governance/drift-locks/check-40-production-readiness-orchestrator-lock.yaml`

**Check #41 — Drift Lock System (Phase 126):**
- `ls cortex-registry/governance/drift-locks/ | wc -l` → must be ≥11
- All drift lock preflight tests GREEN: `python3 scripts/run_tests.py preflight`
- `drift-lock-emit.yaml` primitive wired into audit-fix Stage 8
- Drift lock: self-referential — Check #41 IS the system; its own lock is `check-41-drift-lock-system-lock.yaml`

**Relationship to other agents:**
- `cortex-meta-auditor.md` — audits governance artifacts (prompts, agents, templates), NOT source code
- `architecture-integrity-agent.md` — validates wiring.yaml ↔ implementation alignment (L1→L3)
- `cortex-holistic-validator.md` — pre-implementation validation gate (CORE-048)

**Auto-Fix:** Stages 7–8 convergence loop repairs P0/P1 violations autonomously (via `detect-fix-rescan-loop.yaml` primitive). On every gap close, Stage 8 also invokes `drift-lock-emit.yaml` to emit a permanent CI lock.

**Drift Lock Primitive:** `cortex-registry/workflows/templates/primitives/governance/drift-lock-emit.yaml`
**Drift Lock Dir:** `cortex-registry/governance/drift-locks/`

**Activity Log:** Every stage → `.cortex-runtime/traces/orchestrator-traces.db`
...