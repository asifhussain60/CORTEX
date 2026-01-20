# CORTEX Agent Updates - Phase Consolidation (2026-01-18) [SUPERSEDED BY cortex-impl-map.yaml]

This document describes the historical Phase Consolidation fix from 2026-01-18.

---

## Overview (HISTORICAL)

**Previous Change**: Unified `cortex-master.yaml` (consolidated from split cortex-master.yaml + 26 phase YAML files).

**Current Status**: `cortex-master.yaml` has been superseded by `cortex-impl-map.yaml` (v3.1-corrected) which serves as the authoritative implementation map.

**Why the Update**: Reflected actual implementation state with truth-based phase tracking and proper phase separation.

**Result**: Single source of truth (cortex-impl-map.yaml) with accurate phase status and implementation tracking.

---

## ALL AGENTS: Current Phase Loading (UPDATED 2026-01-20)

### Previous (2026-01-18)
```python
# Load from unified cortex-master.yaml
master = load_yaml("cortex-master.yaml")
phase = master['phases'][f'PHASE-{phase_num}']
```

### Current (2026-01-20)
```python
# Load from cortex-impl-map.yaml
impl_map = load_yaml("cortex-impl-map.yaml")
phase = impl_map['phases_implementation_status']['PHASE-{phase_num}']
# All data with phase_tracker authority
```

---

## Specific Agent Updates

### cortex-builder.md

**Updated Responsibilities**:
1. ✅ Load phase from `cortex-impl-map.yaml → phases_implementation_status:` section
2. ✅ Edit phase specifications directly in `cortex-impl-map.yaml`
3. ✅ Run `python3 scripts/validate-phase-sync.py` before commit
4. ✅ Coordinate with pre-commit hook (automatic validation)

**Key Change**: Reference implementation map instead of deleted master plan.

**Reference**: See `.github/prompts/cortex-builder.prompt.md`

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
1. ✅ Plan phases based on `cortex-impl-map.yaml → phases_implementation_status:` section
2. ✅ Account for phase dependencies (unchanged)
3. ✅ **NEW**: Ensure phase_tracker in cortex-impl-map stays in sync (validator does this)
4. ✅ No longer need to plan dual updates

**Key Change**: Simplified planning - one source to track.

---

### cortex-review-*.md (All Review Agents)

**Updated Responsibilities**:
1. ✅ Review phase execution (unchanged)
2. ✅ Verify AC-ID specs in `cortex-impl-map.yaml → phases_implementation_status:` section
3. ✅ **NEW**: Trust validator for sync consistency (no more manual checks)
4. ✅ Report AC-ID counts from single source

**Key Change**: Trust automation, focus on code quality.

**Reference Files**: These agents remain unchanged - they work through cortex-builder which now uses unified architecture.

---

### cortex-reviewer.md

**Updated Responsibilities**:
1. ✅ Review implementation against specs in `cortex-impl-map.yaml → phases_implementation_status:`
2. ✅ Verify tests match testing requirements (unchanged)
3. ✅ **NEW**: Reference validator output for sync checks (not manual)
4. ✅ Approve phase completion when all AC-IDs done

**Key Change**: Reduced sync verification workload.

---

## New Workflow Pattern (All Agents)

### Phase Load
```yaml
# Load from single source
impl_map = load_yaml("cortex-impl-map.yaml")
phases = impl_map['phases_implementation_status']
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

# Save to cortex-impl-map.yaml ONLY
save_yaml(impl_map, "cortex-impl-map.yaml")

# Validator runs automatically on commit
# No manual sync checks needed
```

### Validation
```python
# Trust the validator
# It runs automatically:
#   - Before each commit (pre-commit hook)
#   - On demand: python3 scripts/validate-phase-sync.py
#   - Auto-fixes safe issues

# If agent job involves cortex-impl-map.yaml changes:
#   Assume validator will catch issues
#   No need to manually verify sync
```

---

## Handoff Pattern (Between Agents)

### Before Handoff
```
Agent A:
  1. Edit cortex-master.yaml (OLD - NOW DELETED)
  2. Manually verify sync with phase-XX.yaml (if separate)
  3. Commit (hopefully consistent)
  4. Document status in report

Agent B receives:
  - Hopes everything synced correctly
  - May discover sync issues during work
```

### After Handoff (Current Pattern - 2026-01-20)
```
Agent A:
  1. Edit cortex-impl-map.yaml → phases_implementation_status: section
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

- **Architecture**: `_workspaces/roadmap/CORTEX-IMPL-MAP-SUMMARY.md`
- **Status**: `_workspaces/roadmap/cortex-impl-map.yaml`
- **Implementation Guide**: `.github/prompts/cortex-builder.prompt.md`
- **Builder Prompt**: `.github/prompts/cortex-builder.prompt.md`

---

## Compatibility Matrix

### Implementation Map Compatibility

| Component | Before | Current | Compatible? |
|-----------|--------|---------|-------------|
| cortex-builder.prompt.md | cortex-master.yaml | cortex-impl-map.yaml | ✅ Use current |
| cortex-impl-map.yaml | N/A | v3.1-corrected | ✅ Authority source |
| phase-XX.yaml files | Required | Archived | ✅ Read-only reference available |
| Pre-commit hook | Basic SSOT checks | Phase sync validation | ✅ Enhanced |
| Validation scripts | None | validate-impl-map.py | ✅ New capability |
| All agents | cortex-master refs | cortex-impl-map refs | ✅ Works (redirect reference) |
| CI/CD | No auto-validation | Auto-validates on commit | ✅ Improved |

---

## Testing the New Workflow

### Agent Test Checklist

When testing new implementation map workflow:

- [ ] Agent loads `cortex-impl-map.yaml` successfully
- [ ] Agent can read `phases_implementation_status:` section
- [ ] Agent extracts AC-IDs from implementation status section
- [ ] Agent edits phase status/AC-IDs directly in cortex-impl-map.yaml
- [ ] Agent commits changes
- [ ] Pre-commit hook validates (should pass)
- [ ] Validator output shows consistency
- [ ] Next agent receives consistent state (no sync issues)

---

## Migration Guide (For Agent Teams)

### Step 1: Understand New Architecture

**Read**: `cortex-impl-map.yaml` documentation (10 min)

Key points:
- Single source of truth in cortex-impl-map.yaml
- phases_implementation_status: section contains all specs
- Validator prevents sync issues
- Pre-commit hook auto-validates

### Step 2: Update References

**Update prompt references**:
```
Old: ".github/prompts/cortex-builder.prompt.md (cortex-master.yaml)"
New: ".github/prompts/cortex-builder.prompt.md (cortex-impl-map.yaml)"
```

**Update file references**:
```
Old: "_workspaces/roadmap/phases/phase-XX.yaml"
New: "cortex-impl-map.yaml → phases_implementation_status.PHASE-XX"
```

### Step 3: Test New Workflow

**Create test phase change**:
1. Load cortex-impl-map.yaml
2. Edit `phases_implementation_status.PHASE-TEST.status = 'IN_PROGRESS'`
3. Commit (validator should pass)
4. Verify pre-commit hook ran
5. Revert test

### Step 4: Train Team

**Share with team**:
- Implementation map file location
- New file references
- How validator works
- Pre-commit hook behavior

---

## FAQ for Agents

### Q: Where do I load phase specs now?

**A**: cortex-impl-map.yaml → phases_implementation_status: section. Example:
```python
impl_map = load_yaml("cortex-impl-map.yaml")
phase = impl_map['phases_implementation_status']['PHASE-01']
# All specs here: title, status, ac_ids, testing, etc.
```

### Q: Do I still need phase-XX.yaml files?

**A**: Not for active work. They're archived in `_archives/phase-yamls-v1/` for reference.

### Q: What if I find a sync issue?

**A**: Run validator:
```bash
python3 scripts/validate-impl-map.py --verbose
python3 scripts/validate-impl-map.py --fix
```

### Q: How do I know if my changes are synced?

**A**: Pre-commit hook validates automatically. If commit is accepted, state is guaranteed consistent.

### Q: Can I bypass the validator?

**A**: Yes: `git commit --no-verify` (use last resort only). Then manually verify:
```bash
python3 scripts/validate-impl-map.py
```

### Q: What's the current builder prompt?

**A**: `.github/prompts/cortex-builder.prompt.md` - includes current workflow guidance with cortex-impl-map.yaml.

---

## Support & Troubleshooting

### Issue: Validator fails on commit

**Solution**:
```bash
python3 scripts/validate-impl-map.py --verbose
python3 scripts/validate-impl-map.py --fix
git add .
git commit -m "fix: implementation map sync"
```

### Issue: Can't find phase spec

**Solution**:
```bash
grep -A 50 "PHASE-XX:" cortex-impl-map.yaml | grep -A 5 "ac_ids:"
```

### Issue: Pre-commit hook too slow

**Note**: Validator runs in <1 second on modern hardware. If slow, check:
```bash
python3 scripts/validate-impl-map.py --verbose
# Check for large phase sections or large AC counts
```

### Issue: Old phase-XX.yaml referenced in code

**Solution**: Update references to use cortex-impl-map.yaml:
```python
# OLD
phase = load_yaml(f"_workspaces/roadmap/phases/phase-{n}.yaml")

# NEW
impl_map = load_yaml("_workspaces/roadmap/cortex-impl-map.yaml")
phase = impl_map['phases_implementation_status'][f'PHASE-{n}']
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

1. ✅ Load phase specs from `cortex-impl-map.yaml → phases_implementation_status:` (not separate phase-XX.yaml)
2. ✅ Edit directly in cortex-impl-map.yaml (atomic single-file updates)
3. ✅ Trust pre-commit hook for sync validation (automatic, no manual checks)
4. ✅ Run `validate-impl-map.py` if issues appear (diagnostic tool)
5. ✅ Reference current builder prompt (`.github/prompts/cortex-builder.prompt.md`)

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

