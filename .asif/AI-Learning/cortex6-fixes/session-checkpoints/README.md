# Session Checkpoints

## Purpose
Preserves conversation context before token limits trigger "Summarizing Conversation History" messages.

## Usage

### Automatic Checkpoint Creation
When token usage reaches ~650K-700K (70% of 1M budget), GitHub Copilot will:
1. Present strategic continuation prompt to user
2. Save checkpoint file: `checkpoint-{timestamp}.yaml`
3. Update `00-CURRENT-STATUS.md` with latest state
4. Provide continuation command for user to copy

### Manual Checkpoint Creation
```bash
# Create checkpoint manually
python3 -m src.main "create checkpoint for cortex6-fixes"
```

### Resuming from Checkpoint
After conversation is summarized, use any of these commands:
```
continue cortex6-fixes from {last_task_id}
resume {phase_id}
pick up where we left off
continue CORTEX6-REMEDIATION-2026-01-08
```

## Checkpoint File Format
```yaml
checkpoint_id: CP-{timestamp}
plan_id: CORTEX6-REMEDIATION-2026-01-08
created_at: {ISO-8601 timestamp}
token_usage: {tokens_used}/{token_limit}

session_context:
  current_phase: {phase_id}
  current_task: {task_id}
  last_completed: {task_id}
  tasks_completed: {count}
  tasks_total: {count}

work_state:
  modified_files: [...]
  test_status: "passing/failing"
  health_score: {score}
  uncommitted_changes: true/false

next_steps:
  - task_id: {next_task_id}
    name: {task_name}
    estimated_hours: {hours}
    dependencies: [...]

continuation_command: "continue cortex6-fixes from {last_task_id} - resume {phase_id}"
```

## Checkpoint Lifecycle
1. **Creation**: Triggered at 70% token usage or manually
2. **Storage**: Persisted to disk in this directory
3. **Resume**: Loaded when user provides continuation command
4. **Retention**: Keep last 10 checkpoints, archive older ones
5. **Cleanup**: Archive checkpoints >7 days old to `archives/`

## Integration with Plan
- Referenced in `00-REMEDIATION-MASTER-PLAN.yaml` under `execution_protocol.continuation_management`
- Status dashboard always shows latest checkpoint: `00-CURRENT-STATUS.md`
- Phase YAMLs updated before checkpoint creation

## Benefits
✅ Seamless resumption after conversation summaries
✅ Zero context loss across sessions
✅ User controls continuation timing
✅ Automatic state preservation
✅ Clear continuation commands

---

*Part of CORTEX 6.0 Remediation Plan - Strategic Context Preservation System*
