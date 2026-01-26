# EXECUTION GUIDE: UnifiedExecutionConfig Plan
## How to Use the Machine-Readable Plan
**Generated:** 2026-01-26 | **Plan ID:** plan_exec_config_refactor_001

---

## 🎯 Quick Start

### For MasterOrchestrator:
```python
# Load the autonomous plan
plan = PlanningOrchestrator.load_plan(
    plan_file="cortex-registry/planning/execution-config-refactor-plan-2026-01-26.yaml"
)

# Validate and execute
if plan.approval_status.status == "ACTIVE":
    result = PlanningOrchestrator.execute_autonomous(plan)
else:
    print("Awaiting user approval...")
    result = PlanningOrchestrator.wait_for_approval(plan)
```

### For Human Reviewers:
1. **Read Section 1 (Metadata)** - Understand mission and timeline
2. **Read Section 2 (Classification)** - Verify refactor scope
3. **Read Section 7 (Risks)** - Understand mitigation strategy
4. **Review Section 6 (WBS)** - Examine phases and tasks
5. **Approve or modify** in Approval Gate section
6. **Proceed** → Triggers Phase 0 execution

---

## 📋 Plan Structure (Machine-Readable)

### Top-Level Keys:
- `plan.metadata` - Immutable plan identity
- `plan.request` - Original user request + context
- `plan.classification` - LENS output (intent, confidence, scope)
- `plan.git_context` - Pre-execution validation
- `plan.challenges` - Strategic challenges (addressed in phases)
- `plan.execution_gates` - Approval requirements
- `plan.phases` - Work breakdown structure (5 phases)
- `plan.risks` - Risk register with mitigation
- `plan.success_criteria` - Measurable success metrics
- `plan.deliverables` - Output checklist per phase
- `plan.governance` - CORE rules compliance
- `plan.status` - State machine (TEMP → PENDING_APPROVAL → ACTIVE → EXECUTING → EXECUTED)

### Each Phase Structure:
```yaml
- phase_id: "phase_N_name"
  phase_name: "Human-readable name"
  phase_type: "FOUNDATION|IMPLEMENTATION|INTEGRATION|VALIDATION|DEPLOYMENT"
  estimated_hours: N
  status: "PENDING_APPROVAL|PENDING_IMPLEMENTATION|IN_PROGRESS|COMPLETE"
  description: "What this phase accomplishes"
  
  tasks:
    - task_id: "task_N_M"
      task_name: "Name"
      estimated_minutes: NN
      handler: "Orchestrator responsible"
      acceptance_criteria:
        - "Criterion 1"
        - "Criterion 2"
      inputs: ["file1.py"]
      outputs: ["file2.py", "test_file2.py"]
      implementation_notes: "How to implement"
```

---

## ⚡ Execution Patterns

### Pattern 1: Sequential Execution
```python
for phase in plan.phases:
    for task in phase.tasks:
        result = execute_task(task)
        if result.is_err():
            log_failure(task, result.error)
            suggest_rollback(phase)
            break
    checkpoint_phase(phase)
```

### Pattern 2: Parallel Execution (Safe Tasks)
```python
# Tasks in Phase 1 can run in parallel:
# - task_1_1 (schema design) - independent
# - task_1_2 (dataclass implementation) - depends on task_1_1
# - task_1_3 (validator) - depends on task_1_1
# Use DAG dependency resolution
```

### Pattern 3: Feature-Flagged Rollout (Phase 5)
```python
# Day 1: Shadow mode
feature_flag.set_mode('execution_config_v1', 'SHADOW')
# Config generated but not used, compare results

# Day 2: Canary (25%)
feature_flag.set_mode('execution_config_v1', 'ENABLED')
feature_flag.set_canary_percentage(25)

# Day 4: Full rollout
feature_flag.set_canary_percentage(100)
```

---

## 🔍 Key Milestones

| Phase | Milestone | Checkpoint |
|-------|-----------|------------|
| 0 | Verify markdown generation | AC-EXEC-CONFIG-001 |
| 1 | YAML schema complete | task_1_4 passing integration tests |
| 2 | Master integration complete | All new tests passing, zero markdown verified |
| 3 | Challenge system working | ConfigInteractionProtocol integrated |
| 4 | All validations pass | Coverage >= 85%, latency OK, no markdown audit clean |
| 5 | Day 4 full rollout | 100% traffic on config flow, monitoring stable |

---

## ⚠️ Abort Conditions

**Auto-rollback triggers (Phase 5):**
1. Error rate > 2% for 5 consecutive minutes
2. Latency p95 > 200ms consistently
3. Database failures > 1%
4. User approval failures > 5%

**Manual abort triggers:**
1. Task acceptance criteria not met
2. Unexpected blocker discovered
3. Governance violations detected
4. Code review rejects implementation

**Rollback procedure:**
```bash
# 1. Disable feature flag
feature_flag.set_mode('execution_config_v1', 'DISABLED')

# 2. All traffic reverts to markdown flow
# 3. Investigate root cause
# 4. Update plan with findings
# 5. Retry with modifications
```

---

## 📊 Progress Tracking

### Dashboard Metrics:
- **Phase completion %:** (completed_tasks / total_tasks)
- **Test coverage %:** (covered_lines / total_lines)
- **Latency (ms):** p50, p95, p99 during staged rollout
- **Error rate %:** failures / total operations
- **Git commits:** AC-EXEC-CONFIG-* count

### Checkpoints:
```yaml
checkpoints:
  - phase_0_complete: "Git commit: AC-EXEC-CONFIG-001"
  - phase_1_complete: "100+ unit tests passing"
  - phase_2_complete: "execute_operation() wired, zero markdown confirmed"
  - phase_3_complete: "InteractionOrchestrator integration done"
  - phase_4_complete: "Test report: >=85% coverage, performance OK"
  - phase_5_complete: "Git commit: AC-EXEC-CONFIG-002, monitoring stable 48h"
```

---

## 🔗 Integration with CORTEX Systems

### DatabaseBackedRegistry:
- Stores UnifiedExecutionConfig as JSON
- Schema version tracked for migrations
- Query: `SELECT * FROM execution_configs WHERE status = 'APPROVED'`

### GovernanceRegistry:
- Validates YAML config against CORE-001 through CORE-035
- Returns violations list
- Blocks execution if Tier0 rules violated

### BehavioralBoundaryRules:
- Checks operation against behavioral limits
- Integrates with config generation
- Returns boundary report

### EnhancedAuditLogger:
- Logs every config state transition
- AC_START/AC_COMPLETE for each task
- Searchable audit trail

### MCP Tools:
- PlanningOrchestrator.load_plan()
- PlanningOrchestrator.execute_autonomous()
- PlanningOrchestrator.report_progress()

---

## 📝 Approval Decision Card

### For User Review:
```
PLAN: UnifiedExecutionConfig Refactor
ID: plan_exec_config_refactor_001

SCOPE:
  - Replace markdown approval with YAML-based certification
  - Eliminate all markdown from execute_operation() flow
  - Zero-breaking-changes (feature-flagged)

TIMELINE:
  - Total effort: 10-16 hours
  - Phases: 5 (Foundation → Implementation → Integration → Validation → Deployment)
  - Staged rollout: 4 days

RISK LEVEL: 🟢 LOW
  - Auto-rollback on error rate > 2%
  - Shadow mode Day 1 catches issues early
  - Feature flag allows fast revert

BENEFITS:
  - 🟢 Extensible: New intent types without code changes
  - 🟢 Scalable: Distributed execution ready
  - 🟢 Accurate: 100% decision audit trail
  - 🟢 Efficient: <50ms config generation

DECISION:
  [ ] APPROVE - Proceed with Phase 0
  [ ] APPROVE with modifications (describe below)
  [ ] DEFER - Wait for other work
  [ ] REJECT - Alternative approach preferred

NOTES:
  _________________________________________________________________
  _________________________________________________________________
```

---

## 🚀 Next Steps (Upon Approval)

1. **Create feature branch:** `git checkout -b feat/execution-config-refactor-001`
2. **Begin Phase 0:** Execute task_0_1 (verify markdown generation)
3. **Report progress:** Update status in `approval_status.approval_decision`
4. **Continue phases:** Sequential execution with checkpoints
5. **Daily standups:** Share progress metrics from Phase 5 dashboard
6. **Post-completion:** Archive plan, update CORTEX documentation

---

## 📚 Related Documentation

- **Master Orchestrator:** docs/02-orchestrators/01-master-orchestrator.md
- **DoRApprovalGate:** (Being replaced by this plan)
- **DatabaseBackedRegistry:** docs/03-infrastructure/database-registry.md
- **CORTEX Brain Tiers:** docs/01-cortex-brain/architecture.md
- **Feature Flags:** cortex/brain/core/feature_flags.py
- **Governance Rules:** cortex_brain/tier0/governance/core-rules.yaml

---

**Plan Status:** READY FOR EXECUTION  
**Last Updated:** 2026-01-26T14:45:00Z  
**Next Review:** Upon Phase 0 completion (within 2 hours of approval)
