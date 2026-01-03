# 🧱 Response Template Lego Architecture

**Version:** 1.0.0  
**Created:** January 3, 2026  
**Author:** Asif Hussain  
**Purpose:** Define modular, composable response template system for CORTEX orchestrators

---

## 🎯 Vision

Create a **Lego-piece template system** where:
- **Components = Lego bricks** (small, reusable, single-purpose)
- **Templates = Lego instructions** (assembly order, parameters, composition)
- **Orchestrators = Lego sets** (custom combinations of shared components)
- **No duplication** (DRY principle enforced at component level)

---

## 🏗️ Lego-Piece Philosophy

### Core Principles

**1. Single Responsibility**
Each component does ONE thing well:
- `header` → Orchestrator identification
- `overall_progress_bar` → Top-level progress visualization
- `phase_table_full` → Complete phase listing with progress
- `next_action` → Single action rule enforcement

**2. Composability**
Components snap together like Lego bricks:
```yaml
# TDD Orchestrator template
display_moments:
  start:
    components:
      - header              # Snap on header
      - overall_progress_bar # Snap on progress bar
      - phase_table_full    # Snap on phase table
      - next_action         # Snap on next step
```

**3. Reusability**
Same component used across multiple orchestrators:
- `header` → Used by all 9 orchestrators
- `overall_progress_bar` → Used by all 9 orchestrators
- `phase_table_full` → Used by 8 orchestrators (Planning, ADO, TDD, Cleanup, Vacuum, Maintenance, Sanitization, Refinement)
- `artifacts_list` → Used by 7 orchestrators

**4. Parameterization**
Components adapt to context via parameters:
```yaml
header:
  orchestrator_name: "TDD Orchestrator v2"  # TDD-specific
  feature_name: "{{feature_name}}"          # Dynamic
  author: "Asif Hussain"                    # Default

overall_progress_bar:
  percentage: 50                            # Dynamic
  status: "in_progress"                     # TDD phase state
```

**5. Display Moment Awareness**
Components know WHEN to appear:
- `start` → Full phase table, 0% progress
- `interim` → Concise update (completed + next)
- `end` → Full phase table, 100% progress, summary

---

## 📊 Display Moment Pattern

### The Three Moments

**Inspired by:** `.github/prompts/maintenance/pipeline/final-report-template.prompt.md`

### START: Full Context Display

**When:** Beginning of orchestrator execution  
**Purpose:** Show user the complete execution plan  
**Components:**
- `header` (orchestrator name, feature)
- `overall_progress_bar` (0%, starting)
- `phase_table_full` (all phases, not started)
- `next_action` (first phase to execute)

**Example (TDD Orchestrator v2):**
```markdown
## 🛡️🧠 CORTEX TDD Orchestrator v2
**Author:** Asif Hussain | **Feature:** User Authentication | **Orchestrator:** TDD Orchestrator v2 ✅

### 📊 Execution Progress

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ STARTING

| # | Phase | Progress | Status |
|---|-------|----------|--------|
| 1 | ⏸️ **RED Phase** | `░░░░░░░░░░` 0% | Not Started |
| 2 | ⏸️ **GREEN Phase** | `░░░░░░░░░░` 0% | Not Started |
| 3 | ⏸️ **REFACTOR Phase** | `░░░░░░░░░░` 0% | Not Started |

**Next:** Begin RED phase (test generation)
```

### INTERIM: Concise Progress Update

**When:** After each phase completes  
**Purpose:** Show progress without repeating full table  
**Components:**
- `phase_update_interim` (completed + next only)
- Optional: `test_results`, `validation_checks` (phase-specific data)

**Example (TDD after RED phase):**
```markdown
✅ **RED Phase Complete** - 12 tests generated, all failing as expected (3m 24s)

⏳ **GREEN Phase Next** - Implement code to pass tests (Expected: ~5 minutes)
```

**Key Characteristics:**
- ✅ **Completed phase:** Name + summary + time
- ⏳ **Next phase:** Name + description + estimate
- **NO full table** (reduces verbosity by 80%)

### END: Complete Summary

**When:** All phases complete  
**Purpose:** Show final results, artifacts, metrics  
**Components:**
- `header` (with "Complete" suffix)
- `overall_progress_bar` (100%, complete)
- `phase_table_full` (all phases with elapsed times)
- `test_results` / `validation_checks` / `work_item_summary` (orchestrator-specific)
- `artifacts_list` (generated files)
- `summary_section` (success metrics)
- `next_action` (completion message)

**Example (TDD after all phases):**
```markdown
## 🛡️🧠 CORTEX TDD Orchestrator v2 Complete
**Author:** Asif Hussain | **Feature:** User Authentication | **Orchestrator:** TDD Orchestrator v2 ✅

### 📊 Final Progress

**Overall Progress:** `████████████████████` **100%** ✅ COMPLETE

| # | Phase | Progress | Status |
|---|-------|----------|--------|
| 1 | ✅ **RED Phase** | `██████████` 100% | Complete (3m 24s) |
| 2 | ✅ **GREEN Phase** | `██████████` 100% | Complete (5m 12s) |
| 3 | ✅ **REFACTOR Phase** | `██████████` 100% | Complete (2m 48s) |

### 🧪 Test Results

- **Passing:** 12/12 (100%)
- **Coverage:** 94%
- **Duration:** 1.2s

### 📦 Artifacts Generated
- tests/auth/test_user_authentication.py (142 lines)
- src/auth/user_authentication.py (89 lines)
- docs/auth-implementation-guide.md (56 lines)

### ✅ Success Metrics
- 12 tests generated (100% coverage)
- All tests passing
- Zero warnings
- Refactor phase: removed 23 lines of duplicated code

**Next:** ✅ All work complete!
```

---

## 🧩 Component Categories

### Core Components (Always Present)

**Used by:** All 9 orchestrators  
**Display Moments:** start, interim, end

| Component | Purpose | Parameters | Size |
|-----------|---------|------------|------|
| `header` | Orchestrator identification | orchestrator_name, feature_name, author | 3 lines |
| `overall_progress_bar` | Top-level progress | percentage, status | 1 line |
| `next_action` | Single action enforcement | action, benefit | 1 line |

**Rationale:** Every orchestrator needs identification, progress tracking, and next step guidance.

### Display Moment Components

**Used by:** 8/9 orchestrators (all except simple tools)  
**Display Moments:** Vary by component

| Component | Purpose | Display Moments | Parameters |
|-----------|---------|-----------------|------------|
| `phase_table_full` | Complete phase listing | start, end | phases (array) |
| `phase_update_interim` | Concise progress | interim | completed_phase, next_phase |
| `summary_section` | Final metrics | end | metrics (array) |
| `artifacts_list` | Generated files | end | artifacts (array) |

**Rationale:** These components provide context at specific execution moments.

### Optional Components (Orchestrator-Specific)

**Used by:** 1-5 orchestrators each  
**Display Moments:** end (mostly)

| Component | Purpose | Used By | Parameters |
|-----------|---------|---------|------------|
| `validation_checks` | DoR/DoD status | Planning, ADO | dor_status, dod_status |
| `work_item_summary` | ADO work items | ADO | work_items (object) |
| `test_results` | Test status | TDD, Maintenance | tests (object) |
| `cleanup_summary` | Files deleted/space freed | Cleanup, Vacuum | cleanup_stats (object) |
| `threat_analysis` | Security scanning | Sanitization | threats (array) |
| `quality_metrics` | Code quality scores | Refinement | quality (object) |

**Rationale:** These components provide orchestrator-specific data that isn't universally applicable.

---

## 🎨 Component Composition Examples

### Example 1: Planning Orchestrator v5

**Phases:** Context Gathering, Plan Generation, Validation, Documentation  
**Display Moments:** START → INTERIM (4x) → END

**START Composition:**
```yaml
start:
  components:
    - header:
        orchestrator_name: "Planning Orchestrator v5"
        feature_name: "{{user_request}}"
    - overall_progress_bar:
        percentage: 0
        status: "starting"
    - phase_table_full:
        phases:
          - {num: 1, name: "Context Gathering", status: "not_started", percentage: 0}
          - {num: 2, name: "Plan Generation", status: "not_started", percentage: 0}
          - {num: 3, name: "Validation", status: "not_started", percentage: 0}
          - {num: 4, name: "Documentation", status: "not_started", percentage: 0}
    - next_action:
        action: "Begin Context Gathering (scan codebase, analyze requirements)"
```

**INTERIM Composition (after Phase 1):**
```yaml
interim:
  components:
    - phase_update_interim:
        completed_phase:
          name: "Context Gathering"
          summary: "Scanned 247 files, identified 12 related components"
          elapsed_time: "45s"
        next_phase:
          name: "Plan Generation"
          description: "Create structured 00-MASTER-PLAN.md with phases"
          estimated_time: "2 minutes"
```

**END Composition:**
```yaml
end:
  components:
    - header:
        orchestrator_name: "Planning Orchestrator v5 Complete"
        feature_name: "{{user_request}}"
    - overall_progress_bar:
        percentage: 100
        status: "complete"
    - phase_table_full:
        phases: "{{completed_phases}}"  # All marked complete
    - validation_checks:
        dor_status: {passed: true, violations: 0}
        dod_status: {passed: true, remaining: 0}
    - artifacts_list:
        artifacts:
          - {path: "planning/active/{{plan_name}}/00-MASTER-PLAN.md", lines: 843}
          - {path: "planning/active/{{plan_name}}/context/baseline-analysis.md", lines: 234}
    - summary_section:
        metrics:
          - {name: "Plan phases", value: "8"}
          - {name: "Context artifacts", value: "4"}
          - {name: "Total tasks", value: "32"}
    - next_action:
        action: "✅ All work complete!"
```

### Example 2: TDD Orchestrator v2

**Phases:** RED, GREEN, REFACTOR  
**Display Moments:** START → INTERIM (3x) → END

**Component Differences from Planning:**
- **Add:** `test_results` (shows pass/fail rates)
- **Remove:** `validation_checks` (not applicable to TDD)
- **Custom:** Phase names (RED/GREEN/REFACTOR vs generic Phase 1/2/3)

**INTERIM Composition (after RED phase):**
```yaml
interim:
  components:
    - phase_update_interim:
        completed_phase:
          name: "RED Phase"
          summary: "12 tests generated, all failing as expected"
          elapsed_time: "3m 24s"
        next_phase:
          name: "GREEN Phase"
          description: "Implement code to pass tests"
          estimated_time: "5 minutes"
    - test_results:  # TDD-specific addition
        tests:
          passing: 0
          total: 12
          pass_rate: 0
```

### Example 3: Cleanup Orchestrator v2

**Phases:** 5 modes (cache, logs, artifacts, full, git)  
**Display Moments:** START → INTERIM (per mode) → END

**Component Differences:**
- **Add:** `cleanup_summary` (files deleted, space freed)
- **Remove:** `test_results`, `validation_checks`
- **Custom:** Dynamic phases based on cleanup mode

**END Composition:**
```yaml
end:
  components:
    - header:
        orchestrator_name: "Cleanup Orchestrator v2 Complete"
    - overall_progress_bar:
        percentage: 100
        status: "complete"
    - phase_table_full:
        phases: "{{completed_phases}}"
    - cleanup_summary:
        cleanup_stats:
          files_deleted: 1247
          space_freed: "342 MB"
          backup_created: true
          backup_path: "cortex-brain/backups/cleanup_20260103_103045.tar.gz"
    - artifacts_list:
        artifacts:
          - {path: "cortex-brain/cleanup-reports/cleanup-report-20260103.json"}
    - summary_section:
        metrics:
          - {name: "Files cleaned", value: "1247"}
          - {name: "Space reclaimed", value: "342 MB"}
          - {name: "Errors", value: "0"}
    - next_action:
        action: "✅ All work complete!"
```

---

## 🔄 Template Composition Process

### Step-by-Step Assembly

**1. Orchestrator Invocation**
```python
from src.response_templates.template_renderer import TemplateRenderer, DisplayMoment

renderer = TemplateRenderer(Path("cortex-brain/response-templates"))
```

**2. START Display**
```python
start_response = renderer.render(
    orchestrator_name="tdd_orchestrator_v2",
    context={
        "feature_name": "user authentication",
        "phases": [
            {"num": 1, "name": "RED Phase", "status": "not_started", "percentage": 0},
            {"num": 2, "name": "GREEN Phase", "status": "not_started", "percentage": 0},
            {"num": 3, "name": "REFACTOR Phase", "status": "not_started", "percentage": 0}
        ]
    },
    display_moment=DisplayMoment.START
)
print(start_response)  # Show full table to user
```

**3. INTERIM Display (after each phase)**
```python
interim_response = renderer.render(
    orchestrator_name="tdd_orchestrator_v2",
    context={
        "completed_phase": {
            "name": "RED Phase",
            "summary": "12 tests generated, all failing",
            "elapsed_time": "3m 24s"
        },
        "next_phase": {
            "name": "GREEN Phase",
            "description": "Implement code to pass tests",
            "estimated_time": "5 minutes"
        },
        "test_metrics": {
            "passing": 0,
            "total": 12,
            "pass_rate": 0
        }
    },
    display_moment=DisplayMoment.INTERIM
)
print(interim_response)  # Show concise update only
```

**4. END Display**
```python
end_response = renderer.render(
    orchestrator_name="tdd_orchestrator_v2",
    context={
        "feature_name": "user authentication",
        "phases": [
            {"num": 1, "name": "RED Phase", "status": "complete", "percentage": 100, "elapsed_time": "3m 24s"},
            {"num": 2, "name": "GREEN Phase", "status": "complete", "percentage": 100, "elapsed_time": "5m 12s"},
            {"num": 3, "name": "REFACTOR Phase", "status": "complete", "percentage": 100, "elapsed_time": "2m 48s"}
        ],
        "test_metrics": {"passing": 12, "total": 12, "pass_rate": 100, "coverage": 94},
        "generated_files": [
            {"path": "tests/auth/test_user_authentication.py", "lines": 142},
            {"path": "src/auth/user_authentication.py", "lines": 89}
        ],
        "success_metrics": [
            {"name": "Tests generated", "value": "12"},
            {"name": "Coverage", "value": "94%"},
            {"name": "Quality score", "value": "A+"}
        ]
    },
    display_moment=DisplayMoment.END
)
print(end_response)  # Show full summary
```

### Behind the Scenes: Renderer Logic

```python
def render(self, orchestrator_name, context, display_moment):
    # 1. Load orchestrator template
    template_config = self._load_orchestrator_template(orchestrator_name)
    
    # 2. Get components for this display moment
    moment_config = template_config['display_moments'][display_moment.value]
    
    # 3. Compose template from components
    composed_markup = ""
    for component_def in moment_config['components']:
        component_name = list(component_def.keys())[0]
        component_params = component_def[component_name]
        
        # Get component from base-components.yaml
        base_component = self.base_components['components'][component_name]
        
        # Render component with parameters
        rendered_component = self._render_component(
            base_component['template'],
            {**context, **component_params}
        )
        
        composed_markup += rendered_component + "\n\n"
    
    # 4. Validate Single Action Rule
    self._validate_single_action(composed_markup)
    
    return composed_markup
```

---

## 📐 Design Patterns

### Pattern 1: Progressive Disclosure

**Problem:** Too much information overwhelms users  
**Solution:** Show details progressively via display moments

- **START:** Show what WILL happen (plan)
- **INTERIM:** Show what DID happen (result) + what's NEXT (action)
- **END:** Show what WAS accomplished (summary)

### Pattern 2: Component Inheritance

**Problem:** Similar orchestrators duplicate components  
**Solution:** Define base components, override parameters

```yaml
# Base component
header:
  author: "Asif Hussain"  # Default for all

# TDD overrides
header:
  orchestrator_name: "TDD Orchestrator v2"  # TDD-specific
  author: "Asif Hussain"  # Inherited from base

# Planning overrides
header:
  orchestrator_name: "Planning Orchestrator v5"  # Planning-specific
  author: "Asif Hussain"  # Inherited from base
```

### Pattern 3: Conditional Components

**Problem:** Not all orchestrators need all components  
**Solution:** Use `display_moments` to conditionally include

```yaml
# TDD needs test_results
test_results:
  display_moments: [interim, end]  # Show during and after execution

# Planning does NOT need test_results (not included in template)
```

### Pattern 4: Template Caching

**Problem:** Loading YAML templates on every render is slow  
**Solution:** Cache compiled templates after first load

```python
class TemplateRenderer:
    def __init__(self):
        self._template_cache = {}
    
    def _load_orchestrator_template(self, name):
        if name in self._template_cache:
            return self._template_cache[name]
        
        # Load from YAML
        template = yaml.safe_load(...)
        self._template_cache[name] = template
        return template
```

---

## ✅ Design Validation

### Anti-Patterns to Avoid

**❌ Monolithic Templates**
```yaml
# BAD: All orchestrator logic in one giant template
autonomous_execution_progress:
  template: |
    ## Header
    {% if orchestrator == 'planning' %}
      Planning-specific stuff
    {% elif orchestrator == 'tdd' %}
      TDD-specific stuff
    {% elif orchestrator == 'ado' %}
      ADO-specific stuff
    {% endif %}
    # 500+ lines of conditional logic...
```

**✅ Modular Components**
```yaml
# GOOD: Orchestrator template composes components
planning_execution_progress:
  display_moments:
    start:
      components:
        - header
        - overall_progress_bar
        - phase_table_full
        - validation_checks  # Planning-specific
        - next_action
```

**❌ Copy-Paste Duplication**
```yaml
# BAD: Duplicate progress bar markup in every template
planning_template:
  progress_bar: |
    **Overall Progress:** `{{bar}}` **{{percent}}%** {{emoji}}

tdd_template:
  progress_bar: |
    **Overall Progress:** `{{bar}}` **{{percent}}%** {{emoji}}  # Duplicated!
```

**✅ Shared Components**
```yaml
# GOOD: Progress bar defined once, used everywhere
# base-components.yaml
overall_progress_bar:
  template: |
    **Overall Progress:** `{{bar}}` **{{percent}}%** {{emoji}}

# planning_template.yaml uses it
# tdd_template.yaml uses it
# No duplication!
```

---

## 🎯 Success Metrics

**Reusability:** Each core component used by 9/9 orchestrators  
**DRY Compliance:** Zero duplication of component markup  
**Maintainability:** Update one component → affects all orchestrators  
**Extensibility:** New orchestrator = compose existing components + add 1-2 custom  
**Performance:** Template caching = <5ms render time

---

**Version:** 1.0.0  
**Status:** Architecture Complete  
**Next:** Implement component library (Phase 2)
