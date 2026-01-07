# Deprecated Governance Engine - Archive

**Date Archived:** December 31, 2025  
**Reason:** Duplicate governance system replaced by BrainProtector

---

## Summary

This archive contains the obsolete GovernanceEngine implementations that were replaced by the production-ready BrainProtector system.

### Files Archived

1. **governance_engine.py** (from `src/tier0/`)
   - Original GovernanceEngine with 29 rules
   - Loaded from `governance.yaml`
   - **Status:** Never instantiated in codebase (0 active usage)
   - **Test Coverage:** 0%

2. **governance.yaml** (from `src/tier0/`)
   - 29 legacy rules: TDD, DoD, DoR, SOLID, Brain Protection
   - Version 3.0, marked "In progress - Phase 0"
   - **Status:** Significant overlap with brain-protection-rules.yaml

3. **governance_brain_tier0.py** (from `src/brain/tier0/`)
   - Alternative GovernanceEngine for CORTEX 4.0
   - Expected `~/.cortex/shared/skull_rules.yaml` (file never existed)
   - **Status:** Broken dependency, never functional

---

## Why Deprecated?

### 1. **Zero Active Usage**
- `grep` search found NO instantiation of GovernanceEngine
- Only 2 legacy imports in deprecated `src/brain/` modules
- BrainProtector handles all governance needs

### 2. **Duplicate Rules**
All 29 GovernanceEngine rules already exist in BrainProtector:
- ✅ TDD_ENFORCEMENT → BrainProtector SKULL rules
- ✅ DoD/DoR → brain-protection-rules.yaml
- ✅ SOLID Principles → BrainProtector compliance layer
- ✅ Brain Protection → Core BrainProtector functionality

### 3. **No Test Coverage**
- GovernanceEngine: **0 tests**
- BrainProtector: **404 tests (100% coverage)**

### 4. **Broken Architecture**
- `governance_brain_tier0.py` expected `skull_rules.yaml` that never existed
- BrainInterface.tier0 was wired to broken implementation
- Legacy system never completed Phase 0

---

## Replacement System

**BrainProtector** (Production System):
- **Location:** `src/tier0/brain_protector.py`
- **Rules:** `cortex-brain/brain-protection-rules.yaml` (6,779 lines, 63 rules)
- **Test Coverage:** 100% (404 tests passing)
- **Wiring:** 
  - Entry Point: `CortexEntry.brain_protector` (line 240)
  - Brain Interface: `BrainInterface.tier0` → BrainProtector (as of Dec 31, 2025)
- **Active Usage:** All orchestrators use BrainProtector via entry point

---

## Migration Notes

### Code Changes (Dec 31, 2025)

1. **BrainInterface.tier0** (src/brain/interface.py)
   ```python
   # BEFORE (broken)
   from .tier0.governance import GovernanceEngine
   rules_path = self.config.shared_root / "skull_rules.yaml"  # doesn't exist
   self._tier0 = GovernanceEngine(rules_path)
   
   # AFTER (working)
   from src.tier0.brain_protector import BrainProtector
   self._tier0 = BrainProtector(brain_root=self.workspace_root / "cortex-brain")
   ```

2. **Removed Imports** (src/brain/__init__.py)
   - Removed: `from .tier0.governance import GovernanceEngine`
   - Removed: `"GovernanceEngine"` from `__all__`
   - Added note: Tier 0 uses BrainProtector

3. **Archived Files**
   - `src/tier0/governance_engine.py` → archived
   - `src/tier0/governance.yaml` → archived
   - `src/brain/tier0/governance.py` → archived as `governance_brain_tier0.py`

---

## Rule Coverage Verification

All 29 legacy rules covered by BrainProtector:

| GovernanceEngine Rule | BrainProtector Coverage |
|-----------------------|-------------------------|
| TDD_ENFORCEMENT | ✅ SKULL rules (tests 1-63) |
| RED_PHASE_VALIDATION | ✅ RED_PHASE_VALIDATION rule |
| HOLISTIC_CODE_DISCOVERY | ✅ HOLISTIC_CODE_DISCOVERY_ENFORCEMENT |
| DoD Criteria | ✅ DEFINITION_OF_DONE |
| DoR Criteria | ✅ DEFINITION_OF_READY |
| SOLID Principles | ✅ SOLID_SRP, SOLID_DIP, etc. |
| Brain Protection | ✅ Core BrainProtector functionality |
| Tier Boundaries | ✅ Tier boundary protection layer |
| Git Isolation | ✅ GIT_ISOLATION_ENFORCEMENT |
| File Organization | ✅ FILE_ORGANIZATION_ENFORCEMENT |

**Result:** No unique rules lost, all functionality preserved.

---

## References

- **Analysis Document:** `.asif/backlog/skull-refactor.md`
- **BrainProtector Tests:** `tests/tier0/test_brain_protector_*.py`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`

---

## Historical Context

**GovernanceEngine Evolution:**
1. **Phase 0** (2025 Q3): Initial governance.yaml created (29 rules)
2. **Phase 1** (2025 Q4): BrainProtector implemented with YAML config
3. **Milestone 0** (Dec 2025): BrainProtector reached 100% test coverage
4. **Dec 31, 2025**: GovernanceEngine deprecated, BrainProtector sole system

**Decision:** Consolidate to single, tested, production-ready governance system.

---

**Archive Status:** ✅ Complete  
**Safe to Delete:** After 2026 Q2 (6 month retention period)
