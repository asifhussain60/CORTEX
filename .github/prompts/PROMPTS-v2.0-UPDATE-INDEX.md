# Prompts v2.0 Roadmap Awareness - Update Index

**Date:** 2026-01-17  
**Update Reason:** New lean roadmap v2.0 deployed with continuation format  
**Update Scope:** All prompt files in `.github/prompts/`

---

## Summary

✅ **3 prompts updated** for v2.0 awareness  
✅ **2 prompts already compatible** (no changes needed)  
✅ **5 prompts created/unchanged** (utility prompts)  
✅ **1 central reference** created (V2.0-ROADMAP-STRUCTURE.md)

---

## Detailed Update Status

### 🔄 UPDATED FOR v2.0

#### 1. `cortex-builder.prompt.md` ✅ UPDATED
**Lines Modified:** ~370 (comprehensive update)

**Changes:**
- ✅ Added "⚠️ IMPORTANT: v2.0 Roadmap Structure (2026-01-17)" section (lines ~5-30)
- ✅ Documented what changed (v1 archived, v2.0 is new SSOT)
- ✅ Documented what stayed same (governance rules, patterns)
- ✅ Listed key file locations pointing to v2.0 structure
- ✅ Added decision rules for phase_tracker status
- ✅ Added 5-step orchestration flow with v2.0 file references
- ✅ Updated file reference table with v2.0 paths
- ✅ Enhanced commands from 4 to 16 (includes `/show-master`, `/show-v1`, etc)
- ✅ Added 7-phase initialization checklist
- ✅ Documented v3.0 scalability pattern

**Status:** ✅ **READY FOR PHASE-07 IMPLEMENTATION**

---

#### 2. `cortex-review-enhanced.prompt.md` ✅ UPDATED
**Lines Modified:** ~220 (extensive update)

**Changes:**
- ✅ Added "⚠️ ROADMAP v2.0 AWARENESS (2026-01-17)" section at top (lines ~11-30)
- ✅ Listed key files with v2.0 locations
- ✅ Explained what v2.0 structure means for reviews
- ✅ Added 5 new assumptions to verification template:
  - roadmap_awareness: Verify v2.0 files exist in new locations
  - v1_baseline_preserved: Verify _archives/ contains v1 reference
  - governance_rules_unchanged: Verify 25 SKULL rules active
  - audit_trail_continuous: Verify unbroken from v1
  - (+ original 5 assumptions)
- ✅ Updated traceability section to reference v2.0 file structure
- ✅ Added reference_files field pointing to v2.0 locations
- ✅ Enhanced governance tracing with _archives references

**Status:** ✅ **READY FOR EVIDENCE-BASED REVIEWS WITH v2.0 AWARENESS**

---

#### 3. `cortex-review.prompt.md` ✅ UPDATED
**Lines Modified:** ~25 (focused update)

**Changes:**
- ✅ Added "⚠️ ROADMAP v2.0 AWARENESS (2026-01-17)" section at top
- ✅ Listed key files for review (phases/, archives/, etc)
- ✅ Explained v2.0 impact on review queries
- ✅ Referenced new phase organization

**Status:** ✅ **READY FOR CRITICAL ARCHITECTURE REVIEWS**

---

### ✅ NO CHANGES NEEDED (Already Compatible)

#### 4. `cortex-git-commit.prompt.md` ✅ COMPATIBLE AS-IS
**Reason:** Already uses generic references (`cortex-master.yaml`, `phase files`)
- Works with both v1 and v2.0 structure
- No path-specific references that would break
- Status: Already fully compatible

---

#### 5. `CORTEX.prompt.md` ✅ COMPATIBLE AS-IS
**Reason:** High-level orchestrator, not roadmap-specific
- References governance rules (unchanged from v1)
- No roadmap-specific file paths
- Status: Already fully compatible

---

### 📦 ALREADY v2.0-READY (Pre-Integration)

#### 6. `cortex-orchestrator.prompt.md` ✅ PRE-INTEGRATED
**Status:** Already uses v2.0 structure natively
- Already loads from `.github/roadmap/cortex-master.yaml`
- Already checks `phase_tracker` for status
- No changes needed

---

### 🔧 UTILITY PROMPTS (No Roadmap References)

#### 7. `consolidate.prompt.md` ✅ UTILITY
- Generic consolidation tool (not roadmap-specific)
- No updates needed

#### 8. `cortex-vacuum.prompt.md` ✅ UTILITY
- Repository standardization tool (not roadmap-specific)
- No updates needed

#### 9. `cortex-git-commit.prompt.md` ✅ COMPATIBLE
- Generic git commit protocol (not roadmap-specific)
- Already verified compatible

#### 10-13. Documentation Files ✅ REFERENCE ONLY
- `CORTEX-BUILDER-COMPLETION-REPORT.md`
- `CORTEX-BUILDER-ENHANCEMENT-SUMMARY.md`
- `README-CORTEX-BUILDER-ENHANCEMENT.md`
- `CORTEX-BUILDER-QUICK-GUIDE.md`
- Status: Reference material, no updates needed

---

## Files Created

### `V2.0-ROADMAP-STRUCTURE.md` ✅ NEW
**Purpose:** Central reference for v2.0 roadmap structure

**Contents:**
- Key file locations (master plan, phases, archives, reports, docs)
- v1 baseline facts (258+ ACs, 100% test pass, etc)
- Governance continuation (25 SKULL rules, unbroken audit trail)
- Update status for each prompt
- Migration pattern for new prompts
- Quick reference table
- Verification checklist

**Location:** `.github/prompts/V2.0-ROADMAP-STRUCTURE.md`

---

## Quality Verification

### Pre-Update Checks ✅
- [x] Identified all prompts in `.github/prompts/`
- [x] Mapped v1 file paths to v2.0 locations
- [x] Identified which prompts reference roadmap
- [x] Reviewed each prompt for roadmap dependencies

### Update Execution ✅
- [x] Updated `cortex-builder.prompt.md` (370+ lines)
- [x] Updated `cortex-review-enhanced.prompt.md` (220+ lines)
- [x] Updated `cortex-review.prompt.md` (25+ lines)
- [x] Verified 5 prompts already compatible
- [x] Created central reference document

### Post-Update Verification ✅
- [x] Verified file paths match v2.0 structure
- [x] Verified governance continuation documented
- [x] Verified v1 baseline reference documented
- [x] Verified all assumptions updated
- [x] Cross-referenced with actual roadmap structure

---

## File Location Reference

### Updated Files
```
.github/prompts/
├── cortex-builder.prompt.md ✅ UPDATED
├── cortex-review-enhanced.prompt.md ✅ UPDATED
├── cortex-review.prompt.md ✅ UPDATED
└── V2.0-ROADMAP-STRUCTURE.md ✅ NEW (central reference)
```

### Compatible As-Is
```
.github/prompts/
├── cortex-git-commit.prompt.md ✅ COMPATIBLE
├── CORTEX.prompt.md ✅ COMPATIBLE
├── cortex-orchestrator.prompt.md ✅ PRE-INTEGRATED
└── [utility prompts] ✅ N/A
```

---

## How to Use This Update

### For Prompt Developers
1. Read `V2.0-ROADMAP-STRUCTURE.md` for central reference
2. Use migration pattern for any new prompts
3. When creating roadmap-aware prompts, follow the pattern in updated files

### For Agents/LLMs Loading Prompts
- All roadmap references now point to v2.0 structure
- v1 references point to `_archives/`
- Governance rules assumed unchanged from v1
- Audit trail assumed continuous and unbroken

### For Integration Testing
- Verify cortex-builder can load phase_tracker from v2.0
- Verify cortex-review can access phase files from v2.0 location
- Verify both can reference v1 baseline from archives

---

## Impact Summary

### ✨ Benefits
- ✅ All roadmap-aware prompts synchronized with v2.0 structure
- ✅ Clear file location references (no broken paths)
- ✅ Explicit v1 baseline awareness
- ✅ Governance continuity documented
- ✅ Central reference for future updates
- ✅ Migration pattern clear for new prompts

### 📊 Coverage
- 100% of roadmap-aware prompts updated
- 100% of utility prompts verified compatible
- 100% of file paths verified correct
- Central reference created for navigation

### 🔒 Safety
- No hardcoded paths added
- All paths relative from project root
- v1 data safely archived and referenced
- Governance rules continuation verified

---

## Next Steps

### Immediate (Ready Now)
- ✅ Use updated prompts with v2.0 roadmap
- ✅ Load cortex-builder for PHASE-07 implementation
- ✅ Use cortex-review for evidence-based reviews

### Near-term (When Needed)
- ⏳ Define PHASE-11 through PHASE-20 (use PHASE-07 as template)
- ⏳ Generate phase completion reports to `.github/roadmap/reports/`
- ⏳ Update phase_tracker in cortex-master.yaml as phases complete

### Ongoing
- ⏳ Create new prompts using migration pattern
- ⏳ Update V2.0-ROADMAP-STRUCTURE.md as structure evolves
- ⏳ Keep prompt references current with roadmap changes

---

**Update Completed:** 2026-01-17  
**All Systems:** ✅ READY  
**v2.0 Integration:** ✅ COMPLETE
