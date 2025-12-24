# Rollback Commands - User Guide

**For:** CORTEX Users  
**Version:** 1.0.0  
**Date:** 2025-11-28

---

## Overview

Rollback commands let you return to previous checkpoints in your workflow when things go wrong. Think of checkpoints as "save points" that are automatically created as you progress through Planning, TDD, or other workflows.

**Use rollback when:**
- ❌ Implementation went in wrong direction → Rollback to DoR
- ❌ Refactoring broke tests → Rollback to GREEN phase
- ❌ Need to try different approach → Rollback to last good state
- ❌ Accidentally committed wrong changes → Rollback before commit

---

## Quick Start

### 1. List Available Checkpoints

**Command:**
```
list checkpoints for session feature-auth-001
```

**Response:**
```
📋 Available checkpoints for session feature-auth-001:

1. dor-checkpoint (DoR phase)
   Created: 2025-11-28 10:30:00
   Commit: abc123
   ✅ Requirements validated, 5 acceptance criteria

2. impl-checkpoint-1 (Implementation phase)
   Created: 2025-11-28 11:15:00
   Commit: def456
   ✅ 3 features completed, 25 tests passing

3. impl-checkpoint-2 (Implementation phase)
   Created: 2025-11-28 12:00:00
   Commit: ghi789
   ✅ All features complete, 30 tests passing
```

### 2. Rollback to Checkpoint

**Command:**
```
rollback to checkpoint dor-checkpoint session feature-auth-001
```

**Response:**
```
🔄 Rolling back to checkpoint: dor-checkpoint

⚠️  Warning: Uncommitted changes detected
Files: src/auth.py, src/login.py

❓ Continue with rollback? This will stash uncommitted changes.
   Type 'yes' to confirm, or use 'rollback --force' to bypass.
```

### 3. Preview Before Rollback (Dry-Run)

**Command:**
```
rollback to dor-checkpoint --dry-run
```

**Response:**
```
🔍 Dry-run mode: Preview of changes

Would rollback from: ghi789 (current)
Would rollback to:   abc123 (dor-checkpoint)

Files that will be affected:
- src/auth.py (modified → reverted)
- src/login.py (new → removed)
- tests/test_auth.py (modified → reverted)

Tests status after rollback:
✅ 25/25 passing (currently: 23/30 passing)

No actual changes made. Use 'rollback to dor-checkpoint' to execute.
```

---

## Command Formats

### Standard Format
```
rollback to checkpoint {checkpoint-id} session {session-id}
```

**Example:**
```
rollback to checkpoint dor-checkpoint session feature-auth-001
```

### Session Format
```
rollback session {session-id} to {checkpoint-id}
```

**Example:**
```
rollback session feature-auth-001 to dor-checkpoint
```

### Shorthand Format
```
rollback {checkpoint-id}
```

**Example:**
```
rollback dor-checkpoint
```
*(Uses current session if only one active)*

---

## Flags and Options

### --dry-run
Preview changes without executing rollback.

**Usage:**
```
rollback to dor-checkpoint --dry-run
```

**When to use:**
- Before important rollbacks
- To see what files will change
- To check test status after rollback

### --force
Bypass safety checks and confirmation prompts.

**Usage:**
```
rollback to dor-checkpoint --force
```

**⚠️ Caution:**
- Uncommitted changes will be stashed
- No confirmation prompt
- Cannot be undone easily

**When to use:**
- Emergency rollback
- Automated scripts
- After verifying changes manually

---

## Common Scenarios

### Scenario 1: Implementation Not Working

**Situation:** You implemented a feature but it's not working as expected.

**Steps:**
1. List checkpoints to find last good state
2. Preview the rollback
3. Execute rollback

**Commands:**
```bash
# 1. Find last good checkpoint
list checkpoints

# 2. Preview rollback
rollback to dor-checkpoint --dry-run

# 3. Execute rollback
rollback to dor-checkpoint
```

**Result:** Back to DoR phase with validated requirements. Start fresh implementation.

### Scenario 2: Refactoring Broke Tests

**Situation:** Refactored code but tests now failing.

**Steps:**
1. Rollback to GREEN phase (when all tests passed)
2. Review what broke
3. Refactor more carefully

**Commands:**
```bash
# Rollback to last GREEN phase
rollback to green-checkpoint session tdd-001

# Verify tests pass
run tests

# Try refactoring again (with checkpoints)
```

**Result:** Tests passing again. Can reattempt refactoring.

### Scenario 3: Wrong Branch Merged

**Situation:** Merged wrong branch, need to undo.

**Steps:**
1. Rollback to checkpoint before merge
2. Verify correct state
3. Merge correct branch

**Commands:**
```bash
# Rollback to before merge
rollback to pre-merge-checkpoint --force

# Verify state
git log --oneline -5

# Merge correct branch
git merge correct-branch
```

### Scenario 4: Lost Work Due to Interruption

**Situation:** Work session interrupted, can't remember where you were.

**Steps:**
1. List checkpoints
2. Review last checkpoint metrics
3. Continue from last checkpoint

**Commands:**
```bash
# Find last state
list checkpoints for session feature-auth-001

# View details
show checkpoint impl-checkpoint-2

# Continue work from there
# (No rollback needed if last checkpoint is correct)
```

---

## Safety Checks

### Uncommitted Changes

**What it checks:** Files modified but not committed.

**Why it matters:** Rollback will discard these changes.

**If triggered:**
```
⚠️  Uncommitted changes detected:
- src/auth.py
- src/login.py

Options:
1. Commit changes: git add . && git commit -m "WIP"
2. Stash changes: git stash
3. Force rollback: rollback --force (will stash automatically)
```

### Merge in Progress

**What it checks:** Active merge operation.

**Why it matters:** Rollback during merge can corrupt repository.

**If triggered:**
```
❌ Merge in progress - resolve conflicts first

Options:
1. Complete merge: resolve conflicts → git commit
2. Abort merge: git merge --abort
3. Then retry rollback
```

### Working Tree Clean

**What it checks:** No untracked or ignored files interfering.

**Why it matters:** Ensures clean rollback.

---

## Understanding Checkpoints

### What is a Checkpoint?

A checkpoint is a **snapshot of your work** at a specific phase:
- 📸 Git commit SHA (exact code state)
- 📊 Metrics (tests passing, coverage, etc.)
- ⏰ Timestamp (when checkpoint created)
- 🏷️ Phase label (DoR, Implementation, DoD, etc.)

### When are Checkpoints Created?

**Planning Workflow:**
- ✅ After DoR validation
- ✅ After Implementation complete
- ✅ After DoD verification

**TDD Workflow:**
- ✅ After RED phase (test fails)
- ✅ After GREEN phase (test passes)
- ✅ After REFACTOR phase (code cleaned)

**System Alignment:**
- ✅ After catalog discovery
- ✅ After integration scoring

### Checkpoint Naming

Checkpoints have descriptive IDs:
- `dor-validated-2025-11-28` → DoR phase on specific date
- `impl-feature-a-complete` → Implementation of Feature A
- `green-all-tests-passing` → GREEN phase with all tests passing
- `refactor-clean-code` → REFACTOR phase after cleanup

---

## Tips and Best Practices

### ✅ DO

1. **Use dry-run before important rollbacks**
   ```
   rollback to dor-checkpoint --dry-run
   ```

2. **Commit work before rollback**
   ```
   git add .
   git commit -m "WIP: Exploring approach"
   rollback to dor-checkpoint
   ```

3. **Review checkpoint metrics**
   ```
   show checkpoint impl-checkpoint-2
   # Check: tests passing, coverage, etc.
   ```

4. **Create manual checkpoints for experiments**
   ```
   create checkpoint experiment-approach-a
   # Try risky changes
   # Rollback if doesn't work
   ```

### ❌ DON'T

1. **Don't rollback during merge**
   - Finish or abort merge first

2. **Don't rollback with uncommitted critical changes**
   - Commit or stash first
   - Or use `--dry-run` to preview

3. **Don't force rollback without understanding impact**
   - Review `--dry-run` output first

4. **Don't rollback to very old checkpoints without checking**
   - Review git history between checkpoints
   - Consider if too much work will be lost

---

## Troubleshooting

### Problem: "Checkpoint not found"

**Cause:** Checkpoint ID doesn't exist or typo.

**Solution:**
```bash
# List available checkpoints
list checkpoints

# Use exact checkpoint ID from list
rollback to dor-validated-2025-11-28
```

### Problem: "Session not found"

**Cause:** Session ID incorrect or session has no checkpoints.

**Solution:**
```bash
# List all sessions
list sessions

# Use correct session ID
rollback session feature-auth-001 to dor-checkpoint
```

### Problem: "Safety check failed"

**Cause:** Uncommitted changes or merge in progress.

**Solution:**
```bash
# Option 1: Commit changes
git add .
git commit -m "WIP"

# Option 2: Stash changes
git stash

# Option 3: Force rollback (careful!)
rollback to dor-checkpoint --force
```

### Problem: "Rollback too slow"

**Cause:** Large number of files or complex git history.

**Solution:**
- Normal for large codebases
- Typical rollback: <2 seconds
- Use `--dry-run` for instant preview

### Problem: "Lost changes after rollback"

**Cause:** Forgot to commit before rollback.

**Solution:**
```bash
# Check git stash (if used --force)
git stash list
git stash show stash@{0}

# Recover if stashed
git stash pop

# Check reflog
git reflog
git checkout <commit-before-rollback>
```

---

## FAQ

### Q: Can I rollback after committing?

**A:** Yes! Rollback works on committed code. It resets your branch to the checkpoint's commit.

### Q: Will rollback delete my files?

**A:** Only if those files were created after the checkpoint. Files existing at checkpoint time are restored to their checkpoint state.

### Q: Can I rollback to a specific commit SHA?

**A:** No, only to named checkpoints. But you can use standard git commands:
```bash
git reset --hard <commit-sha>
```

### Q: How far back can I rollback?

**A:** To any checkpoint in the session. Checkpoints are kept until session is closed.

### Q: Can I rollback after pushing to remote?

**A:** Yes locally, but requires force-push to update remote:
```bash
rollback to dor-checkpoint
git push origin branch-name --force-with-lease
```
**⚠️ Caution:** Force-push affects collaborators.

### Q: What if I rollback to wrong checkpoint?

**A:** Rollback to a newer checkpoint or use git reflog:
```bash
# Rollback forward
rollback to impl-checkpoint-2

# Or use git reflog
git reflog  # Find commit before wrong rollback
git reset --hard HEAD@{1}
```

---

## Examples

### Example 1: Planning Workflow

```bash
# Start planning session
start planning session feature-auth-001

# Complete DoR (checkpoint auto-created)
# Checkpoint: dor-validated-2025-11-28

# Start implementation
# ... work on features ...
# Checkpoint: impl-checkpoint-1 (auto-created)

# Implementation not working, rollback
rollback to dor-validated-2025-11-28

# Review requirements, start fresh
```

### Example 2: TDD Workflow

```bash
# Start TDD session
start tdd session auth-tests-001

# Write failing test (RED phase)
# Checkpoint: red-auth-test-fails (auto-created)

# Implement feature (GREEN phase)
# Checkpoint: green-auth-test-passes (auto-created)

# Refactor code
# ... refactoring breaks tests ...

# Rollback to GREEN
rollback to green-auth-test-passes

# Refactor more carefully
```

### Example 3: Multi-Feature Development

```bash
# Feature A complete
# Checkpoint: feature-a-complete

# Feature B development
# ... complications arise ...

# Preview rollback
rollback to feature-a-complete --dry-run

# Decide: rollback or continue?
# Rollback to restart Feature B
rollback to feature-a-complete

# Try different approach for Feature B
```

---

## Getting Help

### In-App Help
```bash
# General help
help rollback

# Command syntax
help rollback syntax

# Examples
help rollback examples
```

### Documentation
- Implementation Guide: `checkpoint-rollback-system-guide.md`
- API Reference: See component docstrings
- Test Examples: `tests/e2e/test_full_workflow_scenarios.py`

### Support
- GitHub Issues: `github.com/asifhussain60/CORTEX/issues`
- Discussions: `github.com/asifhussain60/CORTEX/discussions`

---

**Remember:** Rollback is a safety net. Use checkpoints liberally and rollback confidently when needed!
