# Week 10 Day 1: ADO Orchestrator Migration Plan

**Version:** 1.1 | **Author:** Asif Hussain | **Created:** December 20, 2025 | **Updated:** December 20, 2025  
**Status:** 🟡 IN PROGRESS | **Estimated Duration:** 3-5 days | **Complexity:** HIGH

---

## 🚀 Execution Modes

### Mode 1: Supervised (Task-by-Task)
- User executes each task individually
- Manual approval after each RED/GREEN/REFACTOR phase
- Git checkpoint requires user confirmation
- **Command:** `execute task [N]`

### Mode 2: Autonomous (Full Phase Execution)
- Execute all 10 tasks end-to-end autonomously
- Auto-validation after each task
- Auto-git checkpoint on success
- Self-healing: Retry failed tasks up to 3 times
- Escalate to user after 3 consecutive failures
- **Commands:** 
  - `execute all phases autonomously`
  - `execute tasks 2-10 autonomously` (continue from Task 2)

**Pattern Reference:** Planning System 2.0 autonomous execution (planning-system-4.0-manifest.yaml line 166+)

---

## 🎯 Mission

Migrate ADO work item management from utility pattern to full Planning System 2.0-compliant orchestrator with parity enforcement, DoR/DoD validation, and interactive workflows.

---

## 📊 Current State Analysis

### ✅ What Exists (Infrastructure 70% Ready)

**ADO Utility (src/operations/modules/ado/ado_utility.py):**
- ✅ Work item CRUD operations (1,086 lines)
- ✅ DoR/DoD validation
- ✅ Completion summaries
- ✅ Data models (WorkItemMetadata, WorkItemSummary)
- ✅ Status enumeration (active/completed/blocked/cancelled)

**ADO Agent (src/cortex_agents/ado_agent.py):**
- ✅ Azure DevOps API integration
- ✅ Authentication handling
- ✅ Work item API calls

**ADO Manifest (ado-planning-manifest.yaml):**
- ✅ Complete requirements specification (8 inherited + 7 ADO-specific)
- ✅ Workflow phases defined (4 phases, 13 steps)
- ✅ Quality gates documented (3 inherited + 3 ADO-specific)
- ✅ Parity checklist with Planning System 2.0

**ADO Parser (src/planning/ado_parser.py):**
- ✅ Plan-to-ADO mapping logic
- ✅ Work item hierarchy generation

### ❌ What's Missing (Gaps = 30%)

**Orchestrator Pattern:**
- ❌ No BaseOrchestrator inheritance
- ❌ No PlanningPhase enum usage
- ❌ No `🎭` engagement hints
- ❌ No phase transitions (DISCOVERY → VALIDATION → GENERATION → EXECUTION)

**Planning System 2.0 Parity:**
- ❌ Interactive DoR workflow (REQ-002)
- ❌ Acceptance criteria approval gate (REQ-001, GATE-005)
- ❌ Contextual review integration (REQ-003 partial)
- ❌ Visual progress rendering (REQ-005)
- ❌ Learning library auto-documentation (REQ-006)
- ❌ Threat modeling integration (REQ-007)
- ❌ TDD reminders visibility (REQ-008)

**ADO-Specific Features:**
- ❌ Area path & iteration assignment (REQ-ADO-005)
- ❌ Bulk work item creation (REQ-ADO-006)
- ❌ Story point validation gate (GATE-ADO-003)
- ❌ Git checkpoint after creation (STEP-ADO-2.4)

---

## 🏗️ Architecture Design

### Target Structure

```
src/orchestrators/ado/
├── __init__.py
├── ado_orchestrator.py              # Main orchestrator (inherits BaseOrchestrator)
├── ado_workflow_phases.py           # Phase implementations
├── ado_validators.py                # DoR/DoD validators
├── ado_generators.py                # Work item generators
├── ado_formatters.py                # ADO-specific formatters
└── tests/
    ├── test_ado_orchestrator.py
    ├── test_ado_validators.py
    ├── test_ado_generators.py
    └── test_ado_integration.py
```

### Phase Flow

```
┌────────────────────────────────────────────────────────────────┐
│ PHASE 0: DISCOVERY                                              │
├────────────────────────────────────────────────────────────────┤
│ • Parse user request (feature/story/task)                       │
│ • Run review orchestrator (contextual analysis)                 │
│ • Check existing ADO items (prevent duplication)                │
│ • Classify complexity (HIGH/MEDIUM/LOW)                         │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 1: VALIDATION                                             │
├────────────────────────────────────────────────────────────────┤
│ • Interactive DoR refinement (user Q&A)                         │
│ • Validate ADO authentication                                   │
│ • Validate project/area path accessibility                      │
│ • Run threat modeling (if security keywords detected)           │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 2: GENERATION                                             │
├────────────────────────────────────────────────────────────────┤
│ • Generate work item hierarchy (Epic→Feature→Task)              │
│ • Map effort hours → story points (Fibonacci)                   │
│ • Inject TDD requirements into acceptance criteria              │
│ • Generate DoD checklist                                        │
│ • Format ADO-specific fields (area path, iteration)             │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 3: APPROVAL GATE (Interactive)                            │
├────────────────────────────────────────────────────────────────┤
│ • Show generated work items preview                             │
│ • User approval: [Create Items] [Modify] [Cancel]               │
│ • If modify: Loop back to GENERATION phase                      │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 4: EXECUTION                                              │
├────────────────────────────────────────────────────────────────┤
│ • Create ADO work items (batch API)                             │
│ • Establish parent-child links                                  │
│ • Assign area path & iteration                                  │
│ • Create git checkpoint                                         │
│ • Document to learning library                                  │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ PHASE 5: COMPLETION                                             │
├────────────────────────────────────────────────────────────────┤
│ • Generate clickable ADO work item links                        │
│ • Show visual progress summary                                  │
│ • Return success response with metrics                          │
│ • Show 🎉 CONGRATULATIONS if all items created successfully     │
└────────────────────────────────────────────────────────────────┘
```

---

## 📋 Autonomous Execution Summary

**Tasks:** 10 total (1 complete, 9 remaining)  
**Estimated Time:** 23-37 hours remaining (3-5 days)  
**Completion Rate:** 10% (Task 1/10 complete)

**Autonomous Workflow:**
1. Execute Task 2-10 sequentially
2. Run RED→GREEN→REFACTOR for each task
3. Auto-validate tests after each task
4. Auto-commit on success with descriptive message
5. Self-heal: Retry up to 3 times on failure
6. Escalate to user after 3 consecutive failures
7. Generate completion report when all tasks done

**Success Criteria (Autonomous):**
- ✅ All 25 tests passing (100% pass rate)
- ✅ 85%+ coverage on ado_orchestrator.py
- ✅ All phases implemented with transitions
- ✅ Parity with Planning System 2.0 validated
- ✅ Git checkpoints at each task completion
- ✅ Final completion report generated

**To Execute:** Say "execute all phases autonomously" or "execute tasks 2-10 autonomously"

---

## 📋 Implementation Tasks (TDD RED→GREEN→REFACTOR)

### Task 1: Orchestrator Foundation (Day 1 Morning - 3h)

**RED Phase (30min):**
```python
# tests/test_ado_orchestrator.py
def test_ado_orchestrator_inherits_base():
    """Orchestrator must inherit BaseOrchestrator."""
    assert issubclass(ADOOrchestrator, BaseOrchestrator)

def test_ado_orchestrator_has_phases():
    """Orchestrator must implement all 5 phases."""
    orchestrator = ADOOrchestrator()
    assert hasattr(orchestrator, 'current_phase')
    # Test phase transitions...

def test_engagement_hints_displayed():
    """Orchestrator must show 🎭 engagement hints."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test Feature")
    assert "🎭 Orchestrator engaged: ADOOrchestrator" in result.logs

# Expected: 3 failing tests
```

**GREEN Phase (2h):**
```python
# src/orchestrators/ado/ado_orchestrator.py
from src.orchestrators.base.base_orchestrator import BaseOrchestrator
from enum import Enum

class ADOPhase(Enum):
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    GENERATION = "generation"
    APPROVAL = "approval"
    EXECUTION = "execution"
    COMPLETION = "completion"

class ADOOrchestrator(BaseOrchestrator):
    def __init__(self):
        super().__init__()
        self.current_phase = ADOPhase.DISCOVERY
        self.logger.info("🎭 Orchestrator engaged: ADOOrchestrator")
    
    def execute(self, **kwargs):
        self.logger.info(f"🎭 Phase transition: START → {ADOPhase.DISCOVERY.value.upper()}")
        # Implementation...
```

**REFACTOR Phase (30min):**
- Extract phase logic to `ado_workflow_phases.py`
- Add type hints
- Document phase responsibilities

**Expected Outcome:** 3/3 tests passing, foundation structure validated

---

### Task 2: Discovery Phase Integration (Day 1 Afternoon - 3h)

**RED Phase (30min):**
```python
def test_review_orchestrator_called():
    """Must run review orchestrator before planning."""
    orchestrator = ADOOrchestrator()
    with patch('src.orchestrators.review.review_orchestrator') as mock:
        orchestrator.execute(feature="Auth System")
        mock.execute.assert_called_once()

def test_duplicate_detection():
    """Must check for existing ADO items with similar names."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Login Feature")
    assert "Existing ADO items found" in result.warnings or \
           "No duplicates found" in result.info

def test_complexity_classification():
    """Must classify feature complexity."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Add JWT authentication")
    assert result.complexity in ["HIGH", "MEDIUM", "LOW"]

# Expected: 3 failing tests
```

**GREEN Phase (2h):**
- Implement review orchestrator integration
- Add ADO API duplicate search
- Integrate complexity analyzer

**REFACTOR Phase (30min):**
- Extract to `ado_validators.py`
- Optimize API calls
- Add caching for duplicate checks

**Expected Outcome:** 6/6 tests passing, discovery phase validated

---

### Task 3: Interactive DoR Workflow (Day 2 Morning - 4h)

**RED Phase (45min):**
```python
def test_interactive_dor_prompts_user():
    """Must prompt user for DoR clarifications."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Payment Gateway")
    assert "DoR Questions" in result.interactive_prompts

def test_dor_validation_blocks_incomplete():
    """Must block work item creation if DoR incomplete."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test", dor_complete=False)
    assert result.status == "blocked"
    assert "DoR incomplete" in result.errors

def test_dor_refinement_loop():
    """Must allow iterative DoR refinement."""
    orchestrator = ADOOrchestrator()
    # Simulate 2-round refinement
    result1 = orchestrator.refine_dor(feature="X", round=1)
    result2 = orchestrator.refine_dor(feature="X", round=2)
    assert result2.refinement_count == 2

# Expected: 3 failing tests
```

**GREEN Phase (2h 45min):**
- Implement interactive Q&A workflow
- Add DoR validation logic
- Support multi-round refinement

**REFACTOR Phase (30min):**
- Extract to `ado_validators.py::DoRValidator`
- Add question templates
- Cache refinement state

**Expected Outcome:** 9/9 tests passing, DoR workflow validated

---

### Task 4: Work Item Generation (Day 2 Afternoon - 4h)

**RED Phase (45min):**
```python
def test_hierarchy_generation():
    """Must generate Epic→Feature→Task hierarchy."""
    generator = ADOGenerator()
    result = generator.generate_hierarchy(plan_data)
    assert result.epic is not None
    assert len(result.features) > 0
    assert len(result.tasks) > 0

def test_story_point_conversion():
    """Must convert hours to Fibonacci story points."""
    generator = ADOGenerator()
    assert generator.hours_to_story_points(1) == 1
    assert generator.hours_to_story_points(3) == 2
    assert generator.hours_to_story_points(6) == 5

def test_tdd_requirements_injection():
    """Must inject TDD into acceptance criteria."""
    generator = ADOGenerator()
    result = generator.generate_work_item(task_data)
    assert any("RED phase" in criterion for criterion in result.acceptance_criteria)

# Expected: 3 failing tests
```

**GREEN Phase (2h 45min):**
- Implement hierarchy generator
- Add Fibonacci conversion
- Inject TDD templates

**REFACTOR Phase (30min):**
- Extract to `ado_generators.py`
- Add configuration for story point mapping
- Optimize TDD template injection

**Expected Outcome:** 12/12 tests passing, generation validated

---

### Task 5: Approval Gate (Day 3 Morning - 3h)

**RED Phase (30min):**
```python
def test_approval_gate_shows_preview():
    """Must show work item preview before creation."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test")
    assert "Work Items Preview" in result.preview

def test_approval_gate_blocks_without_approval():
    """Must not create items without user approval."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test", auto_approve=False)
    assert result.items_created == 0

def test_approval_gate_allows_modification():
    """Must allow user to modify before approval."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test", modify_request=True)
    assert result.status == "awaiting_modification"

# Expected: 3 failing tests
```

**GREEN Phase (2h):**
- Implement preview generation
- Add approval checkpoint
- Support modification loop

**REFACTOR Phase (30min):**
- Extract to `ado_workflow_phases.py::ApprovalPhase`
- Add template for preview display
- Document approval UX

**Expected Outcome:** 15/15 tests passing, approval gate validated

---

### Task 6: ADO API Integration (Day 3 Afternoon - 4h)

**RED Phase (45min):**
```python
def test_batch_work_item_creation():
    """Must create multiple work items in single API call."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test", items=10)
    assert result.api_calls == 1  # Batch, not 10 separate calls

def test_parent_child_linking():
    """Must establish parent-child links."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test")
    for task in result.tasks:
        assert task.parent_id in [f.id for f in result.features]

def test_area_path_assignment():
    """Must assign correct area path and iteration."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test", area="Platform\\API")
    assert all(item.area_path == "Platform\\API" for item in result.items)

# Expected: 3 failing tests
```

**GREEN Phase (2h 45min):**
- Implement batch API calls
- Add link establishment
- Support area path/iteration

**REFACTOR Phase (30min):**
- Optimize API call batching
- Add retry logic for failures
- Cache ADO project metadata

**Expected Outcome:** 18/18 tests passing, API integration validated

---

### Task 7: Git Checkpoint & Learning Library (Day 4 Morning - 3h)

**RED Phase (30min):**
```python
def test_git_checkpoint_after_creation():
    """Must create git checkpoint after successful creation."""
    orchestrator = ADOOrchestrator()
    with patch('src.orchestrators.git.git_checkpoint') as mock:
        orchestrator.execute(feature="Test")
        mock.create_auto_checkpoint.assert_called_once()

def test_learning_library_documentation():
    """Must document ADO strategy to learning library."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Complex Auth System")
    assert result.learning_event is not None
    assert result.learning_event.type == "ado_planning_success"

# Expected: 2 failing tests
```

**GREEN Phase (2h):**
- Integrate git checkpoint
- Add learning library events
- Document strategy patterns

**REFACTOR Phase (30min):**
- Extract to integration module
- Add configuration for auto-checkpoint
- Optimize event logging

**Expected Outcome:** 20/20 tests passing, integrations validated

---

### Task 8: Visual Progress & Completion (Day 4 Afternoon - 3h)

**RED Phase (30min):**
```python
def test_visual_progress_rendering():
    """Must show ASCII progress visualization."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test")
    assert "PHASE 0: DISCOVERY" in result.progress_visual
    assert "[█████]" in result.progress_visual

def test_ado_work_item_links():
    """Must generate clickable ADO links."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test")
    assert all("https://dev.azure.com" in link for link in result.work_item_links)

def test_congratulations_on_success():
    """Must show 🎉 CONGRATULATIONS when all items created."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(feature="Test")
    if result.items_created == result.items_planned:
        assert "🎉 CONGRATULATIONS" in result.response

# Expected: 3 failing tests
```

**GREEN Phase (2h):**
- Implement progress visualization
- Generate ADO links
- Add completion template

**REFACTOR Phase (30min):**
- Extract to `ado_formatters.py`
- Optimize rendering
- Add configuration for visual style

**Expected Outcome:** 23/23 tests passing, completion validated

---

### Task 9: Integration Tests (Day 5 Morning - 3h)

**RED Phase (45min):**
```python
def test_end_to_end_ado_planning():
    """Full workflow: discovery → validation → generation → approval → execution → completion."""
    orchestrator = ADOOrchestrator()
    result = orchestrator.execute(
        feature="User Authentication System",
        auto_approve=True,
        test_mode=True  # Mock ADO API
    )
    assert result.status == "success"
    assert result.items_created > 0

def test_parity_with_planning_system():
    """Must have feature parity with Planning System 2.0."""
    from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
    
    planning_features = dir(PlanningOrchestrator)
    ado_features = dir(ADOOrchestrator)
    
    required_features = [
        'refine_dor_interactive',
        'approve_acceptance_criteria',
        'integrate_review_orchestrator',
        'show_visual_progress'
    ]
    
    for feature in required_features:
        assert feature in ado_features, f"Missing: {feature}"

# Expected: 2 failing tests initially, then passing
```

**GREEN Phase (1h 45min):**
- Wire all phases together
- Add E2E test scenarios
- Validate parity

**REFACTOR Phase (30min):**
- Optimize phase transitions
- Add comprehensive logging
- Document E2E workflow

**Expected Outcome:** 25/25 tests passing, E2E validated

---

### Task 10: Documentation & Finalization (Day 5 Afternoon - 2h)

**Deliverables:**

1. **Module Documentation:**
   - `ado-orchestrator-guide.md` (comprehensive usage guide)
   - Inline docstrings for all public methods
   - Architecture diagrams

2. **Update Status Trackers:**
   - CORTEX4-STATUS.md (mark Week 10 Day 1-5 complete)
   - ado-planning-manifest.yaml (update all statuses to "implemented")

3. **Create Completion Report:**
   - `week-10-ado-orchestrator-completion.md`
   - Metrics: LOC, test coverage, API performance
   - Known issues and future enhancements

---

## 📊 Success Criteria

### Must-Have (100% Required)

- ✅ All 25 tests passing (100% pass rate)
- ✅ BaseOrchestrator inheritance validated
- ✅ All 5 phases implemented with transitions
- ✅ Interactive DoR workflow operational
- ✅ Approval gate enforced
- ✅ ADO API integration working (batch creation)
- ✅ Git checkpoint after creation
- ✅ Visual progress rendering
- ✅ Parity with Planning System 2.0 validated

### Nice-to-Have (80% Completion Acceptable)

- ⚠️ Threat modeling integration (80% OK if time limited)
- ⚠️ Learning library documentation (manual fallback OK)
- ⚠️ Area path/iteration auto-detection (manual input OK)

### Quality Gates

- **Test Coverage:** 85%+ on ado_orchestrator.py
- **Performance:** <500ms for generation phase
- **API Efficiency:** <3 API calls for typical 10-item creation
- **Documentation:** 100% of public methods documented

---

## 🚨 Risk Mitigation

### Risk 1: ADO API Rate Limiting
**Mitigation:** Implement batch API calls, add retry logic with exponential backoff

### Risk 2: Planning System 2.0 Parity Drift
**Mitigation:** Automated parity validation tests, manifest-driven validation

### Risk 3: Interactive Workflow Complexity
**Mitigation:** Start with simple Y/N prompts, iterate to rich UX

### Risk 4: Test Data Dependency
**Mitigation:** Use mocks for ADO API, create comprehensive test fixtures

---

## 📈 Metrics & Validation

**Development Metrics:**
- **Lines of Code:** ~800 (orchestrator) + ~400 (tests) = 1,200 LOC
- **Test Count:** 25 tests (9 unit + 6 integration + 10 phase-specific)
- **Coverage Target:** 85%+
- **Estimated Time:** 3-5 days (26-40 hours)

**Performance Benchmarks:**
- **Phase Transitions:** <50ms each
- **Work Item Generation:** <200ms for 10 items
- **ADO API Creation:** <1s for batch of 10 items
- **Total Workflow:** <3s for typical feature planning

**Quality Validation:**
```bash
# Run test suite
pytest tests/orchestrators/ado/ -v --cov=src/orchestrators/ado --cov-report=html

# Expected: 25/25 passing, 85%+ coverage

# Run parity validation
python scripts/validate_ado_parity.py

# Expected: 8/8 features matching Planning System 2.0
```

---

## 🔄 Dependencies & Prerequisites

### Required (Must Exist)

- ✅ BaseOrchestrator (`src/orchestrators/base/base_orchestrator.py`)
- ✅ ADO Utility (`src/operations/modules/ado/ado_utility.py`)
- ✅ ADO Agent (`src/cortex_agents/ado_agent.py`)
- ✅ Planning System 2.0 (`src/orchestrators/planning/`)
- ✅ Review Orchestrator (`src/orchestrators/review/`)

### Optional (Graceful Degradation)

- ⚠️ Threat Modeler Agent (skip if not available)
- ⚠️ Learning Library (log locally if unavailable)
- ⚠️ Git Checkpoint (warn if git not initialized)

---

## 🎯 Next Steps After Completion

1. **Week 10 Day 6-7:** Sanitization Orchestrator Migration
2. **Week 10 Day 8-10:** Test Migration Analysis
3. **Week 11:** Post-Phase 5 TDD v4.0 Enhancement (57%→95% alignment)

---

## 📞 Contact & Support

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Manifest:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`  
**Status Tracker:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/CORTEX4-STATUS.md`

---

**Approval Status:** 🟡 PENDING REVIEW  
**Ready to Start:** After approval + TDD environment setup validation
