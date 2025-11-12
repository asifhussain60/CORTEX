# Document Refresh Plugin - File Creation Prohibition Update

**Date:** November 9, 2025  
**Type:** Critical Bug Fix  
**Severity:** HIGH  
**Status:** ✅ COMPLETE

---

## 📋 Summary

Updated the document refresh plugin to enforce absolute prohibition on creating new files. This addresses a critical violation where CORTEX created `Awakening Of CORTEX - Quick Read.md` instead of updating the existing `Awakening Of CORTEX.md`.

---

## 🔴 Problem Identified

**MAJOR VIOLATION:**
- Document refresh plugin created a new file: `Awakening Of CORTEX - Quick Read.md`
- This violates the fundamental principle: **ONLY UPDATE, NEVER CREATE**

**Why This Matters:**
- Documentation fragmentation (multiple versions of truth)
- Maintenance complexity (which file is canonical?)
- Version drift (files become inconsistent)
- User confusion (which document to read?)

---

## ✅ Solution Implemented

### 1. File Existence Validation

**Two-level enforcement:**

**Level 1: `_refresh_all_docs()` method**
```python
if self.config.get("enforce_no_file_creation", True):
    if not file_path.exists():
        error_msg = (
            f"PROHIBITED: File '{filename}' does not exist. "
            f"Doc refresh plugin NEVER creates new files."
        )
        results["errors"].append(error_msg)
        results["success"] = False
        continue
```

**Level 2: `_refresh_story_doc()` method**
```python
if not file_path.exists():
    return {
        "success": False,
        "error": "CRITICAL VIOLATION: File does not exist. ..."
    }
```

### 2. Read Time Enforcement

**New functionality:**
- Calculates estimated read time (225 words/minute)
- Validates against target (60 min for full story)
- Acceptable range: ±10%
- Recommends TRIMMING if too long (not creating Quick Read)

**Implementation:**
```python
def _validate_read_time(self, content: str, target_minutes: int):
    words = len(content.split())
    estimated_minutes = words / 225  # words per minute
    
    # Check if within ±10% of target
    within_target = (target * 0.9) <= estimated <= (target * 1.1)
    
    if too_long:
        return "TRIM content. DO NOT create Quick Read variant."
```

### 3. Configuration Schema Updates

**New config options:**
```python
{
    "enforce_no_file_creation": {
        "default": True,  # ALWAYS True
        "description": "CRITICAL: Fail if attempting to create new files"
    },
    "enforce_read_time_limits": {
        "default": True,
        "description": "Enforce target read times"
    },
    "awakening_story_target_minutes": {
        "default": 60,
        "minimum": 15,
        "maximum": 75
    },
    "trim_content_on_exceed": {
        "default": True,
        "description": "Trim content if exceeds (not create new file)"
    }
}
```

### 4. Documentation Updates

**Updated module docstring:**
```python
"""
CRITICAL RULES (ABSOLUTE PROHIBITIONS):
1. **NEVER CREATE NEW FILES** - Only update existing documentation
2. **FORBIDDEN:** Creating Quick Read, Summary, or variant versions
3. **FORBIDDEN:** Creating new files in docs/story/CORTEX-STORY/
4. If file doesn't exist, FAIL with error
5. If content exceeds target length, TRIM existing file

READ TIME ENFORCEMENT:
- "Awakening Of CORTEX.md" target: 60-75 minutes
- If too long: TRIM content, don't create variant
- Plugin should TRIM content, not spawn new files
"""
```

---

## 🧪 Test Coverage

**Created comprehensive test suite:** `tests/plugins/test_doc_refresh_file_rules.py`

### Test Categories

**1. File Creation Prohibition (5 tests):**
- ✅ Fails when file doesn't exist
- ✅ Refresh all docs fails on missing file
- ✅ Prohibits Quick Read creation
- ✅ Prohibits Summary variant creation
- ✅ Only updates existing files

**2. Read Time Enforcement (6 tests):**
- ✅ Calculates read time correctly (225 wpm)
- ✅ Detects when content too long
- ✅ Detects when content too short
- ✅ Validates acceptable range (±10%)
- ✅ Includes read time in transformation plan
- ✅ Story refresh validates read time

**3. Configuration Enforcement (4 tests):**
- ✅ Default config enforces no file creation
- ✅ Default config enforces read time
- ✅ Default config trims on exceed
- ✅ Target read time has valid range

**4. Documentation (1 test):**
- ✅ Module docstring contains critical rules

**Total: 16 tests, all passing ✅**

---

## 📁 Files Changed

### Modified Files

**Plugin Implementation:**
- `src/plugins/doc_refresh_plugin.py`
  - Added file existence validation (2 levels)
  - Added read time validation
  - Updated config schema (4 new options)
  - Updated module docstring with CRITICAL RULES

### New Files

**Test Suite:**
- `tests/plugins/test_doc_refresh_file_rules.py` (16 tests)

**Documentation:**
- `docs/plugins/doc-refresh-file-rules.md` (comprehensive guide)
- `cortex-brain/DOC-REFRESH-FILE-PROHIBITION.md` (this file)

### Deleted Files

**Violation Removed:**
- `docs/story/CORTEX-STORY/Awakening Of CORTEX - Quick Read.md` ❌ (deleted)

---

## 📊 Impact Analysis

### Before Fix

| Metric | Value | Status |
|--------|-------|--------|
| File Creation Prevention | ❌ None | Vulnerable |
| Read Time Enforcement | ❌ None | Uncontrolled |
| Violation Detection | ❌ 0 tests | Unprotected |
| Documentation | ❌ Unclear rules | Ambiguous |

### After Fix

| Metric | Value | Status |
|--------|-------|--------|
| File Creation Prevention | ✅ 2-level validation | Enforced |
| Read Time Enforcement | ✅ Calculated & validated | Controlled |
| Violation Detection | ✅ 16 comprehensive tests | Protected |
| Documentation | ✅ Clear CRITICAL RULES | Explicit |

### Test Coverage

```
Before: 0 tests for file rules
After:  16 tests (100% passing)
Coverage: File creation, read time, config, docs
```

---

## 🎯 Success Criteria

**All criteria met:**

1. ✅ **No File Creation** - Plugin refuses to create new files
2. ✅ **Two-Level Validation** - Checks at refresh_all and refresh_story
3. ✅ **Read Time Enforcement** - Calculates and validates (±10%)
4. ✅ **Trimming Logic** - Recommends trimming (not creating variants)
5. ✅ **Configuration** - 4 new settings, all default-safe
6. ✅ **Test Coverage** - 16 comprehensive tests
7. ✅ **Documentation** - Clear CRITICAL RULES in docstring
8. ✅ **Violation Removed** - Quick Read file deleted

---

## 🚀 Next Steps

### For Future Doc Refreshes

**Checklist before running refresh:**

1. ✅ Verify target file exists
2. ✅ Check current read time
3. ✅ Review transformation plan
4. ✅ Backup existing file
5. ✅ Run validation tests
6. ✅ Apply updates to EXISTING file
7. ✅ Validate read time after update
8. ✅ Never create new files

### Monitoring

**Regular checks:**
```bash
# Detect unauthorized files
ls docs/story/CORTEX-STORY/ | grep -E "(Quick|Summary|Variant)"

# Run file rules tests
pytest tests/plugins/test_doc_refresh_file_rules.py -v

# Check plugin config
python -c "from src.plugins.doc_refresh_plugin import Plugin; \
           p = Plugin(); print(p._get_metadata().config_schema)"
```

---

## ⚠️ Warning to Future Maintainers

**DO NOT DISABLE THESE RULES:**

The following config options should NEVER be changed from defaults:

```python
# ❌ DANGEROUS - Never do this
config = {
    "enforce_no_file_creation": False,  # BAD!
    "trim_content_on_exceed": False     # BAD!
}

# ✅ SAFE - Keep defaults
config = {
    "enforce_no_file_creation": True,   # ALWAYS True
    "trim_content_on_exceed": True      # ALWAYS True
}
```

**Why these rules exist:**
1. Prevent documentation fragmentation
2. Maintain single source of truth
3. Enforce quality standards
4. Enable predictable maintenance

---

## 📚 References

**Related Documents:**
- Plugin Implementation: `src/plugins/doc_refresh_plugin.py`
- Test Suite: `tests/plugins/test_doc_refresh_file_rules.py`
- Detailed Rules: `docs/plugins/doc-refresh-file-rules.md`
- Configuration Guide: `.github/copilot-instructions.md`

**Related Issues:**
- CORTEX created Quick Read variant (violation detected Nov 9, 2025)
- Need to enforce 15-20 min read time rule
- Document refresh should never create new files

---

## ✨ Summary

**Problem:** Document refresh created new file instead of updating existing

**Solution:** 
- Two-level file existence validation
- Read time calculation and enforcement
- Comprehensive test coverage (16 tests)
- Clear documentation of CRITICAL RULES

**Result:**
- ✅ File creation absolutely prohibited
- ✅ Read time enforced (60 min target, ±10%)
- ✅ Violation removed (Quick Read deleted)
- ✅ 16 tests protecting against future violations

**Status:** COMPLETE ✅

---

**Implemented by:** CORTEX  
**Date:** November 9, 2025  
**Test Results:** 16/16 passing ✅  
**Documentation:** Complete ✅
