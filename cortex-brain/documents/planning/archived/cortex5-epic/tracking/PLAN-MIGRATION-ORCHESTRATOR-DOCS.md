# Plan Migration Orchestrator - Documentation

**Location:** `src/orchestrators/plan_migration/plan_migration_orchestrator.py`  
**Version:** 1.1  
**Purpose:** Automate migration from Planning System v5 to v6  
**Status:** ✅ ACTIVE

---

## 🎯 Overview

The Plan Migration Orchestrator automates the transformation of plan structures from:
- **v5:** Physical phase folders (260 folders, 187 empty)
- **v6:** Logical phase definitions in feature.yaml (78 folders, 0 empty)

---

## 📊 Key Features

1. **Auto-Detection:** Identifies EPIC vs FEATURE plan types
2. **Structure Transformation:** Deletes phase folders, generates feature.yaml
3. **Root Cleanup:** Enforces 2-file root governance (CONTINUATION-PROMPT.md, plan-viewer.html)
4. **Backup Creation:** Archives original structure before changes
5. **Validation:** Verifies migration success (0 phase folders, N feature.yaml files)

---

## 🚀 Usage

### Basic Migration

```bash
# Migrate any plan (auto-detects type)
python3 src/orchestrators/plan_migration/plan_migration_orchestrator.py \
  cortex-brain/documents/planning/active/{plan-name}
```

### Example: cortex5-epic Migration

```bash
python3 src/orchestrators/plan_migration/plan_migration_orchestrator.py \
  cortex-brain/documents/planning/active/cortex5-epic
```

**Results:**
- 187 empty phase folders deleted
- 11 feature.yaml files created
- Root cleaned (2 files only)
- Backup saved to `archives/planning-migrations/`

---

## 🏗️ Architecture

### Migration Process (5 Phases)

#### Phase 1: Analysis
- Detect plan type (EPIC or FEATURE)
- Count phase folders to delete
- Identify root files requiring cleanup
- Calculate reduction metrics

#### Phase 2: Backup
- Archive original structure to `cortex-brain/archives/planning-migrations/`
- Preserve git history
- Create restore instructions

#### Phase 3: Transformation
- Delete all `phase-N/` folders (or `phase*-execution/` variants)
- Generate `feature.yaml` for each feature
- Extract phase definitions from folder structure
- Map tasks to phases (4 phases: Design, Implementation, Testing, Deployment)

#### Phase 4: Root Cleanup
- Move `.py` files → `scripts/`
- Move `.md` files (except CONTINUATION-PROMPT.md) → `reports/`
- Move `.json`/`.yaml` files → `tracking/`
- Enforce 2-file root limit

#### Phase 5: Validation
- Verify 0 phase folders remain
- Verify N feature.yaml files exist
- Verify root has exactly 2 files
- Verify all features have required subfolders

---

## 📄 feature.yaml Schema

Generated YAML structure for each feature:

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
    outputs:
      - path: analysis/design.yaml
        type: design_document

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
```

---

## 🔧 Key Methods

### `_detect_mode(plan_path: Path) -> str`
Auto-detects plan type:
- Returns `"EPIC"` if `features/` folder exists
- Returns `"FEATURE"` otherwise

### `_migrate_structure(plan_path: Path, mode: str) -> Dict`
Core migration logic:
- Deletes phase folders (v5) or phase execution folders
- Generates feature.yaml for each feature
- Returns migration statistics

### `_cleanup_root_folder(plan_path: Path, mode: str) -> Dict`
**NEW in v1.1** - Enforces root governance:
- Moves Python scripts to `scripts/`
- Moves markdown files to `reports/`
- Moves JSON/YAML to `tracking/`
- Preserves only: `CONTINUATION-PROMPT.md`, `plan-viewer.html`

### `_generate_feature_yaml(feature_path: Path) -> Dict`
Creates machine-readable phase definitions:
- 4 standard phases (Design, Implementation, Testing, Deployment)
- Task lists with IDs
- Output paths
- Progress tracking

### `_verify_migration(plan_path: Path, mode: str) -> Dict`
Validates migration success:
- Checks for 0 phase folders
- Verifies N feature.yaml files
- Confirms root file count
- Returns validation report

---

## 🛡️ Root File Governance

### Allowed at Epic Root
✅ `CONTINUATION-PROMPT.md` - Next action context  
✅ `plan-viewer.html` - Interactive navigation

### Forbidden at Epic Root
❌ Python scripts (→ `scripts/`)  
❌ Markdown files except CONTINUATION-PROMPT.md (→ `reports/`)  
❌ JSON/YAML files (→ `tracking/`)  
❌ Any other file types

---

## 📊 cortex5-epic Results

### Before (v5)
- Total Folders: 260
- Empty Phase Folders: 187 (72%)
- Root Files: 3
- Hierarchy Depth: 6 levels

### After (v6)
- Total Folders: 78 (70% reduction)
- Empty Phase Folders: 0 (100% eliminated)
- Root Files: 2 (controlled)
- Hierarchy Depth: 4 levels (33% reduction)

### Backup Location
```
cortex-brain/archives/planning-migrations/cortex5-epic-backup-20260107/
```

---

## 🔄 Rollback Instructions

If migration needs to be reversed:

```bash
# 1. Remove v6 structure
rm -rf cortex-brain/documents/planning/active/cortex5-epic

# 2. Restore v5 backup
cp -r cortex-brain/archives/planning-migrations/cortex5-epic-backup-20260107 \
  cortex-brain/documents/planning/active/cortex5-epic

# 3. Commit rollback
git add cortex-brain/documents/planning/active/cortex5-epic
git commit -m "Rollback: Restore v5 structure for cortex5-epic"
```

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| `reports/PLANNING-SYSTEM-V6-OVERVIEW.md` | Complete v6 architecture guide |
| `reports/PLANNING-SYSTEM-V6-MIGRATION-COMPLETE.md` | Migration execution report |
| `analysis/cortex5-epic-structure-simplification-proposal.md` | Original proposal |
| `analysis/planning-system-v6-folder-structures.md` | Folder structure spec |
| `CONTINUATION-PROMPT.md` | Updated continuation prompt with v6 reference |

---

## 🚀 Future Enhancements

1. **Batch Migration:** Migrate all plans in `planning/active/`
2. **Dry-Run Mode:** Preview changes without applying
3. **Interactive Mode:** User confirmation for each phase
4. **Progress Dashboard:** Real-time migration progress
5. **Manifest Registration:** Add to cortex-toolkit for user-facing commands

---

## ✅ Success Criteria

Migration considered successful when:
- ✅ Zero phase folders remain
- ✅ All features have feature.yaml
- ✅ Root has exactly 2 files
- ✅ All features have 6 subfolders (analysis, artifacts, context, reports, tracking, architecture optional)
- ✅ Backup created and verified
- ✅ Git committed with descriptive message

---

**Status:** Production-ready. Used successfully on cortex5-epic (11 features, 187 folders deleted).
