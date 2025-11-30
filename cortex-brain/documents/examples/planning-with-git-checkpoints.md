# Planning Workflow with Git Checkpoints - Example

**Purpose:** Demonstrate automatic git checkpoint creation during planning operations  
**Author:** Asif Hussain  
**Version:** 1.0

---

## Overview

CORTEX automatically creates git checkpoints during planning operations, providing instant rollback capability for all planning workflow stages.

---

## Example: Feature Planning with Checkpoints

### Scenario

You want to plan a new user authentication feature with automatic safety checkpoints.

### Step 1: Generate Plan

```
User: "plan user authentication with JWT tokens"

CORTEX:
  📸 Creating checkpoint: plan-20251130-143022
  ✅ Checkpoint created successfully
  
  🎯 Starting incremental plan generation...
  
  [... generates 3-phase plan ...]
  
  ✅ Plan generated: PLAN-20251130-authentication.md
  📍 Checkpoint available for rollback: plan-20251130-143022
```

**What Happened:**
- CORTEX created pre-work checkpoint **before** generating plan
- Checkpoint name: `plan-20251130-143022` (operation-date-time format)
- Checkpoint message: "Starting plan generation: User authentication with JWT..."
- If generation fails or produces unexpected results, you can rollback

### Step 2: Review and Approve Plan

```
User: "approve plan authentication"

CORTEX:
  📋 Moving plan to approved directory...
  ✅ Status updated: active → approved
  
  📸 Creating checkpoint: approve-20251130-143856
  ✅ Checkpoint created: Plan approved: PLAN-20251130-authentication.md
  
  📍 Plan approved and checkpoint saved
```

**What Happened:**
- Plan moved from `active/` to `approved/` directory
- CORTEX created post-work checkpoint **after** approval
- Checkpoint name: `approve-20251130-143856`
- Checkpoint message: "Plan approved: PLAN-20251130-authentication.md"
- If approval was premature, you can rollback to restore plan to active state

### Step 3: Complete Plan

```
User: "complete plan authentication"

CORTEX:
  📋 Moving plan to completed directory...
  ✅ Status updated: approved → completed
  
  📸 Creating checkpoint: complete-20251130-144512
  ✅ Checkpoint created: Plan completed: PLAN-20251130-authentication.md
  
  🎉 Planning workflow complete!
```

**What Happened:**
- Plan moved from `approved/` to `completed/` directory
- CORTEX created post-work checkpoint **after** completion
- Checkpoint name: `complete-20251130-144512`
- Checkpoint message: "Plan completed: PLAN-20251130-authentication.md"
- Final checkpoint marks end of planning workflow

---

## Viewing Checkpoints

### List All Planning Checkpoints

```bash
# Show all checkpoints from today
git tag -l '*-20251130-*' --sort=-creatordate

# Output:
complete-20251130-144512
approve-20251130-143856
plan-20251130-143022
```

### View Checkpoint Details

```bash
# Show checkpoint metadata
git show plan-20251130-143022

# Output:
tag plan-20251130-143022
Tagger: CORTEX <cortex@ai.assistant>
Date:   Sat Nov 30 14:30:22 2025 -0500

Starting plan generation: User authentication with JWT tokens

commit a1b2c3d4e5f6...
Author: Your Name <you@email.com>
Date:   Sat Nov 30 14:30:00 2025 -0500

    Last commit before planning
```

### Show Changes Since Checkpoint

```bash
# Compare current state to plan generation checkpoint
git diff plan-20251130-143022

# Shows all changes made during planning workflow
```

---

## Checkpoint Naming Convention

**Format:** `{operation}-{YYYYMMDD}-{HHMMSS}`

**Examples:**
- `plan-20251130-143022` - Plan generation at 2:30:22 PM
- `approve-20251130-143856` - Plan approval at 2:38:56 PM
- `complete-20251130-144512` - Plan completion at 2:45:12 PM

**Why This Format:**
- **Operation prefix** - Quickly identify checkpoint type
- **Date (YYYYMMDD)** - Easy sorting and filtering
- **Time (HHMMSS)** - Precise timestamp for same-day operations
- **Chronological sorting** - Natural ordering by timestamp

---

## Checkpoint Operations

### Generate (`plan`)

**When Created:** Before plan generation starts  
**Operation:** `plan`  
**Message Format:** `"Starting plan generation: {feature_name}"`  
**Message Example:** `"Starting plan generation: User authentication with JWT tokens"`

**Use Case:**
- Rollback if plan generation produces unexpected structure
- Restore before plan generation attempt
- Undo auto-generated content

### Approve (`approve`)

**When Created:** After plan approval completes  
**Operation:** `approve`  
**Message Format:** `"Plan approved: {plan_filename}"`  
**Message Example:** `"Plan approved: PLAN-20251130-authentication.md"`

**Use Case:**
- Rollback premature approval
- Restore plan to active state for more changes
- Undo status transition

### Complete (`complete`)

**When Created:** After plan completion  
**Operation:** `complete`  
**Message Format:** `"Plan completed: {plan_filename}"`  
**Message Example:** `"Plan completed: PLAN-20251130-authentication.md"`

**Use Case:**
- Revert completion if work resumes
- Restore plan to approved state
- Undo final status transition

---

## Benefits

✅ **Instant Rollback** - Return to any planning stage in seconds  
✅ **Safe Experimentation** - Try bold changes without fear  
✅ **Clear History** - Track exactly what changed and when  
✅ **Zero Data Loss** - Never lose planning work  
✅ **Non-Blocking** - Planning continues even if checkpoint fails  

---

## Related Documentation

- **Rollback Examples:** `rollback-plan-approval.md`
- **Error Handling:** `checkpoint-failure-handling.md`
- **Git Checkpoint Guide:** `.github/prompts/modules/git-checkpoint-guide.md`
- **Planning System 2.0:** `.github/prompts/modules/planning-orchestrator-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
