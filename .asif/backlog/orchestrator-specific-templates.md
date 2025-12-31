# Orchestrator-Specific Response Templates

**Status:** 📋 Backlog  
**Priority:** Medium  
**Estimated Effort:** 4-8 hours  
**Created:** 2025-12-31  
**Author:** Asif Hussain

---

## 🎯 Overview

Design a composable "LEGO-style" template system where orchestrators can combine specific and generic template blocks in any order while maintaining a consistent copyright header.

---

## 📊 Gap Analysis (Current State)

### Current Classifications

| Category | Status | Location |
|----------|--------|----------|
| **Tier-Based Routing** | ✅ Implemented | `response-templates-v4.yaml` (Tier 1-4) |
| **Custom User Templates** | ✅ 2 templates | `introduction`, `business_value` |
| **Named Templates** | ✅ 3 templates | `autonomous_execution_progress`, `ado_execution_progress`, `progress_bar_simple` |
| **Orchestrator Designation** | ⚠️ Partial | Only ADO manifest has `response_templates` section |

### Orchestrators WITHOUT Designated Templates

| Orchestrator | Manifest File | Has `response_templates` |
|--------------|---------------|--------------------------|
| Planning System 4.0 | `planning-system-4.0-manifest.yaml` | ❌ No |
| TDD Orchestrator | `tdd-orchestrator-v4-manifest.yaml` | ❌ No |
| Debug Orchestrator | `debug-orchestrator-manifest.yaml` | ❌ No |
| CORTEX Lens | `cortex-lens-v3-manifest.yaml` | ❌ No |
| Refinement | `refinement-orchestrator-manifest.yaml` | ❌ No |
| Sanitization | `code-sanitization-manifest.yaml` | ❌ No |
| Technical Docs | `technical-documentation-orchestrator-manifest.yaml` | ❌ No |
| **ADO Planning** | `ado-planning-manifest.yaml` | ✅ Yes |

---

## 🧱 Proposed Architecture: LEGO-Style Composable Templates

### Design Principles

1. **Single Header Block** - Copyright/branding applied ONCE at top
2. **Composable Blocks** - Any block can follow any other block
3. **Orchestrator-Specific Blocks** - Custom blocks per orchestrator
4. **Generic Blocks** - Shared across all orchestrators
5. **Order Independence** - Blocks work in any sequence

### Block Categories

```yaml
block_categories:
  header:
    - cortex_header        # Standard header (ALWAYS first, applied once)
    
  generic_blocks:
    - understanding        # 🎯 Understanding & Scope
    - approach             # ⚡ Approach & Considerations  
    - response             # 💬 Response
    - changes              # 📊 Impact & Changes
    - next_steps           # 🔍 Next Steps
    - context              # 🎯 Context
    - analysis             # ⚡ Analysis
    - results              # 📊 Results
    - cautions             # ⚠️ Cautions
    - validation_status    # ✅ Validation Status
    
  progress_blocks:
    - progress_bar_simple      # [████████░░░░] 60%
    - phase_table              # | Phase | Status | Progress |
    - visual_progress_box      # Unicode box progress
    
  orchestrator_specific:
    tdd:
      - tdd_cycle_status       # RED→GREEN→REFACTOR state
      - test_results_summary   # Pass/Fail/Skip counts
      - coverage_metrics       # Code coverage display
      
    planning:
      - plan_phases            # 4-tier phase breakdown
      - deliverables_matrix    # Deliverables tracking
      - dor_dod_status         # Definition of Ready/Done
      
    ado:
      - work_item_summary      # Epic/Feature/Story/Task counts
      - story_points_tracker   # SP totals by type
      - ado_links              # Azure DevOps URLs
      
    debug:
      - bug_hypothesis         # Investigation hypothesis
      - stack_trace_analysis   # Error analysis
      - fix_verification       # Fix confirmation
      
    lens:
      - health_metrics         # Codebase health scores
      - analytics_summary      # Key analytics
      - trend_indicators       # Up/Down trends
      
    sanitization:
      - sanitization_phases    # 5-phase progress
      - secrets_found          # Secrets detection count
      - cleanup_summary        # What was cleaned
      
    refinement:
      - refinement_phases      # 7-phase progress
      - improvement_metrics    # Before/After comparison
      - quality_scores         # Quality improvement
      
    maintenance:
      - maintenance_phases     # 11-phase pipeline
      - health_report          # System health status
      - auto_repair_summary    # What was fixed
      
    technical_docs:
      - documentation_types    # What docs generated
      - coverage_report        # Doc coverage
      - api_surface            # API documentation
```

### Composition Engine Schema

```yaml
composition_engine:
  version: "1.0"
  
  rules:
    header_rule: "cortex_header MUST be first and applied exactly once"
    composition_rule: "All other blocks can appear in any order"
    repetition_rule: "Blocks can be used multiple times if needed"
    
  template_definition:
    format: |
      template_name: "{orchestrator}_{operation}"
      blocks:
        - cortex_header           # ALWAYS first
        - {block_1}               # Any order from here
        - {block_2}
        - ...
        - {block_n}
      
  rendering_process:
    1_header: "Render cortex_header with operation name"
    2_blocks: "Render each block in defined order"
    3_separator: "Add --- between major sections"
    4_next_steps: "Ensure exactly ONE next action at end"
```

### Example Compositions

**TDD Orchestrator - Test Run:**
```yaml
tdd_test_run:
  blocks:
    - cortex_header           # ## 🧠 CORTEX TDD Test Run
    - understanding           # What test suite is being run
    - tdd_cycle_status        # 🔴 RED → 🟢 GREEN → 🔄 REFACTOR
    - test_results_summary    # 15 passed, 2 failed, 0 skipped
    - coverage_metrics        # 87% coverage
    - next_steps              # Fix failing tests
```

**Planning Orchestrator - Plan Creation:**
```yaml
planning_plan_creation:
  blocks:
    - cortex_header           # ## 🛡️🧠 CORTEX Plan Execution
    - understanding           # Feature scope
    - phase_table             # 4 phases with progress
    - dor_dod_status          # DoR/DoD validation
    - deliverables_matrix     # What will be created
    - validation_status       # All checks passed
    - next_steps              # Begin Phase 1
```

**Debug Orchestrator - Investigation:**
```yaml
debug_investigation:
  blocks:
    - cortex_header           # ## 🧠 CORTEX Debug Session
    - context                 # Error context
    - bug_hypothesis          # Suspected cause
    - stack_trace_analysis    # Error breakdown
    - approach                # Investigation plan
    - next_steps              # Verify fix
```

---

## 📋 Implementation Plan

### Phase 1: Schema Definition (2 hrs)
- [ ] Define block schema in `response-templates-v4.yaml`
- [ ] Create `block_definitions` section with all blocks
- [ ] Add `composition_rules` section

### Phase 2: Generic Blocks (1 hr)
- [ ] Refactor existing sections into standalone blocks
- [ ] Ensure all blocks are self-contained
- [ ] Add block metadata (emoji, title, when_to_use)

### Phase 3: Orchestrator Blocks (2-3 hrs)
- [ ] Create TDD-specific blocks
- [ ] Create Planning-specific blocks
- [ ] Create Debug-specific blocks
- [ ] Create Lens-specific blocks
- [ ] Create Sanitization-specific blocks
- [ ] Create Refinement-specific blocks
- [ ] Create Maintenance-specific blocks
- [ ] Create Technical Docs-specific blocks

### Phase 4: Manifest Updates (1 hr)
- [ ] Add `response_templates` section to all 7 missing manifests
- [ ] Define block compositions per orchestrator operation
- [ ] Reference `response-templates-v4.yaml` block definitions

### Phase 5: Documentation (1 hr)
- [ ] Update `manifest-schema.yaml` with composition rules
- [ ] Document block catalog in README
- [ ] Add usage examples

---

## 📁 File Changes Required

| File | Change |
|------|--------|
| `cortex-brain/response-templates-v4.yaml` | Add `composable_blocks` section |
| `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/cortex-lens-v3-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/technical-documentation-orchestrator-manifest.yaml` | Add `response_templates` |
| `cortex-brain/manifests/orchestrators/manifest-schema.yaml` | Add composition validation |

---

## ✅ Success Criteria

- [ ] All 8 orchestrators have designated templates
- [ ] Blocks can be composed in any order
- [ ] Single header applied consistently
- [ ] Existing templates still work
- [ ] No duplicate code between orchestrators
- [ ] Clear documentation for adding new blocks

---

## 🔗 Related Files

- `cortex-brain/response-templates-v4.yaml` - Main template file
- `cortex-brain/response-templates/base-components.yaml` - Existing components
- `cortex-brain/manifests/orchestrators/` - All orchestrator manifests
- `.github/prompts/CORTEX.prompt.md` - Intent routing
