# Document Refresh Plugin - File Creation Prohibition Rules

**Date:** November 9, 2025  
**Status:** ENFORCED  
**Severity:** CRITICAL VIOLATION

---

## 🚨 MAJOR VIOLATION DETECTED

### The Problem

On November 9, 2025, CORTEX created a new file:
- `docs/story/CORTEX-STORY/Awakening Of CORTEX - Quick Read.md`

**This is a CRITICAL VIOLATION** of the document refresh plugin's fundamental rules.

### Why This Matters

The document refresh plugin exists to **UPDATE** documentation, not **CREATE** it. Creating new files leads to:

1. **Documentation Fragmentation** - Multiple versions of truth
2. **Maintenance Hell** - Which file is canonical?
3. **Version Drift** - Files become inconsistent over time
4. **Confusion** - Users don't know which file to read

---

## ✅ ENFORCED RULES (As of Nov 9, 2025)

### Rule 1: NEVER Create New Files

**Absolute Prohibition:**
- ❌ Creating new files is FORBIDDEN
- ❌ Creating "Quick Read" variants is FORBIDDEN
- ❌ Creating "Summary" variants is FORBIDDEN
- ❌ Creating any derivative files is FORBIDDEN

**What to do instead:**
- ✅ UPDATE existing files only
- ✅ TRIM content if too long
- ✅ EXPAND content if too short
- ✅ FAIL with error if target file doesn't exist

### Rule 2: File Existence Validation

**Before ANY operation:**
```python
if not file_path.exists():
    return {
        "success": False,
        "error": (
            f"CRITICAL VIOLATION: File {file_path} does not exist. "
            f"Doc refresh plugin NEVER creates new files. "
            f"This operation is PROHIBITED."
        )
    }
```

**Enforcement Points:**
- `_refresh_all_docs()` - Checks ALL files before refresh
- `_refresh_story_doc()` - Individual file validation
- Configuration: `enforce_no_file_creation: true` (default, ALWAYS)

### Rule 3: Read Time Enforcement

**Target Read Times:**
- `Awakening Of CORTEX.md` - 60-75 minutes (epic full story)
- Acceptable range: ±10% of target
- If too long: **TRIM** existing file (don't create Quick Read)
- If too short: **EXPAND** existing content

**Read Time Calculation:**
- Industry standard: 225 words per minute
- Validates before and after refresh
- Reports deviation percentage
- Provides trimming recommendations

### Rule 4: Content Trimming (Not Splitting)

**If content exceeds target:**
```
❌ WRONG: Create "Quick Read" version
✅ RIGHT: Trim verbose sections from existing file
```

**Trimming Strategy:**
- Condense wordy descriptions
- Remove redundant examples
- Streamline transitions
- Keep core narrative intact

---

## 🧪 Test Coverage

**16 comprehensive tests enforce these rules:**

### File Creation Prohibition (5 tests)
1. ✅ `test_fails_when_file_does_not_exist`
2. ✅ `test_refresh_all_docs_fails_on_missing_file`
3. ✅ `test_prohibits_quick_read_creation`
4. ✅ `test_prohibits_summary_variant_creation`
5. ✅ `test_only_updates_existing_files`

### Read Time Enforcement (6 tests)
1. ✅ `test_validate_read_time_calculates_correctly`
2. ✅ `test_validate_read_time_detects_too_long`
3. ✅ `test_validate_read_time_detects_too_short`
4. ✅ `test_validate_read_time_acceptable_range`
5. ✅ `test_transformation_plan_includes_read_time_enforcement`
6. ✅ `test_story_refresh_includes_read_time_validation`

### Configuration Enforcement (4 tests)
1. ✅ `test_default_config_enforces_no_file_creation`
2. ✅ `test_default_config_enforces_read_time`
3. ✅ `test_default_config_trims_on_exceed`
4. ✅ `test_target_read_time_has_valid_range`

### Documentation (1 test)
1. ✅ `test_module_docstring_contains_critical_rules`

**Test File:** `tests/plugins/test_doc_refresh_file_rules.py`

---

## 🔧 Technical Implementation

### Configuration Schema

```python
config_schema = {
    "enforce_no_file_creation": {
        "type": "boolean",
        "description": "CRITICAL: Fail if attempting to create new files",
        "default": True  # ALWAYS True
    },
    "enforce_read_time_limits": {
        "type": "boolean",
        "description": "Enforce target read times for story documents",
        "default": True
    },
    "awakening_story_target_minutes": {
        "type": "integer",
        "description": "Target read time for Awakening Of CORTEX.md",
        "default": 60,
        "minimum": 15,
        "maximum": 75
    },
    "trim_content_on_exceed": {
        "type": "boolean",
        "description": "Trim content if exceeds read time (not create new file)",
        "default": True
    }
}
```

### File Existence Check

```python
# In _refresh_all_docs()
if self.config.get("enforce_no_file_creation", True):
    if not file_path.exists():
        error_msg = (
            f"PROHIBITED: File '{filename}' does not exist. "
            f"Doc refresh plugin NEVER creates new files. "
            f"This is a critical violation of plugin rules."
        )
        logger.error(error_msg)
        results["errors"].append(error_msg)
        results["success"] = False
        continue
```

### Read Time Validation

```python
def _validate_read_time(self, content: str, target_minutes: int) -> Dict[str, Any]:
    """Validate estimated read time for document
    
    Uses industry standard: 225 words per minute
    """
    words = len(content.split())
    words_per_minute = 225
    estimated_minutes = words / words_per_minute
    
    # Acceptable range: ±10%
    min_acceptable = target_minutes * 0.9
    max_acceptable = target_minutes * 1.1
    within_target = min_acceptable <= estimated_minutes <= max_acceptable
    
    return {
        "word_count": words,
        "estimated_minutes": round(estimated_minutes, 1),
        "target_minutes": target_minutes,
        "within_target": within_target,
        "recommendation": self._get_read_time_recommendation(...)
    }
```

---

## 📋 Recommended Actions

### Immediate (Completed)

1. ✅ Delete `Awakening Of CORTEX - Quick Read.md`
2. ✅ Add file existence validation
3. ✅ Add read time enforcement
4. ✅ Create comprehensive tests (16 tests)
5. ✅ Update plugin documentation

### Future Refreshes

**When updating `Awakening Of CORTEX.md`:**

1. **Validate file exists** - ALWAYS check first
2. **Check read time** - Is it within 54-66 min range?
3. **If too long** - Trim verbose sections (don't create Quick Read)
4. **If too short** - Expand existing content
5. **Backup first** - Create `.backups/` version
6. **Update only** - Never create new files

### Monitoring

**Watch for violations:**
```bash
# Check for unauthorized files
ls docs/story/CORTEX-STORY/ | grep -E "(Quick Read|Summary|Variant)"

# Run file rules tests
pytest tests/plugins/test_doc_refresh_file_rules.py -v
```

---

## 🎯 Success Metrics

**Before (Nov 9, 2025):**
- ❌ Created `Quick Read` variant (violation)
- ❌ No file existence validation
- ❌ No read time enforcement
- ❌ 0 tests for these rules

**After (Nov 9, 2025):**
- ✅ File creation PROHIBITED
- ✅ File existence validated at 2 levels
- ✅ Read time calculated and enforced
- ✅ 16 comprehensive tests (all passing)
- ✅ Clear documentation of rules
- ✅ Config defaults enforce safety

---

## 📝 Related Files

**Plugin Implementation:**
- `src/plugins/doc_refresh_plugin.py` (updated)

**Tests:**
- `tests/plugins/test_doc_refresh_file_rules.py` (new, 16 tests)

**Documentation:**
- `docs/plugins/doc-refresh-file-rules.md` (this file)

**Deleted Files:**
- `docs/story/CORTEX-STORY/Awakening Of CORTEX - Quick Read.md` (violation removed)

---

## ⚠️ WARNING

**Do NOT disable these rules:**

```python
# ❌ WRONG - NEVER do this
config = {
    "enforce_no_file_creation": False  # DANGEROUS!
}

# ✅ RIGHT - Keep defaults
config = {
    "enforce_no_file_creation": True  # ALWAYS True
}
```

**These rules exist for good reasons:**
1. Prevent documentation fragmentation
2. Maintain single source of truth
3. Enforce quality standards
4. Prevent maintenance nightmares

---

**Last Updated:** November 9, 2025  
**Status:** ENFORCED  
**Test Coverage:** 16/16 passing ✅
