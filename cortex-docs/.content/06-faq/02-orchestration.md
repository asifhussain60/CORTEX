# FAQ — Orchestration & Architecture

---
title: FAQ — Orchestration & Architecture
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/
order: 2
---

> **Purpose:** Answers to questions about how CORTEX's multi-tier orchestrator architecture works, how requests flow, and how the system makes routing decisions. All answers verified against live code.

---

## How many orchestrators does CORTEX have?

**Wired orchestrators** across **4 tiers**:

| Tier | Count | Orchestrators |
|------|-------|--------------|
| **Core** | — | MasterOrchestrator, IntentRouter, TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator, ConversationOrchestrator, InteractionOrchestrator |
| **Domain** | — | RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, ServiceDecompositionOrchestrator, LegacyModernizationOrchestrator |
| **Support** | — | OnboardingOrchestrator, SetupOrchestrator, UpgradeOrchestrator, HealthOrchestrator, VacuumOrchestrator, SweepCatalogueOrchestrator, BulkDigestOrchestrator, DigestSessionOrchestrator, DebuggerOrchestrator, UnifiedDiscoveryOrchestrator, UnifiedQualityOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator, PhaseCompletionOrchestrator |

> **Note:** `cortex/orchestrators/` contains many more Python classes (strategy implementations, mixins, sub-components). The **wired** orchestrators are the canonical `IOrchestrator`-compliant entry points registered in `cortex-registry/core/specifications/`.

---

## What is the universal orchestrator lifecycle?

Every orchestrator satisfies `IOrchestrator` via `OrchestratorProtocolMixin`. The 5-step lifecycle is:

```
setup() → govern() → execute() → validate() → teardown()
```

`execute()` and `run()` auto-log `ORCHESTRATOR_START` / `ORCHESTRATOR_END` to `.cortex-runtime/audit.db` (SQLite WAL). Audit failures are **non-blocking** — a write failure never stops execution.

---

## What is the primary base class for orchestrators?

**`OrchestratorProtocolMixin`** (`cortex/core/orchestrator_protocol_mixin.py`) — used by all wired orchestrators.

`OrchestratorBase` (`cortex/core/orchestrator_base.py`) is the legacy base — only 2 orchestrators still use it. Do not use it for new orchestrators.

---

## How does CORTEX route a request to the right orchestrator?

**IntentRouter** (`cortex/orchestrators/core/intent_router.py`) classifies every request using LENS analysis and keyword extraction. It supports 12+ intent types:

| Intent | Routes To |
|--------|----------|
| `IMPLEMENT` | TDDOrchestrator |
| `FIX` | TDDOrchestrator |
| `REFACTOR` | RefactoringOrchestrator |
| `ANALYZE` | LENS Synthesis |
| `PLAN` | PlanningOrchestrator |
| `AUDIT` | EnforcementOrchestrator |
| `DEBUG` | DebuggerOrchestrator |
| `DIGEST` | BulkDigestOrchestrator / DigestSessionOrchestrator |
| `REPHRASE` | RequestRephraseOrchestrator |
| `DESIGN` | Design coordination |
| `INVESTIGATE` | UnifiedDiscoveryOrchestrator |
| `QUERY` | Context-dependent |

Classification uses `detect_intent()` — a LENS-backed keyword + confidence model. The result is a `(IntentType, confidence_score)` pair. Scores ≥ 0.7 auto-route; 0.5–0.7 may seek clarification; < 0.5 prompts the user.

---

## What is MasterOrchestrator's role?

MasterOrchestrator (`cortex/orchestrators/core/master_orchestrator.py`) is the **conductor** — it does not execute domain logic itself. It:

1. Receives every request from the MCP layer
2. Delegates to IntentRouter for classification
3. Dispatches to the appropriate tier orchestrator
4. Collects results and formats them via the response pipeline

The 4-stage pipeline is split across:
- `master_orchestrator_stage_1.py` — Comprehension + DoR
- `master_orchestrator_stage_2.py` — Intelligence + LENS
- `master_orchestrator_stage_3.py` — Execution + orchestrator dispatch
- `master_orchestrator_stage_4.py` — Response formatting + AC markers

---

## What is TDDOrchestrator and when does it activate?

**TDDOrchestrator** (`cortex/orchestrators/core/tdd_orchestrator.py`) handles all `IMPLEMENT` and `FIX` intents. It enforces the RED → GREEN → REFACTOR cycle mandated by **CORE-008**:

```
RED     → Write a failing test that specifies the behaviour
GREEN   → Write minimum code to make the test pass
REFACTOR → Improve code while keeping all tests passing
```

This is **not optional**. CORE-008 is a Tier 0 skull rule — attempts to skip TDD are BLOCKED by EnforcementOrchestrator before any files change. CORE-019 ensures ALL implementation intents route through TDD-Master.

---

## What is SweepCatalogueOrchestrator and why does it exist?

**SweepCatalogueOrchestrator** (`cortex/orchestrators/support/sweep_catalogue_orchestrator.py`) enforces **CORE-064: Sweep Completeness Contract**.

**The problem it solves:** Long-running FIX/REFACTOR/AUDIT operations span multiple sessions. Before CORE-064, a sweep could be abandoned mid-run — leaving the codebase in a partial-fix state with no record of what was done.

**How it works:** Every sweep is tracked in `.cortex-runtime/sweeps/{sweep_id}.db` (SQLite WAL). A sweep cannot be closed until every item in its catalogue has `status: CLOSED` or an explicit `approve_wont_fix` decision. `SweepCatalogueOrchestrator.get_open_issues(sweep_id)` surfaces open sweeps across sessions.

---

## Can I create my own orchestrator?

Yes. The pattern is:

1. Create a new file in `cortex/orchestrators/{core|domain|support}/` (snake_case — CORE-028)
2. Inherit from `OrchestratorProtocolMixin`
3. Implement `setup()`, `execute()`, `validate()`, `get_name()`, `get_mode()`
4. Add AC markers (`AC_START` / `AC_COMPLETE`) in every public method
5. Write the test first (CORE-008)
6. Register in `cortex-registry/core/specifications/wiring/`

**Template location:** `cortex-registry/core/specifications/` contains the canonical wiring spec for reference.

---

## What are AC markers and why are they required?

**AC markers** are audit trail bookmarks emitted by every orchestrator invocation:

```python
# AC_START: AC-{DOMAIN}-{TIMESTAMP}    ← opens the session
# ... orchestrator logic ...
# AC_COMPLETE: AC-{DOMAIN}-{TIMESTAMP} ✅  ← closes with timing
```

They write to `.cortex-runtime/traces/orchestrator-traces.db` (SQLite). Rules:
- `AC_START` at every public method entry point
- `AC_COMPLETE` on success (`✅` + ms timing) or failure (`❌` + error class)
- No orphaned `AC_START` without a matching `AC_COMPLETE` (P0 violation — Check #19 of the 19-Point Audit)

Enforced by `EnforcementOrchestrator` at pre-commit and by the `/audit fix` Stage 6 meta-audit.

---

## What is the `/audit fix` command?

The canonical single command for production readiness. It runs a **9-stage pipeline**:

| Stage | Action |
|-------|--------|
| -1 | Environment preflight (`UpgradeOrchestrator.validate_requirements()`) |
| 0 | Inflight upgrade + pre-flight governance check |
| 1 | Stage 0 governance pre-flight (full spec) |
| 2 | 19-Point production scan (Checks #1–#19) |
| 3 | Wiring contract validation (L1→L3 architecture integrity) |
| 4 | Orchestrator health (all 22 health endpoints) |
| 5 | Vacuum cleanup (markdown sprawl removal) |
| 6 | Prompt/agent meta-audit (23 checks) |
| 7–8 | Auto-fix convergence loop (detect → fix → rescan until 0 P0/P1) |
| 9 | Full test suite + AC_COMPLETE + SQLite cleanup |

**Convergence guarantee (CORE-064):** Stages 7–8 loop until `p0_count == 0 AND p1_count == 0` — not a single pass. The loop primitive is defined in `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`.

---

## How does cross-orchestrator communication work?

Orchestrators do not call each other directly. Communication flows through:

1. **MasterOrchestrator dispatch** — the primary routing mechanism
2. **SharedAuditTrail** (`cortex/orchestrators/shared_audit_trail.py`) — shared audit context across orchestrator boundaries
3. **LENS context** — LENS analysis results are passed as a structured context object, not re-computed per orchestrator
4. **WorkflowEngine** (`cortex/core/workflow_engine.py`) — for multi-step pipelines defined in YAML

This keeps orchestrators loosely coupled and independently testable. See `03-orchestration/06-cross-orchestrator.md` for the full architecture.

---

## What happens if an orchestrator fails mid-execution?

CORTEX has three layers of resilience:

1. **Circuit Breaker** (`cortex/infrastructure/circuit_breaker.py`) — stops calls to a failing orchestrator after threshold breaches. States: Closed → Open → Half-Open.
2. **Retry Handler** (`cortex/infrastructure/retry_handler.py`) — configurable retry with exponential backoff for transient failures.
3. **Graceful Degradation** (`cortex/infrastructure/graceful_degradation.py`) — returns partial results when non-critical sub-components fail.

Audit failures (SQLite write errors) are explicitly non-blocking — a broken audit log never stops a developer's workflow.

---

*Verified against `cortex/orchestrators/`*
