# CORTEX GitHub Copilot Instructions

**Updated:** 2026-02-24 (Phase 66/67 COMPLETE — all 67 phases done) | ## About CORTEX

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework:

- **27 Wired Orchestrators** across 3 tiers (core, domain, support) — all satisfy IOrchestrator protocol
- **38 MCP Tools** via Pylance-style stdio server (auto-starts with VS Code)
- **35 CORE Governance Rules** (+ 2 AC rules) enforced at pre-commit, CI, and runtime
- **TDD-First Development** — CORE-008: tests before implementation, no exceptions
- **Sweep Completeness Contract** — CORE-064: every FIX/REFACTOR/AUDIT exhausts its full issue catalogue (no partial sweeps)
- **LENS Analysis** — workspace-aware code intelligence (Language → Examination → Navigation → Synthesis)
- **1 Canonical Package** — all imports use `cortex.*` (no `cortex_intelligence`, `cortex_lens`, or `cortex.brain`)

---

## Architecture

| Metric | Value |
|---|---|
| Package | `cortex` (single canonical) |
| Orchestrators | 27 wired in `cortex/orchestrators/` (7 core, 6 domain, 14 support) |
| MCP Tools | 38 in `cortex/mcp/tools/` |
| Top-level Dirs | 16 canonical under `cortex/` |
| Governance Rules | 35 CORE active in `cortex-registry/core/tier0-skull/` (+ 2 AC rules) |
| Test Suite | 16,259 tests (486 golden, 177 phase) |
| Parallel Testing | pytest-xdist (`-n auto --dist loadscope`) |

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
cortex/              ← Python source (16 canonical dirs)
  orchestrators/     ← 27 wired orchestrators across 3 canonical tiers (7 core, 6 domain, 14 support) + 7 additional dirs (health, git, intelligence, strategies, synthesis, validation, workflow)
  mcp/tools/         ← 26 MCP tools (28 total — 2 deprecated)
  core/              ← OrchestratorProtocolMixin (primary, Phase 58), OrchestratorBase (legacy), FileFactory, WorkflowEngine
  testing/           ← Test framework, parallel runner, quality gate
  intelligence/      ← LENS, domain brain, knowledge synthesis
  governance/        ← Rule enforcement, compliance
cortex-registry/     ← YAML governance rules, patterns, plans
tests/               ← All tests (mirrors cortex/ structure)
.cortex-runtime/     ← Runtime data (logs, traces, .db files)
.github/             ← CI/CD, prompts, agents, templates
cortex-docs/         ← User-facing documentation (HTML/CSS only)
```

---

## Key Entry Points

| Component | Location |
|---|---|
| MasterOrchestrator | `cortex/orchestrators/core/master_orchestrator.py` |
| IntentRouter | `cortex/orchestrators/core/intent_router.py` |
| TDDOrchestrator | `cortex/orchestrators/core/tdd_orchestrator.py` |
| EnforcementOrchestrator | `cortex/orchestrators/core/enforcement_orchestrator.py` |
| HealthOrchestrator | `cortex/orchestrators/health/health_orchestrator.py` |
| VacuumOrchestrator | `cortex/orchestrators/health/vacuum_orchestrator.py` |
| OrchestratorProtocolMixin | `cortex/core/orchestrator_protocol_mixin.py` (primary base — Phase 58, used by all 27 wired orchestrators) |
| OrchestratorBase | `cortex/core/orchestrator_base.py` (legacy — 2 orchestrators only) |
| MCP Server | `cortex/mcp/` |
| Refactor Plan | `cortex-registry/planning/cortex-refactor-master.yaml` |
| BulkDigestOrchestrator | `cortex/orchestrators/support/bulk_digest_orchestrator.py` |
| DigestSessionOrchestrator | `cortex/orchestrators/support/digest_session_orchestrator.py` |
| SweepCatalogueOrchestrator | `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` |
| MasterOrchestrationStage1 | `cortex/orchestrators/core/master_orchestrator_stage_1.py` |
| MasterOrchestrationStage3 | `cortex/orchestrators/core/master_orchestrator_stage_3.py` |
| MasterOrchestrationStage4 | `cortex/orchestrators/core/master_orchestrator_stage_4.py` |

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

**SQLite Activity Logging:** Every audit stage, orchestrator invocation, and convergence loop cycle writes to `.cortex-runtime/traces/orchestrator-traces.db`. Schema: `audit_sessions` (1 row per `/audit fix` run), `audit_stage_log` (1 row per stage), `audit_violations` (1 row per violation — queryable for recurring P0 pattern detection), `workflow_cycles` (1 row per detect-fix-rescan iteration), `workflow_runs` (1 row per loop invocation). DB is cleaned up on every Stage 9 exit (30-day retention + VACUUM). Pattern detection surfaces recurring P0s that appear in ≥3 sessions. Guard: `CORTEX_DISABLE_DB_CLEANUP=true` to skip cleanup (CI environments).

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
6. Run smoke gate: `make test-batch`
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

## ✅ Preflight Requirements Validation

CORTEX auto-validates `requirements.txt` at session start via `UpgradeOrchestrator.validate_requirements()`. If the environment is incomplete, CORTEX will attempt `pip install -r requirements.txt` autonomously before proceeding.

- **Silent if all packages satisfied** (CORE-049)
- **P0 hard-stop** if any `[PREFLIGHT CRITICAL]` package is missing
- **To skip** (CI/CD): set `CORTEX_SKIP_PREFLIGHT=true`
