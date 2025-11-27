# CORTEX Documentation Organization Audit Report

**Date:** 2025-11-18  
**Author:** Asif Hussain  
**Purpose:** Audit enterprise documentation generator to enforce organized folder structure

---

## 🎯 Executive Summary

**Finding:** Enterprise documentation generator creates files in scattered locations outside the organized folder structure defined in `cortex-brain/documents/README.md`.

**Impact:** Violates CORTEX.prompt.md mandatory document organization rules, creates technical debt, reduces discoverability.

**Recommendation:** Migrate all documentation generation paths to organized structure, update base URLs, move legacy config.

---

## 📊 Current State Analysis

### Files Using Legacy Paths

1. **Enterprise Documentation Orchestrator**
   - File: `src/operations/enterprise_documentation_orchestrator.py`
   - References: `cortex-brain/doc-generation-config/` (legacy location)
   - Lines: 360, 366

2. **Documentation Module**
   - File: `src/operations/modules/enterprise_documentation_orchestrator_module.py`
   - References: `cortex-brain/doc-generation-config/` (legacy location)
   - Line: 444

3. **Mermaid Diagram Tests**
   - File: `tests/epm/test_mermaid_diagram_generation.py`
   - References: `cortex-brain/doc-generation-config/master-diagram-list.yaml`
   - Line: 325

4. **Base Generator**
   - File: `cortex-brain/admin/documentation/generators/base_generator.py`
   - References: `cortex-brain/doc-generation-config/{config_name}`
   - Line: 306

5. **Test Harnesses**
   - `tests/test_documentation_structure.py` - Uses direct `docs/` paths
   - `tests/test_documentation_structure_paths.py` - Validates against admin config
   - `tests/operations/test_documentation_file_creation.py` - References legacy paths

### Correct Structure (Already Exists)

✅ **Config Location:** `cortex-brain/admin/documentation/config/`
- diagram-definitions.yaml
- master-diagram-list.yaml  
- page-definitions.yaml
- source-mapping.yaml
- validation-rules.yaml

✅ **Documents Location:** `cortex-brain/documents/[category]/`
- reports/
- analysis/
- summaries/
- investigations/
- planning/
- conversation-captures/
- implementation-guides/

---

## 🔧 Required Changes

### Phase 1: Update Base URLs in Source Code

**Files to Update:**
1. `src/operations/enterprise_documentation_orchestrator.py`
2. `src/operations/modules/enterprise_documentation_orchestrator_module.py`
3. `cortex-brain/admin/documentation/generators/base_generator.py`

**Changes:**
```python
# OLD (incorrect)
"cortex-brain/doc-generation-config/"

# NEW (correct)
"cortex-brain/admin/documentation/config/"
```

### Phase 2: Update Test References

**Files to Update:**
1. `tests/epm/test_mermaid_diagram_generation.py`
2. `tests/test_documentation_structure.py`
3. `tests/operations/test_documentation_file_creation.py`

**Changes:**
- Update config path references
- Ensure tests validate organized structure
- Add validation for document categorization

### Phase 3: Clean Up Legacy Config

**Action:** Remove or migrate legacy folder
- Current: `cortex-brain/doc-generation-config/` (if exists in main branch)
- Target: All configs in `cortex-brain/admin/documentation/config/`

**Note:** Test already validates legacy folder should not exist (test_documentation_structure_paths.py)

### Phase 4: Update Documentation Output Paths

**Ensure all generated docs go to:**
- Reports → `cortex-brain/documents/reports/`
- Analysis → `cortex-brain/documents/analysis/`
- Generated files → `docs/generated/` (user-facing)
- Internal docs → Appropriate category in `cortex-brain/documents/`

---

## 📋 Implementation Plan

### Step 1: Update Enterprise Documentation Orchestrator
```python
# Line 360, 366 in enterprise_documentation_orchestrator.py
# Change error messages and path references
```

### Step 2: Update Module References
```python
# Line 444 in enterprise_documentation_orchestrator_module.py
# Update path constant
```

### Step 3: Update Base Generator
```python
# Line 306 in base_generator.py
# Update config path resolution
```

### Step 4: Update Test Harnesses
```python
# Mermaid test - line 325
# Update master-diagram-list.yaml path

# Documentation structure tests
# Ensure validation uses correct paths

# File creation tests  
# Update expected paths
```

### Step 5: Validate Changes
```bash
# Run test suite
pytest tests/test_documentation_structure_paths.py -v
pytest tests/operations/test_documentation_file_creation.py -v
pytest tests/epm/test_mermaid_diagram_generation.py -v

# Run full documentation generation
python src/operations/enterprise_documentation_orchestrator.py --dry-run
```

---

## ✅ Success Criteria

1. ✅ All code references use `cortex-brain/admin/documentation/config/`
2. ✅ No references to legacy `doc-generation-config/` path
3. ✅ Generated documents categorized properly in `cortex-brain/documents/[category]/`
4. ✅ User-facing docs in `docs/` folder
5. ✅ All tests pass with new paths
6. ✅ Test harnesses enforce organized structure

---

## 📊 Risk Assessment

**Risk Level:** Low  
**Reason:** Config already migrated, only updating path strings

**Mitigation:**
- Dry-run tests before live execution
- Validate all tests pass
- Check existing generated files

---

## 🚀 Next Steps

1. Execute Phase 1-4 changes (file updates)
2. Run validation tests
3. Execute dry-run documentation generation
4. Verify output paths
5. Commit changes with audit trail

---

**Status:** Ready for Implementation  
**Estimated Time:** 30-45 minutes  
**Priority:** High (enforces CORTEX.prompt.md mandatory rules)
