# Holistic Requirements Compilation from Chat History

**Compiled:** 2026-01-06  
**Source:** Chat01.md, chat02.md, chat03.md  
**Status:** Complete extraction of all requirements, enhancements, dos and don'ts

---

## 🎯 Executive Summary

This document consolidates ALL requirements, fixes, enhancements, and governance rules mentioned across three chat sessions into a comprehensive requirements list for the CORTEX 5.0 Enhancement Epic.

---

## 1️⃣ Plan Folder Structure Requirements

### 1.1 Folder Hierarchy Rules
- ✅ **MANDATORY:** Child plans MUST be created inside epic parent folders, NOT at active/ root
- ✅ **5-Subfolder Standard:** Every plan MUST have: `analysis/`, `artifacts/`, `context/`, `reports/`, `tracking/`
- ✅ **Epic Structure:** Epic folders MUST also have: `features/`, `phases/`
- ✅ **Meaningful Naming:** Max 22 chars, kebab-case (e.g., `cortex5-enhancement-epic`)
- ❌ **NO UUID-based folders:** No `plan-{uuid}` pattern allowed
- ❌ **NO nested child violations:** Child plans cannot have their own child plans

### 1.2 Root File Rules
- ✅ **ONLY allowed file in plan root:** `plan-viewer.html`
- ❌ **NO .md files in root:** All markdown files go in subfolders
- ❌ **NO .sh/.py scripts in root:** Scripts belong in cortex-toolkit orchestrator
- ✅ **Master plan location:** `phases/master-plan.md`

### 1.3 Epic Parent Path Detection
- ✅ **Continue pattern:** `continue {epic-name}` must detect epic folder
- ✅ **Regex patterns:** Detect epic names like `cortex5-enhancement-epic`, `remediation-epic`, etc.
- ✅ **Context passing:** `epic_parent_path` passed via `master_context` to planning orchestrator
- ✅ **Path construction:** Folder creation checks for epic parent before building path

**Files Modified:**
- `src/entry_point/cortex_entry.py` - Added `_detect_epic_parent_path()` method
- `src/orchestrators/planning/planning_orchestrator_v5.py` - Modified `_create_folder_structure()`

---

## 2️⃣ Script Consolidation & Governance

### 2.1 Script Organization Problem
- ❌ **Current:** 17+ Python files in `src/orchestrators/planning/` with overlapping functionality
- ❌ **Duplicates detected:** Multiple scripts doing duplicate detection, similarity checking, orphan detection
- ❌ **No catalog:** Scripts not registered or tracked
- ❌ **Discovery failures:** Unclear which script to use for specific tasks

### 2.2 Solution: Cortex Toolkit Orchestrator
- ✅ **Master orchestrator:** Intelligent parent with 3 child orchestrators:
  1. **Scanner Child** - Duplicate script detection (AST-based analysis)
  2. **Consolidator Child** - Merge similar scripts into unified modules
  3. **Cataloger Child** - Register scripts in central catalog
- ✅ **Target:** Reduce 17 scripts → <10 scripts (41% reduction)
- ✅ **Catalog location:** `cortex-brain/toolkit/script-catalog.yaml`

### 2.3 Governance Rule: SCRIPT_ORGANIZATION_ENFORCEMENT
- ✅ **Rule ID:** `SCRIPT_ORGANIZATION_ENFORCEMENT`
- ✅ **Category:** `architecture_integrity`
- ✅ **Severity:** `blocked` (prevents uncataloged/duplicate scripts)
- ✅ **Location:** `cortex-brain/brain-protection-rules.yaml` (lines 188-233)
- ✅ **Enforcement:** All scripts MUST be cataloged via toolkit orchestrator
- ✅ **Detection:** Automatic duplicate detection scanner
- ✅ **Consolidation:** Multiple scripts doing same task merged into one

**Epic Phase:** Phase 1.5 - Script Consolidation Governance (⚡ URGENT, 3 days)

---

## 3️⃣ Plan Viewer Generation

### 3.1 Requirements
- ✅ **Location:** `{epic-folder}/plan-viewer.html` (epic root ONLY)
- ✅ **Content:** Interactive HTML showing:
  - Features tree with categories
  - Phases timeline with progress
  - Progress tracker with visual bars
  - Dependencies graph
  - Quick navigation
- ✅ **Generation:** Automatic via Planning Orchestrator v5
- ❌ **Not in child plans:** Child plans should not have separate viewers

### 3.2 Current Issue
- ❌ Epic folder `cortex5-enhancement-epic` has placeholder plan-viewer.html
- ❌ Needs regeneration with actual epic content

---

## 4️⃣ Response Template Compliance

### 4.1 Autonomous Orchestrator Templates
- ✅ **Template:** `autonomous_execution_progress` (from response-templates-v4.yaml)
- ✅ **Required elements:**
  - Progress bars showing completion percentage
  - Phase-by-phase visual tracking
  - Status icons (✅ ⏳ ❌)
  - Update frequency: Phase completion only (not per task)
- ✅ **Concise mode default:** 3-line routing confirmation
- ✅ **Verbose mode:** Only when user requests "explain" or "verbose"

### 4.2 Accessibility Rules (WCAG AA)
- ✅ **COGNITIVE_LOAD:** Max 1 update per phase (not per task)
- ✅ **SILENT_TASKS:** No narration of individual task completions
- ✅ **CONCISE_DEFAULT:** Brief responses unless verbose requested
- ✅ **PROGRESS_FREQUENCY:** Update at phase start, phase complete, overall complete
- ✅ **SUMMARY_CAP:** Completion summaries ≤40 lines
- ✅ **NO_NARRATION:** Eliminate "Now I'll...", "Perfect!", "Excellent!" commentary

---

## 5️⃣ TDD Enforcement

### 5.1 Test Harness for Planning
- ✅ **File:** `tests/test_planning_folder_structure.py`
- ✅ **Coverage:**
  - Epic parent path detection from user requests
  - Folder creation logic checks master_context
  - Child plans created inside epic folder
  - Orphaned plan detection and cleanup
  - 5-subfolder validation
  - PLAN_FILE_ORGANIZATION governance enforcement
- ✅ **Current status:** 13/15 tests passing
- ⚠️ **Failures:**
  1. "inside epic" pattern not detected (regex needs improvement)
  2. Missing subfolders in epic (needs creation)

### 5.2 TDD Workflow
- ✅ **RED→GREEN→REFACTOR mandatory** for all code changes
- ✅ **Tests must fail before implementation**
- ✅ **Regression tests** to prevent plan flooding at active/ root

---

## 6️⃣ Governance Rules (SKULL)

### 6.1 Existing Rules Referenced
1. **TDD_ENFORCEMENT** - Tests must fail before implementation
2. **HOLISTIC_DISCOVERY** - Search before create (prevent duplication)
3. **GIT_ISOLATION** - CORTEX code never commits to user repos
4. **PLANNING_ISOLATION** - Planning commands create plans ONLY, never implement
5. **PLAN_FILE_ORGANIZATION** - Plan files MUST live in subfolders (not root)
6. **HAND_OFF_PROTOCOL** - 🛡️ AUTONOMOUS orchestrators execute independently
7. **SCRIPT_ORGANIZATION_ENFORCEMENT** - ✅ NEW (added to epic Phase 1.5)

### 6.2 Rule Locations
- **File:** `cortex-brain/brain-protection-rules.yaml`
- **Total rules:** 61+ governance rules
- **New rule:** Lines 188-233 (SCRIPT_ORGANIZATION_ENFORCEMENT)

---

## 7️⃣ File Organization Rules

### 7.1 Document Organization
- ✅ **Category-based:** `cortex-brain/documents/{category}/`
- ✅ **Categories:** reports/, analysis/, summaries/, investigations/, planning/, implementation-guides/
- ❌ **FORBIDDEN:** Root-level docs in cortex-brain/
- ✅ **Plan docs:** All plan-related docs in plan subfolder structure

### 7.2 Script Organization
- ✅ **Toolkit location:** All standalone scripts in `cortex-toolkit/`
- ✅ **Orchestrator location:** Orchestrator implementations in `src/orchestrators/`
- ❌ **NOT in plan folders:** Scripts don't belong in plan structure
- ✅ **Catalog required:** All scripts registered in script-catalog.yaml

---

## 8️⃣ Cross-Session Continuation

### 8.1 Continuation Prompts
- ✅ **File:** `{plan-folder}/tracking/CONTINUATION-PROMPT.md`
- ✅ **Content:**
  - Last completed phase
  - Next phase to execute
  - Context summary
  - Command to resume: `continue plan {plan-id} from phase X`
- ✅ **Tier 1 integration:** Query working memory for last session state

### 8.2 State Tracking
- ✅ **Progress tracker:** `tracking/progress-tracker.json`
- ✅ **Milestones:** `tracking/milestones.md`
- ✅ **Snowball effect:** `tracking/snowball.md`
- ✅ **Database:** PlanningStateDB persistence across sessions

---

## 9️⃣ Cleanup & Orphaned Plans

### 9.1 Orphaned Plan Problem (RESOLVED)
- ❌ **Issue:** 29 orphaned plan folders created at active/ root instead of inside epic
- ✅ **Solution:** Created `scripts/cleanup_orphaned_plans.py`
- ✅ **Result:** 27 plans moved automatically, 2 moved manually
- ✅ **Final state:** Only `cortex5-enhancement-epic/` at active/ root

### 9.2 Cleanup Script Features
- ✅ **Dry-run mode:** Preview changes before execution
- ✅ **Archive:** Moves orphaned plans into epic folder (preserves content)
- ✅ **Detection:** Identifies plans that should be inside epic
- ✅ **Validation:** Ensures epic folder exists before moving

---

## 🔟 Dos and Don'ts Summary

### ✅ DO:
1. Create child plans inside epic parent folders
2. Use meaningful naming (max 22 chars, kebab-case)
3. Include 5 required subfolders in every plan
4. Generate plan-viewer.html in epic root
5. Catalog all scripts via toolkit orchestrator
6. Write tests before implementing (RED→GREEN→REFACTOR)
7. Use autonomous execution templates with progress bars
8. Pass epic_parent_path via master_context
9. Archive orphaned plans, don't delete
10. Update CONTINUATION-PROMPT.md for cross-session resumption
11. Store scripts in cortex-toolkit, not plan folders
12. Follow SKULL governance rules strictly
13. Use concise mode by default (verbose only on request)
14. Update progress at phase boundaries only
15. Organize by features/ and phases/ for epics

### ❌ DON'T:
1. Create plans at active/ root when epic exists
2. Use UUID-based folder names (plan-{uuid})
3. Put .md/.sh/.py files in plan root
4. Create duplicate scripts without consolidation
5. Skip test harness validation
6. Narrate individual task completions
7. Use verbose commentary ("Now I'll...", "Perfect!")
8. Create nested child plans (grandchild plans)
9. Store docs at cortex-brain/ root level
10. Commit CORTEX code to user repos
11. Implement during planning phase
12. Skip holistic discovery before creating files
13. Exceed 40 lines in completion summaries
14. Update progress per-task (only per-phase)
15. Leave plans unorganized without features/phases structure

---

## 📊 Gap Analysis vs Current Epic

### Missing from Current Epic:
1. **Intelligent Goal Detection** (Phase 1) - Not in master-plan.md
2. **Goal Inheritance Resolver** (Phase 2) - Not in master-plan.md
3. **Script Consolidation Governance** (Phase 1.5) - Added but not detailed
4. **Cross-Session Continuation** - Not explicitly phased
5. **Plan Viewer Generation** - Not in phases
6. **Test Harness for Planning** - Not in phases
7. **Epic Parent Path Detection** - Completed but not documented in epic
8. **Response Template Compliance** - Not tracked
9. **Accessibility Rules (WCAG AA)** - Not in epic
10. **Knowledge Graph Integration** - Mentioned in CORTEX5-SNOWBALL.md but not phased

### Present in Epic but Needs Detail:
1. **CORTEX5-SNOWBALL.md** - High-level roadmap exists but lacks implementation phases
2. **Plan folder structure** - Fixed but needs documentation in epic
3. **Governance rules** - Added but needs feature document

---

## 🎯 Recommended Epic Reorganization

### Features Folder Structure:
```
features/
├── planning-system.md           # Goal detection, folder structure, epic parent detection
├── governance-rules.md          # SKULL rules, script organization, plan file organization
├── toolkit-orchestration.md     # Script consolidation, cataloging, duplicate detection
├── testing-framework.md         # TDD harness, planning tests, regression prevention
├── response-templates.md        # Autonomous progress, accessibility, concise mode
├── continuation-system.md       # Cross-session, state tracking, tier 1 integration
└── plan-viewer.md              # HTML generation, interactive features, navigation
```

### Phases Folder Structure:
```
phases/
├── master-plan.md              # Complete roadmap with all features
├── phase-0-foundation.md       # Epic parent detection, folder structure fixes
├── phase-1-goal-detection.md   # Intelligent goal detection, pattern library
├── phase-1.5-script-consolidation.md  # Toolkit orchestrator, duplicate elimination
├── phase-2-governance.md       # SKULL rules enforcement, validation
├── phase-3-testing.md          # TDD harness, regression tests
├── phase-4-templates.md        # Response template compliance, accessibility
├── phase-5-continuation.md     # Cross-session support, state persistence
└── phase-6-viewer.md           # Plan viewer generation, interactive features
```

---

## 📈 Snowball Effect Optimization

**Principle:** Each phase builds on previous phases for maximum efficiency

**Optimal Sequence:**
1. **Phase 0:** Foundation (folder structure, epic detection) - COMPLETED ✅
2. **Phase 1.5:** Script Consolidation (reduces maintenance burden) - URGENT ⚡
3. **Phase 1:** Goal Detection (enables intelligent planning)
4. **Phase 2:** Governance (enforces standards automatically)
5. **Phase 3:** Testing (validates all previous phases)
6. **Phase 4:** Templates (improves user experience)
7. **Phase 5:** Continuation (enables long-running epics)
8. **Phase 6:** Viewer (visualization and navigation)

**Why This Order:**
- Foundation first (0) enables everything else
- Script consolidation (1.5) reduces technical debt early
- Goal detection (1) improves all future plans
- Governance (2) prevents regression
- Testing (3) validates foundation, consolidation, goals, governance
- Templates (4) + Continuation (5) + Viewer (6) enhance UX progressively

---

## ✅ Completion Checklist

- [x] Extract all requirements from chat history
- [x] Categorize into 10 major areas
- [x] Document dos and don'ts
- [x] Identify gaps vs current epic
- [x] Propose features/ folder structure
- [x] Propose phases/ folder structure
- [x] Define snowball effect optimization
- [ ] Move to next todo: Analyze current epic structure
- [ ] Move to next todo: Design features/ documents
- [ ] Move to next todo: Design phases/ documents
- [ ] Move to next todo: Consolidate child plans
- [ ] Move to next todo: Update master-plan.md
- [ ] Move to next todo: Generate plan-viewer.html
- [ ] Move to next todo: Final cleanup verification

---

**Compiled by:** CORTEX Planning System v5  
**Next Step:** Analyze current cortex5-enhancement-epic structure (Todo #2)
