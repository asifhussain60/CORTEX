# KDS Root Folder Cleanup Analysis - v6.0 Week 1

**Date:** 2025-11-04  
**Context:** After v6.0 Week 1 implementation  
**Purpose:** Identify and remove obsolete files from v5.0 and earlier versions

---

## 🔍 Files/Folders to Remove

### 1. ❌ context/ - OLD v5.0 Context Brain (OBSOLETE)

**Location:** `KDS/context/`

**What it contains:**
- `routes.json`, `database.json`, `ui-components.json`
- `knowledge-graph.json`
- JSON schemas
- README.md describing v5.0 sensor system

**Why remove:**
- This was the v5.0 "Context Brain" approach using sensors
- v6.0 uses hemisphere architecture with different brain structure
- Sensors still exist (`scripts/sensors/`) but output goes to different location
- This folder is referenced in `context-brain.md` but that file predates v6.0

**Replacement in v6.0:**
- `kds-brain/knowledge-graph.yaml` (existing)
- `kds-brain/development-context.yaml` (existing)
- Hemisphere-specific storage (left/right/corpus-callosum)

**Action:** ✅ SAFE TO DELETE

---

### 2. ❌ config/ - OLD Configuration (PARTIALLY OBSOLETE)

**Location:** `KDS/config/`

**What it contains:**
- `cleanup-rules.yaml`
- `team-intelligence.yaml`

**Why review:**
- These files appear to be from older KDS versions
- Not referenced in v6.0 Week 1 implementation
- Functionality may have moved to governance/ or kds-brain/

**Action:** ⚠️ REVIEW CONTENTS, LIKELY DELETE

---

### 3. ⚠️ Obsolete Documentation Files

**Files that may be superseded by v6.0 docs:**

#### Migration Documentation (No longer needed post-migration)
- `MIGRATION-TO-DEDICATED-REPO.md` - Migration complete
- `MIGRATION-VERIFICATION-ANALYSIS.md` - Migration complete
- `POST-MIGRATION-QUICKSTART.md` - Superseded by KDS-V6-QUICK-START.md

**Action:** ✅ CAN BE ARCHIVED OR DELETED

#### Dual Brain Resolution (v5.0 Issue, resolved in v6.0)
- `DUAL-BRAIN-RESOLUTION-PLAN.md` - v5.0 issue, v6.0 has clear hemisphere architecture
- `Brain Architecture.md` - Superseded by KDS-V6-BRAIN-HEMISPHERES-DESIGN.md

**Action:** ✅ CAN BE DELETED (v6.0 resolves this)

#### Implementation Summaries (Status updates, not reference docs)
- `DOR-IMPLEMENTATION-SUMMARY.md` - Old implementation status
- `BRAIN-AMNESIA-IMPLEMENTATION.md` - Feature now in scripts/
- `TDD-ENFORCEMENT-SUMMARY.md` - Summary, not ongoing reference
- `TIER-0-RULES-ADDED-SUMMARY.md` - Summary, not ongoing reference

**Action:** ⚠️ ARCHIVE (historical record) or DELETE if info captured elsewhere

#### Old KDS Designs
- `KDS-DESIGN.md` - v4.3.0, superseded by v6.0 docs
- `KDS-REVIEW-2025-11-04.md` - One-time review, not ongoing reference

**Action:** ⚠️ ARCHIVE (historical) or DELETE

---

### 4. ⚠️ Multiple V6 Plan Documents (Consolidation Needed)

**Files:**
- `KDS-V6-PLAN-COMPARISON.md`
- `KDS-V6-REFINED-IMPLEMENTATION-PLAN.md`
- `KDS-V6-IMPLEMENTATION-SUMMARY.md`
- `KDS-V6-STATUS-UPDATE.md`
- `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` ← **Active plan**
- `KDS-V6-WEEK1-COMPLETE.md` ← **Active status**

**Why consolidate:**
- Multiple overlapping plans create confusion
- `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` is the authoritative plan
- Other files may be drafts or superseded versions

**Action:** 
- ✅ KEEP: `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` (master plan)
- ✅ KEEP: `KDS-V6-WEEK1-COMPLETE.md` (current status)
- ✅ KEEP: `KDS-V6-QUICK-START.md` (user guide)
- ✅ KEEP: `KDS-V6-DOCUMENTATION-INDEX.md` (navigation)
- ✅ KEEP: `KDS-V6-EXECUTIVE-SUMMARY.md` (overview)
- ✅ KEEP: `KDS-V6-BRAIN-HEMISPHERES-DESIGN.md` (architecture)
- ⚠️ REVIEW: Others may be drafts - check if content is captured in kept files
- ❌ DELETE: `KDS-V6-PLAN-COMPARISON.md` (planning artifact)
- ❌ DELETE: `KDS-V6-REFINED-IMPLEMENTATION-PLAN.md` (superseded by PROGRESSIVE)
- ❌ DELETE: `KDS-V6-IMPLEMENTATION-SUMMARY.md` (superseded by WEEK1-COMPLETE)
- ❌ DELETE: `KDS-V6-STATUS-UPDATE.md` (superseded by WEEK1-COMPLETE)

---

## 📋 Cleanup Action Plan

### Phase 1: Immediate Deletions (Safe)

```powershell
# Delete obsolete context/ folder
Remove-Item -Path "KDS\context" -Recurse -Force

# Delete migration docs (migration complete)
Remove-Item "KDS\MIGRATION-TO-DEDICATED-REPO.md"
Remove-Item "KDS\MIGRATION-VERIFICATION-ANALYSIS.md"
Remove-Item "KDS\POST-MIGRATION-QUICKSTART.md"

# Delete dual brain resolution (resolved in v6.0)
Remove-Item "KDS\DUAL-BRAIN-RESOLUTION-PLAN.md"
Remove-Item "KDS\Brain Architecture.md"

# Delete superseded v6 plan documents
Remove-Item "KDS\KDS-V6-PLAN-COMPARISON.md"
Remove-Item "KDS\KDS-V6-REFINED-IMPLEMENTATION-PLAN.md"
Remove-Item "KDS\KDS-V6-IMPLEMENTATION-SUMMARY.md"
Remove-Item "KDS\KDS-V6-STATUS-UPDATE.md"
```

### Phase 2: Review Before Deletion

```powershell
# Check config/ files for any needed content
Get-Content "KDS\config\cleanup-rules.yaml"
Get-Content "KDS\config\team-intelligence.yaml"
# If content not needed elsewhere, delete config/ folder

# Review implementation summaries
# If info is captured in v6.0 docs, delete:
Remove-Item "KDS\DOR-IMPLEMENTATION-SUMMARY.md"
Remove-Item "KDS\BRAIN-AMNESIA-IMPLEMENTATION.md"
Remove-Item "KDS\TDD-ENFORCEMENT-SUMMARY.md"
Remove-Item "KDS\TIER-0-RULES-ADDED-SUMMARY.md"

# Review old design docs
Remove-Item "KDS\KDS-DESIGN.md"  # v4.3.0
Remove-Item "KDS\KDS-REVIEW-2025-11-04.md"  # One-time review
```

### Phase 3: Update References

After deletion, update any files that reference deleted items:

```powershell
# Search for references to context/
grep -r "KDS/context" KDS/prompts/

# Update code-executor.md and work-planner.md
# Remove references to context-brain.md if it's obsolete

# Update any documentation that points to deleted files
```

---

## ⚠️ Files Requiring Reference Updates

### Files that reference `context-brain.md`:
- `prompts/internal/code-executor.md` (line 7, 333)
- `prompts/internal/work-planner.md` (line 7, 348)

**Action needed:**
1. Determine if `context-brain.md` is still needed in v6.0
2. If not, remove it and update references
3. If yes, update it for v6.0 hemisphere architecture

---

## 🎯 Recommended Keep List

**Essential v6.0 Documentation:**
- ✅ `README.md` - Main repository README
- ✅ `KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` - Master implementation plan
- ✅ `KDS-V6-WEEK1-COMPLETE.md` - Current status
- ✅ `KDS-V6-QUICK-START.md` - User guide
- ✅ `KDS-V6-DOCUMENTATION-INDEX.md` - Documentation navigation
- ✅ `KDS-V6-EXECUTIVE-SUMMARY.md` - High-level overview
- ✅ `KDS-V6-BRAIN-HEMISPHERES-DESIGN.md` - Architecture documentation
- ✅ `KDS-CHEATSHEET.md` - Quick reference (if updated for v6.0)
- ✅ `TDD-QUICK-REFERENCE.md` - TDD workflow reference

**Essential Directories:**
- ✅ `kds-brain/` - v6.0 brain storage
- ✅ `prompts/` - Agent prompts
- ✅ `scripts/` - Automation scripts
- ✅ `tests/` - Test suites
- ✅ `governance/` - Rules and challenges
- ✅ `sessions/` - Session storage
- ✅ `docs/` - Additional documentation
- ✅ `dashboard/` - Health dashboard
- ✅ `backups/` - Backup files

---

## 📊 Impact Analysis

### Files to Delete: 15-18 files
### Folders to Delete: 2 folders (context/, possibly config/)
### Files to Update: 2-4 files (remove references)
### Disk Space Saved: ~500KB-1MB

### Risk Level: LOW
- Most deletions are documentation/status files
- Context data can be regenerated from sensors if needed
- Backups exist in `backups/` folder

---

## ✅ Cleanup Verification

After cleanup, verify:

```powershell
# Run Week 1 validation tests
.\KDS\tests\v6-progressive\week1-validation.ps1

# Should still pass 27/27 tests

# Check for broken references
grep -r "context/" KDS/prompts/ KDS/scripts/
grep -r "MIGRATION-" KDS/
grep -r "DUAL-BRAIN" KDS/

# Verify essential files present
Test-Path "KDS\kds-brain\left-hemisphere"
Test-Path "KDS\kds-brain\right-hemisphere"
Test-Path "KDS\kds-brain\corpus-callosum"
Test-Path "KDS\KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md"
```

---

## 🎯 Summary

**Recommended Cleanup:**
1. ✅ DELETE `context/` folder (v5.0 sensor output, obsolete)
2. ✅ DELETE migration documentation (migration complete)
3. ✅ DELETE dual brain resolution docs (resolved in v6.0)
4. ✅ DELETE superseded v6 plan documents (4 files)
5. ⚠️ REVIEW `config/` folder contents
6. ⚠️ REVIEW implementation summary files
7. ⚠️ UPDATE references to deleted files in agent prompts

**Expected Outcome:**
- Cleaner, more focused repository
- Only v6.0-relevant documentation
- No confusion between v5.0 and v6.0 approaches
- Easier navigation for developers

**Next Step:** Execute Phase 1 cleanup (safe deletions)

---

**Status:** Analysis Complete - Ready for Cleanup Execution  
**Risk:** LOW - Safe to proceed with Phase 1  
**Validation:** Run week1-validation.ps1 after cleanup
