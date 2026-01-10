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
├── 📋 requirements/          # Canonical sources (2 files ONLY)
│   ├── CX6-requirements.yaml
│   └── CX6-acceptance-criteria.yaml
│
├── 🚀 execution/             # Active plan execution
│   ├── config.yaml
│   ├── phases/
│   ├── tracking/
│   │   ├── progress-tracker.json
│   │   └── TODO.md
│   └── dashboard/
│       ├── index.html
│       └── app.js
│
├── 📊 analysis/              # Planning artifacts & strategies
│   ├── architecture-analysis.md
│   ├── context-discovery.md
│   ├── search-findings-*.yaml
│   └── snowball-strategy-*.yaml
│
├── 📦 artifacts/             # Generated deliverables
│   ├── CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml
│   ├── PLAN-VIEWER-DASHBOARD-PLAN.yaml
│   └── completion-reports/
│
├── 📝 summaries/             # Documentation & reports
│   ├── stage-summaries/
│   └── GAP-FIX-IMPROVEMENT-SUMMARY.md
│
└── 🗄️ archive/              # Historical artifacts
    ├── old-structure-20260110/
    ├── requirements-consolidation-2026-01-09/
    └── plans-2026-01-09/
```

---

## 📋 requirements/ - Canonical Sources

**Purpose:** Single source of truth for requirements and acceptance criteria.

**Contents:**
- `CX6-requirements.yaml` (820 lines, 18 SR, 18 DoR, 16 AD)
- `CX6-acceptance-criteria.yaml` (5,717 lines, 361 AC across 26 sections)

**Rules:**
- ✅ ONLY 2 files allowed in this folder
- ✅ All other orchestrators/tools reference these 2 files
- ❌ NO subdirectories (previously had `requirements/` subfolder - now flat)
- ❌ NO additional YAML files

**Previous Location:** `acceptance-criteria/` and `acceptance-criteria/requirements/`

---

## 🚀 execution/ - Active Plan Execution

**Purpose:** Everything needed to execute the active plan.

**Subfolders:**

### `execution/tracking/`
- `progress-tracker.json` - Machine-readable progress
- `TODO.md` - Human-readable task list
- Stage status documents

### `execution/dashboard/`
- `index.html` - Plan Viewer Dashboard
- `app.js` - Dashboard logic
- `static/` - CSS, images, assets

### `execution/phases/`
- Phase definition files
- Phase execution logs

### `execution/config.yaml`
- Plan execution configuration
- Orchestrator settings

**Previous Locations:** `plan/`, `cortex6-planner/tracking/`, `dashboard/`

---

## 📊 analysis/ - Planning Artifacts

**Purpose:** Analysis outputs from planning orchestrators.

**Contents:**
- **Architecture Analysis:** `architecture-analysis.md`
- **Context Discovery:** `context-discovery.md`
- **Gap Detection:** `search-findings-{timestamp}.yaml`
- **Snowball Strategies:** `snowball-strategy-{timestamp}.yaml`
- **Conflict Reports:** `conflict-report-{timestamp}.yaml`

**Previous Locations:** `acceptance-criteria/analysis/`, `acceptance-criteria/strategies/`, `cortex6-planner/analysis/`

---

## 📦 artifacts/ - Generated Deliverables

**Purpose:** Final outputs from orchestrators.

**Contents:**
- **Master Plan:** `CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml`
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
