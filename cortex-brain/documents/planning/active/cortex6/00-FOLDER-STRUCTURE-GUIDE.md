# CORTEX 6.0 Folder Structure Guide

**Date:** 2026-01-11  
**Version:** 2.0.0 (Clean Reorganization)  
**Author:** Asif Hussain  
**Status:** ✅ PRODUCTION

---

## 🎯 Purpose

This document explains the **clean, intuitive folder structure** for CORTEX 6.0 planning materials. The reorganization consolidates 7 overlapping folders into 6 clear-purpose directories.

---

## 📁 Folder Structure

```
cortex6/
├── 📋 Navigation Files (root)
│   ├── 00-SOURCE-OF-TRUTH-README.md      # Primary navigation
│   ├── 00-FOLDER-STRUCTURE-GUIDE.md      # This file
│   └── QUICK-REFERENCE.md                 # Quick access guide
│
├── 📋 requirements/          # Canonical sources (SINGLE SOURCE OF TRUTH)
│   ├── CX6-requirements.yaml              # 54 KB - Strategic + Foundation + Cross-Repo
│   └── CX6-acceptance-criteria.yaml       # 304 KB - 180+ AC with DoD structure
│
├── 🚀 execution/             # Active plan execution
│   ├── config.yaml
│   ├── plan-index.yaml
│   ├── phases/
│   ├── tracking/
│   │   ├── progress-tracker.json
│   │   └── TODO.md
│   └── dashboard/
│       ├── plan-viewer.html
│       └── serve-dashboard.sh
│
├── 📦 artifacts/             # Generated deliverables
│   └── CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml  # Master execution plan
│
└── � reports/               # Operation reports & validation docs
    ├── README.md
    ├── VACUUM-REPORT-2026-01-10.md
    ├── VACUUM-OPERATION-COMPLETE.md
    ├── POST-VACUUM-VALIDATION-PLAN.md
    ├── REQUIREMENTS-VERIFICATION-REPORT.md
    └── CLEANUP-RECORD-2026-01-10.md
```

---

## 📋 requirements/ - Canonical Sources (SINGLE SOURCE OF TRUTH)

**Purpose:** Single source of truth for ALL requirements and acceptance criteria.

**Contents:**
- `CX6-requirements.yaml` (54 KB, 1,353 lines)
  - Strategic Requirements (SR-001 to SR-010)
  - Foundation Requirements (FR-001 to FR-004)
  - Cross-Repo Requirements (CR-001 to CR-005)
  - 19+ DoR decisions (Q1-Q21)
  - Zero ambiguity achieved
  
- `CX6-acceptance-criteria.yaml` (304 KB, 6,214 lines)
  - 180+ unique acceptance criteria (AC-XXX-NNN format)
  - 27 sections covering all features
  - Complete DoD structure (validation + testing + evidence)
  - Full traceability (SR→AC→Tests→Audit)

**Status:**
- ✅ DoR: 100% COMPLETE (zero ambiguity)
- ✅ DoD: 100% COMPLETE (dual evidence: test + audit)
- ✅ Can generate comprehensive plans independently
- ✅ No external references needed

**Rules:**
- ✅ ONLY 2 files allowed in this folder
- ✅ All other orchestrators/tools reference these 2 files
- ❌ NO subdirectories
- ❌ NO additional files

---

## 🚀 execution/ - Active Plan Execution

**Purpose:** Everything needed to execute the active plan.

**Subfolders:**

### `execution/tracking/`
- `progress-tracker.json` - Machine-readable progress
- `TODO.md` - Human-readable task list
- Stage status documents

### `execution/dashboard/`
- `plan-viewer.html` - Plan Viewer Dashboard  
- `serve-dashboard.sh` - Dashboard server script
- `static/` - CSS, images, assets

### `execution/phases/`
- Phase definition files (CX6-005, CX6-006, CX6-007, CX6-008)
- Phase execution logs

### `execution/config.yaml`
- Plan execution configuration
- Orchestrator settings

### `execution/plan-index.yaml`
- Master execution index
- Layer tracking and progress

---

## � artifacts/ - Generated Deliverables

**Purpose:** Master execution plan only (other artifacts archived/deleted).

**Contents:**
- **Master Plan:** `CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml` (1,403 lines)
  - 5-stage snowball remediation strategy
  - 210-288 hours estimated effort
  - Complete phase definitions
  - Acceptance criteria traceability

---

## 📊 reports/ - Operation Reports

**Purpose:** Historical operation reports and validation documentation.

**Contents:**
- `README.md` - Report index and summary
- `VACUUM-REPORT-2026-01-10.md` - Vacuum cleanup details
- `VACUUM-OPERATION-COMPLETE.md` - Success summary
- `POST-VACUUM-VALIDATION-PLAN.md` - Validation tests and recovery
- `REQUIREMENTS-VERIFICATION-REPORT.md` - DoR/DoD verification
- `CLEANUP-RECORD-2026-01-10.md` - Git commit references

**Git References:**
- Vacuum: `3f9b037b4`
- Verification: `5365c3277`
- Final cleanup: `9e92e54c8`

---

## 🗑️ Deleted Folders (No Unique Requirements)

### analysis/ (DELETED 2026-01-10)
- Historical analysis captured in requirements
- Recovery: `git checkout 5365c3277 -- cortex-brain/documents/planning/active/cortex6/analysis/`

### summaries/ (DELETED 2026-01-10)
- Session notes with no unique requirements  
- Recovery: `git checkout 5365c3277 -- cortex-brain/documents/planning/active/cortex6/summaries/`

### archive/ (DELETED 2026-01-10)
- Historical artifacts from pre-vacuum state
- Recovery: `git checkout c705c950f -- cortex-brain/documents/planning/active/cortex6/archive/`
- **Dashboard Plan:** `PLAN-VIEWER-DASHBOARD-PLAN.yaml`
- **Completion Reports:** `completion-reports/`

**Previous Locations:** `artifacts/`, `cortex6-planner/artifacts/`

---

## 📝 summaries/ - Documentation

**Purpose:** Human-readable documentation and summaries.

**Contents:**
- **Stage Summaries:** `stage-summaries/`
- **Improvement Reports:** `GAP-FIX-IMPROVEMENT-SUMMARY.md`
- **Decision Documents:** Stage decisions, consolidation summaries

**Previous Locations:** `acceptance-criteria/summaries/`, `cortex6-planner/summaries/`, root `tracking/`

---

## 🗄️ archive/ - Historical Artifacts

**Purpose:** Preserve old structures and historical artifacts.

**Contents:**
- `old-structure-20260110/` - Pre-reorganization backup
- `requirements-consolidation-2026-01-09/` - Old requirements consolidation
- `plans-2026-01-09/` - Archived plans

**Rules:**
- ✅ Never delete archived content (audit trail)
- ✅ Timestamp all archive folders
- ✅ Move old structures here during reorganizations

**Previous Location:** `archive/`

---

## 🔄 Migration Summary

### Before (7 folders)
```
cortex6/
├── acceptance-criteria/      # Mixed requirements + analysis
├── cortex6-planner/          # Duplicate tracking + artifacts
├── plan/                     # Phases + config
├── dashboard/                # Separate dashboard
├── tracking/                 # Orphaned root tracking
├── artifacts/                # Duplicate artifacts
└── analysis/                 # Orphaned analysis
```

### After (6 folders)
```
cortex6/
├── requirements/             # Canonical sources (2 files)
├── execution/                # Active plan execution
├── analysis/                 # Planning artifacts
├── artifacts/                # Generated deliverables
├── summaries/                # Documentation
└── archive/                  # Historical artifacts
```

### Improvements
- ✅ **Canonical sources** in obvious location (`requirements/`)
- ✅ **Execution files** consolidated (`execution/`)
- ✅ **No overlapping folders** (tracking, artifacts, analysis unified)
- ✅ **Clear purpose** for each folder
- ✅ **Easy navigation** - intuitive structure

---

## 📍 Path Reference Table

| Old Path | New Path |
|----------|----------|
| `acceptance-criteria/CX6-acceptance-criteria.yaml` | `requirements/CX6-acceptance-criteria.yaml` |
| `acceptance-criteria/requirements/CX6-requirements.yaml` | `requirements/CX6-requirements.yaml` |
| `cortex6-planner/tracking/progress-tracker.json` | `execution/tracking/progress-tracker.json` |
| `plan/config.yaml` | `execution/config.yaml` |
| `plan/phases/` | `execution/phases/` |
| `dashboard/` | `execution/dashboard/` |
| `acceptance-criteria/analysis/` | `analysis/` |
| `acceptance-criteria/strategies/` | `analysis/` |
| `acceptance-criteria/search-findings-*.yaml` | `analysis/search-findings-*.yaml` |
| `cortex6-planner/artifacts/` | `artifacts/` |
| `acceptance-criteria/summaries/` | `summaries/` |

---

## 🛡️ Updated References

**Files Updated:**
1. ✅ `.github/prompts/cortex-gap-fix.prompt.md` - All path references
2. ✅ `src/orchestrators/gap_fix/gap_fix_orchestrator.py` - Canonical source loading
3. ✅ `tests/orchestrators/test_gap_fix_orchestrator.py` - Test fixtures
4. ✅ This README

**Test Status:** ✅ 12/12 Gap-Fix tests passing with new structure

---

## 📖 Navigation Quick Start

### Finding Canonical Sources
```bash
cd cortex-brain/documents/planning/active/cortex6/requirements
ls -la
# CX6-requirements.yaml
# CX6-acceptance-criteria.yaml
```

### Checking Progress
```bash
cd cortex-brain/documents/planning/active/cortex6/execution/tracking
cat progress-tracker.json
```

### Running Dashboard
```bash
cd cortex-brain/documents/planning/active/cortex6/execution/dashboard
python3 -m http.server 8000
# Open http://localhost:8000
```

### Viewing Analysis
```bash
cd cortex-brain/documents/planning/active/cortex6/analysis
ls -la *.yaml
```

---

## 🔍 Verification Commands

### Structure Check
```bash
cd cortex-brain/documents/planning/active/cortex6
find . -maxdepth 1 -type d | sort
```

**Expected Output:**
```
./analysis
./archive
./artifacts
./execution
./requirements
./summaries
```

### Canonical Sources Check
```bash
ls -la requirements/
```

**Expected Output:**
```
CX6-acceptance-criteria.yaml (282 KB)
CX6-requirements.yaml (33 KB)
```

### Execution Files Check
```bash
ls -la execution/
```

**Expected Output:**
```
config.yaml
dashboard/
phases/
tracking/
```

---

## 🚀 Next Steps

1. ✅ Folder structure reorganized
2. ✅ All references updated
3. ✅ Tests passing
4. ⏳ Proceed to Layer 4: AC-ID Traceability

---

**Backup Location:** `../cortex6-backup-20260110-055010`  
**Reorganization Script:** `REORGANIZE-CORTEX6-STRUCTURE.sh`  
**Test Coverage:** 12/12 Gap-Fix tests passing

---

**Last Updated:** 2026-01-11T06:00:00Z  
**Author:** CORTEX Gap-Fix Orchestrator
