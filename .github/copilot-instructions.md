# CORTEX GitHub Copilot Instructions

**Updated:** 2026-02-28 (Phase 89 — Self-Healing Prompt Suite) | **Refresh:** `python3 scripts/refresh_prompt_suite.py`

## About CORTEX

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework:

- **282 Orchestrator files** across 9 domains (`core:102 domain:28 support:51 git:4 health:27 intelligence:16 persona:6 validation:12 workflow:29`) — all satisfy IOrchestrator protocol
- **29 MCP Tools registered** in `mcp_registry.py` via Pylance-style stdio server — 35 tool files in `cortex/mcp/tools/`
- **32 Governance YAMLs** in `cortex-registry/core/` enforced at pre-commit, CI, and runtime
- **TDD-First Development** — CORE-008: tests before implementation, no exceptions
- **Sweep Completeness Contract** — CORE-064: every FIX/REFACTOR/AUDIT exhausts its full issue catalogue (no partial sweeps)
- **LENS Analysis** — workspace-aware code intelligence (Language → Examination → Navigation → Synthesis)
- **Unified Reinforcement Signal (URS)** — closed-loop learning across all orchestrators via `cortex_learning` MCP tool (`emit|history|decay|promote|quarantine|metrics|rca`)
- **RCA Memory Engine** — 4 root cause analysis methodologies (Five-Whys, Fishbone, Fault-Tree, Causal-Chain) via `cortex_learning` op=`rca`; `cortex/intelligence/learning/rca_engine.py`
- **Multi-Stack Debug Pipeline** — 8 injection strategies (3 Python + 5 multi-stack: Frontend/HTML-Vision/API/SQL/DotNet), Vision API, auto-cleanup
- **Self-Healing Prompt Suite** — `scripts/refresh_prompt_suite.py` introspects live architecture + SQLite audit logs to regenerate all prompts/agents with zero drift
- **27 Intent Types** routed via IntentRouter (`cortex/orchestrators/core/intent_router_impl.py`)
- **1 Canonical Package** — all imports use `cortex.*` (no `cortex_intelligence`, `cortex_lens`, or `cortex.brain`)
- **LLM-Orchestration Architecture** — CORTEX orchestrates the host LLM (GitHub Copilot/GPT) as the AI engine; it does not embed ML models

---

## Architecture

| Metric | Value |
|---|---|
| Package | `cortex` (single canonical) |
| Orchestrator files | 282 across 9 domains in `cortex/orchestrators/` |
| MCP Tools | 29 registered in `mcp_registry.py`; 35 tool files in `cortex/mcp/tools/` |
| Top-level Dirs | 20 under `cortex/` |
| Governance YAMLs | 32 in `cortex-registry/core/` |
| Test Suite | ~17,407 tests collected (run `python3 -m pytest --collect-only -q` for current count) |
| Parallel Testing | pytest-xdist (`-n auto --dist loadscope`) |
| Phases | 17 completed, 2 planned |
| Master YAML | 469/500 lines (THIN INDEX CONTRACT) |
| Intent Types | 27 (see `cortex/models/canonical_enums.py`) |
| SQLite Databases | 9 in `.cortex-runtime/` (cleanup: `refresh_prompt_suite.py --db-cleanup`) |

---

## MCP Architecture

CORTEX uses **Pylance-style MCP** — works automatically like Pylance (no manual server startup). The server auto-starts when VS Code opens the workspace via stdio transport.

**MCP ARCHITECTURE:** Pylance-style stdio transport, auto-detected by VS Code Copilot Chat. Configuration lives in `.vscode/settings.json`.

**Configuration** (`.vscode/settings.json`):
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**MCP Detection Methods — 3 ways to verify MCP is active:**

- **Method 1 (Tool Registry):** Call `cortex_verify` (op: `mcp`) in Copilot Chat — if it responds, MCP is running. This checks the Tool Registry directly.
- **Method 2 (Environment Variable / Settings):** Check `.vscode/settings.json` for `github.copilot.chat.mcpServers.cortex` key — if present, server is configured.
- **Method 3 (Network Port / Process):** Run `python3 -m cortex.mcp` in terminal — if it starts without import errors, MCP server is healthy. Check port binding or process listing to verify.

**Setup:** Run `python3 scripts/setup-mcp.py` for cross-platform MCP configuration (auto-detects Windows/macOS/Linux).

---

## Development Standards

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create .md/.txt report files |
| CORE-008 | TDD mandatory — write failing test first, then implement |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before IMPLEMENT/FIX/REFACTOR |
| CORE-049 | Silent autonomous execution (progress bars only) |
| CORE-064 | Sweep Completeness Contract — no partial sweeps; every FIX/REFACTOR/AUDIT must exhaust its full catalogue |

**MCP Tool Authoring — `validate_orchestrator_context` guard:** All MCP tool functions that
call `validate_orchestrator_context(orchestrator_context)` must guard the call:
```python
if orchestrator_context is not None:
    validate_orchestrator_context(orchestrator_context)
```
This allows direct test invocation without a `MasterOrchestrator` context while still
enforcing routing in production (where context is always supplied).

---

## Workflow

1. **Write the test first** (CORE-008 — RED phase)
2. **Implement minimum code** to pass tests (GREEN phase)
3. **Refactor** with all tests passing (REFACTOR phase)
4. **EnforcementOrchestrator** validates CORE rules pre-commit
5. **Commit** with conventional commit message

---

## File Organization

```
cortex/              ← Python source (20 dirs)
  orchestrators/     ← 282 orchestrator files across 9 domains (core:102 domain:28 support:51 git:4 health:27 +more)
  mcp/tools/         ← 29 registered MCP tools (35 tool files)
  core/              ← OrchestratorProtocolMixin (primary, Phase 58), OrchestratorBase (legacy), FileFactory, WorkflowEngine
  testing/           ← Test framework, parallel runner, quality gate
  intelligence/      ← LENS, domain brain, knowledge synthesis
  governance/        ← Rule enforcement, compliance
cortex-registry/     ← YAML governance rules, patterns, plans
tests/               ← All tests (mirrors cortex/ structure)
.cortex-runtime/     ← Runtime data (logs, traces, 9 .db files)
.github/             ← CI/CD, prompts, agents, templates
cortex-docs/         ← User-facing documentation (HTML/CSS only)
```

---

## Key Entry Points

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| InteractionOrchestrator | `cortex/orchestrators/core/interaction_orchestrator.py` (Stage 1 LENS per-turn comprehension) |
| TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| HealthOrchestrator | `cortex/orchestrators/health/health_orchestrator.py` |
| VacuumOrchestrator | `cortex/orchestrators/health/vacuum_orchestrator.py` |
| DebuggerOrchestrator | `cortex/orchestrators/support/debugger_orchestrator.py` |
| MarkerInjectionEngine | `cortex/orchestrators/support/debugging/marker_injection_engine.py` |
| AutoCleanupManager | `cortex/orchestrators/support/debugging/auto_cleanup_manager.py` |
| RCA Engine | `cortex/intelligence/learning/rca_engine.py` (Phase 87 — 4 methodologies) |
| RCA Store | `cortex/intelligence/learning/rca_store.py` |

---

## Cross-Cutting Intelligence (Universal — All Orchestrators)

**Every orchestrator invocation must emit AC markers** — this is a CORE requirement, not optional:

```python
# AC_START: AC-{DOMAIN}-{TIMESTAMP}  ← open session
# ... orchestrator logic ...
# AC_COMPLETE: AC-{DOMAIN}-{TIMESTAMP} ✅  ← close session
```

**Persistence target:** `.cortex-runtime/traces/orchestrator-traces.db`
**Enforced by:** `EnforcementOrchestrator` pre-commit hook + `cortex_validate` (op: `compliance`)
**Audited by:** Check #19 (SQLite activity log health) in the 19-Point Production Readiness Audit (`/audit fix`)

**AC Marker Rules:**
- `AC_START` at entry point of every public orchestrator method
- `AC_COMPLETE` on success with ✅ + timing (ms)
- `AC_COMPLETE` on failure with ❌ + error classification
- No orphaned `AC_START` without matching `AC_COMPLETE` (P0 governance violation — Check #19 and Meta-Audit Check #23)

**SQLite Activity Logging:** 9 databases in `.cortex-runtime/`:

| Database | Path | Tables | Purpose |
|---|---|---|---|
| orchestrator-traces | `traces/orchestrator-traces.db` | `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs`, `trace_*` | Primary trace store |
| governance-traces | `traces/governance.db` | `audit_log` | Governance enforcement |
| rca-store | `rca/rca_store.db` | `rca_analyses`, `prevention_rules`, `recurrence_*` | Root cause analysis |
| audit | `audit.db` | `audit_events`, `orchestrator_traces`, `governance_checks`, `phase_progress` | Audit events |
| governance | `governance.db` | `scaffolder_audit_log` | Scaffolder audit |
| conversations | `state/conversations.db` | `conversations`, `turn_records` | Session state |
| brain-governance | `state/cortex_brain/state/governance.db` | `audit_log` | Brain governance |
| wiring-audit | `wiring/contract_validation_audit.db` | `validation_audit`, `contract_versions` | Wiring contracts |
| intelligence-audit | `intelligence/intelligence_audit.db` | `intelligence_audit` | Intelligence traces |

**Cleanup:** `python3 scripts/refresh_prompt_suite.py --db-cleanup` (30-day retention + VACUUM). Guard: `CORTEX_DISABLE_DB_CLEANUP=true` to skip (CI environments).

---

## ⚡ Quick Command Reference

| Command | What It Does | Stages |
|---------|-------------|--------|
| **`/audit fix`** | **Full production-readiness scan + autonomous fix** | 9 stages (see below) |
| `/audit` | Scan only, no auto-fix | Stages 1–6 |
| `/vacuum` | Markdown sprawl + root clutter cleanup | Stage 5 only |
| `/health` | All 22 orchestrator health endpoints | Stage 4 only |
| `/healthcheck` | Full test suite (all tiers, parallel) | On-demand |
| `/upgrade` | Check origin/main, merge if ahead, run audit fix | Inflight upgrade |
| `/digest {path}` | Intelligent content ingestion (3-pipeline) | — |
| `/onboard {repo}` | LENS analysis + SQLite dashboard | — |
| `/challenge {request}` | Generate ≥2 alternatives with trade-offs | — |
| `/totalrecall` | Holistic production readiness refactor (7-phase protocol) | 7 phases |
| `/sync target={path}` | One-way privacy-safe sync: CORTEX → company folder | — |
| `/debug {path}` | Multi-stack debug: inject → capture → analyze → fix-plan → cleanup | 5 phases |
| `/debug-inject {path}` | Insert CORTEX_DEBUG markers (8 strategies: 3 Python + 5 multi-stack) | INJECT |
| `/debug-cleanup` | Remove all CORTEX_DEBUG markers across all languages | CLEANUP |

**Phase 85 — Response Format (canonical):** Every progress display uses the **phase-list+bar** format (not bar-only). SSOT: `.github/templates/cortex-response-templates.md`. Engagement blocks: `BLOCK-ENGAGEMENT-BREADCRUMB` (routing chain, always rendered), `BLOCK-ENGAGEMENT-TIMELINE` (collapsible timing), `BLOCK-PHASE-ROADMAP` (full journey at operation start).

**Phase 86 — Debug strategies (8 total):**
- `TestFailureStrategy`, `RefactorRegressionStrategy`, `GovernanceViolationStrategy` — existing Python strategies
- `FrontendConsoleStrategy` (JS/TS/React/Angular/Vue), `HtmlVisionMappingStrategy` (Vision API + DOM), `ApiTraceStrategy` (REST/GraphQL/gRPC), `SqlTraceStrategy` (SQL Server/Oracle/PostgreSQL), `DotNetTraceStrategy` (C#/.NET) — Phase 86 additions

**Phase 87 — RCA Memory Engine (121 GREEN tests):**
- `RCAEngine` — 4 methodologies: Five-Whys, Fishbone (Ishikawa), Fault-Tree, Causal-Chain
- `RCAStore` — SQLite-backed persistence at `.cortex-runtime/traces/rca.db`
- Exposed via `cortex_learning` MCP tool (op=`rca`, sub-actions: `analyze|query|list`)
- Category → methodology auto-selection: TECHNOLOGY→Five-Whys, PROCESS/PEOPLE→Fishbone, DATA→Causal-Chain
- Each completed RCA generates a `PreventionRule` (ADVISORY by default)

### `/audit fix` — 9-Stage Pipeline (canonical single command for production readiness)

```
Stage -1: Environment Readiness          (UpgradeOrchestrator.validate_requirements() — preflight)
Stage 0:  Inflight Upgrade + Pre-Flight  (git fetch origin/main check + STAGE-0-GOVERNANCE-AUDIT-SPEC.md)
Stage 1:  Stage 0 Governance Pre-Flight  (STAGE-0-GOVERNANCE-AUDIT-SPEC.md full spec)
Stage 2:  19-Point Production Scan       (cortex-auditor.md Checks #1–#19, includes SQLite health)
Stage 3:  Wiring Contract Validation     (architecture-integrity-agent.md, L1→L3)
Stage 4:  Orchestrator Health (all 22)   (HealthOrchestrator.run_health_check())
Stage 5:  Vacuum Cleanup                 (VacuumOrchestrator + cortex_vacuum)
Stage 6:  Prompt/Agent Meta-Audit        (cortex-meta-auditor.md, 23 checks)
Stage 7–8: Auto-Fix Convergence Loop    (detect-fix-rescan-loop primitive — loops until 0 P0/P1)
Stage 9:  Tests + AC_COMPLETE            (python3 scripts/run_tests.py preflight → SQLite cleanup)
```

**Test Tier Manifest:** `cortex-registry/workflows/templates/testing/test-tier-manifest.yaml`
**Output:** Inline violations table with P0/P1/P2 severity, file path, remediation.
**Activity log:** `.cortex-runtime/traces/orchestrator-traces.db` (full schema: `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs`).
**Convergence guarantee:** Stages 7–8 loop until `p0_count == 0 and p1_count == 0` (CORE-064) — not a single pass.
**Workflow template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`
**Loop primitive:** `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`

---

## 📋 Master Plan Decomposition — THIN INDEX CONTRACT

**`cortex-master.yaml` is a REFERENCE INDEX only — never a detail document.**

| Rule | Detail |
|------|--------|
| **Max size** | ≤ 500 lines (alarm at 400) |
| **Prohibited inline** | `phases`, `gap_catalogue`, `tdd_sequence`, `rewrites`, `new_files`, `files_to_edit`, `implementation`, `code_snippets` |
| **Allowed per entry** | `id`, `title`, `status`, `priority`, `sweep_id`, `gaps`, `sub_phases`, `file`, `note`, `phases` (list of IDs only) |
| **Detail location** | `cortex-registry/planning/phases/planned/<phase-id>.yaml` (active/upcoming) |
| **Completed detail** | `cortex-registry/planning/phases/completed/<phase-id>.yaml` |
| **Template** | `cortex-registry/planning/phases/_template.yaml` |
| **Lifecycle governance** | `cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml` |

### Decomposition Checks — Run at TWO points:

**① BEFORE adding any phase to cortex-master.yaml (checkpoint_create):**
1. Create dedicated file first at `cortex-registry/planning/phases/planned/<phase-id>.yaml`
2. Use `cortex-registry/planning/phases/_template.yaml` as scaffold
3. Write ALL detail in the dedicated file (gap catalogue, TDD sequences, acceptance criteria)
4. Add ONLY a thin reference entry to `cortex-master.yaml`
5. Verify `cortex-master.yaml` is still ≤ 500 lines: `wc -l cortex-registry/cortex-master.yaml`
6. Validate YAML: `python3 -c "import yaml; yaml.safe_load(open('cortex-registry/cortex-master.yaml'))"`

**② BEFORE marking any phase COMPLETE in the pipeline (checkpoint_complete):**
1. All gaps in `sweep_catalogue` have `status: CLOSED` (CORE-064)
2. All acceptance criteria documented with ✅ in the dedicated file
3. Move dedicated file from `planned/` → `completed/`
4. Update `file:` reference in `cortex-master.yaml` to point to `completed/`
5. Update `status: COMPLETE` in both `cortex-master.yaml` entry and dedicated file
6. Run smoke gate: `make test-smoke`
7. Verify `cortex-master.yaml` remains ≤ 500 lines

### Why This Exists:
`cortex-master.yaml` grew from ~150L to 3,007L because inline phase detail was written directly to it. This caused: 40+ YAML syntax errors, un-reviewable diffs, context exhaustion when loading the file, and no single-file accountability for each phase's detail. The THIN INDEX CONTRACT prevents recurrence.

---

## References

- Architecture: `cortex-docs/architecture-recommendation.md`
- MCP Setup: `.github/prompts/MCP-SETUP-GUIDE.md`
- Security: `cortex-docs/security.md`
- Architect Prompt: `.github/prompts/cortex-architect.prompt.md`
- Response Templates: `.github/templates/cortex-response-templates.md`
- Master Plan Lifecycle: `cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml`
- Phase Template: `cortex-registry/planning/phases/_template.yaml`
- Debug Agent: `.github/agents/support/cortex-debugger.md`
- Debug Pipeline Template: `cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml`
- **Prompt Refresh Playbook**: `scripts/refresh_prompt_suite.py` (self-healing prompt suite)

---

## ⛔ Test Execution — MANDATORY RULES

**Four-tier optimised execution. Never bypass `run_tests.py`.**

| Mode | Command (macOS/Linux) | Command (Windows) | When to use |
|---|---|---|---|
| **preflight** | `make test-preflight` | `python scripts\run_tests.py preflight` | `/audit fix` Stage 9 — critical wiring (< 10s) |
| **changed** | `make test-changed` | `python scripts\run_tests.py changed` | TDD inner loop — after every save |
| **smoke** | `make test-smoke` | `python scripts\run_tests.py smoke` | Quick sanity before commit (< 60s) |
| **unit** | `make test` | `python scripts\run_tests.py unit` | Default local dev |
| **parallel** | `make test-parallel` | `python scripts\run_tests.py parallel` | Pre-commit full speed |
| **healthcheck** | `make test-healthcheck` | `python scripts\run_tests.py healthcheck` | Full suite on-demand (parallel) |
| **batch** | `make test-batch` | `python scripts\run_tests.py batch` | CI gate (sequential) |

**Three Layers:**
- **Layer 1 — Parallel:** `pytest-xdist` with `-n auto --dist loadscope`. 10 cores → ~3–4× faster. Falls back to sequential if xdist is absent.
- **Layer 2 — Smart:** `pytest-testmon` with `--testmon`. Runs only tests covering changed source files. Ideal for TDD. Incompatible with xdist (runs sequentially). Set `CORTEX_DISABLE_TESTMON=true` for a clean full run.
- **Layer 3 — Import:** `--import-mode=importlib` in `pytest.ini`. Cuts cold collection from ~17s → ~7s.

| ✅ DO — Canonical Methods | ❌ NEVER — Forbidden Patterns |
|---|---|
| `make test-preflight` / `make test-smoke` | `python3 -m pytest tests/ -x -q` |
| `python3 scripts/run_tests.py {mode}` | `pytest --tb=no -q` (silences batch reporter) |
| VS Code tasks (tasks.json) — all modes | `pytest -o addopts=` (wipes import-mode + sugar settings) |
| `CORTEX_WORKERS=4 make test-parallel` | `.venv/bin/python -m pytest` (hard-codes Unix venv path) |

**When running tests in a terminal, always use:**
```
make test-preflight  # fastest — audit gate (< 10s)
make test-changed    # TDD loop (testmon)
make test-smoke      # sanity gate (< 60s)
```
or a VS Code task from `tasks.json`.

**Windows users:** All `make` commands have VS Code Task equivalents in `tasks.json`.
Use `python scripts\run_tests.py {mode}` in PowerShell/cmd — `python3` may not be on PATH.

**Environment overrides:**
- `CORTEX_WORKERS=4` — cap xdist to 4 workers (CI with limited cores)
- `CORTEX_DISABLE_PARALLEL=true` — force sequential (any mode)
- `CORTEX_DISABLE_TESTMON=true` — skip testmon DB (clean run after large refactor)

---

## 🔄 Self-Healing Prompt Suite — Repeatable Refresh Playbook

**Script:** `python3 scripts/refresh_prompt_suite.py`
**Purpose:** Regenerate `copilot-instructions.md`, `AGENT-INDEX.md`, and validate all prompts/agents against live architecture.

### Playbook Steps (execute in order)

| Step | Command | What It Does |
|---|---|---|
| 1 | `python3 scripts/refresh_prompt_suite.py --counts-only` | Introspect live architecture: orchestrators, MCP tools, tests, governance |
| 2 | `python3 scripts/refresh_prompt_suite.py --db-cleanup` | Enforce 30-day retention, delete orphaned AC_START, VACUUM all 9 databases |
| 3 | `python3 scripts/refresh_prompt_suite.py` | Full refresh: cleanup → counts → validate → report |
| 4 | `python3 scripts/refresh_prompt_suite.py --dry-run` | Preview all changes without writing |

### When to Run

- **After every phase completion** — counts drift, new orchestrators/tools added
- **After `/audit fix`** — validates prompt/agent accuracy against live state
- **After major refactoring** — ensures no stale references to deleted files
- **Monthly maintenance** — SQLite cleanup + VACUUM

### SQLite Cleanup Details

| Database | Retention | Cleanup Actions |
|---|---|---|
| orchestrator-traces | 30 days | Delete old traces, orphaned AC_START, VACUUM |
| rca-store | 30 days | Retain analyses, prune old prevention rules |
| conversations | 90 days | Longer retention for session continuity |
| All others | 30 days | Standard retention + VACUUM |

**Guard:** Set `CORTEX_DISABLE_DB_CLEANUP=true` to skip cleanup in CI environments.

### Architecture Drift Detection

The playbook detects drift between documentation and live code:
- Orchestrator file count mismatch → P0 violation
- MCP tool registry vs tool files mismatch → P1 violation
- Intent types in `canonical_enums.py` not covered in agent routing → P1 violation
- `cortex-master.yaml` exceeding 500 lines → P0 violation
- Stray `.db` files outside `.cortex-runtime/` → P1 violation

---

## ✅ Preflight Requirements Validation

CORTEX auto-validates `requirements.txt` at session start via `UpgradeOrchestrator.validate_requirements()`. If the environment is incomplete, CORTEX will attempt `pip install -r requirements.txt` autonomously before proceeding.

- **Silent if all packages satisfied** (CORE-049)
- **P0 hard-stop** if any `[PREFLIGHT CRITICAL]` package is missing
- **To skip** (CI/CD): set `CORTEX_SKIP_PREFLIGHT=true`
