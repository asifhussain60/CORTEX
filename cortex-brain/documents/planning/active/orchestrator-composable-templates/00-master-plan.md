# 🧱 Orchestrator Composable Template System

**Plan ID:** COMPOSABLE-TEMPLATES-001  
**Priority:** MEDIUM-HIGH (#25) | **Effort:** 8-10 hours | **Category:** Enhancement  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** 2025-12-31 | **Updated:** 2025-12-31 | **Orchestrator:** Planning System 4.0 ✅

---

## 🛡️🧠 CORTEX Plan Execution

### 📊 Execution Progress

**Overall Progress:** `░░░░░░░░░░` **0%** ⏳ Not Started

| # | Phase | Progress | Deliverables | Status |
|---|-------|----------|--------------|--------|
| 1 | ⏸️ **Discovery & Analysis** | `░░░░░░░░░░` 0% | 0/4 | Pending |
| 2 | ⏸️ **Template Migration Review** | `░░░░░░░░░░` 0% | 0/3 | Pending |
| 3 | ⏸️ **Intelligent Template Algorithm** | `░░░░░░░░░░` 0% | 0/4 | Pending |
| 4 | ⏸️ **Orchestrator Template Generation** | `░░░░░░░░░░` 0% | 0/8 | Pending |
| 5 | ⏸️ **Composable Blocks Schema** | `░░░░░░░░░░` 0% | 0/2 | Pending |
| 6 | ⏸️ **Manifest Updates (All 8)** | `░░░░░░░░░░` 0% | 0/8 | Pending |
| 7 | ⏸️ **Progress Bar Standardization** | `░░░░░░░░░░` 0% | 0/2 | Pending |
| 8 | ⏸️ **Validation & REFACTOR** | `░░░░░░░░░░` 0% | 0/5 | Pending |

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

### Phase 1: Discovery & Analysis
**Estimated:** 45 min | **Deliverables:** 4

**Tasks:**
- [ ] 1.1 Inventory all existing sections in `response-templates-v4.yaml` (sections library)
- [ ] 1.2 Document all `when_to_use` conditions for each section
- [ ] 1.3 Check existing `response_templates` in orchestrator manifests
- [ ] 1.4 Identify template usage patterns across orchestrators

**Output:** `context/current-state-analysis.md` (update)

---

### Phase 2: Template Migration Review (NEW)
**Estimated:** 60 min | **Deliverables:** 3

**Purpose:** Review existing user response templates and plan migration to composable system.

**Tasks:**
- [ ] 2.1 Catalog all named templates (`autonomous_execution_progress`, `ado_execution_progress`, `plan_created`, etc.)
- [ ] 2.2 Identify reusable blocks within existing templates
- [ ] 2.3 Create migration mapping: old templates → composable blocks

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
      determines: [section_count, detail_level]
    
    orchestrator_type:
      values: [planning, tdd, debug, lens, refinement, sanitization, documentation, ado]
      determines: [specialized_blocks, validation_sections]

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
- [ ] 4.1 Generate Planning orchestrator templates (plan_creation, plan_execution, plan_completion)
- [ ] 4.2 Generate TDD orchestrator templates (test_run, red_phase, green_phase, refactor_phase)
- [ ] 4.3 Generate Debug orchestrator templates (investigation, hypothesis, resolution)
- [ ] 4.4 Generate CORTEX Lens templates (dashboard, health_report, recommendations)
- [ ] 4.5 Generate Refinement orchestrator templates (analysis, improvement, completion)
- [ ] 4.6 Generate Sanitization orchestrator templates (scan, sanitize, report)
- [ ] 4.7 Generate Documentation orchestrator templates (generation, update, review)
- [ ] 4.8 Generate ADO orchestrator templates (story_creation, feature_breakdown, completion)

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

### Phase 5: Composable Blocks Schema
**Estimated:** 45 min | **Deliverables:** 2

**Tasks:**
- [ ] 5.1 Add `composable_blocks` section to `response-templates-v4.yaml`
- [ ] 5.2 Define all generic and specialized blocks with rendering formats

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

### Phase 6: Manifest Updates (All 8)
**Estimated:** 60 min | **Deliverables:** 8

**Tasks:**
- [ ] 6.1 Update `planning-system-4.0-manifest.yaml` with `response_templates`
- [ ] 6.2 Update `tdd-orchestrator-v4-manifest.yaml` with `response_templates`
- [ ] 6.3 Update `debug-orchestrator-manifest.yaml` with `response_templates`
- [ ] 6.4 Update `cortex-lens-v3-manifest.yaml` with `response_templates`
- [ ] 6.5 Update `refinement-orchestrator-manifest.yaml` with `response_templates`
- [ ] 6.6 Update `code-sanitization-manifest.yaml` with `response_templates`
- [ ] 6.7 Update `technical-documentation-orchestrator-manifest.yaml` with `response_templates`
- [ ] 6.8 Verify `ado-planning-manifest.yaml` (already has section, may need update)

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

### Phase 7: Progress Bar Standardization
**Estimated:** 30 min | **Deliverables:** 2

**Tasks:**
- [ ] 7.1 Update all progress templates to use standardized format
- [ ] 7.2 Ensure consistent: 10-char width, `█░` chars, ✅🔄⏳❌⏸️ icons

**Output:** Updated progress templates in `response-templates-v4.yaml`

---

### Phase 8: Validation & REFACTOR (SKULL Rule)
**Estimated:** 45 min | **Deliverables:** 5

**Tasks:**
- [ ] 8.1 Validate all YAML syntax
- [ ] 8.2 Count `response_templates` occurrences (target: 8 manifests)
- [ ] 8.3 Verify `template_selection_algorithm` is complete
- [ ] 8.4 Test CORTEX response rendering with new system
- [ ] 8.5 **REFACTOR:** Remove deprecated templates, clean up duplicates

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
| `composable_blocks` section exists | ⏳ |
| All 8 manifests have `response_templates` | ⏳ |
| Orchestrator-specific templates generated | ⏳ |
| Progress bars use standardized format | ⏳ |
| All YAML files pass syntax validation | ⏳ |
| No breaking changes to existing functionality | ⏳ |
| REFACTOR phase completed (SKULL rule) | ⏳ |

---

## 📌 copilot_instructions

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: false  # Schema changes only, no code
final_refactor_required: true
progress_tracker: "tracking/progress-tracker.json"
algorithm_design: true
orchestrator_template_generation: true
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
