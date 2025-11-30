# Checkpoint Failure Handling - Example

**Purpose:** Demonstrate how CORTEX handles git checkpoint failures gracefully  
**Author:** Asif Hussain  
**Version:** 1.0

---

## Overview

CORTEX planning operations are **resilient to checkpoint failures**. If git is unavailable or checkpoint creation fails, planning continues successfully with a warning logged.

---

## Why Non-Blocking Error Handling?

**Design Principle:** Planning operations are more critical than checkpoints.

✅ **User Value Priority** - Generating/approving/completing plans delivers immediate value  
✅ **Checkpoint is Enhancement** - Git checkpoints are safety features, not requirements  
✅ **Graceful Degradation** - System remains functional even when non-critical features fail  
✅ **User Awareness** - Warnings logged so users know checkpoint didn't save  

---

## Scenario 1: Git Repository Not Available

### Setup

```bash
# Simulate git unavailable (e.g., working in non-git directory)
cd /tmp/non-git-directory
```

### Planning Operation

```
User: "plan user dashboard feature"

CORTEX:
  🎯 Starting incremental plan generation...
  
  ⚠️  Git checkpoint failed: Not a git repository
      Planning will continue without checkpoint
  
  [... generates plan normally ...]
  
  ✅ Plan generated: PLAN-20251130-user-dashboard.md
  ⚠️  Note: No rollback checkpoint created (git unavailable)
```

**What Happened:**
- GitCheckpointOrchestrator.create_auto_checkpoint raised exception
- Exception caught in try/except block
- Warning logged: `"Git checkpoint failed during plan generation: Not a git repository"`
- Planning continued successfully
- Plan generated without checkpoint

**User Impact:**
- ✅ Plan created successfully
- ❌ No rollback capability for this operation
- ℹ️ User informed via warning message

---

## Scenario 2: Git Permission Error

### Setup

```bash
# Simulate read-only git repository (permission denied)
chmod -R 444 .git/
```

### Planning Operation

```
User: "approve plan user-dashboard"

CORTEX:
  📋 Moving plan to approved directory...
  ✅ Status updated: active → approved
  
  ⚠️  Git checkpoint failed: Permission denied
      Plan approval completed successfully
  
  ✅ Plan approved: PLAN-20251130-user-dashboard.md
  ⚠️  Note: No checkpoint created for this approval
```

**What Happened:**
- Plan approval logic executed successfully
- GitCheckpointOrchestrator.create_auto_checkpoint raised PermissionError
- Exception caught, warning logged
- Approval completed without checkpoint

**User Impact:**
- ✅ Plan approved and moved to approved/ directory
- ❌ No rollback checkpoint for approval operation
- ℹ️ User can manually create checkpoint after fixing permissions

**Recovery:**
```bash
# Fix permissions
chmod -R 755 .git/

# Manually create checkpoint
git tag -a manual-approval-20251130-160000 -m "Manual checkpoint after approval"
```

---

## Scenario 3: Disk Space Full

### Setup

```bash
# Simulate full disk (git tag creation fails)
# (Hypothetical - difficult to reproduce safely)
```

### Planning Operation

```
User: "complete plan user-dashboard"

CORTEX:
  📋 Moving plan to completed directory...
  ✅ Status updated: approved → completed
  
  ⚠️  Git checkpoint failed: No space left on device
      Plan completion succeeded
  
  ✅ Plan completed: PLAN-20251130-user-dashboard.md
  ⚠️  Note: Checkpoint not saved due to disk space
  
  💡 Tip: Free up disk space and manually create checkpoint if rollback needed
```

**What Happened:**
- Plan completion logic executed successfully
- Git tag creation failed due to disk space
- Exception caught, warning logged
- Completion finished without checkpoint

**User Impact:**
- ✅ Plan completed and moved to completed/ directory
- ❌ No rollback checkpoint
- ℹ️ User instructed to free disk space and create checkpoint manually

---

## Error Handling Implementation

### Code Pattern

```python
# In planning_orchestrator.py

def generate_incremental_plan(self, feature_requirements, checkpoint_callback=None, output_filename=None):
    """Generate plan with automatic checkpoint."""
    
    # Extract feature name for checkpoint message
    feature_name = feature_requirements[:50] + ("..." if len(feature_requirements) > 50 else "")
    
    # Create checkpoint (non-blocking)
    try:
        self.git_checkpoint.create_auto_checkpoint(
            operation="plan",
            message=f"Starting plan generation: {feature_name}"
        )
    except Exception as e:
        self.logger.warning(f"Git checkpoint failed during plan generation: {str(e)}")
        # Continue planning despite checkpoint failure
    
    # ... proceed with plan generation ...
```

### Key Elements

1. **Try/Except Block** - Wraps checkpoint creation only (not entire method)
2. **Broad Exception Catch** - Catches any Exception (git errors, permission errors, disk errors)
3. **Warning Log** - Records failure reason with context
4. **No Re-Raise** - Exception NOT re-raised, allowing planning to continue
5. **User Notification** - Warning message displayed in CORTEX response

---

## Checkpoint Failure Types

### 1. Repository Errors

**Causes:**
- Not a git repository
- Detached HEAD state
- Corrupted git objects

**Impact:** No checkpoint created, planning continues  
**Recovery:** Initialize git repo, fix git issues, retry planning

### 2. Permission Errors

**Causes:**
- Read-only .git directory
- File system permissions
- Locked git database

**Impact:** No checkpoint created, planning continues  
**Recovery:** Fix permissions, manually create checkpoint

### 3. Disk Space Errors

**Causes:**
- No space left on device
- Quota exceeded
- Disk full

**Impact:** No checkpoint created, planning continues  
**Recovery:** Free disk space, create checkpoint manually

### 4. Network Errors (if remote operations)

**Causes:**
- Remote git server unreachable
- Authentication failure
- Network timeout

**Impact:** No checkpoint created, planning continues  
**Recovery:** Fix network/auth, push checkpoint manually

---

## Logging Examples

### Generate Plan Failure

```
2025-11-30 16:00:00 [WARNING] planning_orchestrator.py:665 - 
Git checkpoint failed during plan generation: Not a git repository (or any of the parent directories): .git
```

### Approve Plan Failure

```
2025-11-30 16:05:00 [WARNING] planning_orchestrator.py:1228 - 
Git checkpoint failed during plan approval: Permission denied: '.git/refs/tags/approve-20251130-160500'
```

### Complete Plan Failure

```
2025-11-30 16:10:00 [WARNING] planning_orchestrator.py:1282 - 
Git checkpoint failed during plan completion: No space left on device
```

---

## Best Practices

### For Users

1. **Check Git Status** - Verify git repository before critical operations
   ```bash
   git status
   ```

2. **Monitor Warnings** - Pay attention to checkpoint failure warnings in CORTEX responses

3. **Manual Checkpoints** - Create checkpoints manually if automatic creation failed
   ```bash
   git tag -a manual-checkpoint-$(date +%Y%m%d-%H%M%S) -m "Manual checkpoint after planning"
   ```

4. **Regular Git Maintenance** - Keep git repository healthy (gc, fsck, prune)

### For Administrators

1. **Disk Space Monitoring** - Alert when disk usage >80%

2. **Permission Audits** - Verify CORTEX has write access to .git/

3. **Git Health Checks** - Run `git fsck` periodically to detect corruption

4. **Logging Review** - Check logs for recurring checkpoint failures

---

## Troubleshooting

### Issue: All checkpoints failing consistently

**Symptoms:**
- Every planning operation logs checkpoint warning
- No checkpoints created for any operation

**Diagnosis:**
```bash
# Check if in git repository
git status

# Check .git directory permissions
ls -la .git/

# Check disk space
df -h
```

**Solutions:**
1. Initialize git repository: `git init`
2. Fix permissions: `chmod -R 755 .git/`
3. Free disk space: Delete old files, expand storage

### Issue: Checkpoints work sometimes but not others

**Symptoms:**
- Intermittent checkpoint failures
- Some operations succeed, others fail

**Diagnosis:**
```bash
# Check git repository health
git fsck

# Check for locked files
lsof | grep .git
```

**Solutions:**
1. Repair git repository: `git fsck --full`
2. Close programs locking git files
3. Restart git daemon if running

### Issue: Want to disable checkpoints entirely

**Symptoms:**
- Frequent checkpoint failures causing noise in logs
- Don't want checkpoint feature

**Solution:**
```yaml
# Edit cortex-brain/git-checkpoint-rules.yaml
auto_checkpoint:
  enabled: false  # Disable all automatic checkpoints
```

**Impact:**
- ✅ No more checkpoint failures
- ❌ No rollback capability
- ℹ️ Can re-enable anytime

---

## Related Documentation

- **Planning with Checkpoints:** `planning-with-git-checkpoints.md`
- **Rollback Example:** `rollback-plan-approval.md`
- **Git Checkpoint Configuration:** `cortex-brain/git-checkpoint-rules.yaml`
- **Git Checkpoint Guide:** `.github/prompts/modules/git-checkpoint-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
