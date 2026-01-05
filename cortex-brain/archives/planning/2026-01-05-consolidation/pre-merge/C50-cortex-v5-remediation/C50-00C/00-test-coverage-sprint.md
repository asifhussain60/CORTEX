# 🧪 Sub-Plan 00C: Test Coverage Sprint

**Plan ID:** test-coverage-sprint  
**Parent Epic:** CORTEX-5.0 Gap Remediation  
**Order:** 00C  
**Created:** January 3, 2026  
**Updated:** January 4, 2026  
**Priority:** 🚨 CRITICAL VALIDATION  
**Duration:** 2-3 weeks  
**Status:** 🔒 Blocked (requires 00B complete)  
**Dependencies:** Epic & Feature Planner (00B) must be functional

---

## 📊 Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏳ NOT STARTED

| Phase | Name | Progress | Tests | Status |
|-------|------|----------|-------|--------|
| 1 | Brain Protection Tests | `░░░░░░░░░░` 0% | 0/25 | ⏳ Not Started |
| 2 | Common Orchestrator Tests | `░░░░░░░░░░` 0% | 0/15 | ⏳ Not Started |
| 3 | Middleware Tests | `░░░░░░░░░░` 0% | 0/5 | ⏳ Not Started |
| 4 | Planning v5 Tests | `░░░░░░░░░░` 0% | 0/15 | ⏳ Not Started |
| 5 | TDD Tests | `░░░░░░░░░░` 0% | 0/8 | ⏳ Not Started |
| 6 | ADO Tests | `░░░░░░░░░░` 0% | 0/6 | ⏳ Not Started |
| 7 | Vacuum Tests | `░░░░░░░░░░` 0% | 0/5 | ⏳ Not Started |
| 8 | Lens Tests | `░░░░░░░░░░` 0% | 0/5 | ⏳ Not Started |

**Total:** 0/84 tests written (Target: 84+ tests for 80% coverage)

---

## 🎯 Objective

**Mission:** Increase test coverage from 15% (20/130 criteria) to 80%+ (104/130 criteria)

**Why Critical:** Without tests, we cannot validate implementations or ensure production readiness.

**Success Criteria:**
- ✅ 84+ new tests written and passing
- ✅ Test coverage ≥80% (104+ of 130 acceptance criteria tested)
- ✅ All brain protection (SKULL) rules have tests
- ✅ All common orchestrator utilities have tests
- ✅ CI/CD pipeline runs all tests automatically

**Gate for Next Sub-Plans:**
- **Gate 1 (50% coverage):** Unlocks Sub-Plans 01-02, 05
- **Gate 2 (80% coverage):** Full confidence for all remaining work

---

## 📋 Phase 1: Brain Protection Tests (25 tests) - HIGHEST PRIORITY

**Duration:** 4-5 days  
**Folder:** `tests/brain_protection/`  
**Priority:** 🚨 CRITICAL

### Tests to Create

**File:** `tests/brain_protection/test_tdd_enforcement.py` (5 tests)
```python
# Test TDD_ENFORCEMENT rule
- test_red_phase_required_before_green()
- test_green_phase_requires_passing_tests()
- test_refactor_phase_after_green_only()
- test_tdd_cycle_state_transitions()
- test_tdd_violations_logged()
```

**File:** `tests/brain_protection/test_holistic_discovery.py` (5 tests)
```python
# Test HOLISTIC_DISCOVERY rule
- test_search_before_create_files()
- test_duplicate_detection_prevents_creation()
- test_semantic_search_runs_first()
- test_grep_search_follows_semantic()
- test_discovery_results_logged()
```

**File:** `tests/brain_protection/test_git_isolation.py` (5 tests)
```python
# Test GIT_ISOLATION rule
- test_cortex_code_never_in_user_repos()
- test_cortex_brain_separate_from_user_files()
- test_git_commits_exclude_cortex_patterns()
- test_isolation_violations_blocked()
- test_isolation_audit_logging()
```

**File:** `tests/brain_protection/test_planning_isolation.py` (5 tests)
```python
# Test PLANNING_ISOLATION rule
- test_planning_commands_create_plans_only()
- test_implementation_patterns_bypass_planning()
- test_plan_vs_implement_detection()
- test_planning_violations_prevented()
- test_planning_audit_trail()
```

**File:** `tests/brain_protection/test_hand_off_protocol.py` (5 tests)
```python
# Test HAND_OFF_PROTOCOL rule
- test_autonomous_orchestrators_hand_off()
- test_guided_orchestrators_no_hand_off()
- test_shield_icon_appears_on_autonomous()
- test_hand_off_confirmation_displayed()
- test_github_copilot_stops_after_hand_off()
```

**Exit Criteria:**
- All 25 tests pass
- Coverage for SKULL rules ≥90%
- Tests run in CI/CD

---

## 📋 Phase 2: Common Orchestrator Tests (15 tests)

**Duration:** 3 days  
**Folder:** `tests/orchestrators/common/`  
**Priority:** HIGH

### Tests to Create

**File:** `tests/orchestrators/common/test_autonomous_execution_progress.py` (5 tests)
```python
# Test autonomous execution progress template
- test_progress_bar_rendering()
- test_phase_status_updates()
- test_concise_mode_output()
- test_verbose_mode_output()
- test_progress_percentage_calculation()
```

**File:** `tests/orchestrators/common/test_git_checkpoints.py` (5 tests)
```python
# Test git checkpoint automation
- test_checkpoint_created_after_phase()
- test_checkpoint_naming_convention()
- test_checkpoint_includes_artifacts()
- test_checkpoint_rollback_works()
- test_checkpoint_validation()
```

**File:** `tests/orchestrators/common/test_dod_validation.py` (5 tests)
```python
# Test Definition of Done validation
- test_dod_checklist_validation()
- test_dor_prerequisites_checked()
- test_incomplete_dod_blocks_completion()
- test_dod_status_reporting()
- test_dod_manual_override_blocked()
```

**Exit Criteria:**
- All 15 tests pass
- Common utilities 100% tested
- Shared code has no regressions

---

## 📋 Phase 3: Middleware Tests (5 tests)

**Duration:** 2 days  
**Folder:** `tests/middleware/`  
**Priority:** HIGH

### Tests to Create

**File:** `tests/middleware/test_cross_session_context.py` (5 tests)
```python
# Test cross-session context middleware
- test_tier1_orchestrator_continuation_under_200_tokens()
- test_tier2_project_fallback()
- test_context_priority_orchestrator_over_project()
- test_continue_resume_patterns_detected()
- test_metadata_only_injection()
```

**Exit Criteria:**
- All 5 tests pass
- Context middleware validated
- Token limits enforced

---

## 📋 Phase 4: Planning v5 Tests (15 tests)

**Duration:** 3 days  
**Folder:** `tests/orchestrators/planning/`  
**Priority:** HIGH

### Tests to Create

**File:** `tests/orchestrators/planning/test_master_plan_content.py` (5 tests)
```python
# Test master plan content validation
- test_visual_progress_tracking_generated()
- test_response_template_reminder_included()
- test_final_refactor_phase_exists()
- test_copilot_instructions_block_present()
- test_refactor_has_18_plus_tasks()
```

**File:** `tests/orchestrators/planning/test_governance_integration.py` (5 tests)
```python
# Test Phase -1 Knowledge Library
- test_phase_minus_one_executes_before_phase_zero()
- test_knowledge_library_consultation_documented()
- test_brain_protection_rules_queried()
- test_knowledge_graph_queries_run()
- test_governance_artifacts_created()
```

**File:** `tests/orchestrators/planning/test_ast_scanning.py` (5 tests)
```python
# Test AST scanning integration
- test_ast_scan_runs_in_phase_zero()
- test_ast_results_include_function_class_counts()
- test_duplicate_code_detection()
- test_orphaned_code_detection()
- test_ast_findings_saved_to_context_folder()
```

**Exit Criteria:**
- All 15 tests pass
- Planning v5 core features validated
- Ready for Sub-Plan 03 (Knowledge Library)

---

## 📋 Phase 5: TDD Tests (8 tests)

**Duration:** 2 days  
**Folder:** `tests/orchestrators/tdd/`  
**Priority:** MEDIUM

### Tests to Create

**File:** `tests/orchestrators/tdd/test_file_location.py` (3 tests)
```python
# Test test file location rules
- test_test_files_in_tests_folder()
- test_test_file_naming_convention()
- test_test_file_mirrors_source_structure()
```

**File:** `tests/orchestrators/tdd/test_refactor_cleanup.py` (5 tests)
```python
# Test REFACTOR phase cleanup
- test_whole_file_cleanup_not_partial()
- test_orphaned_code_removed()
- test_duplicate_code_merged()
- test_unused_imports_removed()
- test_refactor_validation()
```

**Exit Criteria:**
- All 8 tests pass
- TDD workflow validated
- RED→GREEN→REFACTOR enforced

---

## 📋 Phase 6: ADO Tests (6 tests)

**Duration:** 2 days  
**Folder:** `tests/orchestrators/ado/`  
**Priority:** MEDIUM

### Tests to Create

**File:** `tests/orchestrators/ado/test_work_item_generation.py` (3 tests)
```python
# Test ADO work item creation
- test_work_items_generated_from_plan()
- test_story_points_calculated()
- test_work_item_hierarchy_correct()
```

**File:** `tests/orchestrators/ado/test_vision_integration.py` (3 tests)
```python
# Test Vision API integration
- test_image_attachments_analyzed()
- test_vision_context_injected()
- test_vision_findings_in_work_items()
```

**Exit Criteria:**
- All 6 tests pass
- ADO v2 validated
- Vision integration working

---

## 📋 Phase 7: Vacuum Tests (5 tests)

**Duration:** 2 days  
**Folder:** `tests/orchestrators/vacuum/`  
**Priority:** MEDIUM

### Tests to Create

**File:** `tests/orchestrators/vacuum/test_safe_deletion.py` (5 tests)
```python
# Test safe deletion workflow
- test_dry_run_before_actual_deletion()
- test_backup_created_before_deletion()
- test_rollback_works()
- test_git_tracked_files_excluded()
- test_deletion_confirmation_required()
```

**Exit Criteria:**
- All 5 tests pass
- Vacuum v2 validated
- Safe deletion workflow tested

---

## 📋 Phase 8: Lens Tests (5 tests)

**Duration:** 2 days  
**Folder:** `tests/orchestrators/lens/`  
**Priority:** MEDIUM

### Tests to Create

**File:** `tests/orchestrators/lens/test_dashboard_visualization.py` (5 tests)
```python
# Test Lens dashboard generation
- test_html_dashboard_generated()
- test_metrics_calculated()
- test_charts_rendered()
- test_health_scores_computed()
- test_recommendations_generated()
```

**Exit Criteria:**
- All 5 tests pass
- Lens validated
- Dashboard generation working

---

## 🚀 Execution Strategy

### Week 1: Foundation (Phases 1-2)
- Days 1-5: Brain Protection Tests (25 tests)
- Days 6-8: Common Orchestrator Tests (15 tests)
- **Milestone:** 40/84 tests complete (~50% coverage) → **GATE 1 PASSED**

### Week 2: Core Features (Phases 3-5)
- Days 9-10: Middleware Tests (5 tests)
- Days 11-13: Planning v5 Tests (15 tests)
- Days 14-15: TDD Tests (8 tests)
- **Milestone:** 68/84 tests complete (~65% coverage)

### Week 3: Remaining Orchestrators (Phases 6-8)
- Days 16-17: ADO Tests (6 tests)
- Days 18-19: Vacuum Tests (5 tests)
- Days 20-21: Lens Tests (5 tests)
- **Milestone:** 84/84 tests complete (80%+ coverage) → **GATE 2 PASSED**

---

## 📦 Deliverables

### Code Artifacts
1. **84+ Test Files** - All tests written and passing
2. **Test Utilities** - Shared fixtures and mocks
3. **CI/CD Integration** - Automated test runs
4. **Coverage Report** - HTML/JSON coverage metrics

### Documentation
1. **Testing Guide** - How to write and run tests
2. **Test Coverage Report** - Current coverage metrics
3. **Test Patterns** - Reusable test patterns
4. **Troubleshooting Guide** - Common test issues

### Tracking
1. **Daily Progress Log** - Tests written each day
2. **Coverage Dashboard** - Real-time coverage metrics
3. **Blocker Log** - Issues encountered
4. **Lessons Learned** - Testing insights

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Test writing takes > 3 weeks | HIGH | MEDIUM | Prioritize brain protection tests first, accept 50% as Gate 1 |
| Test infrastructure setup delays | MEDIUM | MEDIUM | Use existing pytest patterns, copy from working tests |
| Some criteria hard to test | MEDIUM | LOW | Focus on testable criteria first, document untestable ones |
| CI/CD integration issues | LOW | LOW | Start with local tests, integrate CI/CD in Phase 8 |

---

## ✅ Definition of Done

- [ ] All 84+ tests written
- [ ] All tests pass locally
- [ ] Test coverage ≥80% (104+ criteria)
- [ ] CI/CD runs all tests automatically
- [ ] Test documentation complete
- [ ] Coverage report generated
- [ ] Zero critical test failures
- [ ] **Gate 1 Passed:** ≥50% coverage (unblocks Sub-Plans 01-02)
- [ ] **Gate 2 Passed:** ≥80% coverage (full confidence)

---

**Status:** ⏳ READY TO START  
**Next:** Begin Phase 1 - Brain Protection Tests  
**Dependencies:** None (unblocked)  
**Blocks:** Sub-Plans 01, 02, 05 (waiting for 50% coverage gate)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
