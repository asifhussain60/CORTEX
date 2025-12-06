# Comprehensive Integration Test Suite Plan

**Version:** 1.0  
**Created:** December 6, 2025  
**Author:** Asif Hussain  
**Status:** 📋 PLANNING

---

## 🎯 Executive Summary

**Goal:** Create self-validating CORTEX architecture with comprehensive integration tests across 11 categories, automated test discovery/generation, and align orchestrator integration for continuous validation.

**Key Innovation:** CORTEX validates its own integrity by discovering new components, generating appropriate tests, and executing them during `align` operations - creating a self-improving test suite that leverages Tier 2 learning patterns.

---

## 📐 Architecture Overview

### Test Pyramid Structure

```
tests/
├── unit/                          # ✅ EXISTING (147 tests, 100% passing)
│   └── orchestrators/            # Component isolation tests
│
├── integration/                   # 🆕 NEW - Cross-component validation
│   ├── orchestrators/            # Workflow coordination
│   ├── agents/                   # Agent interactions
│   ├── brain_tiers/              # Tier 0-3 integration
│   ├── workflows/                # Document org, planning flows
│   ├── response_templates/       # Template selection/rendering
│   ├── utilities/                # Progress, file ops, git
│   ├── validation/               # Validator integration
│   ├── sessions/                 # Session model flows
│   ├── config/                   # Configuration loading
│   ├── api_integrations/         # External API tests
│   ├── learning/                 # 🆕 Learning library integration
│   └── e2e/                      # End-to-end scenarios
│
├── test_manifest.yaml            # 🆕 Component coverage tracking
└── conftest.py                   # Shared fixtures
```

### 11 Integration Test Categories

| # | Category | Components | Priority | Estimated Tests |
|---|----------|------------|----------|-----------------|
| 1 | **Orchestrators** | Planning, TDD, Execution, Git Checkpoint | 🔴 Critical | 15-20 |
| 2 | **Agents** | 10 specialist agents (intent router, planner, etc.) | 🔴 Critical | 20-25 |
| 3 | **Brain Tiers** | Tier 0-3 (governance, memory, knowledge, context) | 🔴 Critical | 25-30 |
| 4 | **Workflows** | Document org, incremental planning, streaming | 🟡 High | 10-15 |
| 5 | **Response Templates** | 62 templates (selection, rendering) | 🟡 High | 10-12 |
| 6 | **Utilities** | Progress monitoring, file ops, git | 🟡 High | 8-10 |
| 7 | **Validation Framework** | Plan/task/TDD/code quality | 🟢 Medium | 8-10 |
| 8 | **Session Management** | TDD/Planning/Execution sessions | 🟢 Medium | 6-8 |
| 9 | **Configuration** | Config loading, environment detection | 🟢 Medium | 5-6 |
| 10 | **API Integrations** | GitHub API, Azure DevOps API | 🟢 Medium | 4-6 |
| 11 | **Learning Library** | Event system, pattern learning, bug capture | 🔴 Critical | 15-20 |

**Total Estimated:** 126-162 integration tests

---

## 🆕 Learning Library Integration (Category 11)

### Learning Library Components (from pull)

**Event Infrastructure:**
- `LearningEvent` - Structured learning event capture
- `PatternLearnedEvent` - Domain event for pattern discovery
- `LearningCaptureAgent` - Automatic lesson capture from operations/errors/commits
- `Tier2LearningIntegration` - Adaptive behavior based on user feedback

**Pattern Learning:**
- `BugDrivenLearner` - Learn from bug patterns (8 categories, 4 severity levels)
- `DocumentationPattern` - Template/content/structure patterns
- `LearningSession` - Track patterns learned from correlations

**Integration Points:**
- Ambient daemon events monitoring
- Git commit learning
- Exception pattern extraction
- SKULL violation capture
- Operation success/failure tracking

### Integration Test Requirements for Learning

1. **Event Capture Tests** (5 tests)
   - Test LearningEvent creation from operation results
   - Test exception parsing for learning patterns
   - Test ambient event analysis
   - Test git commit learning
   - Test SKULL violation capture

2. **Pattern Learning Tests** (6 tests)
   - Test bug pattern extraction (8 categories)
   - Test documentation pattern learning
   - Test learning session tracking
   - Test pattern confidence scoring
   - Test pattern deduplication
   - Test cross-conversation pattern matching

3. **Tier 2 Integration Tests** (4 tests)
   - Test pattern storage in knowledge graph
   - Test PatternLearnedEvent propagation
   - Test adaptive threshold learning
   - Test user feedback incorporation

4. **End-to-End Learning Flow** (5 tests)
   - Test operation → failure → learning → prevention cycle
   - Test commit → pattern extraction → knowledge graph update
   - Test exception → lesson learned → similar detection
   - Test user feedback → threshold adjustment → behavior change
   - Test multi-source learning aggregation

**Total Learning Tests:** 20 tests

---

## 🔍 Component Discovery Engine

### Discovery Strategy

**1. Static Analysis (AST Parsing)**
```python
# Discover components via AST
- Classes with @dataclass, BaseAgent, BaseOrchestrator
- Functions with @with_progress decorator
- Validation functions (validate_*)
- Event classes (*Event)
```

**2. Signature Analysis**
```python
# Extract component contracts
- Input parameters (type hints)
- Return types
- Docstring contracts
- Dependency injection points
```

**3. Integration Point Detection**
```python
# Identify cross-component dependencies
- Import relationships
- Event emissions/handlers
- Database interactions (Tier 1-3)
- External API calls
```

**4. Learning-Enhanced Discovery**
```python
# Leverage Tier 2 knowledge graph
- Identify frequently modified components (high-risk)
- Detect error-prone integration points
- Prioritize untested critical paths
- Learn from past integration failures
```

### Discovery Output (test_manifest.yaml)

```yaml
version: "1.0"
last_discovery: "2025-12-06T12:00:00Z"
total_components: 247
tested_components: 189
untested_components: 58
coverage_percentage: 76.5

categories:
  orchestrators:
    discovered: 12
    tested: 10
    untested: 2
    components:
      - name: "PlanningOrchestrator"
        path: "src/orchestrators/planning_orchestrator.py"
        integration_points:
          - "PlanExecutionOrchestrator"
          - "GitCheckpointOrchestrator"
          - "ValidationFramework"
        test_file: "tests/integration/orchestrators/test_planning_integration.py"
        status: "tested"
        last_test_run: "2025-12-06T11:30:00Z"
        coverage: 85.3

      - name: "TDDImplementationOrchestrator"
        path: "src/orchestrators/tdd_implementation_orchestrator.py"
        integration_points:
          - "GitCheckpointOrchestrator"
          - "TDDSession"
          - "ValidationFramework"
          - "LearningCaptureAgent"  # NEW - learning integration
        test_file: "tests/integration/orchestrators/test_tdd_integration.py"
        status: "tested"
        coverage: 78.2

  learning:  # NEW CATEGORY
    discovered: 8
    tested: 0
    untested: 8
    components:
      - name: "LearningCaptureAgent"
        path: "src/cortex_agents/learning_capture_agent.py"
        integration_points:
          - "LessonsLearned"
          - "Tier2KnowledgeGraph"
          - "GitOperations"
        test_file: "tests/integration/learning/test_learning_capture.py"
        status: "untested"
        risk_score: 0.85  # High risk - critical for self-improvement

      - name: "BugDrivenLearner"
        path: "src/cortex_agents/test_generator/bug_driven_learner.py"
        integration_points:
          - "TestGenerator"
          - "PatternStorage"
        test_file: "tests/integration/learning/test_bug_driven_learning.py"
        status: "untested"
        risk_score: 0.72

risk_analysis:
  high_risk_untested: 12  # Components frequently modified with no integration tests
  critical_paths_uncovered: 3  # End-to-end flows without tests
  learning_gaps: 8  # Learning components without tests
```

---

## 🤖 Test Generation Engine

### Generation Strategy

**1. Template-Based Generation**
```python
# Generate test from component signature
template = get_test_template(component_type)
test_code = template.render(
    component_name=component.name,
    integration_points=component.integration_points,
    input_types=component.input_types,
    return_type=component.return_type
)
```

**2. Learning-Enhanced Generation**
```python
# Use Tier 2 patterns for smarter tests
patterns = tier2.query_patterns(
    component=component.name,
    pattern_type="integration_failure"
)
test_code += generate_regression_tests(patterns)
```

**3. Contract-Based Generation**
```python
# Extract contracts from docstrings
contracts = parse_docstring_contracts(component.docstring)
test_code += generate_contract_tests(contracts)
```

### Test Templates (11 categories)

**Orchestrator Integration Template:**
```python
def test_{orchestrator_name}_workflow_integration(temp_project):
    """Test {orchestrator_name} integration with dependencies."""
    # Setup
    {orchestrator_name_lower} = {orchestrator_name}(project_root=temp_project)
    
    # Test integration points
    {% for dep in integration_points %}
    # Test integration with {dep}
    result = {orchestrator_name_lower}.execute_with_{dep_lower}()
    assert result["success"] is True
    assert {dep_lower}_called is True
    {% endfor %}
    
    # Verify state consistency
    assert {orchestrator_name_lower}.state_valid()
```

**Learning Integration Template:**
```python
def test_learning_capture_from_{source}(temp_project):
    """Test learning capture from {source} events."""
    agent = LearningCaptureAgent(project_root=temp_project)
    
    # Trigger {source} event
    event = create_test_{source}_event()
    
    # Capture learning
    learning_event = agent.capture_from_{source}(event)
    
    assert learning_event is not None
    assert learning_event.event_type == "{source}"
    assert learning_event.confidence > 0.7
    
    # Verify Tier 2 storage
    tier2 = KnowledgeGraph()
    pattern = tier2.query_pattern(learning_event.pattern_id)
    assert pattern is not None
```

**Brain Tier Integration Template:**
```python
def test_tier{tier_number}_{operation}_integration(temp_brain):
    """Test Tier {tier_number} {operation} with dependent tiers."""
    tier{tier_number} = Tier{tier_number}(brain_path=temp_brain)
    
    # Test cross-tier operation
    data = {"test": "data"}
    tier{tier_number}.{operation}(data)
    
    # Verify tier dependencies
    {% if tier_number > 0 %}
    # Check Tier {tier_number - 1} interaction
    tier{tier_number - 1}_data = tier{tier_number - 1}.get_data()
    assert tier{tier_number}_data in tier{tier_number - 1}_data
    {% endif %}
    
    # Verify isolation (no upward dependencies)
    {% if tier_number < 3 %}
    # Tier {tier_number} should not directly access Tier {tier_number + 1}
    assert not tier{tier_number}.has_direct_tier{tier_number + 1}_access()
    {% endif %}
```

---

## 🔄 Align Orchestrator Enhancement

### New Align Workflow (with Test Discovery)

```
Phase 1: System Health Check (existing)
├── Check brain databases
├── Validate configuration
└── Check dependencies

Phase 2: Component Discovery (NEW)
├── Scan src/ for new components (AST parsing)
├── Extract component signatures
├── Identify integration points
├── Query Tier 2 for high-risk components
└── Update test_manifest.yaml

Phase 3: Test Coverage Analysis (NEW)
├── Load test_manifest.yaml
├── Calculate coverage by category
├── Identify untested components
├── Prioritize by risk score (Tier 2 patterns)
└── Generate coverage report

Phase 4: Test Generation (NEW)
├── For each untested component:
│   ├── Select appropriate template
│   ├── Generate test code
│   ├── Apply learning patterns (Tier 2)
│   └── Save to tests/integration/
└── Update test_manifest.yaml

Phase 5: Integration Test Execution (NEW)
├── Run pytest tests/integration/ --tb=short
├── Collect results by category
├── Identify breaking changes
├── Update Tier 2 with failure patterns
└── Generate test report

Phase 6: Validation Report (enhanced)
├── System health (existing)
├── Test coverage metrics (NEW)
│   ├── Category coverage
│   ├── Untested high-risk components
│   ├── Integration test pass rate
│   └── Coverage delta from last run
├── Breaking change detection (NEW)
└── Recommendations (enhanced with test data)
```

### Align Command Enhancement

```bash
# Standard align (user repos)
cortex align

# Admin align with full test discovery (CORTEX repo)
cortex align --full

# Align with test generation only (no execution)
cortex align --discover-only

# Align with integration tests only (skip discovery)
cortex align --test-only

# Align with verbose test output
cortex align --verbose-tests
```

### Test Report Output

```
╔══════════════════════════════════════════════════════════════╗
║              CORTEX INTEGRATION TEST REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

📊 Test Coverage Summary
├── Total Components: 247
├── Tested: 189 (76.5%)
├── Untested: 58 (23.5%)
└── Delta: +12 tested since last run

🎯 Category Breakdown
┌─────────────────────┬─────────┬────────┬───────────┬──────────┐
│ Category            │ Total   │ Tested │ Untested  │ Coverage │
├─────────────────────┼─────────┼────────┼───────────┼──────────┤
│ Orchestrators       │ 12      │ 10     │ 2         │ 83.3%    │
│ Agents              │ 10      │ 8      │ 2         │ 80.0%    │
│ Brain Tiers         │ 45      │ 38     │ 7         │ 84.4%    │
│ Workflows           │ 15      │ 12     │ 3         │ 80.0%    │
│ Response Templates  │ 62      │ 52     │ 10        │ 83.9%    │
│ Utilities           │ 18      │ 15     │ 3         │ 83.3%    │
│ Validation          │ 12      │ 10     │ 2         │ 83.3%    │
│ Sessions            │ 8       │ 7      │ 1         │ 87.5%    │
│ Configuration       │ 6       │ 5      │ 1         │ 83.3%    │
│ API Integrations    │ 4       │ 3      │ 1         │ 75.0%    │
│ Learning Library    │ 8       │ 0      │ 8         │ 0.0%     │  ⚠️
└─────────────────────┴─────────┴────────┴───────────┴──────────┘

⚠️  High-Risk Untested Components (12)
├── LearningCaptureAgent (risk: 0.85) - critical for self-improvement
├── BugDrivenLearner (risk: 0.72) - test generation dependency
├── PlanExecutionOrchestrator.auto_chain (risk: 0.68) - recent changes
└── ... (9 more)

✅ Integration Test Results
├── Total Tests: 156
├── Passed: 152 (97.4%)
├── Failed: 4 (2.6%)
├── Skipped: 0
└── Duration: 45.3s

❌ Breaking Changes Detected (4)
├── test_tdd_orchestrator_learning_integration
│   └── Error: LearningCaptureAgent not initialized
├── test_planning_execution_chain
│   └── Error: PlanningSession.metadata missing 'learning_events'
└── ... (2 more)

🔍 Recommendations
1. CRITICAL: Test learning library components (0% coverage)
2. HIGH: Fix 4 breaking changes in learning integration
3. MEDIUM: Generate tests for 12 high-risk untested components
4. LOW: Improve coverage for API integrations (75% → 85%)

📈 Learning Insights (from Tier 2)
├── Components with >3 failures in last 30 days: 5
├── Most frequent integration failure: TDD → GitCheckpoint (12 times)
└── Suggested test priority: GitCheckpointOrchestrator rollback scenarios
```

---

## 📅 Implementation Phases

### Phase 1: Foundation (Week 1)
**Duration:** 8-10 hours

**Tasks:**
1. Create integration test directory structure (11 categories)
2. Build component discovery engine (AST parsing)
3. Create test_manifest.yaml schema
4. Implement basic test generation templates (3 categories)
5. Write 10-15 example integration tests manually

**Deliverables:**
- `tests/integration/` structure
- `src/test_discovery/component_discovery.py`
- `test_manifest.yaml` with schema
- 3 test templates (orchestrators, agents, brain tiers)
- 15 working integration tests

**Success Criteria:**
- Discovery engine finds 80%+ of components
- test_manifest.yaml accurately tracks 3 categories
- All 15 tests pass

### Phase 2: Test Generation (Week 2)
**Duration:** 10-12 hours

**Tasks:**
1. Implement remaining test templates (8 categories)
2. Add learning-enhanced generation (Tier 2 patterns)
3. Build test generation engine
4. Generate tests for untested components
5. Create shared test fixtures (conftest.py)

**Deliverables:**
- 11 test templates (all categories)
- `src/test_discovery/test_generator.py`
- 50-70 auto-generated integration tests
- Comprehensive conftest.py with fixtures

**Success Criteria:**
- Generator creates valid tests for 90%+ components
- Generated tests have 80%+ pass rate
- Coverage reaches 65%+ across all categories

### Phase 3: Align Integration (Week 3)
**Duration:** 6-8 hours

**Tasks:**
1. Enhance align orchestrator with discovery phase
2. Add test coverage analysis
3. Implement test execution integration
4. Create test report generator
5. Add learning library integration tests

**Deliverables:**
- Enhanced `src/operations/modules/admin/align_utility.py`
- Test report generator
- 20 learning library integration tests
- Updated align command with --discover-only, --test-only flags

**Success Criteria:**
- Align discovers all new components
- Test report provides actionable insights
- Learning library tests cover all 4 sub-areas

### Phase 4: Learning Enhancement (Week 4)
**Duration:** 8-10 hours

**Tasks:**
1. Integrate Tier 2 risk scoring
2. Implement failure pattern learning
3. Add adaptive test prioritization
4. Create test quality feedback loop
5. Document test generation patterns

**Deliverables:**
- Risk scoring algorithm (Tier 2 integration)
- Failure pattern database
- Adaptive prioritization engine
- Test quality metrics
- Documentation in `cortex-brain/documents/implementation-guides/`

**Success Criteria:**
- Risk scores correlate with actual failures (70%+ accuracy)
- Failure patterns reduce repeated test failures by 40%+
- Adaptive prioritization focuses on high-value tests

### Phase 5: Optimization & Documentation (Week 5)
**Duration:** 4-6 hours

**Tasks:**
1. Optimize test execution (parallelization)
2. Add test caching for unchanged components
3. Create comprehensive documentation
4. Train team on test generation
5. Establish test coverage targets

**Deliverables:**
- Parallel test execution (<30s for full suite)
- Test cache mechanism
- Implementation guide document
- Team training materials
- Test coverage policy

**Success Criteria:**
- Full integration suite runs in <30 seconds
- Cache reduces redundant test execution by 60%+
- 80%+ coverage across all 11 categories

---

## 🎯 Success Metrics

### Coverage Targets

| Metric | Baseline | Target (3 months) | Stretch Goal (6 months) |
|--------|----------|-------------------|-------------------------|
| Overall Coverage | 0% | 70% | 85% |
| Critical Path Coverage | 0% | 90% | 95% |
| High-Risk Component Coverage | 0% | 85% | 95% |
| Learning Library Coverage | 0% | 80% | 90% |
| Test Pass Rate | N/A | 95% | 98% |

### Quality Metrics

- **Test Generation Accuracy:** 90%+ of generated tests compile and run
- **False Positive Rate:** <5% of passing tests miss actual integration bugs
- **Discovery Accuracy:** 95%+ of new components auto-detected
- **Failure Pattern Learning:** 70%+ of repeated failures prevented by learned patterns

### Performance Metrics

- **Full Suite Execution:** <30 seconds (parallel)
- **Discovery Time:** <5 seconds
- **Test Generation Time:** <10 seconds per component
- **Align Overhead:** +45-60 seconds total (acceptable)

---

## 🔧 Technical Specifications

### Dependencies

**New:**
- `pytest-xdist` - Parallel test execution
- `pytest-cov` - Coverage reporting
- `pytest-timeout` - Test timeout management
- `astroid` - AST analysis for discovery
- `jinja2` - Test template rendering (already available)

**Existing:**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- SQLite3 - Tier 1-3 databases

### File Structure

```
src/test_discovery/
├── __init__.py
├── component_discovery.py      # AST-based discovery
├── test_generator.py           # Test generation engine
├── test_manifest.py            # Manifest management
├── risk_analyzer.py            # Tier 2 risk scoring
└── templates/                  # Test templates
    ├── orchestrator_integration.py.j2
    ├── agent_integration.py.j2
    ├── brain_tier_integration.py.j2
    ├── learning_integration.py.j2
    └── ... (7 more)

tests/integration/
├── conftest.py                 # Shared fixtures
├── orchestrators/
├── agents/
├── brain_tiers/
├── workflows/
├── response_templates/
├── utilities/
├── validation/
├── sessions/
├── config/
├── api_integrations/
├── learning/                   # NEW - Learning library tests
│   ├── test_learning_capture.py
│   ├── test_bug_driven_learning.py
│   ├── test_pattern_learning.py
│   └── test_tier2_integration.py
└── e2e/                        # End-to-end scenarios
    ├── test_plan_to_implementation.py
    ├── test_tdd_full_cycle.py
    └── test_learning_feedback_loop.py
```

---

## 🚨 Risk Analysis

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Test generation produces invalid tests | High | Medium | Manual review + validation phase |
| Discovery misses components | Medium | Low | AST fallback + manual manifest updates |
| Tier 2 integration adds latency | Medium | Medium | Async queries + caching |
| False positives reduce trust | High | Medium | Learning feedback loop + refinement |
| Test suite becomes too slow | Medium | Low | Parallelization + caching |

### Organizational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Team resists automated testing | Medium | Low | Show value early with critical bug catches |
| Test maintenance burden | Medium | Medium | Auto-generation reduces manual work by 70% |
| Coverage targets unrealistic | Low | Low | Phased approach with achievable milestones |

---

## 📚 Learning Library Integration Details

### Event-Driven Test Strategy

**1. Learning Event Capture Tests**
```python
# Test event capture from various sources
def test_capture_operation_failure():
    """Verify learning event created from operation failure."""
    agent = LearningCaptureAgent()
    result = {"success": False, "error": "Connection timeout"}
    
    event = agent.capture_from_operation_result(
        operation_name="deploy",
        result=result,
        context={"environment": "production"}
    )
    
    assert event.event_type == "operation_failure"
    assert event.severity == "high"
    assert "Connection timeout" in event.problem
```

**2. Pattern Learning Tests**
```python
# Test pattern extraction and storage
def test_bug_pattern_learning():
    """Verify bug patterns extracted and stored."""
    learner = BugDrivenLearner()
    
    bug = learner.capture_bug_event(
        test_name="test_auth_expiration",
        bug_category=BugCategory.SECURITY,
        bug_severity=BugSeverity.CRITICAL,
        description="JWT not expiring",
        expected_behavior="401 after timeout"
    )
    
    pattern = learner.extract_pattern(bug)
    assert pattern.category == "security"
    assert pattern.confidence > 0.8
    
    # Verify Tier 2 storage
    tier2 = KnowledgeGraph()
    stored = tier2.query_pattern(pattern.pattern_id)
    assert stored is not None
```

**3. Learning Feedback Loop Tests**
```python
# Test adaptive behavior from learning
def test_learning_feedback_loop():
    """Verify learning improves future behavior."""
    tier2_learning = Tier2LearningIntegration()
    
    # Simulate 10 user responses (70% acceptance)
    for i in range(10):
        accepted = i < 7
        tier2_learning.record_response(
            session_id=f"session-{i}",
            accepted=accepted,
            quality_level="GOOD"
        )
    
    # Check threshold adjustment
    adjusted = tier2_learning.should_adjust_threshold()
    assert adjusted is True
    
    recommendation = tier2_learning.get_threshold_recommendation()
    assert recommendation == "lower"  # More hints
```

### Learning-Enhanced Test Generation

```python
# Use Tier 2 patterns to generate better tests
def generate_tests_from_learning_patterns(component: Component):
    """Generate tests using learned failure patterns."""
    tier2 = KnowledgeGraph()
    
    # Query failure patterns for this component
    patterns = tier2.query_patterns(
        component=component.name,
        pattern_type="integration_failure",
        min_confidence=0.7
    )
    
    tests = []
    for pattern in patterns:
        # Generate regression test for each learned pattern
        test_code = f"""
def test_{component.name}_regression_{pattern.id}():
    '''Regression test for: {pattern.description}'''
    # Setup
    {component.name_lower} = {component.name}()
    
    # Reproduce failure scenario (from pattern)
    {pattern.reproduce_code}
    
    # Verify fix
    result = {component.name_lower}.{pattern.fixed_method}()
    assert result.success is True
    assert not {pattern.failure_condition}
"""
        tests.append(test_code)
    
    return tests
```

---

## 🎯 Next Actions

### Immediate (This Session)
1. ✅ Pull remote changes (learning library)
2. ✅ Analyze learning library architecture
3. ✅ Create comprehensive plan document
4. ⏳ Resolve merge conflicts
5. ⏳ Commit plan document
6. ⏳ Get user approval on plan

### Short Term (Next Session)
1. ⏳ Begin Phase 1 implementation
2. ⏳ Create integration test directory structure
3. ⏳ Build component discovery engine prototype
4. ⏳ Write 5 example learning integration tests

### Decision Point
**User must choose:**
- ✅ **Option A:** Full implementation (all 5 phases, 4-5 weeks)
- ⏸️ **Option B:** Phased rollout (validate after each phase)
- ⏸️ **Option C:** Proof of concept (Phase 1 only, then decide)

---

## 📊 Appendix: Example Test Manifest Entry

```yaml
# Complete example for LearningCaptureAgent
- name: "LearningCaptureAgent"
  path: "src/cortex_agents/learning_capture_agent.py"
  category: "learning"
  component_type: "agent"
  
  signature:
    class_methods:
      - name: "capture_from_operation_result"
        inputs:
          - operation_name: str
          - result: Any
          - context: Dict[str, Any]
        returns: "Optional[LearningEvent]"
      
      - name: "capture_from_exception"
        inputs:
          - exception: Exception
          - context: Dict[str, Any]
        returns: "Optional[LearningEvent]"
      
      - name: "capture_from_ambient_events"
        inputs:
          - lookback_minutes: int
        returns: "List[LearningEvent]"
  
  integration_points:
    - component: "LessonsLearned"
      type: "storage"
      file: "cortex-brain/lessons-learned.yaml"
    
    - component: "Tier2KnowledgeGraph"
      type: "pattern_storage"
      method: "store_pattern"
    
    - component: "GitOperations"
      type: "commit_analysis"
      method: "get_commit_info"
  
  dependencies:
    internal:
      - "src.tier2.knowledge_graph"
      - "src.orchestrators.git_checkpoint_orchestrator"
    external:
      - "yaml"
      - "json"
  
  test_file: "tests/integration/learning/test_learning_capture.py"
  test_status: "untested"
  
  risk_analysis:
    risk_score: 0.85
    risk_factors:
      - "Critical for self-improvement loop"
      - "Modified in last 30 days (15 times)"
      - "Integrates with 3+ components"
      - "No existing integration tests"
    
    tier2_insights:
      - "Failed 3 times in production (exception handling)"
      - "Similar component (BugDrivenLearner) has known issues"
      - "Pattern: Learning agents need robust error handling"
  
  suggested_tests:
    - "test_capture_operation_failure_integration"
    - "test_exception_to_lesson_flow"
    - "test_tier2_pattern_storage_integration"
    - "test_git_commit_learning_integration"
    - "test_ambient_event_processing"
```

---

**End of Plan Document**

**Status:** Awaiting user approval to proceed with Phase 1 implementation.
