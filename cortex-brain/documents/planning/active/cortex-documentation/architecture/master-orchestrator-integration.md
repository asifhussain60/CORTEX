# Master Orchestrator Integration

**Plan:** cortex-documentation  
**Created:** January 03, 2026  
**Purpose:** Document Master Orchestrator touchpoints for this plan

---

## 🎯 Integration Overview

This plan integrates with CORTEX Master Orchestrator for:

1. **Pattern-Based Routing**: Intent classification and orchestrator selection
2. **State Coordination**: Cross-phase state persistence
3. **Cross-Session Continuation**: Automatic resumption from Tier 1
4. **Execution Monitoring**: Progress tracking and validation

---

## 🔀 Routing Configuration

### Pattern Matching Rules

Add to `cortex-brain/config/master-orchestrator.yaml`:

```yaml
patterns:
  - pattern: "continue cortex-documentation"
    orchestrator: "planning_system"
    context:
      plan_id: "cortex-documentation"
      action: "resume"
      
  - pattern: "cortex-documentation status"
    orchestrator: "planning_system"
    context:
      plan_id: "cortex-documentation"
      action: "status"
```

### Intent Classification

If pattern matching fails, LLM classifier routes based on:
- Plan ID mention in user request
- "continue" keyword detection
- Planning-related vocabulary

---

## 🗄️ State Management

### Database Integration

Plan state stored in `cortex-brain/database/planning_state.db`:

**Tables Used:**
- `plans` - High-level plan metadata
- `phases` - Phase execution tracking
- `tasks` - Granular task status
- `execution_log` - Master Orch routing decisions

### State Queries

```python
# Get current phase
state_mgr.get_current_phase(plan_id="cortex-documentation")

# Resume from checkpoint
state_mgr.resume_from_snapshot(snapshot_id="...")

# Update phase status
state_mgr.update_phase_status(
    phase_id="...",
    status="in_progress"
)
```

---

## 🔄 Cross-Session Context

### Tier 1 Integration

Context middleware queries Tier 1 Working Memory for:
- Last 3 sessions metadata
- Previous orchestrator used
- Primary intent from last session
- Phase status at interruption

### Context Injection

Middleware injects <200 tokens:

```json
{
  "last_session": {
    "orchestrator": "planning_system",
    "plan_id": "cortex-documentation",
    "phase": "Phase 3",
    "status": "in_progress",
    "last_task": "Implementing BaseOrchestrator v4.1"
  },
  "continuation_detected": true
}
```

---

## ⚙️ Execution Engine

### Autonomous Execution

Master Orchestrator's Execution Engine:

1. Loads plan from database
2. Identifies current phase
3. Executes phase tasks autonomously
4. Updates progress in real-time
5. Creates checkpoints after each phase

### Monitoring

Progress tracked in:
- Visual progress bars (in master plan)
- `tracking/progress-tracker.json`
- `execution_log` table (database)

---

## 🛡️ Governance Validation

### Pre-Execution Checks

Master Orchestrator validates:
- SKULL rules compliance (brain-protection-rules.yaml)
- Knowledge Graph queries (similar patterns exist?)
- AST scan results (conflicts detected?)

### Continuous Monitoring

During execution:
- TDD_ENFORCEMENT: Tests run before implementation
- GIT_ISOLATION: No CORTEX files in user repos
- REFACTOR_CLEANUP: Cleanup phase exists

---

## 📚 Resources

| Resource | Path | Purpose |
|----------|------|---------|
| Pattern Router | `src/orchestrators/pattern_router.py` | Intent routing |
| State Manager | `src/orchestrators/state_manager.py` | State persistence |
| Execution Engine | `src/orchestrators/execution_engine.py` | Phase execution |
| Context Middleware | `src/operations/utilities/cross_session_context_middleware.py` | Tier 1 integration |
| Master Orch Config | `cortex-brain/config/master-orchestrator.yaml` | Routing rules |

---

## 🚀 Next Steps

1. Update `master-orchestrator.yaml` with plan-specific patterns
2. Test pattern matching with sample user inputs
3. Verify state manager can load plan from database
4. Validate context middleware injects continuation data
5. Execute Phase -1 (Knowledge Library Review)
