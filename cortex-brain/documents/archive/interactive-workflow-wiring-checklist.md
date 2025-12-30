# Interactive Workflow Wiring Checklist

**Version:** 1.0.0  
**Date:** 2025-12-29  
**Author:** Asif Hussain  
**Purpose:** Universal checklist for wiring interactive workflows in CORTEX orchestrators

---

## 🎯 Overview

This checklist ensures complete wiring of interactive workflow components. Use it when:
- Creating new orchestrators with interactive mode
- Adding interactive mode to existing orchestrators
- Reviewing interactive wiring during maintenance
- Debugging interactive workflow issues

**Applies To:**
- ✅ Planning Orchestrator (partially built, needs wiring)
- ✅ ADO Orchestrator (needs full implementation)
- ⚠️ Future orchestrators requiring user collaboration

---

## 📋 Universal Wiring Checklist

### Phase 1: Component Verification ✅

**Before wiring, verify these components exist:**

- [ ] **Interactive Session Module**
  - File: `src/orchestrators/{name}/interactive_session.py`
  - Classes: `SessionState`, `{Name}Session`, `DiscoveryEngine`, `ApprovalWorkflow`, `CleanupPhase`
  - Size: ~600-700 lines

- [ ] **Interactive Agent**
  - File: `src/cortex_agents/strategic/interactive_{name}_planner.py`
  - Classes: `PlanningState`, `QuestionType`, `Question`, `Answer`, `Interactive{Name}Planner`
  - Size: ~800-1000 lines

- [ ] **Orchestrator Base**
  - File: `src/orchestrators/{name}/{name}_orchestrator.py`
  - Must extend: `BaseOrchestrator`
  - Must have: `execute()` method

---

### Phase 2: Decision Logic Implementation ✅

**Component:** Decision point for mode selection

**Implementation Location:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Method:**
```python
def _should_use_interactive_mode(self, kwargs: Dict) -> bool:
    """
    Decide if interactive mode is needed.
    
    Criteria (check all that apply):
    - Explicit request: kwargs.get("interactive", False)
    - User preference: self.config.get("prefer_interactive", False)
    - Complexity tier: Tier 4 (complex operations)
    - Low confidence: Ambiguous requirements (<60%)
    - Conflicts: Existing artifact detected
    
    Returns:
        True if interactive mode should be used
    """
    # Implementation here (~30-50 lines)
    pass
```

**Checklist:**
- [ ] Method `_should_use_interactive_mode()` exists
- [ ] Method checks explicit request flag
- [ ] Method checks user preference in config
- [ ] Method evaluates complexity tier
- [ ] Method estimates confidence score
- [ ] Method detects conflicts with existing artifacts
- [ ] Method has proper docstring
- [ ] Method has unit tests (≥5 test cases)

**Validation:**
```bash
grep -n "_should_use_interactive_mode" src/orchestrators/{name}/{name}_orchestrator.py
```

---

### Phase 3: Agent Registration ✅

**Component:** Register agent in system registry

**Implementation Location:** `src/cortex_agents/agent_registry.py`

**Required Registration:**
```python
from src.cortex_agents.strategic.interactive_{name}_planner import Interactive{Name}Planner

AGENT_REGISTRY = {
    # ... existing agents ...
    "interactive_{name}": Interactive{Name}Planner,
}
```

**Checklist:**
- [ ] Agent import added to `agent_registry.py`
- [ ] Agent registered in `AGENT_REGISTRY` dict
- [ ] Key follows convention: `"interactive_{name}"`
- [ ] Import path is correct and module exists
- [ ] Agent can be instantiated: `AGENT_REGISTRY["interactive_{name}"](config)`

**Validation:**
```bash
grep "interactive_{name}" src/cortex_agents/agent_registry.py
python3 -c "from src.cortex_agents.agent_registry import AGENT_REGISTRY; print('interactive_{name}' in AGENT_REGISTRY)"
```

---

### Phase 4: Orchestrator Agent Import ✅

**Component:** Import agent in orchestrator

**Implementation Location:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Import:**
```python
from src.cortex_agents.strategic.interactive_{name}_planner import (
    Interactive{Name}Planner,
    PlanningState,
    QuestionType
)
```

**Checklist:**
- [ ] Agent class imported
- [ ] Supporting enums imported (PlanningState, QuestionType)
- [ ] Import is at top of file with other imports
- [ ] No import errors when loading orchestrator

**Validation:**
```bash
grep "from.*interactive.*planner import" src/orchestrators/{name}/{name}_orchestrator.py
python3 -c "from src.orchestrators.{name}.{name}_orchestrator import {Name}Orchestrator"
```

---

### Phase 5: Execution Flow Routing ✅

**Component:** Conditional routing to interactive or autonomous mode

**Implementation Location:** `src/orchestrators/{name}/{name}_orchestrator.py::execute()`

**Required Pattern:**
```python
def execute(self, **kwargs) -> OrchestratorResult:
    """Execute orchestrator workflow."""
    self.status = OrchestratorStatus.RUNNING
    self.start_time = datetime.now()
    
    try:
        # Phase 1: Analyze request
        request_analysis = self._analyze_request(kwargs)
        
        # Phase 2: Mode selection (CRITICAL ROUTING POINT)
        if self._should_use_interactive_mode(kwargs):
            return self._execute_interactive_mode(request_analysis, kwargs)
        else:
            return self._execute_autonomous_mode(request_analysis, kwargs)
            
    except Exception as e:
        return self._create_error_result(str(e))
```

**Checklist:**
- [ ] `execute()` method calls `_should_use_interactive_mode()`
- [ ] Conditional routing exists (if/else for mode)
- [ ] Interactive path calls `_execute_interactive_mode()`
- [ ] Autonomous path calls `_execute_autonomous_mode()` (or existing logic)
- [ ] Both paths return `OrchestratorResult`
- [ ] Error handling wraps both paths

**Validation:**
```bash
grep -A 15 "def execute" src/orchestrators/{name}/{name}_orchestrator.py | grep "_should_use_interactive_mode"
grep -A 15 "def execute" src/orchestrators/{name}/{name}_orchestrator.py | grep "_execute_interactive_mode"
```

---

### Phase 6: Interactive Execution Method ✅

**Component:** Implementation of interactive workflow

**Implementation Location:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Method:**
```python
def _execute_interactive_mode(
    self, 
    analysis: RequestAnalysis, 
    kwargs: Dict
) -> OrchestratorResult:
    """
    Execute in interactive mode with user collaboration.
    
    Workflow:
    1. Create planning session
    2. Instantiate interactive agent
    3. Agent collaborates with user through session
    4. Agent returns result data
    5. Wrap in OrchestratorResult
    
    Args:
        analysis: Request analysis with complexity, confidence
        kwargs: Execution parameters from user
        
    Returns:
        OrchestratorResult with planning result
    """
    try:
        # 1. Create session
        session = self.interactive_{name}_creation(
            name=kwargs.get("feature_name", "unnamed"),
            user_context=kwargs.get("user_context", {})
        )
        
        # 2. Get agent
        agent = Interactive{Name}Planner(config=self.config)
        
        # 3. Collaborate (async)
        result_data = await agent.collaborate(session)
        
        # 4. Return result
        return self._create_success_result(
            plan_data=result_data,
            session=session
        )
        
    except Exception as e:
        self.logger.error(f"Interactive mode failed: {e}")
        return self._create_error_result(str(e))
```

**Checklist:**
- [ ] Method `_execute_interactive_mode()` exists
- [ ] Method creates planning session
- [ ] Method instantiates interactive agent
- [ ] Method calls agent's `collaborate()` method
- [ ] Method wraps result in `OrchestratorResult`
- [ ] Method has error handling
- [ ] Method has proper docstring
- [ ] Method has integration test

**Validation:**
```bash
grep -n "_execute_interactive_mode" src/orchestrators/{name}/{name}_orchestrator.py
grep -A 20 "_execute_interactive_mode" src/orchestrators/{name}/{name}_orchestrator.py | grep "Interactive.*Planner"
```

---

### Phase 7: User Interface Bridge ✅

**Component:** Question formatting and response parsing

**Implementation Location:** `src/orchestrators/{name}/user_interface.py` (NEW FILE)

**Required Classes:**

#### Class 1: QuestionFormatter
```python
class QuestionFormatter:
    """Format questions for user display."""
    
    def format_multiple_choice(self, question: Question) -> str:
        """Format multiple choice question with numbered options."""
        pass
    
    def format_yes_no(self, question: Question) -> str:
        """Format yes/no question."""
        pass
    
    def format_free_text(self, question: Question) -> str:
        """Format open-ended question."""
        pass
```

#### Class 2: ResponseParser
```python
class ResponseParser:
    """Parse user responses to questions."""
    
    def parse_answer(self, question: Question, user_input: str) -> Answer:
        """Parse user input based on question type."""
        pass
    
    def validate_answer(self, question: Question, answer: Answer) -> bool:
        """Validate answer is acceptable for question type."""
        pass
```

#### Class 3: ConversationManager
```python
class ConversationManager:
    """Manage interactive conversation flow."""
    
    def ask_question(self, question: Question) -> Answer:
        """Present question and collect answer."""
        pass
    
    def present_draft(self, draft_data: Dict) -> bool:
        """Show draft plan/work item, get approval."""
        pass
    
    def collect_feedback(self) -> List[str]:
        """Collect user's requested changes."""
        pass
```

**Checklist:**
- [ ] File `src/orchestrators/{name}/user_interface.py` exists
- [ ] Class `QuestionFormatter` implemented
- [ ] Class `ResponseParser` implemented
- [ ] Class `ConversationManager` implemented
- [ ] All methods have implementations (not just pass)
- [ ] All classes have docstrings
- [ ] Unit tests exist for each class
- [ ] UI bridge is imported in orchestrator

**Validation:**
```bash
test -f src/orchestrators/{name}/user_interface.py && echo "UI bridge exists" || echo "UI bridge MISSING"
grep "class QuestionFormatter" src/orchestrators/{name}/user_interface.py
grep "class ResponseParser" src/orchestrators/{name}/user_interface.py
grep "class ConversationManager" src/orchestrators/{name}/user_interface.py
```

---

### Phase 8: Integration Testing ✅

**Component:** End-to-end workflow tests

**Implementation Location:** `tests/orchestrators/{name}/test_interactive_workflow.py`

**Required Tests:**

```python
# Test 1: Decision logic - Explicit request
def test_decision_logic_explicit_request():
    """Test interactive mode triggered by explicit request."""
    orchestrator = {Name}Orchestrator(config)
    assert orchestrator._should_use_interactive_mode({"interactive": True}) == True

# Test 2: Decision logic - Complexity
def test_decision_logic_complexity_tier4():
    """Test interactive mode triggered by complexity."""
    orchestrator = {Name}Orchestrator(config)
    assert orchestrator._should_use_interactive_mode({"complexity": 4}) == True

# Test 3: Decision logic - Low confidence
def test_decision_logic_low_confidence():
    """Test interactive mode triggered by ambiguity."""
    orchestrator = {Name}Orchestrator(config)
    kwargs = {"feature_name": "ambiguous requirement"}
    # Mock low confidence
    assert orchestrator._should_use_interactive_mode(kwargs) == True

# Test 4: Mode routing to interactive
def test_mode_routing_to_interactive(mock_interactive_agent):
    """Test execution routes to interactive mode."""
    orchestrator = {Name}Orchestrator(config)
    result = orchestrator.execute(interactive=True, feature_name="test")
    assert result.status == OrchestratorStatus.SUCCESS
    assert mock_interactive_agent.collaborate.called

# Test 5: Mode routing to autonomous
def test_mode_routing_to_autonomous():
    """Test execution routes to autonomous mode."""
    orchestrator = {Name}Orchestrator(config)
    result = orchestrator.execute(interactive=False, feature_name="test")
    assert result.status == OrchestratorStatus.SUCCESS

# Test 6: Agent instantiation
def test_agent_instantiation():
    """Test interactive agent can be instantiated."""
    agent = Interactive{Name}Planner(config)
    assert agent is not None

# Test 7: Session creation
def test_session_creation():
    """Test session creation succeeds."""
    orchestrator = {Name}Orchestrator(config)
    session = orchestrator.interactive_{name}_creation("test", {})
    assert session.plan_name == "test"

# Test 8: End-to-end workflow
@pytest.mark.asyncio
async def test_end_to_end_interactive_workflow(mock_user_responses):
    """Test full interactive workflow from request to finalization."""
    orchestrator = {Name}Orchestrator(config)
    result = await orchestrator.execute_async(
        interactive=True,
        feature_name="complete-test"
    )
    assert result.status == OrchestratorStatus.SUCCESS
    assert result.output_path.exists()
```

**Checklist:**
- [ ] Test file `test_interactive_workflow.py` exists
- [ ] Test 1: Decision logic - explicit request
- [ ] Test 2: Decision logic - complexity threshold
- [ ] Test 3: Decision logic - low confidence
- [ ] Test 4: Mode routing to interactive
- [ ] Test 5: Mode routing to autonomous
- [ ] Test 6: Agent instantiation
- [ ] Test 7: Session creation
- [ ] Test 8: End-to-end workflow
- [ ] All tests pass (100%)
- [ ] Tests run in CI/CD pipeline

**Validation:**
```bash
test -f tests/orchestrators/{name}/test_interactive_workflow.py && echo "Tests exist" || echo "Tests MISSING"
python3 -m pytest tests/orchestrators/{name}/test_interactive_workflow.py -v
```

---

### Phase 9: Documentation ✅

**Component:** User and developer documentation

**Required Documentation:**

#### 1. Orchestrator README
- File: `src/orchestrators/{name}/README.md`
- Section: "Interactive Mode"
- Content: When interactive mode triggers, how to use it, examples

#### 2. Orchestrator Manifest
- File: `cortex-brain/manifests/orchestrators/{name}-orchestrator-manifest.yaml`
- Section: `interactive_mode:`
- Content: Triggers, workflow steps, configuration options

#### 3. User Guide
- File: `docs/user-guide/interactive-workflows.md`
- Section: "{Name} Orchestrator"
- Content: User-facing instructions with screenshots

#### 4. Maintenance Checklist
- File: `.github/prompts/cortex-maintenance.prompt.md`
- Section: "Phase 1.5: Interactive Workflow Wiring"
- Content: Validation steps for this orchestrator

**Checklist:**
- [ ] Orchestrator README updated with interactive mode section
- [ ] Orchestrator manifest has `interactive_mode:` section
- [ ] User guide includes interactive workflow examples
- [ ] Maintenance checklist includes this orchestrator
- [ ] CHANGELOG.md documents interactive mode addition
- [ ] API docs generated and current

**Validation:**
```bash
grep -i "interactive" src/orchestrators/{name}/README.md
grep "interactive_mode:" cortex-brain/manifests/orchestrators/{name}-orchestrator-manifest.yaml
```

---

### Phase 10: Automated Validation ✅

**Component:** Continuous validation script

**Implementation:** Use `scripts/validate_interactive_wiring.sh`

**Checklist:**
- [ ] Script exists: `scripts/validate_interactive_wiring.sh`
- [ ] Script is executable: `chmod +x scripts/validate_interactive_wiring.sh`
- [ ] Script validates this orchestrator
- [ ] Script generates health report
- [ ] Script runs in CI/CD pipeline
- [ ] Script added to maintenance Phase 1.5

**Validation:**
```bash
./scripts/validate_interactive_wiring.sh
echo "Exit code: $?"
ls -l cortex-brain/health-reports/interactive-wiring-status-*.md
```

---

## 🎯 Success Criteria

**Wiring is complete when ALL of the following are true:**

### Technical Criteria
- ✅ All 10 phases completed (100% checklist)
- ✅ Decision logic exists and is called
- ✅ Agent registered and importable
- ✅ Execution flow routes conditionally
- ✅ Interactive method implemented
- ✅ UI bridge exists with all 3 classes
- ✅ Integration tests: ≥8 tests, 100% passing
- ✅ Validation script passes with 100% coverage

### Quality Criteria
- ✅ Code review approved
- ✅ Documentation complete and current
- ✅ No merge conflicts
- ✅ CI/CD pipeline green
- ✅ Performance benchmarks met

### User Experience Criteria
- ✅ Interactive mode can be triggered
- ✅ Questions are clear and formatted well
- ✅ User responses are parsed correctly
- ✅ Draft plans/work items are presented
- ✅ Approval workflow functional
- ✅ Refinement loop works

---

## 🚨 Common Issues

### Issue 1: Agent Not Registered
**Symptom:** `KeyError: 'interactive_{name}'`  
**Fix:** Add agent to `agent_registry.py` and verify import

### Issue 2: Decision Logic Never Returns True
**Symptom:** Always uses autonomous mode  
**Fix:** Check criteria in `_should_use_interactive_mode()`, add logging

### Issue 3: Tests Passing But Functionality Broken
**Symptom:** Tests mock everything, real usage fails  
**Fix:** Add integration tests that use real components

### Issue 4: UI Bridge Not Used
**Symptom:** Agent instantiated but questions not shown  
**Fix:** Wire `ConversationManager` into agent's `collaborate()` method

### Issue 5: Async/Await Issues
**Symptom:** `RuntimeError: coroutine was never awaited`  
**Fix:** Ensure `collaborate()` is async and properly awaited

---

## 📚 References

- **Gap Analysis:** `cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md`
- **Maintenance Guide:** `.github/prompts/cortex-maintenance.prompt.md` (Phase 1.5)
- **Universal Pattern:** Gap analysis Section 3.1
- **Test Examples:** `tests/orchestrators/planning/test_interactive_planning_session.py`

---

## 🔄 Updates

**Version 1.0.0 (2025-12-29):**
- Initial checklist creation
- Covers Planning and ADO orchestrators
- 10-phase comprehensive validation

**Future Enhancements:**
- Pre-commit hooks for enforcement
- Automated checklist generation
- Interactive mode coverage dashboard

---

**End of Checklist**

Use this checklist for ANY orchestrator requiring interactive mode. Copy and customize for your specific orchestrator.
