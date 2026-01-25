# 🚀 CORTEX Zero-Duplication Quick Reference
**Use before EVERY implementation to ensure CORE-035 compliance**

---

## ⚡ 60-Second Check (DO THIS FIRST)

```bash
# 1. Check if your class/function exists
python scripts/duplication_audit.py

# 2. Look for your name in the output
# Found it? → Use consolidation pattern ✅
# Not found? → Safe to create new implementation ✅
```

## 🔍 3 Questions Before You Code

```
1. Does my class/function already exist in cortex/ or cortex_brain/?
   → Check: grep -r "class MyClass\|def my_function" cortex/ --include="*.py"
   → If YES: Go to step 2
   → If NO: Safe to create new (skip to implementation)

2. Are there multiple implementations?
   → If YES (2+ locations): Must use CONS-pattern consolidation
   → If NO (1 location): Can import and reuse from canonical location

3. Is it an intentional duplicate? (main(), test classes, script utilities)
   → If YES: Document with TODO comment explaining why
   → If NO: MUST consolidate using CONS-pattern
```

---

## ✅ CONS-Pattern Template (Copy-Paste Ready)

```python
# File: cortex/core/enums.py (or cortex/core/data_classes.py)
# Priority: HIGH - This is your canonical location

from enum import Enum

class UnifiedMyComponent(Enum):
    """CORE-035: Single canonical implementation.
    
    Consolidates 3 implementations:
    - cortex/core/safety/my_component.py (original)
    - cortex/devx/my_component.py (variant A)
    - cortex/brain/devx/my_component.py (variant B)
    
    Backward compatible via aliases:
    - Old imports still work: from cortex.devx import MyComponent
    - All code continues to function (100% backward compatible)
    
    AC-ID: AC-CONSOLIDATION-XXX (track in git commit)
    """
    
    VALUE_1 = "value_1"
    VALUE_2 = "value_2"
    VALUE_3 = "value_3"

# CRITICAL: Backward compatibility aliases
# These MUST be present - do not delete!
# Old code that does: from cortex.devx import MyComponent still works
MyComponent = UnifiedMyComponent  # cortex.devx.MyComponent users
_MyComponent = UnifiedMyComponent  # cortex.devx._MyComponent users
```

**Then in the old files:**
```python
# In cortex/devx/my_component.py (old location)
# Replace the class definition with this import:

from cortex.core.enums import UnifiedMyComponent as MyComponent

# Old code that does: from cortex.devx import MyComponent
# will still work because of the import above
```

---

## 🎯 High-Priority Consolidation Targets

| Target | Violations | Effort | Value | Status |
|--------|-----------|--------|-------|--------|
| ValidationSeverity | 5 | 4h | 85% | 📋 PLANNED |
| SeverityLevel | 4 | 3h | 85% | 📋 PLANNED |
| MetricType | 4 | 3h | 85% | 📋 PLANNED |
| ResponseFormat | 4 | 3h | 85% | 📋 PLANNED |
| Result | 2 | 4h | 85% | 📋 PLANNED |

---

## 🧪 Minimum Test Coverage Required

```python
import pytest
from cortex.core.enums import UnifiedMyComponent

def test_unified_my_component_backward_compatibility():
    """REQUIRED: Verify all old imports still work."""
    from cortex.devx.my_component import MyComponent as OldImport1
    from cortex.brain.devx.my_component import MyComponent as OldImport2
    
    # All should be the same object
    assert OldImport1 is UnifiedMyComponent
    assert OldImport2 is UnifiedMyComponent
    
    # All values accessible from all imports
    assert OldImport1.VALUE_1 == UnifiedMyComponent.VALUE_1
    assert OldImport2.VALUE_2 == UnifiedMyComponent.VALUE_2

def test_unified_my_component_composition():
    """REQUIRED: Verify composition pattern delegates correctly."""
    comp = UnifiedMyComponent.VALUE_1
    assert comp.value == "value_1"
    assert comp.name == "VALUE_1"
```

---

## 📝 Git Commit Template

```bash
git commit -m "AC-CONSOLIDATION-XXX: Consolidate MyComponent (5→1)

Consolidates 5 implementations into single canonical location:
- cortex/core/safety/my_component.py:18
- cortex/devx/my_component.py:25
- cortex/brain/devx/my_component.py:15
- cortex/domain_orchestrators/my_component.py:12
- cortex/brain/domain_orchestrators/my_component.py:20

Consolidation pattern applied (CONS-003):
✅ Single entry point: UnifiedMyComponent
✅ 100% backward compatible (old imports still work)
✅ Composition-based delegation
✅ Zero breaking changes

Tests:
✅ test_backward_compatibility: PASS (all 5 variants accessible)
✅ test_composition_pattern: PASS (values routing works)
✅ test_zero_breaking_changes: PASS (existing tests unchanged)

CONS-Pattern Evidence:
- Consolidated 5 implementations into 1
- Maintained 100% backward compatibility via aliases
- Achieved 85% consolidation value (from CONS-003-009 baseline)
- CORE-035 compliant: Single canonical implementation

AC_START: 2026-01-25T09:19:41
AC_EXECUTE: implementation + testing
AC_COMPLETE: 2026-01-XX"
```

---

## 🚨 DO NOT DO

❌ Create duplicate implementations  
❌ Leave TODOs without consolidation plan  
❌ Delete backward-compatibility aliases  
❌ Skip tests for consolidation patterns  
❌ Forget to log AC_ID tracking  

---

## ✅ DO THIS

✅ Check duplication audit first  
✅ Use CONS-pattern template  
✅ Maintain 100% backward compatibility  
✅ Add comprehensive tests  
✅ Document AC-ID in git commit  
✅ Update core-rules.yaml progress  

---

## 🎓 Learn from Proven Patterns

These consolidations already worked in CORTEX:

- **CONS-002:** Master Orchestrator (4 stages → 1) - 82% token savings
- **CONS-003:** Intent Routing (3 → 1) - 85% value, 100% compat
- **CONS-004:** Registry (5 → 1) - 85% value, proven pattern
- **CONS-005-009:** Additional consolidations - all 100% backward compatible

**Key Learning:** The CONS-pattern works! Just apply it consistently.

---

## 📞 Need Help?

1. **Check duplication:** `python scripts/duplication_audit.py`
2. **Read strategy:** `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/reports/ZERO-DUPLICATION-IMPLEMENTATION-STRATEGY.md`
3. **Review CONS-pattern:** `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/phases/transform-002-consolidation.yaml`
4. **Check governance:** `grep -A5 "CORE-035" cortex_brain/tier0/governance/core-rules.yaml`

---

**Status:** 239 violations remaining | **Next Target:** ValidationSeverity (5→1)

**Remember:** Zero duplication = Production ready! 🚀
