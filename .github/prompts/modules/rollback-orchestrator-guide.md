# Rollback Orchestrator Guide

**Module:** `RollbackOrchestrator`  
**Location:** `src/operations/modules/git/rollback_orchestrator.py`  
**Purpose:** Safe Git rollback operations with checkpoint restoration  
**Status:** ✅ Production  
**Version:** 3.3.0

---

## Overview

The Rollback Orchestrator provides safe Git rollback capabilities using the Git Checkpoint system. It allows users to undo changes, restore previous states, and recover from mistakes without data loss.

**Key Capabilities:**
- List available Git checkpoints
- Rollback to specific checkpoint
- Soft rollback (keep changes)
- Hard rollback (discard changes)
- Preview rollback impact
- Safety confirmations

---

## Natural Language Triggers

**Primary Commands:**
- `rollback`
- `undo changes`
- `restore checkpoint`
- `git rollback`

**Context Variations:**
- "Roll back to last checkpoint"
- "Undo my recent changes"
- "Restore previous state"

---

## Architecture & Integration

**Dependencies:**
- Git CLI (command-line interface)
- `GitCheckpointOrchestrator` - Checkpoint management
- `BrainProtector` - Validates rollback safety
- Git checkpoint database

**Integration Points:**
- Unified Entry Point Orchestrator for command routing
- Response template system for user feedback
- Safety confirmation workflow

---

## Usage Examples

### List Checkpoints

```
User: "rollback"
CORTEX: Shows list of available checkpoints with timestamps and descriptions
```

### Rollback to Checkpoint

```
User: "rollback to [checkpoint-id]"
CORTEX: Confirms action → Restores state → Reports result
```

### Soft Rollback (Keep Changes)

```
User: "rollback --soft"
CORTEX: Resets Git history but preserves working directory changes
```

### Hard Rollback (Discard Changes)

```
User: "rollback --hard"
CORTEX: Warning → Confirmation → Discards all changes
```

---

## Safety Features

**Pre-Rollback Checks:**
1. ✅ Checkpoint exists and is valid
2. ✅ No uncommitted critical changes
3. ✅ No merge conflicts present
4. ✅ User confirmation for destructive operations
5. ✅ Automatic checkpoint before rollback

**Protection Mechanisms:**
- **Double Confirmation:** Required for hard rollbacks
- **Change Preview:** Shows what will be lost
- **Backup Checkpoint:** Created before any rollback
- **Staged Changes Warning:** Alerts if work in progress

---

## Rollback Modes

**Soft Rollback:**
- Moves HEAD to checkpoint
- Keeps working directory changes
- Preserves staged files
- Safe for experimenting

**Mixed Rollback (Default):**
- Moves HEAD to checkpoint
- Resets staging area
- Keeps working directory changes
- Balance of safety and cleanup

**Hard Rollback:**
- Moves HEAD to checkpoint
- Resets staging area
- **Discards working directory changes**
- Requires confirmation

---

## Configuration

**Checkpoint Settings:**
- Checkpoint retention: 30 days
- Maximum checkpoints: 50
- Auto-checkpoint before rollback: Enabled

**Safety Settings:**
- Confirmation required: Enabled for hard rollbacks
- Preview changes: Enabled
- Create backup: Enabled

---

## Implementation Details

**Class:** `RollbackOrchestrator`

**Key Methods:**
- `execute(context)` - Main rollback orchestration
- `_list_checkpoints()` - Show available checkpoints
- `_preview_rollback(checkpoint_id)` - Show impact
- `_confirm_rollback()` - User confirmation
- `_create_backup_checkpoint()` - Safety backup
- `_perform_rollback(checkpoint_id, mode)` - Execute rollback

---

## Error Handling

**Common Issues:**
1. **Checkpoint not found** → Lists available checkpoints
2. **Uncommitted changes** → Warns user, offers to stash
3. **Merge conflict** → Requires resolution first
4. **Invalid checkpoint ID** → Suggests correct format

---

## Checkpoint Format

**Checkpoint Naming:**
- `checkpoint-[timestamp]-[description]`
- Example: `checkpoint-20251128-153045-before-refactor`

**Checkpoint Data:**
- Git commit SHA
- Timestamp
- Description
- File changes summary
- Branch name

---

## Testing

**Test Coverage:** 20% (needs significant improvement)

**Test Files:**
- `tests/operations/test_rollback_orchestrator.py` (planned)

**Manual Validation:**
1. Create checkpoint via `git checkpoint`
2. Make changes
3. Run `rollback`
4. Verify state restored correctly
5. Check backup checkpoint created

---

## Related Modules

- **GitCheckpointOrchestrator** - Creates and manages checkpoints
- **CommitOrchestrator** - Creates commits with checkpoints
- **BrainProtector** - Validates rollback operations

---

## Troubleshooting

**Issue:** Rollback fails with merge conflict  
**Solution:** Resolve conflicts manually, then retry rollback

**Issue:** Changes lost after rollback  
**Solution:** Check backup checkpoint, restore from there

**Issue:** Checkpoint list empty  
**Solution:** Create checkpoints using `git checkpoint` command

---

## Best Practices

**When to Use Rollback:**
- ✅ After failed experiments
- ✅ When changes break tests
- ✅ To recover from mistakes
- ✅ Before starting risky operations

**When NOT to Use Rollback:**
- ❌ On shared branches (use revert instead)
- ❌ After pushing to remote (coordination required)
- ❌ Without backup checkpoint
- ❌ With uncommitted critical work

---

## Future Enhancements

**Planned (CORTEX 4.0):**
- Selective file rollback (not entire checkpoint)
- Rollback preview with diff visualization
- Automatic conflict resolution for simple cases
- Checkpoint branching (create branch from checkpoint)
- Remote checkpoint sync for team collaboration

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Last Updated:** November 28, 2025  
**Guide Version:** 1.0.0
