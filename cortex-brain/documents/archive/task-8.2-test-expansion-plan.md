# Task 8.2 - Unit Test Expansion Plan
**Target:** Add 240 tests for 95% coverage  
**Current Coverage:** 14.45% (16,876/116,771 lines)  
**Target Coverage:** 95% (~110,833 lines covered)  
**Existing Tests:** 2,517 tests in 110 test files  
**Source Modules:** 1,256 Python files

---

## 📊 Current State Analysis

### Coverage Baseline
- **Total Lines:** 116,771
- **Covered Lines:** 16,876 (14.45%)
- **Gap:** 93,957 lines need coverage
- **Test Files:** 110 existing

### Critical Gaps (0% Coverage Modules)
1. **Tier 1 Brain** - entity_extractor, file_tracker, request_logger, tier1_api
2. **Collectors** - 11 collector modules (base, metrics, performance, etc.)
3. **Brain Transfer** - exporter, importer, cli, git_operations, plugin
4. **Core Modules** - context_injector, document_validator, git_automation
5. **Conversation Capture** - auto_detection, capture_manager, command_processor

---

## 🎯 Test Distribution Strategy (240 Tests)

### Phase 1: Critical Infrastructure (90 tests)
**Target Modules with 0% Coverage**

#### 1.1 Tier 1 Brain (25 tests) - PRIORITY 1
**Files:** `src/brain/tier1/`
- `entity_extractor.py` (8 tests)
  - Test entity extraction from conversation text
  - Test entity type classification (file, function, class, variable)
  - Test entity relationship building
  - Edge: malformed input, empty strings, special characters
  
- `file_tracker.py` (8 tests)
  - Test file modification tracking
  - Test file relationship discovery
  - Test workspace synchronization
  - Edge: missing files, permission errors, symlinks
  
- `request_logger.py` (5 tests)
  - Test request logging to database
  - Test log retrieval and filtering
  - Test log rotation
  - Edge: database unavailable, disk full
  
- `tier1_api.py` (4 tests)
  - Test API initialization
  - Test component integration
  - Test error handling
  - Edge: missing dependencies

#### 1.2 Collectors System (40 tests) - PRIORITY 1
**Files:** `src/collectors/`
- `base_collector.py` (5 tests)
  - Test abstract base class contract
  - Test collector lifecycle (init, collect, store)
  - Test error propagation
  
- `brain_metrics_collector.py` (8 tests)
  - Test metric collection (memory, queries, performance)
  - Test metric aggregation
  - Test metric storage
  - Edge: database errors, missing tables
  
- `conversation_collector.py` (6 tests)
  - Test conversation data extraction
  - Test turn counting and analysis
  - Test metadata collection
  
- `manager.py` (10 tests)
  - Test collector registration
  - Test parallel collection execution
  - Test error handling across collectors
  - Test result aggregation
  - Edge: collector timeout, partial failures
  
- `workspace_health_collector.py` (6 tests)
  - Test health check execution
  - Test health metrics calculation
  - Test alert generation
  
- Other collectors (5 tests)
  - brain_performance, response_template, token_usage

#### 1.3 Brain Transfer (25 tests) - PRIORITY 2
**Files:** `src/brain_transfer/`
- `brain_exporter.py` (8 tests)
  - Test brain state serialization
  - Test export to multiple formats (JSON, YAML)
  - Test incremental exports
  - Edge: large databases, corrupted data
  
- `brain_importer.py` (8 tests)
  - Test brain state restoration
  - Test import validation
  - Test merge strategies
  - Edge: version mismatches, corrupted imports
  
- `git_operations.py` (5 tests)
  - Test git checkpoint creation
  - Test commit message generation
  - Edge: untracked files, merge conflicts
  
- `cli.py` + `plugin.py` (4 tests)
  - Test CLI command parsing
  - Test plugin registration

---

### Phase 2: Core Systems Enhancement (70 tests)

#### 2.1 Core Modules (35 tests) - PRIORITY 1
**Files:** `src/core/`

- `context_management/context_injector.py` (8 tests)
  - Test context injection into prompts
  - Test context prioritization
  - Test token budget management
  - Edge: context overflow, conflicting priorities
  
- `document_validator.py` (6 tests)
  - Test document schema validation
  - Test YAML/JSON structure checks
  - Edge: malformed documents, missing required fields
  
- `git_automation.py` (6 tests)
  - Test automated git operations
  - Test commit history analysis
  - Edge: detached HEAD, merge conflicts
  
- `progress_tracker.py` (5 tests)
  - Test task progress tracking
  - Test milestone detection
  - Test progress persistence
  
- `response_tier_selector.py` (5 tests)
  - Test tier selection logic
  - Test complexity scoring
  - Test template matching
  
- `section_selector.py` (5 tests)
  - Test section filtering logic
  - Test priority-based selection

#### 2.2 Conversation Capture (15 tests) - PRIORITY 2
**Files:** `src/conversation_capture/`
- `auto_detection.py` (6 tests)
  - Test automatic conversation boundary detection
  - Test trigger pattern matching
  
- `capture_manager.py` (6 tests)
  - Test capture lifecycle
  - Test storage management
  
- `command_processor.py` (3 tests)
  - Test command parsing
  - Test command execution

#### 2.3 Orchestrator Enhancements (20 tests) - PRIORITY 1
**Enhance existing tests to reach 85%+**

- `maintenance_orchestrator_v3.py` (8 tests)
  - Test phase transitions
  - Test rollback mechanisms
  - Test health check integration
  
- `planning_orchestrator.py` (7 tests)
  - Test plan generation
  - Test phase execution
  - Test DoR/DoD validation
  
- `tdd_orchestrator.py` (5 tests)
  - Test RED→GREEN→REFACTOR cycle
  - Test test quality evaluation

---

### Phase 3: Agent & Intelligence (40 tests)

#### 3.1 Agents (25 tests) - PRIORITY 1
**Files:** `src/cortex_agents/`

- `strategic_planning_agent.py` (10 tests)
  - Test request analysis
  - Test complexity assessment
  - Test planning strategy selection
  - Test manifest generation
  - Edge: ambiguous requests, conflicting requirements
  
- `tactical_orchestration_agent.py` (10 tests)
  - Test orchestrator selection
  - Test execution coordination
  - Test phase management
  - Edge: orchestrator failures, timeouts
  
- `investigation_router.py` (5 tests)
  - Test route determination
  - Test agent delegation
  - Test fallback handling

#### 3.2 Intelligence Systems (15 tests) - PRIORITY 2
**Files:** `src/orchestrators/planning/intelligence/`

- `test_intelligence_adapter.py` (8 tests)
  - Test coverage analysis
  - Test gap detection
  - Test test generation recommendations
  
- Other intelligence modules (7 tests)

---

### Phase 4: Supporting Systems (40 tests)

#### 4.1 Caching System (15 tests) - PRIORITY 2
**Files:** `src/caching/`
- `cache_health.py` (8 tests)
  - Test cache health monitoring
  - Test cache invalidation
  - Test cache metrics
  
- Other caching modules (7 tests)

#### 4.2 Integration & Validation (15 tests) - PRIORITY 2
- Cross-module integration tests
- End-to-end workflow tests
- Performance regression tests

#### 4.3 Edge Cases & Error Handling (10 tests) - PRIORITY 3
- Boundary condition tests
- Error recovery tests
- Concurrent operation tests

---

## 🔬 Test Implementation Guidelines

### TDD Approach (RED→GREEN→REFACTOR)
1. **RED Phase:** Write failing test first
2. **GREEN Phase:** Implement minimal code to pass
3. **REFACTOR Phase:** Clean up while maintaining green tests

### Test Structure Template
```python
"""Tests for [module_name].

Test Coverage:
- Happy path: [scenarios]
- Edge cases: [scenarios]
- Error conditions: [scenarios]
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

class Test[ClassName][Feature]:
    """Tests for [specific feature]."""
    
    def test_[feature]_[scenario]_[expected_outcome](self):
        """Test that [feature] [scenario] results in [outcome]."""
        # Arrange
        # Act
        # Assert
        
    def test_[feature]_edge_case_[scenario](self):
        """Test edge case: [description]."""
        # Arrange edge condition
        # Act
        # Assert proper handling
```

### Coverage Targets by Module Type
- **Core Infrastructure:** 90%+ (collectors, tier1, agents)
- **Orchestrators:** 85%+ (complex workflows)
- **Utilities:** 80%+ (helper functions)
- **Supporting Systems:** 75%+ (caching, validation)

### Test Quality Standards
- ✅ Each test tests ONE concept
- ✅ Clear arrange-act-assert structure
- ✅ Descriptive test names (test_feature_scenario_outcome)
- ✅ Edge cases included (empty input, None, errors)
- ✅ Mocks used for external dependencies
- ✅ No test interdependencies
- ✅ Fast execution (<100ms per test)

---

## 📈 Execution Plan

### Week 1: Critical Infrastructure (90 tests)
**Days 1-2:** Tier 1 Brain (25 tests) → Coverage: 20%  
**Days 3-4:** Collectors System (40 tests) → Coverage: 35%  
**Day 5:** Brain Transfer (25 tests) → Coverage: 45%

### Week 2: Core Systems (70 tests)
**Days 1-2:** Core Modules (35 tests) → Coverage: 60%  
**Day 3:** Conversation Capture (15 tests) → Coverage: 65%  
**Days 4-5:** Orchestrator Enhancements (20 tests) → Coverage: 75%

### Week 3: Intelligence & Integration (80 tests)
**Days 1-2:** Agents (25 tests) → Coverage: 82%  
**Day 3:** Intelligence Systems (15 tests) → Coverage: 85%  
**Days 4-5:** Supporting Systems (40 tests) → Coverage: 95%+

---

## 🎯 Success Criteria

### Quantitative Metrics
- ✅ Total coverage ≥ 95%
- ✅ 240+ new tests added
- ✅ All tests passing (100% pass rate)
- ✅ Critical modules ≥ 90% coverage
- ✅ No modules < 75% coverage (except legacy)

### Qualitative Metrics
- ✅ All tests follow TDD approach
- ✅ Comprehensive edge case coverage
- ✅ Clear, maintainable test code
- ✅ Fast test execution (<5min total)
- ✅ Zero flaky tests

---

## 🔍 Coverage Validation Commands

```bash
# Full coverage report
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# Module-specific coverage
pytest tests/brain/tier1/ --cov=src/brain/tier1 --cov-report=term

# Coverage by file (lowest first)
pytest --cov=src --cov-report=json -q && \
  python3 -c "import json; data=json.load(open('coverage.json')); \
  files=[(v['summary']['percent_covered'], k) for k,v in data['files'].items()]; \
  files.sort(); print('\n'.join([f'{p:.1f}% - {f}' for p,f in files[:20]]))"

# Verify 95% target
pytest --cov=src --cov-report=term | grep "TOTAL"
```

---

## 📝 Documentation Updates

Upon completion, update:
1. `CHANGELOG.md` - Add Task 8.2 entry
2. `cortex-brain/documents/reports/task-8.2-completion-report.md` - Final metrics
3. `README.md` - Update test coverage badge (if present)
4. `tests/README.md` - Document new test structure

---

## ⚠️ Risk Mitigation

### Identified Risks
1. **Mock Complexity:** Some modules heavily depend on external systems
   - *Mitigation:* Use comprehensive fixtures in conftest.py
   
2. **Test Execution Time:** 240 new tests may slow CI
   - *Mitigation:* Parallel test execution, fast mocks
   
3. **Flaky Tests:** Database/file system tests can be unstable
   - *Mitigation:* Isolated test environments, proper cleanup
   
4. **Coverage Gaming:** Tests that don't verify behavior
   - *Mitigation:* Code review focus on assertion quality

---

**Next Step:** Begin Phase 1.1 - Tier 1 Brain tests (25 tests)
