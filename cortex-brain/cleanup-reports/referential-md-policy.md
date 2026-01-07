# Referential MD File Policy

## Decision: Keep Historical Reports in Organized Structure

**Date:** 2025-11-16  
**Status:** Policy Established

## Background

During cleanup, discovered 47 completion reports and 6 summary documents in `cortex-brain/documents/`:
- reports/ (41 files)
- summaries/ (6 files)
- analysis/ (2 COMPLETE files)
- implementation-guides/ (1 SUMMARY file)
- investigations/ (1 COMPLETE file)
- planning/ (1 COMPLETE file)

## Analysis

These files contain:
- Historical project decisions
- Lessons learned from completed work
- Performance metrics and improvements
- Implementation details and rationale

**Value:** High - useful for understanding project evolution and learning from past work

**Problem:** MD format is human-readable but not machine-queryable

## Policy Decision

### Keep Historical Reports (Do Not Delete)

**Reason:** These documents provide valuable historical context and learning value

**Location:** `cortex-brain/documents/` (current structure)

**Organization:**
- ✅ Already organized by category (reports/, summaries/, etc.)
- ✅ Follow naming convention: `PROJECT-FEATURE-STATUS.md`
- ✅ Proper CORTEX brain structure

### Future: No New Completion Reports

**Rule:** Copilot will NOT create new completion/summary MD files after completing tasks

**Exception:** Machine-readable YAML format in `cortex-brain/reports-index/` if needed for:
- Performance metrics tracking
- Test results archival
- System health monitoring

### Conversion Plan (Optional Future Work)

If machine-queryability becomes important:

1. Create `cortex-brain/reports-index/` with YAML metadata
2. Keep original MD files in archives for human reference
3. Index includes: date, project, status, key metrics, file location

**Priority:** Low - Current MD organization is functional

## Implementation Status

✅ **Completed:**
- Deleted redundant docs-backup folders (15 folders)
- Deleted temp referential files (8 files in scripts/temp)
- Updated CORTEX.prompt.md to prevent new summary documents
- Updated cleanup module to block docs-backup creation

⏸️ **Deferred:**
- MD to YAML conversion (complexity > value for now)
- Keep existing organized reports as-is

## Guidelines for Future

### When Completing Work:

❌ **Don't Create:**
- Standalone completion/summary MD files
- docs-backup folders
- Root-level report files

✅ **Do Create:**
- YAML metrics if needed: `cortex-brain/metrics/YYYY-MM-DD-feature.yaml`
- Git commits with detailed messages
- Update existing tracking documents

### User Preference:

**From user:** "I do not read these documents"

**Action:** Stop creating end-of-task summary documents entirely

**Alternative:** Use YAML for machine-readable data that systems can query/process
