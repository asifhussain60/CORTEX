# Incremental Planning Integration Guide

**Version:** 1.0  
**Date:** December 8, 2025  
**Author:** Asif Hussain

---

## Overview

The Planning System now automatically delegates to incremental plan generation for complex features, preventing response length failures and creating plans phase-by-phase.

## Problem Solved

**Before:** User requests like "plan JWT authentication" would try to generate the entire plan in one LLM call, hitting response length limits and failing.

**After:** Complex features are automatically detected and routed to incremental generator, creating plans in manageable chunks:
1. Skeleton (200 tokens) → approval
2. Phase 1 sections (500 tokens each) → approval  
3. Phase 2 sections (500 tokens each) → approval
4. Phase 3 sections (500 tokens each) → approval

## Complexity Detection

### AUTO-DETECTION Algorithm

The system analyzes feature name, description, and user input to determine complexity:

**HIGH Complexity** (Always Incremental):
- Security: `auth`, `jwt`, `token`, `session`, `security`, `encrypt`, `hash`
- Access Control: `permission`, `role`, `access control`
- Data: `migration`, `schema change`, `alter table`, `data model`
- Architecture: `microservice`, `api gateway`, `event driven`, `message queue`
- External: `external api`, `third-party`
- Multi-phase: `multi-phase`, `all phases`, `end to end`

**MEDIUM Complexity** (Incremental if description >50 chars):
- Refactoring: `refactor`, `restructure`
- API: `new endpoint`, `new route`
- Frontend: `ui change`, `frontend`, `react`, `vue`
- Database: `database`, `query`, `index`
- Performance: `performance`, `optimize`, `cache`
- Deployment: `deployment`, `ci/cd`, `pipeline`

**LOW Complexity** (Simple Skeleton):
- Bug fixes, config changes, typos, simple enhancements

### Manual Override

While auto-detection is automatic, you can still specify complexity:

```python
from src.operations.modules.planning.planning_utility import create_plan

result = create_plan(
    feature_name="My Feature",
    description="Description here",
    complexity="high",  # Will be overridden if auto-detection differs
    user_input="plan my feature"
)
```

## Integration Points

### 1. Planning Utility (`src/operations/modules/planning/planning_utility.py`)

**New Functions:**
- `detect_plan_complexity()` - Analyzes feature for complexity indicators
- `_create_plan_incremental()` - Delegates to PlanningOrchestrator

**Modified Functions:**
- `create_plan()` - Now detects complexity and delegates appropriately

### 2. Planning Orchestrator (`src/orchestrators/planning_orchestrator.py`)

**New Helper Methods:**
- `_create_empty_plan_file()` - Creates initial plan file
- `_append_phase_to_plan()` - Appends phases incrementally

**Existing Methods:**
- `generate_incremental_plan()` - Phase-by-phase generation (now wired up)

### 3. Operations CLI (`src/operations/planning.py`)

No changes needed - automatically inherits new behavior through `create_plan()`.

## User Experience

### Simple Feature (Auto-Skeleton)

```
User: "plan fix typo in button"

CORTEX: ✅ LOW complexity: Using simple plan skeleton
        📄 Plan created: fix-typo-in-button-20251208.yaml
        Location: cortex-brain/documents/planning/features/active/
```

### Complex Feature (Auto-Incremental)

```
User: "plan JWT authentication with refresh tokens"

CORTEX: 🎯 HIGH complexity detected: Security-critical authentication feature
        🔄 Delegating to incremental generator
        
        🔍 Incremental Plan Generation started...
        ⏳ Skeleton generated (200 tokens): 1/5 (20.0%, 2.1s, ETA: 8.4s)
        ⏳ Phase 1: Foundation complete: 2/5 (40.0%, 4.5s, ETA: 6.8s)
        ⏳ Phase 2: Development complete: 3/5 (60.0%, 7.2s, ETA: 4.8s)
        ⏳ Phase 3: Validation & Deployment complete: 4/5 (80.0%, 9.8s, ETA: 2.5s)
        ⏳ Plan finalized with TDD requirements: 5/5 (100.0%, 12.1s)
        ✅ Incremental Plan Generation completed (12.1s)
        
        ✅ Plan complete: jwt-authentication-with-refresh-tokens-20251208.yaml
        Location: cortex-brain/documents/planning/features/active/
```

**Visual Progress Features:**
- Real-time progress bar updates
- Phase-by-phase completion tracking
- ETA calculation based on generation velocity
- Total time reporting

## Execution Modes

### Approval-Gated (Default)

Currently auto-approves checkpoints. Interactive approval coming in future version.

```
User: "plan authentication system"
```

### Autonomous (Auto-Execute)

Auto-approves all checkpoints without prompting:

```
User: "plan authentication system - execute all phases autonomously"
User: "plan migration - auto chained"
User: "plan refactor - without user intervention"
```

## Configuration

### Enable/Disable Incremental

To temporarily disable incremental generation (testing only):

```python
# In planning_utility.py, modify ORCHESTRATOR_AVAILABLE
ORCHESTRATOR_AVAILABLE = False  # Forces all plans to use skeleton
```

### Adjust Complexity Thresholds

Modify `detect_plan_complexity()` in `planning_utility.py`:

```python
# Change description length threshold for medium complexity
if description_length > 100:  # Default: 100 chars
    return ("medium", True, "Detailed description")
```

## Testing

### Manual Testing

```bash
# Test complexity detection
python -c "
from src.operations.modules.planning.planning_utility import detect_plan_complexity
complexity, use_inc, reason = detect_plan_complexity('JWT Auth', 'Add auth', 'plan auth')
print(f'Complexity: {complexity}, Incremental: {use_inc}')
"

# Test simple plan creation
python -m src.operations.planning create "Fix Typo" --description "Fix button typo"

# Test complex plan creation  
python -m src.operations.planning create "JWT Authentication" --description "JWT auth with refresh tokens and RBAC"
```

### Automated Testing

```bash
# Run integration tests
python test_incremental_wiring.py
```

## Troubleshooting

### Issue: All Plans Use Skeleton

**Cause:** `ORCHESTRATOR_AVAILABLE = False` or import error  
**Fix:** Check orchestrator imports and ensure `PlanningOrchestrator` is available

### Issue: Incremental Generation Fails

**Cause:** Missing helper methods or generator initialization error  
**Fix:** Check logs for specific error, ensure `IncrementalPlanGenerator` is initialized

### Issue: Wrong Complexity Detected

**Cause:** Keywords not matching or description too short  
**Fix:** Add keywords to `detect_plan_complexity()` or provide longer description

## Future Enhancements

1. **Interactive Checkpoint Approval** - Prompt user for phase approvals
2. **Complexity Learning** - Learn from user feedback to improve detection
3. **Custom Complexity Rules** - User-defined patterns for project-specific detection
4. **Progress Dashboard** - Real-time visualization of plan generation progress
5. **Resume from Checkpoint** - Pause and resume plan generation

## Migration Notes

### Existing Plans

No migration needed - existing plans continue to work.

### API Compatibility

`create_plan()` API unchanged - complexity parameter still accepted but may be overridden.

### Behavior Changes

- Plans now auto-detect complexity (previously used provided value)
- Complex features automatically use incremental generation (previously skeleton only)
- Execution mode now affects checkpoint approval behavior

---

**Related Documentation:**
- `.github/prompts/modules/planning-orchestrator-guide.md` - Planning System overview
- `src/workflows/incremental_plan_generator.py` - Incremental generator implementation
- `cortex-brain/brain-protection-rules.yaml` - TDD_ENFORCEMENT rules for plans

**Support:** For issues or questions, check logs in `cortex-brain/documents/planning/`
