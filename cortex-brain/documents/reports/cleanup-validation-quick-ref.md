# Cleanup Validation Quick Reference

**Version:** 3.4.0  
**Date:** November 26, 2025

---

## What Is Cleanup Validation?

Cleanup validation automatically checks if proposed cleanup operations would break CORTEX functionality **before** executing any changes.

---

## How It Works

### **Phase 1: Dry-Run Validation (Automatic)**
When you run `cleanup cortex`, validation happens automatically:

1. **Import Dependencies** - Checks if any code imports files marked for deletion
2. **Critical Files** - Ensures protected files (src/, tests/, configs) aren't deleted
3. **Test Discovery** - Validates pytest can still find all tests
4. **Entry Points** - Ensures main.py and cortex_entry.py remain functional

**Time:** <30 seconds  
**Result:** PASS (cleanup proceeds) or FAIL (cleanup blocked)

### **Phase 2: Post-Execution Verification (Automatic)**
After cleanup executes (if you approve):

1. **Import Validation** - Tests all critical module imports work
2. **Test Discovery** - Runs pytest --collect-only
3. **Health Check** - Quick system health validation
4. **Smoke Tests** - Runs critical Tier 0/1/2 tests

**Time:** <35 seconds  
**Result:** PASS (success) or WARNING (manual review recommended)

---

## What It Prevents

Based on Chat003.md (45-minute debugging session), validation prevents:

1. **Import Path Errors** (15 min debug)
   - Files deleted that other modules import
   - Automatic detection with detailed importer list

2. **Attribute Naming Issues** (embedded in import fixes)
   - Post-cleanup verification catches broken imports immediately
   - Automatic warning triggers manual review

3. **Unicode Encoding Errors** (10 min debug)
   - Smoke tests catch encoding issues
   - Verification warns before you commit changes

---

## Usage

### **Standard Cleanup (Validation Enabled)**
```
User: "cleanup cortex"

CORTEX will:
1. Scan repository
2. Generate cleanup manifest
3. Generate report
4. **RUN VALIDATION** ← NEW
5. Show summary

If validation passes:
  → You can approve cleanup
  
If validation fails:
  → Cleanup BLOCKED
  → Review validation report
  → Fix issues before retrying
```

### **View Validation Report**
If cleanup is blocked, check the validation report:

```
Location: cortex-brain/documents/reports/cleanup-validation-YYYYMMDD-HHMMSS.md

Contents:
- Critical issues detected
- Affected files
- Importer details (for import errors)
- Remediation instructions
```

---

## Common Scenarios

### **✅ Scenario 1: Validation Passes**
```
Phase 4: Dry-Run Validation
  1. Validating import dependencies...
  2. Checking critical file protection...
  3. Validating test discovery...
  4. Validating entry points...
✅ Validation passed in 18.42s
   Cleanup is safe to execute

To execute cleanup, say: 'approve cleanup'
```

**Action:** Approve cleanup with confidence

---

### **❌ Scenario 2: Import Dependency Error**
```
❌ VALIDATION FAILED

Critical Issues:
  • File imported by 3 modules
    File: src/operations/legacy_cleanup.py
    importers:
      - file: src/main.py, line: 45
      - file: src/operations/cleanup_entry.py, line: 12
      - file: tests/test_cleanup.py, line: 8

⚠️  Cleanup BLOCKED to protect CORTEX functionality
```

**Action:**
1. Update imports in main.py, cleanup_entry.py, test_cleanup.py
2. OR remove legacy_cleanup.py from cleanup manifest
3. Re-run cleanup after fixes

---

### **❌ Scenario 3: Critical File Protection**
```
❌ VALIDATION FAILED

Critical Issues:
  • File is critical to CORTEX operation
    File: src/tier1/working_memory.py
    reason: File is in protected directory or import chain

⚠️  Cleanup BLOCKED to protect CORTEX functionality
```

**Action:**
1. DO NOT delete files in src/, tests/, cortex-brain/tier*/
2. Remove file from cleanup manifest
3. These directories are protected for CORTEX stability

---

### **⚠️ Scenario 4: Post-Cleanup Warning**
```
Cleanup executed: 35 deleted, 12 renamed, 47.23 MB freed

POST-CLEANUP VERIFICATION
❌ Import validation failed
   Some CORTEX functionality may be compromised
   Manual review recommended
```

**Action:**
1. Check verification report in output
2. Test CORTEX functionality manually
3. If issues found, restore from git history
4. Report issue to improve validation logic

---

## Protected Elements

Validation automatically protects:

### **Directories**
- `src/` - All CORTEX source code
- `tests/` - All test files
- `cortex-brain/tier0/` - Governance rules
- `cortex-brain/tier1/` - Working memory database
- `cortex-brain/tier2/` - Knowledge graph
- `cortex-brain/tier3/` - Development context
- `.git/` - Git repository
- `.github/prompts/` - CORTEX prompts

### **Files**
- `cortex.config.json` - Configuration
- `VERSION` - Version tracking
- `requirements.txt` - Dependencies
- `pytest.ini` - Test configuration
- `cortex-brain/response-templates.yaml` - Response templates
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules

### **Entry Points**
- `src/main.py` - Main entry point
- `src/entry_point/cortex_entry.py` - CORTEX entry
- `src/cortex_agents/intent_router.py` - Intent router

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Import dependency check | <5s | Checks all Python imports |
| Critical file protection | <3s | Verifies protected paths |
| Test discovery | <10s | Runs pytest --collect-only |
| Entry point validation | <2s | Tests critical imports |
| **Total validation** | **<30s** | Dry-run phase |
| Post-cleanup verification | <35s | After execution |

**Compare to:**
- Manual debugging (Chat003.md): **45 minutes**
- Time saved: **44 minutes 30 seconds** (98.9% reduction)

---

## Troubleshooting

### **Q: Validation blocks cleanup but I know it's safe**
**A:** Validation is conservative. Options:
1. Review validation report - may reveal real issues
2. Update imports/references before cleanup
3. Remove problematic files from cleanup manifest
4. If absolutely necessary: Skip validation (not recommended)

### **Q: How do I skip validation?**
**A:** Not currently exposed in user interface. Validation is designed to always protect CORTEX. If you need to bypass, contact CORTEX development team.

### **Q: Validation says file is imported but I can't find the import**
**A:** Check validation report for:
- Exact file and line number of import
- May be indirect import (A imports B, B imports C)
- Use "Find in Files" for module name

### **Q: Post-cleanup verification warns but everything seems fine**
**A:** Verification is cautious. If manual testing confirms CORTEX works:
1. File issue report to improve verification logic
2. Continue using CORTEX normally
3. Future validation will be improved based on feedback

---

## Benefits

1. **Zero Manual Debugging** - Validation catches issues automatically
2. **Fast Feedback** - <30s validation vs 45 min debugging
3. **Clear Error Messages** - Detailed reports with remediation steps
4. **Confidence** - Approve cleanups knowing they won't break CORTEX
5. **Auditable** - All validation reports saved with timestamps

---

## Related Documentation

- **Implementation Guide:** `cortex-brain/documents/implementation-guides/cleanup-validation-implementation.md`
- **Analysis Document:** `cortex-brain/documents/analysis/cleanup-efficiency-analysis.md`
- **Completion Report:** `cortex-brain/documents/reports/cleanup-validation-complete.md`
- **Chat003.md:** Historical record of 45-min debugging session that motivated this feature

---

**Questions?** Say "help cleanup validation" or review the implementation guide.

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
