# CORTEX 6.0 Planning - Single Source of Truth

**Date:** 2026-01-10  
**Version:** 2.0.0  
**Status:** ✅ PRODUCTION (Clean Structure)

---

## 🎯 Quick Start

```bash
# View requirements (SINGLE SOURCE OF TRUTH)
cat requirements/CX6-requirements.yaml
cat requirements/CX6-acceptance-criteria.yaml

# View execution plan
cat artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml

# Launch dashboard (interactive)
cd execution/dashboard/
./serve-dashboard.sh

# View current phase
cat execution/phases/CX6-005-ac-traceability.yaml

# Check progress
cat execution/tracking/TODO.md
cat execution/tracking/progress-tracker.json
```

---

## 📁 Folder Structure

```
cortex6/
│
├── README.md                          ← YOU ARE HERE
│
├── requirements/                      ← 📋 SINGLE SOURCE OF TRUTH
│   ├── CX6-requirements.yaml         (54 KB, 1,353 lines)
│   │   • Strategic Requirements (SR-001 to SR-010)
│   │   • Foundation Requirements (FR-001 to FR-004)
│   │   • Cross-Repo Requirements (CR-001 to CR-005)
│   │   • 19+ DoR decisions (Q1-Q21)
│   │   • DoR Status: 100% COMPLETE (zero ambiguity)
│   │
│   └── CX6-acceptance-criteria.yaml  (304 KB, 6,214 lines)
│       • 180+ acceptance criteria (AC-XXX-NNN format)
│       • 27 sections covering all features
│       • DoD: 100% COMPLETE (validation + testing + evidence)
│       • Full traceability: SR→AC→Tests→Audit
│
├── execution/                         ← 🚀 ACTIVE PLAN EXECUTION
│   ├── config.yaml                    (Plan execution config)
│   ├── plan-index.yaml                (Master execution index)
│   │
│   ├── phases/                        (Phase definitions)
│   │   ├── CX6-005-ac-traceability.yaml   🔄 IN_PROGRESS
│   │   ├── CX6-006-dashboard.yaml         ⏸️ PENDING
│   │   ├── CX6-007-migrate.yaml           ⏸️ PENDING
│   │   └── CX6-008-cross-repo.yaml        ⏸️ PENDING
│   │
│   ├── tracking/                      (Progress tracking)
│   │   ├── progress-tracker.json      (Machine-readable)
│   │   ├── TODO.md                    (Human-readable)
│   │   └── stage-*.md                 (Stage status)
│   │
│   └── dashboard/                     (Interactive viewer)
│       ├── plan-viewer.html           (Dashboard UI)
│       ├── serve-dashboard.sh         (Server script)
│       └── static/                    (CSS, images)
│
├── artifacts/                         ← 📦 GENERATED DELIVERABLES
│   └── CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml
│       • 1,403 lines master execution plan
│       • 5-stage snowball remediation strategy
│       • 210-288 hours estimated effort
│       • Complete phase definitions
│       • Acceptance criteria traceability
│
└── reports/                           ← 📊 OPERATION DOCUMENTATION
    ├── README.md                      (Report index)
    ├── VACUUM-REPORT-2026-01-10.md    (Cleanup details)
    ├── VACUUM-OPERATION-COMPLETE.md   (Success summary)
    ├── POST-VACUUM-VALIDATION-PLAN.md (Validation tests)
    ├── REQUIREMENTS-VERIFICATION-REPORT.md (DoR/DoD verification)
    ├── CLEANUP-RECORD-2026-01-10.md   (Git commit references)
    └── ROOT-CLEANUP-2026-01-10.md     (Root organization)
```

---

## 📋 Requirements Folder - Canonical Sources

**Purpose:** Single source of truth for ALL requirements and acceptance criteria.

### File 1: `CX6-requirements.yaml`
- **Size:** 54 KB (1,353 lines)
- **Version:** 1.0.0
- **Status:** FINALIZED
- **DoR Status:** 100% COMPLETE

**Contents:**
- **Strategic Requirements** (SR-001 to SR-010)
  - Memory layers, orchestrators, governance, TDD enforcement
- **Foundation Requirements** (FR-001 to FR-004)
  - Audit logging, state management, pattern routing
- **Cross-Repo Requirements** (CR-001 to CR-005)
  - Multi-repo support, discovery, sanitization
- **DoR Decisions** (19+ decisions: Q1-Q21)
  - All architectural ambiguities resolved
  - Decision rationale documented

### File 2: `CX6-acceptance-criteria.yaml`
- **Size:** 304 KB (6,214 lines)
- **Version:** 16.1.0+
- **Status:** AUTHORITATIVE
- **Total Criteria:** 180+ unique AC across 27 sections

**Structure (per AC):**
```yaml
- id: AC-XXX-NNN
  criterion: "What to build"
  acceptance: "How to validate"
  validation: "Acceptance criteria"
  test_file: "Path to test file"
  status: "NOT_STARTED | IN_PROGRESS | COMPLETE"
```

**Key Governance:**
- **AC-GOV-011:** TDD-Master required for ALL development (CORE-019)
- **AC-TDD-MASTER-000:** Supports unplanned mode (lightweight TDD)

---

## 🚀 Execution Folder - Active Work

### Master Index: `plan-index.yaml`
Tracks 5-layer snowball remediation:
- **Layer 0:** Foundation (audit logger, state manager, pattern router)
- **Layer 1:** Classic orchestrators (cleanup, investigation, etc.)
- **Layer 2:** Governance (SKULL, TODO, validation)
- **Layer 3:** TDD enforcement (TDD-Master orchestrator)
- **Layer 4:** AC traceability ← **CURRENT**
- **Layer 5:** Dashboard + migrate

### Phase Files: `phases/CX6-00X-*.yaml`
Detailed execution plans for each phase:
- Task breakdown
- Acceptance criteria mapping
- Time estimates
- Dependencies
- Success criteria

### Tracking
- **`progress-tracker.json`**: Machine-readable progress (automation)
- **`TODO.md`**: Human-readable task list (development)
- **Stage files**: Status documents per stage

### Dashboard
- **Interactive HTML viewer** for plan visualization
- **Local server** (`serve-dashboard.sh`) for browsing
- **Real-time progress** updates

---

## 📦 Artifacts Folder - Master Plan

### `CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml`
**1,403 lines** of comprehensive execution strategy:

**Contents:**
- **Metadata:** Project info, version, status
- **5-Stage Snowball Strategy:** Layer-by-layer remediation
- **Complete Phase Definitions:** CX6-001 through CX6-008
- **Time Estimates:** 210-288 hours total effort
- **AC Traceability:** Maps all 180+ criteria to phases
- **Dependencies:** Cross-phase dependency graph
- **Success Criteria:** Per-phase validation

---

## 📊 Reports Folder - Operation History

Historical documentation of cleanup and validation operations:

| Report | Purpose |
|--------|---------|
| **VACUUM-REPORT-2026-01-10.md** | Detailed cleanup results (23 files deleted, 54% reduction) |
| **VACUUM-OPERATION-COMPLETE.md** | Success summary and final state |
| **POST-VACUUM-VALIDATION-PLAN.md** | 12-point validation test plan |
| **REQUIREMENTS-VERIFICATION-REPORT.md** | DoR/DoD 100% completeness confirmation |
| **CLEANUP-RECORD-2026-01-10.md** | Git commit references for recovery |
| **ROOT-CLEANUP-2026-01-10.md** | Root folder organization details |

**Git Recovery References:**
- Vacuum cleanup: `3f9b037b4`
- Requirements verification: `5365c3277`
- Final cleanup: `9e92e54c8`
- Root cleanup: `a23584db3`

---

## 🗑️ Deleted Folders (Zero Unique Content)

The following folders were deleted after verification they contained no unique requirements:

| Folder | Deleted | Recovery Commit | Recovery Command |
|--------|---------|-----------------|------------------|
| `analysis/` | 2026-01-10 | `5365c3277` | `git checkout 5365c3277 -- cortex-brain/documents/planning/active/cortex6/analysis/` |
| `summaries/` | 2026-01-10 | `5365c3277` | `git checkout 5365c3277 -- cortex-brain/documents/planning/active/cortex6/summaries/` |
| `archive/` | 2026-01-10 | `c705c950f` | `git checkout c705c950f -- cortex-brain/documents/planning/active/cortex6/archive/` |

**Justification:** All deleted content captured in `requirements/` folder. DoR: 100% COMPLETE, DoD: 100% COMPLETE.

---

## ✅ Validation Status

### Requirements Completeness
- ✅ **DoR: 100% COMPLETE** - Zero ambiguity achieved
- ✅ **DoD: 100% COMPLETE** - Dual evidence structure (test + audit)
- ✅ **Traceability: FULL** - SR→AC→Tests→Audit mapping
- ✅ **Independent Planning: YES** - Can generate comprehensive plans

### Folder Organization
- ✅ **Root:** Clean navigation (1 README only)
- ✅ **requirements/:** 2 canonical YAML files only
- ✅ **execution/:** Active execution state preserved
- ✅ **artifacts/:** Master plan only
- ✅ **reports/:** Historical documentation archived

### Git Status
- ✅ **Branch:** CORTEX-5.5
- ✅ **Remote:** All changes pushed to origin
- ✅ **Recovery:** Git history preserved for all deleted content

---

## 🎯 Usage Guidelines

### For Planning Orchestrator
```bash
# Read canonical requirements
requirements_file = "requirements/CX6-requirements.yaml"
acceptance_criteria_file = "requirements/CX6-acceptance-criteria.yaml"

# Generate plan based on requirements ONLY
# No need to read analysis/, summaries/, or other folders
```

### For TDD-Master Orchestrator
```bash
# Read acceptance criteria
ac_file = "requirements/CX6-acceptance-criteria.yaml"

# Find relevant AC by ID
# Generate tests based on AC validation structure
```

### For Epic Review Orchestrator
```bash
# Read master plan
plan_file = "artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml"

# Read progress tracker
progress_file = "execution/tracking/progress-tracker.json"

# Generate health report
```

---

## 🔒 Protection Rules

**requirements/ Folder Rules:**
- ✅ ONLY 2 YAML files allowed
- ❌ NO subdirectories
- ❌ NO additional files
- ❌ NO markdown documentation (use reports/ instead)

**Root Rules:**
- ✅ ONLY 1 README.md allowed
- ❌ NO redundant navigation files
- ❌ NO operation reports (use reports/ instead)
- ❌ NO temporary files

**Git Rules:**
- ✅ ALWAYS push after significant changes
- ✅ ALWAYS document deletions with recovery commits
- ✅ NEVER force push without backup

---

## 📈 Progress Summary

### Overall CORTEX 6.0 Build
- **Total Effort:** 210-288 hours estimated
- **Current Progress:** Layer 4 (AC Traceability)
- **Current Phase:** CX6-005-ac-traceability.yaml
- **Completion:** ~48.6% (estimated)

### Recent Operations
- ✅ Vacuum cleanup (54% file reduction)
- ✅ Requirements verification (DoR/DoD 100%)
- ✅ Root organization (1 README only)
- ✅ Reports consolidation (7 operation docs)

---

## 🚀 Next Steps

1. **Continue CX6-005** - AC traceability implementation
2. **Launch Dashboard** - CX6-006 execution
3. **Migrate Orchestrator** - CX6-007 implementation
4. **Cross-Repo Support** - CX6-008 execution

---

## 📚 Additional Resources

- **Epic Review:** Run `epic review` for health check and gap analysis
- **Planning:** Run `plan <feature>` for new feature planning
- **TDD:** Run `tdd <feature>` for test-driven development
- **Dashboard:** Visit `execution/dashboard/` for interactive viewer

---

**Last Updated:** 2026-01-10 08:15  
**Maintained By:** Asif Hussain  
**Version:** 2.0.0 (Clean Reorganization)  
**Status:** ✅ PRODUCTION READY
