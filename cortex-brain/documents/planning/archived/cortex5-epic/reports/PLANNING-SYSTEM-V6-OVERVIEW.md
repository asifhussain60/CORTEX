# Planning System v6 - Architecture & Migration Guide

**Epic:** cortex5-epic  
**Document Type:** Architecture Overview  
**Created:** 2026-01-07  
**Status:** ✅ ACTIVE (Migration Complete)

---

## 🎯 Overview

Planning System v6 represents a fundamental shift from **physical phase folders** to **logical phase definitions** within YAML files. This eliminates 70% of folder overhead while preserving 100% of functionality.

---

## 📊 Key Improvements

| Metric | v5 (Phase Folders) | v6 (feature.yaml) | Improvement |
|--------|-------------------|-------------------|-------------|
| **Total Folders** | 260 | 78 | 70% reduction |
| **Empty Folders** | 187 (72%) | 0 (0%) | 100% elimination |
| **Phase Definitions** | Implicit (folder structure) | Explicit (YAML) | Machine-readable |
| **Hierarchy Depth** | 6 levels | 4 levels | 33% reduction |
| **Root Files** | Unlimited | 2 (controlled) | Enforced governance |

---

## 🏗️ Architecture

### v5 Structure (DEPRECATED)

```
cortex5-epic/
├── features/
│   └── feat01-continuation-system/
│       ├── analysis/
│       ├── artifacts/
│       ├── context/
│       ├── reports/
│       ├── tracking/
│       ├── phase-0/               ❌ Empty (0 bytes)
│       │   ├── analysis/
│       │   ├── artifacts/
│       │   └── reports/
│       ├── phase-1/               ❌ Empty (0 bytes)
│       ├── phase-2/               ❌ Empty (0 bytes)
│       └── phase-3/               ❌ Empty (0 bytes)
```

**Problems:**
- 187 empty phase folders (0 bytes wasted)
- Phase structure implicit (folder names)
- 6-level deep hierarchy
- No machine-readable phase definitions
- Root files uncontrolled (scripts, markdown, JSON)

### v6 Structure (CURRENT)

```
cortex5-epic/
├── CONTINUATION-PROMPT.md         ✅ Root file (allowed)
├── plan-viewer.html               ✅ Root file (allowed)
├── analysis/                      ✅ Epic-level analysis
├── architecture/                  ✅ Epic-level architecture
├── artifacts/                     ✅ Epic-level artifacts
├── context/                       ✅ Epic-level context
├── reports/                       ✅ Epic-level reports
├── scripts/                       ✅ Epic-level scripts
│   └── launch_plan_viewer.py      ✅ Moved from root
├── tracking/                      ✅ Epic-level tracking
└── features/
    └── feat01-continuation-system/
        ├── feature.yaml           ✅ Machine-readable phases
        ├── analysis/              ✅ Feature-level analysis
        ├── artifacts/             ✅ Feature-level artifacts
        ├── context/               ✅ Feature-level context
        ├── reports/               ✅ Feature-level reports
        └── tracking/              ✅ Feature-level tracking
```

**Benefits:**
- Zero empty folders
- Explicit phase definitions in YAML
- 4-level hierarchy
- Machine-readable (automation-friendly)
- Root files strictly controlled (governance)

---

## 📄 feature.yaml Schema

Each feature contains a `feature.yaml` file with explicit phase definitions:

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
    outputs:
      - path: artifacts/test_feat01_continuation_system.py
        type: test_suite

  - phase: 4
    name: Documentation & Deployment
    status: NOT_STARTED
    progress: 0
    estimated_hours: 4
    tasks:
      - id: task-4.1
        name: Write documentation
        status: NOT_STARTED
    outputs:
      - path: reports/feat01-continuation-system-guide.md
        type: documentation

artifacts:
  design: []
  implementation: []
  tests: []
  documentation: []
```

---

## 🔧 Plan Migration Orchestrator

### Purpose

Automates migration from Planning System v5 (phase folders) to v6 (feature.yaml).

**Location:** `src/orchestrators/plan_migration/plan_migration_orchestrator.py`

### Key Features

1. **Auto-Detection:** Identifies EPIC vs FEATURE plan types
2. **Structure Transformation:** Deletes phase folders, generates feature.yaml
3. **Root Cleanup:** Moves scripts to `scripts/`, markdown to `reports/`, JSON/YAML to `tracking/`
4. **Backup Creation:** Archives original structure to `cortex-brain/archives/planning-migrations/`
5. **Validation:** Verifies 0 phase folders, N feature.yaml files

### Usage

```bash
# Migrate a plan (auto-detects type)
python3 src/orchestrators/plan_migration/plan_migration_orchestrator.py \
  cortex-brain/documents/planning/active/cortex5-epic

# Result:
# - 187 empty phase folders deleted
# - 11 feature.yaml files created
# - Root cleaned (only CONTINUATION-PROMPT.md and plan-viewer.html remain)
# - Backup saved to archives/planning-migrations/
```

### Migration Process

#### Phase 1: Analysis
- Detect plan type (EPIC or FEATURE)
- Count phase folders
- Identify root files requiring cleanup
- Calculate reduction metrics

#### Phase 2: Backup
- Archive original structure
- Preserve git history
- Create restore instructions

#### Phase 3: Transformation
- Delete all `phase-N/` folders
- Generate `feature.yaml` for each feature
- Extract phase definitions from folder structure
- Map tasks to phases

#### Phase 4: Root Cleanup
- Move `.py` files → `scripts/`
- Move `.md` files (except CONTINUATION-PROMPT.md) → `reports/`
- Move `.json`/`.yaml` files → `tracking/`
- Keep only 2 allowed root files

#### Phase 5: Validation
- Verify 0 phase folders remain
- Verify N feature.yaml files exist (N = feature count)
- Verify root has exactly 2 files
- Verify all features have 6 subfolders

### Migration Orchestrator Methods

```python
class PlanMigrationOrchestrator:
    def _detect_mode(self, plan_path: Path) -> str:
        """Auto-detect EPIC vs FEATURE plan type"""
        
    def _migrate_structure(self, plan_path: Path, mode: str) -> Dict:
        """Delete phase folders, generate feature.yaml"""
        
    def _cleanup_root_folder(self, plan_path: Path, mode: str) -> Dict:
        """Enforce root file rules (NEW in v1.1)"""
        
    def _generate_feature_yaml(self, feature_path: Path) -> Dict:
        """Create machine-readable phase definitions"""
        
    def _verify_migration(self, plan_path: Path, mode: str) -> Dict:
        """Validate migration success"""
```

---

## 🛡️ Root File Governance

**ALLOWED at Epic Root:**
- `CONTINUATION-PROMPT.md` - Next action context
- `plan-viewer.html` - Interactive navigation

**FORBIDDEN at Epic Root:**
- Python scripts (→ `scripts/`)
- Markdown files except CONTINUATION-PROMPT.md (→ `reports/`)
- JSON/YAML files (→ `tracking/`)
- Any other file types

**Enforcement:** `_cleanup_root_folder()` method in migration orchestrator

---

## 📊 cortex5-epic Migration Results

### Before (v5)
- **Total Folders:** 260
- **Empty Phase Folders:** 187 (72%)
- **Root Files:** 3 (CONTINUATION-PROMPT.md, plan-viewer.html, launch_plan_viewer.py)
- **Features:** 11
- **Hierarchy Depth:** 6 levels

### After (v6)
- **Total Folders:** 78 (70% reduction)
- **Empty Phase Folders:** 0 (100% eliminated)
- **Root Files:** 2 (CONTINUATION-PROMPT.md, plan-viewer.html)
- **Features:** 11 (unchanged)
- **Hierarchy Depth:** 4 levels (33% reduction)

### Phase Definitions
- **v5:** Implicit (folder names `phase-0/`, `phase-1/`, etc.)
- **v6:** Explicit (YAML with task lists, outputs, estimates)

### Backup
- **Location:** `cortex-brain/archives/planning-migrations/cortex5-epic-backup-20260107/`
- **Size:** ~2.5MB (includes all original folders)
- **Restoration:** Copy backup contents back to replace current structure

---

## 🎯 When to Use Each System

### Use v5 (Phase Folders) - DEPRECATED
❌ Never use v5 - migrate existing plans to v6

### Use v6 (feature.yaml) - CURRENT
✅ All new plans  
✅ All epic plans  
✅ All feature plans  
✅ Machine-readable automation  
✅ Clean folder hierarchy  

---

## 🔄 Migration Checklist

- [ ] **Backup:** Verify backup exists in `archives/planning-migrations/`
- [ ] **Phase Folders:** Verify 0 phase folders remain
- [ ] **feature.yaml:** Verify all features have `feature.yaml`
- [ ] **Root Cleanup:** Verify only 2 root files
- [ ] **Scripts:** Verify scripts moved to `scripts/`
- [ ] **Validation:** Run migration verification
- [ ] **Git Commit:** Commit migration with descriptive message
- [ ] **Testing:** Verify plan viewer still works

---

## 📚 Related Documents

- **Simplification Proposal:** `cortex-brain/documents/analysis/cortex5-epic-structure-simplification-proposal.md`
- **Visual Comparison:** `cortex-brain/documents/analysis/cortex5-epic-structure-visual-comparison.md`
- **v6 Folder Structures:** `cortex-brain/documents/analysis/planning-system-v6-folder-structures.md`
- **Quick Reference:** `cortex-brain/documents/analysis/QUICK-REF-epic-vs-feature-structures.md`
- **Migration Complete Report:** `cortex-brain/documents/planning/active/cortex5-epic/reports/PLANNING-SYSTEM-V6-MIGRATION-COMPLETE.md`

---

## 🚀 Future Enhancements

1. **Planning Orchestrator v6 Integration**
   - Update to generate v6 structures by default
   - Remove phase folder creation logic
   - Add root cleanup to plan generation

2. **Manifest Registration**
   - Create `plan-migration-orchestrator.yaml` manifest
   - Register with cortex-toolkit
   - Enable user-facing migration commands

3. **Batch Migration Tool**
   - Migrate all plans in `planning/active/`
   - Parallel execution support
   - Progress tracking dashboard

4. **Validation Dashboard**
   - Real-time structure validation
   - Compliance scoring
   - Drift detection alerts

---

## ✅ Conclusion

Planning System v6 achieves:
- ✅ 70% folder reduction (260 → 78)
- ✅ 100% empty folder elimination (187 → 0)
- ✅ Explicit machine-readable phase definitions
- ✅ Enforced root file governance
- ✅ Simplified 4-level hierarchy
- ✅ Automated migration tooling

**Status:** cortex5-epic fully migrated and validated.
