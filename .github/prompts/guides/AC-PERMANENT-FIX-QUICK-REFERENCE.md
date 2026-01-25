# AC-PERMANENT-FIX Quick Reference Card

**Efficient Identify-and-Fix Pattern for CORTEX Permanent Fixes**

---

## 🚀 Quick Start (30 seconds)

```python
from cortex.tools.total_recall_agent import TotalRecallAgent

agent = TotalRecallAgent()

# Option 1: Check status explicitly
status = agent.check_ac_permanent_fixes()
print(status)

# Option 2: Automatic verification on recall (default)
result = agent.recall("orchestrator", verify_ac_permanent_fixes=True)

# Option 3: Get formatted report
from cortex.tools.total_recall_agent import ACPermanentFixEnforcer
report = ACPermanentFixEnforcer.get_ac_permanent_fix_report()
print(report)
```

---

## 📋 4 Active Permanent Fixes

| Fix ID | Issue | Status | Critical |
|--------|-------|--------|----------|
| **AC-PERMANENT-FIX-001** | Registry auto-regenerating, losing wiring | ✅ LOCKED | 🔴 YES |
| **AC-PERMANENT-FIX-002** | No regression detection mechanism | ✅ TESTS | 🔴 YES |
| **AC-PERMANENT-FIX-003** | No deployment readiness statement | ✅ DOCUMENTED | 🟡 NO |
| **AC-PERMANENT-FIX-004** | Registry persistence not verified | ✅ VERIFIED | 🔴 YES |

---

## 🔍 Verify Fix Status

### AC-PERMANENT-FIX-001 (Registry Wiring)
```bash
# Check registry is locked
grep "registry_template: false" cortex_brain/tier0/repo-registry.yaml

# Count wired orchestrators (expect 18+)
grep -c "wiring_status: \"wired\"" cortex_brain/tier0/repo-registry.yaml
```

### AC-PERMANENT-FIX-002 (Verification)
```bash
# Verify test files exist
ls tests/unit/orchestrators/verify_registry.py
ls tests/unit/orchestrators/test_fix_verification.py

# Run tests
pytest tests/unit/orchestrators/test_fix_verification.py -v
```

### AC-PERMANENT-FIX-003 (Documentation)
```bash
# Check documentation
grep -i "ready for deployment" docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md
```

### AC-PERMANENT-FIX-004 (Persistence)
```bash
# Run persistence tests
pytest tests/unit/orchestrators/test_fix_verification.py::test_registry_persistence -v
```

---

## ⚙️ Verification Algorithm

```
1. IDENTIFY (Git History)
   → git log --grep="AC-PERMANENT-FIX"

2. VERIFY (File State)
   → Check each fix using verification methods

3. DETECT REGRESSION
   → If critical fix reverted: BLOCK EXECUTION
   → If non-critical fix reverted: WARN ONLY

4. REPORT (Status)
   → Generate markdown status report
```

---

## 🛑 If a Fix is Reverted

### Critical Fixes (AC-PERMANENT-FIX-001, 002, 004)
```
❌ EXECUTION BLOCKED
RuntimeError: AC-PERMANENT-FIX-001 reverted!
```
**Action:** Restore the fix immediately or create new AC-PERMANENT-FIX explaining the change.

### Non-Critical Fixes (AC-PERMANENT-FIX-003)
```
⚠️  WARNING LOGGED
AC-PERMANENT-FIX-003 reverted (documentation issue)
```
**Action:** Non-blocking, but should restore documentation.

---

## 📊 Implementation Details

**Classes:**
- `ACPermanentFixEnforcer` - Core verification system
- `TotalRecallAgent` - Enhanced with AC-PERMANENT-FIX support

**Methods:**
- `check_ac_permanent_fixes()` → Dict with status for each fix
- `verify_all_fixes()` → Verify all 4 fixes simultaneously
- `get_ac_permanent_fix_report()` → Formatted markdown report

**Files Modified:**
- `cortex/tools/total_recall_agent.py` (+430 lines)
- `.github/prompts/cortex-total-recall.prompt.md` (+118 lines)

**Documentation:**
- `.github/prompts/AC-PERMANENT-FIX-ENFORCEMENT.md` (351 lines)
- `.github/prompts/AC-PERMANENT-FIX-IMPLEMENTATION-SUMMARY.md` (detailed guide)

---

## 🎯 Usage Patterns

### Pattern 1: Explicit Status Check
```python
agent = TotalRecallAgent()
status = agent.check_ac_permanent_fixes()

for fix_id, result in status.items():
    if result["critical"] and not result["valid"]:
        print(f"CRITICAL: {fix_id} failed!")
        sys.exit(1)
```

### Pattern 2: Automatic Verification
```python
# Verifies on every recall (default behavior)
result = agent.recall("feature_name")

# Or explicitly enable:
result = agent.recall("feature", verify_ac_permanent_fixes=True)
```

### Pattern 3: Manual Verification
```python
from cortex.tools.total_recall_agent import ACPermanentFixEnforcer

fixes = ACPermanentFixEnforcer.verify_all_fixes()

# Generate report
report = ACPermanentFixEnforcer.get_ac_permanent_fix_report()
print(report)
```

---

## 🚨 Common Issues & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| "AC-PERMANENT-FIX-001 reverted!" | `registry_template` value | Set to `false` in repo-registry.yaml |
| Test files not found | File existence | Create verify_registry.py and test_fix_verification.py |
| Orchestrators not wired | Count wired orchestrators | Ensure 18+ orchestrators have `wiring_status: "wired"` |
| Registry doesn't persist | Unit test results | Run registry persistence tests |

---

## 📚 Full Documentation

**Comprehensive Guides:**
- **AC-PERMANENT-FIX-ENFORCEMENT.md** - Complete specification and usage guide
- **AC-PERMANENT-FIX-IMPLEMENTATION-SUMMARY.md** - Implementation details and roadmap
- **cortex-total-recall.prompt.md** (v5.0) - Full prompt specification

---

## ✅ Checklist for Developers

- [ ] Reviewed AC-PERMANENT-FIX registry (4 fixes)
- [ ] Understand verification algorithm (4 steps)
- [ ] Know how to check fix status (3 methods)
- [ ] Know what to do if fix reverts (block/warn)
- [ ] Familiar with agent integration (`check_ac_permanent_fixes()`)
- [ ] Read efficiency improvements (identify-and-fix pattern)

---

**Status:** ✅ PRODUCTION READY  
**Version:** 5.0 (cortex-total-recall.prompt.md)  
**Last Updated:** 2026-01-24 14:28 UTC
