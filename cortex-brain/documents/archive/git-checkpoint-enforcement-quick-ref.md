# Git Checkpoint Wiring Enforcement - Quick Reference

**Status:** ✅ ENFORCED  
**Severity:** BLOCKED  
**Validation Point:** Alignment Orchestrator  

---

## What's Enforced

### 4 Mandatory Validations

1. **Method Exists**
   - `GitCheckpointOrchestrator.create_auto_checkpoint()` must exist
   - Must be callable

2. **Signature Correct**
   - Must have `operation` parameter
   - Must have `message` parameter

3. **Orchestrator Wired**
   - `PlanningOrchestrator.git_checkpoint` must exist
   - Must be `GitCheckpointOrchestrator` instance

4. **Phases Commit**
   - Phase 1 calls `plan-phase-1` checkpoint
   - Phase 2 calls `plan-phase-2` checkpoint
   - Phase 3 calls `plan-phase-3` checkpoint

---

## Quick Test

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

python -c "
from pathlib import Path
from src.orchestrators.alignment_orchestrator import AlignmentOrchestrator

orchestrator = AlignmentOrchestrator(Path.cwd())
result = orchestrator.run_alignment()

if result.orchestrator_wiring_validated:
    print('✅ Git checkpoint wiring VALIDATED')
else:
    print('❌ Git checkpoint wiring FAILED')
    for issue in result.wiring_issues:
        print(f'   - {issue}')
"
```

---

## Expected Results

### ✅ Success
```
✅ Git checkpoint wiring VALIDATED
```

### ❌ Failure Examples
```
❌ Git checkpoint wiring FAILED
   - GitCheckpointOrchestrator missing create_auto_checkpoint method
```

```
❌ Git checkpoint wiring FAILED
   - PlanningOrchestrator.generate_incremental_plan missing git checkpoint for plan-phase-2
```

---

## Integration Points

| System | Enforcement |
|--------|-------------|
| `align` command | ✅ Validates on every run |
| Deployment gates | ✅ Blocks deploy if invalid |
| CI/CD pipeline | ✅ Fails build if invalid |
| Health monitoring | ✅ Reports in health checks |

---

## Fixing Validation Errors

### Error: "missing create_auto_checkpoint method"

**Fix:** Add method to `GitCheckpointOrchestrator`:
```python
def create_auto_checkpoint(
    self,
    operation: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    session_id = f"auto-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    return self.create_checkpoint(
        session_id=session_id,
        checkpoint_type=f"auto-{operation}",
        message=message,
        metadata=metadata
    )
```

### Error: "missing git checkpoint for plan-phase-X"

**Fix:** Add checkpoint call after phase in `PlanningOrchestrator.generate_incremental_plan()`:
```python
# After phase completion
try:
    self.git_checkpoint.create_auto_checkpoint(
        operation="plan-phase-X",
        message=f"Planning Phase X complete: {feature_name}"
    )
    logger.info("✅ Git checkpoint created for Phase X")
except Exception as e:
    logger.warning(f"Git checkpoint failed for Phase X: {e}")
```

### Error: "PlanningOrchestrator missing git_checkpoint attribute"

**Fix:** Add to `PlanningOrchestrator.__init__()`:
```python
self.git_checkpoint = GitCheckpointOrchestrator(project_root=str(self.cortex_root))
```

---

## SKULL Rules Enforced

- ✅ `GIT_CHECKPOINT_ENFORCEMENT` (Severity: BLOCKED)
- ✅ `INCREMENTAL_PLAN_GENERATION` (Severity: BLOCKED)
- ✅ `GIT_ISOLATION_ENFORCEMENT`

---

## Files Involved

**Enforcement Logic:**
- `src/orchestrators/alignment_orchestrator.py`

**Validated Components:**
- `src/orchestrators/git_checkpoint_orchestrator.py`
- `src/orchestrators/planning_orchestrator.py`

**Documentation:**
- `cortex-brain/documents/reports/git-checkpoint-wiring-enforcement.md`
- `cortex-brain/documents/reports/planning-git-checkpoint-integration-report.md`

---

**Last Updated:** 2025-12-04  
**Author:** Asif Hussain
