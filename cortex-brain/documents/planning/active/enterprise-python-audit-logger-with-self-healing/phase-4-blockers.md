# Phase 4 Blockers - Enterprise Audit Logger

**Date:** January 5, 2026  
**Plan:** A01-enterprise-audit-logger  
**Phase:** 4 - Security & Performance Hardening

---

## 🚨 Critical Blocker

### Issue: brain-protection-rules.yaml YAML Syntax Errors

**Impact:** HIGH - Blocks all orchestrator execution via `python3 -m src.main`

**Error:**
```
yaml.parser.ParserError: while parsing a block collection
  in "cortex-brain/brain-protection-rules.yaml", line 24, column 3
expected <block end>, but found '?'
  in "cortex-brain/brain-protection-rules.yaml", line 52, column 3
```

**Root Cause:**
- Multiple rule entries have inconsistent indentation
- Some rules use `- rule_id:` (no spaces) instead of `  - rule_id:` (2 spaces)
- All sub-keys (category, severity, name, etc.) need consistent indentation under each rule
- Complex nested structure with 10+ rules makes manual fixing error-prone

**Files Affected:**
- `cortex-brain/brain-protection-rules.yaml` (431 lines, 10+ rules)
- All orchestrators that depend on brain protector validation

**Attempted Fixes:**
1. ✅ Fixed first rule (SETUP_VERIFICATION) indentation
2. ⚠️ Used `sed` to fix rule_id indentation globally - still failing
3. ❌ Incremental fixes not working due to cascading indentation issues

---

## 🔧 Recommended Solution

### Option 1: Complete YAML Restructure (Recommended)
**Duration:** 2 hours  
**Approach:**
1. Create backup: `cp brain-protection-rules.yaml brain-protection-rules.yaml.backup-phase4`
2. Parse existing rules manually
3. Generate new YAML with correct structure:
   ```yaml
   rules:
     - rule_id: RULE_NAME
       category: category_name
       severity: level
       name: "Display Name"
       description: |
         Multi-line description
       enforcement:
         trigger: "event"
         action: "action"
       validation:
         - "Check 1"
         - "Check 2"
       examples:
         pass:
           - "Example 1"
         fail:
           - "Example 1"
   ```
4. Validate with `yamllint` and Python `yaml.safe_load()`
5. Test with orchestrators

### Option 2: Temporary Bypass (Quick Workaround)
**Duration:** 15 minutes  
**Approach:**
1. Modify `src/tier0/brain_protector.py` to skip YAML validation temporarily
2. Add try/catch with graceful degradation
3. Log warning instead of blocking
4. Proceed with Phase 4 implementation
5. Fix YAML in separate cleanup task

**Code Change:**
```python
# In brain_protector.py __init__
try:
    self.rules_config = self._load_rules()
except yaml.YAMLError as e:
    logger.warning(f"Brain protector rules YAML invalid, using defaults: {e}")
    self.rules_config = {
        "schema_version": "5.0",
        "rules": []  # Empty rules = permissive mode
    }
```

---

## 📋 Recommendation

**Use Option 2 (Temporary Bypass) NOW to unblock Phase 4, then schedule Option 1 as separate task.**

**Rationale:**
- Phase 4 has 10 hours of critical security/performance work
- YAML fix is infrastructure debt (not feature work)
- Bypass allows progress while documenting the issue properly
- Separate task ensures proper testing of YAML restructure

---

## 📝 Next Steps

1. **Immediate:** Implement Option 2 bypass
2. **Phase 4:** Proceed with TDD implementation
3. **Post-Phase 4:** Create separate task for brain-protection-rules.yaml restructure
4. **Testing:** Validate brain protector works with fixed YAML

---

**Status:** ⏸️ BLOCKED → Waiting for workaround approval
