# Workflow Orchestrator

**Purpose:** Coordinates multi-step operations with validation, checkpoints, and error handling

**Version:** 3.2.0  
**Status:** ✅ PRODUCTION

---

## Commands

- `workflow` or `execute workflow` - Run workflow operation
- `workflow status` - Show current workflow state
- `resume workflow` - Continue interrupted workflow

---

## What It Does

**Workflow orchestrator provides:**
1. **Multi-Step Coordination:** Chains operations in sequence
2. **Validation Gates:** Validates inputs/outputs between steps
3. **Checkpoint System:** Saves progress for resumability
4. **Error Handling:** Graceful failures with rollback capability
5. **Progress Tracking:** Real-time status updates

---

## Workflow Types

**Supported Workflows:**
- Feature Development (Plan → Implement → Test → Deploy)
- Onboarding (Setup → Configure → Validate → Tutorial)
- Migration (Backup → Transform → Validate → Deploy)
- Custom (User-defined step sequences)

---

## How It Works

```
1. Workflow Definition
   ↓
2. Pre-Validation (inputs, prerequisites)
   ↓
3. Step Execution (with checkpoints)
   ↓
4. Inter-Step Validation (outputs → next inputs)
   ↓
5. Post-Validation (final results)
   ↓
6. Completion Report
```

---

## Checkpoint System

**Purpose:** Enable workflow resumption after interruptions

**Checkpoints Store:**
- Current step index
- Step outputs/results
- Validation status
- Timestamp and session ID

**Location:** `cortex-brain/workflows/checkpoints/[workflow-id].json`

---

## Error Handling

**On Error:**
1. **Capture:** Log error details (step, context, stack trace)
2. **Rollback:** Undo partial changes if configured
3. **Save State:** Create recovery checkpoint
4. **Notify:** Report error with recovery options
5. **Suggest:** Provide actionable next steps

**Recovery Options:**
- Retry failed step
- Skip step (with confirmation)
- Rollback to previous checkpoint
- Abort workflow

---

## Validation Gates

**Pre-Validation:** Before workflow starts
- Check prerequisites (dependencies, permissions)
- Validate inputs (types, ranges, existence)
- Verify system health

**Inter-Step Validation:** Between steps
- Verify previous step succeeded
- Check output meets requirements
- Validate inputs for next step

**Post-Validation:** After workflow completes
- Verify all steps completed successfully
- Validate final outputs
- Check system integrity

---

## Configuration

**Configurable via cortex.config.json:**
```json
{
  "workflow": {
    "enable_checkpoints": true,
    "checkpoint_frequency": "per_step",
    "enable_rollback": true,
    "max_retry_attempts": 3,
    "timeout_seconds": 3600
  }
}
```

---

## Integration Points

- **All Orchestrators:** Can be wrapped in workflows
- **Planning System:** Integrates with feature planning
- **TDD Mastery:** Supports test-driven workflows
- **Brain System:** Stores workflow history in Tier 1

---

## Natural Language Examples

- "execute feature development workflow"
- "start onboarding workflow"
- "resume interrupted workflow"
- "show workflow status"

---

## Output

**Console:**
```
🔄 CORTEX Workflow Execution

📋 Workflow: Feature Development
   Steps: 4 total

✅ Step 1/4: Feature Planning
   Duration: 2m 15s
   Status: Complete

✅ Step 2/4: Implementation
   Duration: 8m 42s
   Status: Complete

⏳ Step 3/4: Testing
   Status: In Progress...
```

**Files Created:**
- `cortex-brain/workflows/[workflow-id]/workflow.json` (definition)
- `cortex-brain/workflows/[workflow-id]/checkpoints/` (progress)
- `cortex-brain/workflows/[workflow-id]/results.json` (final output)

---

## Testing

**Test File:** `tests/operations/modules/test_workflow_orchestrator.py`

**Coverage:** >70% required for deployment

**Key Tests:**
- Workflow execution with all steps
- Checkpoint save/restore
- Error handling and rollback
- Validation gates

---

## See Also

- TDD Mastery: `.github/prompts/modules/tdd-mastery-guide.md`
- Planning System: `.github/prompts/modules/planning-system-guide.md`
- Operation Factory: `cortex-brain/documents/implementation-guides/operation-factory.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
