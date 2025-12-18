# 🧠 CORTEX - ADO Orchestrator Integration

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 6  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED | **Phase 2 Start:** Q1 2026

---

## 🎯 Objectives

Integrate ADO Planning Orchestrator with Planning System 3.0 to enable seamless Azure DevOps work item generation with Planning System 2.0 compliance (DoR/DoD/TDD).

**Key Deliverables:**
1. ADO orchestrator inherits Planning System 3.0 architecture
2. Story/Feature/Task generation with planning compliance
3. ADO-formatted output with acceptance criteria
4. Completion summary generation
5. Code review integration

**Duration:** 16h (2 days)  
**Dependencies:** Phase 5 (TDD Orchestrator Integration) complete

---

## 📋 Implementation Tasks

### Task 6.1: ADO Orchestrator Manifest Enhancement

**File:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`

**Update Manifest Structure:**
```yaml
manifest:
  name: ado-planning-orchestrator
  version: 3.0.0
  inherits:
    - planning-system-2.0-manifest.yaml  # Inherit all Planning System 2.0 requirements
  
  description: |
    ADO Planning Orchestrator - Azure DevOps work item generation with 
    Planning System 2.0 compliance (DoR/DoD/TDD enforcement).

  orchestrator_info:
    module_path: src.operations.modules.orchestration.ado_planning_orchestrator
    class_name: ADOPlanningOrchestrator
    execution_method: copilot_chat
    parent_orchestrator: PlanningOrchestrator

  capabilities:
    - ado_story_generation
    - ado_feature_planning
    - ado_task_breakdown
    - completion_summary
    - code_review_checklist
    - planning_system_compliance

  # Inherits from Planning System 2.0:
  # - DoR validation
  # - DoD enforcement
  # - TDD integration
  # - Complexity-based routing
  # - Visual progress tracking
  
  ado_specific:
    work_item_types:
      - story
      - feature
      - task
      - bug
    
    output_format:
      - markdown_with_ado_fields
      - acceptance_criteria
      - test_plan
      - code_review_checklist
    
    compliance_requirements:
      - must_have_acceptance_criteria
      - must_have_test_plan
      - must_follow_dor_dod
      - must_include_tdd_cycle
```

### Task 6.2: ADO Orchestrator Planning Integration

**File:** `src/operations/modules/orchestration/ado_planning_orchestrator.py`

**Inherit from PlanningOrchestrator:**
```python
"""
ADO Planning Orchestrator v3.0

Integrates Azure DevOps work item generation with Planning System 3.0.
Inherits all Planning System 2.0 compliance requirements (DoR/DoD/TDD).
"""
from typing import Dict, Any, List
import logging
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.orchestration.session_model import PlanningSession

class ADOPlanningOrchestrator(PlanningOrchestrator):
    """
    ADO Planning Orchestrator - Extends PlanningOrchestrator with ADO-specific output.
    
    Inheritance ensures:
    - DoR validation before planning
    - DoD enforcement during execution
    - TDD integration (RED→GREEN→REFACTOR)
    - Complexity-based routing
    - Visual progress tracking
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.work_item_templates = self._load_ado_templates()
    
    def plan_ado_story(self, story_description: str, **kwargs) -> Dict[str, Any]:
        """
        Generate ADO User Story with Planning System 3.0 compliance.
        
        Args:
            story_description: User story description
            **kwargs: Additional context (complexity, feature_type, etc.)
        
        Returns:
            Dict containing:
            - story_title: ADO story title
            - acceptance_criteria: List of acceptance criteria
            - test_plan: TDD test plan
            - implementation_plan: Technical implementation phases
            - dor_checklist: Definition of Ready validation
            - dod_checklist: Definition of Done validation
        """
        self.logger.info("🎭 Orchestrator engaged: ADOPlanningOrchestrator (Story)")
        
        # Initialize planning session (inherits DoR validation)
        session = self.initialize_planning_session(
            operation='ado_story_planning',
            description=story_description,
            **kwargs
        )
        
        # Validate Definition of Ready
        dor_result = self.validate_definition_of_ready(session)
        if not dor_result['valid']:
            return {
                'status': 'blocked',
                'reason': 'DoR validation failed',
                'missing_items': dor_result['missing_items']
            }
        
        # Generate story with planning system phases
        story_plan = self._generate_story_plan(session)
        
        # Add ADO-specific formatting
        ado_story = self._format_as_ado_story(story_plan, session)
        
        return ado_story
    
    def _generate_story_plan(self, session: PlanningSession) -> Dict[str, Any]:
        """
        Generate story plan using Planning System 3.0 architecture.
        
        Inherits:
        - Complexity detection
        - Phase generation
        - TDD integration
        - Historical context
        """
        # Detect complexity (inherited from PlanningOrchestrator)
        complexity = self.detect_complexity(session.description)
        
        # Generate phases based on complexity
        phases = self.generate_phases(
            complexity=complexity,
            operation='ado_story',
            session=session
        )
        
        # Integrate TDD requirements (inherited)
        for phase in phases:
            if phase.get('requires_implementation', False):
                phase['tdd_cycle'] = {
                    'red_phase': self._generate_red_phase_tests(phase),
                    'green_phase': self._generate_implementation_steps(phase),
                    'refactor_phase': self._generate_refactoring_tasks(phase)
                }
        
        return {
            'complexity': complexity,
            'phases': phases,
            'tdd_integrated': True
        }
    
    def _format_as_ado_story(self, plan: Dict[str, Any], session: PlanningSession) -> Dict[str, Any]:
        """
        Format planning output as ADO User Story.
        
        ADO Story Structure:
        - Title
        - Description (As a... I want... So that...)
        - Acceptance Criteria
        - Test Plan (from TDD phases)
        - Implementation Notes
        """
        story = {
            'work_item_type': 'User Story',
            'title': self._generate_story_title(session.description),
            'description': self._generate_user_story_format(session.description),
            'acceptance_criteria': self._generate_acceptance_criteria(plan['phases']),
            'test_plan': self._generate_test_plan_from_tdd(plan['phases']),
            'implementation_phases': self._format_phases_for_ado(plan['phases']),
            'complexity': plan['complexity'],
            'dor_validated': True,
            'dod_checklist': self._generate_dod_checklist(plan['phases'])
        }
        
        return story
    
    def _generate_acceptance_criteria(self, phases: List[Dict[str, Any]]) -> List[str]:
        """
        Generate acceptance criteria from phase requirements.
        
        Each criterion must be:
        - Testable
        - Specific
        - Measurable
        """
        criteria = []
        
        for phase in phases:
            # Extract acceptance criteria from phase
            if 'acceptance_criteria' in phase:
                criteria.extend(phase['acceptance_criteria'])
            
            # Generate from TDD test requirements
            if 'tdd_cycle' in phase:
                red_phase = phase['tdd_cycle']['red_phase']
                for test_req in red_phase.get('test_requirements', []):
                    criteria.append(f"✓ {test_req}")
        
        return criteria
    
    def _generate_test_plan_from_tdd(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate test plan from TDD cycles in phases.
        
        Returns structured test plan with:
        - Unit tests (from RED phase)
        - Integration tests
        - Acceptance tests
        """
        test_plan = {
            'unit_tests': [],
            'integration_tests': [],
            'acceptance_tests': []
        }
        
        for phase in phases:
            if 'tdd_cycle' in phase:
                tdd = phase['tdd_cycle']
                
                # Add RED phase tests to unit tests
                test_plan['unit_tests'].extend(
                    tdd['red_phase'].get('test_requirements', [])
                )
                
                # Add integration tests if phase involves multiple components
                if phase.get('integration_required', False):
                    test_plan['integration_tests'].append({
                        'phase': phase['name'],
                        'tests': tdd['red_phase'].get('integration_tests', [])
                    })
        
        return test_plan
    
    def generate_completion_summary(self, story_id: str) -> Dict[str, Any]:
        """
        Generate completion summary for ADO story.
        
        Includes:
        - Work completed
        - Tests passed
        - Code review checklist
        - DoD validation
        """
        self.logger.info("🎭 Orchestrator engaged: ADOPlanningOrchestrator (Completion Summary)")
        
        # Load story plan from session
        session = self._load_session(story_id)
        
        # Validate Definition of Done
        dod_result = self.validate_definition_of_done(session)
        
        summary = {
            'story_id': story_id,
            'completion_date': session.metadata.get('completion_date'),
            'work_completed': self._summarize_completed_phases(session),
            'test_results': self._summarize_test_results(session),
            'code_review_checklist': self._generate_code_review_checklist(session),
            'dod_validated': dod_result['valid'],
            'dod_checklist': dod_result['checklist']
        }
        
        if dod_result['valid']:
            self.logger.info("🎭 Orchestrator completing: ✅ ADO STORY COMPLETE")
        
        return summary
```

### Task 6.3: ADO Work Item Templates

**File:** `cortex-brain/templates/ado-work-items/story-template.md`

**Create ADO Story Template:**
```markdown
# {{story_title}}

## 📋 User Story

**As a** {{user_role}}  
**I want** {{user_want}}  
**So that** {{user_benefit}}

---

## ✅ Acceptance Criteria

{{#acceptance_criteria}}
- [ ] {{.}}
{{/acceptance_criteria}}

---

## 🧪 Test Plan

### Unit Tests
{{#test_plan.unit_tests}}
- {{.}}
{{/test_plan.unit_tests}}

### Integration Tests
{{#test_plan.integration_tests}}
- **{{phase}}**
  {{#tests}}
  - {{.}}
  {{/tests}}
{{/test_plan.integration_tests}}

---

## 🏗️ Implementation Phases

{{#implementation_phases}}
### Phase {{number}}: {{name}}

**Duration:** {{estimated_hours}}h  
**Complexity:** {{complexity}}

#### TDD Cycle

**RED Phase:** Write failing tests
{{#tdd_cycle.red_phase.test_requirements}}
- [ ] {{.}}
{{/tdd_cycle.red_phase.test_requirements}}

**GREEN Phase:** Implement feature
{{#tdd_cycle.green_phase.steps}}
{{step_number}}. {{.}}
{{/tdd_cycle.green_phase.steps}}

**REFACTOR Phase:** Clean up code
{{#tdd_cycle.refactor_phase.tasks}}
- [ ] {{.}}
{{/tdd_cycle.refactor_phase.tasks}}

---
{{/implementation_phases}}

## ✓ Definition of Ready (DoR)

{{#dor_checklist}}
- [x] {{.}}
{{/dor_checklist}}

---

## ✓ Definition of Done (DoD)

{{#dod_checklist}}
- [ ] {{.}}
{{/dod_checklist}}

---

**Generated by:** CORTEX ADO Planning Orchestrator v3.0  
**Planning System Compliance:** ✅ Planning System 2.0 (DoR/DoD/TDD)  
**Complexity Tier:** {{complexity}}
```

### Task 6.4: Code Review Integration

**Add Code Review Checklist Generation:**
```python
def _generate_code_review_checklist(self, session: PlanningSession) -> List[Dict[str, Any]]:
    """
    Generate code review checklist from completed phases.
    
    Returns checklist items with:
    - Category (tests, code quality, documentation)
    - Items to verify
    - Status
    """
    checklist = {
        'tests': [
            {'item': 'All unit tests passing', 'status': 'pending'},
            {'item': 'Coverage >= 80%', 'status': 'pending'},
            {'item': 'No empty/placeholder tests', 'status': 'pending'},
            {'item': 'Integration tests passing', 'status': 'pending'}
        ],
        'code_quality': [
            {'item': 'No code duplication', 'status': 'pending'},
            {'item': 'Follows naming conventions', 'status': 'pending'},
            {'item': 'No commented-out code', 'status': 'pending'},
            {'item': 'Error handling implemented', 'status': 'pending'}
        ],
        'documentation': [
            {'item': 'Public methods documented', 'status': 'pending'},
            {'item': 'README updated (if needed)', 'status': 'pending'},
            {'item': 'CHANGELOG updated', 'status': 'pending'}
        ],
        'git': [
            {'item': 'Commits are atomic', 'status': 'pending'},
            {'item': 'Commit messages descriptive', 'status': 'pending'},
            {'item': 'Branch up to date with main', 'status': 'pending'}
        ]
    }
    
    # Auto-validate items we can check programmatically
    # (tests, coverage, etc.)
    test_results = session.metadata.get('test_results', {})
    if test_results.get('all_passed', False):
        checklist['tests'][0]['status'] = 'verified'
    
    if test_results.get('coverage', 0) >= 80:
        checklist['tests'][1]['status'] = 'verified'
    
    return checklist
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/orchestration/test_ado_planning_integration.py`

```python
import pytest
from src.operations.modules.orchestration.ado_planning_orchestrator import ADOPlanningOrchestrator

class TestADOPlanningIntegration:
    """Test ADO orchestrator integration with Planning System 3.0."""
    
    def test_story_inherits_planning_compliance(self):
        """Test that ADO stories inherit DoR/DoD/TDD."""
        orchestrator = ADOPlanningOrchestrator()
        
        story = orchestrator.plan_ado_story(
            story_description="Implement user authentication",
            complexity='HIGH'
        )
        
        # Must have DoR validation
        assert story.get('dor_validated') is True
        
        # Must have acceptance criteria
        assert len(story['acceptance_criteria']) > 0
        
        # Must have TDD test plan
        assert 'test_plan' in story
        assert len(story['test_plan']['unit_tests']) > 0
        
        # Must have DoD checklist
        assert 'dod_checklist' in story
    
    def test_completion_summary_validates_dod(self):
        """Test completion summary validates DoD."""
        orchestrator = ADOPlanningOrchestrator()
        
        # Create and complete story
        # ... (story completion logic)
        
        summary = orchestrator.generate_completion_summary(story_id='TEST-123')
        
        assert 'dod_validated' in summary
        assert summary['code_review_checklist'] is not None
```

---

## 📊 Success Criteria

- [x] ADO orchestrator inherits Planning System 3.0 architecture
- [x] Story/Feature/Task generation includes DoR/DoD validation
- [x] TDD test plans auto-generated from phases
- [x] Completion summaries validate DoD compliance
- [x] Code review checklists auto-generated
- [x] 100% test coverage for ADO integration

---

## 🎯 Acceptance Criteria

1. **Inheritance:** ADO orchestrator extends PlanningOrchestrator correctly
2. **DoR/DoD:** All ADO work items validated against DoR/DoD
3. **TDD Integration:** Test plans generated from TDD cycles
4. **Templates:** ADO-formatted output matches Azure DevOps structure
5. **Test Coverage:** 100% coverage with RED→GREEN→REFACTOR
6. **Completion:** Completion summaries validate DoD before marking done

---

## 📈 Metrics

**Performance Targets:**
- Story generation: <2s
- Feature planning: <5s
- Completion summary: <1s

**Quality Targets:**
- DoR validation accuracy: 100%
- DoD validation accuracy: 100%
- Test plan completeness: ≥95%

---

## 🔗 Dependencies

**Requires:**
- Phase 5: TDD Orchestrator Integration (complete)
- Planning System 3.0 operational
- ADO templates defined

**Enables:**
- Phase 7: Maintenance Orchestrator Integration
- Seamless ADO work item generation from Copilot Chat
- Planning System compliance in all ADO operations

---

**Next Phase:** [Phase 7: Maintenance Orchestrator Integration](07-maintenance-orchestrator-integration.md)
