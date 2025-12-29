# Orchestrator Progress Templates - Implementation Guide

**Created:** December 8, 2025  
**Author:** Asif Hussain  
**Version:** 3.8.1

---

## Overview

Integrated visual progress templates into key orchestrators to provide real-time phase updates in GitHub Copilot Chat during autonomous execution. Users can now see progress bars, phase status, and execution details as long-running operations proceed.

---

## Templates Created

### 1. Autonomous Execution Progress

**Template:** `autonomous_execution_progress`  
**Location:** `cortex-brain/response-templates.yaml` (lines 48-90)

**Purpose:** Display plan execution progress during autonomous phase-by-phase execution

**Fields:**
- `progress_bar` - Visual progress bar (e.g., `[████████░░]`)
- `percentage` - Completion percentage (0-100)
- `current_phase` - Current phase number
- `total_phases` - Total number of phases
- `phase_name` - Name of current phase
- `completed_tasks` - Number of completed tasks
- `total_tasks` - Total tasks in plan
- `elapsed_time` - Time elapsed since start
- `current_task` - Currently executing task
- `plan_id` - Plan identifier
- `status` - Execution status (executing/completed)

**Example Output:**
```markdown
## 🧠 CORTEX Autonomous Plan Execution
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 📊 Execution Progress

**Progress:** [████████░░] 80%

🔄 **Phase 3 of 4:** Implementation
✅ **Tasks Completed:** 12/15
⏱️  **Elapsed Time:** 25m 30s
📋 **Current Task:** 3.4 - Implement data layer

### 🎯 Plan Details

**Plan ID:** PLAN-2025-12-08-feature-xyz
**Status:** executing
**Phases:** Phase 1: Planning, Phase 2: Design, Phase 3: Implementation, Phase 4: Testing
```

---

### 2. Maintenance Phase Progress

**Template:** `maintenance_phase_progress`  
**Location:** `cortex-brain/response-templates.yaml` (lines 92-118)

**Purpose:** Display system maintenance phase progress with metrics

**Fields:**
- `current_phase` - Current phase number
- `total_phases` - Total phases (5 or 6 with EPM)
- `phase_name` - Current phase name
- `phase_status_list` - Formatted list of all phases with status
- `total_improvements` - Number of improvements applied
- `total_warnings` - Number of warnings
- `total_errors` - Number of errors
- `elapsed_time` - Time elapsed (formatted as "Xm Ys")
- `current_operation` - Current operation status

**Example Output:**
```markdown
## 🔧 System Maintenance Progress

**Phase 3 of 5:** Cleanup and Organization

### 📊 Phase Status

**Phase 1:** Pre-maintenance Healthcheck - ✅ Complete
**Phase 2:** System Alignment - ✅ Complete
**Phase 3:** Cleanup and Organization - 🔄 In Progress
**Phase 4:** CORTEX Optimization - ⏳ Pending
**Phase 5:** Post-maintenance Healthcheck - ⏳ Pending

### 📈 Metrics Summary

✅ **Improvements Applied:** 15
⚠️  **Warnings:** 2
❌ **Errors:** 0

### ⏱️ Progress

**Elapsed Time:** 8m 23s
**Current Operation:** Organizing files
```

---

### 3. Checkpoint Status

**Template:** `checkpoint_status`  
**Location:** `cortex-brain/response-templates.yaml` (lines 120-135)

**Purpose:** Display git checkpoint status after phase boundaries

**Fields:**
- `operation` - Operation that triggered checkpoint
- `status` - Success/failure indicator
- `commit_message` - Git commit message
- `files_changed` - Number of files changed
- `timestamp` - Checkpoint timestamp
- `error_details` - Error information (if failed)

**Example Output:**
```markdown
## 🔖 Git Checkpoint

**Operation:** autonomous_execution
**Status:** ✅ Success

### 📝 Commit Details

**Message:** Completed Implementation of plan PLAN-2025-12-08-feature-xyz
**Files Changed:** 12
**Timestamp:** 2025-12-08 14:45:30
```

---

## Integration Points

### 1. PlanningOrchestrator

**File:** `src/orchestrators/planning_orchestrator.py`

**Integration Location:** `execute_plan_autonomously()` method (lines 1520-1620)

**When Rendered:**
- **Phase Start:** At the beginning of each phase execution
- **Git Checkpoint:** After completing each phase (success or failure)

**Code Pattern:**
```python
# Phase start progress
if self.template_manager:
    try:
        phase_progress_context = {
            'progress_bar': self._generate_progress_bar(completed, total),
            'percentage': int((completed / total) * 100),
            'current_phase': phase_idx,
            'total_phases': total_phases,
            'phase_name': phase_name,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'current_task': f'Starting {phase_name}',
            'plan_id': plan_id,
            'status': 'executing'
        }
        rendered = self.template_manager.render('autonomous_execution_progress', phase_progress_context)
        print(f"\n{rendered}\n")
    except Exception as e:
        logger.debug(f"Template rendering skipped: {e}")

# Git checkpoint status
checkpoint_context = {
    'operation': 'autonomous_execution',
    'status': '✅ Success',
    'commit_message': f"Completed {phase_name} of plan {plan_id}",
    'files_changed': checkpoint_result.get('files_changed', 'N/A'),
    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'error_details': ''
}
rendered = self.template_manager.render('checkpoint_status', checkpoint_context)
print(f"\n{rendered}\n")
```

---

### 2. SystemMaintenanceOrchestrator

**File:** `src/operations/modules/orchestration/system_maintenance_orchestrator.py`

**Integration Location:** 
- `__init__()` - Template manager initialization (lines 49-64)
- `execute()` - Phase progress rendering after each phase (lines 90-165)
- `_render_phase_progress()` - Rendering method (lines 465-520)

**When Rendered:**
- After each phase completes (healthcheck, alignment, cleanup, optimization)

**Code Pattern:**
```python
# Initialize template manager in __init__
try:
    from src.response_templates.response_template_manager import ResponseTemplateManager
    self.template_manager = ResponseTemplateManager()
except Exception as e:
    logger.warning(f"Failed to initialize template manager: {e}")
    self.template_manager = None

# Render after phase completion
self._render_phase_progress(
    current_phase, 
    total_phases, 
    "System Alignment", 
    "Completed"
)
```

---

## User Experience Flow

### Autonomous Plan Execution

1. User: `execute all phases autonomously`
2. **Phase 1 Start** → Chat shows progress template
   ```
   Phase 1 of 4: Planning
   Progress: [██░░░░░░░░] 20%
   Tasks: 3/15 completed
   ```
3. **Phase 1 Complete** → Chat shows checkpoint status
   ```
   ✅ Git Checkpoint: Completed Planning
   Files Changed: 5
   ```
4. **Phase 2 Start** → Chat updates progress
   ```
   Phase 2 of 4: Design
   Progress: [████░░░░░░] 40%
   Tasks: 6/15 completed
   ```
5. Process continues for all phases with real-time updates

---

### System Maintenance Execution

1. User: `system maintenance`
2. **Phase 1** → Pre-healthcheck progress shown
   ```
   Phase 1 of 5: Pre-maintenance Healthcheck - ✅ Complete
   Improvements: 1
   ```
3. **Phase 2** → Alignment progress shown
   ```
   Phase 2 of 5: System Alignment - 🔄 In Progress
   Improvements: 8 (alignment fixes)
   ```
4. **Phase 3** → Cleanup progress shown
   ```
   Phase 3 of 5: Cleanup and Organization - ✅ Complete
   Improvements: 12 (files organized)
   ```
5. Continues through optimization and post-healthcheck

---

## Benefits

### 1. Visibility
- Users see real-time progress instead of waiting silently
- Clear indication of which phase is executing
- Transparency into multi-phase operations

### 2. Confidence
- Visual progress bars show forward movement
- Checkpoint confirmations provide reassurance
- Phase completion markers indicate steady progress

### 3. Debugging
- Phase-level granularity helps identify slow operations
- Checkpoint failures immediately visible
- Metrics (improvements/warnings/errors) updated in real-time

### 4. User Control
- Users can cancel if execution takes too long
- Progress estimates help with time management
- Clear phase boundaries allow for interruption points

---

## Testing

### Manual Test: Planning Orchestrator

```python
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

orchestrator = PlanningOrchestrator(cortex_root="/path/to/CORTEX")

# Execute approved plan autonomously
result = orchestrator.execute_plan_autonomously("PLAN-2025-12-08-test.yaml")

# Expected: Progress templates render in console as phases execute
# Expected: Checkpoint status templates render after each phase
```

### Manual Test: System Maintenance Orchestrator

```python
from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

orchestrator = SystemMaintenanceOrchestrator()

# Execute maintenance
result = orchestrator.execute({})

# Expected: Phase progress templates render after each phase
# Expected: Metrics update in each template
```

---

## Configuration

### Disabling Template Rendering

Templates gracefully degrade if template manager fails to initialize:

```python
try:
    self.template_manager = ResponseTemplateManager()
except Exception as e:
    logger.warning(f"Failed to initialize template manager: {e}")
    self.template_manager = None  # Falls back to basic logging
```

### Template Customization

Edit templates in `cortex-brain/response-templates.yaml`:

```yaml
shared:
  autonomous_execution_progress:
    format: '## 🧠 CORTEX Autonomous Plan Execution
      
      ### 📊 Execution Progress
      
      **Progress:** [{progress_bar}] {percentage}%
      
      # Customize fields here
      '
```

---

## Future Enhancements

### Planned Features

1. **ETA Calculation** - Add estimated time remaining to progress templates
2. **Task-Level Progress** - Show individual task progress within phases
3. **Performance Metrics** - Display execution speed and resource usage
4. **Cancellation Points** - Allow user to cancel at phase boundaries
5. **Email Notifications** - Send progress updates for long operations
6. **Dashboard Integration** - Show live progress in dashboard UI

### Template Expansion

Additional templates to create:
- `task_execution_progress` - Granular task-level updates
- `error_recovery_status` - Show error recovery attempts
- `validation_results` - Display validation gate results
- `deployment_progress` - Multi-stage deployment tracking

---

## Troubleshooting

### Issue: Templates not rendering

**Cause:** Template manager failed to initialize  
**Fix:** Check logs for initialization error, verify `response-templates.yaml` is valid

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates.yaml'))"
```

### Issue: Progress not updating

**Cause:** `yield_progress()` calls missing  
**Fix:** Ensure `@with_progress` decorator present and `yield_progress()` called regularly

### Issue: Templates show incorrect data

**Cause:** Context dict missing required fields  
**Fix:** Review template field requirements in this guide

---

## Files Modified

| File | Lines Changed | Purpose |
|------|--------------|---------|
| `cortex-brain/response-templates.yaml` | +44 lines | Added 3 new templates |
| `src/orchestrators/planning_orchestrator.py` | +60 lines | Integrated phase & checkpoint rendering |
| `src/operations/modules/orchestration/system_maintenance_orchestrator.py` | +73 lines | Added template manager & phase rendering |

---

## Related Documentation

- **Progress Monitoring:** `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`
- **Planning System:** `.github/prompts/modules/planning-orchestrator-guide.md`
- **System Maintenance:** `cortex-brain/documents/implementation-guides/system-maintenance-orchestrator.md`
- **Template System:** `src/response_templates/README.md`

---

**Status:** ✅ COMPLETE - Visual progress templates integrated into PlanningOrchestrator and SystemMaintenanceOrchestrator with real-time chat updates during autonomous execution.

**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Source-Available
