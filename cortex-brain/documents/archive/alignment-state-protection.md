# Alignment State Protection Implementation Guide

**Version:** 2.0  
**Author:** Asif Hussain  
**Status:** PRODUCTION (Machine-Local Approach)  
**Priority:** High  
**Updated:** December 6, 2025

---

## ⚠️ IMPORTANT: Solution Changed

**Original Approach (v1.0 - DEPRECATED):** Auto-commit alignment state after every run  
**Current Approach (v2.0 - PRODUCTION):** Machine-local state with `.gitignore`

**Why Changed:**
- Alignment state contains machine-specific file checksums
- Machine A's checksums don't match Machine B's files
- Sharing state via git causes constant merge conflicts
- Each machine should maintain independent state

**See:** `multi-machine-alignment.md` for complete implementation guide

---

## Problem Statement

The align orchestrator successfully validates system health and creates/updates `cortex-brain/admin/alignment-state.json`, but this state file is never committed. When users pull/merge from remote, the uncommitted alignment state is overwritten, causing:

1. **Lost Performance:** Incremental scans (2s) revert to full scans (15s) - 650% slower
2. **Lost State:** File checksums, validation scores, performance metrics disappear
3. **User Confusion:** "Why is everything unwired after merge?"
4. **Manual Overhead:** Users must manually manage state persistence

---

## Root Cause Analysis

```
User Workflow (BROKEN):
1. Run align → alignment-state.json created/updated ✅
2. Git status → File shows as modified (uncommitted) ⚠️
3. Git pull → Remote overwrites local state ❌
4. Git merge → Alignment state lost ❌
5. Run align → Full scan required (slow) ⚠️
```

**Why It Happens:**
- `align_utility.py` saves state via `AlignmentStateManager.save()`
- No git operations performed after save
- State exists only in working directory
- Git pull/merge treats as untracked/conflicting file

---

## Solution: 3-Part Protection

### Part 1: Post-Align Commit Hook ⚠️ NOT YET IMPLEMENTED

Add automatic commit of alignment state after successful run.

**Location:** `src/operations/modules/admin/align_utility.py`

**Implementation:**

```python
def _commit_alignment_state(self, state_path: Path, cortex_root: Path) -> bool:
    """
    Commit alignment state after successful run.
    
    Args:
        state_path: Path to alignment-state.json
        cortex_root: CORTEX repository root
    
    Returns:
        True if committed successfully, False otherwise
    """
    if not state_path.exists():
        logger.warning("Alignment state file not found, skipping commit")
        return False
    
    try:
        import subprocess
        
        # Add alignment state file
        result = subprocess.run(
            ["git", "add", str(state_path)],
            check=True,
            cwd=cortex_root,
            capture_output=True,
            text=True
        )
        
        # Commit with skip CI flag
        result = subprocess.run(
            ["git", "commit", "-m", "chore: update alignment state [skip ci]", "--no-verify"],
            check=True,
            cwd=cortex_root,
            capture_output=True,
            text=True
        )
        
        logger.info("✅ Alignment state committed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        # Not a git repository or nothing to commit
        logger.debug(f"Could not commit alignment state: {e.stderr}")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Failed to commit alignment state: {e}")
        return False
```

**Integration Point:**

```python
# In run_align_utility() after successful alignment
if result['success']:
    # Existing code...
    safe_print(report_text)
    
    # NEW: Commit alignment state
    if utility.context_type == "admin":
        state_path = cortex_root / "cortex-brain" / "admin" / "alignment-state.json"
        _commit_alignment_state(state_path, cortex_root)
```

---

### Part 2: Git Merge Strategy ✅ IMPLEMENTED

Configure git to preserve local alignment state during merge.

**Location:** `.gitattributes`

**Implementation:** ✅ DONE

```properties
# Brain state files (preserve local changes during merge)
cortex-brain/admin/alignment-state.json merge=ours
```

**How It Works:**
- `merge=ours`: During merge conflicts, keep local version
- Rationale: Alignment state is workspace-specific, not shared
- Each workspace has unique file checksums, feature states
- Remote state is irrelevant to local workspace

---

### Part 3: SKULL Rule Protection ✅ IMPLEMENTED

Add Brain Protection Rule to enforce alignment state persistence.

**Location:** `cortex-brain/brain-protection-rules.yaml`

**Implementation:** ✅ DONE

```yaml
tier0_instincts:
  # ... existing instincts
  - ALIGNMENT_STATE_PROTECTION  # Added

brain_state_files:
  - conversation-history.jsonl
  - conversation-context.jsonl
  - events.jsonl
  - development-context.yaml
  - protection-events.jsonl
  - alignment-state.json  # Added
```

**Rule Definition:** ⚠️ NEEDS YAML RULE ADDITION

(See full rule in Evidence Template below - needs to be added to YAML manually)

---

## Implementation Checklist

### Completed ✅
- [x] Add `alignment-state.json` to `brain_state_files` list
- [x] Add `ALIGNMENT_STATE_PROTECTION` to `tier0_instincts`
- [x] Add `merge=ours` strategy to `.gitattributes`

### Pending ⚠️
- [ ] Add `_commit_alignment_state()` function to `align_utility.py`
- [ ] Integrate commit hook into `run_align_utility()`
- [ ] Add SKULL rule definition to `brain-protection-rules.yaml`
- [ ] Add pre-pull validation to commit orchestrator
- [ ] Update align documentation with automatic commit behavior
- [ ] Test alignment → commit → pull → align workflow

---

## Expected User Experience

### Before Fix (BROKEN)
```
$ python -m src.operations.align
✅ System healthy (8/8 checks passed)
📝 Alignment state saved

$ git status
modified: cortex-brain/admin/alignment-state.json (uncommitted)

$ git pull
⚠️  Local state overwritten

$ python -m src.operations.align
🔄 Full scan (15.2s) ← Slow because checksums lost
```

### After Fix (CORRECT)
```
$ python -m src.operations.align
✅ System healthy (8/8 checks passed)
📝 Alignment state saved
💾 Alignment state committed [abc123]

$ git status
nothing to commit, working tree clean

$ git pull
✅ Local alignment state preserved (merge=ours)

$ python -m src.operations.align
🔄 Incremental scan (2.1s, 3 features checked, 89 skipped) ← Fast
```

---

## Performance Impact

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| First align | 15s | 15s | 0% (baseline) |
| Incremental align | N/A (lost) | 2s | N/A |
| After pull/merge | 15s | 2s | **650% faster** |
| State persistence | Manual | Automatic | **100% automated** |

---

## Technical Details

### Alignment State Structure
```json
{
  "version": "3.2",
  "last_alignment": "2025-12-06T10:30:00",
  "last_full_scan": "2025-12-06T10:30:00",
  "scan_mode": "incremental",
  "context_type": "admin",
  "file_checksums": {
    "src/operations/align.py": {
      "sha256": "abc123...",
      "last_modified": "2025-12-06T10:00:00",
      "size_bytes": 23456
    }
  },
  "feature_scores": { ... },
  "performance_metrics": {
    "last_run_duration_seconds": 2.1,
    "features_checked": 3,
    "features_skipped": 89,
    "cache_hit_rate": 0.967
  }
}
```

### Why Checksums Matter
- **Timestamp-based detection:** Unreliable (git operations touch files)
- **SHA256 checksums:** Detects actual content changes
- **Performance:** Only re-validate changed files (97% cache hit rate)

---

## Edge Cases

1. **Not a git repository:** Commit silently fails, alignment still works
2. **Detached HEAD:** Commit fails, user warned but alignment succeeds
3. **Merge conflicts:** `merge=ours` prevents conflicts automatically
4. **Fresh clone:** No state file exists, full scan runs (expected)

---

## Rollback Plan

If auto-commit causes issues:

1. Remove commit hook from `align_utility.py`
2. Keep `.gitattributes` merge strategy (harmless)
3. Keep SKULL rule (informational only)
4. Document manual commit recommendation

---

## Related Files

- `src/operations/modules/admin/align_utility.py` - Main alignment logic
- `src/operations/modules/admin/alignment_state.py` - State management
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `.gitattributes` - Git merge strategies

---

## Next Steps

**Priority 1 (Required):**
1. Implement `_commit_alignment_state()` in `align_utility.py`
2. Add function call after successful alignment
3. Test full workflow: align → commit → pull → align

**Priority 2 (Enhancement):**
4. Add SKULL rule definition to YAML
5. Add pre-pull validation
6. Update documentation

**Priority 3 (Future):**
7. Consider state versioning/migration
8. Add state analytics to dashboard
9. Track alignment state across git branches
