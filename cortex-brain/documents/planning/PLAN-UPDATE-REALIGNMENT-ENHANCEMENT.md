# Plan Update Summary - Realignment Script Enhancement

**Plan ID:** CORTEX-SETUP-001  
**Version:** 1.2 → 1.3  
**Updated:** 2025-12-03  
**Enhancement:** Task 8.6 expanded with comprehensive realignment script specification

---

## 🎯 What Changed

### Task 8.6: From Simple to Comprehensive

**Before (Version 1.2):**
- Simple "Bulk Rename Existing Long Filenames" task
- Basic functionality: scan, suggest, rename
- Limited safety features

**After (Version 1.3):**
- Full "Realignment Script" with enterprise-grade features
- Dual modes: Dry-run (preview) and Execute (apply)
- Atomic operations with rollback
- Cross-reference updating across .md/.yaml/.json files
- Comprehensive reporting and backup system

---

## 📋 Key Enhancements

### 1. Dry-Run Mode (Default)
```bash
python scripts/realign_filenames.py
```

**Features:**
- Preview all rename operations without changes
- Show before/after comparison with character savings
- Identify cross-reference locations
- Generate detailed report: `FILENAME-REALIGNMENT-REPORT.md`
- Safe to run anytime (exit code 0, no changes)

### 2. Execution Mode (--execute flag)
```bash
python scripts/realign_filenames.py --execute
```

**Features:**
- Create timestamped backup: `cortex-brain/backups/filename-realignment-{timestamp}.tar.gz`
- Atomic rename operations (all-or-nothing)
- Update cross-references in all files
- Validate all links post-rename
- Generate completion report with rollback instructions

### 3. Safety Features

**Pre-Execution:**
- ✅ Full backup creation and verification
- ✅ Git status check (warns if uncommitted changes)
- ✅ Collision detection (prevents overwrites)
- ✅ Dry-run validation requirement

**During Execution:**
- ✅ Atomic operations (rollback on any failure)
- ✅ Transaction-like behavior
- ✅ No partial state

**Post-Execution:**
- ✅ Cross-reference validation
- ✅ Completion report generation
- ✅ Backup available for manual restore

### 4. Self-Application

**This plan file will be renamed:**
- **Current:** `shared-environment-default-activation.md` (41 chars)
- **Target:** `PLAN-001-shared-env-setup.md` (27 chars, -34%)
- **Rationale:** Follows TYPE-ID-TITLE pattern, removes redundancy

---

## 📊 Updated Metrics

### Estimated Hours
- **Before:** 128 hours
- **After:** 136 hours (+8 hours for enhanced realignment script)

### Timeline
- **Before:** 15-22 days (~3-4 weeks)
- **After:** 16-24 days (~3.5-5 weeks)

### Success Criteria Added
- [ ] Realignment script with dry-run mode identifies 40+ files needing rename
- [ ] Realignment script execution mode safely renames files with atomic rollback
- [ ] Cross-reference updater modifies 150+ references across .md/.yaml/.json files
- [ ] This plan file renamed: `shared-environment-default-activation.md` → `PLAN-001-shared-env-setup.md`
- [ ] Average filename length reduced from ~47 to ~27 chars (43% reduction)
- [ ] VS Code tabs visible increased from 2 to 5+ tabs (157% improvement)

### New Success Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Average filename length | ~47 chars | ~27 chars | Measured across all docs |
| Filename reduction | 0% | 43% | Character savings |
| VS Code tabs visible | ~2 tabs | 5+ tabs | UI measurement |
| Files needing rename | 42 (17%) | 0 (0%) | Realignment script report |

---

## 📁 New Documents Created

### 1. Plan Update (main file)
**File:** `cortex-brain/documents/planning/shared-environment-default-activation.md`  
**Version:** 1.3  
**Changes:**
- Task 8.6 expanded with 50+ lines of detailed specification
- Acceptance criteria enhanced (8 → 13 items)
- Success metrics table expanded (10 → 14 metrics)
- Timeline adjusted (15-22 → 16-24 days)
- YAML frontmatter updated (estimated_hours: 128→136, added "realignment" tag)
- Header updated with current/target filename

### 2. Realignment Quick Reference
**File:** `cortex-brain/documents/planning/REALIGNMENT-SCRIPT-QUICK-REF.md`  
**Purpose:** Standalone guide for using the realignment script  
**Contents:**
- Usage instructions (dry-run and execute modes)
- What the script does (4-phase process)
- Example transformations (including this plan file)
- Safety features and rollback instructions
- Sample reports (dry-run and completion)
- Troubleshooting guide

### 3. Phase 8 Summary Update
**File:** `cortex-brain/documents/planning/phase-8-file-naming-summary.md`  
**Changes:**
- Implementation section updated (Task 6 description enhanced)
- Migration strategy completely rewritten (3 phases, safety features)
- Example migration expanded (this plan file + real CORTEX examples)
- Usage examples added (bash commands for dry-run, execute, rollback)

---

## 🔍 Implementation Details

### Script Specification

**Location:** `scripts/realign_filenames.py`

**Core Functions:**
```python
def scan_files(directory: str) -> List[Path]
def analyze_filename(path: Path) -> FilenameAnalysis
def generate_optimized_name(path: Path) -> str
def detect_collisions(renames: List[Tuple[Path, str]]) -> List[Collision]
def find_cross_references(path: Path) -> List[Reference]
def create_backup(timestamp: str) -> Path
def rename_file_atomic(old_path: Path, new_path: Path) -> bool
def update_references(reference: Reference, old: str, new: str) -> bool
def generate_report(mode: str, results: Results) -> Path
```

**Dependencies:**
- `src/utils/filename_optimizer.py` - Abbreviation engine
- `src/utils/filename_validator.py` - Validation logic

**Testing:**
```python
# tests/test_realign_filenames.py
test_dry_run_no_changes()
test_backup_creation()
test_collision_detection()
test_cross_reference_updating()
test_atomic_rollback()
test_git_status_check()
test_report_generation()
```

### Cross-Reference Updating

**File Types Scanned:**
- `.md` files - Markdown links `[text](./file.md)` and inline references
- `.yaml` files - YAML string values referencing files
- `.json` files - JSON string values referencing files

**Reference Patterns:**
```python
PATTERNS = [
    r'\[.*?\]\((.*?\.md)\)',           # Markdown links
    r'file:\s*["\']?(.*?\.md)["\']?',  # YAML/JSON file references
    r'path:\s*["\']?(.*?\.md)["\']?',  # Path fields
    r'location:\s*["\']?(.*?\.md)["\']?',  # Location fields
]
```

### Reporting

**Dry-Run Report (`FILENAME-REALIGNMENT-REPORT.md`):**
- Summary statistics (total files, files needing rename, percentages)
- Sample transformations (top 10 by character savings)
- Impact analysis (tabs visible, character savings)
- Cross-reference locations
- Next steps

**Completion Report (`FILENAME-REALIGNMENT-COMPLETION-REPORT.md`):**
- Execution summary (duration, files renamed, references updated)
- Backup location and size
- Rollback instructions
- Verification checklist
- Post-realignment actions

---

## 🎯 Rationale for Enhancement

### Why Expand Task 8.6?

1. **Risk Mitigation:** Renaming 42+ files (17% of all documents) is high-risk without proper safeguards
2. **Cross-References:** 150+ references across multiple file types need updating
3. **Production Readiness:** Enterprise-grade tooling required for CORTEX codebase
4. **Repeatability:** Other projects may need similar realignment (reusable tool)
5. **Confidence:** Dry-run mode allows validation before execution
6. **Rollback:** Full backup ensures no data loss

### Why Self-Application?

- **Lead by Example:** This plan should follow its own governance
- **Validation:** Tests the naming convention on a real, complex filename
- **Demonstration:** Shows 34% character reduction is achievable
- **Consistency:** All CORTEX plans should use TYPE-ID-TITLE pattern

---

## ✅ Completion Checklist

### Plan Document Updates
- [x] Task 8.6 expanded with comprehensive specification
- [x] Acceptance criteria enhanced (13 items total)
- [x] Success metrics expanded (14 metrics total)
- [x] Timeline adjusted (16-24 days)
- [x] YAML frontmatter updated (136 hours, "realignment" tag)
- [x] Version bumped (1.2 → 1.3)
- [x] Header updated with current/target filename

### New Documentation
- [x] Realignment quick reference created
- [x] Phase 8 summary updated
- [x] This summary document created

### Ready for Approval
- [x] All changes documented
- [x] All files internally consistent
- [x] Self-application specified
- [x] Rollback plan included
- [x] Safety features comprehensive

---

## 🚀 Next Steps

1. **User Approval** - Review updated plan (version 1.3)
2. **Implementation** - Begin Phase 8 Task 8.6 development
3. **Testing** - Write 20+ tests for realignment script
4. **Dry-Run** - Execute on CORTEX repository (preview mode)
5. **Review** - Validate suggested renames
6. **Execute** - Apply realignment after Phase 7 completion
7. **Rename Plan** - Apply to this file: `shared-environment-default-activation.md` → `PLAN-001-shared-env-setup.md`

---

**Version History:**
- v1.0 (2025-12-03): Initial plan with Phases 1-5
- v1.1 (2025-12-03): Added Phase 6 (Planning Infrastructure)
- v1.2 (2025-12-03): Added Phase 8 (File Naming Governance)
- v1.3 (2025-12-03): Enhanced Task 8.6 with comprehensive realignment script ← **CURRENT**

**Files Modified:**
1. `cortex-brain/documents/planning/shared-environment-default-activation.md` (plan)
2. `cortex-brain/documents/planning/phase-8-file-naming-summary.md` (phase summary)

**Files Created:**
1. `cortex-brain/documents/planning/REALIGNMENT-SCRIPT-QUICK-REF.md` (quick reference)
2. `cortex-brain/documents/planning/PLAN-UPDATE-REALIGNMENT-ENHANCEMENT.md` (this summary)

---

*This comprehensive realignment script addresses filename governance holistically across all CORTEX documents.*
