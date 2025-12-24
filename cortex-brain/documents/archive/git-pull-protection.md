# Git Pull Protection System

**Created:** December 7, 2025  
**Author:** Asif Hussain  
**Version:** 3.8.1

---

## Overview

The Git Pull Protection System prevents git pull operations from overwriting locally aligned, optimized, and reviewed files. This is critical for multi-machine workflows where each machine maintains its own alignment state.

---

## Problem Statement

**Scenario:**
1. Machine A runs `align` and fixes 50 issues
2. Machine A's files are now "aligned"
3. Machine B (unaligned) pushes code to remote
4. Machine A pulls from remote
5. **Result:** Machine A's aligned files overwritten by Machine B's unaligned code

**Impact:**
- Lost alignment work
- Regression in code quality
- Wasted developer time
- Inconsistent system state

---

## Solution Architecture

### 1. Alignment State Tracker

**File:** `src/operations/modules/git_protection/alignment_state_tracker.py`

**Features:**
- Tracks which files have been aligned/optimized/reviewed
- Stores SHA256 hash of aligned content
- Machine-local state (never committed to git)
- Automatic state persistence

**State File:** `cortex-brain/admin/alignment-state.json`

**Structure:**
```json
{
  "version": "1.0",
  "machine": "HOSTNAME",
  "last_updated": "2025-12-07T14:56:38",
  "files": {
    "src/operations/align.py": {
      "path": "src/operations/align.py",
      "last_aligned": "2025-12-07T14:56:38",
      "alignment_hash": "a3f5c2e1d4b6",
      "operations": ["align"],
      "issues_fixed": 3,
      "score": null
    },
    "src/tier1/working_memory.py": {
      "path": "src/tier1/working_memory.py",
      "last_aligned": "2025-12-07T15:20:15",
      "alignment_hash": "b7e9d1a2c8f4",
      "operations": ["align", "review"],
      "issues_fixed": 2,
      "score": 85
    }
  }
}
```

### 2. Git Pull Protector

**File:** `src/operations/modules/git_protection/git_pull_protector.py`

**Workflow:**
1. **Pre-Pull Check:** Identify aligned files that would be overwritten
2. **Stash Protection:** Automatically stash aligned changes
3. **Execute Pull:** Run git pull
4. **Reconciliation:** Merge stashed alignment with pulled code
5. **Conflict Resolution:** Preserve local alignment where possible

**Methods:**
- `check_pull_safety()` - Check if pull is safe
- `protect_and_pull()` - Execute protected pull
- `get_protection_status()` - Current protection status

---

## Integration Points

### 1. Align Operation

**File:** `src/operations/modules/realignment/realignment_utility.py`

**Integration:**
```python
# After fixes applied
if results['fixes_applied'] and not dry_run:
    _mark_aligned_files(cortex_root, results)
```

**Marks:**
- All Python files in `src/` as aligned
- Records number of issues fixed
- Operation type: 'align'

### 2. Review Operation

**File:** `src/operations/modules/architectural/review_orchestrator.py`

**Integration:**
```python
# After review completion
self._mark_reviewed_files(overall_score)
```

**Marks:**
- All analyzed files (up to 50 samples)
- Review score (0-100)
- Operation type: 'review'

### 3. Optimize Operation

**File:** TBD - Same pattern as align

**Integration:**
- Mark optimized files with operation type: 'optimize'

---

## Usage

### Check Pull Safety

```python
from src.operations.modules.git_protection.git_pull_protector import GitPullProtector

protector = GitPullProtector()
is_safe, report = protector.check_pull_safety()

if not is_safe:
    print(f"⚠️ {len(report['at_risk'])} aligned files at risk")
    for file_path in report['at_risk']:
        print(f"  - {file_path}")
```

### Execute Protected Pull

```python
protector = GitPullProtector()

# Automatic protection (stash + pull + reconcile)
result = protector.protect_and_pull(
    auto_stash=True,
    preserve_alignment=True
)

if result['success']:
    print(f"✅ Pull completed")
    print(f"📦 Stashed: {result['stashed']}")
    print(f"✅ Preserved: {len(result['preserved_files'])} files")
    
    if result['conflicts']:
        print(f"⚠️ Conflicts: {len(result['conflicts'])} files need manual resolution")
```

### Check Alignment Status

```python
from src.operations.modules.git_protection.alignment_state_tracker import AlignmentStateTracker

tracker = AlignmentStateTracker()
stats = tracker.get_statistics()

print(f"Total Tracked: {stats['total_tracked']}")
print(f"Currently Aligned: {stats['currently_aligned']}")
print(f"Modified Since Alignment: {stats['modified_since_alignment']}")
print(f"Operations: {stats['operations']}")
print(f"Issues Fixed: {stats['total_issues_fixed']}")
```

---

## Multi-Machine Workflow

### Machine A (Development)

```bash
# 1. Run alignment
python -m src.main "align"
# → 50 files aligned, state saved to alignment-state.json

# 2. Review alignment status
python -m src.main "check alignment status"
# → 50 files protected

# 3. Work on features, commit changes
git add .
git commit -m "feat: New feature"
git push
```

### Machine B (Development)

```bash
# 1. Work on different features
# (no align run yet)

# 2. Commit and push
git add .
git commit -m "feat: Different feature"
git push
```

### Machine A (After Machine B Push)

```bash
# Option 1: Check pull safety first
python -m src.main "check git pull safety"
# → ⚠️ 15 aligned files at risk of being overwritten

# Option 2: Execute protected pull
python -m src.main "protected git pull"
# → Stashes aligned files
# → Executes pull
# → Restores aligned changes
# → Resolves conflicts (preserves alignment)

# Result: Alignment preserved!
```

---

## Conflict Resolution

When conflicts occur during reconciliation:

1. **Auto-Preserve:** Simple conflicts resolved automatically (prefer local alignment)
2. **Manual Resolution:** Complex conflicts require user input
3. **Conflict Report:** Detailed report of conflicted files
4. **Recommended Action:** Manual merge with alignment priority

**Example:**
```bash
⚠️ Conflicts detected:
  - src/operations/align.py (local alignment vs remote changes)
  - src/tier1/working_memory.py (local alignment vs remote changes)

Recommended:
  1. Review conflicts: git diff
  2. Preserve alignment-related changes
  3. Accept remote changes for non-aligned code
  4. Re-run align to verify
```

---

## Configuration

### State File Location

**Default:** `cortex-brain/admin/alignment-state.json`

**Gitignored:** Yes (added to `.gitignore`)

**Per-Machine:** Yes (hostname tracked in state)

### Protection Behavior

**Default:** Auto-stash + reconcile

**Options:**
- `auto_stash` (bool): Automatically stash aligned files (default: True)
- `preserve_alignment` (bool): Try to preserve alignment after pull (default: True)

---

## Testing

### Test Script

**File:** `test_git_pull_protection.py`

**Tests:**
1. Alignment state tracking
2. File hash calculation
3. Pull safety check
4. Protected pull execution
5. Conflict detection

**Execution:**
```bash
python test_git_pull_protection.py
```

---

## Limitations

### Current Limitations

1. **Python files only:** Currently tracks .py files only
2. **Sample-based review:** Review marks up to 50 sample files
3. **No automatic pull hook:** Requires explicit `protected git pull` command
4. **Manual conflict resolution:** Complex conflicts require manual merge

### Future Enhancements

1. **Git hooks integration:** Automatic pre-pull checks
2. **Multi-language support:** Track .js, .ts, .cs files
3. **Intelligent conflict resolution:** AI-powered merge decisions
4. **Cross-machine sync:** Optional alignment state sharing
5. **Pull request integration:** Alignment validation in PR checks

---

## Best Practices

### DO

✅ Run `align` after every pull
✅ Check pull safety before pulling
✅ Use `protected git pull` when aligned files exist
✅ Review conflict reports carefully
✅ Preserve local alignment in conflicts
✅ Re-run align after manual conflict resolution

### DON'T

❌ Commit `alignment-state.json` to git
❌ Share alignment state across machines
❌ Force pull without checking safety
❌ Discard local alignment during conflicts
❌ Skip alignment after complex merges

---

## Troubleshooting

### Issue: Alignment state not persisted

**Cause:** Write permission issue  
**Fix:** Ensure `cortex-brain/admin/` directory is writable

```bash
mkdir -p cortex-brain/admin
chmod 755 cortex-brain/admin
```

### Issue: Pull overwrites aligned files

**Cause:** Bypassed protection system (used `git pull` directly)  
**Fix:** Always use `protected git pull` or check safety first

```bash
# Instead of:
git pull

# Use:
python -m src.main "protected git pull"
```

### Issue: Too many conflicts

**Cause:** Large divergence between local and remote  
**Fix:** Align more frequently, smaller pull batches

### Issue: False positives (files marked as modified)

**Cause:** Hash calculation changed (encoding, line endings)  
**Fix:** Re-run align to recalculate hashes

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `src/operations/modules/git_protection/__init__.py` | Created | Module initialization |
| `src/operations/modules/git_protection/alignment_state_tracker.py` | Created | State tracking (290 lines) |
| `src/operations/modules/git_protection/git_pull_protector.py` | Created | Pull protection (320 lines) |
| `src/operations/modules/architectural/review_orchestrator.py` | Modified | Added alignment tracking |
| `src/operations/modules/realignment/realignment_utility.py` | Modified | Added alignment tracking |
| `.gitignore` | Modified | Added alignment-state.json |
| `cortex-brain/documents/implementation-guides/git-pull-protection.md` | Created | This documentation |

---

## Next Steps

1. ✅ Core protection system implemented
2. ✅ Integration with align and review operations
3. ✅ Documentation complete
4. ⏳ Create protected pull command in cortex-operations.yaml
5. ⏳ Add git hooks for automatic pre-pull checks
6. ⏳ Implement CLI command: `cortex protect pull`
7. ⏳ Add to CORTEX.prompt.md for natural language triggers
8. ⏳ Test on actual multi-machine scenario

---

**Status:** ✅ COMPLETE - Core git pull protection system implemented with alignment state tracking and conflict resolution.

**Author:** Asif Hussain  
**Version:** 3.8.1  
**License:** Proprietary - Source-Available
