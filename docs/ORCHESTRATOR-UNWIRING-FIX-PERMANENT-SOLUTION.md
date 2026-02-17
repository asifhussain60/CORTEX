# Orchestrator Unwiring Fix - Permanent Solution

**AC-ID:** AC-PERMANENT-FIX-001, AC-PERMANENT-FIX-002, AC-PERMANENT-FIX-003, AC-PERMANENT-FIX-004  
**Authority:** CORTEX Architect  
**Status:** ✅ IMPLEMENTED  
**Last Updated:** 2026-02-17

## Executive Summary

This document describes the permanent solution to the orchestrator unwiring regression issue where `repo-registry.yaml` orchestrator wiring was being lost during git operations.

## Problem Statement

### Original Issue
Orchestrator wiring in `cortex_intelligence/memory/core/repo-registry.yaml` was periodically reset to an empty template state, causing system-wide failures. The registry contained critical wiring information for 18+ orchestrators that would be lost during regeneration.

### Root Cause
The `registry_template` flag was set to `true`, causing automated tooling to regenerate the registry file and wipe all orchestrator wiring data.

## Permanent Solution

### AC-PERMANENT-FIX-001: Registry Template Lock

**Implementation:**
```yaml
# cortex_intelligence/memory/core/repo-registry.yaml
metadata:
  version: 2.0
  status: PRODUCTION_WIRED
registry_template: false  # ← LOCKED (prevents regeneration)
```

**Enforcement:**
- `registry_template: false` prevents automatic regeneration
- Tests verify this flag remains false (test_fix_verification.py)
- Pre-commit hooks check registry integrity

### AC-PERMANENT-FIX-002: Verification Mechanisms

**Automated Verification Script:**
```python
# tests/unit/orchestrators/verify_registry.py

def verify_registry_template_locked() -> Tuple[bool, str]:
    """Verify registry_template is locked (false)."""
    # Returns (True, message) if locked, (False, message) if unlocked

def verify_orchestrator_wiring(min_wired: int = 18) -> Tuple[bool, str]:
    """Verify minimum orchestrators wired."""
    # Returns (True, message) if >= min_wired orchestrators are wired

def verify_wiring_status_section() -> Tuple[bool, str]:
    """Verify wiring_status metadata is accurate."""
    # Returns (True, message) if wiring stats are valid
```

**Test Suite:**
```python
# tests/unit/orchestrators/test_fix_verification.py

class TestACPermanentFix001:
    def test_registry_template_is_locked(self):
        """Regression test: registry_template must be false."""
        
    def test_minimum_orchestrators_wired(self):
        """Regression test: >= 18 orchestrators must be wired."""
        
    def test_full_wiring_status(self):
        """Regression test: wiring_status section valid."""
```

### AC-PERMANENT-FIX-003: Documentation

This document serves as the permanent solution documentation, covering:
- Problem statement and root cause
- Permanent solution implementation
- Verification mechanisms
- Recovery procedures
- Maintenance guidelines

### AC-PERMANENT-FIX-004: Registry Persistence

**File Location:**
```
cortex_intelligence/memory/core/repo-registry.yaml
```

**Status Validation:**
```yaml
metadata:
  status: PRODUCTION_WIRED  # Must be PRODUCTION_WIRED
registry_template: false    # Must be false
```

**Wiring Requirements:**
- Minimum 18 orchestrators wired
- Coverage >= 80%
- All core orchestrators active

## Verification Checklist

### Pre-Commit Verification
- [ ] `registry_template: false` in repo-registry.yaml
- [ ] Minimum 18 orchestrators with `wiring_status: "wired"`
- [ ] `metadata.status: PRODUCTION_WIRED`
- [ ] Test suite passes: `pytest tests/unit/orchestrators/test_fix_verification.py`

### CI/CD Pipeline Verification
- [ ] All AC-PERMANENT-FIX tests pass
- [ ] Registry integrity validated
- [ ] No regression detected

## Recovery Procedure

If orchestrator unwiring occurs despite these safeguards:

### Step 1: Verify Issue
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -c "from tests.unit.orchestrators.verify_registry import verify_all; print(verify_all())"
```

### Step 2: Check Git History
```bash
git log --follow -- cortex_intelligence/memory/core/repo-registry.yaml
git diff HEAD~1 cortex_intelligence/memory/core/repo-registry.yaml
```

### Step 3: Restore from Backup
```bash
# If registry_template was changed to true:
git checkout HEAD~1 -- cortex_intelligence/memory/core/repo-registry.yaml
```

### Step 4: Validate Restoration
```bash
pytest tests/unit/orchestrators/test_fix_verification.py -v
```

## Maintenance Guidelines

### Monthly Audit
1. Run verification script: `python3 tests/unit/orchestrators/verify_registry.py`
2. Check orchestrator coverage >= 80%
3. Verify test suite passes
4. Review git history for any unauthorized changes

### Adding New Orchestrators
1. Add orchestrator entry to `registered_orchestrators` list
2. Set `wiring_status: "wired"`
3. Update `wiring_status.total_orchestrators` count
4. Update `wiring_status.coverage_percentage`
5. Run verification: `pytest tests/unit/orchestrators/test_fix_verification.py`

### Preventing Regression
- **Never set** `registry_template: true`
- **Never regenerate** repo-registry.yaml automatically
- **Always use** `git mv` when moving the registry file
- **Always run** verification tests after changes

## Governance Compliance

- **CORE-002:** Test-driven approach (tests verify permanent fix)
- **CORE-008:** Tests before code (AC-PERMANENT-FIX-002)
- **CORE-035:** Single source of truth (repo-registry.yaml is authoritative)
- **CORE-042:** Registry consolidation (centralized in cortex_intelligence/memory/core/)

## Related Documentation

- Phase 20: Registry YAML Consolidation
- cortex-registry/planning/phase-20-registry-yaml-consolidation.yaml
- cortex-registry/core/governance/skull-rules.yaml (CORE rules)
- tests/unit/orchestrators/test_fix_verification.py

## Contact

For questions or issues related to this permanent fix:
- **Authority:** CORTEX Architect
- **Test Location:** `tests/unit/orchestrators/test_fix_verification.py`
- **Verification Script:** `tests/unit/orchestrators/verify_registry.py`

---

**Version History:**
- v1.0 (2026-01-24): Initial permanent solution implementation
- v1.1 (2026-02-17): Updated for Phase 20 registry consolidation
