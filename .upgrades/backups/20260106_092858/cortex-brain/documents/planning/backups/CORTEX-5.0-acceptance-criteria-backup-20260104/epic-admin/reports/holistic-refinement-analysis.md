# 🎯 CORTEX-5.0 Holistic Refinement & Reprioritization Analysis

**Analysis Date:** January 4, 2026  
**Author:** Asif Hussain  
**Purpose:** Align CORTEX-5.0 epic structure with Epic & Feature Planner Vision  
**Status:** 🔬 STRATEGIC ANALYSIS

---

## 📊 Executive Summary

**Key Finding:** CORTEX-5.0 is **ALREADY structured as an Epic Plan** but lacks the infrastructure to execute as one.

### Current Reality vs. Vision Alignment

| Aspect | Current State | Vision Requirements | Gap Status |
|--------|---------------|---------------------|------------|
| **Structure** | Epic with 13+ child plans | Epic with 2+ child plans | ✅ **ALIGNED** |
| **Master Plan** | `00-MASTER-REMEDIATION-PLAN.md` | `00-MASTER-*.md` in root | ✅ **ALIGNED** |
| **Child Plans** | NN-{name}/ folders | NN-{name}/ folders | ✅ **ALIGNED** |
| **Planner Detection** | ❌ Not implemented | `detect_planner_mode()` | ⚠️ **MISSING** |
| **Epic Tracking** | ❌ Manual progress table | `epic-progress-tracker.json` | ⚠️ **MISSING** |
| **HTML Viewers** | ❌ None | Static glassmorphism viewers | ⚠️ **MISSING** |
| **Dependency Tracking** | ✅ Manual in master plan | Automated validation | ⚠️ **PARTIAL** |
| **Progress Aggregation** | ❌ Manual updates | Automatic from child plans | ⚠️ **MISSING** |

**Strategic Recommendation:** 🎯 **Implement Epic & Feature Planner FIRST** (as Sub-Plan 00B) before Test Coverage Sprint.

---

## 🔍 Deep Analysis: Current CORTEX-5.0 Structure

### Discovered Structure

```
CORTEX-5.0/
├── 00-cortex-v5-gap-remediation/          # EPIC ROOT (incorrectly nested)
│   └── 00-MASTER-REMEDIATION-PLAN.md      # Epic master plan
├── 00-test-coverage-sprint/               # Child Plan 00
│   └── 00-test-coverage-sprint.md
├── 01-refinement-orchestrator/            # Child Plan 01
├── 02-debug-orchestrator/                 # Child Plan 02
├── 03-knowledge-library-phase/            # Child Plan 03
├── 04-ast-scanning-planning/              # Child Plan 04
├── 05-context-middleware/                 # Child Plan 05
├── 06-visual-progress/                    # Child Plan 06
├── 07-refactor-enforcement/               # Child Plan 07
├── 08-orchestrator-migrations/            # Child Plan 08
├── 09-final-validation/                   # Child Plan 09
├── 10-acceptance-validation-system/       # Child Plan 10A
├── 10-planning-system-v5-fix/             # Child Plan 10B (duplicate prefix!)
├── 10-planning-v5-enhancement/            # Child Plan 10C (duplicate prefix!)
├── 10-planning-v5-fix/                    # Child Plan 10D (duplicate prefix!)
├── 11-cortex-lens-admin/                  # Child Plan 11
├── 12-production-validation-pipeline/     # Child Plan 12
├── 13-onboarding-system/                  # Child Plan 13
├── 14-demo-tutorials/                     # Child Plan 14
├── 15-user-response-templates/            # Child Plan 15
└── EPIC-FEATURE-PLANNER-VISION.md         # Design doc (this analysis)
```

### 🚨 Critical Structural Issues

#### Issue 1: Nested Epic Root
**Current:** Epic master plan is inside `00-cortex-v5-gap-remediation/` subfolder  
**Expected:** Epic master plan should be at `CORTEX-5.0/00-MASTER-REMEDIATION-PLAN.md`  
**Impact:** Detection algorithm won't recognize this as epic

**Fix Required:**
```bash
# Move master plan up one level
mv 00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md ./
# Delete empty wrapper folder
rmdir 00-cortex-v5-gap-remediation/
```

#### Issue 2: Duplicate Order Prefixes (10A, 10B, 10C, 10D)
**Current:** Four plans share prefix "10-"  
**Expected:** Unique numeric prefixes (10, 16, 17, 18)  
**Impact:** Breaks ordering, causes confusion

**Fix Required:**
```bash
# Renumber duplicate plans
mv 10-planning-system-v5-fix/ 16-planning-system-v5-fix/
mv 10-planning-v5-enhancement/ 17-planning-v5-enhancement/
mv 10-planning-v5-fix/ 18-planning-v5-fix/  # Or merge with 16?
```

#### Issue 3: Missing Epic Infrastructure
**Current:** No tracking/, no JSON trackers, no HTML viewers  
**Expected:** Full epic planner infrastructure per vision  
**Impact:** Cannot execute as true epic plan

**Fix Required:** Implement Epic & Feature Planner (Sub-Plan 00B)

---

## 🎯 Reprioritization Strategy

### Original Priority Order (from Master Plan)

| Order | Sub-Plan | Duration | Issue |
|-------|----------|----------|-------|
| 00 | Test Coverage Sprint | 2-3w | ✅ Correct priority |
| 01-02 | Refinement + Debug | 2w | ⚠️ Depends on 50% test coverage |
| 03-04 | Knowledge Library + AST | 1w | ⚠️ Depends on Planning v5 fixes |
| 05-15 | Various features | 4-6w | ⚠️ Builds on unstable foundation |

### 🎯 NEW Priority Order (Epic-First Strategy)

| Order | Sub-Plan | Duration | Rationale |
|-------|----------|----------|-----------|
| **00A** | **Epic Structure Cleanup** | **2h** | 🚨 **BLOCKER** - Fix structure issues first |
| **00B** | **Epic & Feature Planner Implementation** | **2-3w** | 🚨 **FOUNDATION** - Enables all other work |
| **00C** | **Test Coverage Sprint (Original 00)** | **2-3w** | 🎯 **VALIDATION** - Now has epic infrastructure |
| 01-02 | Refinement + Debug | 2w | ✅ Proceeds as planned |
| 03-15 | Remaining sub-plans | 4-6w | ✅ Benefits from epic tracking |

**Key Insight:** Epic & Feature Planner is **NOT** a "nice-to-have enhancement" — it's **critical infrastructure** for managing this 17-plan epic.

---

## 📋 Refined Execution Sequence

### Phase 00A: Epic Structure Cleanup (IMMEDIATE - 2 hours)

**Blocking Issues to Fix:**

1. **Restructure Epic Root**
   ```bash
   cd cortex-brain/documents/planning/active/CORTEX-5.0/
   
   # Move master plan to correct location
   mv 00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md ./
   
   # Create epic tracking folder
   mkdir -p tracking/
   
   # Remove nested wrapper
   rmdir 00-cortex-v5-gap-remediation/
   ```

2. **Renumber Duplicate Plans**
   ```bash
   # Consolidate or renumber four "10-" prefixed plans
   # Recommendation: Merge 10-planning-v5-fix and 18-planning-v5-fix (duplicates?)
   # Then renumber 10-planning-system-v5-fix → 16-...
   #          10-planning-v5-enhancement → 17-...
   ```

3. **Create Epic Tracking Infrastructure**
   ```bash
   # tracking/epic-progress-tracker.json (schema per vision doc)
   # tracking/child-plan-registry.json
   # tracking/dependency-graph.json
   ```

4. **Update Master Plan Header**
   ```markdown
   # Add to 00-MASTER-REMEDIATION-PLAN.md header:
   **Plan Type:** EPIC
   **Planner Mode:** epic
   **Child Plans:** 17 (after consolidation)
   **Epic Viewer:** CORTEX-5.0-plan-viewer.html (pending Sub-Plan 00B)
   ```

**Exit Criteria:**
- ✅ `detect_planner_mode()` correctly identifies CORTEX-5.0 as EPIC
- ✅ All child plans have unique numeric prefixes
- ✅ Epic tracking folder structure in place
- ✅ Manual tracking JSONs created (will be automated in 00B)

---

### Phase 00B: Epic & Feature Planner Implementation (NEW - 2-3 weeks)

**Priority:** 🚨 **CRITICAL FOUNDATION**

This is the **EPIC-FEATURE-PLANNER-VISION.md** implementation itself.

**Why First:**
1. **Visibility** - Cannot manage 17 child plans without epic dashboard
2. **Tracking** - Manual progress updates are error-prone and unsustainable
3. **Validation** - Need automated dependency checking before scaling up
4. **Foundation** - All future sub-plans benefit from epic infrastructure

**Phases (from vision doc):**

| Phase | Name | Duration | Deliverable |
|-------|------|----------|-------------|
| 0 | Architecture Design | 2d | Data models + manifest schema |
| 1 | Epic Planner Implementation | 3d | `epic_planner.py` + tests |
| 2 | Feature Planner Enhancement | 2d | Parent epic awareness |
| 3 | Plan Viewer HTML Generator | 4d | Glassmorphism viewers |
| 4 | Real-Time Progress Updates | 3d | Auto-refresh + JSON hooks |
| 5 | Testing & Validation | 2d | E2E tests with CORTEX-5.0 |
| 6 | Documentation & Templates | 1d | User guides + migration |

**Key Deliverables:**

1. **Epic Planner Module**
   - `src/orchestrators/planning/epic_planner.py`
   - `src/orchestrators/planning/models.py` (PlannerMode enum)
   - `detect_planner_mode()` function

2. **Epic Progress Tracking**
   - Automatic aggregation from child plans
   - Dependency validation
   - Status propagation (blocked → ready → in-progress)

3. **Static HTML Viewers**
   - `CORTEX-5.0-plan-viewer.html` (epic level)
   - `{child-plan}-plan-viewer.html` (feature level)
   - Glassmorphism-compliant design
   - Auto-refresh every 5s

4. **Manifest Updates**
   - `planning-system-5.0-manifest.yaml` extended with epic/feature modes
   - `planner_modes` configuration section
   - `html_viewer` generation rules

**Integration Points:**
- ✅ Planning Orchestrator v5 (add mode detection)
- ✅ ADO Orchestrator (epic → feature → story mapping)
- ⏭️ CORTEX-LENS (future: embed viewers in dashboard)

**Exit Criteria:**
- ✅ `detect_planner_mode(CORTEX-5.0)` returns `PlannerMode.EPIC`
- ✅ Epic HTML viewer displays all 17 child plans
- ✅ Dependency validation blocks 01-refinement until 00C reaches 50%
- ✅ Progress aggregates automatically from child JSON trackers
- ✅ All 6 phases tested with CORTEX-5.0 real structure

**Post-Completion Impact:**
- 📊 **Visibility:** Single HTML viewer shows entire epic status
- 🔄 **Automation:** No more manual progress table updates
- 🔒 **Safety:** Dependencies enforced programmatically
- 🎯 **Foundation:** All future planning benefits from epic infrastructure

---

### Phase 00C: Test Coverage Sprint (ORIGINAL 00 - 2-3 weeks)

**Now benefits from Epic infrastructure:**
- Progress automatically reflected in epic viewer
- Dependency gates for sub-plans 01-02 enforced
- Feature-level HTML viewer shows test suite growth
- JSON tracker updates real-time as tests written

**No changes to plan content**, but execution enhanced by epic tooling.

---

## 🔧 Alignment with Existing Code

### What Already Exists (Leverage These)

1. **Planning Orchestrator v5** (`src/orchestrators/planning/planning_orchestrator_v5.py`)
   - ✅ Folder structure creation
   - ✅ Phase execution framework
   - ✅ Database state tracking
   - ⚠️ **Missing:** Epic/feature mode detection
   - ⚠️ **Missing:** HTML viewer generation

2. **ADO Orchestrator** (`src/orchestrators/ado/ado_orchestrator.py`)
   - ✅ Epic → Feature → Story hierarchy (lines 1183+)
   - ✅ Work item preview formatting
   - ⚠️ **Missing:** Plan-to-ADO mapping automation

3. **Manifest System** (`cortex-brain/manifests/orchestrators/`)
   - ✅ `planning-system-5.0-manifest.yaml` exists
   - ⚠️ **Missing:** Epic/feature mode configuration
   - ⚠️ **Missing:** HTML viewer generation rules

4. **Test Infrastructure** (from Sub-Plan 00 analysis)
   - ✅ Test folder structure planned
   - ✅ Test templates designed
   - ⚠️ **Missing:** Epic-level test coverage aggregation

### What Needs to Be Built (Sub-Plan 00B Tasks)

1. **Mode Detection Logic**
   ```python
   # Add to src/orchestrators/planning/planning_orchestrator_v5.py
   
   def detect_planner_mode(plan_path: Path) -> PlannerMode:
       """Detect if plan is epic or feature based on structure."""
       master_plan = list(plan_path.glob("00-*.md"))
       child_plans = [d for d in plan_path.iterdir() 
                      if d.is_dir() and re.match(r'^\d{2}-', d.name)]
       
       if len(child_plans) >= 2 and master_plan:
           return PlannerMode.EPIC
       elif (plan_path / "context").exists():
           return PlannerMode.FEATURE
       else:
           raise ValueError(f"Cannot detect mode for {plan_path}")
   ```

2. **Epic Planner Class**
   ```python
   # NEW: src/orchestrators/planning/epic_planner.py
   
   class EpicPlanner:
       def __init__(self, epic_path: Path): ...
       def register_child_plan(self, feature: FeaturePlan): ...
       def validate_dependencies(self) -> dict: ...
       def aggregate_progress(self) -> float: ...
       def generate_epic_viewer(self): ...
   ```

3. **HTML Viewer Generator**
   ```python
   # NEW: src/orchestrators/planning/viewer_generator.py
   
   class PlanViewerGenerator:
       def generate_epic_viewer(self, epic: EpicPlan) -> Path: ...
       def generate_feature_viewer(self, feature: FeaturePlan) -> Path: ...
       def validate_glassmorphism_compliance(self, html: Path) -> bool: ...
   ```

4. **Tracking JSON Schemas**
   - `tracking/epic-progress-tracker.json` (template in vision doc lines 639-677)
   - `tracking/child-plan-registry.json`
   - `tracking/dependency-graph.json`

---

## 🎯 Recommended Action Plan

### Immediate Actions (Today - 2 hours)

1. **Fix CORTEX-5.0 Structure (Phase 00A)**
   - Move master plan to root
   - Renumber duplicate 10-* plans
   - Create tracking/ folder
   - Initialize manual JSON trackers

2. **Create Sub-Plan 00B Folder**
   ```bash
   mkdir -p "cortex-brain/documents/planning/active/CORTEX-5.0/00B-epic-feature-planner/"
   cd "00B-epic-feature-planner/"
   mkdir -p context/ artifacts/ reports/ tracking/
   ```

3. **Generate Sub-Plan 00B Master Plan**
   - Use EPIC-FEATURE-PLANNER-VISION.md as source
   - Convert design doc to executable plan format
   - Add TDD requirements (tests before implementation)

### This Week (Next 5 days)

1. **Sub-Plan 00B Phase 0-1: Architecture + Epic Planner**
   - Define data models (`PlannerMode`, `EpicPlan`, `FeaturePlan`)
   - Implement `detect_planner_mode()`
   - Write unit tests for detection logic
   - Create `EpicPlanner` class with child plan registration

### Next Week (Days 6-10)

1. **Sub-Plan 00B Phase 2-3: Feature Planner + Viewer Generator**
   - Enhance Feature Planner with parent epic awareness
   - Build `PlanViewerGenerator` class
   - Create Jinja2 templates (glassmorphism-compliant)
   - Generate first draft of CORTEX-5.0-plan-viewer.html

### Week 3 (Days 11-15)

1. **Sub-Plan 00B Phase 4-6: Integration + Testing**
   - Add real-time progress update hooks
   - End-to-end test with CORTEX-5.0
   - Documentation and user guides
   - Migration guide for existing plans

2. **Launch Sub-Plan 00C: Test Coverage Sprint**
   - Now benefits from full epic infrastructure
   - Progress visible in epic HTML viewer
   - Dependencies enforced programmatically

---

## 🚨 Critical Success Factors

### Must-Have Before Proceeding

1. **Epic Structure Valid**
   - ✅ `detect_planner_mode(CORTEX-5.0)` returns `EPIC`
   - ✅ All child plans have unique prefixes
   - ✅ Tracking folder exists with JSON schemas

2. **Epic Planner Functional**
   - ✅ Child plan registration works
   - ✅ Progress aggregation calculates correctly
   - ✅ Dependency validation blocks child plans appropriately

3. **HTML Viewers Operational**
   - ✅ Epic viewer displays all child plans
   - ✅ Feature viewer shows phases/tasks
   - ✅ Auto-refresh updates every 5s
   - ✅ Glassmorphism design standard compliance

4. **Test Coverage Adequate**
   - ✅ Unit tests for `detect_planner_mode()`
   - ✅ Unit tests for `EpicPlanner` methods
   - ✅ Integration tests with CORTEX-5.0 structure
   - ✅ E2E test of epic → feature workflow

### Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Vision too ambitious | Medium | High | MVP-first approach (6 phases, not all nice-to-haves) |
| CORTEX-5.0 structure too complex | Low | Medium | Use as real test case (if it works here, works anywhere) |
| HTML viewers break on mobile | Low | Medium | Responsive CSS + mobile testing (Phase 5) |
| Dependencies too rigid | Medium | Medium | Configurable dependency rules in JSON |

---

## 📊 Updated CORTEX-5.0 Timeline

### Original Timeline: 8-9 weeks

| Phase | Duration | Work |
|-------|----------|------|
| Sub-Plans 00-09 | 6-7w | Core features |
| Sub-Plans 10-15 | 2w | Finalization |
| **TOTAL** | **8-9w** | **130 criteria → 100% complete** |

### Refined Timeline: 10-11 weeks

| Phase | Duration | Work |
|-------|----------|------|
| **00A: Structure Cleanup** | **2h** | **Fix epic structure** |
| **00B: Epic Planner** | **2-3w** | **Foundation infrastructure** |
| 00C: Test Coverage | 2-3w | Original Sub-Plan 00 |
| 01-09: Core Features | 5-6w | Original timeline |
| 10-15: Finalization | 2w | Original timeline |
| **TOTAL** | **10-11w** | **17 sub-plans + epic infrastructure** |

**Added Time:** +2-3 weeks  
**Added Value:** 
- ✅ Epic-level visibility and control
- ✅ Automated progress tracking
- ✅ Dependency enforcement
- ✅ Reusable for ALL future multi-plan work
- ✅ Foundation for ADO integration

**ROI:** 3 weeks investment → Saves 10+ weeks across all future planning work

---

## 🎯 Alignment with SKULL Rules

### Brain Protection Compliance

| SKULL Rule | Alignment Check |
|------------|-----------------|
| **TDD_ENFORCEMENT** | ✅ Sub-Plan 00B requires tests before implementation |
| **HOLISTIC_DISCOVERY** | ✅ This analysis IS holistic discovery |
| **GIT_ISOLATION** | ✅ Epic planner stays in CORTEX repo only |
| **PLANNING_ISOLATION** | ✅ This document creates NO implementations |
| **HAND_OFF_PROTOCOL** | ✅ Vision doc is design-only (defers to 00B for execution) |

---

## 📚 References

### Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **Epic & Feature Planner Vision** | `EPIC-FEATURE-PLANNER-VISION.md` | Source design document |
| **Master Remediation Plan** | `00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md` | Current epic master plan |
| **Test Coverage Sprint** | `00-test-coverage-sprint/00-test-coverage-sprint.md` | Original Sub-Plan 00 |
| **Planning System v5 Manifest** | `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` | Current manifest |
| **Glassmorphism Standard** | `cortex-brain/documents/standards/glassmorphism-design-standard.md` | UI design requirements |

### Implementation Files to Create

```
src/orchestrators/planning/
├── epic_planner.py              # NEW - Epic orchestration
├── models.py                    # NEW - PlannerMode, EpicPlan, FeaturePlan
├── viewer_generator.py          # NEW - HTML viewer generation
└── planning_orchestrator_v5.py  # UPDATE - Add detect_planner_mode()

templates/planning/
├── epic-plan-viewer.jinja2      # NEW - Epic HTML template
└── feature-plan-viewer.jinja2   # NEW - Feature HTML template

cortex-brain/documents/planning/active/CORTEX-5.0/
├── 00-MASTER-REMEDIATION-PLAN.md       # MOVE - Up one level from subfolder
├── 00B-epic-feature-planner/           # NEW - Sub-Plan 00B
├── tracking/                           # NEW - Epic tracking folder
│   ├── epic-progress-tracker.json      # NEW
│   ├── child-plan-registry.json        # NEW
│   └── dependency-graph.json           # NEW
└── CORTEX-5.0-plan-viewer.html         # NEW - Static epic viewer
```

---

## ✅ Next Steps

### For CORTEX (AI Assistant)

**If user approves this analysis:**

1. **Execute Phase 00A (Structure Cleanup)** - 2 hours
   - Move master plan to root
   - Renumber duplicate plans
   - Create tracking infrastructure
   - Validate with `detect_planner_mode()`

2. **Generate Sub-Plan 00B** - Design → Implementation plan
   - Convert EPIC-FEATURE-PLANNER-VISION.md to executable plan
   - Use Planning v5 to create 00B-epic-feature-planner/ folder
   - Add TDD requirements and acceptance criteria

3. **Begin Sub-Plan 00B Phase 0** - Architecture Design
   - Define data models
   - Update manifest schema
   - Write first tests (TDD)

### For User (Human Decision)

**Approve or Modify:**

1. **Strategic Direction:** Agree with Epic-First approach?
2. **Timeline Trade-Off:** Accept +2-3 weeks for epic infrastructure?
3. **Priority Inversion:** Build Epic Planner before Test Coverage?
4. **Structure Changes:** OK to move/rename folders in CORTEX-5.0?

**Alternative Paths:**

- **Option A (Recommended):** Follow this analysis (Epic-First)
- **Option B (Original):** Proceed with Test Coverage Sprint (ignore epic features)
- **Option C (Hybrid):** Light epic infrastructure now, full planner later

---

**🧠 CORTEX Response Template:** `holistic_analysis`  
**Author:** Asif Hussain  
**Date:** January 4, 2026  
**Version:** 1.0.0
