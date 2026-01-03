# 🧱 Response Template Lego System - Master Plan

**Plan ID:** response-template-lego-system  
**Feature:** Modular, composable response templates with visual progress bars for all autonomous orchestrators  
**Created:** January 3, 2026  
**Complexity:** TIER 4 (ARCHITECTURAL)  
**Strategy:** Build reusable template components (Lego pieces) that orchestrators compose based on execution context  
**Estimated Duration:** 3 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Architecture Design | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 1 | Template Audit | `░░░░░░░░░░` | 2h | ⏸️ Not Started |
| 2 | Component Library | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 3 | Orchestrator Templates | `░░░░░░░░░░` | 6h | ⏸️ Not Started |
| 4 | Progress Bar System | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 5 | Template Renderer | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 6 | Orchestrator Integration | `░░░░░░░░░░` | 8h | ⏸️ Not Started |
| 7 | Testing | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 8 | Documentation | `░░░░░░░░░░` | 2h | ⏸️ Not Started |
| 9 | Toolkit Orchestrator | `░░░░░░░░░░` | 6h | ⏸️ Not Started |

**Total Estimated Time:** 44 hours (~6 days)

---

## 🎯 Objective

Create a modular response template system where:
1. **Each orchestrator has custom templates** (like specialized Lego sets)
2. **Shared components are reusable** (like standard Lego bricks)
3. **Visual progress bars match maintenance prompt** (full table start/end, concise interim updates)
4. **Display moments control output** (start/interim/end)
5. **Single Action Rule enforced** (exactly one next step)

---

## 🏗️ Architecture Principles

### 1. Lego-Piece Philosophy

**Components = Lego Bricks**
- Small, single-purpose, reusable
- Parameterized for flexibility
- Composable into larger structures
- No duplication across orchestrators

**Templates = Lego Instructions**
- Define which components to use
- Specify assembly order
- Customize parameters per orchestrator
- Support multiple display moments

### 2. Display Moment Pattern (from Maintenance Prompt)

**Three Display Moments:**

**START (Beginning of Execution):**
```markdown
## 🛡️🧠 CORTEX Orchestrator Execution
**Author:** Asif Hussain | **Feature:** X | **Orchestrator:** Y

### 📊 Execution Progress

**Overall Progress:** `░░░░░░░░░░` **0%** ⏸️ STARTING

| # | Phase | Progress | Status |
|---|-------|----------|--------|
| 1 | ⏸️ **Phase 1** | `░░░░░░░░░░` 0% | Not Started |
| 2 | ⏸️ **Phase 2** | `░░░░░░░░░░` 0% | Not Started |
| 3 | ⏸️ **Phase 3** | `░░░░░░░░░░` 0% | Not Started |

**Next:** Begin Phase 1 (Feature analysis)
```

**INTERIM (After Each Phase):**
```markdown
✅ **Phase 1 Complete** - Feature analysis done (12 features identified, 3m 24s)

⏳ **Phase 2 Next** - Test generation (Expected: ~5 minutes)
```

**END (Completion):**
```markdown
## 🛡️🧠 CORTEX Orchestrator Execution Complete
**Author:** Asif Hussain | **Feature:** X | **Orchestrator:** Y

### 📊 Final Progress

**Overall Progress:** `██████████` **100%** ✅ COMPLETE

| # | Phase | Progress | Status |
|---|-------|----------|--------|
| 1 | ✅ **Phase 1** | `██████████` 100% | Complete (3m 24s) |
| 2 | ✅ **Phase 2** | `██████████` 100% | Complete (5m 12s) |
| 3 | ✅ **Phase 3** | `██████████` 100% | Complete (2m 48s) |

### 📦 Artifacts Generated
- tests/test_auth.py (142 lines)
- src/auth.py (89 lines)
- docs/auth-guide.md

### ✅ Success Metrics
- 12 tests generated (100% coverage)
- All tests passing
- Zero warnings

**Next:** ✅ All work complete!
```

### 3. Component Categories

**Core Components (Always Used):**
- `header` - Orchestrator identification
- `overall_progress` - Top-level progress bar
- `next_action` - Single action rule enforcement

**Display Moment Components:**
- `phase_table_full` - Complete phase listing (start/end)
- `phase_update_interim` - Concise completed + next (interim)
- `summary_section` - Execution summary (end only)
- `artifacts_list` - Generated files (end only)

**Optional Components:**
- `validation_checks` - DoR/DoD validation
- `threat_analysis` - Security scanning results
- `work_item_summary` - ADO-specific work items
- `test_results` - TDD-specific test status

---

## 📋 Phase 0: Architecture Design

**Duration:** 4 hours

### Deliverables

1. **Architecture Document** (`architecture/response-template-architecture.md`)
   - Lego-piece philosophy explained
   - Display moment pattern documented
   - Component categories defined
   - Composition examples provided

2. **Component Specification** (`architecture/component-specification.yaml`)
   - Each component defined with:
     - Parameters (required/optional)
     - Display moments (start/interim/end/all)
     - Example usage
     - Dependencies

3. **Orchestrator Template Map** (`architecture/orchestrator-template-map.yaml`)
   - Matrix of orchestrators × components
   - Which components each orchestrator uses
   - Custom parameters per orchestrator
   - Display moment configurations

### Acceptance Criteria

- [ ] Architecture document complete
- [ ] Component specification covers all orchestrators
- [ ] Template map shows clear component reuse
- [ ] Display moment pattern documented with examples

---

## 📋 Phase 1: Template Audit

**Duration:** 2 hours

### Tasks

1. **Analyze `response-templates-v4.yaml`:**
   - Existing templates: `autonomous_execution_progress`, `ado_execution_progress`
   - Missing templates: TDD, Cleanup, Vacuum, Debug, Maintenance, Sanitization, Refinement
   - Shared patterns across templates
   - Duplication opportunities

2. **Review Maintenance Prompt:**
   - Progress bar implementation
   - Display moment switching
   - Interim update format
   - Final report structure

3. **Identify Component Candidates:**
   - Progress bars (overall, phase table, interim)
   - Headers (orchestrator-specific)
   - Status indicators (emoji, percentages)
   - Artifact lists
   - Validation sections
   - Next action formatters

### Deliverables

- **Audit Report** (`context/template-audit-report.md`)
  - Current template inventory
  - Duplication analysis
  - Component extraction opportunities
  - Migration complexity assessment

### Acceptance Criteria

- [ ] All existing templates documented
- [ ] Duplication identified and quantified
- [ ] Component candidates listed with reuse potential
- [ ] Migration complexity estimated

---

## 📋 Phase 2: Component Library

**Duration:** 4 hours

### Design: base-components.yaml Structure

```yaml
version: "1.0.0"
description: "Reusable Lego-piece components for response templates"

components:
  # ============================================================================
  # CORE COMPONENTS (Always Used)
  # ============================================================================
  
  header:
    display_moments: [start, end]
    parameters:
      orchestrator_name: {type: string, required: true}
      feature_name: {type: string, required: true}
      author: {type: string, default: "Asif Hussain"}
    template: |
      ## 🛡️🧠 CORTEX {{orchestrator_name}}
      **Author:** {{author}} | **Feature:** {{feature_name}} | **Orchestrator:** {{orchestrator_name}} ✅
  
  overall_progress_bar:
    display_moments: [start, interim, end]
    parameters:
      percentage: {type: number, required: true}
      status: {type: string, enum: [starting, in_progress, complete]}
    template: |
      **Overall Progress:** `{{progress_bar}}` **{{percentage}}%** {{status_emoji}} {{status_text}}
    helpers:
      - generate_progress_bar(percentage, width=20)
      - format_status_emoji(status)
      - format_status_text(status)
  
  next_action:
    display_moments: [start, interim, end]
    parameters:
      action: {type: string, required: true}
      benefit: {type: string, required: false}
    template: |
      **Next:** {{action}}{{#if benefit}} ({{benefit}}){{/if}}
    validation:
      single_action_rule: true
      forbidden_patterns: ["or", "either", "option"]
  
  # ============================================================================
  # DISPLAY MOMENT COMPONENTS
  # ============================================================================
  
  phase_table_full:
    display_moments: [start, end]
    parameters:
      phases: {type: array, required: true}
    template: |
      | # | Phase | Progress | Status |
      |---|-------|----------|--------|
      {{#each phases}}
      | {{phase_num}} | {{status_emoji}} **{{phase_name}}** | `{{phase_bar}}` {{percentage}}% | {{status_text}}{{#if elapsed_time}} ({{elapsed_time}}){{/if}} |
      {{/each}}
    helpers:
      - generate_phase_bars(phases)
      - format_phase_status(phase)
  
  phase_update_interim:
    display_moments: [interim]
    parameters:
      completed_phase: {type: object, required: true}
      next_phase: {type: object, required: true}
    template: |
      ✅ **{{completed_phase.name}} Complete** - {{completed_phase.summary}} ({{completed_phase.elapsed_time}})
      
      ⏳ **{{next_phase.name}} Next** - {{next_phase.description}}{{#if next_phase.estimated_time}} (Expected: ~{{next_phase.estimated_time}}){{/if}}
  
  summary_section:
    display_moments: [end]
    parameters:
      metrics: {type: object, required: true}
    template: |
      ### ✅ Success Metrics
      {{#each metrics}}
      - {{name}}: {{value}}
      {{/each}}
  
  artifacts_list:
    display_moments: [end]
    parameters:
      artifacts: {type: array, required: true}
    template: |
      ### 📦 Artifacts Generated
      {{#each artifacts}}
      - {{path}}{{#if lines}} ({{lines}} lines){{/if}}
      {{/each}}
  
  # ============================================================================
  # OPTIONAL COMPONENTS (Orchestrator-Specific)
  # ============================================================================
  
  validation_checks:
    display_moments: [end]
    parameters:
      dor_status: {type: object, required: true}
      dod_status: {type: object, required: true}
    template: |
      ### ✅ Validation Status
      
      | Check | Status |
      |-------|--------|
      | **Definition of Ready** | {{#if dor_status.passed}}✅ Passed{{else}}⚠️ {{dor_status.violations}} issue(s){{/if}} |
      | **Definition of Done** | {{#if dod_status.passed}}✅ Passed{{else}}⏳ {{dod_status.remaining}} remaining{{/if}} |
  
  work_item_summary:
    display_moments: [end]
    parameters:
      work_items: {type: object, required: true}
    template: |
      ### 🎫 Work Item Summary
      
      | Type | Count | Story Points | Status |
      |------|-------|--------------|--------|
      {{#each work_items}}
      | **{{type}}** | {{count}} | {{#if story_points}}{{story_points}} SP{{else}}-{{/if}} | {{status}} |
      {{/each}}
  
  test_results:
    display_moments: [interim, end]
    parameters:
      tests: {type: object, required: true}
    template: |
      ### 🧪 Test Results
      
      - **Passing:** {{tests.passing}}/{{tests.total}} ({{tests.pass_rate}}%)
      - **Coverage:** {{tests.coverage}}%
      - **Duration:** {{tests.duration}}
```

### Deliverables

1. **`cortex-brain/response-templates/base-components.yaml`**
   - All core components defined
   - Display moment specifications
   - Parameter schemas
   - Template markup
   - Helper function references

2. **Component Documentation** (`architecture/component-library.md`)
   - Usage guide for each component
   - Parameter descriptions
   - Display moment behavior
   - Composition examples

### Acceptance Criteria

- [ ] base-components.yaml created with 15+ components
- [ ] Each component has clear parameters and display moments
- [ ] Component documentation complete
- [ ] Components cover all orchestrator needs

---

## 📋 Phase 3: Orchestrator-Specific Templates

**Duration:** 6 hours

### Templates to Create

**1. Planning v5: `autonomous_planning_progress`** (Update existing)
- Components: header, overall_progress_bar, phase_table_full (start/end), phase_update_interim, validation_checks, artifacts_list, summary_section, next_action
- Custom: Plan file link, DoR/DoD checks
- Display moments: Full table start/end, interim updates between phases

**2. ADO v2: `ado_execution_progress`** (Update existing)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, work_item_summary, artifacts_list, next_action
- Custom: Work item counts, story points, hierarchy tracking
- Display moments: Full table start/end, interim with work item counts

**3. TDD v2: `tdd_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, test_results, artifacts_list, next_action
- Custom: RED/GREEN/REFACTOR phase indicators, test pass rate, coverage
- Display moments: Full table start (3 phases), interim after each phase, end with test metrics

**4. Cleanup v2: `cleanup_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: Files deleted, space freed, backup counts
- Display moments: Full table start (5 modes), interim per mode, end with space metrics

**5. Vacuum v2: `vacuum_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: 10 cleanup categories, duplicate detection, orphan files
- Display moments: Full table start (10 categories), interim per category, end with cleanup stats

**6. Debug: `debug_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: Error analysis, root cause identification, fix recommendations
- Display moments: Full table start (4 phases), interim diagnostics, end with fix summary

**7. Maintenance: `maintenance_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: 11-phase health check, issues found, auto-fixes applied
- Display moments: Match existing maintenance prompt exactly (11 phases)

**8. Sanitization: `sanitization_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: Sensitive data removed, placeholder generation, validation
- Display moments: Full table start (5 phases), interim per phase, end with sanitization report

**9. Refinement: `refinement_execution_progress`** (New)
- Components: header, overall_progress_bar, phase_table_full, phase_update_interim, artifacts_list, summary_section, next_action
- Custom: Code quality metrics, refactoring suggestions, optimization wins
- Display moments: Full table start (7 phases), interim per phase, end with quality report

### Template Structure Example (TDD v2)

```yaml
tdd_execution_progress:
  description: "TDD v2 execution with RED→GREEN→REFACTOR visual progress"
  orchestrator: "tdd_orchestrator_v2"
  
  display_moments:
    start:
      components:
        - header:
            orchestrator_name: "TDD Orchestrator v2"
            feature_name: "{{feature_name}}"
        - overall_progress_bar:
            percentage: 0
            status: "starting"
        - phase_table_full:
            phases: [
              {num: 1, name: "RED Phase", status: "not_started"},
              {num: 2, name: "GREEN Phase", status: "not_started"},
              {num: 3, name: "REFACTOR Phase", status: "not_started"}
            ]
        - next_action:
            action: "Begin RED phase (test generation)"
            benefit: "Create failing tests that define requirements"
    
    interim:
      components:
        - phase_update_interim:
            completed_phase: "{{completed_phase}}"
            next_phase: "{{next_phase}}"
        - test_results:  # Only if tests available
            tests: "{{test_metrics}}"
    
    end:
      components:
        - header:
            orchestrator_name: "TDD Orchestrator v2 Complete"
            feature_name: "{{feature_name}}"
        - overall_progress_bar:
            percentage: 100
            status: "complete"
        - phase_table_full:
            phases: "{{completed_phases}}"
        - test_results:
            tests: "{{final_test_metrics}}"
        - artifacts_list:
            artifacts: "{{generated_files}}"
        - summary_section:
            metrics: [
              {name: "Tests generated", value: "{{test_count}}"},
              {name: "Coverage", value: "{{coverage}}%"},
              {name: "Quality score", value: "{{quality_score}}"}
            ]
        - next_action:
            action: "✅ All work complete!"
```

### Deliverables

- **9 template files** in `cortex-brain/response-templates/orchestrators/`
  - `planning-v5-template.yaml`
  - `ado-v2-template.yaml`
  - `tdd-v2-template.yaml`
  - `cleanup-v2-template.yaml`
  - `vacuum-v2-template.yaml`
  - `debug-template.yaml`
  - `maintenance-template.yaml`
  - `sanitization-template.yaml`
  - `refinement-template.yaml`

### Acceptance Criteria

- [ ] All 9 orchestrator templates created
- [ ] Each template uses base components (no duplication)
- [ ] Display moments properly configured (start/interim/end)
- [ ] Custom components defined where needed
- [ ] Templates validated against component library

---

## 📋 Phase 4: Progress Bar System

**Duration:** 4 hours

### Implementation: `src/response_templates/progress_bar_generator.py`

```python
"""
Progress Bar Generator - Visual progress tracking for autonomous orchestrators.

Generates Unicode progress bars matching maintenance prompt format:
- Overall progress: `████████░░` 80%
- Phase tables with individual progress bars
- Interim updates (completed + next)
"""

from typing import List, Dict, Any, Optional
from enum import Enum

class DisplayMoment(Enum):
    """When to display specific template components."""
    START = "start"
    INTERIM = "interim"
    END = "end"
    ALL = "all"

class PhaseStatus(Enum):
    """Phase execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ERROR = "error"

class ProgressBarGenerator:
    """Generate visual progress bars and phase tables."""
    
    # Unicode characters for progress bars
    FILLED_CHAR = '█'
    EMPTY_CHAR = '░'
    DEFAULT_WIDTH = 20
    
    # Status emojis
    STATUS_EMOJIS = {
        PhaseStatus.NOT_STARTED: '⏸️',
        PhaseStatus.IN_PROGRESS: '⏳',
        PhaseStatus.COMPLETE: '✅',
        PhaseStatus.ERROR: '❌'
    }
    
    @classmethod
    def generate_overall_bar(
        cls,
        percentage: float,
        width: int = DEFAULT_WIDTH,
        filled: str = FILLED_CHAR,
        empty: str = EMPTY_CHAR
    ) -> str:
        """
        Generate overall progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Total bar width in characters
            filled: Character for filled portion
            empty: Character for empty portion
        
        Returns:
            Progress bar string like: `████████░░`
        
        Example:
            >>> ProgressBarGenerator.generate_overall_bar(80)
            '████████████████░░░░'
        """
        filled_count = int((percentage / 100) * width)
        empty_count = width - filled_count
        return filled * filled_count + empty * empty_count
    
    @classmethod
    def generate_phase_table(
        cls,
        phases: List[Dict[str, Any]],
        display_moment: DisplayMoment = DisplayMoment.START
    ) -> str:
        """
        Generate phase table with progress bars.
        
        Args:
            phases: List of phase dicts with keys:
                - num: Phase number
                - name: Phase name
                - status: PhaseStatus enum
                - percentage: Progress percentage (0-100)
                - elapsed_time: Optional elapsed time string
            display_moment: When this table is shown (affects formatting)
        
        Returns:
            Markdown table with progress bars
        
        Example:
            | # | Phase | Progress | Status |
            |---|-------|----------|--------|
            | 1 | ✅ **RED Phase** | `██████████` 100% | Complete (3m 24s) |
            | 2 | ⏳ **GREEN Phase** | `█████░░░░░` 50% | In Progress |
            | 3 | ⏸️ **REFACTOR Phase** | `░░░░░░░░░░` 0% | Not Started |
        """
        rows = []
        for phase in phases:
            num = phase['num']
            name = phase['name']
            status = PhaseStatus(phase['status'])
            percentage = phase.get('percentage', 0)
            elapsed_time = phase.get('elapsed_time')
            
            emoji = cls.STATUS_EMOJIS[status]
            bar = cls.generate_overall_bar(percentage, width=10)
            status_text = cls._format_status_text(status, elapsed_time)
            
            row = f"| {num} | {emoji} **{name}** | `{bar}` {percentage}% | {status_text} |"
            rows.append(row)
        
        header = "| # | Phase | Progress | Status |"
        separator = "|---|-------|----------|--------|"
        
        return "\n".join([header, separator] + rows)
    
    @classmethod
    def format_interim_update(
        cls,
        completed_phase: Dict[str, Any],
        next_phase: Dict[str, Any]
    ) -> str:
        """
        Generate concise interim update (completed + next).
        
        Args:
            completed_phase: Dict with keys:
                - name: Phase name
                - summary: Brief completion summary
                - elapsed_time: Time taken
            next_phase: Dict with keys:
                - name: Next phase name
                - description: What it does
                - estimated_time: Optional estimate
        
        Returns:
            Concise update string
        
        Example:
            ✅ **RED Phase Complete** - 12 tests generated (3m 24s)
            
            ⏳ **GREEN Phase Next** - Implement code to pass tests (Expected: ~5 minutes)
        """
        completed_text = (
            f"✅ **{completed_phase['name']} Complete** - "
            f"{completed_phase['summary']} ({completed_phase['elapsed_time']})"
        )
        
        next_text = f"⏳ **{next_phase['name']} Next** - {next_phase['description']}"
        if 'estimated_time' in next_phase:
            next_text += f" (Expected: ~{next_phase['estimated_time']})"
        
        return f"{completed_text}\n\n{next_text}"
    
    @classmethod
    def calculate_overall_percentage(cls, phases: List[Dict[str, Any]]) -> float:
        """
        Calculate overall progress percentage from phase percentages.
        
        Args:
            phases: List of phase dicts with 'percentage' key
        
        Returns:
            Overall percentage (0-100)
        """
        if not phases:
            return 0.0
        
        total_percentage = sum(p.get('percentage', 0) for p in phases)
        return round(total_percentage / len(phases), 1)
    
    @classmethod
    def format_status_emoji(cls, status: PhaseStatus) -> str:
        """Get emoji for phase status."""
        return cls.STATUS_EMOJIS.get(status, '⏸️')
    
    @classmethod
    def _format_status_text(cls, status: PhaseStatus, elapsed_time: Optional[str] = None) -> str:
        """Format status text with optional elapsed time."""
        status_texts = {
            PhaseStatus.NOT_STARTED: "Not Started",
            PhaseStatus.IN_PROGRESS: "In Progress",
            PhaseStatus.COMPLETE: "Complete",
            PhaseStatus.ERROR: "Error"
        }
        
        text = status_texts.get(status, "Unknown")
        
        if status == PhaseStatus.COMPLETE and elapsed_time:
            text += f" ({elapsed_time})"
        
        return text
```

### Deliverables

- `src/response_templates/progress_bar_generator.py` (350+ lines)
- Unit tests in `tests/response_templates/test_progress_bar_generator.py`

### Acceptance Criteria

- [ ] ProgressBarGenerator class implemented
- [ ] generate_overall_bar() creates Unicode bars
- [ ] generate_phase_table() creates full tables
- [ ] format_interim_update() creates concise updates
- [ ] All helper methods implemented
- [ ] 100% test coverage

---

## 📋 Phase 5: Template Renderer

**Duration:** 4 hours

### Implementation: `src/response_templates/template_renderer.py`

```python
"""
Template Renderer - Compose and render response templates from Lego components.

Handles:
- Loading templates from YAML files
- Composing components based on display moment
- Rendering Jinja2 templates with context
- Validating Single Action Rule
- Caching compiled templates
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, Template
from enum import Enum

from .progress_bar_generator import ProgressBarGenerator, DisplayMoment, PhaseStatus

class TemplateRenderer:
    """Render orchestrator response templates."""
    
    def __init__(self, template_dir: Path):
        """
        Initialize template renderer.
        
        Args:
            template_dir: Directory containing template YAML files
        """
        self.template_dir = template_dir
        self.base_components = self._load_base_components()
        self.orchestrator_templates = {}
        self._template_cache = {}
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False  # We control the content
        )
        
        # Register custom helpers
        self._register_helpers()
    
    def render(
        self,
        orchestrator_name: str,
        context: Dict[str, Any],
        display_moment: DisplayMoment = DisplayMoment.START
    ) -> str:
        """
        Render orchestrator template for specific display moment.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "tdd_orchestrator_v2")
            context: Template context data
            display_moment: When to display (start/interim/end)
        
        Returns:
            Rendered markdown response
        
        Example:
            renderer = TemplateRenderer(Path("cortex-brain/response-templates"))
            response = renderer.render(
                "tdd_orchestrator_v2",
                {
                    "feature_name": "user authentication",
                    "phases": [...],
                    "completed_phase": {...},
                    "next_phase": {...}
                },
                display_moment=DisplayMoment.INTERIM
            )
        """
        # Load orchestrator template
        template_config = self._load_orchestrator_template(orchestrator_name)
        
        # Get components for this display moment
        moment_config = template_config['display_moments'][display_moment.value]
        
        # Compose template from components
        composed_template = self._compose_template(moment_config['components'])
        
        # Render with context
        rendered = self._render_jinja2(composed_template, context)
        
        # Validate Single Action Rule
        self._validate_single_action(rendered)
        
        return rendered
    
    def _load_base_components(self) -> Dict[str, Any]:
        """Load base component library."""
        components_path = self.template_dir / "base-components.yaml"
        with open(components_path) as f:
            return yaml.safe_load(f)
    
    def _load_orchestrator_template(self, orchestrator_name: str) -> Dict[str, Any]:
        """Load orchestrator-specific template."""
        if orchestrator_name in self.orchestrator_templates:
            return self.orchestrator_templates[orchestrator_name]
        
        template_path = self.template_dir / "orchestrators" / f"{orchestrator_name}-template.yaml"
        with open(template_path) as f:
            template = yaml.safe_load(f)
            self.orchestrator_templates[orchestrator_name] = template
            return template
    
    def _compose_template(self, components: List[Dict[str, Any]]) -> str:
        """
        Compose template from component list.
        
        Args:
            components: List of component configs with parameters
        
        Returns:
            Composed template markup
        """
        sections = []
        
        for component_config in components:
            # Get component name (first key in dict)
            component_name = list(component_config.keys())[0]
            component_params = component_config[component_name]
            
            # Get component definition
            component_def = self.base_components['components'][component_name]
            
            # Get template markup
            template_markup = component_def['template']
            
            sections.append(template_markup)
        
        return "\n\n".join(sections)
    
    def _render_jinja2(self, template_markup: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template with context."""
        template = Template(template_markup, undefined=self.jinja_env.undefined)
        return template.render(**context)
    
    def _register_helpers(self):
        """Register Jinja2 helper functions."""
        self.jinja_env.globals['generate_progress_bar'] = ProgressBarGenerator.generate_overall_bar
        self.jinja_env.globals['generate_phase_table'] = ProgressBarGenerator.generate_phase_table
        self.jinja_env.globals['format_interim_update'] = ProgressBarGenerator.format_interim_update
        self.jinja_env.globals['format_status_emoji'] = ProgressBarGenerator.format_status_emoji
    
    def _validate_single_action(self, rendered: str):
        """
        Validate rendered template follows Single Action Rule.
        
        Raises:
            ValueError: If multiple actions detected
        """
        forbidden_patterns = ['or', 'either', 'option 1', 'option 2']
        lower_rendered = rendered.lower()
        
        for pattern in forbidden_patterns:
            if pattern in lower_rendered and 'next:' in lower_rendered:
                # Check if it's in the "Next:" section
                next_section = lower_rendered.split('next:')[-1]
                if pattern in next_section:
                    raise ValueError(
                        f"Single Action Rule violated: Multiple options detected ('{pattern}' in Next section)"
                    )
```

### Deliverables

- `src/response_templates/template_renderer.py` (400+ lines)
- Unit tests in `tests/response_templates/test_template_renderer.py`

### Acceptance Criteria

- [ ] TemplateRenderer class implemented
- [ ] Template loading from YAML working
- [ ] Component composition working
- [ ] Display moment switching working
- [ ] Jinja2 rendering working
- [ ] Single Action Rule validation working
- [ ] Template caching implemented
- [ ] 100% test coverage

---

## 📋 Phase 6: Orchestrator Integration

**Duration:** 8 hours

### Integration Pattern

Each orchestrator needs:

1. **Import TemplateRenderer:**
```python
from src.response_templates.template_renderer import TemplateRenderer, DisplayMoment
```

2. **Initialize renderer (in `__init__`):**
```python
self.template_renderer = TemplateRenderer(
    Path("cortex-brain/response-templates")
)
```

3. **START: Render initial progress:**
```python
def execute(self, user_request: str, options: Dict[str, Any]) -> Dict[str, Any]:
    # Render START display
    start_response = self.template_renderer.render(
        orchestrator_name="tdd_orchestrator_v2",
        context={
            "feature_name": self._extract_feature_name(user_request),
            "phases": self._get_phase_definitions(),
            "overall_percentage": 0
        },
        display_moment=DisplayMoment.START
    )
    
    print(start_response)  # Show to user
```

4. **INTERIM: After each phase:**
```python
def _execute_red_phase(self, ...):
    # Execute phase logic
    result = {...}
    
    # Render INTERIM update
    interim_response = self.template_renderer.render(
        orchestrator_name="tdd_orchestrator_v2",
        context={
            "completed_phase": {
                "name": "RED Phase",
                "summary": f"{result['tests_generated']} tests generated",
                "elapsed_time": self._format_elapsed_time(elapsed)
            },
            "next_phase": {
                "name": "GREEN Phase",
                "description": "Implement code to pass tests",
                "estimated_time": "5 minutes"
            }
        },
        display_moment=DisplayMoment.INTERIM
    )
    
    print(interim_response)  # Show to user
```

5. **END: Final summary:**
```python
    # All phases complete
    end_response = self.template_renderer.render(
        orchestrator_name="tdd_orchestrator_v2",
        context={
            "feature_name": feature_name,
            "phases": self._get_completed_phases(),
            "overall_percentage": 100,
            "test_metrics": {...},
            "generated_files": [...],
            "success_metrics": [...]
        },
        display_moment=DisplayMoment.END
    )
    
    print(end_response)  # Show to user
    
    return result
```

### Orchestrators to Update

1. **Planning v5** (`src/orchestrators/planning/planning_orchestrator_v5.py`)
2. **ADO v2** (`src/orchestrators/ado/ado_orchestrator_v2.py`)
3. **TDD v2** (`src/orchestrators/tdd/tdd_orchestrator_v2.py`)
4. **Cleanup v2** (`src/orchestrators/cleanup/cleanup_orchestrator_v2.py`)
5. **Vacuum v2** (`src/orchestrators/vacuum/vacuum_orchestrator_v2.py`)
6. **Debug** (`src/orchestrators/debug/debug_orchestrator.py`)
7. **Maintenance** (via prompt - document pattern)
8. **Sanitization** (via prompt - document pattern)
9. **Refinement** (via prompt - document pattern)

### Deliverables

- All autonomous orchestrators integrated with TemplateRenderer
- Display moment logic implemented (START/INTERIM/END)
- Context data properly extracted and passed to renderer

### Acceptance Criteria

- [ ] All 6 Python orchestrators integrated
- [ ] START displays full table
- [ ] INTERIM displays completed + next only
- [ ] END displays full table + summary
- [ ] Templates validated with manual testing
- [ ] No regressions in orchestrator functionality

---

## 📋 Phase 7: Testing

**Duration:** 4 hours

### Test Coverage

**Unit Tests:**
- `tests/response_templates/test_progress_bar_generator.py`
- `tests/response_templates/test_template_renderer.py`

**Integration Tests:**
- `tests/orchestrators/test_planning_v5_templates.py`
- `tests/orchestrators/test_tdd_v2_templates.py`
- `tests/orchestrators/test_cleanup_v2_templates.py`
- `tests/orchestrators/test_vacuum_v2_templates.py`

**Test Scenarios:**
1. **Display Moment Switching:**
   - START shows full table
   - INTERIM shows completed + next only
   - END shows full table + summary

2. **Progress Bar Generation:**
   - Overall bars render correctly (0%, 50%, 100%)
   - Phase tables render with correct emojis
   - Interim updates format correctly

3. **Component Composition:**
   - Components load from base-components.yaml
   - Orchestrator templates compose correctly
   - Parameters passed through to components

4. **Single Action Rule:**
   - Valid single actions pass validation
   - Multiple options trigger validation error
   - "All work complete" passes validation

5. **Template Caching:**
   - Templates cached after first load
   - Cache invalidates on template change

### Deliverables

- 200+ test cases across all test files
- 100% coverage for TemplateRenderer
- 100% coverage for ProgressBarGenerator
- Integration tests for all orchestrators

### Acceptance Criteria

- [ ] All tests passing
- [ ] 100% coverage for template system
- [ ] Integration tests validate full workflow
- [ ] Display moment behavior verified
- [ ] Single Action Rule validation tested

---

## 📋 Phase 8: Documentation

**Duration:** 2 hours

### Documentation Files

**1. Architecture Document** (`cortex-brain/documents/architecture/response-template-architecture.md`)
- Lego-piece philosophy
- Component library overview
- Template composition process
- Display moment pattern
- Best practices

**2. Developer Guide** (`cortex-brain/documents/guides/template-developer-guide.md`)
- Adding custom orchestrator templates
- Creating new components
- Testing templates
- Debugging tips

**3. Migration Guide** (`cortex-brain/documents/guides/template-migration-guide.md`)
- Converting existing orchestrators
- Display moment implementation
- Testing migration
- Rollback procedure

**4. Component Reference** (`cortex-brain/documents/reference/template-component-reference.md`)
- Complete component catalog
- Parameter specifications
- Usage examples
- Display moment compatibility

### Deliverables

- 4 comprehensive documentation files
- Code examples in all guides
- Migration checklist

### Acceptance Criteria

- [ ] All documentation complete
- [ ] Examples tested and working
- [ ] Migration guide validated
- [ ] Developer guide covers all workflows

---

## 🎯 Success Criteria

Template system complete when:

1. ✅ All 9 orchestrators have custom templates
2. ✅ base-components.yaml contains reusable Lego pieces
3. ✅ ProgressBarGenerator generates visual bars
4. ✅ TemplateRenderer composes and validates templates
5. ✅ Display moments work (START/INTERIM/END)
6. ✅ Single Action Rule enforced
7. ✅ All tests passing (200+ test cases)
8. ✅ Documentation complete

---

## 📦 Deliverables Summary

**Code:**
- `cortex-brain/response-templates/base-components.yaml`
- `cortex-brain/response-templates/orchestrators/*.yaml` (9 files)
- `src/response_templates/progress_bar_generator.py`
- `src/response_templates/template_renderer.py`
- Updated orchestrators (6 Python files)

**Tests:**
- `tests/response_templates/test_progress_bar_generator.py`
- `tests/response_templates/test_template_renderer.py`
- Integration tests for orchestrators

**Documentation:**
- `cortex-brain/documents/architecture/response-template-architecture.md`
- `cortex-brain/documents/guides/template-developer-guide.md`
- `cortex-brain/documents/guides/template-migration-guide.md`
- `cortex-brain/documents/reference/template-component-reference.md`

---

---

## 📋 Phase 9: Toolkit Orchestrator Conversion

**Duration:** 6 hours

### Objective

Convert `scripts/` toolkit manager → intelligent Toolkit Orchestrator that:
1. **Organizes scripts into clean folder structures** (by category, purpose, lifecycle)
2. **Maintains manifest-based index** (searchable, discoverable, self-documenting)
3. **Prevents duplication** (detects similar tools, suggests consolidation)
4. **Maximizes utility** (exposes tools via CLI, validates availability, tracks usage)

### Problem Analysis

**Current State (`scripts/` - 470+ files):**
- ❌ Flat structure (all scripts in one directory)
- ❌ Naming inconsistencies (`cleanup_*.py`, `fix_*.py`, `generate_*.py`, `validate_*.py`)
- ❌ No categorization (CLI tools mixed with utilities mixed with migrations)
- ❌ Duplication risk (similar tools created without discovery)
- ❌ No manifest (hard to find the right tool for a job)
- ❌ No lifecycle management (obsolete tools linger)

**Script Categories (from directory scan):**
- **Maintenance** (68 scripts): `cleanup_*.py`, `fix_*.py`, `repair_*.py`
- **Generation** (42 scripts): `generate_*.py`, `create_*.py`
- **Validation** (38 scripts): `validate_*.py`, `check_*.py`, `verify_*.py`
- **Analysis** (31 scripts): `analyze_*.py`, `audit_*.py`, `scan_*.py`
- **Migration** (24 scripts): `migrate_*.py`, `execute_phase*.py`
- **Documentation** (19 scripts): `regenerate_*_docs.py`, `generate_*_documentation.py`
- **Orchestrators** (12 scripts): CLI wrappers, launchers
- **Utilities** (236 scripts): Everything else

### Target Architecture

```
scripts/
├── toolkit-manifest.yaml              # Master index of all tools
├── __init__.py                        # Import aliasing
├── cortex-cli.py                      # Main CLI entry point
│
├── orchestrators/                     # 🛡️ Autonomous orchestrators
│   ├── planning/
│   │   └── planning_orchestrator_v5.py
│   ├── ado/
│   │   └── ado_orchestrator_v2.py
│   ├── tdd/
│   │   └── tdd_orchestrator_v2.py
│   ├── cleanup/
│   │   └── cleanup_orchestrator_v2.py
│   └── vacuum/
│       └── vacuum_orchestrator_v2.py
│
├── maintenance/                       # Cleanup, repair, health checks
│   ├── cleanup/
│   │   ├── cleanup_temp_files.py
│   │   ├── cleanup_inline_styles.py
│   │   └── cleanup_pre_commit.py
│   ├── repair/
│   │   ├── fix_html_issues.py
│   │   ├── repair_html_structure.py
│   │   └── fix_yaml_comprehensive.py
│   └── health/
│       ├── monitor_brain_health.py
│       └── check_wiring_integrity.py
│
├── generators/                        # Code/doc generation
│   ├── documentation/
│   │   ├── generate_docs_from_code.py
│   │   ├── regenerate_all_docs.py
│   │   └── generate_knowledge_docs.py
│   ├── tests/
│   │   ├── generate_test_templates.py
│   │   └── generate_performance_tests.py
│   └── diagrams/
│       ├── generate_uml_standalone.py
│       └── dependency_graph_generator.py
│
├── validators/                        # Validation, verification, checks
│   ├── deployment/
│   │   ├── validate_deployment.py
│   │   └── post_deployment_check.py
│   ├── configuration/
│   │   ├── validate_orchestrator_config.py
│   │   └── validate_manifests.py
│   └── quality/
│       ├── validate_templates.py
│       └── check_commit_score.py
│
├── analyzers/                         # Analysis, auditing, scanning
│   ├── code/
│   │   ├── analyze_critical.py
│   │   └── analyze_unwired_components.py
│   ├── metrics/
│   │   ├── measure_prompt_tokens.py
│   │   └── token_pricing_calculator.py
│   └── patterns/
│       ├── search_patterns.py
│       └── detect_duplicates.py
│
├── migrations/                        # Database/schema migrations
│   ├── database/
│   │   ├── migrate_brain_db.py
│   │   └── init_ado_database.py
│   └── schema/
│       ├── migrate_tier1_schema.py
│       └── migrate_enhancement_catalog_schema.py
│
├── utilities/                         # Helper utilities
│   ├── file_ops/
│   │   ├── process_includes.py
│   │   └── batch_path_hardening.py
│   ├── git_ops/
│   │   ├── git-sync.sh
│   │   └── install_git_hooks.py
│   └── deployment/
│       ├── deploy_cortex.py
│       └── build_package.py
│
├── cli_wrappers/                      # CLI integration
│   ├── cortex-bug
│   ├── cortex-capture
│   ├── cortex-feature
│   └── cortex-resume
│
├── launchers/                         # Launch scripts
│   ├── launch_docs.sh
│   └── launch_dashboard.ps1
│
└── admin/                            # Administrative tools
    └── cortex_system_doctor.py
```

### Manifest Structure: `toolkit-manifest.yaml`

```yaml
version: "1.0.0"
description: "CORTEX Toolkit Manifest - Indexed tool registry"
last_updated: "2026-01-03T10:30:00Z"

categories:
  orchestrators:
    description: "Autonomous orchestrators with Python implementations"
    tools:
      - name: "planning_orchestrator_v5"
        path: "scripts/orchestrators/planning/planning_orchestrator_v5.py"
        type: "autonomous"
        purpose: "Create structured plans with context gathering"
        entry_point: "python3 scripts/cortex-cli.py planning_system"
        options: ["--phase", "--resume"]
        dependencies: []
        status: "active"
        last_modified: "2026-01-02"
      
      - name: "ado_orchestrator_v2"
        path: "scripts/orchestrators/ado/ado_orchestrator_v2.py"
        type: "autonomous"
        purpose: "Generate Azure DevOps work items with acceptance criteria"
        entry_point: "python3 scripts/cortex-cli.py ado_orchestrator_v2"
        options: ["--type", "--estimate"]
        dependencies: ["azure-devops"]
        status: "active"
        last_modified: "2026-01-01"
  
  maintenance:
    description: "System maintenance, cleanup, and repair tools"
    tools:
      - name: "cleanup_temp_files"
        path: "scripts/maintenance/cleanup/cleanup_temp_files.py"
        purpose: "Remove temporary files from cortex-brain/"
        entry_point: "python3 scripts/maintenance/cleanup/cleanup_temp_files.py"
        options: ["--dry-run", "--aggressive"]
        dependencies: []
        status: "active"
        similar_tools: ["cleanup_unnecessary_files", "master_cleanup"]
        consolidation_candidate: true
      
      - name: "monitor_brain_health"
        path: "scripts/maintenance/health/monitor_brain_health.py"
        purpose: "Monitor CORTEX brain tier health metrics"
        entry_point: "python3 scripts/maintenance/health/monitor_brain_health.py"
        options: ["--tier", "--export"]
        dependencies: []
        status: "active"
  
  generators:
    description: "Code, documentation, and artifact generation"
    tools:
      - name: "generate_docs_from_code"
        path: "scripts/generators/documentation/generate_docs_from_code.py"
        purpose: "Generate markdown documentation from Python docstrings"
        entry_point: "python3 scripts/generators/documentation/generate_docs_from_code.py"
        options: ["--module", "--output"]
        dependencies: ["ast"]
        status: "active"
  
  validators:
    description: "Validation, verification, and quality checks"
    tools:
      - name: "validate_deployment"
        path: "scripts/validators/deployment/validate_deployment.py"
        purpose: "Validate CORTEX deployment completeness"
        entry_point: "python3 scripts/validators/deployment/validate_deployment.py"
        options: ["--environment", "--strict"]
        dependencies: []
        status: "active"
  
  analyzers:
    description: "Code analysis, metrics, and pattern detection"
    tools:
      - name: "measure_prompt_tokens"
        path: "scripts/analyzers/metrics/measure_prompt_tokens.py"
        purpose: "Calculate token count for prompt files"
        entry_point: "python3 scripts/analyzers/metrics/measure_prompt_tokens.py"
        options: ["--file", "--model"]
        dependencies: ["tiktoken"]
        status: "active"
  
  migrations:
    description: "Database and schema migration scripts"
    tools:
      - name: "migrate_brain_db"
        path: "scripts/migrations/database/migrate_brain_db.py"
        purpose: "Migrate cortex-brain database schema"
        entry_point: "python3 scripts/migrations/database/migrate_brain_db.py"
        options: ["--version", "--rollback"]
        dependencies: ["sqlite3"]
        status: "active"
  
  utilities:
    description: "General-purpose helper utilities"
    tools:
      - name: "deploy_cortex"
        path: "scripts/utilities/deployment/deploy_cortex.py"
        purpose: "Deploy CORTEX to production"
        entry_point: "python3 scripts/utilities/deployment/deploy_cortex.py"
        options: ["--target", "--dry-run"]
        dependencies: []
        status: "active"

# Duplication detection rules
duplication_rules:
  - pattern: "cleanup_*"
    check_purpose: true
    suggest_consolidation: true
  - pattern: "validate_*"
    check_options: ["--dry-run", "--strict"]
    suggest_consolidation: true
  - pattern: "generate_*_docs"
    check_dependencies: true
    suggest_consolidation: true

# Lifecycle management
lifecycle:
  deprecated:
    - name: "old_cleanup_legacy_3_0.py"
      reason: "Replaced by cleanup_orchestrator_v2"
      deprecated_date: "2025-12-15"
      removal_date: "2026-02-01"
  
  experimental:
    - name: "simulate_hybrid_capture.py"
      status: "testing"
      target_release: "v4.1.0"
```

### Phase 9 Tasks

**Task 9.1: Tool Discovery & Categorization (2 hours)**
1. Scan `scripts/` directory (470+ files)
2. Categorize by purpose (maintenance, generators, validators, analyzers, migrations, utilities)
3. Identify duplicates (similar purpose, overlapping functionality)
4. Extract metadata (dependencies, entry points, options)
5. Generate initial toolkit-manifest.yaml

**Task 9.2: Folder Structure Migration (2 hours)**
1. Create category folders (`orchestrators/`, `maintenance/`, `generators/`, etc.)
2. Move scripts to appropriate folders
3. Update import paths in affected files
4. Update documentation references
5. Test all tools in new locations

**Task 9.3: Toolkit Orchestrator Implementation (2 hours)**
1. Create `src/orchestrators/toolkit/toolkit_orchestrator.py`
2. Implement manifest loading and querying
3. Add tool discovery: `cortex toolkit search <query>`
4. Add tool info: `cortex toolkit info <tool_name>`
5. Add duplication detection: `cortex toolkit duplicates`
6. Add lifecycle management: `cortex toolkit deprecated`
7. CLI integration: `python3 scripts/cortex-cli.py toolkit <command>`

### Toolkit Orchestrator API

```python
class ToolkitOrchestrator:
    """
    Intelligent toolkit manager with manifest-based indexing.
    
    Features:
    - Tool discovery by purpose/category
    - Duplication detection
    - Lifecycle management (active/deprecated/experimental)
    - Usage tracking
    - Self-documentation
    """
    
    def search_tools(self, query: str, category: str = None) -> List[Tool]:
        """Search tools by purpose, name, or dependencies."""
        pass
    
    def get_tool_info(self, tool_name: str) -> ToolInfo:
        """Get detailed info about a specific tool."""
        pass
    
    def detect_duplicates(self) -> List[DuplicationReport]:
        """Find tools with similar purposes/functionality."""
        pass
    
    def suggest_consolidation(self, tools: List[str]) -> ConsolidationPlan:
        """Generate plan to consolidate duplicate tools."""
        pass
    
    def list_deprecated(self) -> List[DeprecatedTool]:
        """List tools scheduled for removal."""
        pass
    
    def validate_manifest(self) -> ValidationReport:
        """Validate toolkit manifest against actual files."""
        pass
```

### CLI Commands

```bash
# Search for tools
cortex toolkit search "cleanup cache"
cortex toolkit search "generate docs" --category generators

# Get tool info
cortex toolkit info cleanup_temp_files
cortex toolkit info --path scripts/maintenance/cleanup/cleanup_temp_files.py

# Find duplicates
cortex toolkit duplicates
cortex toolkit duplicates --category maintenance

# List deprecated tools
cortex toolkit deprecated
cortex toolkit deprecated --removal-date "2026-02-01"

# Validate manifest
cortex toolkit validate
cortex toolkit validate --fix
```

### Deliverables

1. **toolkit-manifest.yaml** (800+ lines)
   - All 470+ tools indexed
   - Categories defined
   - Duplication rules specified
   - Lifecycle states tracked

2. **Organized folder structure**
   - 7 category folders created
   - All scripts moved to appropriate locations
   - Import paths updated

3. **ToolkitOrchestrator** (`src/orchestrators/toolkit/toolkit_orchestrator.py`)
   - Manifest loading and querying
   - Tool discovery and search
   - Duplication detection
   - Lifecycle management
   - CLI integration

4. **Migration documentation** (`cortex-brain/documents/guides/toolkit-migration-guide.md`)
   - Old path → new path mapping
   - Import path updates
   - CLI command changes
   - Rollback procedure

### Acceptance Criteria

- [ ] toolkit-manifest.yaml complete with all 470+ tools
- [ ] All tools categorized and moved to new structure
- [ ] ToolkitOrchestrator implemented with full API
- [ ] CLI commands working (`cortex toolkit search/info/duplicates/deprecated/validate`)
- [ ] All import paths updated
- [ ] All tools tested in new locations
- [ ] Documentation complete
- [ ] Zero regressions

### Integration with Template System

**Template:** `toolkit_execution_progress` (similar to other orchestrators)

**Display Moments:**
- **START:** Full category table (7 categories, tool counts per category)
- **INTERIM:** `✅ Category migrated - N tools moved (time)` + `⏳ Next category`
- **END:** Full category table + migration summary + duplicate detection results

**Example Progress:**
```markdown
## 🛡️🧠 CORTEX Toolkit Orchestrator

### 📊 Migration Progress

**Overall Progress:** `████████░░` **80%** ⏳ IN PROGRESS

| # | Category | Tools | Progress | Status |
|---|----------|-------|----------|--------|
| 1 | ✅ **Orchestrators** | 12 | `██████████` 100% | Complete (5m 12s) |
| 2 | ✅ **Maintenance** | 68 | `██████████` 100% | Complete (12m 34s) |
| 3 | ✅ **Generators** | 42 | `██████████` 100% | Complete (8m 45s) |
| 4 | ⏳ **Validators** | 38 | `████░░░░░░` 40% | In Progress |
| 5 | ⏸️ **Analyzers** | 31 | `░░░░░░░░░░` 0% | Not Started |
| 6 | ⏸️ **Migrations** | 24 | `░░░░░░░░░░` 0% | Not Started |
| 7 | ⏸️ **Utilities** | 236 | `░░░░░░░░░░` 0% | Not Started |

**Next:** Complete Validators migration (15 tools remaining)
```

---

## 🎯 Updated Success Criteria

Template system + Toolkit Orchestrator complete when:

1. ✅ All 9 orchestrators have custom templates
2. ✅ base-components.yaml contains reusable Lego pieces
3. ✅ ProgressBarGenerator generates visual bars
4. ✅ TemplateRenderer composes and validates templates
5. ✅ Display moments work (START/INTERIM/END)
6. ✅ Single Action Rule enforced
7. ✅ All tests passing (250+ test cases)
8. ✅ Documentation complete
9. ✅ **Toolkit Orchestrator operational**
10. ✅ **All 470+ tools indexed in manifest**
11. ✅ **Clean folder structure implemented**
12. ✅ **Duplication detection working**

---

## 📦 Updated Deliverables Summary

**Code:**
- `cortex-brain/response-templates/base-components.yaml`
- `cortex-brain/response-templates/orchestrators/*.yaml` (9 files)
- `src/response_templates/progress_bar_generator.py`
- `src/response_templates/template_renderer.py`
- `src/orchestrators/toolkit/toolkit_orchestrator.py` (NEW)
- `scripts/toolkit-manifest.yaml` (NEW)
- Updated orchestrators (6 Python files)
- Reorganized scripts/ folder structure

**Tests:**
- `tests/response_templates/test_progress_bar_generator.py`
- `tests/response_templates/test_template_renderer.py`
- `tests/orchestrators/toolkit/test_toolkit_orchestrator.py` (NEW)
- Integration tests for orchestrators

**Documentation:**
- `cortex-brain/documents/architecture/response-template-architecture.md`
- `cortex-brain/documents/guides/template-developer-guide.md`
- `cortex-brain/documents/guides/template-migration-guide.md`
- `cortex-brain/documents/guides/toolkit-migration-guide.md` (NEW)
- `cortex-brain/documents/reference/template-component-reference.md`
- `cortex-brain/documents/reference/toolkit-manifest-reference.md` (NEW)

---

**Author:** CORTEX Planning Team  
**Date:** January 3, 2026  
**Plan Type:** Architectural Enhancement  
**Estimated Duration:** 44 hours (~6 days) - Updated with Toolkit Orchestrator phase
