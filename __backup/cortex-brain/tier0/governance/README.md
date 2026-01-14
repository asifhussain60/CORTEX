# CORTEX 6.0 Governance System - Tier 0

**Status:** Active  
**Version:** 6.0.0  
**Created:** 2026-01-08

---

## Overview

This directory contains Tier 0 governance rules - the **CORE PROTECTION RULES (SKULL)** that define CORTEX's operational boundaries.

These rules are:
- **IMMUTABLE** - Cannot be modified at runtime
- **HIGHEST PRECEDENCE** - Override all other governance categories
- **MANDATORY** - Enforced strictly with audit logging

---

## Files

| File | Purpose | Rule Count |
|------|---------|------------|
| `core-rules.yaml` | 17 core SKULL rules (CORE-001 to CORE-017) | 17 |

---

## Rule Categories

1. **orchestration_lifecycle** - Rules governing orchestrator execution
2. **response_formatting** - Rules governing response structure
3. **portability** - Rules ensuring cross-platform compatibility
4. **development_workflow** - Rules governing development practices
5. **architecture_integrity** - Rules governing code structure
6. **quality_gates** - Rules governing code quality
7. **security_privacy** - Rules protecting data and systems

---

## Core Rules (CORE-001 to CORE-017)

| Rule ID | Name | Category | Severity |
|---------|------|----------|----------|
| CORE-001 | Incremental Autonomous Execution | orchestration_lifecycle | blocked |
| CORE-002 | No Summary File Generation | response_formatting | blocked |
| CORE-003 | Visual Progress Response Format | response_formatting | blocked |
| CORE-004 | No Continuation Bloat | response_formatting | blocked |
| CORE-005 | Path Portability | portability | blocked |
| CORE-006 | Setup Verification | orchestration_lifecycle | blocked |
| CORE-007 | Teardown Refactor | orchestration_lifecycle | blocked |
| CORE-008 | TDD Enforcement | development_workflow | blocked |
| CORE-009 | Plan File Organization | architecture_integrity | blocked |
| CORE-010 | Script Organization | architecture_integrity | blocked |
| CORE-011 | Python Type Hints | quality_gates | blocked |
| CORE-012 | Python Docstrings | quality_gates | blocked |
| CORE-013 | Python Error Handling | quality_gates | blocked |
| CORE-014 | SOLID Principles | architecture_integrity | blocked |
| CORE-015 | Python Import Organization | quality_gates | warning |
| CORE-016 | Python Code Formatting | quality_gates | warning |
| CORE-017 | Governance Enforcement | security_privacy | blocked |

---

## Migration History

**From:** `cortex-brain/brain-protection-rules.yaml` (v5.0)  
**To:** `cortex-brain/tier0/governance/core-rules.yaml` (v6.0)  
**Date:** 2026-01-08T00:30:00Z  
**Migrated By:** feat03-governance Phase 1

---

## Integration with 4-Category Governance

The Tier 0 rules are the foundation of the 4-category governance system:

```
Tier 0: CORTEX CORE (this directory)
  ↓ Highest precedence
Tier 1: BUSINESS_TIER_0 (Company compliance)
  ↓
Tier 2: COMPANY_PRACTICES (Engineering standards)
  ↓
Tier 3: KNOWLEDGE_PRACTICES (Learned patterns)
```

**Conflict Resolution:** Tier 0 always wins.

---

## Usage

Rules are loaded by `GovernanceMerger` and enforced by middleware:

```python
from src.orchestrators.core.governance_merger import GovernanceMerger

merger = GovernanceMerger()
unified_rules = merger.merge()  # Tier 0 rules included
```

---

## Audit Logging

All governance enforcement is logged to:
```
cortex-brain/audit-logs/governance-enforcement.jsonl
```

---

## Next Steps

- **Phase 2:** Implement GovernanceMerger (4-category integration)
- **Phase 3:** Add caching and performance optimization
- **Phase 4:** Integration testing with TODO Orchestrator
