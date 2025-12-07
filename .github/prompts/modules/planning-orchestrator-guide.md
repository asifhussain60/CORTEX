# Planning Orchestrator Guide

**Version:** 2.0 | **Updated:** December 6, 2025

---

## Overview

The Planning Orchestrator provides comprehensive feature planning with:
- Interactive plan creation with Vision API support
- Definition of Ready (DoR) and Definition of Done (DoD) validation
- File-based persistence for cross-chat resumption
- Autonomous execution with progress tracking
- Automatic TDD requirement injection
- Git checkpoint integration

---

## Commands

### Plan Creation
- `plan [feature]` - Start interactive planning
- `create a plan` - Alternative planning trigger
- `make a plan` - Alternative planning trigger
- `plan ado` - Create ADO work items from plan

### Plan Management
- `approve plan` - Approve completed plan
- `complete plan [plan_id]` - Mark plan as completed
- `execute all phases autonomously` - Run plan end-to-end without manual approval
- `execute autonomously` - Synonym for autonomous execution
- `auto chained` - Synonym for autonomous execution

---

## Autonomous Execution

**NEW in v2.0:** Plans can now be executed autonomously from start to finish.

### How It Works

1. **Load Approved Plan**
   - Plan must be in `cortex-brain/documents/planning/approved/`
   - Status must be "approved"

2. **Phase-by-Phase Execution**
   - Executes all tasks in Phase 1
   - Creates git checkpoint
   - Executes all tasks in Phase 2
   - Creates git checkpoint
   - Continues until all phases complete

3. **Progress Tracking**
   - Visual progress bar updates in real-time
   - Shows current phase, task, and completion percentage
   - Estimated time remaining displayed

4. **TDD Enforcement**
   - RED→GREEN→REFACTOR workflow mandatory
   - Tests must fail before implementation
   - Git checkpoints at phase boundaries

5. **Automatic Completion**
   - Plan marked as completed
   - Moved to `cortex-brain/documents/planning/completed/`
   - Documentation reminder generated

### Usage

```
User: execute all phases autonomously
CORTEX: [Loads approved plan, executes all phases with progress updates]

Progress: [████████░░] 80% - Phase 3 of 4 Complete
⏱️  Estimated Time Remaining: 8 hours
📋 Current Task: 3.2 - Implement template renderer
✅ Completed: 11/14 tasks
```

### Execution Log

Each autonomous execution generates a detailed log:
- Phase completion timestamps
- Task execution status
- Git checkpoint success/failure
- Error details (if any)

---

## TDD Requirements

**ENHANCED in v3.8.1:** New validation rules ensure comprehensive test coverage.

All plans automatically include 6 DoR + 6 DoD TDD requirements:

**Definition of Ready:**
1. TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)
2. Tests MUST fail before implementation (RED phase validation)
3. Git checkpoints required at RED, GREEN, REFACTOR phases
4. Test coverage targets defined for all new code
5. **NEW:** Test files MUST exist for all production code (per-layer validation)
6. **NEW:** No empty/placeholder tests allowed (quality validation)

**Definition of Done:**
1. All code follows TDD workflow with git checkpoints
2. Git history shows test-first commits (RED phase before GREEN phase)
3. All tests pass with minimum coverage thresholds met
4. No test skips or ignores without documented justification
5. **NEW:** Per-layer coverage thresholds met (Domain: 90%, Application: 85%, Infrastructure: 70%, API: 80%)
6. **NEW:** No empty placeholder tests (UnitTest1, Test1, etc.) in codebase

**Cannot Be Bypassed:** TDD requirements injected automatically before validation.

### Coverage Validation (NEW)

The planning system now validates test coverage using two Tier 0 instincts:

**TDD_TEST_FILE_VALIDATION (Severity: BLOCKED)**
- Scans production code by architectural layer
- Validates corresponding test files exist
- Enforces minimum coverage per layer:
  - Domain: 90% minimum
  - Application: 85% minimum
  - Infrastructure: 70% minimum
  - API: 80% minimum
- Blocks commit/deployment if thresholds not met

**TDD_EMPTY_TEST_DETECTION (Severity: WARNING)**
- Detects empty test methods
- Identifies placeholder test names (Test1, UnitTest1)
- Flags meaningless assertions (Assert.True(true))
- Warns about tests with zero assertions
- Provides cleanup guidance

### Validation During Execution

Autonomous execution now includes test validation at each phase:

**After RED Phase:**
- Validates test file created in correct location
- Scans for empty/placeholder patterns
- Ensures test actually fails

**After GREEN Phase:**
- Validates coverage increase per layer
- Checks minimum test count per production file
- Verifies test file completeness

**After REFACTOR Phase:**
- Validates test file completeness across all layers
- Scans for and reports empty/placeholder tests
- Ensures tests still pass after cleanup

**Example Validation Output:**
```
Phase 2 Complete - Running TDD Validation...
✅ Domain Layer: 92% coverage (threshold: 90%)
✅ Application Layer: 87% coverage (threshold: 85%)
❌ Infrastructure Layer: 65% coverage (threshold: 70%)
⚠️  Warning: 2 placeholder tests detected in Tests/UnitTest1.cs

⏸️  Execution Paused - Infrastructure coverage below threshold
Required: Add TaskRepositoryTests.cs (3 tests minimum)
```

---

## Documentation Reminders

Plans automatically generate documentation reminders at key points:

**Plan Approval:**
- Location: `cortex-brain/documents/learning/planning_strategies/`
- Captures: Requirements, scope, approach, decisions

**Plan Completion:**
- Location: `cortex-brain/documents/learning/milestones/`
- Captures: Key learnings, decisions, outcomes

**ADO Work Item Completion:**
- Location: `cortex-brain/documents/learning/ado_workflows/`
- Captures: Implementation details, technical decisions

All documentation accessible via `load dashboard` command.

---

## Progress Monitoring

Autonomous execution uses the progress monitoring system:

**Features:**
- Auto-activation for operations >5 seconds
- Real-time progress bar updates
- ETA calculation based on task velocity
- Hang detection (alerts if no progress for 30 seconds)
- Thread-safe with <0.1% overhead

**Visual Format:**
```
Progress: [████████░░] 80%
Phase 3 of 4 Complete
⏱️  Estimated Time Remaining: 8 hours
📋 Current: Task 3.2 - Implement template renderer
✅ Completed: 11/14 tasks
```

---

## File Structure

```
cortex-brain/documents/planning/
├── active/           # Plans being created
├── approved/         # Plans ready for execution
├── completed/        # Finished plans
└── archived/         # Historical plans
```

**Plan Format:** YAML (`.yaml` extension)

**Naming Convention:** `PLAN-YYYY-MM-DD-{feature-name}.yaml`

---

## Cross-Chat Resumption

Plans persist across chat sessions:

1. Create plan in Chat A
2. Open new Chat B
3. Reference plan: "Continue plan PLAN-2025-12-06-auto-doc-gen"
4. CORTEX loads plan and resumes

---

## Vision API Integration

Plans support screenshot extraction:

1. Attach screenshot to planning request
2. Vision API extracts text/requirements
3. Planner incorporates extracted data into plan

---

## Error Handling

**Invalid Plan:**
- Validation errors displayed with specific line numbers
- Plan not saved until all errors resolved

**Execution Failure:**
- Execution log captures error details
- Phase and task where failure occurred
- Plan remains in "approved" status for retry

**Git Checkpoint Failure:**
- Warning logged, execution continues
- Execution log notes checkpoint failure
- Does not stop autonomous execution

---

## Best Practices

1. **Review before approving** - Plans locked after approval
2. **Use autonomous execution for small-medium plans** - Large plans (>40 hours) may need manual intervention
3. **Check execution logs** - Review for errors after autonomous execution
4. **Document learnings** - Follow documentation reminders after completion
5. **Use git checkpoints** - Phase boundaries create recovery points

---

## Related Guides

- TDD Mastery Guide: `.github/prompts/modules/tdd-mastery-guide.md`
- Progress Monitoring: `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`
- Git Checkpoints: `cortex-brain/git-checkpoint-rules.yaml`

---

**Quick Start:** Say "plan [feature name]" to begin interactive planning.
