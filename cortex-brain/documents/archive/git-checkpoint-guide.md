# Git Checkpoint System Guide

**Purpose:** Comprehensive guide to CORTEX's git checkpoint system for safe, rollback-capable development  
**Version:** 2.0.0  
**Author:** Asif Hussain  
**Last Updated:** 2025-11-27

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Commands Reference](#commands-reference)
5. [Workflow Examples](#workflow-examples)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Integration with CORTEX](#integration-with-cortex)

---

## Overview

### What is Git Checkpoint System?

CORTEX's Git Checkpoint System creates automatic safety snapshots before and after development work, enabling:

- **Instant Rollback** - Return to known-good state in seconds
- **Zero Data Loss** - Never lose work due to experiments or mistakes
- **Clear History** - Track exactly what changed and when
- **Safe Experimentation** - Try bold changes without fear

### Why Not Branch Isolation?

We chose **checkpoint-based workflow** over temporary branches because:

✅ **Simpler** - No branch management complexity  
✅ **Faster** - No switching overhead (changes appear immediately)  
✅ **Safer** - Git tags more reliable than automatic branch cleanup  
✅ **User-Friendly** - Standard git commands (`reset --hard`)  
✅ **Production-Ready** - Existing Git Checkpoint Orchestrator

### Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Auto-Checkpoints** | Before/after all CORTEX operations | Always have rollback point |
| **Dirty State Detection** | Warns about uncommitted changes | Prevents data loss |
| **Retention Policy** | 30-day/50-count automatic cleanup | Prevents checkpoint bloat |
| **User Consent Workflow** | Interactive prompts for conflicts | User stays in control |
| **Tag-Based Storage** | Uses git tags (not branches) | No branch proliferation |

---

## Quick Start

### 1. Enable Auto-Checkpoints (Default)

Auto-checkpoints are **enabled by default**. No setup needed!

### 2. Start Development

```
# Natural language - CORTEX creates checkpoint automatically
"implement authentication feature"

# CORTEX responds:
🔍 Detected uncommitted changes in branch 'main'
📸 Creating pre-work checkpoint...
✅ Checkpoint created: pre-work-20251127-143022

If you want to undo CORTEX changes later:
  rollback to pre-work-20251127-143022
```

### 3. Review Work

```
# See all checkpoints
"show checkpoints"

# Rollback if needed
"rollback to pre-work-20251127-143022"
```

### 4. Clean Up Old Checkpoints

```
# View old checkpoints
"cleanup checkpoints"

# Auto-cleanup (30+ days old)
Runs automatically via retention policy
```

---

## Core Concepts

### Checkpoints vs Commits

| Aspect | Checkpoint (Tag) | Commit |
|--------|------------------|--------|
| **Purpose** | Safety snapshot | Permanent history |
| **Visibility** | Local only | Can push to remote |
| **Weight** | Lightweight | Heavier (full history) |
| **Lifecycle** | Auto-cleanup after 30 days | Permanent |
| **Rollback** | `git reset --hard <tag>` | `git reset --hard <sha>` |

### Checkpoint Types

**Automatic Checkpoints:**
- `pre-work-YYYYMMDD-HHMMSS` - Before CORTEX starts work
- `post-work-YYYYMMDD-HHMMSS` - After CORTEX completes work
- `implementation-YYYYMMDD-HHMMSS` - After feature implementation
- `refactoring-YYYYMMDD-HHMMSS` - After refactoring
- `tdd-red-YYYYMMDD-HHMMSS` - After RED phase (test writing)
- `tdd-green-YYYYMMDD-HHMMSS` - After GREEN phase (implementation)
- `tdd-refactor-YYYYMMDD-HHMMSS` - After REFACTOR phase
- `test-failure-YYYYMMDD-HHMMSS` - When tests fail (debugging aid)

**User-Created Checkpoints:**
- `user-[custom-name]-YYYYMMDD-HHMMSS` - Manual checkpoint with custom name

### Dirty State Detection

CORTEX checks for **uncommitted changes** before starting work:

**Detected States:**
- ✅ **Clean** - No uncommitted changes, proceed automatically
- ⚠️ **Dirty** - Uncommitted changes, user consent required
- ❌ **Blocked** - Merge/rebase in progress, must resolve first

**User Options When Dirty:**
- **A) Commit first (RECOMMENDED)** - Preserves clear attribution
- **B) Stash changes** - Temporary storage, restore later
- **C) Proceed anyway** - CORTEX creates checkpoint of dirty state
- **X) Cancel** - Abort operation

### Retention Policy

**Automatic Cleanup Rules:**
- **Max Age:** 30 days (configurable)
- **Max Count:** 50 checkpoints per repository (configurable)
- **Preserve Named:** User-created checkpoints never auto-deleted
- **Grace Period:** 3-day minimum before deletion
- **Cleanup Interval:** Every 24 hours

**What Gets Deleted:**
- Generic auto-checkpoints older than 30 days
- Excess checkpoints beyond 50-count limit (oldest first)

**What's Preserved:**
- User-named checkpoints (`user-*`)
- Tagged checkpoints with custom tags
- All checkpoints less than 3 days old

---

## Commands Reference

### Natural Language Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create checkpoint [name]` | Manual checkpoint with custom name | `create checkpoint before-major-refactor` |
| `show checkpoints` | List all CORTEX checkpoints | `show checkpoints` |
| `list checkpoints` | Alternative to show | `list checkpoints` |
| `rollback to [checkpoint]` | Reset to specific checkpoint | `rollback to pre-work-20251127-143022` |
| `rollback last` | Undo last CORTEX operation | `rollback last` |
| `cleanup checkpoints` | Remove old checkpoints (30+ days) | `cleanup checkpoints` |

### Direct Git Commands

```bash
# List all checkpoint tags
git tag -l '*-2025*' --sort=-creatordate

# View checkpoint details
git show pre-work-20251127-143022

# Rollback to checkpoint (destructive!)
git reset --hard pre-work-20251127-143022

# Create manual checkpoint
git tag -a checkpoint-$(date +%Y%m%d-%H%M%S) -m "Manual checkpoint before X"

# Delete specific checkpoint
git tag -d pre-work-20251127-143022

# View diff between checkpoints
git diff pre-work-20251127-143022 post-work-20251127-143856
```

---

## Workflow Examples

### Example 1: Simple Feature Implementation

```
User: "implement user login feature"

CORTEX:
  🔍 Checking git status...
  ✅ Clean working tree
  📸 Creating pre-work checkpoint: pre-work-20251127-140000
  
  [... implements feature ...]
  
  📸 Creating post-work checkpoint: implementation-20251127-140530
  ✅ Feature complete!
  
  Checkpoints created:
  • pre-work-20251127-140000 (rollback point)
  • implementation-20251127-140530 (current state)

User (later): "rollback to pre-work-20251127-140000"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will DISCARD all changes after checkpoint 'pre-work-20251127-140000'
  
  Changes to be lost:
   src/auth.py           | 50 ++++++++++++++++++++++++++++++++++++++++++++
   tests/test_auth.py    | 30 +++++++++++++++++++++++++++
   2 files changed, 80 insertions(+)
  
  Type 'yes' to confirm rollback: yes
  
  📸 Creating safety checkpoint before rollback...
  ✅ Rolled back to checkpoint: pre-work-20251127-140000
```

### Example 2: Dirty State Workflow

```
User: "refactor authentication module"

CORTEX:
  🔍 Checking git status...
  ⚠️  DIRTY STATE DETECTED - USER CONSENT REQUIRED
  
  Modified files (3):
    - src/auth.py
    - src/user.py
    - config/settings.py
  
  OPTIONS:
    A) Commit your changes first (RECOMMENDED)
    B) Stash changes and continue
    C) Proceed anyway (CORTEX will checkpoint current state)
    X) Cancel operation
  
  Your choice (A/B/C/X): A

User (in terminal):
  git add .
  git commit -m "WIP: auth module changes"
  
User: "refactor authentication module"

CORTEX:
  🔍 Checking git status...
  ✅ Clean working tree
  📸 Creating pre-work checkpoint: pre-work-20251127-141500
  
  [... performs refactoring ...]
  
  📸 Creating post-work checkpoint: refactoring-20251127-142000
  ✅ Refactoring complete!
```

### Example 3: TDD Workflow with Checkpoints

```
User: "start tdd for user registration"

CORTEX:
  📸 TDD Session Started
  📸 Creating pre-work checkpoint: pre-work-20251127-143000
  
  --- RED PHASE ---
  [... writes failing tests ...]
  📸 Creating checkpoint: tdd-red-20251127-143100
  ✅ Tests fail as expected (RED phase complete)
  
  --- GREEN PHASE ---
  [... implements minimal code to pass ...]
  📸 Creating checkpoint: tdd-green-20251127-143500
  ✅ Tests pass (GREEN phase complete)
  
  --- REFACTOR PHASE ---
  [... improves code while tests pass ...]
  📸 Creating checkpoint: tdd-refactor-20251127-143800
  ✅ Refactoring complete, tests still pass
  
  📸 Creating post-work checkpoint: post-work-20251127-143900
  
  TDD Session Complete!
  Checkpoints created:
  • pre-work-20251127-143000 (session start)
  • tdd-red-20251127-143100 (failing tests)
  • tdd-green-20251127-143500 (passing tests)
  • tdd-refactor-20251127-143800 (refactored code)
  • post-work-20251127-143900 (session end)
```

### Example 4: Checkpoint Cleanup

```
User: "show checkpoints"

CORTEX:
  📋 Git Checkpoints (Last 30 Days):
  
  Recent (< 7 days):
  1. post-work-20251127-143900 (TDD session) - 2 hours ago
  2. tdd-refactor-20251127-143800 (refactor) - 2 hours ago
  3. tdd-green-20251127-143500 (green) - 3 hours ago
  4. tdd-red-20251127-143100 (red) - 3 hours ago
  5. pre-work-20251127-143000 (session start) - 3 hours ago
  
  Old (> 30 days):
  6. pre-work-20251027-091500 - 31 days ago
  7. implementation-20251026-140000 - 32 days ago
  8. pre-work-20251025-103000 - 33 days ago
  
  💡 Tip: Run 'cleanup checkpoints' to remove old checkpoints

User: "cleanup checkpoints"

CORTEX:
  🔍 Analyzing checkpoints for cleanup...
  
  Total checkpoints: 8
  To keep: 5 (< 30 days old)
  To delete: 3 (> 30 days old)
  
  Will delete:
  • pre-work-20251027-091500 (31 days old)
  • implementation-20251026-140000 (32 days old)
  • pre-work-20251025-103000 (33 days old)
  
  🗑️  Deleted checkpoint: pre-work-20251027-091500
  🗑️  Deleted checkpoint: implementation-20251026-140000
  🗑️  Deleted checkpoint: pre-work-20251025-103000
  
  ✅ Cleanup complete: 3 deleted, 5 kept
```

---

## Configuration

### Location

**Config File:** `cortex-brain/git-checkpoint-rules.yaml`

### Key Settings

```yaml
auto_checkpoint:
  enabled: true                      # Enable/disable auto-checkpoints
  triggers:
    before_implementation: true      # Checkpoint before code changes
    after_implementation: true       # Checkpoint after code changes
    before_refactoring: true         # Checkpoint before refactoring
    after_refactoring: true          # Checkpoint after refactoring
    on_test_failure: true            # Checkpoint when tests fail

retention:
  max_age_days: 30                   # Delete checkpoints older than 30 days
  max_count: 50                      # Keep maximum 50 checkpoints
  preserve_named: true               # Never delete user-named checkpoints

safety:
  detect_uncommitted_changes: true   # Detect dirty state
  warn_on_uncommitted: true          # Warn before proceeding
  require_confirmation: true         # Require user confirmation
  create_backup_before_rollback: true # Safety checkpoint before rollback
```

### Customization

**Change retention period:**
```yaml
retention:
  max_age_days: 60  # Keep for 60 days instead of 30
```

**Disable dirty state warnings:**
```yaml
safety:
  warn_on_uncommitted: false
```

**Change checkpoint naming:**
```yaml
naming:
  format: "checkpoint-{type}-{timestamp}"
  timestamp_format: "%Y%m%d-%H%M%S"
```

---

## Best Practices

### 1. Let CORTEX Manage Checkpoints

✅ **DO:** Let CORTEX create automatic checkpoints  
❌ **DON'T:** Manually create checkpoints unless needed

**Why:** CORTEX's auto-checkpoint system is optimized for TDD workflow and safety.

### 2. Commit Before CORTEX Work

✅ **DO:** Commit your changes before saying "implement X"  
❌ **DON'T:** Mix your uncommitted work with CORTEX changes

**Why:** Clear attribution, easier rollback, simpler debugging.

### 3. Review Checkpoints Regularly

✅ **DO:** Use `show checkpoints` to see safety points  
❌ **DON'T:** Ignore checkpoints until something breaks

**Why:** Awareness of rollback points gives confidence for bold changes.

### 4. Use Named Checkpoints for Milestones

✅ **DO:** Create named checkpoints: `create checkpoint v1-stable`  
❌ **DON'T:** Rely only on auto-checkpoints for important milestones

**Why:** Named checkpoints are preserved forever, auto-checkpoints expire.

### 5. Test Rollback Occasionally

✅ **DO:** Practice rollback on non-critical changes  
❌ **DON'T:** Wait for disaster to learn rollback process

**Why:** Confidence in recovery reduces fear of experimentation.

### 6. Clean Up Regularly

✅ **DO:** Run `cleanup checkpoints` monthly  
❌ **DON'T:** Let checkpoints accumulate forever

**Why:** Automatic cleanup helps, but manual review is good practice.

---

## Troubleshooting

### Problem: Checkpoint Creation Failed

**Symptoms:**
```
❌ Failed to create checkpoint
Error: git tag failed
```

**Solutions:**
1. Check git repository status: `git status`
2. Ensure no merge conflicts exist: `git diff --check`
3. Verify git is accessible: `git --version`
4. Check disk space: `df -h`

### Problem: Rollback Failed

**Symptoms:**
```
❌ Rollback failed
Error: checkpoint not found
```

**Solutions:**
1. Verify checkpoint exists: `git tag -l`
2. Check exact checkpoint name: `show checkpoints`
3. Use git reflog to find commit: `git reflog`
4. Try git commands directly: `git reset --hard <sha>`

### Problem: Too Many Checkpoints

**Symptoms:**
```
⚠️  50+ checkpoints detected
Repository size growing
```

**Solutions:**
1. Run cleanup: `cleanup checkpoints`
2. Adjust retention policy: Edit `git-checkpoint-rules.yaml`
3. Delete specific checkpoints: `git tag -d <checkpoint-name>`
4. Review checkpoint age: `git tag -l --sort=-creatordate`

### Problem: Dirty State Warning Won't Clear

**Symptoms:**
```
⚠️  Dirty state detected
Modified files: ...
```

**Solutions:**
1. Check what's modified: `git status`
2. Commit changes: `git add . && git commit -m "description"`
3. Stash changes: `git stash save "WIP: description"`
4. Discard changes: `git reset --hard HEAD` (careful!)

### Problem: Can't Find Recent Checkpoint

**Symptoms:**
```
I rolled back but lost my recent work
```

**Solutions:**
1. Check git reflog: `git reflog` (shows recent commits)
2. Find lost commit: Look for commit message in reflog
3. Restore: `git reset --hard <commit-sha>`
4. Check safety checkpoint: `git tag -l '*pre-rollback*'`

---

## Integration with CORTEX

### TDD Workflow

Checkpoints are automatically integrated with TDD Mastery workflow:

```python
# In TDD orchestrator
checkpoint_orchestrator = GitCheckpointOrchestrator(project_root)

# Before RED phase
checkpoint_orchestrator.create_auto_checkpoint("tdd-red", "Before writing tests")

# After GREEN phase
checkpoint_orchestrator.create_auto_checkpoint("tdd-green", "After implementation")

# After REFACTOR phase
checkpoint_orchestrator.create_auto_checkpoint("tdd-refactor", "After refactoring")
```

### Planning Workflow

Checkpoints created during feature planning:

- Before implementation starts
- After each phase (DoR, DoD validation)
- After feature completion

### Debug System

Debug sessions automatically create checkpoints:

- Before debug session starts (safety point)
- After debug session ends (capture fixes)

### Optimize Operation

Optimization creates checkpoints:

- Before governance drift fixes
- After optimization completes

---

## Advanced Usage

### Custom Checkpoint Scripts

**Create checkpoint hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit
# Auto-checkpoint before every commit

git tag -a checkpoint-$(date +%Y%m%d-%H%M%S) \\
        -m "Auto checkpoint before commit"
```

**Checkpoint aliases:**
```bash
# Add to ~/.gitconfig
[alias]
    checkpoint = !git tag -a checkpoint-$(date +%Y%m%d-%H%M%S) -m \"Manual checkpoint\"
    undo = reset --hard
    list-checkpoints = tag -l '*-2025*' --sort=-creatordate
```

### Programmatic Usage

```python
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from pathlib import Path

# Initialize
checkpoint = GitCheckpointOrchestrator(Path("/path/to/repo"))

# Check dirty state
dirty_state = checkpoint.detect_dirty_state()
if dirty_state["is_dirty"]:
    # Get user consent
    can_proceed, checkpoint_id = checkpoint.check_dirty_state_and_consent("my operation")
    
    if not can_proceed:
        print("Operation cancelled")
        exit(1)

# Create checkpoint
checkpoint_id = checkpoint.create_auto_checkpoint(
    "implementation",
    "Before implementing feature X"
)

# ... do work ...

# Create post-work checkpoint
checkpoint.create_auto_checkpoint(
    "post-work",
    "After implementing feature X"
)

# List checkpoints
checkpoints = checkpoint.list_all_checkpoints(max_age_days=7)
for cp in checkpoints:
    print(f"{cp['checkpoint_id']}: {cp['message']}")

# Rollback if needed
checkpoint.rollback_to_checkpoint_by_name("pre-work-20251127-140000")
```

---

## FAQs

### Q: Why not use branches instead?

**A:** Checkpoints (git tags) are simpler:
- No switching overhead
- No merge conflicts
- No branch proliferation
- Standard git commands
- Auto-cleanup built-in

### Q: Are checkpoints pushed to remote?

**A:** No, by default checkpoints are local-only. This prevents remote repository pollution. You can manually push important checkpoints if needed: `git push origin <checkpoint-name>`

### Q: What happens to checkpoints after 30 days?

**A:** Auto-checkpoints older than 30 days are automatically deleted. User-named checkpoints are preserved forever.

### Q: Can I disable auto-checkpoints?

**A:** Yes, edit `cortex-brain/git-checkpoint-rules.yaml`:
```yaml
auto_checkpoint:
  enabled: false
```

### Q: How much disk space do checkpoints use?

**A:** Minimal! Git tags are just pointers (< 1KB each). The actual commits already exist in git history.

### Q: Can I rollback part of a checkpoint?

**A:** No, rollback is all-or-nothing. For partial rollback, use:
```bash
# Restore specific file from checkpoint
git checkout <checkpoint-name> -- path/to/file.py
```

### Q: What if I accidentally delete a checkpoint?

**A:** Use git reflog to find the commit SHA, then recreate the tag:
```bash
git reflog  # Find commit SHA
git tag <checkpoint-name> <commit-sha>
```

---

## Related Documentation

- **TDD Mastery Guide:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Planning Orchestrator:** `.github/prompts/modules/planning-orchestrator-guide.md`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Git Checkpoint Rules:** `cortex-brain/git-checkpoint-rules.yaml`

---

**Last Updated:** 2025-11-27  
**Version:** 2.0.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
