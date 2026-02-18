# End-to-End Request Flow

---
title: End-to-End Request Flow — Complete Trace from User Input to Delivered Result
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-18
source_of_truth: cortex/orchestrators/ + cortex/__wiring_contract__.yaml + cortex/mcp/
format: diátaxis-explanation
voice: third-person-blended
phase: Production (v8.1)
order: 8
---

> **Purpose:** Walk through a single real request — "implement email validation with TDD" — from the moment it leaves the user's keyboard to the moment CORTEX returns the result. Every layer is shown with actual timings.

---

## The Request

```
User types in VS Code Copilot Chat:
"implement a validate_email function with full TDD"
```

Total elapsed time at completion: **~1.1 seconds**

---

## Full Trace

### T+0ms — MCP Gateway Receives the Request

The VS Code MCP client serialises the message as JSON-RPC 2.0 and sends it to the CORTEX MCP server:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_process_request",
    "arguments": {
      "request": "implement a validate_email function with full TDD"
    }
  },
  "id": "req-20260218-001"
}
```

The MCP server assigns a `request_id`, opens an audit record in `governance.db`, and passes the raw request to the pipeline.

---

### T+0ms → T+18ms — Stage -1: RequestRephraseOrchestrator

Automatically enriches the request before classification:

**Input:** `"implement a validate_email function with full TDD"`

**Enrichment applied:**
- Governance context prepended: CORE-008 (TDD mandatory) loaded
- Domain detection: Python codebase detected via LENS polyglot scan
- Session context: No recent related requests (cold context)

**Output:** `"implement validate_email(address: str) -> bool in Python with TDD: write failing test first (CORE-008), minimal GREEN implementation, REFACTOR pass. Type hints mandatory."`

---

### T+18ms → T+50ms — Stage 2: IntentRouter

Classifies the enriched request:

| Dimension | Result | Confidence |
|-----------|--------|------------|
| Intent type | IMPLEMENT | 0.97 |
| Target orchestrator | TDDOrchestrator | 0.97 |
| Risk tier | Tier 0 (requires gate) | — |
| Domain | Python / generic | 0.91 |

IntentRouter routes to MasterOrchestrator with classification attached.

---

### T+50ms → T+200ms — Stage 3: Holistic Validation Gate

MasterOrchestrator runs 7-step pre-execution validation in parallel where possible:

```
T+50ms  ├── Registry consistency check          → PASS (200ms)
T+50ms  ├── LENS pre-warm (async, already warm) → PASS (0ms, cached)
T+55ms  ├── Dependency graph analysis           → Risk 0.08
T+55ms  ├── Regression risk scorer              → 0.10 → PASS
T+60ms  ├── Architecture drift detection        → 0% drift
T+65ms  ├── Challenge gate                      → 1 alternative presented
T+200ms └── Validation complete                 → VERDICT: PASS
```

Risk score 0.10 < 0.4 threshold → proceed without blocking.

Challenge gate presented (CORE-048):

```
⚠️ MANDATORY CHALLENGE

Your Approach: Custom regex validation
  Pros: Full control, no dependencies
  Cons: Edge cases in RFC 5321 are hard to cover

Alternative A (Recommended): email-validator library wrapper
  Pros: RFC-compliant, battle-tested
  Cons: External dependency added

Decision required — user types "proceed" to use custom approach
```

User types: `proceed`

---

### T+200ms → T+500ms — LENS Intelligence (Stage 3 continued)

LENSSynthesis runs 8 analyzers (pre-warmed from async fetch):

| Analyzer | Finding | Time |
|----------|---------|------|
| AST | No existing `validate_email` in codebase | 45ms |
| Git History | Email validation attempted 3 months ago, deleted | 12ms |
| Comment | Docstring patterns: Google style preferred | 8ms |
| Config | pytest configured, coverage required ≥90% | 3ms |
| Dependency | `re` available (stdlib), no `email-validator` installed | 6ms |
| API Contract | No public API exports to consider | 4ms |
| Database | Not applicable | 1ms |
| Polyglot | Python 3.11 detected | 2ms |

**LENS snapshot built:** 450ms total (pre-warm means only 81ms additional)

---

### T+500ms → T+850ms — TDDOrchestrator: RED Phase

Writes failing test first:

```python
# tests/test_validate_email.py
# AC_START: AC-IMPLEMENT-20260218-001
import pytest
from cortex.utils.validation import validate_email

def test_valid_email_returns_true():
    assert validate_email("user@example.com") is True

def test_missing_at_returns_false():
    assert validate_email("notanemail.com") is False

def test_double_at_returns_false():
    assert validate_email("a@@b.com") is False

def test_empty_string_returns_false():
    assert validate_email("") is False

def test_whitespace_returns_false():
    assert validate_email("user @example.com") is False
```

Test run: **5/5 FAILING** ✅ (RED confirmed)

---

### T+850ms → T+1000ms — TDDOrchestrator: GREEN Phase

Minimal implementation:

```python
# cortex/utils/validation.py
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_email(address: str) -> bool:
    """
    Validate a basic email address format.

    Args:
        address: The string to validate.

    Returns:
        True if address matches the expected email pattern, False otherwise.
    """
    return bool(_EMAIL_RE.match(address))
```

Test run: **5/5 PASSING** ✅ (GREEN confirmed)

---

### T+1000ms → T+1060ms — TDDOrchestrator: REFACTOR Phase

Checks for improvement opportunities:
- Naming: clear ✅
- Single responsibility: ✅
- Type hints: ✅
- Docstring: Google style ✅
- No duplication: ✅

No structural changes required. All 5 tests still pass.

```python
# AC_COMPLETE: AC-IMPLEMENT-20260218-001 ✅ 5/5 tests passing
```

---

### T+1060ms → T+1090ms — EnforcementOrchestrator

8-agent governance validation:

| Agent | Check | Result |
|-------|-------|--------|
| GovernanceEnforcementAgent | TDD followed, type hints, docstring | ✅ PASS |
| SecurityCheckpointAgent | No secrets, no unsafe patterns | ✅ PASS |
| ComplianceValidationAgent | Follows domain patterns | ✅ PASS |
| FileNamingEnforcementAgent | `validation.py` — correct location | ✅ PASS |
| IncrementalExecutionAgent | Deliverable size: 1 function — OK | ✅ PASS |
| MarkdownSuppressionAgent | No `.md` files created | ✅ PASS |
| ArchitectureIntegrityAgent | Utils module pattern consistent | ✅ PASS |
| EnvironmentIntegrityAgent | MCP server active | ✅ PASS |

**Verdict: ALL PASS**

---

### T+1090ms → T+1100ms — InteractionOrchestrator: Format & Return

Formats result as inline markdown (no files created — CORE-002):

```
██████████ 100%  Complete — 5/5 tests passing

| Metric        | Value                            |
|---------------|----------------------------------|
| Tests Added   | 5                                |
| Coverage      | 100% (new function)              |
| Risk Score    | 0.10 (PASS)                      |
| Elapsed       | 1.1s                             |
| Audit Marker  | AC-IMPLEMENT-20260218-001 ✅     |
```

MCP server serialises the response and VS Code renders it inline in chat.

---

## Summary Timeline

```
T+0ms     MCP Gateway receives request
T+18ms    Stage -1 rephrase complete
T+50ms    Intent classified (IMPLEMENT → TDD, confidence 0.97)
T+200ms   Holistic validation gate PASS (risk 0.10)
T+500ms   LENS snapshot built (8 analyzers)
T+850ms   RED phase — 5 failing tests written
T+1000ms  GREEN phase — implementation complete, 5/5 passing
T+1060ms  REFACTOR phase — no changes needed
T+1090ms  Governance validation — 8/8 agents PASS
T+1100ms  Response delivered inline
```

---

## Related Documents

- **[Orchestration Overview](./01-overview.md)** — Full orchestrator registry
- **[Master Orchestrator](./02-master-orchestrator.md)** — Coordination logic
- **[TDD Orchestrator](./04-tdd-orchestrator.md)** — RED/GREEN/REFACTOR detail
- **[Request Lifecycle Diagram](../07-diagrams/06-request-lifecycle.md)** — Visual version

---

*Last verified: 2026-02-18 | Source: cortex/orchestrators/ + cortex/__wiring_contract__.yaml*
