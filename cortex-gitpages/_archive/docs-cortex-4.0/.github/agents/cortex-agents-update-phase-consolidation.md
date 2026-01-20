# CORTEX Agent Updates - Phase Consolidation (2026-01-18)

This document updates guidance for all CORTEX agents regarding the Phase Consolidation fix.

---

## Overview

**Change**: All agents now work with a **unified cortex-master.yaml** instead of split cortex-master.yaml + 26 phase YAML files.

**Why**: Eliminates sync drift that was discovered in chat01.md (4 phase status mismatches, 50 AC-ID count errors).

**Result**: Faster, more reliable implementation with automatic sync validation.

---

## ALL AGENTS: Updated Phase Loading

### Before
```python
# OLD - Load from split sources
master = load_yaml("cortex-master.yaml")
phase = load_yaml(f"phases/phase-{phase_num}.yaml")
# Merge two sources mentally
```

### After
```python
# NEW - Load from single source
master = load_yaml("cortex-master.yaml")
phase = master['phases'][f'PHASE-{phase_num}']
# All data in one place
```

---

## Specific Agent Updates

### cortex-builder.md

**Updated Responsibilities**:
1. ✅ Load phase from `cortex-master.yaml → phases:` section
2. ✅ Edit phase specifications directly in `cortex-master.yaml`
3. ✅ Run `python3 scripts/validate_phase_sync.py` before commit
4. ✅ Coordinate with pre-commit hook (automatic validation)

**Key Change**: No longer need to maintain dual edits (phase-XX.yaml AND cortex-master.yaml).

**Reference**: See `.github/prompts/cortex-builder-unified.prompt.md`

---

### cortex-gap-detection.md

**Updated Responsibilities**:
1. ✅ Detect gaps from master plan (unchanged)
2. ✅ Generate gap reports (unchanged)
3. ✅ **NEW**: Recommend remediation phases that consolidate into `phases:` section
4. ✅ **NEW**: Avoid recommending split phase/AC-ID structures

**Key Change**: Gap reports now recommend unified remediation phases.

---

### cortex-planner.md

**Updated Responsibilities**:
1. ✅ Plan phases based on `cortex-master.yaml → phases:` section
2. ✅ Account for phase dependencies (unchanged)
3. ✅ **NEW**: Ensure phase_tracker in cortex-master stays in sync (validator does this)
4. ✅ No longer need to plan dual updates

**Key Change**: Simplified planning - one source to track.

---

### cortex-review-*.md (All Review Agents)

**Updated Responsibilities**:
1. ✅ Review phase execution (unchanged)
2. ✅ Verify AC-ID specs in `cortex-master.yaml → phases:` section
3. ✅ **NEW**: Trust validator for sync consistency (no more manual checks)
4. ✅ Report AC-ID counts from single source

**Key Change**: Trust automation, focus on code quality.

**Reference Files**: These agents remain unchanged - they work through cortex-builder which now uses unified architecture.

---

### cortex-reviewer.md

**Updated Responsibilities**:
1. ✅ Review implementation against specs in `cortex-master.yaml → phases:`
2. ✅ Verify tests match testing requirements (unchanged)
3. ✅ **NEW**: Reference validator output for sync checks (not manual)
4. ✅ Approve phase completion when all AC-IDs done

**Key Change**: Reduced sync verification workload.

---

## New Workflow Pattern (All Agents)

### Phase Load
```yaml
# Load from single source
phases = cortex_master['phases']
current_phase = phases['PHASE-XX']

# Use directly - no split sources to reconcile
title = current_phase['title']
ac_ids = current_phase['ac_ids']
testing = current_phase['testing']
```

### Phase Update
```yaml
# Edit single location
phases['PHASE-XX']['status'] = 'IN_PROGRESS'
phases['PHASE-XX']['ac_ids']['AC-XXX-XX-01']['status'] = 'COMPLETED'

# Save to cortex-master.yaml ONLY
save_yaml(cortex_master, "cortex-master.yaml")

# Validator runs automatically on commit
# No manual sync checks needed
```

### Validation
```python
# Trust the validator
# It runs automatically:
#   - Before each commit (pre-commit hook)
#   - On demand: python3 scripts/validate_phase_sync.py
#   - Auto-fixes safe issues

# If agent job involves cortex-master.yaml changes:
#   Assume validator will catch issues
#   No need to manually verify sync
```

---

## Handoff Pattern (Between Agents)

### Before Handoff
```
Agent A:
  1. Edit cortex-master.yaml
  2. Manually verify sync with phase-XX.yaml (if separate)
  3. Commit (hopefully consistent)
  4. Document status in report

Agent B receives:
  - Hopes everything synced correctly
  - May discover sync issues during work
```

### After Handoff (New Pattern)
```
Agent A:
  1. Edit cortex-master.yaml → phases: section
  2. Commit (pre-commit hook validates automatically)
  3. Guarantee: sync validation passed (or commit rejected)
  4. Document status in report

Agent B receives:
  - Guarantee of consistent state
  - Can trust cortex-master.yaml completely
  - No sync discovery needed
```

---

## Error Detection & Recovery

### If Sync Issue Appears in Agent Work

**Before**: Manual debugging needed
```
- Check cortex-master.yaml
- Check 26 phase-XX.yaml files
- Find mismatch
- Fix both places
```

**After**: Validator handles it
```
# Agent detects issue
python3 scripts/validate_phase_sync.py --verbose

# Shows exact problem
# Shows auto-fixes available

# Fix command
python3 scripts/validate_phase_sync.py --fix

# Try commit again (pre-commit hook validates)
```

---

## Documentation Updates for Agents

### Reference Files (Updated)

| Agent | Reference File | Update Status |
|-------|---------------|----|
| cortex-builder | `cortex-builder-unified.prompt.md` | ✨ NEW |
| All review agents | `.github/agents/*` | ✅ No changes (reference updated prompt) |
| CI/CD | `.git/hooks/pre-commit` | ✅ Updated |
| Developers | `PHASE-CONSOLIDATION-IMPLEMENTATION-GUIDE.md` | ✨ NEW |

### Quick Links

- **Architecture**: `_workspaces/roadmap/CORTEX-PHASE-CONSOLIDATION-SUMMARY.md`
- **Strategy**: `_workspaces/roadmap/PHASE-CONSOLIDATION-STRATEGY.md`
- **Implementation**: `_workspaces/roadmap/PHASE-CONSOLIDATION-IMPLEMENTATION-GUIDE.md`
- **Builder Prompt**: `.github/prompts/cortex-builder-unified.prompt.md`

---

## Compatibility Matrix

### Phase Consolidation Compatibility

| Component | Before | After | Compatible? |
|-----------|--------|-------|-------------|
| cortex-builder.prompt.md | Split sources | Unified source | ✅ Use `cortex-builder-unified.prompt.md` |
| cortex-master.yaml | Metadata + tracker | + phases: section | ✅ Superset (backward compatible structure) |
| phase-XX.yaml files | Required | Archived | ✅ Read-only reference available |
| Pre-commit hook | Basic SSOT checks | Phase sync validation | ✅ Enhanced |
| Validation scripts | None | consolidate_phases.py + validate_phase_sync.py | ✅ New capability |
| All agents | Reference split sources | Reference unified source | ✅ Works (redirect reference) |
| CI/CD | No auto-validation | Auto-validates on commit | ✅ Improved |

---

## Testing the New Workflow

### Agent Test Checklist

When testing new unified workflow:

- [ ] Agent loads `cortex-master.yaml` successfully
- [ ] Agent can read `phases:` section
- [ ] Agent extracts AC-IDs from phases section (not separate file)
- [ ] Agent edits phase status/AC-IDs directly in cortex-master.yaml
- [ ] Agent commits changes
- [ ] Pre-commit hook validates (should pass)
- [ ] Validator output shows consistency
- [ ] Next agent receives consistent state (no sync issues)

---

## Migration Guide (For Agent Teams)

### Step 1: Understand New Architecture

**Read**: `CORTEX-PHASE-CONSOLIDATION-SUMMARY.md` (10 min)

Key points:
- Single source of truth in cortex-master.yaml
- phases: section contains all specs
- Validator prevents sync issues
- Pre-commit hook auto-validates

### Step 2: Update References

**Update prompt references**:
```
Old: "See .github/prompts/cortex-builder.prompt.md"
New: "See .github/prompts/cortex-builder-unified.prompt.md"
```

**Update file references**:
```
Old: "_workspaces/roadmap/phases/phase-XX.yaml"
New: "cortex-master.yaml → phases.PHASE-XX"
```

### Step 3: Test New Workflow

**Create test phase change**:
1. Load cortex-master.yaml
2. Edit `phases.PHASE-TEST.status = 'IN_PROGRESS'`
3. Commit (validator should pass)
4. Verify pre-commit hook ran
5. Revert test

### Step 4: Train Team

**Share with team**:
- New prompt location
- New file references
- How validator works
- Pre-commit hook behavior

---

## FAQ for Agents

### Q: Where do I load phase specs now?

**A**: cortex-master.yaml → phases: section. Example:
```python
master = load_yaml("cortex-master.yaml")
phase = master['phases']['PHASE-01']
# All specs here: title, status, ac_ids, testing, etc.
```

### Q: Do I still need phase-XX.yaml files?

**A**: Not for active work. They're archived in `_archives/phase-yamls-v1/` for reference.

### Q: What if I find a sync issue?

**A**: Run validator:
```bash
python3 scripts/validate_phase_sync.py --verbose
python3 scripts/validate_phase_sync.py --fix
```

### Q: How do I know if my changes are synced?

**A**: Pre-commit hook validates automatically. If commit is accepted, state is guaranteed consistent.

### Q: Can I bypass the validator?

**A**: Yes: `git commit --no-verify` (use last resort only). Then manually verify:
```bash
python3 scripts/validate_phase_sync.py
```

### Q: What's the new cortex-builder prompt?

**A**: `.github/prompts/cortex-builder-unified.prompt.md` - includes unified workflow guidance.

---

## Support & Troubleshooting

### Issue: Validator fails on commit

**Solution**:
```bash
python3 scripts/validate_phase_sync.py --verbose
python3 scripts/validate_phase_sync.py --fix
git add .
git commit -m "fix: phase sync"
```

### Issue: Can't find phase spec

**Solution**:
```bash
grep -A 50 "PHASE-XX:" cortex-master.yaml | grep -A 5 "ac_ids:"
```

### Issue: Pre-commit hook too slow

**Note**: Validator runs in <1 second on modern hardware. If slow, check:
```bash
python3 scripts/validate_phase_sync.py --verbose
# Check for large phase sections or large AC counts
```

### Issue: Old phase-XX.yaml referenced in code

**Solution**: Update references to use cortex-master.yaml:
```python
# OLD
phase = load_yaml(f"_workspaces/roadmap/phases/phase-{n}.yaml")

# NEW
master = load_yaml("_workspaces/roadmap/cortex-master.yaml")
phase = master['phases'][f'PHASE-{n}']
```

---

## Rollback Plan (If Needed)

**If consolidation causes problems**:

```bash
# Quick rollback
git revert <CONSOLIDATION_COMMIT>

# Full rollback
cp -r _archives/phase-yamls-v1/* _workspaces/roadmap/phases/
# Restore old prompts and scripts
```

Estimated time: 10 minutes

---

## Summary

### Key Changes for Agents

1. ✅ Load phase specs from `cortex-master.yaml → phases:` (not separate phase-XX.yaml)
2. ✅ Edit directly in cortex-master.yaml (atomic single-file updates)
3. ✅ Trust pre-commit hook for sync validation (automatic, no manual checks)
4. ✅ Run `validate_phase_sync.py` if issues appear (diagnostic tool)
5. ✅ Reference new unified prompt (`.github/prompts/cortex-builder-unified.prompt.md`)

### What Stays the Same

1. ✅ All governance rules (CORE-008 through CORE-028)
2. ✅ AC-ID naming conventions
3. ✅ Status machine (NOT_STARTED → IN_PROGRESS → COMPLETED)
4. ✅ Testing requirements format
5. ✅ Audit trail logging

### What Improves

1. ✨ No more manual sync coordination
2. ✨ Faster phase updates (single file edit)
3. ✨ Automatic validation (pre-commit hook)
4. ✨ Guaranteed consistency (validator prevents drift)
5. ✨ Simpler phase implementation workflow

