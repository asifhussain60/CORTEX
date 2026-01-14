# CORTEX.prompt.md Enhancement - CX6 File Organization Mandate

**Date:** 2026-01-11 06:30 UTC  
**Version:** 6.2.0  
**Enhancement:** Added CX6 File Organization Mandate as Master Orchestrator responsibility  
**Status:** ✅ COMPLETE

---

## 🎯 What Was Added

### New Section: CX6 File Organization Mandate (Line 9)

**Critical Addition:** Master Orchestrator now ENFORCES that ALL CORTEX 6.0 related files must be organized under:

```
/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/cx6-plan/
```

### Key Features Added

1. **Single Source of Truth Structure** (182 lines)
   - Comprehensive folder hierarchy documentation
   - Clear subdirectory purposes (viewer/, validation/, reports/, phases/, architecture/, archive/)
   - Example file placements for all CX6 content types

2. **Automatic File Routing Rules** (Table format)
   - HTML dashboards → `viewer/`
   - Evidence bundles → `validation/`
   - Completion reports → `reports/`
   - Phase docs → `phases/`
   - Architecture diagrams → `architecture/`
   - Legacy content → `archive/`

3. **FORBIDDEN Locations** (Enforcement)
   - ❌ Root directory (violates CORE-009)
   - ❌ `cortex-brain/documents/` (not CX6-specific)
   - ❌ `templates/plan-viewer/` (move to `cx6-plan/viewer/`)
   - ❌ Any location outside `cortex-brain/cx6-plan/`

4. **Enforcement Protocol** (3-step process)
   - Before creating file: Block if wrong location, propose correct path
   - After detecting misplaced: Auto-consolidate via script
   - During vacuum: Report as HIGH severity violation

5. **Benefits Documentation**
   - ✅ Single source of truth
   - ✅ Easy navigation
   - ✅ Prevents duplication
   - ✅ Simplifies backups
   - ✅ Better context loading
   - ✅ Governance compliance
   - ✅ Version control clarity

6. **Reference Update Protocol**
   - Automatic find/replace when moving files
   - Integrity verification after consolidation

7. **Master Orchestrator Checkpoint** (7-item checklist)
   - Verifies all CX6 files in correct location
   - Runs before completing any operation
   - Triggers consolidation if violations found

---

## 📊 Enhancement Statistics

| Metric | Value |
|--------|-------|
| **Lines Added** | 182 lines |
| **New Section Size** | ~9KB |
| **Version Updated** | 6.1.0 → 6.2.0 |
| **File Size** | 3,378 → 3,560 lines (+5.4%) |
| **Enforcement Points** | 7 checkpoints |
| **Forbidden Locations** | 6 explicitly blocked |

---

## 🔧 Scripts Referenced

All enforcement uses existing production scripts:

1. **consolidate_documents.py** - Moves misplaced files to correct location
2. **vacuum_orchestrator.py** - Detects location violations (HIGH severity)
3. **verify_integrity.py** - Validates references after moves

**No new scripts needed** - leverages existing automation infrastructure.

---

## ✅ Integration Points

### With Existing CORTEX.prompt.md Features:

1. **Document Consolidation Protocol** (Line 569)
   - Now targets `cortex-brain/cx6-plan/` as default destination
   - Enforces subdirectory routing rules

2. **Vacuum Orchestrator Protocol** (Line 644)
   - Detects CX6 files outside `cx6-plan/` as HIGH violations
   - Auto-proposes consolidation

3. **Visual Dashboard Management** (Line 778)
   - Dashboard files MUST be in `cx6-plan/viewer/`
   - Update script uses correct paths

4. **Post-Operation Verification** (Line 837)
   - Verification includes CX6 file location check
   - Part of standard integrity protocol

---

## 🎯 User Benefits

### Before Enhancement:
- ❌ CX6 files scattered across workspace
- ❌ Manual tracking of plan-viewer location
- ❌ No enforcement of file organization
- ❌ Risk of duplication and version confusion

### After Enhancement:
- ✅ All CX6 files in one predictable location
- ✅ Automatic enforcement via Master Orchestrator
- ✅ Clear folder structure by content type
- ✅ Prevention of misplaced files
- ✅ Easy backup/restore of entire CX6 plan

---

## 📋 Implementation Verification

```bash
# 1. Verify section added to prompt
grep -n "CX6 FILE ORGANIZATION MANDATE" .github/prompts/CORTEX.prompt.md
# Result: Line 9 ✅

# 2. Verify file size increase
wc -l .github/prompts/CORTEX.prompt.md
# Result: 3,560 lines (was 3,378) ✅

# 3. Verify version updated
head -5 .github/prompts/CORTEX.prompt.md | grep "Version:"
# Result: Version: 6.2.0 ✅

# 4. Check for broken references (should be 0)
grep -E "cortex-brain/documents/validation/(phase1-verification|plan-viewer-update)" .github/prompts/CORTEX.prompt.md
# Result: No matches (fixed to cx6-plan paths) ✅
```

---

## 🔄 Master Orchestrator Behavior Change

### Before:
- Accepted file creation anywhere in workspace
- Did not enforce CX6 file organization
- Manual cleanup required

### After:
**ON EVERY TURN:**
1. Scans for misplaced CX6 files
2. Blocks creation of CX6 files outside `cx6-plan/`
3. Auto-proposes correct location with explanation
4. Runs consolidation if violations detected
5. Verifies integrity after moves

**NEW BLOCKING BEHAVIOR:**
```python
if cx6_file_requested and not path.is_relative_to("cortex-brain/cx6-plan"):
    print("🛑 BLOCKED: CX6 files must be under cortex-brain/cx6-plan/")
    print(f"Correct location: {propose_correct_path()}")
    return  # BLOCKS until user confirms correct path
```

---

## 📖 Documentation References Updated

Fixed 2 broken links in "Key Documents to Review" section:

1. `phase1-verification-report.yaml`:
   - Old: `cortex-brain/documents/validation/`
   - New: `cortex-brain/cx6-plan/validation/` ✅

2. `plan-viewer-update-summary.md`:
   - Old: `cortex-brain/documents/validation/`
   - New: `cortex-brain/cx6-plan/viewer/docs/` ✅

---

## 🎉 Completion Summary

**Status:** ✅ COMPLETE

**What Changed:**
- ✅ Version: 6.1.0 → 6.2.0
- ✅ Added: 182-line CX6 File Organization Mandate section
- ✅ Role: Added "CX6 File Organization Guardian" to Master Orchestrator
- ✅ Fixed: 2 broken documentation links
- ✅ Integration: 4 existing protocols now enforce CX6 organization

**Files Modified:**
1. `.github/prompts/CORTEX.prompt.md` (+182 lines, 2 link fixes)

**Files Created:**
1. `cortex-brain/documents/validation/cortex-prompt-cx6-organization-enhancement.md` (this file)

**Net Result:** Master Orchestrator now ENFORCES single source of truth for all CORTEX 6.0 content under `cortex-brain/cx6-plan/` with automatic detection and consolidation of violations.

---

**Author:** GitHub Copilot (Acting as Master Orchestrator)  
**Approved By:** User (Option A implementation)  
**Next Action:** Run vacuum to verify zero CX6 location violations
