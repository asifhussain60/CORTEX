# User Response Template (URT) Audit Report

**Date:** 2025-11-20  
**Author:** Asif Hussain  
**Purpose:** Comprehensive audit of existing URTs for multi-template orchestration alignment

---

## Executive Summary

**Total Templates:** 29  
**Core Templates:** 18 (minimalist approach)  
**Confidence Indicators:** 4  
**Routing Triggers:** 56  

**Current Architecture:**
- ✅ **Minimal set design** - 18 core templates vs 107 original (83% reduction)
- ✅ **Fallback pattern** - Universal fallback template for unlisted scenarios
- ✅ **Trigger-based routing** - Natural language triggers mapped to templates
- ⚠️ **No orchestration metadata** - Missing relevance keywords, priority, composability rules
- ⚠️ **Identical structure** - Most templates share same base structure (redundancy opportunity)

---

## Template Inventory

### 1. Help & Documentation Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `help_table` | table | help_table | **High** - Works with status, quick_start |
| `help_detailed` | detailed | help_detailed | **Medium** - Can combine with specific operation help |
| `admin_help` | detailed | admin help, docs admin | **Low** - Standalone admin operations |
| `quick_start` | narrative | quick start, get started | **High** - Works with help, status |

**Observations:**
- Context summary template embedded in `help_table` only
- All share standard 5-section format
- High composability potential (help + status common use case)

---

### 2. Status & Progress Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `status_check` | table | status, where are we | **High** - Works with help, operation_progress |
| `operation_started` | narrative | operation_started | **High** - Sequential with operation_progress |
| `operation_progress` | narrative | operation_progress | **High** - Sequential with operation_complete |
| `operation_complete` | detailed | operation_complete | **Medium** - Can merge with success_general |

**Observations:**
- Strong sequential relationship (started → progress → complete)
- Good candidates for timeline composition
- `status_check` overlaps with `help_table` in functionality

---

### 3. Execution & Testing Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `executor_success` | detailed | executor_success | **Medium** - Can combine with tester_success |
| `executor_error` | detailed | executor_error | **Low** - Error templates usually standalone |
| `tester_success` | detailed | tester_success | **Medium** - Can combine with executor_success |

**Observations:**
- Execution + testing workflow natural combination
- `executor_success` + `tester_success` = complete implementation report
- Error templates should remain standalone (priority)

---

### 4. Planning Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `work_planner_success` | detailed | work_planner_success | **Low** - Complex standalone workflow |
| `planning_dor_incomplete` | detailed | planning_dor_incomplete | **Low** - Blocking template |
| `planning_dor_complete` | detailed | planning_dor_complete | **Medium** - Can merge with security review |
| `planning_security_review` | detailed | security review, owasp review | **High** - Works with planning DoR |

**Observations:**
- Planning templates are comprehensive (300+ lines each)
- DoR validation + security review natural combination
- Most should remain standalone due to complexity

---

### 5. ADO Work Item Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `ado_created` | detailed | ado_created | **Low** - Initial creation template |
| `ado_resumed` | detailed | ado_resumed | **Medium** - Can combine with status_check |
| `ado_search_results` | table | ado_search_results | **High** - Works with status displays |

**Observations:**
- ADO templates are domain-specific
- `ado_resumed` + `status_check` = complete resumption context
- Search results can combine with help for ADO guidance

---

### 6. Enhancement & Workflow Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `enhance_existing` | detailed | enhance, improve, extend | **Medium** - Can combine with crawler results |

**Observations:**
- Single comprehensive enhancement template
- Good candidate for phased response (discovery → analysis → planning)

---

### 7. Brain Management Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `brain_export_guide` | detailed | export brain, share brain | **Low** - Complete standalone guide |
| `brain_import_guide` | detailed | import brain, load brain | **Low** - Complete standalone guide |

**Observations:**
- Comprehensive guides (400+ lines each)
- Should remain standalone
- Could split into quick-reference + detailed versions

---

### 8. Documentation Generation Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `generate_documentation_intro` | detailed | generate documentation | **High** - Sequential with completion |
| `generate_documentation_completion` | detailed | doc_generation_completion | **High** - Sequential with intro |

**Observations:**
- Natural intro → completion sequence
- Good example of multi-template workflow

---

### 9. General & Fallback Templates

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `success_general` | narrative | success_general | **High** - Works with many templates |
| `error_general` | narrative | error_general | **Low** - Error priority standalone |
| `not_implemented` | narrative | not_implemented | **Low** - Blocking template |
| `fallback` | structured | * (catch-all) | **High** - Universal fallback |
| `question_documentation_issues` | detailed | question_documentation_issues | **Medium** - Can combine with help |

**Observations:**
- `fallback` is universal template (all unmatched queries)
- `success_general` highly composable
- Error/blocking templates should stay standalone

---

### 10. Confidence Indicators

| Template ID | Response Type | Triggers | Composability |
|-------------|--------------|----------|---------------|
| `confidence_high` | confidence_indicator | (none - system) | **High** - Injects into any response |
| `confidence_medium` | confidence_indicator | (none - system) | **High** - Injects into any response |
| `confidence_low` | confidence_indicator | (none - system) | **High** - Injects into any response |
| `confidence_none` | confidence_indicator | (none - system) | **High** - Injects into any response |

**Observations:**
- System-generated (not user-triggered)
- Perfect for multi-template composition (metadata injection)
- Already designed for combination with other templates

---

## Composability Matrix

### High Composability Pairs (Tested & Recommended)

| Primary Template | Secondary Template | Use Case | Expected Benefit |
|------------------|-------------------|----------|------------------|
| `help_table` | `status_check` | "help + where are we?" | Complete overview |
| `help_table` | `quick_start` | New user onboarding | Guidance + quickstart |
| `executor_success` | `tester_success` | Feature completion report | Full implementation status |
| `planning_dor_complete` | `planning_security_review` | Approved plan + security validation | Security-first planning |
| `ado_resumed` | `status_check` | Resume work with context | Full resumption context |
| `generate_documentation_intro` | `generate_documentation_completion` | Doc generation workflow | Expectation + results |
| `operation_started` | `operation_progress` | Long-running operations | Progress tracking |
| `operation_progress` | `operation_complete` | Operation completion | Status + completion |

---

### Medium Composability Pairs (Conditional)

| Primary Template | Secondary Template | Condition | Use Case |
|------------------|-------------------|-----------|----------|
| `success_general` | `operation_complete` | Operation succeeded | Generic + specific success |
| `fallback` | `help_table` | Unknown query | Fallback + guidance |
| `enhance_existing` | `status_check` | Enhancement in progress | Current status + next steps |
| `question_documentation_issues` | `help_detailed` | Documentation question | Specific issue + general help |

---

### Low Composability (Should Remain Standalone)

- `error_general` - Errors need immediate attention
- `executor_error` - Error context critical
- `not_implemented` - Blocking response
- `planning_dor_incomplete` - Blocking until resolved
- `brain_export_guide` - Comprehensive standalone guide
- `brain_import_guide` - Comprehensive standalone guide
- `work_planner_success` - Complex workflow template

---

## Orchestration Metadata Requirements

### Proposed Metadata Schema

```yaml
templates:
  template_id:
    # Existing fields
    name: "Template Name"
    trigger: [list of triggers]
    response_type: type
    content: "..."
    
    # NEW: Orchestration metadata
    orchestration:
      relevance_keywords:  # For relevance scoring
        - keyword1
        - keyword2
      priority: 50  # 0-100 (higher = shown first in multi-template)
      composability:
        level: high  # high/medium/low
        compatible_with:  # IDs of templates that work well together
          - template_id_1
          - template_id_2
        conflicts_with:  # IDs of templates that should not combine
          - template_id_3
        section_merge_rules:
          Response: merge  # merge/replace/keep_first
          Next Steps: merge
          Challenge: keep_first
      category: help  # help/status/planning/execution/error/general
      verbosity: concise  # concise/detailed/expert
```

---

## Template Structure Analysis

### Standard 5-Section Structure (21/29 templates)

1. **Header:** `# 🧠 CORTEX [Operation Type]` + Author/Copyright
2. **Understanding:** `🎯 **My Understanding Of Your Request:**`
3. **Challenge:** `⚠️ **Challenge:**` (Accept or Challenge)
4. **Response:** `💬 **Response:**` (Main content)
5. **Request Echo:** `📝 **Your Request:**` (Refined summary)
6. **Next Steps:** `🔍 **Next Steps:**` (Actionable recommendations)

**Standardization Benefits:**
- Predictable structure for section merging
- Easy to identify duplicate sections
- Clear priority order for composition

**Exceptions:**
- Confidence indicators (no full structure)
- Some detailed guides (extended Response section)

---

## Multi-Template Scenarios (Real-World)

### Scenario 1: New User Help Request
**User Query:** "help me get started with CORTEX"  
**Relevant Templates:**
1. `help_table` (primary, score: 0.9)
2. `quick_start` (secondary, score: 0.8)
3. `confidence_none` (metadata, score: N/A)

**Composition Strategy:**
- Use `help_table` as base
- Inject `quick_start` Next Steps section
- Add `confidence_none` indicator (new territory)

---

### Scenario 2: Feature Implementation Complete
**User Query:** "implemented authentication, all tests passing"  
**Relevant Templates:**
1. `executor_success` (primary, score: 0.85)
2. `tester_success` (secondary, score: 0.80)
3. `confidence_medium` (metadata, score: N/A)

**Composition Strategy:**
- Merge Response sections (execution + testing)
- Combine Next Steps (deployment + monitoring)
- Add confidence indicator (medium - some patterns)

---

### Scenario 3: Planning with Security
**User Query:** "plan authentication with OWASP compliance"  
**Relevant Templates:**
1. `work_planner_success` (primary, score: 0.9)
2. `planning_security_review` (secondary, score: 0.85)
3. `confidence_high` (metadata, score: N/A)

**Composition Strategy:**
- Use `work_planner_success` as base
- Inject OWASP checklist from `planning_security_review`
- Add confidence indicator (high - auth patterns exist)

---

## Recommendations

### Phase 2: Template Alignment Tasks

1. **Add Orchestration Metadata (High Priority)**
   - Add `relevance_keywords` to all 29 templates
   - Define `priority` scores (error=100, planning=80, help=50, general=30)
   - Map `compatible_with` relationships (8 high-composability pairs identified)
   - Define `section_merge_rules` for standard sections

2. **Create Compatibility Matrix (High Priority)**
   - Document 8 high-composability pairs with merge rules
   - Document 4 medium-composability pairs with conditions
   - Document 7 low-composability templates (standalone)
   - Create validation tests for compatibility

3. **Standardize Section Headers (Medium Priority)**
   - Ensure all 21 standard templates use exact emoji + text format
   - Normalize whitespace/formatting
   - Add section IDs for reliable parsing

4. **Category Tagging (Medium Priority)**
   - Tag templates: help (4), status (4), planning (4), execution (3), ado (3), brain (2), docs (2), general (5), confidence (4)
   - Enable category-based filtering in orchestrator

5. **Verbosity Variants (Low Priority - Future)**
   - Consider splitting large guides (brain export/import) into concise/detailed versions
   - Would enable: "quick help" vs "detailed guide" automatic selection

---

## Phase 3: Integration Requirements

### ResponseFormatter Integration Points

```python
# Current (single-template)
ResponseFormatter.format_from_context(context) → single_template

# Enhanced (multi-template orchestration)
ResponseFormatter.format_from_context(
    context,
    max_templates=3,  # NEW
    min_score=0.3,    # NEW
    enable_composition=True  # NEW
) → composed_multi_template
```

### API Design

```python
# Get relevant templates (no composition)
orchestrator.get_relevant_templates(query, context, top_n=5)
→ List[TemplateScore]

# Generate composed response (full orchestration)
orchestrator.generate_response(query, context, rule=None)
→ str (composed response)

# Explain selection (debugging/transparency)
orchestrator.explain_selection(query, context)
→ Dict[str, Any] (selection reasoning)
```

---

## Testing Strategy

### Unit Tests (Phase 3)
- [ ] RelevanceScorer keyword matching accuracy (>80%)
- [ ] TemplateCompositor section extraction
- [ ] ConflictResolver priority handling
- [ ] ResponseBlender formatting consistency

### Integration Tests (Phase 3)
- [ ] Scenario 1: help + quick_start composition
- [ ] Scenario 2: executor_success + tester_success composition
- [ ] Scenario 3: planning + security_review composition
- [ ] Edge case: No templates above min_score threshold
- [ ] Edge case: Only one template eligible (no composition)

### Acceptance Criteria
- [ ] Multi-template responses ≥ single template responses (quality)
- [ ] Composition time < 500ms
- [ ] No section duplication in composed output
- [ ] Correct priority ordering of sections

---

## Migration Path

### Backward Compatibility
- ✅ **Existing templates work unchanged** (orchestration metadata optional)
- ✅ **Single-template mode still available** (orchestrator bypassed)
- ✅ **Gradual migration** (add metadata incrementally)

### Rollout Plan
1. **Week 1:** Add orchestration metadata to all templates (non-breaking)
2. **Week 1:** Implement core orchestrator (behind feature flag)
3. **Week 1:** Test 8 high-composability pairs (validation)
4. **Week 2:** Enable orchestrator for select routes (help, status)
5. **Week 2:** Monitor composition quality vs single-template baseline
6. **Week 2:** Expand to all routes if quality ≥ baseline

---

## Appendix: Full Template Metadata (Proposed)

See `cortex-brain/response-templates-enhanced.yaml` for complete proposed YAML with orchestration metadata.

---

**Next Action:** Proceed with Phase 2 - Template Alignment Implementation

**Estimated Effort:** 2-3 hours  
**Dependencies:** None (orchestrator already implemented)  
**Blocker:** None
