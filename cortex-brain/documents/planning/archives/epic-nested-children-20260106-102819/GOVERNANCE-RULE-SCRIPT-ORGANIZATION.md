# ✅ Governance Rule Added: SCRIPT_ORGANIZATION_ENFORCEMENT

**Date:** 2026-01-06  
**Rule ID:** `SCRIPT_ORGANIZATION_ENFORCEMENT`  
**Epic:** cortex5-enhancement-epic  
**Phase:** 1.5 (Script Consolidation Governance)  
**Status:** ✅ Rule Created, ⏳ Implementation Pending

---

## 🎯 Problem Identified

**Issue:** Script sprawl in `src/orchestrators/planning/` directory
- 15+ Python scripts doing similar/overlapping functionality
- Multiple duplicate detection scripts (orphan_detector.py, duplicate_detector.py, similarity_checker.py)
- No central catalog or organization system
- Discovery failures ("which script does what?")
- Maintenance burden (updating logic in multiple places)

**Impact:**
- Code duplication → harder to maintain
- Import confusion → which module to use?
- Testing gaps → duplicate scripts need duplicate tests
- Increased codebase size → slower to navigate
- Knowledge silos → unclear ownership

---

## ✅ Governance Rule Created

### Rule Details

**File:** `cortex-brain/brain-protection-rules.yaml` (lines 188-233)

**Rule ID:** `SCRIPT_ORGANIZATION_ENFORCEMENT`  
**Category:** `architecture_integrity`  
**Severity:** `blocked`  
**Name:** Script Consolidation & Cataloging Required

### Rule Description

ALL utility scripts MUST be:
1. **Cataloged** by Cortex Toolkit Orchestrator
2. **Scanned** for duplicate functionality
3. **Consolidated** into unified modules if overlapping
4. **Archived** if orphaned (unused)
5. **Organized** via child orchestrators per domain

### Enforcement

**Trigger:** `script_creation`  
**Action:** `block_if_uncataloged_or_duplicate`

**Validation Checks:**
- ✅ Script must be registered in catalog
- ✅ Duplicate functionality scanner must run
- ✅ Similar scripts must be consolidated
- ✅ Orphaned scripts must be archived
- ✅ Child orchestrators manage organization

### Implementation

**Master Orchestrator:** `cortex_toolkit`  
**Scanner:** `src.orchestrators.toolkit.duplicate_script_detector`  
**Catalog:** `cortex-brain/toolkit/script-catalog.yaml`

**Remediation Commands:**
```bash
# Scan for duplicate scripts
python3 -m src.orchestrators.toolkit.scan_duplicate_scripts

# Consolidate scripts for specific domain
python3 -m src.orchestrators.toolkit.consolidate_scripts --domain planning

# View consolidation report
cat cortex-brain/documents/reports/script-consolidation-{timestamp}.md
```

### Examples

**✅ PASS:**
- Planning scripts consolidated into `planning_orchestrator_v5.py` modules
- Duplicate detectors merged into single `duplicate_detector.py`
- Scripts registered in toolkit catalog with clear ownership

**❌ FAIL:**
- 10+ `*.py` files in `src/orchestrators/planning/` doing similar tasks
- Multiple duplicate detection scripts without consolidation
- Uncataloged scripts in random directories

---

## 📋 Phase 1.5: Script Consolidation Governance

**Added to:** `cortex5-enhancement-epic/CORTEX5-SNOWBALL.md` (Phase 1.5)

### Objectives

1. **Create Cortex Toolkit Orchestrator** (Master + Child orchestrators)
   - Scanner child: Duplicate script detection
   - Consolidator child: Merge similar scripts
   - Cataloger child: Register scripts in central catalog

2. **Scan & Consolidate** `src/orchestrators/planning/`
   - AST-based similarity detection
   - Function signature matching
   - Purpose overlap analysis
   - Target: <10 scripts (down from 15+)

3. **Create Script Catalog Registry**
   - `cortex-brain/toolkit/script-catalog.yaml`
   - Document purpose, owner, dependencies
   - Enforce registration for new scripts

### Deliverables

**Code:**
- `src/orchestrators/toolkit/cortex_toolkit_orchestrator.py` (Master)
- `src/orchestrators/toolkit/duplicate_script_detector.py` (Child)
- `src/orchestrators/toolkit/script_consolidator.py` (Child)
- `src/orchestrators/toolkit/script_cataloger.py` (Child)

**Configuration:**
- `cortex-brain/toolkit/script-catalog.yaml` (Registry)

**Documentation:**
- `cortex-brain/documents/reports/script-consolidation-2026-01-06.md`

### Success Criteria

- ✅ <10 scripts in `src/orchestrators/planning/` (reduced from 15+)
- ✅ Zero duplicate functionality detected
- ✅ All scripts registered in catalog
- ✅ `SCRIPT_ORGANIZATION_ENFORCEMENT` rule active in brain protection

### Timeline

**Duration:** 3 days (urgent priority)  
**Status:** ⏳ Not Started  
**Blocks:** Phase 2 (Goal Inheritance Resolver)

---

## 🔍 Current Script Inventory (Planning Domain)

**Location:** `src/orchestrators/planning/`

**Scripts to Review:**
1. `planning_orchestrator_v5.py` - Main orchestrator
2. `duplicate_detector.py` - Detects code duplicates
3. `orphan_detector.py` - Finds orphaned functions
4. `similarity_checker.py` - Checks code similarity
5. `ast_scanner.py` - AST parsing
6. `knowledge_graph_query.py` - Knowledge graph integration
7. `governance_integrator.py` - Governance checks
8. `html_viewer_generator.py` - Plan viewer HTML
9. `planner_mode_detector.py` - Epic vs Feature detection
10. `dual_mode_integration.py` - Dual mode support
11. `acceptance_criteria_validator.py` - DoR/DoD validation
12. `phases/phase_*.py` - Phase implementations (5 files)

**Suspected Duplicates:**
- `duplicate_detector.py` + `orphan_detector.py` + `similarity_checker.py` → Consolidate into `code_analyzer.py`
- Phase files might share common logic → Extract to `phase_base.py`

**Total:** ~17 files → Target: <10 files after consolidation

---

## 🚀 Implementation Plan

### Step 1: Create Toolkit Orchestrator (Day 1)
```bash
# Create master toolkit orchestrator
python3 -m src.main "plan cortex toolkit orchestrator with child orchestrators for duplicate detection, script consolidation, and cataloging"

# Implement master + 3 child orchestrators
```

### Step 2: Scan & Analyze (Day 1-2)
```bash
# Run duplicate script scanner
python3 -m src.orchestrators.toolkit.scan_duplicate_scripts --domain planning

# Generate similarity report
cat cortex-brain/documents/reports/duplicate-scripts-planning-2026-01-06.md
```

### Step 3: Consolidate Scripts (Day 2)
```bash
# Consolidate detected duplicates
python3 -m src.orchestrators.toolkit.consolidate_scripts --domain planning --auto

# Review consolidation proposal
cat cortex-brain/documents/reports/consolidation-proposal-planning.md

# Approve and execute
python3 -m src.orchestrators.toolkit.consolidate_scripts --domain planning --execute
```

### Step 4: Create Catalog (Day 3)
```bash
# Generate script catalog
python3 -m src.orchestrators.toolkit.catalog_scripts --domain planning

# View catalog
cat cortex-brain/toolkit/script-catalog.yaml
```

### Step 5: Verify & Enforce (Day 3)
```bash
# Verify all scripts cataloged
python3 -m src.orchestrators.toolkit.verify_catalog --strict

# Enable enforcement rule
# (SCRIPT_ORGANIZATION_ENFORCEMENT already added to brain-protection-rules.yaml)
```

---

## 📊 Expected Outcomes

### Before (Current State):
```
src/orchestrators/planning/
├── planning_orchestrator_v5.py
├── duplicate_detector.py          # ❌ Overlaps with orphan_detector
├── orphan_detector.py              # ❌ Overlaps with duplicate_detector
├── similarity_checker.py           # ❌ Overlaps with both above
├── ast_scanner.py
├── knowledge_graph_query.py
├── governance_integrator.py
├── html_viewer_generator.py
├── planner_mode_detector.py
├── dual_mode_integration.py
├── acceptance_criteria_validator.py
├── phases/phase_minus_one.py       # ❌ Shared logic across phases
├── phases/phase_zero.py            # ❌ Shared logic across phases
├── phases/phase_one.py             # ❌ Shared logic across phases
├── phases/phase_two.py             # ❌ Shared logic across phases
└── phases/phase_three.py           # ❌ Shared logic across phases

Total: 17 files (with overlapping functionality)
```

### After (Target State):
```
src/orchestrators/planning/
├── planning_orchestrator_v5.py
├── code_analyzer.py                # ✅ Consolidated duplicate/orphan/similarity
├── ast_scanner.py
├── knowledge_graph_query.py
├── governance_integrator.py
├── html_viewer_generator.py
├── planner_mode_detector.py
├── dual_mode_integration.py
├── acceptance_criteria_validator.py
├── phases/phase_base.py            # ✅ Extracted shared logic
└── phases/phase_implementations.py # ✅ Consolidated phase files

Total: <10 files (no duplication, clear separation of concerns)
```

**Reduction:** 17 files → 10 files (41% reduction)  
**Duplication:** Eliminated  
**Maintainability:** Significantly improved

---

## 🏆 Benefits

### Immediate:
1. **Reduced codebase size** - 41% fewer files to maintain
2. **Eliminated duplication** - Single source of truth per functionality
3. **Clearer organization** - One module per responsibility
4. **Faster discovery** - Easy to find "which script does what"

### Long-term:
1. **Easier maintenance** - Update logic in one place
2. **Better test coverage** - Test once, not multiple times
3. **Reduced onboarding time** - New developers understand structure faster
4. **Enforced standards** - Governance rule prevents future sprawl

---

## 📚 Related Documentation

- **Governance Rule:** `cortex-brain/brain-protection-rules.yaml` (lines 188-233)
- **Epic Plan:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX5-SNOWBALL.md` (Phase 1.5)
- **Master Plan:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml` (61 rules total)

---

**Status:** ✅ Rule Created, ⏳ Implementation Pending  
**Priority:** ⚡ URGENT (blocks Phase 2)  
**Duration:** 3 days  
**Epic:** cortex5-enhancement-epic
