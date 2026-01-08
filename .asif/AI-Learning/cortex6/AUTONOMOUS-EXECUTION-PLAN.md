# CORTEX 6.0 - Autonomous Execution Plan
# feat04 Phase 2-3 Completion

## Task 2.2: Governance Merger-TODO Integration
**Goal:** Connect 4-category governance to TODO generation

### Implementation:
1. Add `connect_governance()` method to MasterOrchestrator
2. Create GovernanceMerger stub (references feat03 system)
3. Wire governance rules → TODO creation
4. Tests: governance_rules_drive_todos

### Files:
- `src/orchestrators/core/master_orchestrator.py` (enhance)
- `tests/unit/test_master_orchestrator_governance.py` (new)

### Estimated: 30 minutes

---

## Task 2.3: Unified Execution Pipeline
**Goal:** Integrate TODO + Governance + Master Orchestrator

### Implementation:
1. Create `execute_pipeline()` method in MasterOrchestrator
2. Flow: Request → Governance → TODO → Execution
3. End-to-end integration
4. Tests: full_pipeline_flow

### Files:
- `src/orchestrators/core/master_orchestrator.py` (enhance)
- `tests/integration/test_unified_pipeline.py` (new)

### Estimated: 45 minutes

---

## Task 3.1: Silent Execution Middleware
**Goal:** Suppress verbose output, show only essentials

### Implementation:
1. Create `SilentExecutionMiddleware` class
2. Output suppression logic
3. Essential-only mode
4. Tests: output_suppression

### Files:
- `src/orchestrators/middleware/silent_execution.py` (new)
- `tests/unit/test_silent_execution.py` (new)

### Estimated: 30 minutes

---

## Task 3.2: Progress Update Throttling  
**Goal:** Limit progress update frequency

### Implementation:
1. Create `ProgressThrottler` class
2. Time-based throttling (e.g., max 1 update per 5 seconds)
3. Backpressure handling
4. Tests: throttling_logic

### Files:
- `src/orchestrators/middleware/progress_throttler.py` (new)
- `tests/unit/test_progress_throttler.py` (new)

### Estimated: 20 minutes

---

## Task 3.3: Phase-Boundary-Only Updates
**Goal:** Updates only at phase start/end

### Implementation:
1. Create `PhaseBoundaryReporter` class
2. Detect phase boundaries
3. Suppress mid-phase updates
4. Tests: boundary_detection

### Files:
- `src/orchestrators/middleware/phase_boundary_reporter.py` (new)
- `tests/unit/test_phase_boundary_reporter.py` (new)

### Estimated: 25 minutes

---

## Total Estimated: 2.5 hours
## Target: Complete in 20-30 minutes (10x efficiency)

## Execution Strategy:
1. Simplified implementations (stubs where needed)
2. Core functionality only
3. Tests validate contracts
4. Full details deferred to later phases if needed
