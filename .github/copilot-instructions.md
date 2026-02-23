# CORTEX GitHub Copilot Instructions

**Updated:** 2026-02-23 | ## About CORTEX

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI Engineering Framework:

- **22 Wired Orchestrators** across 3 tiers (core, domain, support) — all satisfy IOrchestrator protocol
- **24 MCP Tools** via Pylance-style stdio server (auto-starts with VS Code)
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
| Orchestrators | 22 wired in `cortex/orchestrators/` (6 core, 6 domain, 10 support) |
| MCP Tools | 24 in `cortex/mcp/tools/` |
| Top-level Dirs | 16 canonical under `cortex/` |
| Governance Rules | 35 CORE active in `cortex-registry/core/tier0-skull/` (+ 2 AC rules) |
| Test Suite | 15,145 tests (539 golden, 177 phase) |
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
  orchestrators/     ← 22 wired orchestrators across 3 tiers (core, domain, support)
  mcp/tools/         ← 24 MCP tools
  core/              ← OrchestratorBase, FileFactory, WorkflowEngine
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
| OrchestratorBase | `cortex/core/orchestrator_base.py` |
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
**Audited by:** Check #7 in the 13-Point Production Readiness Audit (`/audit fix`)

**AC Marker Rules:**
- `AC_START` at entry point of every public orchestrator method
- `AC_COMPLETE` on success with ✅ + timing (ms)
- `AC_COMPLETE` on failure with ❌ + error classification
- No orphaned `AC_START` without matching `AC_COMPLETE` (governance violation)

---

## ⚡ Quick Command Reference

| Command | What It Does | Stages |
|---------|-------------|--------|
| **`/audit fix`** | **Full production-readiness scan + autonomous fix** | 9 stages (see below) |
| `/audit` | Scan only, no auto-fix | Stages 1–6 |
| `/vacuum` | Markdown sprawl + root clutter cleanup | Stage 5 only |
| `/health` | All 22 orchestrator health endpoints | Stage 4 only |
| `/upgrade` | Check origin/main, merge if ahead, run audit fix | Inflight upgrade |
| `/digest {path}` | Intelligent content ingestion (3-pipeline) | — |
| `/onboard {repo}` | LENS analysis + SQLite dashboard | — |
| `/challenge {request}` | Generate ≥2 alternatives with trade-offs | — |

### `/audit fix` — 9-Stage Pipeline (canonical single command for production readiness)

```
Stage 1: Stage 0 Governance Pre-Flight      (STAGE-0-GOVERNANCE-AUDIT-SPEC.md)
Stage 2: 17-Point Production Scan           (cortex-auditor.md Checks #1–#17)
Stage 3: Wiring Contract Validation         (architecture-integrity-agent.md, L1→L3)
Stage 4: Orchestrator Health (all 22)       (HealthOrchestrator.run_health_check())
Stage 5: Vacuum Cleanup                     (VacuumOrchestrator + cortex_vacuum)
Stage 6: Prompt/Agent Meta-Audit            (cortex-meta-auditor.md, 22 checks)
Stage 7: Auto-Fix confidence >90%           (autonomous remediation)
Stage 8: Re-validate → zero-violation gate  (0 P0, 0 P1 required to pass)
Stage 9: Tests + AC_COMPLETE               (python3 scripts/run_tests.py batch)
```

**Output:** Inline violations table with P0/P1/P2 severity, file path, remediation.
**Activity log:** `.cortex-runtime/traces/orchestrator-traces.db` (AC markers per stage).

---

## References

- Architecture: `cortex-docs/architecture-recommendation.md`
- MCP Setup: `.github/prompts/MCP-SETUP-GUIDE.md`
- Security: `cortex-docs/security.md`
- Architect Prompt: `.github/prompts/cortex-architect.prompt.md`
- Response Templates: `.github/templates/cortex-response-templates.md`

---

## ⛔ Test Execution — MANDATORY RULES

**CORTEX uses `CortexXdistPlugin` as the canonical batch runner. Never bypass it.**

| ✅ DO — Canonical Methods | ❌ NEVER — Forbidden Patterns |
|---|---|
| `make test-batch` | `python3 -m pytest tests/ -x -q` |
| `make test-all` | `pytest --tb=no -q` (silences batch reporter) |
| `make test-fast` | `pytest -o addopts=` (wipes xdist config) |
| `make test-smoke` | `pytest -x` alone (stops before batch summary) |
| VS Code tasks (tasks.json) | Any command that adds `-q` or `-o addopts=` |
| `python3 scripts/run_tests.py {mode}` *(cross-platform)* | Direct `python3 -m pytest` with flag overrides |
| `./scripts/run-tests.sh {mode}` *(Unix only — delegates to run_tests.py)* | `.venv/bin/python -m pytest` (venv-path hard-codes Unix) |

**Why:** `pytest.ini` enforces `-n auto --dist loadscope`. `conftest.py` registers `cortex_xdist_plugin`.
Adding `-q` silences the batch reporter's stderr. Adding `-o addopts=` wipes xdist entirely.
The batch plugin (`CORTEX_BATCH_SIZE=500`) provides live batch boundaries, pass/fail counts, and a final summary table — these are lost when raw pytest commands override the project config.

**When running tests in a terminal, always use:**
```
make test-batch
```
or a VS Code task from `tasks.json`.

**Windows users:** Replace `python3` with `python` and replace `./scripts/run-tests.sh {mode}` with `python scripts\run_tests.py {mode}`. All `make` commands have VS Code Task equivalents in `tasks.json` for Windows-first users who cannot use `make`.

---

## ✅ Preflight Requirements Validation

CORTEX auto-validates `requirements.txt` at session start via `UpgradeOrchestrator.validate_requirements()`. If the environment is incomplete, CORTEX will attempt `pip install -r requirements.txt` autonomously before proceeding.

- **Silent if all packages satisfied** (CORE-049)
- **P0 hard-stop** if any `[PREFLIGHT CRITICAL]` package is missing
- **To skip** (CI/CD): set `CORTEX_SKIP_PREFLIGHT=true`
