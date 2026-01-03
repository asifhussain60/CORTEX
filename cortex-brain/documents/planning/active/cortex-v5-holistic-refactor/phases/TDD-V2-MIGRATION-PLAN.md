# 🧪 TDD Orchestrator v2 Migration Plan

**Feature:** Transform TDD Orchestrator from 📋 GUIDED to 🛡️ AUTONOMOUS  
**Plan ID:** tdd-v2-migration  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.5)  
**Created:** January 3, 2026  
**Duration:** 4 days  
**Status:** ⏳ IN PROGRESS - Day 1  

---

## 📊 Executive Summary

### Current State (v4.0)
- **Type:** 📋 GUIDED - Copilot reads manifest and executes instructions
- **Implementation:** 1,179 lines in `src/orchestrators/tdd/tdd_orchestrator.py`
- **Test Coverage:** 15 test files in `tests/orchestrators/tdd/`
- **Capabilities:** RED→GREEN→REFACTOR workflow with technology discovery
- **Invocation:** Manual interpretation by Copilot

### Target State (v2.0)
- **Type:** 🛡️ AUTONOMOUS - Python code executes independently via CLI bridge
- **Implementation:** Enhanced orchestrator + CLI bridge integration
- **Test Coverage:** Comprehensive test suite (100% core paths)
- **Capabilities:** Full autonomous TDD cycle with CLI invocation
- **Invocation:** `python3 scripts/cortex-cli.py tdd_orchestrator_v2 "<request>"`

### Migration Benefits
1. **Consistency:** Deterministic execution (no LLM interpretation variance)
2. **Speed:** 10x faster (Python vs Copilot reading + executing)
3. **Reliability:** 100% test coverage ensures quality
4. **Integration:** Seamless Master Orchestrator routing
5. **Token Efficiency:** Minimal prompt tokens (<100 for invocation)

---

## 🎯 Success Criteria

### Phase 6.5 Acceptance Criteria (from Master Plan)

**TDD-1:** CLI Bridge Integration
- [ ] `tdd_orchestrator_v2` command handler in `cortex-cli.py`
- [ ] Argument parsing for TDD-specific options (phase, test_path, feature)
- [ ] Response formatting for terminal output

**TDD-2:** Autonomous Execution Flow
- [ ] TDD orchestrator executes RED→GREEN→REFACTOR without Copilot interaction
- [ ] State persistence across phases
- [ ] Progress reporting via CLI output

**TDD-3:** Master Orchestrator Routing
- [ ] Pattern match: `start tdd`, `run tests`, `tdd [feature]`
- [ ] 🛡️ AUTONOMOUS designation in `master-orchestrator.yaml`
- [ ] CORTEX.prompt.md Intent Router updated

**TDD-4:** Test Suite Validation
- [ ] 100% coverage of CLI bridge integration
- [ ] End-to-end tests for autonomous execution
- [ ] Regression tests for existing v4.0 functionality

**TDD-5:** Documentation
- [ ] Migration guide for v4.0 → v2.0
- [ ] CLI usage examples
- [ ] Architecture diagrams showing CLI bridge flow

---

## 📋 Migration Roadmap (4 Days)

### Day 1: Foundation & RED Phase (8 hours)

**Task 1.1: Analysis & Planning (2h)** ✅ COMPLETE
- [x] Review TDD Orchestrator v4.0 implementation
- [x] Identify CLI bridge integration points
- [x] Create migration plan document
- [x] Define acceptance criteria

**Task 1.2: CLI Bridge Interface Design (2h)** ⏳ CURRENT
- [ ] Design `tdd_orchestrator_v2` command handler
- [ ] Define argument structure:
  - `user_request`: Natural language TDD request
  - `--option phase=<RED|GREEN|REFACTOR>`: Explicit phase
  - `--option test_path=<path>`: Specific test file
  - `--option feature=<name>`: Feature under test
- [ ] Document invocation patterns

**Task 1.3: RED Phase - Write Failing Tests (4h)**
- [ ] Test CLI bridge argument parsing
- [ ] Test TDD orchestrator invocation flow
- [ ] Test RED phase autonomous execution
- [ ] Test error handling and reporting

**Deliverables (Day 1):**
- [x] Migration plan document (this file)
- [ ] CLI bridge interface specification
- [ ] Failing test suite (RED phase complete)

---

### Day 2: GREEN Phase - Implementation (8 hours)

**Task 2.1: CLI Bridge Implementation (3h)**
- [ ] Add `tdd_orchestrator_v2` handler to `cortex-cli.py`
- [ ] Implement argument parser with TDD-specific options
- [ ] Add response formatter for TDD results
- [ ] Integrate with `invoke_orchestrator` tool

**Task 2.2: Autonomous Execution Engine (3h)**
- [ ] Enhance TDD orchestrator for CLI invocation
- [ ] Add state persistence for multi-phase execution
- [ ] Implement progress reporting
- [ ] Add rollback capability

**Task 2.3: Master Orchestrator Integration (2h)**
- [ ] Add TDD patterns to `master-orchestrator.yaml`
- [ ] Configure 🛡️ AUTONOMOUS routing
- [ ] Update CORTEX.prompt.md Intent Router
- [ ] Test pattern matching

**Deliverables (Day 2):**
- [ ] CLI bridge implementation (all tests passing)
- [ ] Enhanced TDD orchestrator
- [ ] Master Orchestrator configuration

---

### Day 3: REFACTOR Phase - Optimization (8 hours)

**Task 3.1: Code Quality Improvements (3h)**
- [ ] Refactor CLI bridge for maintainability
- [ ] Optimize TDD orchestrator performance
- [ ] Remove code duplication
- [ ] Enhance error messages

**Task 3.2: Test Suite Expansion (3h)**
- [ ] Add end-to-end autonomous execution tests
- [ ] Add edge case tests
- [ ] Add performance tests
- [ ] Achieve 100% coverage

**Task 3.3: Documentation (2h)**
- [ ] Write usage guide
- [ ] Create architecture diagrams
- [ ] Document CLI options
- [ ] Add troubleshooting section

**Deliverables (Day 3):**
- [ ] Refactored codebase (100% coverage)
- [ ] Comprehensive test suite
- [ ] Complete documentation

---

### Day 4: Validation & Deployment (8 hours)

**Task 4.1: Integration Testing (3h)**
- [ ] Test Master Orchestrator routing
- [ ] Test cross-session continuation
- [ ] Test state persistence
- [ ] Test error recovery

**Task 4.2: Performance Validation (2h)**
- [ ] Benchmark CLI bridge latency (<100ms)
- [ ] Benchmark TDD execution speed
- [ ] Validate memory usage
- [ ] Stress test with large codebases

**Task 4.3: Deployment & Rollout (3h)**
- [ ] Git checkpoint: `checkpoint-phase-6-5-tdd-v2-complete`
- [ ] Update CORTEX.prompt.md with TDD v2
- [ ] Create migration guide for users
- [ ] Announce v2 availability

**Deliverables (Day 4):**
- [ ] Production-ready TDD v2
- [ ] Git checkpoint
- [ ] Migration guide
- [ ] Deployment complete

---

## 🏗️ Architecture

### Current Architecture (v4.0 - GUIDED)

```
User: "start tdd for auth module"
  ↓
GitHub Copilot
  ↓ (reads manifest)
cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml
  ↓ (interprets instructions)
GitHub Copilot
  ↓ (executes steps manually)
RED → GREEN → REFACTOR
```

**Problems:**
- ❌ LLM interpretation variance
- ❌ Slow execution (Copilot reads + acts)
- ❌ No deterministic behavior
- ❌ High token cost

### Target Architecture (v2.0 - AUTONOMOUS)

```
User: "start tdd for auth module"
  ↓
GitHub Copilot (Intent Router)
  ↓ (detects TDD pattern)
Master Orchestrator
  ↓ (routes to 🛡️ AUTONOMOUS)
run_in_terminal tool
  ↓
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "auth module"
  ↓
CLI Bridge (cortex-cli.py)
  ↓
invoke_orchestrator(name="tdd_orchestrator_v2", request="auth module")
  ↓
TDD Orchestrator v2 (src/orchestrators/tdd/tdd_orchestrator.py)
  ↓ (executes autonomously)
RED → GREEN → REFACTOR
  ↓ (returns result)
CLI Bridge
  ↓ (formats output)
Terminal Output (visible to Copilot & user)
```

**Benefits:**
- ✅ Deterministic Python execution
- ✅ 10x faster (no LLM in loop)
- ✅ 100% test coverage
- ✅ <100 token invocation cost

---

## 🔧 Implementation Details

### CLI Bridge Interface

**Command Pattern:**
```bash
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "<user_request>" [--option key=value]
```

**Examples:**
```bash
# Full TDD cycle for feature
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "implement user authentication"

# Explicit phase execution
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "auth tests" --option phase=RED

# Specific test file
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "run auth tests" --option test_path=tests/auth/test_login.py

# Custom feature name
python3 scripts/cortex-cli.py tdd_orchestrator_v2 "tdd cycle" --option feature="User Login"
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `phase` | str | `"RED"` | Explicit phase: RED, GREEN, or REFACTOR |
| `test_path` | str | `"tests/"` | Path to test file or directory |
| `feature` | str | `""` | Feature name (extracted from request if empty) |
| `auto_refactor` | bool | `true` | Auto-run REFACTOR after GREEN |
| `coverage_threshold` | int | `80` | Minimum coverage % required |
| `strict_mode` | bool | `false` | Fail on any test quality issues |

**Response Format:**
```json
{
  "status": "success",
  "orchestrator": "tdd_orchestrator_v2",
  "phase": "GREEN",
  "summary": "Tests passing: 12/12 | Coverage: 85% | Refactorings: 3",
  "execution_time": 4.32,
  "artifacts": [
    "tests/auth/test_login.py",
    "src/auth/login.py",
    "cortex-brain/documents/reports/tdd-report-20260103-101500.md"
  ],
  "progress": {
    "phase": "GREEN",
    "tests_passing": 12,
    "tests_failing": 0,
    "coverage_percent": 85,
    "refactorings_applied": 3
  },
  "continuation_prompt": "All tests passing. Run REFACTOR phase? Say 'continue' or 'refactor now'."
}
```

### Master Orchestrator Routing

**Pattern Configuration (`cortex-brain/config/master-orchestrator.yaml`):**
```yaml
# TDD Orchestrator v2 - AUTONOMOUS
- pattern: "^(start tdd|run tests|tdd).*$"
  orchestrator: "tdd_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 30
  metadata:
    description: "TDD Mastery v2 (Autonomous RED→GREEN→REFACTOR)"
    autonomous: true
    cli_invocation: true
    response_template: "autonomous_execution_progress"
```

**Intent Router Update (`.github/prompts/CORTEX.prompt.md`):**
```markdown
| `start tdd`, `run tests`, `tdd [x]` | 🛡️ **TDD Mastery v2 (AUTONOMOUS)** | `tdd-orchestrator-v4-manifest.yaml` | **CLI INVOKE:** `python3 scripts/cortex-cli.py tdd_orchestrator_v2 "<request>"` |
```

---

## 🧪 Test Strategy

### Test Coverage Matrix

| Component | Test File | Coverage Target |
|-----------|-----------|-----------------|
| CLI Bridge Handler | `tests/orchestrators/tdd/test_cli_bridge_integration.py` | 100% |
| Autonomous Execution | `tests/orchestrators/tdd/test_autonomous_execution.py` | 100% |
| Phase State Persistence | `tests/orchestrators/tdd/test_state_persistence.py` | 100% |
| Master Orch Routing | `tests/orchestrators/test_master_orchestrator.py` | 100% |
| End-to-End Flow | `tests/orchestrators/tdd/test_tdd_v2_e2e.py` | 100% |
| Regression Suite | `tests/orchestrators/tdd/test_tdd_v2_regression.py` | 100% |

### Key Test Scenarios

**RED Phase Tests:**
1. CLI invocation with natural language request
2. Argument parsing for TDD-specific options
3. Test generation for feature
4. Test quality validation
5. Error handling (invalid requests, missing files)

**GREEN Phase Tests:**
1. Minimal implementation generation
2. Test execution and validation
3. Coverage threshold enforcement
4. Over-engineering detection
5. Rollback on failures

**REFACTOR Phase Tests:**
1. Code smell detection
2. Refactoring suggestions
3. Incremental refactoring with validation
4. Documentation updates
5. Knowledge graph pattern learning

**Integration Tests:**
1. Master Orchestrator routing to TDD v2
2. Cross-session state persistence
3. Continuation prompt handling
4. Multi-phase execution flow
5. Error recovery and rollback

---

## 📊 Progress Tracking

### Day 1 Progress (January 3, 2026)

**Completed:**
- ✅ Task 1.1: Analysis & Planning (2h)
  - Reviewed TDD Orchestrator v4.0 (1,179 lines)
  - Analyzed existing test suite (15 files)
  - Examined CLI bridge patterns (cortex-cli.py)
  - Created migration plan document

**In Progress:**
- ⏳ Task 1.2: CLI Bridge Interface Design (2h)
  - Defining argument structure
  - Documenting invocation patterns

**Next:**
- 📋 Task 1.3: RED Phase - Write Failing Tests (4h)
  - Test CLI bridge argument parsing
  - Test autonomous execution flow
  - Test error handling

**Blockers:** None

**Insights:**
1. **Existing v4.0 Quality:** TDD Orchestrator v4.0 is well-structured with 1,179 lines of clean, modular code
2. **Test Coverage:** Strong foundation with 15 existing test files
3. **CLI Bridge Pattern:** `cortex-cli.py` provides excellent template (291 lines, clean architecture)
4. **Technology Discovery:** Existing `TechnologyDiscoveryEngine` is powerful and can be reused
5. **Strategy Pattern:** Phase strategies (RED/GREEN/REFACTOR) are well-designed for autonomous execution

---

## 🔄 State Management

### Phase State Schema

```json
{
  "session_id": "tdd-session-20260103-101500",
  "orchestrator": "tdd_orchestrator_v2",
  "current_phase": "GREEN",
  "feature_name": "User Authentication",
  "workspace_root": "/path/to/project",
  "test_path": "tests/auth/test_login.py",
  "impl_path": "src/auth/login.py",
  "state": {
    "red_phase": {
      "status": "complete",
      "tests_generated": 12,
      "test_quality_score": 0.85,
      "timestamp": "2026-01-03T10:15:00Z"
    },
    "green_phase": {
      "status": "in_progress",
      "tests_passing": 8,
      "tests_failing": 4,
      "coverage_percent": 65,
      "timestamp": "2026-01-03T10:20:00Z"
    },
    "refactor_phase": {
      "status": "pending"
    }
  },
  "continuation_data": {
    "next_phase": "GREEN",
    "prompt": "4 tests still failing. Continue with GREEN phase implementation?"
  }
}
```

**Storage:** `cortex-brain/tier1/working-memory/orchestrator-sessions/tdd-session-<id>.json`

---

## 📝 Migration Checklist

### Day 1 ✅
- [x] **1.1:** Analysis & Planning (2h)
- [ ] **1.2:** CLI Bridge Interface Design (2h)
- [ ] **1.3:** RED Phase - Write Failing Tests (4h)

### Day 2
- [ ] **2.1:** CLI Bridge Implementation (3h)
- [ ] **2.2:** Autonomous Execution Engine (3h)
- [ ] **2.3:** Master Orchestrator Integration (2h)

### Day 3
- [ ] **3.1:** Code Quality Improvements (3h)
- [ ] **3.2:** Test Suite Expansion (3h)
- [ ] **3.3:** Documentation (2h)

### Day 4
- [ ] **4.1:** Integration Testing (3h)
- [ ] **4.2:** Performance Validation (2h)
- [ ] **4.3:** Deployment & Rollout (3h)

---

## 🎯 Definition of Done (Phase 6.5)

- [ ] **TDD-1:** CLI bridge integration complete (100% coverage)
- [ ] **TDD-2:** Autonomous execution validated (RED→GREEN→REFACTOR)
- [ ] **TDD-3:** Master Orchestrator routing configured and tested
- [ ] **TDD-4:** Test suite passing (100% coverage)
- [ ] **TDD-5:** Documentation complete (usage guide + architecture)
- [ ] **Performance:** CLI invocation <100ms
- [ ] **Reliability:** 0 failures in integration test suite
- [ ] **Git Checkpoint:** `checkpoint-phase-6-5-tdd-v2-complete`

---

## 📚 References

### Source Files
- **TDD Orchestrator v4.0:** `src/orchestrators/tdd/tdd_orchestrator.py` (1,179 lines)
- **CLI Bridge:** `scripts/cortex-cli.py` (291 lines)
- **Master Orchestrator:** `src/orchestrators/master/master_orchestrator.py`
- **Test Suite:** `tests/orchestrators/tdd/` (15 files)

### Configuration Files
- **Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Intent Router:** `.github/prompts/CORTEX.prompt.md`

### Related Plans
- **Master Plan:** `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md`
- **Phase 1.5:** CLI Bridge implementation (complete)
- **Phase 4.5:** Cross-Session Context Middleware (complete)

---

**Author:** CORTEX Planning System v5  
**Status:** ⏳ IN PROGRESS - Day 1  
**Last Updated:** January 3, 2026
