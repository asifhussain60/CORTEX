# CORTEX RCA Memory Engine

---
title: RCA Memory Engine — Root Cause Analysis, Prevention Gate, and Recurrence Detection
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/intelligence/learning/ + cortex/core/orchestrator_protocol_mixin.py + cortex/mcp/tools/cortex_learning.py
order: 21
---

> **The central idea:** Recording *what* failed is necessary but insufficient. The RCA Memory Engine captures *why* it failed using four proven industrial methodologies — and then prevents the same root cause from striking twice using a structured Prevention Gate.

---

## Why Root Cause Analysis Is Institutional Infrastructure

Every engineering team writes the same bug more than once. Not because developers are careless, but because root cause knowledge is ephemeral — stored in a Slack thread, a Confluence page that no one reads, or an individual's memory that leaves when they do.

CORTEX's RCA Memory Engine makes root cause analysis persistent, structured, and actionable. Every time a failure is analysed, the result is stored in a queryable SQLite database, cross-referenced against all previous failures, and converted into a prevention rule that fires automatically the next time the same causal pattern is detected.

The result is institutional memory that compounds. The tenth occurrence of a root cause class is far cheaper to prevent than the first — because CORTEX has seen it nine times before.

---

## Architecture Overview

The RCA Engine is built entirely within CORTEX's existing learning infrastructure. It introduces zero new orchestrators and zero new MCP tools. Instead, it extends:

- **OPJMixin** — adds two new methods to the Operational Pattern Journal mixin
- **cortex_learning MCP tool** — adds a new `op="rca"` operation to the existing tool
- **CrossSessionPatternCache** — adds four new SQLite tables to the existing cache store
- **URS (Unified Reinforcement Signal)** — emits structured signals based on RCA outcomes

All components live in `cortex/intelligence/learning/`.

### New Files

| File | Purpose |
|------|---------|
| `cortex/intelligence/learning/rca_engine.py` | Core RCA analysis engine — four methodologies |
| `cortex/intelligence/learning/rca_models.py` | `RCAAnalysis` dataclass, `RCATemplate` enum, `RCACategory` enum |
| `cortex/intelligence/learning/rca_store.py` | SQLite persistence layer for all RCA data |
| `cortex/intelligence/learning/prevention_gate.py` | `PreventionGate` — advisory/blocking logic |
| `cortex/intelligence/learning/recurrence_engine.py` | `RecurrenceSignatureEngine` — fingerprinting and matching |
| `cortex-registry/workflows/templates/rca/rca-analysis-workflow.yaml` | Orchestration workflow template |

---

## Four Analysis Methodologies

The `RCAEngine` selects the appropriate methodology based on the failure's `RCACategory`:

### 1. Five Whys — Linear Causal Chain

The simplest and most widely applicable methodology. Starting from the observable symptom, the engine asks "why?" repeatedly until it reaches a root cause at depth 3 or greater.

```
Symptom: Test suite failing on async endpoint
  Why 1: AttributeError raised in response handler
  Why 2: Response object accessed before await completed
  Why 3: Missing `await` keyword in calling code
  Why 4: No async linting rule enforced in CI  ← ROOT CAUSE
```

Best for: Sequential failures, missing null checks, unhandled exceptions, any failure with a clear linear cause chain.

### 2. Fishbone (Ishikawa) — Category Analysis

For failures with multiple contributing causes across different domains, the Fishbone methodology maps causes to four standard categories:

| Category | Examples |
|----------|---------|
| **People** | Missing code review, wrong assumptions, context switch errors |
| **Process** | No linting for async patterns, TDD skipped for "small" changes |
| **Technology** | Framework version mismatch, deprecated API usage |
| **Data** | Test fixtures stale, mock data not representative of production |

Best for: Multi-factor failures that involve team practices, tooling, and data quality simultaneously.

### 3. Fault Tree — Probability-Weighted Tree

For complex system-wide failures with multiple contributing paths, the Fault Tree methodology builds a tree of AND/OR gates. Each leaf node is an observable event; each gate represents whether *all* (AND) or *any* (OR) of its children must be true for the parent to occur.

Best for: Race conditions, distributed system failures, failures with multiple independent contributing paths.

### 4. Causal Chain — Time-Ordered Sequence

For failures that unfold over time — cascade shutdowns, async race conditions, event loop saturation — the Causal Chain methodology records events in temporal order with timestamps and delta measurements.

Best for: Production incidents, performance degradations, anything with a clear before/after event sequence.

---

## The Prevention Gate

The Prevention Gate intercepts future operations before they execute and checks them against stored prevention rules. The gate has three severity levels:

| Recurrence Count | Gate Level | User Experience |
|-----------------|------------|----------------|
| 1st occurrence | **Advisory** | Info message surfaces in next OPJ consult: "Similar past failure: RCA-2026-001. Root cause: missing async boundary." |
| 2nd occurrence | **Warning** | Governance gate response includes warning with full RCA reference and previous fix summary |
| 3rd+ P0 occurrence | **Blocking** | Operation halts. Structured review required. `cortex_learning op="rca" action="review_required"` must be acknowledged |

The blocking threshold applies only to P0-severity recurrences. P1 recurrences remain at Warning after three occurrences. P2 recurrences remain Advisory indefinitely.

### Gate Bypass (Emergency Override)

In production emergency scenarios, the Prevention Gate can be bypassed with explicit acknowledgment:

```
cortex_learning op="rca" action="bypass_gate" rca_id="RCA-2026-001" reason="Production P0 — hotfix required"
```

The bypass is logged to the audit trail with the reason and the requestor's session ID. Bypass frequency is tracked and surfaces in the weekly governance summary.

---

## Recurrence Signature Engine

The `RecurrenceSignatureEngine` generates a canonical fingerprint for every RCA:

```
RCA-SIG-{methodology}-{category}-{root_cause_hash[:8]}
```

For example: `RCA-SIG-FIVE_WHYS-TECHNOLOGY-a3f9b2c1`

When a new failure arrives, its signature is compared against all stored signatures using a multi-factor similarity algorithm:

- **Exact match (100%)** — Same root cause, same category. Recurrence counter incremented.
- **Near match (85–99%)** — Same root cause class, different specific cause. Advisory surfaced.
- **Cluster match (70–84%)** — Same failure category, different root cause. Contextual suggestion offered.
- **No match (<70%)** — Novel failure. New RCA record created.

### Cross-Orchestrator Recurrence Detection

Recurrence detection is not scoped to a single orchestrator. The same root cause class appearing in TDDOrchestrator, EnforcementOrchestrator, and DebuggerOrchestrator all contribute to the same recurrence counter. This cross-orchestrator visibility surfaces systemic issues that would be invisible within a single orchestrator's journal.

---

## URS Integration

Every RCA outcome emits a Unified Reinforcement Signal (URS) that feeds back into the confidence layer:

| Outcome | URS Signal | Effect |
|---------|-----------|--------|
| P0 recurrence blocked | `STRONG_PUNISHMENT (−1.0)` | Root cause pattern confidence reduced; prevention rule promoted |
| P1 recurrence warned | `MODERATE_PUNISHMENT (−0.5)` | Pattern confidence reduced |
| Prevention gate fired correctly | `MODERATE_REWARD (+0.5)` | Prevention rule confidence increased |
| Prevention gate blocked and developer confirmed correct | `STRONG_REWARD (+1.0)` | Prevention rule promoted to top-tier knowledge |
| Prevention gate false-positive bypassed | `MODERATE_PUNISHMENT (−0.5)` | Prevention rule confidence reduced |

---

## SQLite Schema

Four new tables are added to `.cortex-runtime/rca/rca_store.db`:

### `rca_analyses`

```sql
CREATE TABLE rca_analyses (
  id TEXT PRIMARY KEY,              -- RCA-{uuid}
  failure_id TEXT NOT NULL,         -- Link to OPJ failure entry
  methodology TEXT NOT NULL,        -- FIVE_WHYS | FISHBONE | FAULT_TREE | CAUSAL_CHAIN
  category TEXT NOT NULL,           -- TECHNOLOGY | PROCESS | PEOPLE | DATA
  root_cause TEXT NOT NULL,         -- Structured root cause string
  analysis_json TEXT NOT NULL,      -- Full RCAAnalysis as JSON
  confidence REAL NOT NULL,         -- 0.0–1.0
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `prevention_rules`

```sql
CREATE TABLE prevention_rules (
  id TEXT PRIMARY KEY,              -- PREV-{uuid}
  rca_id TEXT NOT NULL,             -- Foreign key to rca_analyses
  rule_text TEXT NOT NULL,          -- Human-readable prevention rule
  gate_level TEXT NOT NULL,         -- ADVISORY | WARNING | BLOCKING
  active BOOLEAN DEFAULT TRUE,
  trigger_count INTEGER DEFAULT 0,
  false_positive_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `recurrence_signatures`

```sql
CREATE TABLE recurrence_signatures (
  signature TEXT PRIMARY KEY,       -- RCA-SIG-{methodology}-{category}-{hash}
  rca_ids TEXT NOT NULL,            -- JSON list of linked rca_analyses IDs
  occurrence_count INTEGER DEFAULT 1,
  last_seen TIMESTAMP,
  severity TEXT NOT NULL            -- P0 | P1 | P2
);
```

### `recurrence_incidents`

```sql
CREATE TABLE recurrence_incidents (
  id TEXT PRIMARY KEY,
  signature TEXT NOT NULL,          -- Foreign key to recurrence_signatures
  orchestrator TEXT NOT NULL,       -- Which orchestrator triggered the recurrence
  session_id TEXT,
  gate_action TEXT NOT NULL,        -- ADVISED | WARNED | BLOCKED | BYPASSED
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## OPJ Integration

The RCA Memory Engine adds two new methods to `OPJMixin` in `cortex/core/orchestrator_protocol_mixin.py`:

### `_opj_analyze_rca(failure_id, methodology=None)`

Runs structured RCA on an existing OPJ failure entry. If `methodology` is not specified, the `RCAEngine` selects the best methodology based on the failure's category.

Returns an `RCAAnalysis` dataclass with the full structured analysis, prevention rule, and recurrence signature.

### `_opj_check_prevention_gate(operation_context)`

Called at the start of any operation that may be related to a known failure pattern. Checks `operation_context` against all active prevention rules. Returns a `PreventionGateResult` with the gate level (`PASS`, `ADVISORY`, `WARNING`, or `BLOCKED`) and the matched rule if any.

---

## MCP Interface

The `cortex_learning` MCP tool gains a new `op="rca"` operation:

```json
{
  "tool": "cortex_learning",
  "arguments": {
    "op": "rca",
    "action": "analyze",
    "failure_id": "OPJ-2026-001",
    "methodology": "five_whys"
  }
}
```

Supported actions:

| Action | Description |
|--------|-------------|
| `analyze` | Run RCA on an OPJ failure entry |
| `query` | Query stored RCA analyses by date, category, or severity |
| `summary` | Summarise recurrence patterns for a time window |
| `review_required` | Acknowledge a blocking gate to allow proceeding |
| `bypass_gate` | Emergency override with mandatory reason |

All responses are delivered inline per CORE-002 — no report files are created.

---

## cortex-docs Sync

Documentation files that reference orchestrator counts, test baselines, or learning capabilities are kept in sync with the live codebase.

This flat-file (`21-rca-memory-engine.md`) is part of the documentation sync deliverable.

---

## For Business Leaders

Root cause analysis has been an engineering discipline for decades, but it has remained manual, inconsistent, and organisationally siloed. CORTEX's RCA Memory Engine automates the capture, storage, retrieval, and enforcement of root cause knowledge — turning every incident into a compounding institutional asset.

The Prevention Gate means that the third time a team encounters the same root cause class, CORTEX stops them before they make the same mistake again. The deeper the team's history with CORTEX, the smarter its prevention gets.

For organisations with high engineer turnover, this is particularly valuable. Knowledge that would otherwise leave with a departing engineer stays encoded in the RCA store, surfaced automatically to their successors.

---

*Live capability (Phase 87) · 121 GREEN tests · Zero new orchestrators · Zero new MCP tools*
