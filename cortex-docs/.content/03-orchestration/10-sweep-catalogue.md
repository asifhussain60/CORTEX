# Sweep Catalogue

---
title: Sweep Catalogue — CORE-064 Sweep Completeness Contract
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/support/sweep_catalogue_orchestrator.py + cortex-registry/core/CORE-064.yaml
order: 10
---

> **Brain analogy:** The Sweep Catalogue is the **prefrontal cortex**'s task-completion centre. It ensures CORTEX never declares a sweep done until every item in the catalogue has been explicitly addressed — the same way a careful surgeon counts every instrument before closing.

---

## Overview

The **Sweep Completeness Contract** (CORE-064) guarantees that every `FIX`, `REFACTOR`, or `AUDIT` operation exhausts its full issue catalogue before reporting success. Partial sweeps — where some issues are skipped due to token budget, time pressure, or oversight — are a governance violation.

The `SweepCatalogueOrchestrator` enforces this contract by maintaining a persistent SQLite catalogue of every open issue discovered during a sweep. Orchestrators must call `mark_resolved()` for each item; `assert_exhausted()` is the final gate before reporting completion.

---

## CORE-064 Rule

| Field | Value |
|-------|-------|
| **Rule ID** | CORE-064 |
| **Name** | Sweep Completeness Contract |
| **Severity** | P0 — Blocking |
| **Enforcement** | Pre-commit hook + runtime gate |
| **Introduced** | Phase 16 |

**Contract:** *Every FIX/REFACTOR/AUDIT operation MUST exhaustively process its complete issue catalogue before declaring success. Partial sweeps are a governance violation.*

---

## SweepCatalogueOrchestrator

**Location:** `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`

### Lifecycle

```
1. open_sweep(sweep_id, issues)    ← Register all discovered issues
       │
       ▼
2. [Orchestrator processes issues one-by-one]
       │
       ▼
3. mark_resolved(sweep_id, issue_id)   ← Called for each fixed issue
       │
       ▼
4. assert_exhausted(sweep_id)          ← Final gate — raises if any open issues remain
       │
       ▼
5. [Only now can the sweep report SUCCESS]
```

### API Reference

```python
from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator

orch = SweepCatalogueOrchestrator()

# Step 1: Register the full catalogue of issues
sweep_id = "fix-security-2026-02-21"
await orch.open_sweep(sweep_id, issues=[
    {"id": "issue-001", "description": "SQL injection in auth.py:42"},
    {"id": "issue-002", "description": "XSS vector in template.py:88"},
    {"id": "issue-003", "description": "Credentials in config.py:12"},
])

# Step 2–3: Process and mark each issue resolved
await orch.mark_resolved(sweep_id, issue_id="issue-001")
await orch.mark_resolved(sweep_id, issue_id="issue-002")
await orch.mark_resolved(sweep_id, issue_id="issue-003")

# Step 4: Assert all issues are resolved before reporting done
await orch.assert_exhausted(sweep_id)
# ← Raises SweepIncompleteError if any issues remain open
```

### Storage

Sweep state is persisted in **SQLite WAL mode**:

```
.cortex-runtime/sweeps/{sweep_id}.db
```

This means sweeps survive process restarts and token budget resets — a new Copilot session can resume an in-progress sweep by calling `get_open_issues(sweep_id)` to see what remains.

---

## Sweep Status Access

Sweep status is exposed via `SweepCatalogueOrchestrator` directly. The `.db` files in `.cortex-runtime/sweeps/` are SQLite WAL databases queryable by any orchestrator.

> Note: `cortex_sweep_status` is referenced in older documentation but is not currently registered in `mcp_registry.py`. Sweep catalogue access is via the orchestrator's `get_open_issues(sweep_id)` method.

```python
# Programmatic access
from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepCatalogueOrchestrator
orchestrator = SweepCatalogueOrchestrator()
open_issues = orchestrator.get_open_issues("fix-security-2026-02-21")
```

---

## Integration with EnforcementOrchestrator

`EnforcementOrchestrator` calls `assert_exhausted()` as part of the pre-commit gate. If any sweep registered for the current branch has open items, the commit is **blocked**:

```
EnforcementOrchestrator.pre_commit_gate()
      ├── Check CORE rule violations
      ├── Validate test coverage
      └── assert_exhausted(current_sweep_id)   ← CORE-064 gate
              ↓ raises SweepIncompleteError
              ↓ pre-commit hook exits non-zero
              ↓ commit is blocked
```

---

## Practical Examples

**Developer:** "I'm fixing 12 security findings. With CORE-064, I open a sweep catalogue at the start, mark each finding resolved as I fix it, and the pre-commit hook will block my commit if I miss even one."

**Product Owner:** "The sweep catalogue gives us audit trail evidence that every discovered issue in a sprint was addressed — not just the easy ones. Compliance teams love it."

**Business Leader:** "CORE-064 means 'done' actually means done. No more partial fix reports that quietly skip the hard cases."

---

## Related Documents

- [Governance & Compliance](../01-capabilities/05-governance-compliance.md) — Full CORE rule set including CORE-064
- [MCP Tools Catalog](../04-mcp/03-tools-catalog.md) — registered tool reference
- [Master Orchestrator](02-master-orchestrator.md) — How sweeps integrate with 4-stage pipeline

---

*Verified against `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` · CORE-064 active · 21 February 2026*
