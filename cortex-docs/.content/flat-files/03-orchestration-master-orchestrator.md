# MasterOrchestrator

---
title: MasterOrchestrator — The Executive Coordinator
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-25
source_of_truth: cortex/orchestrators/core/master_orchestrator.py
order: 2
---

> **Brain analogy:** MasterOrchestrator is the **thalamus** — the central relay hub. Every sensory signal (request) passes through it before reaching the specialized cortical regions (domain orchestrators). It doesn't process the work itself; it ensures the right region handles it.

---

## Responsibility

MasterOrchestrator coordinates all 27 wired orchestrators through hierarchical dispatch:

1. Receives enriched request from MCP Gateway (39 tools, Pylance-style stdio)
2. Invokes IntentRouter for LENS-based classification (20–40ms)
3. Dispatches to the appropriate orchestrator across 3 canonical tiers
4. Monitors execution progress via AC markers
5. Records audit trail to `.cortex-runtime/traces/orchestrator-traces.db`

**Location:** `cortex/orchestrators/core/master_orchestrator.py`
**Implements:** `IOrchestrator` via `OrchestratorProtocolMixin` (Phase 58 — canonical base)

---

## The 9-Stage Audit Pipeline

MasterOrchestrator owns and coordinates the `/audit fix` pipeline:

| Stage | Name | Key Component |
|-------|------|---------------|
| −1 | Environment Readiness | `UpgradeOrchestrator.validate_requirements()` — preflight |
| 0 | Inflight Upgrade + Pre-Flight | git fetch origin/main + STAGE-0-GOVERNANCE-AUDIT-SPEC.md |
| 1 | Stage 0 Governance Pre-Flight | Full spec validation |
| 2 | 19-Point Production Scan | cortex-auditor.md Checks #1–#19, SQLite health |
| 3 | Wiring Contract Validation | architecture-integrity-agent.md L1→L3 |
| 4 | Orchestrator Health (all 22) | `HealthOrchestrator.run_health_check()` |
| 5 | Vacuum Cleanup | `VacuumOrchestrator` + `cortex_vacuum` |
| 6 | Prompt/Agent Meta-Audit | cortex-meta-auditor.md — 23 checks |
| 7–8 | Auto-Fix Convergence Loop | detect-fix-rescan-loop primitive — loops until 0 P0/P1 |
| 9 | Tests + AC_COMPLETE | `python3 scripts/run_tests.py batch` → SQLite cleanup |

---

## Multi-Stage Decomposition

For complex pipelines, MasterOrchestrator delegates to stage-specific implementations:

| File | Stage Coverage |
|------|----------------|
| `master_orchestrator_stage_1.py` | Stage 0 governance audit + pre-flight |
| `master_orchestrator_stage_3.py` | Wiring contract + architecture integrity |
| `master_orchestrator_stage_4.py` | Orchestrator health endpoints |

---

## Core Tier Context

MasterOrchestrator is one of **7 core-tier orchestrators**:

| Orchestrator | Role |
|---|---|
| **MasterOrchestrator** | Top-level coordinator — routes intents, manages 9-stage audit pipeline |
| IntentRouter | LENS-based request classification → 12+ intent types |
| TDDOrchestrator | RED→GREEN→REFACTOR cycle enforcement (CORE-008) |
| EnforcementOrchestrator | Pre-commit 35-CORE-rule validation + SQLite audit |
| WorkflowOrchestrator | YAML workflow template execution engine |
| ConversationOrchestrator | Multi-turn conversation, state persistence |
| AuditOrchestrator | 19-point production readiness audit — P0/P1/P2 scanning |

---

## AC Marker Protocol

Every MasterOrchestrator invocation emits AC markers:

```python
# AC_START: AC-MASTER-{TIMESTAMP}
# ... orchestrator logic ...
# AC_COMPLETE: AC-MASTER-{TIMESTAMP} ✅  (ms elapsed)
```

Markers persist to `.cortex-runtime/traces/orchestrator-traces.db` (schema: `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs`).

---

## Practical Examples

**Business Leader:** "MasterOrchestrator is the control tower. Every development action — implementing features, fixing bugs, auditing code — passes through it. Nothing bypasses governance."

**Product Owner:** "The 9-stage audit pipeline is deterministic. Stage 7–8 loop until P0/P1 violations hit zero (CORE-064). You get a convergence guarantee, not a best-effort scan."

**Developer:** "I call `/audit fix` and MasterOrchestrator runs all 9 stages autonomously. AC markers in `.cortex-runtime/traces/orchestrator-traces.db` give me a full execution timeline if anything goes wrong."

---

*Verified against `cortex/orchestrators/core/master_orchestrator.py` · 25 February 2026 · Phase 79-D complete · 27 wired orchestrators (7 core, 6 domain, 14 support)*
