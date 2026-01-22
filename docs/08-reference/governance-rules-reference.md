# Governance Rules Reference

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** All Contributors

## Overview

CORTEX enforces 29 CORE-* rules at Tier 0 (immutable). These rules cannot be overridden by higher tiers.

## Tier Structure

| Tier | Authority | Mutability | Location |
|------|-----------|------------|----------|
| **Tier 0** | Core rules (29) | Immutable | `cortex_brain/tier0/governance/` |
| **Tier 1** | Domain rules | Admin-mutable | `cortex_brain/tier1/` |
| **Tier 2** | Context rules | Session-mutable | `cortex_brain/tier2/` |
| **Tier 3** | Runtime rules | Dynamic | Domain Brain |

## Enforcement Levels

| Level | Description | Effect |
|-------|-------------|--------|
| **BLOCKED** | Hard stop | Operation fails immediately |
| **STRICT** | Enforced with warning | Operation proceeds, warning logged |
| **ADVISORY** | Logged only | Information captured for review |

## Core Rules (Tier 0)

### CORE-001: Response Size Limit

**Description:** Response must be < 500 lines  
**Enforcement:** BLOCKED  
**Rationale:** Prevents overwhelming context windows, ensures digestible outputs

```python
# Example: BLOCKED
def generate_response():
    return "\n".join(["line"] * 600)  # FAILS: 600 > 500

# Example: ALLOWED
def generate_response():
    return "\n".join(["line"] * 400)  # OK: 400 < 500
```

### CORE-005: No Hardcoded Paths

**Description:** Use `path_resolver` for all file paths  
**Enforcement:** BLOCKED  
**Rationale:** Ensures cross-platform compatibility

```python
# ❌ BLOCKED
file_path = "C:/Users/dev/cortex/config.yaml"

# ✅ ALLOWED
from cortex.core.path_resolver import resolve_path
file_path = resolve_path("config.yaml")
```

### CORE-008: TDD Requirement

**Description:** Tests must be written before implementation  
**Enforcement:** STRICT  
**Rationale:** Ensures test coverage, prevents untested code

```python
# ✅ Correct order:
# 1. Write test
def test_calculate_score():
    assert calculate_score(10, 20) == 30

# 2. Implement function
def calculate_score(a: int, b: int) -> int:
    return a + b
```

### CORE-011: Type Hints Required

**Description:** All functions must have type hints  
**Enforcement:** STRICT  
**Rationale:** Improves code clarity, enables static analysis

```python
# ❌ STRICT violation
def process(data):
    return data.upper()

# ✅ ALLOWED
def process(data: str) -> str:
    return data.upper()
```

### CORE-012: Docstrings Required

**Description:** Google-style docstrings on all functions  
**Enforcement:** STRICT  
**Rationale:** Ensures documentation, aids understanding

```python
# ❌ STRICT violation
def calculate(a, b):
    return a + b

# ✅ ALLOWED
def calculate(a: int, b: int) -> int:
    """
    Calculate sum of two integers.
    
    Args:
        a: First integer.
        b: Second integer.
    
    Returns:
        Sum of a and b.
    """
    return a + b
```

### CORE-013: No Bare Except

**Description:** Catch specific exceptions only  
**Enforcement:** STRICT  
**Rationale:** Prevents swallowing unexpected errors

```python
# ❌ STRICT violation
try:
    risky_operation()
except:
    pass

# ✅ ALLOWED
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
except Exception as e:
    logger.error(f"Unexpected: {e}")
    raise
```

### CORE-026: Git Checkpoints

**Description:** Commit after each meaningful change  
**Enforcement:** ADVISORY  
**Rationale:** Enables rollback, preserves history

### CORE-027: Audit Trail

**Description:** All operations must be logged  
**Enforcement:** STRICT  
**Rationale:** Compliance, debugging, accountability

```python
# ✅ ALLOWED
from cortex.infrastructure.audit_logger import log_operation

@log_operation(ac_id="AC-GOV-001")
def execute_governance_check(context: Dict) -> Result:
    # Operation automatically logged
    pass
```

### CORE-028: File Naming Convention

**Description:** Kebab-case, ≤25 characters  
**Enforcement:** STRICT  
**Rationale:** Consistency, cross-platform compatibility

```
✅ governance-rule.py
✅ mcp-server.py
❌ GovernanceRule.py      # PascalCase
❌ governance_rule.py     # snake_case
❌ this-is-way-too-long-filename.py  # > 25 chars
```

### CORE-029: Response Header

**Description:** All responses must include standard header  
**Enforcement:** BLOCKED  
**Rationale:** Consistency, traceability

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
```

## Quick Reference Table

| Rule | Description | Enforcement |
|------|-------------|-------------|
| CORE-001 | Response < 500 lines | BLOCKED |
| CORE-005 | No hardcoded paths | BLOCKED |
| CORE-008 | TDD (tests first) | STRICT |
| CORE-011 | Type hints required | STRICT |
| CORE-012 | Docstrings (Google) | STRICT |
| CORE-013 | No bare except | STRICT |
| CORE-026 | Git checkpoints | ADVISORY |
| CORE-027 | Audit trail | STRICT |
| CORE-028 | Kebab-case ≤25 | STRICT |
| CORE-029 | Response header | BLOCKED |

## Rule Loading

Rules are loaded from YAML:

```python
from cortex_brain.tier0.governance import load_rules

rules = load_rules()
# Returns list of 29 GovernanceRule objects
```

## Validation API

```python
from cortex.core.governance_enforcer import validate

result = validate(
    rule_id="CORE-001",
    context={"lines": 600}
)

if not result.is_valid:
    print(f"Violation: {result.violation}")
    print(f"Enforcement: {result.enforcement}")
```

## Related

- [Governance Tiers Diagram](../_diagrams/governance-tiers.mmd)
- [ADR-002: Tier Precedence](../02-architecture/adrs/adr-002-tier-precedence.md)
- [Code Style Guide](../07-contributing/4-code-style-guide.md)
