# CORTEX 6.0 Plan Structure Comparison

**Date:** 2026-01-09  
**Analysis:** Current cortex6-planner vs Correct Epic Structure

---

## ❌ CURRENT STRUCTURE (INCORRECT)

```
cortex6-planner/
├── 00-cortex6-complete-build.md              # Flat root-level plan file
├── CX6-comprehensive-remediation-plan.yaml   # Flat remediation plan
├── HOLISTIC-REVIEW-2026-01-09.md
├── RESTORATION-SUMMARY.md
├── GAP-FIX-COMPLETION-SUMMARY.md
├── PLAN-UPDATE-SUMMARY-20260109.md
├── search-findings-20260109.yaml
├── analysis/                                  # Analysis folder (OK)
│   └── AUDIT-001-Analysis-Summary.md
├── artifacts/                                 # Empty artifacts folder
├── context/                                   # Empty context folder
├── foundation/                                # Foundation docs (mixed purpose)
│   ├── AUDIT-001-Quick-Reference.md
│   ├── AUDIT-001-Refactoring-Plan.md
│   ├── AUDIT-001-Workflow-Diagram.md
│   └── INVESTIGATION-REPORT-20260109.yaml
└── tracking/                                  # Tracking folder (OK)
    ├── CONSOLIDATION-SUMMARY-2026-01-09.md
    ├── effort-log.md
    ├── progress-tracker.json
    └── stage1-status.md
```

**Issues:**
- ❌ **NO `features/` folder** - Core epic organization missing
- ❌ **Flat file structure** - No feature isolation
- ❌ **No `feature.yaml` files** - Missing YAML-based phase/task tracking
- ❌ **Mixed content types** - Analysis, foundation, remediation all at root
- ❌ **No context/ per feature** - Context files not organized by feature
- ❌ **No phases/ structure** - Phase-based tracking absent

---

## ✅ CORRECT STRUCTURE (Epic Planning System v6)

```
cortex5-epic/                                  # Example from git commit 4b906347e
├── CONTINUATION-PROMPT.md                     # Root-level continuation prompt
├── plan-viewer.html                           # Interactive viewer
├── launch_plan_viewer.py                      # Launcher script
├── features/                                  # ✅ FEATURES FOLDER (REQUIRED)
│   ├── feat01-continuation-system/
│   │   ├── feature.yaml                       # ✅ YAML tracker (phases, tasks, deps)
│   │   └── context/
│   │       └── continuation-system.md         # Feature context docs
│   ├── feat02-goal-detection/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── goal-detection.md
│   ├── feat03-goal-inheritance/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── goal-inheritance.md
│   ├── feat04-governance-rules/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── governance-rules.md
│   ├── feat05-knowledge-integration/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── knowledge-integration.md
│   ├── feat06-plan-viewer/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── plan-viewer.md
│   ├── feat07-planning-system/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── planning-system.md
│   ├── feat08-planning-system-core/
│   │   ├── feature.yaml
│   │   └── tracking/
│   │       └── progress-tracker.json          # Per-feature progress
│   ├── feat09-response-templates/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── response-templates.md
│   ├── feat10-testing-framework/
│   │   ├── feature.yaml
│   │   └── context/
│   │       └── testing-framework.md
│   └── feat11-toolkit-orchestration/
│       ├── feature.yaml
│       └── context/
│           └── toolkit-orchestration.md
├── analysis/                                  # Epic-level analysis
├── artifacts/                                 # Epic-level artifacts
├── reports/                                   # Epic-level reports
└── tracking/                                  # Epic-level tracking
    ├── progress-tracker.json                  # Overall epic progress
    ├── plan-data.yaml
    └── snowball.md
```

**Key Features:**
- ✅ **`features/` folder** - All features organized under one parent
- ✅ **`feat##-{name}/` naming** - Consistent feature identification
- ✅ **`feature.yaml` per feature** - YAML-based phase/task/dependency tracking
- ✅ **`context/` per feature** - Feature-specific documentation
- ✅ **`tracking/` per feature** - Optional per-feature progress tracking
- ✅ **`phases/` structure** - Defined in `feature.yaml` (not as folders)
- ✅ **Clear separation** - Features isolated, epic-level folders for shared content

---

## 📊 Feature.yaml Structure

**Example from `feat01-continuation-system/feature.yaml`:**

```yaml
feature_id: feat01-continuation-system
feature_name: 'Feature: Cross-Session Continuation'
epic_id: cortex5-epic
priority: P2_MEDIUM
status: NOT_STARTED
progress: 0
metadata:
  created_date: '2026-01-07'
  last_updated: '2026-01-07T09:50:16.072219'
  estimated_weeks: 2
  actual_weeks: 0
dependencies: {}
phases:
  - phase: 1
    name: Design & Architecture
    status: NOT_STARTED
    progress: 0
    estimated_hours: 8
    tasks:
      - id: task-1.1
        name: Design system architecture
        status: NOT_STARTED
      - id: task-1.2
        name: Design data models
        status: NOT_STARTED
      - id: task-1.3
        name: Design API interfaces
        status: NOT_STARTED
    outputs:
      - path: analysis/design.yaml
        type: design_document
      - path: architecture/components.yaml
        type: architecture
  - phase: 2
    name: Implementation
    status: NOT_STARTED
    progress: 0
    estimated_hours: 16
    tasks:
      - id: task-2.1
        name: Implement core logic
        status: NOT_STARTED
        test_required: true
      - id: task-2.2
        name: Implement data layer
        status: NOT_STARTED
        test_required: true
      - id: task-2.3
        name: Implement API endpoints
        status: NOT_STARTED
        test_required: true
    outputs:
      - path: artifacts/feat01_continuation_system.py
        type: implementation
  - phase: 3
    name: Testing
    status: NOT_STARTED
    progress: 0
    estimated_hours: 8
    tasks:
      - id: task-3.1
        name: Unit tests
        status: NOT_STARTED
      - id: task-3.2
        name: Integration tests
        status: NOT_STARTED
      - id: task-3.3
        name: System tests
        status: NOT_STARTED
    outputs:
      - path: artifacts/test_feat01_continuation_system.py
        type: test_suite
      - path: reports/test-results.yaml
        type: test_report
  - phase: 4
    name: Documentation & Deployment
    status: NOT_STARTED
    progress: 0
    estimated_hours: 4
    tasks:
      - id: task-4.1
        name: Write documentation
        status: NOT_STARTED
      - id: task-4.2
        name: Create deployment guide
        status: NOT_STARTED
      - id: task-4.3
        name: Deploy to production
        status: NOT_STARTED
    outputs:
      - path: reports/feat01-continuation-system-guide.md
        type: documentation
      - path: reports/deployment-report.yaml
        type: deployment_log
artifacts:
  design: []
  implementation: []
  tests: []
  documentation: []
progress_summary:
  phases_total: 4
  phases_completed: 0
  phases_in_progress: 0
  phases_not_started: 4
  tasks_total: 12
  tasks_completed: 0
  tasks_in_progress: 0
  tasks_not_started: 12
context_files:
  - context/continuation-system.md
```

---

## 🔄 Required Transformation

**Current State:**
- `cortex-brain/documents/planning/active/cortex6/cortex6-planner/` (flat structure)

**Target State:**
- `cortex-brain/documents/planning/active/cortex6/cortex6-planner/features/` (epic structure)

**Actions Required:**

1. **Create `features/` folder** under `cortex6-planner/`
2. **Identify CORTEX 6.0 features** from acceptance criteria and master plan
3. **Create `feat##-{name}/` folders** for each feature
4. **Generate `feature.yaml`** for each feature with:
   - Phases (Design, Implementation, Testing, Documentation)
   - Tasks per phase
   - Dependencies
   - Progress tracking
   - Outputs (artifacts, reports, tests)
5. **Migrate context docs** to `features/feat##-{name}/context/`
6. **Reorganize root-level files** (move analysis, foundation to appropriate locations)
7. **Update tracking files** to reference feature-based structure

---

## 📋 CORTEX 6.0 Features (From Acceptance Criteria)

**Preliminary Feature List** (needs validation against `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml`):

1. **feat01-epic-review-orchestrator** - Health metrics, progress tracking, gap detection
2. **feat02-gap-fix-orchestrator** - Search + align unified workflow
3. **feat03-autonomous-execution** - 100% Python-based orchestration
4. **feat04-planning-system-v5** - YAML-first, DAG-based planning
5. **feat05-response-templates-v4** - INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE
6. **feat06-brain-protection-skull** - 61 governance rules
7. **feat07-todo-orchestrator** - DAG management, dependency resolution
8. **feat08-master-orchestrator** - Intent routing, LLM classification
9. **feat09-vision-api-integration** - Image analysis middleware
10. **feat10-accessibility-wcag** - Cognitive load, concise output, visual progress
11. **feat11-tdd-enforcement** - RED→GREEN→REFACTOR mandatory
12. **feat12-audit-logging** - Comprehensive activity tracking

---

## 🎯 Next Steps

1. **Validate feature list** against CORTEX 6.0 master source of truth
2. **Generate feature.yaml templates** for each identified feature
3. **Restore `features/` folder structure** in `cortex6-planner/`
4. **Migrate existing content** to appropriate feature folders
5. **Update progress tracking** to use feature-based metrics
6. **Generate plan-viewer.html** for CORTEX 6.0 epic visualization

---

**Reference Commits:**
- `4b906347e` - "✅ Migrated cortex5-epic from Planning System v5 to v6"
- `d71024e4c` - "feat(plan-converter): Enforce feat0X- and phase1- naming conventions"
- `0f4034ff4` - "feat(AC): Consolidate CORTEX 6.0 Acceptance Criteria to canonical location (v8.0.0)"

**Source Folder:**
- `cortex-brain/documents/planning/archived/cortex5-epic/` (git commit 4b906347e)

**Target Folder:**
- `cortex-brain/documents/planning/active/cortex6/cortex6-planner/features/`
