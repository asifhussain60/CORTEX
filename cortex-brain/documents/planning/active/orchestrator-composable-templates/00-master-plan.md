# 🧱 Orchestrator Composable Template System

**Plan ID:** COMPOSABLE-TEMPLATES-001  
**Priority:** MEDIUM-HIGH (#25) | **Effort:** 8-10 hours | **Category:** Enhancement  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** 2025-12-31 | **Updated:** 2025-12-31 | **Orchestrator:** Planning System 4.0 ✅

---

## 🛡️🧠 CORTEX Plan Execution

### 📊 Execution Progress

**Overall Progress:** `██████████` **100%** ✅ Complete

| # | Phase | Progress | Deliverables | Status |
|---|-------|----------|--------------|--------|
| 1 | ✅ **Shield Icon Governance** | `██████████` 100% | 4/4 | Complete |
| 2 | ✅ **Discovery & Analysis** | `██████████` 100% | 4/4 | Complete |
| 3 | ✅ **Template Migration Review** | `██████████` 100% | 3/3 | Complete |
| 4 | ✅ **Intelligent Template Algorithm** | `██████████` 100% | 4/4 | Complete |
| 5 | ✅ **Orchestrator Template Generation** | `██████████` 100% | 8/8 | Complete |
| 6 | ✅ **Composable Blocks Schema** | `██████████` 100% | 2/2 | Complete |
| 7 | ✅ **Manifest Updates (All 8)** | `██████████` 100% | 8/8 | Complete |
| 8 | ✅ **Progress Bar Standardization** | `██████████` 100% | 2/2 | Complete |
| 9 | ✅ **Validation & REFACTOR** | `██████████` 100% | 5/5 | Complete |
| 10 | ✅ **Toolkit Tools Creation** | `██████████` 100% | 4/4 | Complete |
| 11 | ✅ **Tracker Sync Enhancement** | `██████████` 100% | 2/2 | Complete |

---

## 🎯 Objective

Implement a **LEGO-style composable template system** with:
1. **Intelligent Template Selection Algorithm** - Dynamically compose responses from template blocks
2. **Orchestrator-Specific Templates** - Each orchestrator gets tailored template compositions
3. **Migration from Existing Templates** - Review and migrate current templates to new system
4. **Standardized Progress Bars** - Consistent visual progress across all orchestrators

### Success Criteria

| Criterion | Verification Command | Status |
|-----------|---------------------|--------|
| `composable_blocks` section exists | `grep "composable_blocks:" cortex-brain/response-templates-v4.yaml` | ⏳ |
| `template_selection_algorithm` defined | `grep "template_selection_algorithm:" response-templates-v4.yaml` | ⏳ |
| All 8 orchestrator manifests have `response_templates` | `grep -l "response_templates:" cortex-brain/manifests/orchestrators/*-manifest.yaml \| wc -l` = 8 | ⏳ |
| Orchestrator-specific templates generated | Each manifest has tailored template blocks | ⏳ |
| Progress bars use 10-character width | Visual inspection of templates | ⏳ |
| Standardized icons: ✅ 🔄 ⏳ ❌ ⏸️ | `grep -E "✅\|🔄\|⏳\|❌\|⏸️" cortex-brain/response-templates-v4.yaml` | ⏳ |
| YAML files valid | `python -c "import yaml; yaml.safe_load(...)"` succeeds | ⏳ |
| No breaking changes | CORTEX renders responses correctly | ⏳ |

---

## 📋 Phase Breakdown

### Phase 1: Shield Icon Governance Implementation
**Estimated:** 60 min | **Deliverables:** 4

**Tasks:**
- [x] 2.1 Inventory all existing sections in `response-templates-v4.yaml` (sections library)
- [x] 2.2 Document all `when_to_use` conditions for each section
- [x] 2.3 Check existing `response_templates` in orchestrator manifests
- [x] 2.4 Identify template usage patterns across orchestrators
- [x] 2.5 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 2 --progress 100 --status complete`)

**Output:** `context/current-state-analysis.md` (update)

---

### Phase 3: Template Migration Review (NEW)
```yaml
response_template: "autonomous_execution_progress"
response_instructions: |
  REQUIRED: Use response template that includes shield icon (🛡️) in header.
**Tasks:**
- [x] 3.1 Catalog all named templates (`autonomous_execution_progress`, `ado_execution_progress`, `plan_created`, etc.)
- [x] 3.2 Identify reusable blocks within existing templates
- [x] 3.3 Create migration mapping: old templates → composable blocks
- [x] 3.4 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 3 --progress 100 --status complete`)

**Migration Mapping Format:**brain/response-templates-v4.yaml:autonomous_execution_progress
```

**Governance Enhancement Format:**
```yaml
- rule_id: AUTONOMOUS_EXECUTION_PROTECTION
  description: "Autonomous execution MUST include safety checks AND visual confirmation via shield icon (🛡️) in response header."
  visual_confirmation:
    required: true
    icon: "🛡️"
    header_format: "## 🛡️🧠 CORTEX {{title}}"
    purpose: "User visual confirmation that orchestrator has been engaged"
    enforcement: "Response template must include shield icon in header"
```

**Output:** 
- Updated `planning-system-4.0-manifest.yaml`
- Updated `ado-planning-manifest.yaml`
- Updated `brain-protection-rules.yaml`
- Validation confirmation

---

### Phase 2: Discovery & Analysis
**Estimated:** 45 min | **Deliverables:** 4
**Output:** `context/template-migration-mapping.md`

---

### Phase 4: Intelligent Template Selection Algorithm (NEW)or manifests
- [x] 1.4 Identify template usage patterns across orchestrators
- [x] 1.5 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 1 --progress 100 --status complete`)

**Output:** `context/current-state-analysis.md` (update)
**Tasks:**
- [ ] 4.1 Define context signals for template selection (operation type, phase, complexity)
- [ ] 4.2 Create block priority rules (which blocks are mandatory vs optional)
- [ ] 4.3 Design composition algorithm with block ordering logic
- [ ] 4.4 Add algorithm specification to `response-templates-v4.yaml`

**Algorithm Schema:**xisting user response templates and plan migration to composable system.

**Tasks:**
- [x] 2.1 Catalog all named templates (`autonomous_execution_progress`, `ado_execution_progress`, `plan_created`, etc.)
- [x] 2.2 Identify reusable blocks within existing templates
- [x] 2.3 Create migration mapping: old templates → composable blocks
- [x] 2.4 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 2 --progress 100 --status complete`)

**Migration Mapping Format:**
```yaml
template_migration:
  autonomous_execution_progress:
    source_lines: "715-770"
    extractable_blocks:
      - cortex_header
      - progress_tracker
      - validation_status
      - plan_file_link
      - next_action
    status: "migrate_to_composable"
    
  ado_execution_progress:
    source_lines: "780-845"
    extractable_blocks:
      - cortex_header
      - progress_tracker
      - work_item_summary
      - ado_links
      - validation_status
      - plan_file_link
    status: "migrate_to_composable"
```

**Output:** `context/template-migration-mapping.md`

---

### Phase 3: Intelligent Template Selection Algorithm (NEW)
**Estimated:** 90 min | **Deliverables:** 4

**Purpose:** Design algorithm to dynamically compose responses from template blocks like LEGO pieces.

**Tasks:**
- [ ] 3.1 Define context signals for template selection (operation type, phase, complexity)
- [ ] 3.2 Create block priority rules (which blocks are mandatory vs optional)
- [ ] 3.3 Design composition algorithm with block ordering logic
- [ ] 3.4 Add algorithm specification to `response-templates-v4.yaml`

**Algorithm Schema:**
```yaml
template_selection_algorithm:
  version: "1.0"
  description: "Intelligent LEGO-style template composition"
  
  # Context signals used for block selection
  context_signals:
    operation_type:
      values: [planning, execution, analysis, debug, refinement, documentation, ado]
      determines: [header_style, progress_format, completion_format]
    
    response_phase:
      values: [start, in_progress, complete, error]
      determines: [status_indicators, next_steps_format]
    
    complexity_tier:
      values: [INSTANT, FOCUSED, STRUCTURED, COMPREHENSIVE]
**Output:** Updated `response-templates-v4.yaml` with `template_selection_algorithm` section

---

### Phase 5: Orchestrator-Specific Template Generation (NEW)

  # Block categories with priorities
  block_categories:
    mandatory:
      - cortex_header      # Always first
      - next_steps         # Always last
    
    conditional:
      - progress_tracker   # If multi_phase_operation
      - understanding      # If discovery_performed
      - validation_status  # If validation_ran
      - changes            # If files_modified
      - cautions           # If risks_present
    
    orchestrator_specific:
      planning: [dor_dod_status, deliverables_matrix, plan_file_link]
      tdd: [tdd_cycle_status, test_results_summary, coverage_metrics]
      debug: [bug_hypothesis, root_cause, fix_verification]
      ado: [work_item_summary, ado_links, story_points]
      lens: [analytics_summary, health_metrics, recommendations]
      refinement: [improvement_areas, code_quality_delta]
      sanitization: [sanitization_findings, pii_removed, secrets_redacted]
      documentation: [doc_summary, coverage_report]

  # Composition rules
  composition_rules:
    order: [cortex_header, understanding, approach, progress_tracker, response, 
            orchestrator_specific, changes, validation_status, cautions, next_steps]
    
    max_sections:
      INSTANT: 1
      FOCUSED: 3
      STRUCTURED: 5
      COMPREHENSIVE: 8
    
    section_selection:
      - rule: "Include mandatory blocks always"
      - rule: "Add conditional blocks if context_signal matches when_to_use"
      - rule: "Add orchestrator_specific blocks based on orchestrator_type"
      - rule: "Respect max_sections for complexity_tier"
      - rule: "Prioritize blocks with higher relevance scores"
```

**Output:** Updated `response-templates-v4.yaml` with `template_selection_algorithm` section

---

### Phase 4: Orchestrator-Specific Template Generation (NEW)
**Estimated:** 120 min | **Deliverables:** 8

**Purpose:** Generate tailored template compositions for each orchestrator based on its operations.

**Tasks:**
- [ ] 5.1 Generate Planning orchestrator templates (plan_creation, plan_execution, plan_completion)
- [ ] 5.2 Generate TDD orchestrator templates (test_run, red_phase, green_phase, refactor_phase)
- [ ] 5.3 Generate Debug orchestrator templates (investigation, hypothesis, resolution)
- [ ] 5.4 Generate CORTEX Lens templates (dashboard, health_report, recommendations)
- [ ] 5.5 Generate Refinement orchestrator templates (analysis, improvement, completion)
- [ ] 5.6 Generate Sanitization orchestrator templates (scan, sanitize, report)
- [ ] 5.7 Generate Documentation orchestrator templates (generation, update, review)
- [ ] 5.8 Generate ADO orchestrator templates (story_creation, feature_breakdown, completion)

**Template Generation Format (per orchestrator):**
```yaml
# Example: Planning Orchestrator Templates
planning_orchestrator:
  operations:
    plan_creation:
      context_signals:
        operation_type: planning
        response_phase: start
        complexity_tier: STRUCTURED
      blocks:
        mandatory: [cortex_header, next_steps]
        conditional: [understanding, progress_tracker, dor_dod_status]
        orchestrator_specific: [deliverables_matrix, plan_file_link]
      
    plan_execution:
      context_signals:
        operation_type: execution
        response_phase: in_progress
        complexity_tier: COMPREHENSIVE
      blocks:
        mandatory: [cortex_header, next_steps]
        conditional: [progress_tracker, changes, validation_status]
        orchestrator_specific: [deliverables_matrix, phase_details]
      
    plan_completion:
      context_signals:
        operation_type: planning
        response_phase: complete
        complexity_tier: STRUCTURED
      blocks:
        mandatory: [cortex_header]  # No next_steps for completion
        conditional: [progress_tracker, changes, validation_status, achievements]
        orchestrator_specific: [deliverables_matrix, plan_file_link]
      completion_format: "🎉 CONGRATULATIONS"
```

**Output:** `artifacts/orchestrator-templates.yaml` + updates to each manifest

---

### Phase 6: Composable Blocks Schema
**Estimated:** 45 min | **Deliverables:** 2

**Tasks:**
- [ ] 6.1 Add `composable_blocks` section to `response-templates-v4.yaml`
- [ ] 6.2 Define all generic and specialized blocks with rendering formats

**Schema:**
```yaml
composable_blocks:
  version: "1.0"
  
  # Standard Progress Tracker Block
  progress_tracker_standard:
    description: "Standardized visual progress tracker"
    format: |
      ### 📊 {{operation_name}} STATUS
      **Overall Progress:** `{{overall_bar}}` **{{overall_percentage}}%** {{status_emoji}} {{status_text}}
      | Phase | Progress | Status |
      |-------|----------|--------|
      {{#each phases}}
      | Phase {{phase_num}} - {{phase_name}} | `{{phase_bar}}` | {{phase_percentage}}% {{phase_icon}} {{phase_status}} |
      {{/each}}
    config:
      bar_width: 10
      filled_char: "█"
      empty_char: "░"
      icons:
        complete: "✅"
        in_progress: "🔄"
        pending: "⏳"
        failed: "❌"
        skipped: "⏸️"

  # Generic Reusable Blocks
  generic_blocks:
    cortex_header:
      format: |
        ## {{#if orchestrator_engaged}}🛡️{{/if}}🧠 CORTEX {{title}}
        **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
    
    understanding:
      emoji: "🎯"
      title: "Understanding & Scope"
      format: "### 🎯 Understanding & Scope\n\n{{content}}"
    
    approach:
      emoji: "⚡"
      title: "Approach & Considerations"
      format: "### ⚡ Approach & Considerations\n\n{{content}}"
    
    response:
      emoji: "💬"
      title: "Response"
      format: "### 💬 Response\n\n{{content}}"
    
    changes:
      emoji: "📊"
      title: "Impact & Changes"
      format: |
        ### 📊 Impact & Changes
        | File | Change |
        |------|--------|
        {{#each files}}
        | `{{file}}` | {{change}} |
        {{/each}}
    
    next_steps:
      emoji: "🔍"
      title: "Next Steps"
      format: "**Next:** {{action}}"
    
    validation_status:
      emoji: "✅"
      title: "Validation Status"
      format: |
        ### ✅ Validation Status
        | Check | Status |
        |-------|--------|
        {{#each checks}}
        | **{{name}}** | {{status_icon}} {{status}} |
        {{/each}}
    
    plan_file_link:
      format: |
        ### 📄 Plan File
        **Open in Editor:** [{{filename}}]({{path}})
    
    completion_banner:
      format: |
        # 🎉 CONGRATULATIONS
        ## 🧠 CORTEX {{operation}}
        
        ✅ **All work complete!** No further action required.

  # Orchestrator-Specific Blocks
  specialized_blocks:
    tdd_cycle_status:
      format: |
        ### 🔴🟢🔄 TDD Cycle
        | Phase | Status |
        |-------|--------|
        | RED (Failing Test) | {{red_status}} |
        | GREEN (Passing Test) | {{green_status}} |
        | REFACTOR (Clean Up) | {{refactor_status}} |
    
    work_item_summary:
      format: |
        ### 🎫 Work Items
        | Type | Count | Story Points |
        |------|-------|--------------|
        {{#each items}}
        | {{type}} | {{count}} | {{sp}} SP |
        {{/each}}
    
    dor_dod_status:
      format: |
        ### ✅ Definition of Ready/Done
        | Criterion | Status |
        |-----------|--------|
        | **DoR** | {{dor_status}} |
        | **DoD** | {{dod_status}} |
    
    bug_hypothesis:
      format: |
        ### 🔍 Bug Hypothesis
        **Suspected Cause:** {{hypothesis}}
        **Confidence:** {{confidence}}%
    
    analytics_summary:
      format: |
        ### 📈 Analytics Summary
        {{#each metrics}}
        - **{{name}}:** {{value}}
        {{/each}}
```

**Output:** Updated `response-templates-v4.yaml`

---

### Phase 7: Manifest Updates (All 8)
**Estimated:** 60 min | **Deliverables:** 8

**Tasks:**
- [x] 7.1 Update `planning-system-4.0-manifest.yaml` with `response_templates`
- [x] 7.2 Update `tdd-orchestrator-v4-manifest.yaml` with `response_templates`
- [x] 7.3 Update `debug-orchestrator-manifest.yaml` with `response_templates`
- [x] 7.4 Update `cortex-lens-v3-manifest.yaml` with `response_templates`
- [x] 7.5 Update `refinement-orchestrator-manifest.yaml` with `response_templates`
- [x] 7.6 Update `code-sanitization-manifest.yaml` with `response_templates`
- [x] 7.7 Update `technical-documentation-orchestrator-manifest.yaml` with `response_templates`
- [x] 7.8 Verify `ado-planning-manifest.yaml` (already has section, may need update)
- [x] 7.9 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 7 --progress 100 --status complete`)

**Each manifest gets:**
```yaml
response_templates:
  use_algorithm: true
  algorithm_version: "1.0"
  operations:
    {operation_name}:
      blocks: [list_of_blocks]
      context_signals:
        operation_type: {type}
        complexity_tier: {tier}
```

**Output:** 8 updated manifest files

---

### Phase 8: Progress Bar Standardization
**Estimated:** 30 min | **Deliverables:** 2

**Tasks:**
- [ ] 8.1 Update all progress templates to use standardized format
- [ ] 8.2 Ensure consistent: 10-char width, `█░` chars, ✅🔄⏳❌⏸️ icons

**Output:** Updated progress templates in `response-templates-v4.yaml`

---

### Phase 9: Validation & REFACTOR (SKULL Rule)
**Estimated:** 45 min | **Deliverables:** 5

**Tasks:**
- [ ] 9.1 Validate all YAML syntax
- [ ] 9.2 Count `response_templates` occurrences (target: 8 manifests)
- [ ] 9.3 Verify `template_selection_algorithm` is complete
- [ ] 9.4 Test CORTEX response rendering with new system
- [ ] 9.5 **REFACTOR:** Remove deprecated templates, clean up duplicates

**Validation Commands:**
```bash
# YAML Syntax Check
python -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates-v4.yaml'))" && echo "✅ Valid YAML"

# Count manifests with response_templates
grep -l "response_templates:" cortex-brain/manifests/orchestrators/*-manifest.yaml | wc -l
# Expected: 8

# Verify composable_blocks exists
grep "composable_blocks:" cortex-brain/response-templates-v4.yaml && echo "✅ composable_blocks found"

# Verify algorithm exists
grep "template_selection_algorithm:" cortex-brain/response-templates-v4.yaml && echo "✅ algorithm found"
```

**Output:** `reports/validation-report.md`

---

### Phase 10: Toolkit Tools Creation (NEW)
**Estimated:** 90 min | **Deliverables:** 4

**Purpose:** Create reusable CORTEX Toolkit tools for template system management.

**Tasks:**
- [x] 10.1 Create `validate_templates.py` (YAML validation)
- [x] 10.2 Create `analyze_blocks.py` (block usage analysis)
- [x] 10.3 Create `progress_bar.py` (standardized progress generation)
- [x] 10.4 Update `cortex-toolkit/README.md` with new tools section
- [x] 10.5 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 10 --progress 100 --status complete`)

**Output:** 3 Python tools + updated README

---

### Phase 11: Tracker Sync Enhancement (NEW)
**Estimated:** 60 min | **Deliverables:** 2

**Purpose:** Implement progress tracker synchronization and bidirectional linking.

**Tasks:**
- [x] 11.1 Create `sync_plan_tracker.py` toolkit tool
- [x] 11.2 Update Planning System manifest with tracker sync guidance
- [x] 11.3 Update ADO Planning manifest with tracker sync guidance
- [x] 11.4 Add bidirectional linking requirements to manifests
- [x] 11.5 Update master plan with navigation links
- [x] 11.6 Create tracker JSON file with initial state
- [x] 11.7 **Update progress tracker** (`python cortex-toolkit/sync_plan_tracker.py --update-phase 11 --progress 100 --status complete`)

**Features:**
- Extract progress from master plan markdown table
- Sync to `tracking/progress-tracker.json`
- Update master plan from command line
- Validate consistency between master and tracker
- Generate bidirectional navigation links
- Support for all active plans (bulk sync)

**Output:** `sync_plan_tracker.py` + updated manifests

---

## 📁 Files to Modify

| File | Change |
|------|--------|
| `cortex-brain/response-templates-v4.yaml` | Add `template_selection_algorithm`, `composable_blocks`, standardize progress |
| `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/technical-documentation-orchestrator-manifest.yaml` | Add `response_templates` with algorithm |
| `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` | Update existing `response_templates` |

## 📁 Files to Create

| File | Purpose |
|------|---------|
| `context/template-migration-mapping.md` | Migration plan from old to new templates |
| `artifacts/orchestrator-templates.yaml` | Generated orchestrator-specific templates |
| `reports/validation-report.md` | Final validation results |

---

## ✅ Definition of Ready (DoR)

| Criterion | Status |
|-----------|--------|
| Clear objective defined | ✅ |
| Success criteria measurable | ✅ |
| Files to modify identified | ✅ |
| Algorithm specification provided | ✅ |
| Migration mapping planned | ✅ |
| Validation commands specified | ✅ |

---

## ✅ Definition of Done (DoD)

| Criterion | Status |
|-----------|--------|
| `template_selection_algorithm` defined | ⏳ |
## ✅ Definition of Done (DoD)

| Criterion | Status |
|-----------|--------|
| `template_selection_algorithm` defined | ✅ |
| `composable_blocks` section exists | ✅ |
| All 8 manifests have `response_templates` | ✅ |
| Orchestrator-specific templates generated | ✅ |
| Progress bars use standardized format | ✅ |
| All YAML files pass syntax validation | ✅ |
| No breaking changes to existing functionality | ✅ |
| REFACTOR phase completed (SKULL rule) | ✅ |
| Progress tracker sync tool created | ✅ |
| Bidirectional linking implemented | ✅ |

---

## 📌 copilot_instructions

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: false  # Schema changes only, no code
final_refactor_required: true
progress_tracker: "tracking/progress-tracker.json"
progress_tracker_sync: true  # NEW: Enforce tracker sync in each phase
bidirectional_linking: true  # NEW: Enforce file linking
algorithm_design: true
orchestrator_template_generation: true
toolkit_tools:
  - validate_templates.py
  - analyze_blocks.py
  - progress_bar.py
  - sync_plan_tracker.py  # NEW
```

---

## 📄 Plan Navigation

**Master Plan:** [00-master-plan.md](00-master-plan.md) (you are here)
**Progress Tracker:** [progress-tracker.json](tracking/progress-tracker.json)

**Context Files:**
- [current-state-analysis.md](context/current-state-analysis.md)
- [template-migration-mapping.md](context/template-migration-mapping.md)

**Artifacts:**
- [orchestrator-templates.yaml](artifacts/orchestrator-templates.yaml)

**Reports:**
- [validation-report.md](reports/validation-report.md)

**Completion Reports:**
- [toolkit-completion-report.md](toolkit-completion-report.md)
- [final-summary.md](final-summary.md)

**Sync Commands:**
```bash
# Update phase progress (N = 1-11)
python cortex-toolkit/sync_plan_tracker.py "cortex-brain/documents/planning/active/orchestrator-composable-templates" --update-phase N --progress PCT --status STATUS

# Validate consistency
python cortex-toolkit/sync_plan_tracker.py "cortex-brain/documents/planning/active/orchestrator-composable-templates" --validate

# Sync from master plan to tracker
python cortex-toolkit/sync_plan_tracker.py "cortex-brain/documents/planning/active/orchestrator-composable-templates"
```

---

## 🗑️ Post-Completion

After successful execution:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/25-orchestrator-composable-templates.md
```

---

### 📄 Open Plan in Editor

**Click to open:** [00-master-plan.md](cortex-brain/documents/planning/active/orchestrator-composable-templates/00-master-plan.md)

---

**Next:** Execute Phase 1 - Discovery & Analysis
