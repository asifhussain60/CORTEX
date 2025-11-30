# Rollback Plan Approval - Example

**Purpose:** Demonstrate how to rollback plan approval using git checkpoints  
**Author:** Asif Hussain  
**Version:** 1.0

---

## Scenario

You approved a plan prematurely and want to restore it to active state for more refinement.

---

## Step-by-Step Rollback

### 1. Create and Approve Plan

```
User: "plan payment integration with Stripe API"

CORTEX:
  📸 Creating checkpoint: plan-20251130-150000
  ✅ Plan generated: PLAN-20251130-payment-integration.md
  
User: "approve plan payment-integration"

CORTEX:
  📸 Creating checkpoint: approve-20251130-150530
  ✅ Plan approved and moved to approved/ directory
```

**State After Approval:**
- Plan located at: `cortex-brain/documents/planning/approved/PLAN-20251130-payment-integration.md`
- Status: `approved`
- Checkpoints: `plan-20251130-150000`, `approve-20251130-150530`

### 2. Realize Premature Approval

```
User: "I need to add more technical details to the payment plan"

CORTEX:
  ⚠️  Plan is currently in approved state
  💡 Tip: You can rollback the approval to restore it to active state
```

### 3. List Available Checkpoints

```bash
# Show approval checkpoints
git tag -l 'approve-*' --sort=-creatordate

# Output:
approve-20251130-150530
```

**Alternative Command:**
```bash
# Show all checkpoints from today
git tag -l '*-20251130-*'

# Output:
approve-20251130-150530
plan-20251130-150000
```

### 4. View Checkpoint Details

```bash
# See what's in the approval checkpoint
git show approve-20251130-150530

# Output:
tag approve-20251130-150530
Tagger: CORTEX <cortex@ai.assistant>
Date:   Sat Nov 30 15:05:30 2025 -0500

Plan approved: PLAN-20251130-payment-integration.md

commit d7e8f9a0b1c2...
Author: Your Name <you@email.com>
Date:   Sat Nov 30 15:05:00 2025 -0500

    Planning work in progress
```

### 5. Preview Changes to Rollback

```bash
# See what will be undone
git diff approve-20251130-150530

# Output shows:
# - Plan file moved from active/ to approved/
# - Status changed from "active" to "approved"
# - Approval timestamp added
```

### 6. Execute Rollback

```bash
# Rollback to approval checkpoint
git reset --hard approve-20251130-150530

# Output:
HEAD is now at d7e8f9a Planning work in progress
```

**⚠️ WARNING:** This discards **ALL** changes after the checkpoint, not just the plan approval. Ensure no other uncommitted work will be lost.

### 7. Verify Rollback

```bash
# Check plan location
ls cortex-brain/documents/planning/approved/

# Output: (empty - plan no longer in approved/)

ls cortex-brain/documents/planning/active/

# Output:
PLAN-20251130-payment-integration.md  # ✅ Plan restored to active/
```

**Check Plan Status:**
```bash
# View plan frontmatter
head -10 cortex-brain/documents/planning/active/PLAN-20251130-payment-integration.md

# Output:
---
status: active          # ✅ Status restored to "active"
created: 2025-11-30
---

# Payment Integration with Stripe API
```

### 8. Resume Editing

```
User: "update payment plan - add PCI compliance section"

CORTEX:
  ✅ Plan found in active state
  📝 Adding PCI compliance requirements...
  ✅ Plan updated successfully
```

### 9. Re-Approve When Ready

```
User: "approve plan payment-integration"

CORTEX:
  📸 Creating checkpoint: approve-20251130-153000
  ✅ Plan re-approved with updated content
```

---

## Alternative: Rollback via CORTEX Command

Instead of manual git commands, you can use CORTEX's rollback command:

```
User: "rollback to approve-20251130-150530"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will discard all changes after checkpoint 'approve-20251130-150530'
  
  Changes to be lost:
   cortex-brain/documents/planning/approved/PLAN-20251130-payment-integration.md | moved to active/
   1 file changed, status reverted
  
  Type 'yes' to confirm rollback: yes
  
  📸 Creating safety checkpoint before rollback: pre-rollback-20251130-152000
  ✅ Rolled back to checkpoint: approve-20251130-150530
  ✅ Plan restored to active state
```

---

## Key Insights

### When to Rollback Plan Approval

✅ **Forgot technical details** - Need to add architecture, dependencies, or security notes  
✅ **Scope changed** - Business requirements updated after approval  
✅ **Premature approval** - Approved before stakeholder review  
✅ **Testing scenario** - Experimenting with approval workflow  

### Rollback Safety

✅ **Safety Checkpoint** - CORTEX creates `pre-rollback-*` checkpoint before execution  
✅ **Confirmation Required** - Must type 'yes' to confirm destructive rollback  
✅ **Diff Preview** - Shows exactly what will be undone before proceeding  
✅ **Recoverable** - Can rollback the rollback using `pre-rollback-*` checkpoint  

### Best Practices

1. **Check Git Status First**
   ```bash
   git status
   ```
   Ensure no uncommitted work that would be lost

2. **List Checkpoints**
   ```bash
   git tag -l '*-20251130-*' --sort=-creatordate
   ```
   Verify you have the right checkpoint ID

3. **Preview Diff**
   ```bash
   git diff approve-20251130-150530
   ```
   Confirm what will be undone

4. **Create Manual Checkpoint** (optional)
   ```bash
   git tag -a manual-before-rollback-20251130-152000 -m "Safety checkpoint before rollback"
   ```
   Extra safety for peace of mind

5. **Verify After Rollback**
   ```bash
   ls cortex-brain/documents/planning/active/
   head cortex-brain/documents/planning/active/PLAN-*.md
   ```
   Confirm plan restored correctly

---

## Troubleshooting

### Issue: "Cannot rollback - uncommitted changes"

**Symptom:**
```bash
git reset --hard approve-20251130-150530
# Error: You have uncommitted changes. Please commit or stash them first.
```

**Solution:**
```bash
# Option 1: Commit changes
git add .
git commit -m "WIP: Current work before rollback"

# Option 2: Stash changes
git stash save "WIP before rollback"

# Then retry rollback
git reset --hard approve-20251130-150530
```

### Issue: "Checkpoint not found"

**Symptom:**
```bash
git reset --hard approve-20251130-150530
# Error: reference is not a tree: approve-20251130-150530
```

**Solution:**
```bash
# Verify checkpoint exists
git tag -l 'approve-*'

# If missing, use git reflog to find commit SHA
git reflog | grep "Plan approved"

# Rollback using SHA instead
git reset --hard d7e8f9a0
```

### Issue: "Rolled back too far"

**Symptom:** You rolled back to wrong checkpoint and lost more changes than intended

**Solution:**
```bash
# Find the "pre-rollback" safety checkpoint
git tag -l 'pre-rollback-*'

# Restore to pre-rollback state
git reset --hard pre-rollback-20251130-152000

# Or use reflog to find lost commits
git reflog
git reset --hard HEAD@{2}  # Adjust index as needed
```

---

## Related Examples

- **Plan Generation:** `planning-with-git-checkpoints.md`
- **Error Handling:** `checkpoint-failure-handling.md`
- **Git Checkpoint Guide:** `.github/prompts/modules/git-checkpoint-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
