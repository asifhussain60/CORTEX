# AC-AR-010 Continuation Guide: Next Steps
**Status**: Ready for Implementation  
**Date**: 2026-01-18  
**Prepared for**: Next development session

---

## Current State Summary

### AC-AR-010-01: Design Phase ✅ COMPLETE
- **FOLDER_STRUCTURE_DESIGN.md**: Comprehensive design document
- **MIGRATION_PLAN.md**: Detailed 4-phase migration strategy
- **Tests**: 18/18 passing (100%)
- **Git Commits**: 3 commits documenting design work

### Phase Position
```
PHASE-02-CODEBASE-COHERENCE:
├─ AC-AR-010-01: Design Phase              ✅ LOCKED
├─ AC-AR-010-02: Migration Script          ← NEXT (Ready to start)
└─ AC-AR-010-03: Import Updates & Validation ← After AC-02
```

---

## Option 1: Continue with AC-AR-010-02 (Recommended)

### What It Entails
Implement the **automated migration script** that will move 170+ files from dual structure (cortex-brain/ + src/) to unified cortex/ structure.

### Specific Tasks

1. **Create Migration Script** (`scripts/migrate_folder_structure.py`)
   - Parse current directory structure
   - Create mapping (source → destination)
   - Move files in dependency-aware order
   - Verify checksums before/after
   - Generate migration report
   - Create rollback script

2. **Test on Staging**
   - Run script in dry-run mode
   - Verify all files would move correctly
   - Test rollback capability

3. **Success Criteria**
   - Script successfully moves ~170 files
   - All checksums verify (no data loss)
   - Rollback script works correctly
   - Migration report generated

### Estimated Time
**1-2 days** for script development + testing

### Deliverable
- `scripts/migrate_folder_structure.py`
- `scripts/rollback_migration.sh`
- Migration report (JSON)
- AC-AR-010-02 test suite

### Success Marker
All tests for AC-AR-010-02 passing (10/10 expected)

---

## Option 2: Continue with AC-AR-010-03 (Alternative)

### What It Entails
Implement **import path updates and validation** to ensure all 200+ import statements work after migration.

### Specific Tasks

1. **AST-Based Import Rewriting**
   - Parse all Python files
   - Identify import statements
   - Apply transformation rules (cortex_brain → cortex.brain, etc.)
   - Update __init__.py files
   - Save modified files

2. **Manual Fixes for Complex Cases**
   - Handle circular dependencies
   - Fix dynamic imports
   - Resolve conditional imports

3. **Validation**
   - Import resolution tests (no broken imports)
   - Tier isolation verification (no cross-tier violations)
   - Circular dependency detection
   - Cross-platform path validation

### Estimated Time
**2-3 days** for import updates + validation

### Deliverable
- Updated 170+ files with correct imports
- Import validation tests
- Tier isolation report
- AC-AR-010-03 test suite

### Success Marker
All tests passing + 0 broken imports detected

### Note
AC-AR-010-03 **depends on AC-AR-010-02** being complete (files must be moved first before imports can be updated).

---

## Option 3: Pause for Architecture Review

### What It Entails
Take a step back and review:
- Design document comprehensiveness
- Migration strategy alignment with current code
- Risks and contingencies adequacy
- Team capacity for implementation

### When to Choose
- If you want broader team input before proceeding
- If you want to optimize migration strategy further
- If you need time to assess current codebase more thoroughly

### Estimated Time
**1-2 hours** for review + discussion

### Deliverable
- Architecture review notes
- Updated migration strategy (if needed)
- Decisions for next steps

---

## Recommended Path Forward

### Immediate (Next 5-7 days)
1. **AC-AR-010-02**: Implement migration script (1-2 days)
2. **AC-AR-010-03**: Implement import updates (2-3 days)
3. **Testing & Validation**: Full test suite + cross-platform (1-2 days)

### By End of Week
- ✅ PHASE-02-CODEBASE-COHERENCE LOCKED (all 3 ACs complete)
- ✅ New unified cortex/ structure ready for use
- ✅ All 35/35 tests passing
- ✅ PHASE-03-CORE-ARCHITECTURE unblocked

### Strategic Impact
- **Eliminates** 200+ hours annual navigation/import confusion
- **Enables** clean, scalable structure for remaining 3 phases
- **Prevents** structural debt accumulation

---

## Implementation Checklist for AC-AR-010-02

If you choose Option 1, here's what to implement:

```python
# scripts/migrate_folder_structure.py should include:

class MigrationMapping:
    """Define where each file/folder should move"""
    # cortex-brain/tier0/* → cortex/core/ + cortex/brain/tier0/
    # cortex-brain/tier1/* → cortex/brain/tier1/
    # ... etc
    
class MigrationValidator:
    """Pre-migration validation"""
    def validate_git_clean()
    def validate_current_structure()
    def validate_mappings()
    
class FileMigrator:
    """Execute migration"""
    def safe_move(src, dest)  # with checksum verification
    def generate_report()
    def create_rollback_script()
    
class ChecksumVerifier:
    """Ensure no data loss"""
    def hash_all_files_before()
    def hash_all_files_after()
    def verify_checksums_match()
    
def main():
    # 1. Validate preconditions
    # 2. Create mappings
    # 3. Move files
    # 4. Verify integrity
    # 5. Generate reports
    # 6. Create rollback script
```

---

## Implementation Checklist for AC-AR-010-03

If you eventually reach Option 2, here's what to implement:

```python
# For import updates:

class ImportTransformer:
    """Transform old imports to new"""
    # cortex_brain.tier2 → cortex.brain.tier2
    # src.api → cortex.api
    # src.orchestrators → cortex.orchestrators
    
class ImportValidator:
    """Verify all imports resolve"""
    def test_no_broken_imports()
    def test_no_tier_isolation_violations()
    def test_no_circular_dependencies()
    def test_cross_platform_paths()
    
class CircularDependencyResolver:
    """Fix circular imports"""
    # Move shared code to separate module, or
    # Import at function level (inside functions)
```

---

## Key Files to Reference

### Design Documents (For Context)
- **FOLDER_STRUCTURE_DESIGN.md**: Target structure & organization principles
- **MIGRATION_PLAN.md**: 4-phase strategy, risks, rollback plan
- **AC-AR-010-01-DESIGN-PHASE-SUMMARY.md**: Session summary

### Test Specifications
- **tests/test_ac_ar_010_01_design.py**: Test suite validating AC-AR-010-01

### Related Documentation
- **cortex-master.yaml** (_workspaces/roadmap/): Phase definitions and ACs

---

## Decision Matrix

| Factor | Option 1 (AC-02) | Option 2 (AC-03) | Option 3 (Review) |
|--------|------------------|------------------|-------------------|
| Time Commitment | 1-2 days | 2-3 days | 1-2 hours |
| Dependency | None (can start now) | Requires AC-02 done first | None |
| Risk Level | Medium (file movement) | Medium-High (imports everywhere) | Low (planning) |
| Value Delivered | Infrastructure ready | All imports working | Better planning |
| Recommended | ✅ YES | NEXT (after AC-02) | Optional |

---

## Success Definition

### After AC-AR-010-02 Complete
- ✅ ~170 files moved to new structure
- ✅ All checksums verified (no data loss)
- ✅ Rollback script created and tested
- ✅ 10/10 tests passing (expected for AC-02)

### After AC-AR-010-03 Complete
- ✅ All import paths updated
- ✅ 0 broken imports detected
- ✅ 0 tier isolation violations
- ✅ 10/10 tests passing (expected for AC-03)

### After AC-AR-010 Complete
- ✅ PHASE-02-CODEBASE-COHERENCE LOCKED
- ✅ All 35 ACs passing
- ✅ New unified structure ready for use
- ✅ PHASE-03-CORE-ARCHITECTURE unblocked

---

## Next Immediate Action

**I recommend**: Start with **Option 1 (AC-AR-010-02)** immediately.

This will:
1. Build on momentum from design phase completion
2. Deliver tangible file structure improvements quickly
3. Unblock subsequent ACs
4. Achieve Phase 2 completion by end of week

Would you like me to:
- **Option 1**: Begin implementing AC-AR-010-02 (migration script)?
- **Option 2**: Begin implementing AC-AR-010-03 (import updates)?
- **Option 3**: Review and refine current design documents?
- **Option 4**: Something else entirely?

---

**Ready to proceed**: Let me know which path you'd like to take! 🚀
