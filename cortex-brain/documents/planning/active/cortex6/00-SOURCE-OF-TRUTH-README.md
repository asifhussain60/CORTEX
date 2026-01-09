# CORTEX 6.0 Source of Truth - README

**Date:** 2026-01-09  
**Status:** ✅ CONSOLIDATED (Single Source of Truth Achieved)  
**Author:** Asif Hussain

---

## 🎯 CANONICAL SOURCE FILES (2 Only)

### 1. **Requirements** → `acceptance-criteria/requirements/CX6-requirements.yaml`

**Purpose:** Business requirements + Definition of Ready (DoR) decisions  
**Size:** 25 KB (784 lines)  
**Version:** 1.0.0  
**Status:** FINALIZED  
**DoR Status:** 100% COMPLETE (14/14 decisions)

**Contents:**
- Strategic Requirements (7)
- Foundation Requirements (4)
- Cross-Repo Requirements (5)
- Migrate Orchestrator Requirement (1)
- **Total:** 17 requirements with zero ambiguity

**DoR Integration:**
- 3 clarification sessions documented
- All 14 architectural decisions captured
- Q3-Q16 responses integrated
- Decision rationale explained

---

### 2. **Acceptance Criteria** → `acceptance-criteria/CX6-acceptance-criteria.yaml`

**Purpose:** Validation criteria for all CORTEX 6.0 features  
**Size:** 265 KB (5,448 lines)  
**Version:** 16.1.0  
**Status:** AUTHORITATIVE  
**Total Criteria:** 390+ across 25 sections

**Contents:**
- Section 1: Audit Logger Infrastructure (10 criteria)
- Section 2-24: Orchestrators, Governance, TDD, etc.
- Section 25: TDD-Master Orchestrator (8 criteria)
- Section 26-27: Cross-Repo + Migrate (planned for v17.0)

**Key Governance:**
- AC-GOV-011: TDD-Master required for ALL development (CORE-019)
- AC-TDD-MASTER-000: Supports unplanned mode (lightweight TDD)
- Dual validation framework (test + audit evidence)

---

## 🗂️ ARCHIVED FILES (Consolidation 2026-01-09)

**Location:** `archive/requirements-consolidation-2026-01-09/`

**Archived (10 files):**
1. ✅ `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml` (1,122 lines) - Epic definition, superseded by CX6-requirements.yaml
2. ✅ `INTELLIGENT-PLANNING-STRUCTURE-V6.yaml` (857 lines) - Planning workflow, now in orchestrator specs
3. ✅ `CX6-GOVERNANCE.yaml` (22 KB) - Governance rules, merged into acceptance criteria
4. ✅ `CX6-autonomous-safeguards-AC.yaml` (32 KB) - Safeguards, merged into acceptance criteria
5. ✅ `CX6-foundation-tasks-AC.yaml` (33 KB) - Foundation tasks, merged into requirements
6. ✅ `CX6-build-sequence.yaml` (24 KB) - Build sequence, now in execution plan
7. ✅ `CX6-completion-criteria.yaml` (21 KB) - Completion gates, merged into acceptance criteria
8. ✅ `CX6-requirements-OLD.yaml` (27 KB) - Previous version, superseded by finalized requirements
9. ✅ `plan-viewer-dashboard-requirements.yaml` (13 KB) - Dashboard reqs, part of main requirements
10. ✅ `RELOCATION-MAP.yaml` (7 KB) - Relocation tracking, no longer needed

**Why Archived:**
- Duplicated content now consolidated
- Outdated versions superseded
- Created confusion with multiple sources
- DoR decisions finalized all ambiguities

---

## 📊 CONSOLIDATION IMPACT

### Before Consolidation
- ❌ 12+ YAML files with overlapping content
- ❌ Multiple "source of truth" files
- ❌ Requirements split across 5+ files
- ❌ Acceptance criteria in 6+ files
- ❌ Unclear which file was authoritative

### After Consolidation
- ✅ **2 canonical files** (requirements + acceptance criteria)
- ✅ **Single source of truth** for requirements
- ✅ **Single source of truth** for validation
- ✅ **DoR design captured** in both files
- ✅ **Zero ambiguity** on what to reference

---

## 🎯 DEFINITION OF READY (DoR) DESIGN

**Captured In:** Both canonical files (metadata sections)

### DoR Achievement Tracking

**Requirements File (`CX6-requirements.yaml`):**
```yaml
metadata:
  dor_status: COMPLETE
  total_decisions: 14
  ambiguity_level: 0
  execution_readiness: true
  
  clarification_sessions:
    session_1: Q1-Q7 (7 decisions)
    session_2: Q8-Q11 (4 decisions + refinements)
    session_3: Q12-Q16 (5 decisions + Migrate Orchestrator)
```

**Acceptance Criteria File (`CX6-acceptance-criteria.yaml`):**
```yaml
metadata:
  version: 16.1.0
  status: AUTHORITATIVE
  total_criteria: 390+
  
  decision_integration:
    total_decisions: 14
    new_criteria: 15 (from DoR sessions)
    updated_criteria: 7
```

### Key DoR Decisions Captured

| Decision | File | Location |
|----------|------|----------|
| Q3: No backward compatibility (SKULL deletion) | Requirements | SR-001 + metadata |
| Q4: Manual housekeeping only | Requirements | SR-004 |
| Q5: Simplified cross-repo (PATH-based) | Requirements | SR-003 |
| Q7: Dual validation (test + audit) | Requirements | SR-002 |
| Q8: Home directory plan storage | Requirements | SR-006 |
| Q12-Q16: Cross-repo architecture | Requirements | SR-003 + XR-001 to XR-005 |

---

## 📁 FOLDER STRUCTURE (After Consolidation)

```
cortex6/
├── 00-SOURCE-OF-TRUTH-README.md        # ⭐ THIS FILE (navigation guide)
├── 00-README-PLAN-EXECUTION.md         # Execution guide
├── continuation-prompt.md              # Session continuation
│
├── acceptance-criteria/
│   ├── CX6-acceptance-criteria.yaml    # ⭐ CANONICAL SOURCE (validation)
│   │
│   ├── requirements/
│   │   └── CX6-requirements.yaml       # ⭐ CANONICAL SOURCE (business + DoR)
│   │
│   ├── enhancements/                   # Enhancement proposals
│   ├── summaries/                      # Summary documents
│   └── workflows/                      # Workflow documentation
│
├── artifacts/
│   └── CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml  # Execution plan (NOT requirements)
│
├── implementation-guides/              # Developer guides
│   └── STAGE-1-IMPLEMENTATION-GUIDE.md
│
├── tracking/                           # Progress tracking
│   ├── progress-tracker.json
│   └── CLEANUP-AND-PLAN-SUMMARY-2026-01-09.md
│
└── archive/
    ├── plans-2026-01-09/               # Old plans
    └── requirements-consolidation-2026-01-09/  # ⭐ Archived requirement files
```

---

## 🚀 HOW TO USE

### For Developers

**1. Read Requirements First:**
```bash
# Understand business requirements + DoR decisions
cat acceptance-criteria/requirements/CX6-requirements.yaml
```

**2. Then Read Acceptance Criteria:**
```bash
# Understand validation requirements
cat acceptance-criteria/CX6-acceptance-criteria.yaml
```

**3. Then Read Execution Plan:**
```bash
# Understand implementation order
cat artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml
```

### For Orchestrators

**Planning Orchestrator v6:**
- Read `CX6-requirements.yaml` to understand feature requirements
- Generate execution plan based on requirements
- Reference `CX6-acceptance-criteria.yaml` for validation

**TDD-Master Orchestrator:**
- Read `CX6-acceptance-criteria.yaml` to find AC-IDs
- Generate tests with `@pytest.mark.ac_id()` markers
- Implement code to pass tests (RED→GREEN→REFACTOR)

**Gap-Fix Orchestrator:**
- Compare implementation vs `CX6-acceptance-criteria.yaml`
- Identify gaps (missing AC implementations)
- Generate remediation tasks

---

## 📝 UPDATING THE SOURCE FILES

**⚠️ CRITICAL RULES:**

1. **Never create new requirement YAML files** - Update canonical files only
2. **Never duplicate acceptance criteria** - Extend existing sections
3. **Archive before major changes** - Create timestamped backup
4. **Update version numbers** - Increment on changes (semantic versioning)
5. **Document in changelog** - Explain what changed and why

**Update Process:**
```bash
# 1. Create backup
cp acceptance-criteria/CX6-acceptance-criteria.yaml \
   archive/CX6-acceptance-criteria-BACKUP-$(date +%Y%m%d-%H%M%S).yaml

# 2. Edit canonical file
vim acceptance-criteria/CX6-acceptance-criteria.yaml

# 3. Update version number in metadata
# 4. Add changelog entry
# 5. Commit with descriptive message
```

---

## ✅ CONSOLIDATION SUMMARY

**Operation:** Requirements Consolidation 2026-01-09  
**Result:** ✅ SUCCESS  
**Files Reduced:** 12 → 2 (83% reduction)  
**Canonical Sources:** 2 files (requirements + acceptance criteria)  
**Archived Files:** 10 files (historical record preserved)  
**DoR Status:** 100% COMPLETE (captured in both files)  
**Ambiguity:** 0 (zero conflicting sources)

**Benefits:**
- ✅ Single source of truth for requirements
- ✅ Single source of truth for validation
- ✅ DoR design fully captured
- ✅ No conflicting files
- ✅ Clear navigation (this README)
- ✅ Historical record preserved (archive/)

---

## 📚 REFERENCES

**Canonical Files:**
- [CX6-requirements.yaml](acceptance-criteria/requirements/CX6-requirements.yaml) - Business requirements + DoR
- [CX6-acceptance-criteria.yaml](acceptance-criteria/CX6-acceptance-criteria.yaml) - Validation criteria

**Execution:**
- [CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml](artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml) - 5-stage plan
- [STAGE-1-IMPLEMENTATION-GUIDE.md](implementation-guides/STAGE-1-IMPLEMENTATION-GUIDE.md) - Developer guide

**Archive:**
- [requirements-consolidation-2026-01-09/](archive/requirements-consolidation-2026-01-09/) - Old requirement files

---

**Last Updated:** 2026-01-09  
**Maintained By:** CORTEX Planning System  
**Status:** ✅ ACTIVE - Single Source of Truth Achieved
