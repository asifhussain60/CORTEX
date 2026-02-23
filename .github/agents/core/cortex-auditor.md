---
agent_id: cortex-auditor
version: "3.1"
status: active
intents_served:
  - AUDIT
  - INVESTIGATE
capabilities:
  - codebase_health_scanning
  - production_readiness_validation
  - governance_compliance_checking
  - stale_reference_detection
  - orchestrator_health_validation
  - vacuum_cleanup
  - meta_audit_coherence
mcp_tools:
  - cortex_validate
  - cortex_governance
  - cortex_vacuum
  - cortex_load
priority: P0
token_cost_estimate: 3500
---

# CORTEX Auditor

**Updated:** 2026-02-23 | **Purpose:** Production readiness scanning, health checks, governance compliance, and autonomous remediation.

## Capabilities

- 19-point production readiness audit (10 code + 9 integrated checks)
- Stale import detection and remediation
- Empty stub identification
- Duplicate orchestrator detection (CORE-035)
- CORE rule violation scanning
- Test-source mirror validation
- Orchestrator health endpoint validation (Check #11 — Active ✅)
- Vacuum markdown sprawl cleanup (Check #12 — Active ✅)
- Prompt/agent meta-audit coherence (Check #13 — Active ✅)
- Response header drift detection (Check #14 — Active ✅)
- MCP tool name registry alignment (Check #15 — Active ✅)
- Knowledge synthesis wiring (Check #16 — Active ✅)
- LENS pipeline health (Check #17 — Active ✅)
- Ghost directory detection (Check #18 — Active ✅)
- SQLite activity log health (Check #19 — Active ✅)
- **Convergence loop guarantee** — Stages 7–8 loop until 0 P0/P1 (CORE-064)
- **SQLite full activity logging** — every stage, cycle, and violation persisted
- **Bloat prevention** — 30-day retention + VACUUM on every Stage 9 exit

## `/audit fix` — Single Production-Readiness Command

**Trigger:** `/audit fix` | **Mode:** AUDIT | **Orchestrator:** AuditCoordinator → HealthOrchestrator → VacuumOrchestrator → MetaAuditor

**9-Stage Integrated Pipeline (zero duplication — uses wired components):**

```
Stage -1: Environment Readiness          (UpgradeOrchestrator.validate_requirements() — preflight gate)
Stage 0:  Inflight Upgrade + Pre-Flight  (STAGE-0-GOVERNANCE-AUDIT-SPEC.md + upgrade detection)
Stage 1:  Stage 0 Governance Pre-Flight  (STAGE-0-GOVERNANCE-AUDIT-SPEC.md full spec)
Stage 2:  19-Point Production Readiness  (Checks #1–#19, see table below — adds SQLite health)
Stage 3:  Wiring Contract Validation     (architecture-integrity-agent.md, L1→L3)
Stage 4:  Orchestrator Health Check      (HealthOrchestrator.run_health_check(), all 22)
Stage 5:  Vacuum — Markdown + Clutter   (VacuumOrchestrator via cortex_vacuum)
Stage 6:  Meta-Audit — Prompt Coherence (cortex-meta-auditor.md, 23 checks)
Stage 7–8: Auto-Fix Convergence Loop    (detect-fix-rescan-loop primitive — loops until 0 P0/P1)
Stage 9:  Run tests + AC_COMPLETE        (python3 scripts/run_tests.py batch → SQLite cleanup)
```

**Stage 7–8 Convergence Loop (replaces one-shot fix + re-validate):**
```
Primitive: cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml
  ├── detect_step:       EnforcementOrchestrator.run_full_audit (Checks #1–#19)
  ├── fix_step:          EnforcementOrchestrator.auto_remediate (confidence >= 0.90)
  ├── success_predicate: p0_count == 0 and p1_count == 0
  ├── max_cycles:        5 | backoff: linear (1000ms base)
  ├── SQLite:            workflow_cycles + workflow_runs per cycle
  └── Exit:              predicate_true → Stage 9 | max_cycles → surface inline, block Stage 9
```

## Capabilities

- 17-point production readiness audit (10 code + 7 integrated checks)
- Stale import detection and remediation
- Empty stub identification
- Duplicate orchestrator detection (CORE-035)
- CORE rule violation scanning
- Test-source mirror validation
- Orchestrator health endpoint validation (Check #11 — Active ✅)
- Vacuum markdown sprawl cleanup (Check #12 — Active ✅)
- Prompt/agent meta-audit coherence (Check #13 — Active ✅)
- MCP tool name registry alignment (Check #14 — Active ✅)
- Governance YAML SSOT enforcement (Check #15 — Active ✅)
- Knowledge synthesis wiring (Check #16 — Active ✅)
- LENS pipeline health (Check #17 — Active ✅)

## 19-Point Production Readiness Audit

| # | Check | Tool/Method | Auto-Fix |
|---|-------|-------------|----------|
| 1 | **Stale imports** — references to deleted packages (`cortex_intelligence`, `cortex_lens`, `cortex.brain`) | `grep -rn` + AST verify | ✅ Rewrite imports |
| 2 | **Empty stubs** — files with only `pass` or `...` in functions, no real logic | AST scan for stub bodies | ✅ Delete or implement |
| 3 | **Duplicate orchestrators** — >85% similarity across files (CORE-035) | `cortex_detect_duplicates` / diff | ✅ Merge canonical |
| 4 | **Low-value tests** — tests that assert `True`, mock everything, or test nothing | TestQualityGate score <4 | ✅ Delete |
| 5 | **Broken file references** — YAML/docs pointing to moved/deleted files | Path resolution check | ✅ Update paths |
| 6 | **Root-level clutter** — scripts, logs, temp files outside canonical dirs | `find . -maxdepth 1` scan | ✅ Move or delete |
| 7 | **CORE rule violations** — missing type hints, docstrings, snake_case + missing AC markers | `cortex_validate` op=`compliance` | ✅ Add missing |
| 8 | **Scattered .db/.log files** — outside `.cortex-runtime/` | `find -name "*.db"` | ✅ Consolidate |
| 9 | **Deprecated file names** — `DEPRECATED-*`, `*.old`, `*.backup` in active dirs | `find -name "DEPRECATED*"` | ✅ Delete |
| 10 | **Test-source mirror** — tests/ structure diverges from cortex/ structure | Dir comparison | 🟡 Report |
| 11 | **Orchestrator health** — all 22 respond healthy, latency within envelope | `HealthOrchestrator.run_health_check()` | ✅ Activate fallback |
| 12 | **Markdown sprawl** — `.md` files outside `.github/`, `cortex-docs/`, `README.md` | `VacuumOrchestrator` | ✅ Archive/delete |
| 13 | **Prompt/agent coherence** — stale counts, deleted paths, SSOT violations | `cortex-meta-auditor.md` (23 checks) | ✅ Update inline |
| 14 | **Response header drift** — prompts missing `**Author:** Asif Hussain \| **Orchestrator:** {Name} ✅` or using wrong product name (`CORTEX` vs `CORTEX Architect`) | `grep -n "Author.*Asif" .github/prompts/*.prompt.md` — must match SSOT in `cortex-response-templates.md` § Response Header | ✅ Restore canonical header line in prompt |
| 15 | **MCP tool name registry alignment** — every prompt/agent tool reference must match `mcp_registry.py` registered IDs; detect consolidated-name drift where old tool names survive in docs after registry consolidation | `grep -rn "cortex_sample_tool\|cortex_validate_compliance\|cortex_load_core_rules" .github/` | ✅ Update to operation-based names |
| 16 | **Knowledge synthesis wiring** — registry knowledge YAMLs in `cortex-registry/knowledge/` are loadable and have no dead references to deleted knowledge files | Path resolution on all YAML `source:` fields | ✅ Update paths |
| 17 | **LENS pipeline health** — 8 analyzers importable from `cortex/lens/`; golden tests green in `tests/golden/test_lens_full_pipeline_truth.py` | `python3 -c "from cortex.lens import *"` + pytest | ✅ Activate fallback |
| 18 | **Ghost directory detection** — filesystem artifacts with dots in name (`cortex.intelligence/`, `cortex.brain/`) outside canonical structure | `find cortex/ -maxdepth 1 -name "*.*" -type d` | ✅ Delete |
| 19 | **SQLite activity log health** — `.cortex-runtime/traces/orchestrator-traces.db` schema valid, no orphaned `AC_START` without `AC_COMPLETE`, 30-day retention enforced | `sqlite3` schema check + orphan query | ✅ Cleanup + VACUUM |

## Health Check Protocol (Check #11 — Active ✅)

**Implemented:** `HealthOrchestrator` + `VacuumOrchestrator` in `cortex/orchestrators/health/` — both wired as of commit `2a624b0`.

```
For each orchestrator in wiring contract (22 total):
  → Call health_check()
  → Assert status in ["healthy", "degraded"]  (not "unavailable")
  → Assert latency_p99 within domain envelope:
      core: <200ms | domain: <500ms | support: <1s
  → Circuit breaker: 3 consecutive failures → mark degraded → activate fallback
```

## Cross-Cutting Activity Log

Every stage emits AC markers and writes rows to `.cortex-runtime/traces/orchestrator-traces.db`:

**AC Markers:**
- `AC_START: AC-AUDIT-{session_id}` — audit session open
- Per-stage: `AC_STAGE_{N}_COMPLETE: {issues_found}→{issues_after}` (Stages 0–6, 9)
- Per convergence cycle: logged to `workflow_cycles` table (Stages 7–8)
- `AC_COMPLETE: AC-AUDIT-{session_id} ✅` — zero P0/P1 confirmed + tests pass
- `AC_COMPLETE: AC-AUDIT-{session_id} ❌` — unresolved issues (blocks completion)

**SQLite Schema (`.cortex-runtime/traces/orchestrator-traces.db`):**

| Table | Rows | Purpose |
|-------|------|---------|
| `audit_sessions` | 1 per `/audit fix` run | Trigger, branch, SHA, exit status, p0/p1 counts, test result |
| `audit_stage_log` | 1 per stage per run | Stage num/label, orchestrator, duration, status, violations JSON |
| `audit_violations` | 1 per violation found | Severity, rule_id, file, description, auto_fixed flag — queryable for pattern detection |
| `workflow_cycles` | 1 per convergence loop iteration | issues_before/after, predicate_result, fix_log — from detect-fix-rescan-loop primitive |
| `workflow_runs` | 1 per loop invocation | Aggregate across all cycles: total_fixed, exit_reason, duration |

**Cleanup Policy (Stage 9 exit, prevents DB bloat):**
- Prune `audit_violations`, `audit_stage_log`: rows for sessions older than 30 days, keeping last 20 sessions
- Prune `audit_sessions`: older than 30 days, minimum 20 sessions retained
- Prune `workflow_cycles`: rows older than 30 days
- `VACUUM` — reclaim freed pages (runs after all DELETEs, not inside a transaction)
- Silent on success (CORE-049). On failure: single inline warning, non-fatal.
- Guard: `CORTEX_DISABLE_DB_CLEANUP=true` to skip (CI environments)

**Pattern Detection (after cleanup, before AC_COMPLETE):**
Query `audit_violations` for P0 violations appearing in ≥3 sessions without auto-fix.
If found: emit inline — recurring systemic issues require architectural fix.

**Workflow Template:** `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml`
**Convergence Loop Primitive:** `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`