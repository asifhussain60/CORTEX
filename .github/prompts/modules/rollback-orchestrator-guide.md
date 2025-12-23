# Rollback Orchestrator Guide

**Purpose:** Safe git rollback to previous checkpoints with validation and user confirmation  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The Rollback Orchestrator provides a safe, intelligent workflow for rolling back repository changes to previous checkpoints:
- List available checkpoints from TDD workflow phases
- Validate checkpoint exists before rollback
- Safety checks for uncommitted changes and merge conflicts
- User confirmation with diff preview
- Dry-run mode for preview without execution
- Force mode to bypass safety checks (use with caution)

**Key Principle:** Checkpoints are safety points created during TDD workflows (pre-work, post-work, tdd-red, tdd-green, refactoring). Rollback lets you restore to these points if something goes wrong.

---

## 🚀 Commands

**Natural Language Triggers:**
- `rollback to <checkpoint-id>`
- `rollback <checkpoint-id>`
- `restore to checkpoint`
- `undo to checkpoint`
- `revert to checkpoint`

**Use Cases:**
- Rolling back after failed refactoring
- Restoring to last GREEN phase in TDD
- Recovering from accidental code deletion
- Returning to known working state
- Testing different implementation approaches

---

## 📊 Workflow Steps

### Phase 1: Checkpoint Validation (2s)
```
Verify checkpoint exists:
- Check PhaseCheckpointManager for checkpoint_id
- Verify checkpoint has valid metadata
- Confirm git commit SHA exists
- Return validation result
```

### Phase 2: Safety Checks (5s)
```
Validate git repository state:
1. Check for uncommitted changes
   - If found: Warn user, require commit/stash first
2. Check for merge in progress
   - If found: Require merge completion or abort first
3. Check working tree is clean
   - If dirty: Cannot proceed
```

### Phase 3: Preview Changes (10s)
```
Generate diff between current state and checkpoint:
1. Run git diff HEAD <checkpoint-id>
2. Show first 1000 characters of diff
3. Display file count and line changes
4. Ask user: "Rollback to '<checkpoint-id>'? (yes/no)"
```

### Phase 4: User Confirmation (user-dependent)
```
Wait for user input:
- "yes" → Proceed to execution
- "no" → Cancel rollback, return success=false
- Invalid → Prompt again
```

### Phase 5: Execute Rollback (5s)
```
Perform git reset:
1. git reset --hard <checkpoint-id>
2. Verify reset success
3. Create post-rollback checkpoint (optional)
4. Report rollback status
```

---

## 🔧 Configuration

**Config File:** `cortex.config.json`

```json
{
  "rollback_orchestrator": {
    "require_confirmation": true,
    "show_diff_preview": true,
    "create_post_rollback_checkpoint": true,
    "max_checkpoints_displayed": 10,
    "checkpoint_retention_days": 30
  }
}
```

**Options:**
- `require_confirmation` - Require user confirmation before rollback (default: `true`)
- `show_diff_preview` - Show diff preview before confirmation (default: `true`)
- `create_post_rollback_checkpoint` - Create checkpoint after rollback (default: `true`)
- `max_checkpoints_displayed` - Maximum checkpoints to list (default: `10`)
- `checkpoint_retention_days` - Days to keep checkpoints (default: `30`)

---

## 📈 Examples

### Example 1: Safe Rollback with Preview
```
User: "rollback to tdd-green-20251129-140000"

CORTEX:
  🔍 Validating checkpoint...
  ✅ Checkpoint 'tdd-green-20251129-140000' found
  
  🔒 Running safety checks...
  ✅ No uncommitted changes
  ✅ No merge in progress
  ✅ Working tree clean
  
  📊 Preview of changes to be discarded:
  ============================================================
  src/feature.py | 25 ++++++-------------------
  tests/test_feature.py | 10 ----------
  2 files changed, 7 insertions(+), 28 deletions(-)
  ============================================================
  
  ❓ Rollback to 'tdd-green-20251129-140000'? (yes/no): yes
  
  ⏪ Rolling back...
  ✅ Rollback successful!
  
  Summary:
  • Restored to: tdd-green-20251129-140000
  • Commit SHA: abc1234
  • Phase: GREEN (all tests passing)
  • Created: 2025-11-29 14:00:00
```

### Example 2: Rollback Blocked (Uncommitted Changes)
```
User: "rollback to pre-work-20251129-130000"

CORTEX:
  🔍 Validating checkpoint...
  ✅ Checkpoint 'pre-work-20251129-130000' found
  
  🔒 Running safety checks...
  ❌ Safety check failed: Uncommitted changes detected
  
  The following files have uncommitted changes:
    - src/feature.py
    - tests/test_feature.py
  
  🛠️ Resolution Options:
  1. Commit changes: git add . && git commit -m "message"
  2. Stash changes: git stash
  3. Force rollback: rollback --force (DANGER: loses changes)
  
  ⚠️ Cannot proceed. Please commit or stash changes first.
```

### Example 3: Dry-Run Mode (Preview Only)
```
User: "rollback to refactoring-20251129-150000 --dry-run"

CORTEX:
  🔍 Validating checkpoint...
  ✅ Checkpoint 'refactoring-20251129-150000' found
  
  📊 Dry-run preview (no changes will be made):
  ============================================================
  WOULD ROLLBACK TO: refactoring-20251129-150000
  
  Changes to be discarded:
  src/utils.py | 50 ++++++++++++++++++++++++++++++++++++++++++++
  tests/test_utils.py | 30 +++++++++++++++++++++++++
  2 files changed, 80 insertions(+)
  ============================================================
  
  ℹ️ This is a dry-run. No changes were made.
  ℹ️ To execute rollback, run: rollback to refactoring-20251129-150000
```

### Example 4: Force Rollback (Bypass Safety)
```
User: "rollback to tdd-red-20251129-120000 --force"

CORTEX:
  🔍 Validating checkpoint...
  ✅ Checkpoint 'tdd-red-20251129-120000' found
  
  ⚠️ FORCE MODE: Bypassing safety checks
  ⚠️ WARNING: You have uncommitted changes that will be lost!
  
  ⏪ Executing forced rollback...
  ✅ Forced rollback completed
  
  Summary:
  • Restored to: tdd-red-20251129-120000
  • Phase: RED (tests failing as expected)
  • ⚠️ Uncommitted changes discarded (cannot be recovered)
```

---

## 🎓 Key Concepts

### Checkpoints vs Commits
**Checkpoints** are lightweight git tags created at TDD workflow phases:
- `pre-work-YYYYMMDD-HHMMSS` - Before starting work
- `tdd-red-YYYYMMDD-HHMMSS` - After writing failing test
- `tdd-green-YYYYMMDD-HHMMSS` - After making test pass
- `refactoring-YYYYMMDD-HHMMSS` - After refactoring
- `post-work-YYYYMMDD-HHMMSS` - After completing work

**Commits** are permanent git history entries. Checkpoints reference commits but are temporary (30-day retention).

### Safety Guarantees
1. **Uncommitted Changes** - Rollback blocked if working tree dirty
2. **Merge Conflicts** - Rollback blocked if merge in progress
3. **User Confirmation** - Always requires "yes" confirmation (unless forced)
4. **Diff Preview** - Shows exactly what will be lost
5. **Dry-Run Mode** - Test rollback without executing

### When to Use Rollback
✅ **Good Use Cases:**
- Failed refactoring (rollback to last GREEN)
- Experimental implementation didn't work (rollback to pre-work)
- Accidental code deletion (rollback to recent checkpoint)
- Testing different approaches (rollback, try again)

❌ **Bad Use Cases:**
- Reverting committed changes (use `git revert` instead)
- Undoing pushed changes (creates divergent history)
- Fixing bugs (write tests and fix properly)
- Avoiding merge conflicts (resolve conflicts properly)

---

## 🔍 Troubleshooting

### Issue: "Checkpoint not found"
**Cause:** Checkpoint ID doesn't exist or was expired (>30 days)  
**Solution:** Use `list checkpoints` to see available checkpoints

### Issue: "Safety check failed: Uncommitted changes"
**Cause:** Working tree has uncommitted files  
**Solution:** Commit changes (`git add . && git commit`) or stash (`git stash`)

### Issue: "Merge in progress - resolve conflicts first"
**Cause:** Git merge operation incomplete  
**Solution:** Complete merge (`git commit`) or abort (`git merge --abort`)

### Issue: "Git reset failed"
**Cause:** Git command error (corrupted repo, invalid commit SHA)  
**Solution:** Check git status, verify repo integrity (`git fsck`)

---

## 🧪 Testing

**Test Files:**
- `tests/orchestrators/test_rollback_orchestrator_foundation.py` - Core functionality
- `tests/orchestrators/test_rollback_orchestrator_extended.py` - Safety checks, confirmation

**Key Test Scenarios:**
1. Checkpoint validation (exists/doesn't exist)
2. Safety checks (uncommitted changes, merge in progress)
3. User confirmation (yes/no/invalid input)
4. Dry-run mode (preview without execution)
5. Force mode (bypass safety checks)
6. Git reset execution (success/failure)

**Run Tests:**
```bash
pytest tests/orchestrators/test_rollback_orchestrator*.py -v
```

---

## 🔗 Integration

**Dependencies:**
- `PhaseCheckpointManager` - Manages checkpoint metadata and storage
- `GitCheckpointSystem` - Creates/lists git tags for checkpoints
- `CommitOrchestrator` - Works alongside (commit before rollback recommended)

**Called By:**
- Interactive planner during TDD workflow
- User natural language commands ("rollback to X")
- Error recovery workflows (auto-suggest rollback on failures)

**Calls:**
- `PhaseCheckpointManager.list_checkpoints()` - Get available checkpoints
- `git status --porcelain` - Check for uncommitted changes
- `git diff HEAD <checkpoint>` - Generate diff preview
- `git reset --hard <checkpoint>` - Execute rollback

---

## 📚 Related Documentation

- **Commit Orchestrator Guide** - Syncing with remote before rollback
- **TDD Mastery Guide** - Understanding checkpoint creation during TDD
- **Git Checkpoint System** - Low-level checkpoint mechanics
- **Phase Checkpoint Manager** - Checkpoint metadata and storage

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions) - See LICENSE  
**Repository:** https://github.com/asifhussain60/CORTEX
