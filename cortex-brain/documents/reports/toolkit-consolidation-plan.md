# 🔧 Toolkit Consolidation Plan

**Date:** December 30, 2025  
**Author:** Asif Hussain  
**Status:** Ready for Execution

---

## 📊 Current State Analysis

### Total Scripts Found: 65 Python files

### Scripts in Manifest: 27 tools
- Listed in `toolkit-manifest.yaml`
- Documented in `TOOLS-INVENTORY.md`
- Organized into 9 categories

### Scripts NOT in Manifest: ~38 files
- Wrappers, shared utilities, support files
- Some may be obsolete or redundant

---

## 🎯 Consolidation Actions

### 1. Duplicate Cleanup Scripts

**Issue:** Multiple cleanup scripts with overlapping functionality

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| `core/brain/cleanup.py` | Delegator to wrapper | ✅ KEEP | Primary entry point |
| `cli/wrappers/cleanup_wrapper.py` | Wrapper for holistic cleanup | ✅ KEEP | Routes to orchestrator |
| `maintenance/master_cleanup.py` | One-shot cleanup orchestrator | 🔄 MERGE | Merge into full_cleanup.py |
| `maintenance/full_cleanup.py` | 5-phase cleanup orchestrator | ✅ KEEP | Primary maintenance cleanup |
| `maintenance/cleanup_temp_files.py` | Interactive temp file cleanup | ✅ KEEP | Specific use case |
| `maintenance/clear_caches.py` | Clear VS Code/Python caches | ✅ KEEP | Called by full_cleanup.py |
| `maintenance/remove_legacy_refs.py` | Remove deprecated references | ✅ KEEP | Called by full_cleanup.py |
| `maintenance/validate_templates.py` | Validate response templates | ✅ KEEP | Called by full_cleanup.py |
| `maintenance/detect_duplicates.py` | Detect duplicate code | ✅ KEEP | Called by full_cleanup.py |

**Action:** Merge `master_cleanup.py` functionality into `full_cleanup.py` and delete `master_cleanup.py`

---

### 2. Duplicate Health Check Scripts

**Issue:** Two health monitoring scripts

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| `core/brain/healthcheck.py` | Delegator to wrapper | ✅ KEEP | Primary entry point |
| `cli/wrappers/healthcheck_wrapper.py` | Wrapper for health checks | ✅ KEEP | Routes to orchestrator |
| `analytics/metrics/monitor_brain_health.py` | Tier 1 utilization monitor | ✅ KEEP | Different purpose (weekly checks) |
| `analytics/metrics/collect_dashboard_data.py` | Dashboard data collector | ✅ KEEP | Different purpose (metrics) |
| `analytics/visualization/visualize_brain_health.py` | Health visualization | ✅ KEEP | Different purpose (visuals) |

**Action:** No merge needed - each has distinct purpose

---

### 3. Duplicate Generator Wrappers

**Issue:** Multiple wrapper files for generators

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| `cli/wrappers/generate_ra_specs.py` | Legacy wrapper? | ❌ DELETE | Not in manifest |
| `cli/wrappers/generate_ra_specs_v4_wrapper.py` | V4 wrapper | ✅ KEEP | In manifest |
| `cli/wrappers/generate_legacy_specs_wrapper.py` | Legacy wrapper | ✅ KEEP | In manifest |
| `cli/wrappers/extract_schemas_wrapper.py` | Schema extractor wrapper | ✅ KEEP | In manifest |

**Action:** Delete `cli/wrappers/generate_ra_specs.py` (not referenced in manifest)

---

### 4. Obsolete/Orphaned Scripts

**Issue:** Scripts not listed in manifest or README files

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| `rename_planning_system_version.py` | One-time utility | ⚠️ REVIEW | Likely obsolete, but in manifest |
| `analytics/profiling/profile_startup.py` | Startup profiling | ⚠️ REVIEW | Not in manifest, check usage |
| `documentation/html-tools/` subfolder | Nested duplicate structure | 🔄 FIX | Appears to be incorrect nesting |

**Action:** 
- Keep `rename_planning_system_version.py` (it's in the manifest)
- Check if `profile_startup.py` is used anywhere
- Fix `html-tools` folder structure (appears to have incorrect nesting)

---

### 5. HTML Tools Folder Structure Issue

**Issue:** Incorrect nesting detected

```
documentation/html-tools/cortex-toolkit/html-tools/
├── __init__.py
├── generator.py
├── html_toolkit.py
└── validator.py
```

**Should be:**
```
documentation/html-tools/
├── __init__.py
├── generator.py
├── html_toolkit.py
└── validator.py
```

**Action:** Move files up to correct location, delete nested folders

---

## 📋 Execution Steps

### Step 1: Backup Current State ✅
Already backed up via Git

### Step 2: Merge master_cleanup.py into full_cleanup.py
- Review unique functionality in `master_cleanup.py`
- Integrate scan/cleanup workflow into `full_cleanup.py`
- Delete `master_cleanup.py`

### Step 3: Delete Obsolete Wrapper
- Delete `cli/wrappers/generate_ra_specs.py`

### Step 4: Fix HTML Tools Structure
- Move files from `documentation/html-tools/cortex-toolkit/html-tools/` to `documentation/html-tools/`
- Delete empty nested directories

### Step 5: Update Manifest
- Remove `rename-planning-system-version` if truly obsolete
- Verify all paths exist

### Step 6: Update TOOLS-INVENTORY.md
- Reflect new tool count
- Update file paths if changed

### Step 7: Validation
- Run `verify-installation.py`
- Check all manifest scripts exist
- Test primary tools

---

## ✅ Success Criteria

- [ ] No duplicate master/full cleanup scripts
- [ ] No obsolete wrapper files
- [ ] HTML tools folder structure correct
- [ ] All manifest entries have existing scripts
- [ ] TOOLS-INVENTORY.md accurate
- [ ] All primary tools functional

---

## 📊 Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Total Python files | 65 | ~60 |
| Duplicate scripts | 3 | 0 |
| Obsolete scripts | 2+ | 0 |
| Structural issues | 1 | 0 |
| Tools in manifest | 27 | 27 (or 26) |

---

**Next Step:** Execute consolidation actions
