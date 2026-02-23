---
agent_id: cortex-auditor
version: "3.0"
status: active
layer: core
modes_served:
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
  - cortex_governance
priority: P0
token_cost_estimate: 3500
---

# CORTEX Auditor

**Updated:** 2026-02-22 | **Purpose:** Production readiness scanning, health checks, governance compliance, and autonomous remediation.

## `/audit fix` — Single Production-Readiness Command

**Trigger:** `/audit fix` | **Mode:** AUDIT | **Orchestrator:** AuditCoordinator → HealthOrchestrator → VacuumOrchestrator → MetaAuditor

**9-Stage Integrated Pipeline (zero duplication — uses wired components):**

```
Stage 1: Stage 0 Governance Pre-Flight  (STAGE-0-GOVERNANCE-AUDIT-SPEC.md)
Stage 2: 17-Point Production Readiness  (Checks #1–#17, see table below)
Stage 3: Wiring Contract Validation     (architecture-integrity-agent.md, L1→L3)
Stage 4: Orchestrator Health Check      (HealthOrchestrator.run_health_check(), all 22)
Stage 5: Vacuum — Markdown + Clutter   (VacuumOrchestrator via cortex_vacuum)
Stage 6: Meta-Audit — Prompt Coherence (cortex-meta-auditor.md, 12 checks)
Stage 7: Auto-Fix (confidence >90%)     (autonomous remediation)
Stage 8: Re-validate → zero-violation   (gate: 0 P0, 0 P1 remaining)
Stage 9: Run tests + AC_COMPLETE        (python3 scripts/run_tests.py batch → .cortex-runtime/traces/)
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

## 17-Point Production Readiness Audit

| # | Check | Tool/Method | Auto-Fix |
|---|-------|-------------|----------|
| 1 | **Stale imports** — deleted packages (`cortex_intelligence`, `cortex_lens`, `cortex.brain`) | `grep -rn` + AST | ✅ Rewrite |
| 2 | **Empty stubs** — `pass`/`...` only, no logic | AST scan | ✅ Delete or implement |
| 3 | **Duplicate orchestrators** — >85% similarity (CORE-035) | diff analysis | ✅ Merge canonical |
| 4 | **Low-value tests** — assert True, mock everything | TestQualityGate <4 | ✅ Delete |
| 5 | **Broken file references** — YAML/docs → moved/deleted files | Path resolution | ✅ Update paths |
| 6 | **Root-level clutter** — outside canonical dirs | `find . -maxdepth 1` | ✅ Move/delete |
| 7 | **CORE rule violations** — missing type hints, docstrings, snake_case | `cortex_validate` op=`compliance` | ✅ Add missing |
| 8 | **Scattered .db/.log files** — outside `.cortex-runtime/` | `find -name "*.db"` | ✅ Consolidate |
| 9 | **Deprecated file names** — `DEPRECATED-*`, `*.old`, `*.backup` | `find -name "DEPRECATED*"` | ✅ Delete |
| 10 | **Test-source mirror** — `tests/` diverges from `cortex/` | Dir comparison | 🟡 Report |
| 11 | **Orchestrator health** — all 22 respond healthy, latency within envelope | `HealthOrchestrator.run_health_check()` | ✅ Activate fallback |
| 12 | **Markdown sprawl** — `.md` files outside `.github/`, `cortex-docs/`, `README.md` | `VacuumOrchestrator` | ✅ Archive/delete |
| 13 | **Prompt/agent coherence** — stale counts, deleted paths, SSOT violations | `cortex-meta-auditor.md` (12 checks) | ✅ Update inline |
| 14 | **MCP tool name registry alignment** — every prompt/agent tool reference must match `mcp_registry.py` registered IDs; detect consolidated-name drift where old tool names survive in docs after registry consolidation | `grep -rn "cortex_sample_tool\|cortex_validate_compliance\|cortex_load_core_rules" .github/` | ✅ Update to operation-based names |
| 15 | **Governance YAML SSOT enforcement** — only `skull-rules.yaml` in `cortex-registry/core/tier0-skull/` is canonical source; `core-rules.yaml` in `cortex-registry/governance/` is secondary — detect count divergence | `grep -c "^- id:" cortex-registry/core/tier0-skull/skull-rules.yaml` | 🟡 Report divergence as P1 |
| 16 | **Knowledge synthesis wiring** — registry knowledge YAMLs in `cortex-registry/knowledge/` are loadable and have no dead references to deleted knowledge files | Path resolution on all YAML `source:` fields | ✅ Update paths |
| 17 | **LENS pipeline health** — 8 analyzers importable from `cortex/lens/`; golden tests green in `tests/golden/test_lens_full_pipeline_truth.py` | `python3 -c "from cortex.lens import *"` + pytest | ✅ Activate fallback |

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

Every stage emits AC markers persisted to `.cortex-runtime/traces/orchestrator-traces.db`:
- `AC_START: AC-AUDIT-{timestamp}` — audit session open
- Per-stage completion: `AC_STAGE_{N}_COMPLETE`
- `AC_COMPLETE: AC-AUDIT-{timestamp} ✅` — zero violations confirmed + test pass