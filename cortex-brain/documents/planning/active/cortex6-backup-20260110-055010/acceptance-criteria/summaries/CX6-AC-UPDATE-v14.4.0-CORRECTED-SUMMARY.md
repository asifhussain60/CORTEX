# CX6 Acceptance Criteria Update - v14.4.0 CORRECTED SUMMARY

**Date:** 2026-01-09  
**Version:** v14.4.0 (Corrected)  
**Author:** CORTEX  
**Status:** CORRECTED - Aligned with approved planning structure

---

## 🔴 Critical Correction Applied

**Issue:** Initial v14.4.0 update contained INCORRECT planning structure requirements in AC-ORC-002.

**Root Cause:** Agent error - proposed rules based on incomplete manifest analysis (planner-v1-manifest.yaml only) without checking approved AC-ORC-PLAN-002.

**Resolution:** AC-ORC-002 corrected to align with AC-ORC-PLAN-002 (approved structure from commit 44949e126).

---

## ✅ Corrected Planning Structure Requirements

### **ROOT FILES (Exactly 3 Allowed)**

| File | Purpose | Format |
|------|---------|--------|
| `continuation-prompt.md` | Session continuation prompt (token limit management) | Markdown |
| `thoughts.txt` | Random thoughts/notes during plan execution | Plain text |
| `plan-viewer.html` | Plan visualization dashboard | HTML |

### **FORBIDDEN on Root**
- ❌ `00-{plan-name}.md` (legacy master plan format)
- ❌ `README.md` (must be in artifacts/ or analysis/)
- ❌ Any `.yaml` or `.json` files
- ❌ Any files with `00-`, `01-`, etc. prefixes
- ❌ `launch_plan_viewer.py` (generated on approval, not during planning)

### **REQUIRED SUBFOLDERS**

| Folder | Contents |
|--------|----------|
| `analysis/` | Deep analysis, architecture review, gap detection |
| `artifacts/` | Generated YAML plans, master plans, feature specs |
| `context/` | Background docs, discovery reports, constraints |
| `reports/` | Progress reports, completion summaries |
| `tracking/` | Progress tracker JSON, state snapshots |

### **FILE FORMAT REQUIREMENTS**

- ✅ **All planning artifacts:** YAML (`.yaml`) or JSON (`.json`) format
- ✅ **Naming convention:** `kebab-case-pattern.yaml` (NO `00-` prefixes)
- ❌ **FORBIDDEN:** Legacy `00-master-plan.md`, `01-feature.md` format

---

## 📋 What Changed in v14.4.0 (Corrected)

### AC-ORC-002 (Corrected)
**Before (INCORRECT):**
```yaml
- "**ROOT FILE REQUIREMENT:** ONLY plan-viewer.html allowed on root (NO other files)"
- "**README:** README.md in root OR analysis/ (NOT 00-README.md)"
- "**CONTINUATION PROMPT:** tracking/CONTINUATION-PROMPT.md exists"
```

**After (CORRECT):**
```yaml
- "**ROOT FILES:** EXACTLY 3 files allowed: continuation-prompt.md, thoughts.txt, plan-viewer.html"
- "**CONTINUATION PROMPT:** continuation-prompt.md at root (NOT in tracking/)"
- "**RANDOM THOUGHTS:** thoughts.txt at root for ad-hoc notes during execution"
- "**MASTER PLAN:** Plan YAML in artifacts/ or tracking/ (NOT root, MUST be .yaml format)"
```

### New Acceptance Criteria Added

#### AC-ORC-013: plan-viewer.html Generation
- Generated when plan approved for execution (NOT during planning)
- Registered in CapabilityRegistry with metadata
- Auto-launches via `launch_plan_viewer.py` (background execution)
- Validates against AC-ORC-PLAN-004 (CORTEX logo at 200x200px)

#### AC-ORC-014: launch_plan_viewer.py Generation
- HTTP server launcher with auto-port detection (8000-8010)
- Non-blocking background execution
- Project root detection (finds CORTEX repo via .git)
- Generated alongside plan-viewer.html on approval

### SECTION 20: REGISTRATION FRAMEWORK (8 New AC)

| AC ID | Criterion |
|-------|-----------|
| AC-REG-001 | All orchestrators registered in OrchestratorRegistry |
| AC-REG-002 | All MCP tools registered in CapabilityRegistry |
| AC-REG-003 | All modules registered with import validation |
| AC-REG-004 | Registration integrity tests for every component |
| AC-REG-005 | Orchestrator instantiation tests via registry |
| AC-REG-006 | MCP tool discovery and invocation tests |
| AC-REG-007 | Module dependency validation |
| AC-REG-008 | Registration failure handling and rollback |

---

## 🎯 Alignment with Approved Structure

### AC-ORC-PLAN-002 (Source of Truth)
**Added in v7.0.0 (commit 44949e126):**
```yaml
acceptance:
  - "**FORBIDDEN:** Planning files must NOT use legacy 00-*, 01-*, etc. prefix format"
  - "**REQUIRED:** All planning artifacts must be YAML (.yaml) or JSON (.json) format"
  - "**EXCEPTION:** Only 3 files allowed at plan root: continuation-prompt.md, thoughts.txt, plan-viewer.html"
  - "**VALIDATION:** File scan detects legacy format and blocks plan creation"
  - "**GOVERNANCE:** CORE-PLAN-FILE-FORMAT rule enforced"
```

### SKULL Rules Updated

| Rule | Enforcement |
|------|-------------|
| `PLAN_FILE_ORGANIZATION` | EXACTLY 3 files on root (continuation-prompt.md, thoughts.txt, plan-viewer.html) |
| `NO_00_PREFIX_FILES` | NO files may start with 00- |
| `FIVE_SUBFOLDER_STRUCTURE` | analysis, artifacts, context, reports, tracking REQUIRED |
| `YAML_JSON_ONLY` | All plan artifacts (except 3 root files) MUST be .yaml or .json format |

---

## 📊 Impact Summary

### Files Modified
- ✅ `CX6-acceptance-criteria.yaml` (AC-ORC-002 corrected, 10 new AC added)

### Acceptance Criteria Status
- **Total AC:** 390+ (10 new in v14.4.0)
- **Corrected:** AC-ORC-002 (planning structure)
- **Added:** AC-ORC-013, AC-ORC-014, AC-REG-001 to AC-REG-008

### Priority Breakdown
- **P0_CRITICAL:** AC-ORC-002, AC-ORC-PLAN-002, AC-REG-001 to AC-REG-008
- **P1_HIGH:** AC-ORC-013, AC-ORC-014

---

## 🚀 Migration Guide

### For Existing Plans (Created with OLD Structure)

**Example: cortex6-planner/**

**Current (INCORRECT):**
```
cortex6-planner/
├── 00-cortex6-complete-build.md   ❌ (00- prefix, .md format, on root)
├── README.md                       ❌ (not allowed on root)
├── analysis/
├── artifacts/
├── context/
├── reports/
└── tracking/
```

**Should Be (CORRECT):**
```
cortex6-planner/
├── continuation-prompt.md          ✅ (root)
├── thoughts.txt                    ✅ (root)
├── plan-viewer.html                ✅ (root, generated on approval)
├── analysis/
├── artifacts/
│   └── cortex6-build-plan.yaml    ✅ (master plan in artifacts/)
├── context/
├── reports/
└── tracking/
    └── progress-tracker.json       ✅
```

### Migration Steps

1. **Move master plan:** `00-*.md` → `artifacts/{plan-name}.yaml` (convert to YAML)
2. **Move README:** `README.md` → `artifacts/README.md` or `analysis/README.md`
3. **Create root files:** `continuation-prompt.md`, `thoughts.txt`
4. **Generate on approval:** `plan-viewer.html` (via Planning Orchestrator)
5. **Validate:** Run `tests/orchestrators/test_planning_v5_structure.py`

---

## 🔍 Verification

### Test Coverage
```bash
# Planning structure validation
pytest tests/orchestrators/test_planning_v5_structure.py

# File format compliance
pytest tests/orchestrators/test_planning_file_format.py

# Registration framework
pytest tests/registration/test_orchestrator_registry.py
pytest tests/registration/test_capability_registry.py
```

### Audit Validation
```bash
# Check planning structure audit logs
ls cortex-brain/audit-logs/planning-structure-*.json

# Verify plan folder structure
cat {plan_folder}/reports/structure-validation.json
```

---

## 📚 References

### Source Documents
- **AC-ORC-PLAN-002:** Line 1444, CX6-acceptance-criteria.yaml (v7.0.0, commit 44949e126)
- **AC-ORC-002:** Line 1010, CX6-acceptance-criteria.yaml (v14.4.0, corrected)
- **PLAN_FILE_ORGANIZATION SKULL Rule:** cortex-brain/brain-protection-rules.yaml (commit fbda1492c)

### Related Manifests
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- `cortex-brain/manifests/orchestrators/planner-v1-manifest.yaml`

---

## ⚠️ Lessons Learned

### What Went Wrong
1. **Incomplete Analysis:** Checked planner-v1-manifest.yaml (future system) instead of AC-ORC-PLAN-002 (approved current system)
2. **Manifest Mismatch:** planner-v1 has "ONLY plan-viewer.html" rule, but approved structure allows 3 root files
3. **Version Confusion:** Mixed Planning System v5 (current) with Planner v1 (future migration target)

### Prevention
1. ✅ **Always check acceptance-criteria/ first** (source of truth for requirements)
2. ✅ **Cross-reference multiple sources** (manifests + AC + git history)
3. ✅ **Verify with user** before proposing corrections
4. ✅ **Check changelog** in AC file for approved changes

---

## ✅ Conclusion

**v14.4.0 Status:** CORRECTED  
**AC-ORC-002:** Aligned with AC-ORC-PLAN-002 (approved structure)  
**Planning Structure:** 3 root files (continuation-prompt.md, thoughts.txt, plan-viewer.html)  
**File Format:** YAML/JSON only (NO 00- prefixes)  
**Registration Framework:** 8 new AC for component validation  

**Next Steps:**
1. Update Planning Orchestrator v5 to enforce corrected structure
2. Migrate existing plans (cortex6-planner/) to new structure
3. Implement registration framework (AC-REG-001 to AC-REG-008)
4. Generate plan-viewer.html on plan approval (AC-ORC-013)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
