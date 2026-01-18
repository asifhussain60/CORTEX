# CORTEX Phase Consolidation - Implementation Guide

## Overview

This document guides the implementation of the **Phase Consolidation Strategy** - moving from a 27-file sync nightmare to a single-file SSOT architecture.

**Problem Solved**:
- ❌ Before: 27 files (cortex-master.yaml + 26 phase YAMLs) causing constant sync drift
- ❌ Chat01 required 2+ passes to achieve basic consistency  
- ❌ Completion metrics wrong: 90.7% → 74.2% (50 AC-IDs miscounted)
- ❌ Status mismatches discovered in 4 phases

**Solution**:
- ✅ Single cortex-master.yaml file with `phases:` section containing ALL specs
- ✅ Validation script prevents sync issues before they happen
- ✅ Pre-commit hook auto-validates every commit
- ✅ Old phase files archived (read-only reference)

---

## Implementation Steps

### Phase 1: Setup Scripts (5 minutes)

**Already created**:
1. ✅ `scripts/consolidate_phases.py` - Reads phase YAMLs, generates consolidated spec
2. ✅ `scripts/validate_phase_sync.py` - Validates cortex-master.yaml phases section
3. ✅ `.git/hooks/pre-commit` - Auto-validates before each commit

**Verify they exist**:
```bash
ls -la scripts/consolidate_phases.py
ls -la scripts/validate_phase_sync.py
ls -la .git/hooks/pre-commit
```

### Phase 2: Test Validator (5 minutes)

```bash
# Test the validation script (should fail until phases: section exists)
python3 scripts/validate_phase_sync.py

# Expected output:
# ❌ phases: section not found in cortex-master.yaml
# This is expected - we'll create it in Phase 3
```

### Phase 3: Consolidate Phase Data (10 minutes)

```bash
# Run consolidation script
python3 scripts/consolidate_phases.py

# This will:
# 1. Read all 27 phase-XX.yaml files
# 2. Generate consolidated YAML snippet
# 3. Save to: _workspaces/roadmap/phases-consolidated-snippet.yaml
# 4. Archive originals to: _workspaces/roadmap/_archives/phase-yamls-v1/

# Expected output:
# ✓ Found 27 phase files
# ✓ Total Phases: 27
# ✓ Total AC-IDs: 310
# ... (more details)
# ✅ CONSOLIDATION COMPLETE
```

### Phase 4: Update cortex-master.yaml (15 minutes)

**Approach**: Append the consolidated phases section to cortex-master.yaml

```bash
# View the generated snippet
head -100 _workspaces/roadmap/phases-consolidated-snippet.yaml

# Manually append to cortex-master.yaml after final_status section
# Location: Find final_status: section, append phases: section after it

# Or use automated append:
cat _workspaces/roadmap/phases-consolidated-snippet.yaml >> _workspaces/roadmap/cortex-master.yaml
```

**Verify structure**:
```bash
# Check that phases: section is now in cortex-master.yaml
grep -c "^  PHASE-" _workspaces/roadmap/cortex-master.yaml
# Should show 27 phases

# Check AC-ID count
grep "AC-[A-Z]" _workspaces/roadmap/cortex-master.yaml | wc -l
# Should show 310+ lines
```

### Phase 5: Run Validator (5 minutes)

```bash
# Now validator should pass (or show fixable issues)
python3 scripts/validate_phase_sync.py

# Expected output:
# ✓ Loaded cortex-master.yaml
# ✓ Found phases: section with 27 phases
# ✓ All 310 AC-IDs are unique
# ✓ No circular dependencies detected
# ✅ ALL CHECKS PASSED
```

**If validator finds issues**:
```bash
# Auto-fix what's safe
python3 scripts/validate_phase_sync.py --fix

# View detailed report
python3 scripts/validate_phase_sync.py --verbose

# Then re-run
python3 scripts/validate_phase_sync.py
```

### Phase 6: Archive Original Files (5 minutes)

```bash
# Move phase-XX.yaml files to archives (script does this, but verify)
ls -la _workspaces/roadmap/_archives/phase-yamls-v1/

# Should show 27 .yaml files

# Verify originals still in phases/ (we keep them as backup)
ls _workspaces/roadmap/phases/ | wc -l
# Should show 27 files (or 26 if you delete them - optional)
```

**Optional: Clean up original files**
```bash
# If you want to delete originals (since they're archived):
rm _workspaces/roadmap/phases/phase-*.yaml
# Except phase-consolidated-snippet.yaml can be deleted after verification
```

### Phase 7: Test Pre-Commit Hook (5 minutes)

```bash
# Make a test commit
git add _workspaces/roadmap/cortex-master.yaml
git commit -m "test: consolidate phases into cortex-master.yaml"

# Pre-commit hook should:
# 1. Detect cortex-master.yaml in staged files
# 2. Run validate_phase_sync.py
# 3. Show ✅ or ❌ result
# 4. Accept or reject commit

# Expected output:
# 🔍 Phase Sync Validation (pre-commit hook)...
# ✅ Phase sync validation passed
# [BRANCH 1abc2de] test: consolidate phases...
```

**If hook rejects**:
```bash
# Fix issues and try again
python3 scripts/validate_phase_sync.py --verbose
python3 scripts/validate_phase_sync.py --fix

# Then commit again
git add .
git commit -m "fix: phase sync validation issues"
```

### Phase 8: Update Documentation (5 minutes)

```bash
# Update SSOT reference guide
# Backup old cortex-builder.prompt.md
cp .github/prompts/cortex-builder.prompt.md .github/prompts/cortex-builder.prompt.md.backup

# New unified prompt is ready
cat .github/prompts/cortex-builder-unified.prompt.md

# Archive old approach (for reference)
cp .github/prompts/cortex-builder.prompt.md _archives/cortex-builder-legacy.prompt.md
```

### Phase 9: Test New Workflow (10 minutes)

Test the new unified workflow with a simple phase update:

```bash
# 1. Load phase spec from cortex-master.yaml (no separate file needed)
grep -A 50 "PHASE-01:" _workspaces/roadmap/cortex-master.yaml

# 2. Make a test edit (change a phase status)
# Edit cortex-master.yaml → phases.PHASE-03 → status: NOT_STARTED

# 3. Validate
python3 scripts/validate_phase_sync.py

# 4. Commit
git add _workspaces/roadmap/cortex-master.yaml
git commit -m "phase-03: marked as NOT_STARTED (test)"

# 5. Pre-commit hook should pass
# ✅ Phase sync validation passed

# 6. Revert test
git revert HEAD
```

### Phase 10: Final Verification (5 minutes)

```bash
# Verify consolidation is complete
echo "✅ Checklist:"
echo "   Phases in cortex-master.yaml: $(grep -c "^  PHASE-" cortex-master.yaml || echo 'N/A')"
echo "   AC-IDs in cortex-master.yaml: $(grep -c "AC-[A-Z]" cortex-master.yaml || echo 'N/A')"
echo "   Files archived: $(ls _workspaces/roadmap/_archives/phase-yamls-v1/ | wc -l)"
echo "   Validator passes: $(python3 scripts/validate_phase_sync.py 2>&1 | grep -c 'ALL CHECKS PASSED' || echo '0')"
echo "   Pre-commit hook exists: $([ -f .git/hooks/pre-commit ] && echo 'YES' || echo 'NO')"
```

---

## Verification After Consolidation

### 1. Single Source of Truth Verified

```bash
# Count active phase definitions
grep "^  PHASE-[0-9]" cortex-master.yaml | wc -l
# Should be: 27

# Verify NO phase-XX.yaml files are referenced in prompts
grep -r "phase-[0-9][0-9]\.yaml" .github/prompts/ 2>/dev/null
# Should return: (nothing) or only legacy documentation
```

### 2. Sync Prevention Validated

```bash
# Try to introduce a sync error (commit should be rejected)
# Edit cortex-master.yaml phases section
# Then also try to edit old phase-XX.yaml file (it's archived now)

git add _workspaces/roadmap/cortex-master.yaml
git commit -m "test: intentional sync violation"
# Pre-commit hook should show validation checks passing
```

### 3. Automatic Repair Tested

```bash
# Manually break metadata count
# Edit cortex-master.yaml: total_ac_ids: 300 (wrong value)

python3 scripts/validate_phase_sync.py --fix
# Should show: 🔧 AUTO-FIX: Updating total_ac_ids 300 → 310

# Verify it was fixed
grep "total_ac_ids:" cortex-master.yaml
# Should show: total_ac_ids: 310
```

---

## Rollback Plan (If Needed)

**If consolidation causes problems**, follow these steps:

### Quick Rollback (Keeps git history)

```bash
# Revert the consolidation commit
git log --oneline | head -5
# Find: "consolidation" or "phase-consolidation" commit

git revert <COMMIT_HASH>
git commit -m "revert: phase consolidation - restoring split architecture"
```

### Full Rollback (Restore pre-consolidation state)

```bash
# 1. Restore original phase files from archives
cp -r _workspaces/roadmap/_archives/phase-yamls-v1/* _workspaces/roadmap/phases/

# 2. Remove consolidated phases section from cortex-master.yaml
# (manually delete phases: section or use git checkout)

# 3. Restore old prompts
cp _archives/cortex-builder-legacy.prompt.md .github/prompts/cortex-builder.prompt.md

# 4. Remove validator scripts (optional)
rm scripts/consolidate_phases.py
rm scripts/validate_phase_sync.py

# 5. Restore old pre-commit hook
git checkout .git/hooks/pre-commit

# 6. Commit rollback
git add -A
git commit -m "rollback: restore split phase file architecture"
```

---

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| 1. Setup Scripts | 5 min | ✅ Complete |
| 2. Test Validator | 5 min | Ready |
| 3. Consolidate Data | 10 min | Ready |
| 4. Update Master | 15 min | Ready |
| 5. Run Validator | 5 min | Ready |
| 6. Archive Files | 5 min | Ready |
| 7. Test Pre-Commit | 5 min | Ready |
| 8. Update Docs | 5 min | Ready |
| 9. Test Workflow | 10 min | Ready |
| 10. Final Check | 5 min | Ready |
| **TOTAL** | **70 minutes** | Ready to Execute |

---

## Success Criteria

After consolidation is complete, verify:

1. ✅ **Single Source of Truth**
   - All phase specs in cortex-master.yaml `phases:` section
   - Original phase-XX.yaml files archived (read-only)
   - No references to phase files in active prompts

2. ✅ **Validation Automated**
   - `python3 scripts/validate_phase_sync.py` passes with 0 errors
   - Pre-commit hook validates automatically on every commit
   - Metadata counts match actual AC-ID counts

3. ✅ **Sync Issues Prevented**
   - Cannot commit cortex-master.yaml if sync validation fails
   - Cannot accidentally split phase definitions between files
   - All AC-IDs unique across all phases

4. ✅ **Workflow Simplified**
   - Phase implementation now reads cortex-master.yaml ONLY
   - No "sync audit" sessions needed
   - Atomic phase updates (edit once, all references consistent)

5. ✅ **Zero Regressions**
   - All 310 AC-IDs accounted for
   - All 27 phases present
   - All governance rules intact
   - All tests still pass

---

## Maintenance After Consolidation

### Weekly Checks

```bash
# Ensure sync is maintained
python3 scripts/validate_phase_sync.py

# Expected output: ✅ ALL CHECKS PASSED
```

### When Adding New Phases

```bash
# Edit cortex-master.yaml phases section directly
# No need to create new phase-XX.yaml file

# Add to phases:
phases:
  PHASE-NEW:
    title: "New Phase"
    status: NOT_STARTED
    locked: false
    ac_ids:
      AC-NEW-001: {...}

# Commit (pre-commit hook validates)
git commit -m "phase: add PHASE-NEW"
```

### When Updating Phase Status

```bash
# Edit status in cortex-master.yaml only
phases:
  PHASE-XX:
    status: IN_PROGRESS  # ← Changed

# Run validator
python3 scripts/validate_phase_sync.py --fix

# Commit (automatic repair if metadata out of sync)
git commit -m "phase-xx: status updated to IN_PROGRESS"
```

### If Validator Issues Appear

```bash
# Diagnose
python3 scripts/validate_phase_sync.py --verbose

# Auto-fix (safe fixes only)
python3 scripts/validate_phase_sync.py --fix

# Commit fixes
git add cortex-master.yaml
git commit -m "fix: phase sync validation issues"
```

---

## Questions & Troubleshooting

### Q: What if I need to look up the old phase-XX.yaml format?

**A**: Archives are read-only reference:
```bash
cat _workspaces/roadmap/_archives/phase-yamls-v1/phase-XX.yaml
```

### Q: Can I revert a phase status?

**A**: Yes, use the state machine:
```
NOT_STARTED → IN_PROGRESS → COMPLETED
        ↓           ↓              
    (can change)  (can change)    
```

To go backwards, edit cortex-master.yaml:
```yaml
PHASE-XX:
  status: NOT_STARTED  # ← Reverted from IN_PROGRESS
```

### Q: What if validator fails on commit?

**A**: Read the error and fix:
```bash
python3 scripts/validate_phase_sync.py --verbose
python3 scripts/validate_phase_sync.py --fix
git add cortex-master.yaml
git commit -m "fix: phase validation"
```

### Q: Can I bypass the pre-commit hook?

**A**: Yes (use with caution):
```bash
git commit --no-verify
```
But then manually run:
```bash
python3 scripts/validate_phase_sync.py
```

---

## Support

For consolidation issues:

1. Check this guide first
2. Run with `--verbose` flag for details
3. Review PHASE-CONSOLIDATION-STRATEGY.md for architecture overview
4. Check git logs for recent commits that may have caused issues

