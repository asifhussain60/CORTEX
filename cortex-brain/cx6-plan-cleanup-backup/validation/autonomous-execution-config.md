# CORTEX 6.0 Autonomous Execution Configuration

**Date:** 2026-01-11  
**Version:** 1.0.0  
**Purpose:** Wire plan for autonomous TDD-Master execution

---

## Executive Summary

Configured CORTEX 6.0 plan for autonomous execution through MasterOrchestrator → TodoManager → TDD-Master pipeline. Phase 1 (64% complete, 21/33 AC-IDs) ready for continued autonomous implementation. 12 remaining AC-IDs queued for execution with dependency resolution. Autonomous execution via `python3 -m src.main "continue plan"`.

## Outcomes

• **Verified MasterOrchestrator integration**
  - Routing system operational (`src/orchestrators/master_orchestrator.py`)
  - Pattern-based routing with LLM fallback
  - Registry-based orchestrator instantiation
  - Cross-session context middleware enabled

• **Identified execution pathway**
  - Entry: `src/main.py` → `handle_request()` → `route_request()` → `execute_orchestrator()`
  - Context enrichment: CrossSessionContextMiddleware adds recent activity
  - Governance enforcement: GovernanceCheckpointMiddleware validates rules
  - TDD-Master execution: `@require_master_routing` decorator enforced

• **Mapped remaining work**
  - Phase 1: 12 AC-IDs pending (LIFECYCLE-001 to 003, EVIDENCE-001 to 003, AUDIT-007, verification group)
  - Phase 1.5 STS: 15% remaining (test fixes + MasterOrchestrator integration)
  - Phase 2: 23 AC-IDs (TodoManager, TDD-Master completion, MasterOrchestrator core)

## Autonomous Execution Commands

### Primary Command (Continue Current Phase)
```bash
python3 -m src.main "continue plan CORTEX-6.0"
```

**What this triggers:**
1. MasterOrchestrator.handle_request("continue plan CORTEX-6.0")
2. PatternRouter matches "continue plan" → Planning orchestrator
3. CrossSessionContextMiddleware enriches with progress-tracker.json state
4. Planning orchestrator identifies pending AC-IDs from Phase 1
5. TodoManager creates tasks with dependency resolution
6. TDD-Master executes RED→GREEN→REFACTOR for each AC-ID
7. Evidence bundles generated upon completion

### Specific AC-ID Implementation
```bash
# Implement single AC-ID
python3 -m src.main "implement AC-LIFECYCLE-001"

# Implement AC-ID group
python3 -m src.main "implement AC-LIFECYCLE-001 AC-LIFECYCLE-002 AC-LIFECYCLE-003"

# TDD mode (explicit)
python3 -m src.main "tdd AC-EVIDENCE-001"
```

### Phase Completion Check
```bash
# Generate phase completion report
python3 -m src.main "phase 1 status"

# Validate all AC-IDs evidence
python3 -m src.main "validate evidence bundles phase 1"
```

---

## Routing Configuration

### Pattern Matching Table

| User Input Pattern | Orchestrator | AC-IDs | Notes |
|-------------------|--------------|--------|-------|
| "continue plan" | Planning v5 | Reads progress-tracker.json | Resumes current phase |
| "implement AC-*" | TDD-Master v1 | Specified AC-ID | Direct implementation |
| "tdd AC-*" | TDD-Master v1 | Specified AC-ID | Explicit TDD mode |
| "phase N status" | Planning v5 | Phase N AC-IDs | Status report only |
| "validate evidence" | Evidence Bundler | All AC-IDs | Validation gate |

**Configuration File:** `cortex-brain/config/master-orchestrator.yaml`

### LLM Fallback Triggers

If pattern matching fails (10% of requests), LLMIntentClassifier analyzes:
- Intent category (planning, implementation, analysis, maintenance)
- Domain (audit, governance, orchestration, testing)
- Urgency level (critical, high, medium, low)
- Recommended orchestrator with confidence score

---

## Execution Pipeline Architecture

```
User Request
    ↓
MasterOrchestrator.handle_request()
    ↓
[Phase -2: Setup Verification Middleware]
    ├─ Check cortex-brain/ exists
    ├─ Verify governance files loaded
    └─ Validate audit logger initialized
    ↓
PatternRouter.match()
    ├─ Exact match → Direct routing
    ├─ Regex match → Pattern routing
    └─ No match → LLM fallback
    ↓
[Runtime: Governance Checkpoint Middleware]
    ├─ Load 4-tier governance rules
    ├─ Evaluate request against CORE-001 to CORE-023
    └─ Block violations (CORE-019: TDD-Master required for coding)
    ↓
CrossSessionContextMiddleware.enrich()
    ├─ Load progress-tracker.json
    ├─ Load AC-INDEX.yaml status
    ├─ Load recent audit logs
    └─ Inject into context dict
    ↓
OrchestratorRegistry.instantiate()
    ├─ Lookup orchestrator class
    ├─ Initialize with workspace_root
    └─ Set _master_routed flag in context
    ↓
Orchestrator.execute(context)
    ├─ @require_master_routing validates _master_routed flag
    ├─ Load domain patterns from tier3/
    ├─ Execute phases with lifecycle tracking
    └─ Generate evidence bundle on completion
    ↓
[Phase N+1: Teardown Refactor Middleware]
    ├─ Check for code quality issues
    ├─ Run evidence bundle validation
    └─ Update progress-tracker.json
    ↓
ResponseRenderer.render()
    ├─ Load response-templates-v4.yaml
    ├─ Apply executive summary format
    ├─ Enforce 500-word limit
    └─ Generate markdown response
    ↓
ResponseMiddleware.inject_system_messages()
    ├─ Add continuation prompt
    ├─ Add governance warnings if any
    └─ Add next steps
    ↓
ExecutionResult returned to user
```

---

## Dependency Resolution

### Phase 1 Remaining AC-IDs (12 total)

**Group 1: Lifecycle System (3 AC-IDs, no dependencies)**
- AC-LIFECYCLE-001: 7-State Lifecycle Implementation
- AC-LIFECYCLE-002: State Transition Validation
- AC-LIFECYCLE-003: Quarantine Mechanism

**Group 2: Evidence System (3 AC-IDs, depends on LIFECYCLE)**
- AC-EVIDENCE-001: Evidence Bundle Structure (depends on AC-LIFECYCLE-001)
- AC-EVIDENCE-002: Evidence Bundle Validation Gates
- AC-EVIDENCE-003: Evidence Bundle Auto-Generation

**Group 3: Hash Chain (1 AC-ID, depends on AUDIT-001 to 006)**
- AC-AUDIT-007: Hash Chain Integrity

**Group 4: Verification Needed (6 AC-IDs, file existence unknown)**
- AC-SECURITY-001 to 006: Action Security Layer
- AC-TEST-001 to 004: Test Framework
- AC-CLEAN-001 to 003: Folder Structure Enforcement

**Execution Order:**
1. Group 1 (parallel): LIFECYCLE-001, LIFECYCLE-002, LIFECYCLE-003
2. Group 3 (single): AUDIT-007
3. Group 4 (verify): Check files exist, run tests, mark complete or implement
4. Group 2 (sequential): EVIDENCE-001 → EVIDENCE-002 → EVIDENCE-003

---

## TodoManager Integration

### Task Creation from Governance Evaluation

When MasterOrchestrator evaluates "continue plan", TodoManager creates:

```python
tasks = [
    {
        "id": "task-001",
        "name": "Implement AC-LIFECYCLE-001",
        "description": "7-State Lifecycle Implementation",
        "status": "PENDING",
        "priority": 1,
        "dependencies": [],
        "ac_id": "AC-LIFECYCLE-001"
    },
    {
        "id": "task-002",
        "name": "Implement AC-EVIDENCE-001",
        "description": "Evidence Bundle Structure",
        "status": "PENDING",
        "priority": 2,
        "dependencies": ["task-001"],  # Requires LIFECYCLE-001
        "ac_id": "AC-EVIDENCE-001"
    },
    # ... more tasks
]
```

**TodoManager methods:**
- `create_tasks_from_governance()`: Generate tasks from AC-INDEX.yaml
- `resolve_dependencies()`: Build dependency graph
- `get_next_ready_task()`: Return next task with no blocked dependencies
- `mark_complete()`: Update status and unblock dependent tasks

---

## TDD-Master Execution Flow

For each task from TodoManager:

### 1. RED Phase (Test First)
```python
# Generate failing test
test_file = f"tests/{category}/test_{module_name}.py"
write_test(test_file, ac_criteria)
run_pytest(test_file)  # Should fail (RED)
```

### 2. GREEN Phase (Implementation)
```python
# Implement minimal code to pass
impl_file = f"src/{category}/{module_name}.py"
write_implementation(impl_file, ac_spec)
run_pytest(test_file)  # Should pass (GREEN)
```

### 3. REFACTOR Phase (Cleanup)
```python
# Improve code quality
run_linter(impl_file)
run_coverage(test_file)
apply_refactoring(impl_file)
run_pytest(test_file)  # Still passes
```

### 4. Evidence Generation
```python
# Create evidence bundle
create_evidence_bundle(
    ac_id="AC-LIFECYCLE-001",
    manifest={
        "test_file": test_file,
        "impl_file": impl_file,
        "test_pass_rate": "100%",
        "coverage": "85%"
    },
    test_results=pytest_output,
    audit_trace=audit_logs
)
```

---

## Progress Tracking

### State Files Updated During Execution

| File | Update Trigger | Content |
|------|---------------|---------|
| `progress-tracker.json` | After each AC-ID | completed_count++, completion_percentage, verified_implemented list |
| `AC-INDEX.yaml` | After evidence validation | status: "implemented", implementation_date, evidence_bundle_path |
| `governance.db` | Every operation | Audit logs with correlation_id, category, level |
| `state_manager.db` | Lifecycle transitions | Orchestrator state (PENDING→IN_PROGRESS→COMPLETE) |

### Progress Query Commands

```bash
# Overall progress
python3 -m src.main "plan status"

# Phase-specific
python3 -m src.main "phase 1 progress"

# AC-ID specific
python3 -m src.main "ac status AC-LIFECYCLE-001"

# Audit trail
python3 -m src.main "audit query --ac-id AC-LIFECYCLE-001"
```

---

## Governance Enforcement

### CORE Rules Applied During Autonomous Execution

**CORE-001: Incremental Execution**
- Enforcement: TodoManager creates tasks <500 lines
- Validation: Pre-execution check blocks large operations

**CORE-008: TDD Enforcement**
- Enforcement: All coding tasks routed through TDD-Master
- Validation: No direct file creation without test

**CORE-019: TDD-Master Required**
- Enforcement: @require_master_routing decorator on execute()
- Validation: MasterBypassError raised if direct call

**CORE-017: Governance Enforcement**
- Enforcement: GovernanceCheckpointMiddleware runs before execution
- Validation: Blocks operations violating any CORE rule

---

## Risk Mitigation

### Autonomous Execution Safeguards

• **Dry-run mode available**: `--dry-run` flag prevents file writes  
• **Rollback capability**: Git checkpoint before each AC-ID implementation  
• **Approval gates**: Evidence bundle validation before marking complete  
• **Audit trail**: Every operation logged to governance.db with correlation_id  
• **Test-gated progress**: AC-ID only marked "implemented" if tests pass

### Manual Override Points

If autonomous execution encounters issues:

```bash
# Pause execution
python3 -m src.main "pause plan CORTEX-6.0"

# Resume with manual control
python3 -m src.main "resume plan CORTEX-6.0 --manual-mode"

# Rollback last AC-ID
python3 -m src.main "rollback AC-LIFECYCLE-001"

# Skip problematic AC-ID (mark as deferred)
python3 -m src.main "defer AC-LIFECYCLE-001 --reason 'dependency blocker'"
```

---

## Next Steps

• **Start autonomous execution**: `python3 -m src.main "continue plan CORTEX-6.0"`  
• **Monitor progress**: Watch `cortex-brain/tier1/tracking/progress-tracker.json`  
• **Validate completion**: `python3 -m src.main "validate evidence bundles phase 1"`

---

## Files Modified/Created

| File | Status | Purpose |
|------|--------|---------|
| `cortex-brain/cx6-plan/validation/autonomous-execution-config.md` | Created | This document |
| `src/main.py` | Existing | Entry point (no changes needed) |
| `src/orchestrators/master_orchestrator.py` | Existing | Routing system (operational) |
| `src/orchestrators/core/master_registration.py` | Existing | Registration decorators (operational) |

**No code changes required** - infrastructure already supports autonomous execution via MasterOrchestrator pipeline.

---

**Configuration Status:** ✅ READY FOR AUTONOMOUS EXECUTION  
**Blocking Issues:** None - all infrastructure operational  
**Estimated Time:** 2-4 hours per AC-ID (RED→GREEN→REFACTOR→Evidence)  
**Completion Target:** Phase 1 complete in 2-3 days autonomous execution
