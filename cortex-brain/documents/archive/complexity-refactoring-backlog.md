# Code Complexity Refactoring Backlog

**Generated:** December 16, 2025  
**Source:** Refinement Orchestrator  
**Total Functions Identified:** 169 high-complexity functions (complexity > 15)

---

## 🎯 Top 20 Priority Targets

These functions have the highest cyclomatic complexity and should be prioritized for refactoring:

### Critical Priority (Complexity > 30)

1. **`align_system_v2`** - Complexity: 56
   - **File:** `src/operations/modules/realignment/realignment_utility.py:491`
   - **Impact:** Core system alignment functionality
   - **Suggestion:** Break into phase-specific alignment functions

2. **`_check_rule`** - Complexity: 35
   - **File:** `src/tier0/brain_protector.py:249`
   - **Impact:** SKULL rule validation (critical path)
   - **Suggestion:** Extract rule-specific validators

3. **`build_pr_context`** - Complexity: 35
   - **File:** `src/operations/modules/pr/pr_context_utility.py:318`
   - **Impact:** PR context generation
   - **Suggestion:** Separate context collection from formatting

4. **`generate_master_plan`** - Complexity: 34
   - **File:** `src/operations/modules/planning/unified_plan_generator.py:167`
   - **Impact:** Planning System core
   - **Suggestion:** Extract phase generators

5. **`_parse_markdown_plan`** - Complexity: 33
   - **File:** `src/utils/plan_file_resolver.py:261`
   - **Impact:** Plan parsing
   - **Suggestion:** Use state machine pattern

6. **`_generate_enhanced_what_it_does`** - Complexity: 32
   - **File:** `src/dashboard/aggregators/enhanced_executive_summary_aggregator.py:335`
   - **Impact:** Dashboard summary generation
   - **Suggestion:** Template-based generation

7. **`run`** - Complexity: 32
   - **File:** `src/operations/modules/admin/alignment_validators.py:73`
   - **Impact:** Alignment validation
   - **Suggestion:** Break into validator classes

8. **`_detect_framework_evidence`** - Complexity: 31
   - **File:** `src/dashboard/validators/data_validator.py:188`
   - **Impact:** Framework detection
   - **Suggestion:** Plugin-based detection system

9. **`validate`** - Complexity: 31
   - **File:** `src/operations/modules/admin/gap_remediation_validator.py:31`
   - **Impact:** Gap analysis
   - **Suggestion:** Separate validation concerns

10. **`_consolidate_markdown_docs`** - Complexity: 30
    - **File:** `src/operations/optimize_operation.py:703`
    - **Impact:** Documentation optimization
    - **Suggestion:** Extract document processors

### High Priority (Complexity 25-29)

11. **`_detect_application_type`** - Complexity: 29
    - **File:** `src/dashboard/data/architecture_collector.py:97`

12. **`_parse_connection_strings`** - Complexity: 29
    - **File:** `src/dashboard/data/tech_stack_collector.py:413`

13. **`detect_changes`** - Complexity: 29
    - **File:** `src/utils/doc_sync_hooks.py:67`

14. **`extract_entities`** - Complexity: 28
    - **File:** `src/agents/estimation/scope_inference_engine.py:152`

15. **`detect_project_structure`** - Complexity: 27
    - **File:** `src/operations/modules/setup/master_setup_utility.py:184`

16. **`_run_lint_checks`** - Complexity: 26
    - **File:** `src/operations/modules/generators/legacy_spec_generator.py:2197`

17. **`_format_markdown`** - Complexity: 26
    - **File:** `src/entry_point/response_formatter.py:297`

18. **`extract_task_metrics_from_git`** - Complexity: 26
    - **File:** `src/tier3/context_intelligence.py:1406`

19. **`count_tests_in_files`** - Complexity: 26
    - **File:** `src/utils/incremental_test_runner.py:56`

20. **`_collect_backend`** - Complexity: 26
    - **File:** `src/dashboard/data/tech_stack_collector.py:105`

---

## 📊 Complexity Distribution

| Complexity Range | Count | Priority |
|------------------|-------|----------|
| 56 | 1 | 🔴 Critical |
| 30-35 | 9 | 🔴 Critical |
| 25-29 | 10 | 🟠 High |
| 20-24 | 28 | 🟡 Medium |
| 16-19 | 121 | 🟢 Low |

---

## 🎯 Refactoring Strategies

### Strategy 1: Extract Method
**Best for:** Long functions with distinct sections
**Example:** `align_system_v2` → `align_tier0()`, `align_tier1()`, etc.

### Strategy 2: Strategy Pattern
**Best for:** Multiple conditional branches
**Example:** `_check_rule` → Rule validator classes

### Strategy 3: Template Method
**Best for:** Repeated patterns with variations
**Example:** `generate_master_plan` → Phase template classes

### Strategy 4: State Machine
**Best for:** Complex parsing/flow control
**Example:** `_parse_markdown_plan` → Parser state machine

### Strategy 5: Plugin Architecture
**Best for:** Detection/collection logic
**Example:** `_detect_framework_evidence` → Framework plugins

---

## 🚀 Implementation Approach

### Phase 1: Critical Functions (Complexity > 30)
- **Effort:** 2-3 weeks
- **Impact:** High - Core functionality stability
- **Risk:** Medium - Requires comprehensive testing

### Phase 2: High Priority (Complexity 25-29)
- **Effort:** 3-4 weeks
- **Impact:** Medium - Improved maintainability
- **Risk:** Low - Less critical paths

### Phase 3: Medium Priority (Complexity 20-24)
- **Effort:** 4-6 weeks
- **Impact:** Low - Code quality improvement
- **Risk:** Very Low - Incremental improvements

### Phase 4: Low Priority (Complexity 16-19)
- **Effort:** Ongoing
- **Impact:** Very Low - Nice to have
- **Risk:** None - Opportunistic refactoring

---

## 📋 Refactoring Checklist

For each function refactored:

- [ ] Create comprehensive test coverage (>90%)
- [ ] Document refactoring rationale
- [ ] Run SKULL validation
- [ ] Update related documentation
- [ ] Measure complexity reduction
- [ ] Profile performance impact
- [ ] Update orchestrator manifests if needed
- [ ] Generate before/after metrics

---

## 🔍 Tracking Progress

**Repository:** github.com/asifhussain60/CORTEX  
**Branch Strategy:** `refactor/complexity-reduction`  
**Issue Label:** `tech-debt`, `complexity-refactoring`  
**Milestone:** CORTEX 4.0 - Code Quality

---

## 📚 References

- **Cyclomatic Complexity:** McCabe's threshold of 10 (we use 15 for complex orchestrators)
- **SOLID Principles:** Single Responsibility focus
- **Refactoring Patterns:** Martin Fowler's catalog
- **CORTEX Standards:** `cortex-brain/brain-protection-rules.yaml`

---

**Next Review:** After Phase 1 completion  
**Owner:** Development Team  
**Status:** 📋 Backlog Ready
