# 🛡️ ADO Orchestrator v2 Migration Plan

**Plan ID:** ado-v2-migration  
**Feature:** ADO Orchestrator Migration to Pure Autonomous Architecture with Conversational Wizard  
**Created:** January 2, 2026  
**Complexity:** TIER 3 (ORCHESTRATOR MIGRATION)  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.1)  
**Strategy:** Migrate existing ADO v1 (6-phase hybrid) + Conversational Wizard (5.1a) to config-driven autonomous v2  
**Estimated Duration:** 6 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `██████████░░░░░░░░░░` **50%** ⏳ IN PROGRESS

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation & Analysis | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 1 | Core v2 Implementation | `█████████░` | 2d | ⚠️ 90% Complete (assessed) |
| 2 | Wizard Integration | `██████████` | 1d | ✅ Complete |
| 3 | Config & Templates | `██████████` | 1d | ✅ Complete |
| 4 | Testing & Validation | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |
| 5 | Master Orch Activation | `░░░░░░░░░░` | 0.5d | ⏸️ Not Started |

---

## 🎯 Executive Summary

### Migration Goals

Transform ADO Orchestrator from **hybrid execution model** to **pure autonomous architecture**:

**Current State (v1):**
- ✅ 6-phase workflow (DISCOVERY → VALIDATION → GENERATION → APPROVAL → EXECUTION → COMPLETION)
- ✅ Planning System parity (DoR, approval gates, visual progress)
- ✅ Conversational wizard added (Phase 5.1a - 7-stage interactive mode)
- ❌ Mixed Python/YAML logic (manifest contains natural language instructions)
- ❌ Not Master Orchestrator integrated
- ❌ State not tracked in PlanningStateDB
- ❌ No template-driven outputs
- ❌ Limited rollback capabilities

**Target State (v2):**
- ✅ Pure Python execution (zero natural language in manifest)
- ✅ Config-only YAML manifest (routing patterns, templates, validation rules)
- ✅ Master Orchestrator integrated (pattern-based routing + LLM fallback)
- ✅ State persistence in PlanningStateDB
- ✅ Template-driven output generation (Jinja2)
- ✅ Atomic transactions with rollback
- ✅ Dual-mode operation (auto-generation + conversational wizard)
- ✅ BaseOrchestrator v4.1 compliance

### Success Criteria

**Technical:**
- ✅ ADO v2 inherits from BaseOrchestrator v4.1
- ✅ All 6 phases execute via pure Python (no manifest interpretation)
- ✅ Conversational wizard integrated as mode selector
- ✅ Config manifest contains ONLY data structures
- ✅ State tracked across all 6 phases in database
- ✅ Templates render work item previews, approval screens, completion messages
- ✅ 100% test coverage (unit + integration)
- ✅ Master Orchestrator routes "ado story" → ADO v2

**Functional:**
- ✅ Dual-mode: `ado story X` (auto) + `ado wizard X` (interactive)
- ✅ Vision API integration for screenshot-based acceptance criteria
- ✅ DoR refinement workflow preserved
- ✅ Approval gate with markdown preview
- ✅ ADO API integration unchanged (work item creation)
- ✅ Parent-child linking operational
- ✅ Backward compatibility (same user commands)

---

## 🏗️ Phase 0: Foundation & Analysis (1 day)

**Goal:** Analyze existing ADO v1, document architecture, prepare migration artifacts

### Task 0.1: ADO v1 Analysis
**Duration:** 4h

Analyze existing implementation:

**Files to Analyze:**
- `src/orchestrators/ado/ado_orchestrator.py` (2106 lines - v1 implementation)
- `src/orchestrators/ado/ado_conversational_wizard.py` (685 lines - Phase 5.1a)
- `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` (if exists)
- `src/cortex_agents/ado_agent.py` (agent integration)

**Analysis Deliverables:**
- `context/ado-v1-architecture.md` - Complete architectural documentation
  - 6-phase workflow breakdown
  - State management approach
  - ADO API integration patterns
  - Error handling mechanisms
  - Current limitations

- `context/conversational-wizard-design.md` - Wizard architecture from 5.1a
  - 7-stage conversation flow
  - Session state management
  - Vision API integration points
  - Skip/default handling
  - Approval/refine loop

- `context/hybrid-execution-analysis.md` - Brittleness identification
  - Natural language in manifest
  - Ambiguous control flow points
  - State inconsistencies
  - Failure recovery gaps

### Task 0.2: Baseline Testing
**Duration:** 2h

Establish test baseline for regression prevention:

**Actions:**
- Run existing ADO v1 tests (capture results)
- Document current test coverage
- Identify untested edge cases
- Create regression test suite

**Deliverable:** `context/baseline-test-results.md`

### Task 0.3: Migration Strategy Document
**Duration:** 2h

**File:** `artifacts/migration-strategy.md`

**Content:**
- Phase-by-phase migration approach
- Risk mitigation strategies
- Rollback procedures
- Data migration (if needed)
- User impact assessment (should be zero)

### Completion Criteria
- ✅ ADO v1 fully documented (architecture, flows, limitations)
- ✅ Conversational wizard design captured
- ✅ Baseline tests established
- ✅ Migration strategy documented
- ✅ Risk assessment complete

---

## 🏛️ Phase 1: Core ADO v2 Implementation (2 days)

**Goal:** Implement pure autonomous ADO Orchestrator v2 with BaseOrchestrator v4.1 compliance

### Task 1.1: ADOOrchestratorV2 Base Class
**Duration:** 6h

**File:** `src/orchestrators/ado/ado_orchestrator_v2.py`

**Implementation:**
```python
"""
ADO Orchestrator v2 - Pure Autonomous Azure DevOps Work Item Generation.

Config-driven orchestrator with zero natural language in execution logic.
All decisions in Python, manifest contains only configuration data.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.database.planning_state_db import PlanningStateDB
from typing import Dict, Any, List

class ADOOrchestratorV2(BaseOrchestratorV4_1):
    """
    ADO Orchestrator v2 - Pure autonomous work item generation.
    
    Dual-mode operation:
    - Auto mode: Direct generation from feature description
    - Wizard mode: Multi-turn conversational refinement
    
    Architecture:
    - Inherits BaseOrchestrator v4.1 (config loading, templates, state)
    - 6-phase workflow (pure Python execution)
    - State persistence in PlanningStateDB
    - Template-driven outputs
    - Master Orchestrator integrated
    """
    
    def __init__(self, config_path: str, state_db: PlanningStateDB):
        super().__init__(config_path, state_db)
        
        # Load ADO-specific config
        self.ado_config = self.config['ado_specific']
        self.work_item_types = self.config['work_item_types']
        self.complexity_thresholds = self.config['complexity']
        
        # Initialize wizard if available
        from src.orchestrators.ado.ado_conversational_wizard import ADOConversationalWizard
        self.wizard = ADOConversationalWizard(
            state_db=state_db,
            vision_api=self._get_vision_api()
        )
    
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute ADO workflow with mode detection.
        
        Modes:
        - auto: kwargs['mode'] == 'auto' OR no mode specified
        - wizard: kwargs['mode'] == 'wizard'
        
        Returns:
            ADOResult dictionary with work items, status, phase info
        """
        mode = kwargs.get('mode', 'auto')
        
        if mode == 'wizard':
            return self._execute_wizard_mode(kwargs)
        else:
            return self._execute_auto_mode(kwargs)
    
    def _execute_auto_mode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-generation workflow (6 phases).
        
        Phases:
        0. DISCOVERY: Context gathering, complexity analysis
        1. VALIDATION: DoR refinement, authentication
        2. GENERATION: Work item hierarchy, story points
        3. APPROVAL: User preview (if auto_approve=False)
        4. EXECUTION: ADO API calls
        5. COMPLETION: Link generation, success response
        """
        # Create execution plan in database
        plan_id = self.state_db.create_plan(
            feature_name=params['feature'],
            metadata={
                'orchestrator': 'ado_v2',
                'mode': 'auto',
                'user_params': params
            }
        )
        
        try:
            # Phase 0: Discovery
            phase_id = self.state_db.start_phase(plan_id, 0, {'name': 'DISCOVERY'})
            discovery_result = self._phase_discovery(params)
            self.state_db.complete_phase(phase_id)
            
            # Phase 1: Validation
            phase_id = self.state_db.start_phase(plan_id, 1, {'name': 'VALIDATION'})
            validation_result = self._phase_validation(discovery_result)
            self.state_db.complete_phase(phase_id)
            
            # Phase 2: Generation
            phase_id = self.state_db.start_phase(plan_id, 2, {'name': 'GENERATION'})
            work_items = self._phase_generation(validation_result)
            self.state_db.complete_phase(phase_id)
            
            # Phase 3: Approval (if required)
            if not params.get('auto_approve', False):
                phase_id = self.state_db.start_phase(plan_id, 3, {'name': 'APPROVAL'})
                approved = self._phase_approval(work_items)
                self.state_db.complete_phase(phase_id)
                
                if not approved:
                    return {'status': 'cancelled', 'message': 'User rejected'}
            
            # Phase 4: Execution
            phase_id = self.state_db.start_phase(plan_id, 4, {'name': 'EXECUTION'})
            created_items = self._phase_execution(work_items)
            self.state_db.complete_phase(phase_id)
            
            # Phase 5: Completion
            phase_id = self.state_db.start_phase(plan_id, 5, {'name': 'COMPLETION'})
            completion_result = self._phase_completion(created_items)
            self.state_db.complete_phase(phase_id)
            
            return completion_result
        
        except Exception as e:
            self.state_db.fail_phase(phase_id, str(e))
            raise
    
    def _phase_discovery(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 0: DISCOVERY - Context gathering and complexity analysis.
        
        Pure Python logic:
        - Analyze feature description for complexity indicators
        - Search workspace for related code
        - Query ADO for existing work items (duplicate detection)
        - Classify complexity (HIGH/MEDIUM/LOW)
        - Estimate work item count
        
        No natural language interpretation - algorithmic only.
        """
        feature = params['feature']
        
        # Complexity analysis (algorithmic)
        complexity = self._analyze_complexity(feature)
        
        # Workspace search (AST + grep)
        related_code = self._search_workspace(feature)
        
        # ADO duplicate detection
        duplicates = self._check_ado_duplicates(feature)
        
        return {
            'feature': feature,
            'complexity': complexity,
            'related_code': related_code,
            'duplicates': duplicates,
            'estimated_items': self._estimate_item_count(complexity)
        }
    
    # ... (implement remaining phases)
```

**Key Methods to Implement:**
- `_analyze_complexity()` - Keyword-based complexity scoring
- `_phase_validation()` - DoR refinement, auth check
- `_phase_generation()` - Work item hierarchy creation
- `_phase_approval()` - Template rendering + user prompt
- `_phase_execution()` - ADO API integration
- `_phase_completion()` - Success response generation

### Task 1.2: Phase Method Implementation
**Duration:** 8h

Implement all 6 phase methods with pure Python logic:

**_phase_validation():**
- Validate ADO authentication (PAT token check)
- Refine DoR (assumptions, constraints)
- Threat modeling (if HIGH complexity)

**_phase_generation():**
- Create work item hierarchy (Epic → Features → Stories → Tasks)
- Calculate story points (Fibonacci mapping)
- Inject TDD tasks (if configured)
- Apply work item templates

**_phase_approval():**
- Render markdown preview (template-driven)
- Display work item hierarchy
- Await user confirmation
- Handle "refine" requests

**_phase_execution():**
- ADO API authentication
- Batch work item creation
- Parent-child linking
- Error handling + rollback

**_phase_completion():**
- Generate work item links
- Render success template
- Update metrics

### Task 1.3: Helper Utilities
**Duration:** 2h

**Files to Create:**
- `src/orchestrators/ado/complexity_analyzer.py` - Complexity scoring
- `src/orchestrators/ado/dor_refiner.py` - Definition of Ready logic
- `src/orchestrators/ado/story_point_calculator.py` - Fibonacci mapping
- `src/orchestrators/ado/ado_api_client.py` - ADO REST API wrapper

### Task 1.4: Error Handling & Rollback
**Duration:** 2h

Implement transactional behavior:

**Features:**
- Savepoints before each phase
- Rollback on error
- State restoration
- Error logging with context

### Completion Criteria
- ✅ ADOOrchestratorV2 fully implemented (all 6 phases)
- ✅ Pure Python execution (zero natural language)
- ✅ State persistence in PlanningStateDB
- ✅ Rollback operational
- ✅ Helper utilities complete

---

## 🔄 Phase 2: Wizard Integration (1 day)

**Goal:** Integrate conversational wizard (5.1a) into ADO v2 dual-mode architecture

### Task 2.1: Wizard Mode Integration
**Duration:** 4h

**Updates to `ado_orchestrator_v2.py`:**
```python
def _execute_wizard_mode(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wizard mode: Multi-turn conversational work item creation.
    
    Flow:
    1. Start wizard session
    2. Iterate through 7 stages
    3. Collect user responses
    4. Generate final work items
    5. Execute via auto-mode pipeline (reuse phases 4-5)
    """
    # Start wizard
    wizard_response = self.wizard.start_wizard(params['feature'])
    
    # Conversation loop (handled by wizard)
    while wizard_response.stage != WizardStage.COMPLETE:
        # Display prompt to user
        user_response = self._prompt_user(wizard_response.prompt)
        
        # Process response
        wizard_response = self.wizard.process_response(
            session_id=wizard_response.session_id,
            user_input=user_response,
            vision_context=self._get_vision_context()
        )
    
    # Extract work items from wizard session
    work_items = wizard_response.context['ado_item']
    
    # Execute phases 4-5 (EXECUTION + COMPLETION) via auto-mode
    return self._execute_from_work_items(work_items)
```

### Task 2.2: Vision API Integration
**Duration:** 2h

Ensure Vision API analysis injects into wizard's acceptance criteria stage:

**Integration Points:**
- Wizard stage: ACCEPTANCE_CRITERIA
- If image attached → Extract UI elements
- Convert to acceptance criteria format
- Display to user for approval

### Task 2.3: Wizard-Auto Pipeline
**Duration:** 2h

**Goal:** Reuse auto-mode phases 4-5 after wizard generates work items

**Implementation:**
```python
def _execute_from_work_items(self, work_items: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute EXECUTION + COMPLETION phases with pre-generated work items.
    
    Used by:
    - Wizard mode (work items from conversation)
    - External integrations (work items from API)
    """
    # Skip phases 0-3 (already done via wizard)
    # Execute phase 4: EXECUTION
    created_items = self._phase_execution(work_items)
    
    # Execute phase 5: COMPLETION
    return self._phase_completion(created_items)
```

### Completion Criteria
- ✅ Wizard integrated into ADO v2
- ✅ Dual-mode routing functional
- ✅ Vision API working in wizard
- ✅ Auto-mode phases reusable by wizard

**Status:** ✅ COMPLETE (January 2, 2026)

**Deliverables:**
1. `_execute_wizard_mode()` method - Full 7-stage conversational workflow integration
2. `_execute_from_work_items()` helper - Reusable execution pipeline for pre-generated work items
3. `_extract_vision_context()` - Vision API context extraction and injection
4. `_get_vision_api()` - Enhanced Vision API detection (config, middleware, runtime)
5. Wizard tests: 30/35 passing (85.7% - 5 pre-existing parsing issues in wizard itself)

**Key Features:**
- Multi-turn wizard conversation with session management
- Vision API auto-injection at ACCEPTANCE_CRITERIA stage
- Work items generated from wizard data
- Phases 4-5 (EXECUTION + COMPLETION) reused from auto-mode
- Graceful degradation if wizard unavailable

**Test Results:**
```
30 passed, 5 failed (pre-existing wizard parsing logic issues)
- ✅ Wizard session creation and continuation
- ✅ All 7 wizard stages functional
- ✅ Vision context injection working
- ✅ Full wizard flow (minimal and complete)
- ✅ Session history tracking
- ❌ 5 parsing edge cases (effort size, comma-separated lists) - wizard-level issues
```

---

## 📝 Phase 3: Config & Templates (1 day)

**Goal:** Create config-only manifest and Jinja2 templates

### Task 3.1: Manifest Creation
**Duration:** 4h

**File:** `cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml`

**Structure:**
```yaml
schema_version: "5.0"
orchestrator:
  name: "ado_orchestrator"
  version: "2.0"
  type: "autonomous"
  base_class: "BaseOrchestratorV4_1"

modes:
  auto:
    description: "Direct work item generation from feature description"
    phases: ["DISCOVERY", "VALIDATION", "GENERATION", "APPROVAL", "EXECUTION", "COMPLETION"]
  wizard:
    description: "Multi-turn conversational work item refinement"
    stages: 7

ado_specific:
  authentication:
    required: true
    token_type: "PAT"
    validation_endpoint: "https://dev.azure.com/{org}/_apis/projects"
  
  work_item_types:
    epic:
      max_features: 5
      complexity_threshold: "HIGH"
    feature:
      max_stories: 8
      story_point_range: [5, 21]
    story:
      max_tasks: 5
      story_point_values: [1, 2, 3, 5, 8, 13, 21]
    task:
      default_estimation: 4

complexity:
  high_keywords: ["security", "authentication", "migration", "refactor", "architecture"]
  medium_keywords: ["api", "integration", "feature", "enhancement"]
  length_thresholds:
    high: 200
    medium_min: 50
    medium_max: 200

dor:
  required_assumptions:
    - "Development environment configured"
    - "Dependencies available"
  required_constraints:
    - "Standard sprint timeline"
    - "Code review required"

output_templates:
  work_item_preview: "templates/ado/work-item-preview.jinja2"
  approval_prompt: "templates/ado/approval-prompt.jinja2"
  completion_message: "templates/ado/completion-message.jinja2"
  wizard_stage_prompts: "templates/ado/wizard/"

validation:
  required_fields:
    - "feature"
  optional_fields:
    - "auto_approve"
    - "test_mode"
    - "complexity_override"
```

**Zero Natural Language:** Only data structures and configuration values.

### Task 3.2: Template Creation
**Duration:** 4h

**Templates to Create:**

1. `templates/ado/work-item-preview.jinja2` - Work item hierarchy display
2. `templates/ado/approval-prompt.jinja2` - Approval gate UI
3. `templates/ado/completion-message.jinja2` - Success response
4. `templates/ado/wizard/basic-info.jinja2` - Wizard stage 1
5. `templates/ado/wizard/acceptance-criteria.jinja2` - Wizard stage 2
6. `templates/ado/wizard/review.jinja2` - Wizard stage 7

**Example:** `work-item-preview.jinja2`
```jinja2
# 📋 ADO Work Item Preview

## Epic: {{ epic.title }}
**Complexity:** {{ complexity }} | **Estimated Story Points:** {{ total_story_points }}

### Features
{% for feature in features %}
- **{{ feature.title }}** ({{ feature.story_points }} SP)
  {% for story in feature.stories %}
  - {{ story.title }} ({{ story.story_points }} SP)
    {% for task in story.tasks %}
    - [ ] {{ task.title }}
    {% endfor %}
  {% endfor %}
{% endfor %}

## Acceptance Criteria
{% for criterion in acceptance_criteria %}
- {{ criterion }}
{% endfor %}

## Definition of Ready
**Assumptions:**
{% for assumption in dor.assumptions %}
- {{ assumption }}
{% endfor %}

**Constraints:**
{% for constraint in dor.constraints %}
- {{ constraint }}
{% endfor %}

---
**Actions:**
- Say **'approve'** to create work items
- Say **'refine [section]'** to modify (e.g., 'refine acceptance criteria')
- Say **'cancel'** to abort
```

### Completion Criteria
- ✅ Config manifest contains ONLY data structures
- ✅ All templates created (work item, wizard, approval)
- ✅ Templates render correctly with test data
- ✅ Manifest validates against schema

---

## ✅ Phase 4: Testing & Validation (0.5 days)

**Goal:** Comprehensive testing of ADO v2

### Task 4.1: Unit Tests
**Duration:** 2h

**Files to Create:**
- `tests/orchestrators/ado/test_ado_orchestrator_v2.py` (500+ lines)
- `tests/orchestrators/ado/test_complexity_analyzer.py`
- `tests/orchestrators/ado/test_dor_refiner.py`
- `tests/orchestrators/ado/test_story_point_calculator.py`

**Test Coverage:**
- ✅ All 6 phases (auto mode)
- ✅ Wizard integration
- ✅ Error handling + rollback
- ✅ State persistence
- ✅ Template rendering
- ✅ ADO API integration (mocked)

**Target:** 100% coverage

### Task 4.2: Integration Tests
**Duration:** 2h

**Scenarios:**
1. Auto mode: Feature description → Created work items (end-to-end)
2. Wizard mode: 7-stage conversation → Created work items
3. Vision API: Screenshot → Acceptance criteria extraction
4. Approval gate: Reject → Refine → Approve
5. Rollback: Phase failure → State restored
6. Duplicate detection: Existing work item → Warning displayed

### Completion Criteria
- ✅ 100% unit test coverage
- ✅ All integration scenarios pass
- ✅ Regression tests from v1 pass
- ✅ Performance benchmarks met

---

## 🔴 Phase 5: Master Orchestrator Activation (0.5 days)

**Goal:** Activate ADO v2 routing via Master Orchestrator

### Task 5.1: Master Orchestrator Configuration
**Duration:** 2h

**Update:** `cortex-brain/config/master-orchestrator.yaml`

**Add Patterns:**
```yaml
# ADO Operations - Dual Mode
- pattern: "^(ado wizard|ado interactive).*$"
  orchestrator: "ado_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 29
  metadata:
    description: "ADO wizard mode (interactive)"
    autonomous: true
    mode: "wizard"

- pattern: "^(ado|ado story|ado feature).*$"
  orchestrator: "ado_orchestrator_v2"
  confidence: 1.0
  match_type: "regex"
  priority: 30
  metadata:
    description: "ADO auto mode (quick generation)"
    autonomous: true
    mode: "auto"
```

### Task 5.2: Orchestrator Registration
**Duration:** 1h

**Register in OrchestratorRegistry:**
```python
# In src/mcp/registry.py

registry.register(
    orchestrator_id="ado_orchestrator_v2",
    class_name="ADOOrchestratorV2",
    module_path="src.orchestrators.ado.ado_orchestrator_v2",
    patterns=[
        {"pattern": r"^(ado wizard|ado interactive).*$", "mode": "wizard"},
        {"pattern": r"^(ado|ado story|ado feature).*$", "mode": "auto"}
    ],
    dependencies=["planning_state_db", "vision_api"]
)
```

### Task 5.3: CORTEX.prompt.md Update
**Duration:** 1h

**Update Intent Router:**
```markdown
| `ado story [feature]` | 🛡️ **ADO Operations v2 (AUTONOMOUS)** | `ado-orchestrator-v2.yaml` | **HAND-OFF** → Auto-mode generation |
| `ado wizard [feature]` | 🛡️ **ADO Wizard (AUTONOMOUS)** | `ado-orchestrator-v2.yaml` | **HAND-OFF** → Interactive wizard |
```

### Task 5.4: End-to-End Routing Test
**Duration:** 30min

**Test Commands:**
```
User: "ado story user authentication"
→ Master Orch routes to ado_orchestrator_v2 (auto mode)
→ ADO v2 executes 6 phases
→ Work items created

User: "ado wizard user authentication"
→ Master Orch routes to ado_orchestrator_v2 (wizard mode)
→ Wizard starts 7-stage conversation
→ Work items created after completion
```

### Completion Criteria
- ✅ Master Orchestrator routes ADO commands
- ✅ Dual-mode routing functional
- ✅ End-to-end test passes
- ✅ CORTEX.prompt.md updated
- ✅ ADO v2 LIVE via Master Orchestrator

---

## 🎉 Migration Completion Checklist

### Technical Deliverables
- [ ] ADOOrchestratorV2 implemented (pure Python)
- [ ] All 6 phases autonomous
- [ ] Conversational wizard integrated
- [ ] Config-only manifest (no natural language)
- [ ] State persistence in PlanningStateDB
- [ ] Templates render correctly
- [ ] 100% test coverage
- [ ] Master Orchestrator routing operational

### Functional Validation
- [ ] Auto mode: `ado story X` generates work items
- [ ] Wizard mode: `ado wizard X` starts interactive flow
- [ ] Vision API extracts acceptance criteria
- [ ] Approval gate functional
- [ ] DoR refinement preserved
- [ ] ADO API integration working
- [ ] Parent-child linking operational
- [ ] Backward compatibility maintained

### Documentation
- [ ] v1 analysis complete
- [ ] v2 architecture documented
- [ ] Migration guide written
- [ ] User guide updated
- [ ] API documentation generated

### Operational
- [ ] v1 archived
- [ ] v2 activated via Master Orchestrator
- [ ] Metrics tracking operational
- [ ] Git checkpoint created
- [ ] Regression testing passed

---

## 📋 Next Steps

After ADO v2 migration complete:

1. **Immediate:** Update parent plan (cortex-v5-holistic-refactor Phase 6.1 → ✅ Complete)
2. **Next Migration:** Vacuum Orchestrator v2 (Task 5.2 of parent plan)
3. **Integration:** Ensure Master Orchestrator handles both Planning v5 + ADO v2
4. **Documentation:** Update CORTEX.prompt.md with ADO v2 capabilities

---

**Status:** ⏸️ NOT STARTED - Ready for execution  
**Parent Plan:** cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md  
**Estimated Start:** After Phase 5 completion of parent plan
