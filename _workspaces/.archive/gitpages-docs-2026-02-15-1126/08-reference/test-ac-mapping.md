# Test-AC Mapping Reference

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Contributors, QA

## Overview

CORTEX tracks 257 unique Acceptance Criteria (AC) IDs across 409 test files. This document provides mapping between AC IDs and their corresponding test files.

## AC-ID Format

```
AC-{DOMAIN}-{NUMBER}

Domains:
- AR   : Architecture
- GOV  : Governance
- ORCH : Orchestration
- MCP  : MCP Protocol
- INT  : Integration
- INF  : Infrastructure
- SEC  : Security
- NFR  : Non-Functional Requirements
```

## Architecture ACs (AC-AR-*)

| AC-ID | Description | Test File(s) |
|-------|-------------|--------------|
| AC-AR-010-01 | Package design | `tests/test_ac_ar_010_01_design.py` |
| AC-AR-010-02 | Migration validation | `tests/test_ac_ar_010_02_migration.py` |
| AC-AR-010-03 | Import structure | `tests/test_ac_ar_010_03_imports.py` |

## Governance ACs (AC-GOV-*)

| AC-ID | Description | Test File(s) |
|-------|-------------|--------------|
| AC-GOV-001 | Context-aware rules | `tests/unit/governance/test_context_aware.py` |
| AC-GOV-002 | Tier precedence | `tests/unit/governance/test_tier_precedence.py` |
| AC-GOV-003 | Rule enforcement | `tests/unit/governance/test_enforcement.py` |

## Non-Functional ACs (AC-NFR-*)

| AC-ID | Description | Test File(s) |
|-------|-------------|--------------|
| AC-NFR-003-01 | Security hardening | `tests/test_ac_nfr_003_01_security_hardening.py` |
| AC-NFR-003-03 | Credential protection | `tests/test_ac_nfr_003_03_credential_protection.py` |

## Infrastructure ACs (AC-INF-*)

| AC-ID | Description | Test File(s) |
|-------|-------------|--------------|
| AC-INF-001 | Resilience foundation | `tests/unit/infrastructure/test_resilience.py` |
| AC-INF-002 | Circuit breaker | `tests/unit/infrastructure/test_circuit_breaker.py` |
| AC-INF-003 | Retry handler | `tests/unit/infrastructure/test_retry_handler.py` |

## E2E & Integration ACs

| AC-ID | Description | Test File(s) |
|-------|-------------|--------------|
| AC-E2E-001 | Smoke tests | `tests/e2e/smoke/test_smoke.py` |
| AC-CICD-001 | Pipeline validation | `tests/test_impl_cicd_validation.py` |
| AC-E2E-VAL | E2E validation | `tests/test_impl_e2e_validation.py` |

## Phase-to-AC Mapping

| Phase ID | AC IDs | Test Count |
|----------|--------|------------|
| impl-governance-001-context-aware | AC-GOV-001, AC-GOV-002 | 75 |
| impl-intelligence-001-routing | AC-INT-001 | 12 |
| impl-intelligence-002-duration | AC-INT-002 | 15 |
| impl-intelligence-003-errors | AC-INT-003 | 15 |
| impl-infra-001-resilience | AC-INF-001, AC-INF-002, AC-INF-003 | 126 |
| consolidation-001-src-cleanup | AC-AR-010-01, AC-AR-010-02, AC-AR-010-03 | 460 |

## Finding Tests by AC-ID

```powershell
# Find test files containing an AC-ID
Get-ChildItem -Path tests -Recurse -Filter "*.py" | 
    Select-String -Pattern "AC-GOV-001" | 
    Select-Object -Unique Path

# Run tests for specific AC
pytest tests/ -k "AC_GOV_001" -v

# Generate AC coverage report
pytest tests/ -v --collect-only | 
    Select-String -Pattern "AC-" | 
    ForEach-Object { $_.Line -match "AC-\w+-\d+" | Out-Null; $Matches[0] } | 
    Sort-Object -Unique
```

## Adding AC-ID to Tests

Include AC-ID in test docstrings:

```python
def test_governance_rule_blocks_large_response():
    """
    Verify CORE-001 blocks responses over 500 lines.
    
    AC-ID: AC-GOV-001
    Phase: impl-governance-001-context-aware
    
    Verifies:
    - Response > 500 lines is blocked
    - Appropriate error message returned
    - Audit trail created
    """
    context = {"lines": 600}
    result = validate_core_001(context)
    assert not result.is_valid
    assert result.violation == "CORE-001"
```

## Coverage Statistics

| Category | AC Count | Tests | Coverage |
|----------|----------|-------|----------|
| Architecture | 15 | 460 | 100% |
| Governance | 30 | 75 | 96% |
| Infrastructure | 25 | 126 | 100% |
| Intelligence | 20 | 42 | 100% |
| MCP | 14 | TBD | Stub |
| Security | 10 | 21 | 100% |
| Operations | 12 | 28 | 100% |
| **Total** | **257** | **1,081+** | **95%+** |

## Missing AC Coverage

ACs without tests (action required):

| AC-ID | Description | Priority |
|-------|-------------|----------|
| AC-MCP-001 through AC-MCP-014 | MCP tool implementations | P0 (after Phase B) |

## Related

- [Testing Strategy](../07-contributing/3-testing-strategy.md)
- [Test Pyramid Diagram](../_diagrams/test-pyramid.mmd)
- [Implementation Status](implementation-status.md)
