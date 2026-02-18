# TDD Orchestrator

---
title: TDDOrchestrator — Test-Driven Implementation Engine
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-18
source_of_truth: cortex/orchestrators/core/tdd_orchestrator.py + cortex-registry/core/CORE-008.yaml
format: diátaxis-explanation
voice: third-person-blended
phase: Production (v8.1, Priority 55)
authority: CORE-008 (TDD Mandatory)
order: 4
---

> **Role:** The TDDOrchestrator is the primary implementation engine for all IMPLEMENT and FIX intents. It enforces the RED → GREEN → REFACTOR cycle without exception. No code is written before a failing test exists.

---

## Why TDD is Non-Negotiable

CORE-008 mandates test-first development for all IMPLEMENT and FIX operations. The rationale:

- **Correctness by construction** — Tests define the contract before implementation
- **Regression prevention** — Every change has a safety net from day one
- **Design pressure** — Testable code is inherently more modular
- **Audit traceability** — Each AC (Audit Commit) marker references test counts

There are **zero exceptions**. Override is not permitted. Governance blocks commits without tests.

---

## The RED → GREEN → REFACTOR Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    TDD CYCLE (CORE-008)                          │
│                                                                   │
│   ┌─────────┐    FAIL     ┌─────────┐    PASS    ┌───────────┐  │
│   │   RED   │ ──────────► │  GREEN  │ ──────────► │ REFACTOR  │  │
│   │         │             │         │             │           │  │
│   │ Write   │             │ Write   │             │ Improve   │  │
│   │ failing │             │ minimal │             │ structure │  │
│   │ test    │             │ code    │             │ all tests │  │
│   │         │             │         │             │ still pass│  │
│   └─────────┘             └─────────┘             └───────────┘  │
│        ▲                                                │         │
│        └────────────────────────────────────────────────┘        │
│                     Repeat per feature unit                       │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1 — RED (Write Failing Test)

The orchestrator:
1. Analyses the request using LENS context (existing patterns, function signatures, domain)
2. Generates a test that precisely defines the expected behaviour
3. Runs the test — it **must** fail (if it passes without implementation, test is invalid)
4. Records test count and file location in the audit log

```python
# Example RED phase output
def test_validate_email_rejects_missing_at_symbol():
    """Email without @ must return False."""
    assert validate_email("notanemail.com") is False
```

### Phase 2 — GREEN (Minimal Implementation)

The orchestrator writes the **minimum code** required to make the failing test pass:

- No premature optimization
- No extra features beyond what the test requires
- Type hints mandatory (CORE-008 enforcement)
- Docstring required at function level

```python
def validate_email(address: str) -> bool:
    """Return True if address contains exactly one @ symbol."""
    return address.count("@") == 1
```

Test runs — must pass. If it fails, the orchestrator debugs the implementation, not the test.

### Phase 3 — REFACTOR (Improve Without Breaking)

With a green test as a safety net:
1. Improve naming, structure, and readability
2. Apply SOLID principles (single responsibility, etc.)
3. Remove duplication
4. Run full test suite — all must still pass

```python
import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_email(address: str) -> bool:
    """
    Validate that an email address conforms to basic RFC format.

    Args:
        address: The email string to validate.

    Returns:
        True if address matches pattern, False otherwise.
    """
    return bool(_EMAIL_PATTERN.match(address))
```

---

## Handling Large Features

When a request cannot be delivered in one TDD cycle (estimated >500 LOC), the `IncrementalTaskDecomposer` (Priority 70) splits it into deliverable chunks:

```
Large feature request
        │
        ▼
IncrementalTaskDecomposer
        │
        ├── Chunk 1: Data model + tests    ← TDD cycle 1
        ├── Chunk 2: Validation logic      ← TDD cycle 2
        ├── Chunk 3: API endpoint          ← TDD cycle 3
        └── Chunk 4: Integration test      ← TDD cycle 4
```

Each chunk is independently deliverable and auditable.

---

## Audit Integration

Every TDD cycle creates audit markers:

```python
# AC_START: AC-IMPLEMENT-042
# Description: Email validation function — TDD cycle
# Tests: test_validate_email_*.py (5 tests)
...implementation...
# AC_COMPLETE: AC-IMPLEMENT-042 ✅ 5/5 tests passing
```

These markers link to `cortex_intelligence/governance.db` for full traceability.

---

## Performance Characteristics

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| RED phase (test generation) | 320ms | 450ms | 600ms |
| GREEN phase (implementation) | 380ms | 600ms | 900ms |
| REFACTOR phase | 150ms | 250ms | 400ms |
| Full cycle (small) | 850ms | 1200ms | 1800ms |
| Full cycle (large) | 2100ms | 2600ms | 3500ms |

---

## Common Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Test passes immediately (RED) | Test is not specific enough | Orchestrator rewrites test with tighter assertion |
| GREEN phase loops | Implementation does not converge | Decompose into smaller chunk |
| REFACTOR breaks tests | Refactoring changed behaviour | Revert refactoring, re-examine test |
| Governance block | Missing type hint / docstring | Auto-added by enforcement agent before commit |

---

## Related Documents

- **[Orchestration Overview](./01-overview.md)** — Where TDD fits in the full stack
- **[Master Orchestrator](./02-master-orchestrator.md)** — How TDD is invoked
- **[Governance & Compliance](../01-capabilities/07-governance-compliance.md)** — CORE-008 detail
- **[TDD Cycle Diagram](../07-diagrams/07-tdd-cycle.md)** — Visual sequence

---

*Last verified: 2026-02-18 | Authority: CORE-008 | Source: cortex/orchestrators/core/tdd_orchestrator.py*
