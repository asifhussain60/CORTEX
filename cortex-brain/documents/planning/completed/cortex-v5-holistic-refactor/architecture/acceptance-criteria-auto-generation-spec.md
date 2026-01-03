# 🎯 Acceptance Criteria Auto-Generation - Feature Specification

**Feature:** Automatic Acceptance Criteria Generation in Planning and ADO Orchestrators  
**Created:** January 2, 2026  
**Status:** ✅ SPECIFICATION COMPLETE - Ready for Implementation  
**Priority:** HIGH - Core Planning/ADO Feature  

---

## 📋 Overview

**Problem:** Plans and ADO work items are created without formalized, testable acceptance criteria, making final validation subjective and inconsistent.

**Solution:** Automatically generate comprehensive, granular acceptance criteria during plan/work item creation that maps to SKULL rules and orchestrator requirements.

**Impact:**
- **Plans:** Every generated plan includes linked acceptance criteria for final validation
- **ADO Work Items:** Every work item includes testable acceptance criteria
- **Validation:** Objective, measurable pass/fail conditions for all work
- **Quality:** Ensures SKULL compliance and orchestrator requirements are testable

---

## 🎯 Acceptance Criteria for This Feature (Meta!)

| ID | Criterion | Pass Condition |
|----|-----------|----------------|
| **AC-1** | Planning v5 generates acceptance criteria artifact | `artifacts/final-acceptance-criteria-link.md` created |
| **AC-2** | ADO Orchestrator includes acceptance criteria in work items | Work item has ≥3 testable criteria |
| **AC-3** | Criteria mapped to SKULL rules | Each criterion references brain-protection-rules.yaml |
| **AC-4** | Final phase validation runs against criteria | Script `generate_acceptance_report.py` exists |
| **AC-5** | Criteria stored in plan structure | Phase 10/Final includes validation task |

---

## 🏗️ Architecture

### Component 1: Planning System v5 Integration

**File:** `src/orchestrators/planning/acceptance_criteria_generator.py`

**Class:** `AcceptanceCriteriaGenerator`

**Responsibilities:**
1. Analyze plan phases and extract orchestrators involved
2. Map orchestrators to acceptance criteria sections
3. Extract applicable SKULL rules from plan context
4. Generate plan-specific acceptance criteria document
5. Link to master acceptance criteria document

**Integration Point:** Called during `PlanningOrchestrator.generate_plan()` after phases are finalized

### Component 2: ADO Operations Integration

**File:** `src/orchestrators/ado/work_item_acceptance_generator.py`

**Class:** `WorkItemAcceptanceGenerator`

**Responsibilities:**
1. Analyze user story/feature description
2. Generate ≥3 testable acceptance criteria
3. Map to relevant SKULL rules if applicable
4. Format for ADO work item structure
5. Include DoR and DoD checklists

**Integration Point:** Called during `ADOOrchestrator.generate_work_item()` after story creation

### Component 3: Validation Script

**File:** `scripts/generate_acceptance_report.py`

**Responsibilities:**
1. Read plan acceptance criteria
2. Execute relevant test suites
3. Match test results to criteria IDs
4. Generate pass/fail report
5. Output final acceptance report

---

## 📐 Design Specification

### Planning System v5: Acceptance Criteria Generation

#### 1. Orchestrator Detection

```python
def extract_orchestrators(phases: List[Dict[str, Any]]) -> List[str]:
    """
    Extract unique orchestrators from plan phases.
    
    Args:
        phases: List of phase dictionaries with tasks
    
    Returns:
        List of orchestrator IDs (e.g., ['planning_orchestrator', 'tdd_orchestrator'])
    """
    orchestrators = set()
    
    for phase in phases:
        for task in phase.get('tasks', []):
            # Check task metadata for orchestrator hints
            if 'orchestrator' in task:
                orchestrators.add(task['orchestrator'])
            
            # Infer from task patterns
            if 'tdd' in task.get('title', '').lower():
                orchestrators.add('tdd_orchestrator')
            if 'ado' in task.get('title', '').lower():
                orchestrators.add('ado_orchestrator')
    
    return list(orchestrators)
```

#### 2. SKULL Rule Extraction

```python
def extract_skull_rules(plan_data: Dict[str, Any]) -> List[str]:
    """
    Extract applicable SKULL rules from plan context.
    
    Args:
        plan_data: Complete plan data dictionary
    
    Returns:
        List of SKULL rule IDs (e.g., ['TDD_ENFORCEMENT', 'GIT_ISOLATION'])
    """
    rules = set()
    
    # Always enforce core rules
    rules.update([
        'TDD_ENFORCEMENT',
        'HOLISTIC_DISCOVERY',
        'REFACTOR_CODE_CLEANUP_ENFORCEMENT',
        'GIT_ISOLATION_ENFORCEMENT'
    ])
    
    # Add rule based on plan type
    if plan_data.get('complexity') in ['TIER_4', 'TIER_5']:
        rules.add('KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT')
    
    # Add rule if AST scanning involved
    if any('ast' in phase.get('name', '').lower() for phase in plan_data.get('phases', [])):
        rules.add('HOLISTIC_CODE_DISCOVERY_ENFORCEMENT')
    
    return list(rules)
```

#### 3. Criteria Mapping

```python
# Orchestrator → Acceptance Criteria Section Mapping
ORCHESTRATOR_CRITERIA_MAP = {
    'master_orchestrator': 'Section 1',
    'planning_orchestrator': 'Section 2',
    'tdd_orchestrator': 'Section 3',
    'ado_orchestrator': 'Section 4',
    'vacuum_orchestrator': 'Section 5',
    'refinement_orchestrator': 'Section 6',
    'debug_orchestrator': 'Section 7',
    'cortex_lens': 'Section 8'
}

# SKULL Rule → Acceptance Criteria Section Mapping
SKULL_RULE_SECTION_MAP = {
    'GIT_ISOLATION_ENFORCEMENT': 'Section 9.1',
    'DOCUMENT_ORGANIZATION_ENFORCEMENT': 'Section 9.2',
    'TDD_ENFORCEMENT': 'Section 9.3',
    'KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT': 'Section 9.4',
    'REFACTOR_CODE_CLEANUP_ENFORCEMENT': 'Section 9.5'
}
```

#### 4. Criteria ID Retrieval

```python
def get_criteria_for_orchestrator(orchestrator_id: str) -> List[str]:
    """
    Get acceptance criteria IDs for specific orchestrator.
    
    Args:
        orchestrator_id: Orchestrator identifier
    
    Returns:
        List of criterion IDs (e.g., ['MO-1.1.1', 'MO-1.2.1'])
    """
    # Load master acceptance criteria
    criteria_doc = load_acceptance_criteria_document()
    
    # Parse section for orchestrator
    section = ORCHESTRATOR_CRITERIA_MAP.get(orchestrator_id)
    if not section:
        return []
    
    # Extract criterion IDs from section
    criterion_ids = parse_criterion_ids_from_section(criteria_doc, section)
    
    return criterion_ids
```

#### 5. Document Generation

```python
def generate_acceptance_criteria_document(
    plan_id: str,
    orchestrators: List[str],
    skull_rules: List[str],
    plan_data: Dict[str, Any]
) -> str:
    """
    Generate plan-specific acceptance criteria document.
    
    Args:
        plan_id: Plan identifier
        orchestrators: List of orchestrators involved
        skull_rules: List of applicable SKULL rules
        plan_data: Complete plan data
    
    Returns:
        Markdown content for acceptance criteria document
    """
    sections = [
        "# 🎯 Final Acceptance Criteria - Plan Integration",
        f"**Plan ID:** {plan_id}",
        f"**Created:** {datetime.now().strftime('%B %d, %Y')}",
        "",
        "## 📋 Acceptance Criteria Reference",
        f"**Primary Document:** [`cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md`](../../FINAL-ACCEPTANCE-CRITERIA.md)",
        "",
        "## 🎯 Plan-Specific Acceptance Criteria",
        ""
    ]
    
    # Add orchestrator criteria
    if orchestrators:
        sections.append("### Orchestrator Requirements")
        sections.append("")
        sections.append("| Criterion ID | Component | Requirement | Reference |")
        sections.append("|--------------|-----------|-------------|-----------|")
        
        for orch_id in orchestrators:
            section_ref = ORCHESTRATOR_CRITERIA_MAP.get(orch_id)
            criteria_ids = get_criteria_for_orchestrator(orch_id)
            
            for criterion_id in criteria_ids[:3]:  # Top 3 criteria per orchestrator
                criterion = get_criterion_details(criterion_id)
                sections.append(
                    f"| **{criterion_id}** | {orch_id} | {criterion['requirement']} | {section_ref} |"
                )
        
        sections.append("")
    
    # Add SKULL rule criteria
    if skull_rules:
        sections.append("### SKULL Rule Compliance")
        sections.append("")
        sections.append("| Criterion ID | Rule | Requirement | Reference |")
        sections.append("|--------------|------|-------------|-----------|")
        
        for rule_id in skull_rules:
            section_ref = SKULL_RULE_SECTION_MAP.get(rule_id)
            criteria_ids = get_criteria_for_skull_rule(rule_id)
            
            for criterion_id in criteria_ids[:2]:  # Top 2 criteria per rule
                criterion = get_criterion_details(criterion_id)
                sections.append(
                    f"| **{criterion_id}** | {rule_id} | {criterion['requirement']} | {section_ref} |"
                )
        
        sections.append("")
    
    # Add test execution plan
    sections.extend([
        "## 🧪 Test Execution Plan",
        "",
        "```bash",
        f"# Run acceptance criteria validation",
        f"python scripts/generate_acceptance_report.py \\",
        f"  --plan-id {plan_id} \\",
        f"  --criteria cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md \\",
        f"  --output cortex-brain/documents/planning/active/{plan_id}/reports/final-acceptance-report.md",
        "```",
        ""
    ])
    
    return "\n".join(sections)
```

### ADO Orchestrator: Acceptance Criteria Generation

#### 1. Story Analysis

```python
def analyze_user_story(story_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user story to extract acceptance criteria inputs.
    
    Args:
        story_data: User story with title, description, as-a-want-so-that
    
    Returns:
        Analysis results with key entities, actions, constraints
    """
    analysis = {
        'entities': [],      # Nouns (user, system, data)
        'actions': [],       # Verbs (login, create, validate)
        'constraints': [],   # Requirements (secure, fast, accessible)
        'scenarios': []      # Test scenarios
    }
    
    # Extract from "As a... I want... So that..."
    if 'as_a' in story_data:
        analysis['entities'].append(story_data['as_a'])
    
    if 'i_want' in story_data:
        # Parse verbs and objects from "I want to X"
        actions = extract_actions(story_data['i_want'])
        analysis['actions'].extend(actions)
    
    if 'so_that' in story_data:
        # Parse constraints from "So that Y"
        constraints = extract_constraints(story_data['so_that'])
        analysis['constraints'].extend(constraints)
    
    return analysis
```

#### 2. Criteria Generation

```python
def generate_acceptance_criteria(
    story_data: Dict[str, Any],
    analysis: Dict[str, Any]
) -> List[str]:
    """
    Generate testable acceptance criteria for work item.
    
    Args:
        story_data: User story data
        analysis: Story analysis results
    
    Returns:
        List of acceptance criteria (≥3 items)
    """
    criteria = []
    
    # Generate criteria from actions
    for action in analysis['actions']:
        criteria.append(f"{analysis['entities'][0]} can {action}")
    
    # Generate criteria from constraints
    for constraint in analysis['constraints']:
        criteria.append(f"System meets {constraint} requirement")
    
    # Generate edge case criteria
    if len(criteria) < 3:
        criteria.append("Error handling works for invalid inputs")
        criteria.append("Success message displayed on completion")
    
    # Add SKULL-related criteria if applicable
    if 'authentication' in story_data.get('feature_name', '').lower():
        criteria.append("Follows SECURITY_AUTHENTICATION rule (OWASP compliant)")
    
    return criteria[:5]  # Max 5 criteria
```

#### 3. DoR/DoD Generation

```python
def generate_definition_of_ready(story_data: Dict[str, Any]) -> List[str]:
    """Generate Definition of Ready checklist."""
    return [
        "Requirements clarified with stakeholder",
        "Design mockups approved (if UI work)",
        "API contract defined (if backend work)",
        "Test scenarios documented",
        "Dependencies identified and available"
    ]

def generate_definition_of_done(story_data: Dict[str, Any]) -> List[str]:
    """Generate Definition of Done checklist."""
    dod = [
        "All acceptance criteria met",
        "Unit tests pass (RED→GREEN→REFACTOR)",
        "Integration tests pass",
        "Code reviewed and approved",
        "Documentation updated",
        "No SKULL rule violations"
    ]
    
    # Add task-specific DoD items
    if 'database' in story_data.get('description', '').lower():
        dod.append("Database migration tested")
    
    if 'api' in story_data.get('description', '').lower():
        dod.append("API documentation updated")
    
    return dod
```

---

## 📂 File Structure Integration

### Planning System v5 Output

```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md
├── context/
├── reports/
├── artifacts/
│   └── final-acceptance-criteria-link.md  ← NEW FILE
└── tracking/
    └── progress-tracker.json
```

**Content:** Links to master criteria document + plan-specific criteria table

### ADO Work Item Output

```yaml
work_item:
  title: "User Authentication"
  type: "User Story"
  description: "..."
  as_a: "user"
  i_want: "to log in securely"
  so_that: "my data is protected"
  
  acceptance_criteria:  ← NEW SECTION
    - "User can log in with email + password"
    - "Invalid credentials show error message"
    - "Session expires after 30 minutes"
  
  definition_of_ready:  ← NEW SECTION
    - "Requirements clarified"
    - "Design mockups approved"
    - "API contract defined"
  
  definition_of_done:  ← NEW SECTION
    - "All acceptance criteria met"
    - "Tests pass (RED→GREEN→REFACTOR)"
    - "Code reviewed"
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/orchestrators/planning/test_acceptance_criteria_generator.py`

```python
def test_extract_orchestrators():
    """Test orchestrator extraction from phases."""
    phases = [
        {'tasks': [{'orchestrator': 'planning_orchestrator'}]},
        {'tasks': [{'title': 'Run TDD tests'}]}
    ]
    
    orchestrators = extract_orchestrators(phases)
    
    assert 'planning_orchestrator' in orchestrators
    assert 'tdd_orchestrator' in orchestrators

def test_extract_skull_rules():
    """Test SKULL rule extraction."""
    plan_data = {
        'complexity': 'TIER_5',
        'phases': [{'name': 'AST Analysis'}]
    }
    
    rules = extract_skull_rules(plan_data)
    
    assert 'KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT' in rules
    assert 'HOLISTIC_CODE_DISCOVERY_ENFORCEMENT' in rules
```

### Integration Tests

**File:** `tests/integration/test_planning_acceptance_criteria.py`

```python
def test_plan_generation_includes_acceptance_criteria(temp_plan_folder):
    """Test that generated plans include acceptance criteria artifact."""
    orchestrator = PlanningOrchestratorV5(...)
    
    plan = orchestrator.generate_plan({
        'feature_name': 'User Authentication',
        'complexity': 'TIER_3'
    })
    
    # Check artifact exists
    criteria_file = temp_plan_folder / 'artifacts' / 'final-acceptance-criteria-link.md'
    assert criteria_file.exists()
    
    # Check content links to master document
    content = criteria_file.read_text()
    assert 'FINAL-ACCEPTANCE-CRITERIA.md' in content
    assert 'MO-' in content or 'PS-' in content  # Contains criterion IDs
```

---

## 📋 Implementation Checklist

### Phase 1: Core Implementation (4h)

- [ ] Create `AcceptanceCriteriaGenerator` class
- [ ] Implement `extract_orchestrators()`
- [ ] Implement `extract_skull_rules()`
- [ ] Create orchestrator/SKULL mapping constants
- [ ] Implement `generate_acceptance_criteria_document()`
- [ ] Write unit tests (20+ tests)

### Phase 2: Planning Integration (3h)

- [ ] Integrate into `PlanningOrchestratorV5.generate_plan()`
- [ ] Create artifact folder if missing
- [ ] Save criteria document to `artifacts/final-acceptance-criteria-link.md`
- [ ] Add Phase 10 task for validation
- [ ] Update copilot_instructions template
- [ ] Write integration tests (5+ tests)

### Phase 3: ADO Integration (4h)

- [ ] Create `WorkItemAcceptanceGenerator` class
- [ ] Implement `analyze_user_story()`
- [ ] Implement `generate_acceptance_criteria()`
- [ ] Implement DoR/DoD generators
- [ ] Integrate into `ADOOrchestrator.generate_work_item()`
- [ ] Write unit tests (15+ tests)

### Phase 4: Validation Script (3h)

- [ ] Create `scripts/generate_acceptance_report.py`
- [ ] Implement criteria document parser
- [ ] Implement test suite executor
- [ ] Implement report generator
- [ ] Add CLI arguments (plan-id, criteria, output)
- [ ] Write script tests (10+ tests)

### Phase 5: Documentation (2h)

- [ ] Update Planning System v5 documentation
- [ ] Update ADO Orchestrator documentation
- [ ] Create usage examples
- [ ] Update CORTEX.prompt.md with acceptance criteria feature
- [ ] Add to orchestrator capability lists

---

## 🎯 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Plan Coverage | 100% | All plans include acceptance criteria artifact |
| ADO Coverage | 100% | All work items include ≥3 acceptance criteria |
| Criterion Relevance | ≥90% | Manual review shows criteria are applicable |
| Validation Adoption | ≥80% | Plans actually run validation script in Phase 10 |
| Test Pass Rate | ≥95% | Plans meet acceptance criteria on first validation |

---

## 📚 References

- **Master Criteria Document:** `cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md`
- **Planning System v5 Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **ADO Orchestrator Manifest:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`

---

**Status:** Ready for implementation in Phase 5.1a (ADO Wizard Enhancement) of v5 holistic refactor plan.
