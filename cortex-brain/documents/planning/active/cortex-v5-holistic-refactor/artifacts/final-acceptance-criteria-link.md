# 🎯 Final Acceptance Criteria - Plan Integration

**Plan ID:** cortex-v5-holistic-refactor  
**Created:** January 2, 2026  
**Purpose:** Link to comprehensive acceptance criteria for final validation  

---

## 📋 Acceptance Criteria Reference

This plan's final validation (Phase 10 - REFACTOR & Cleanup) MUST be tested against the comprehensive acceptance criteria document.

**Primary Document:** [`cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md`](../../FINAL-ACCEPTANCE-CRITERIA.md)

---

## 🎯 Plan-Specific Acceptance Criteria

### Bootstrap Phase (Phases 0-4.5)

| Criterion ID | Component | Requirement | Reference |
|--------------|-----------|-------------|-----------|
| **MO-1.1.1** | Master Orchestrator | Pattern matching ≥90% accuracy | Section 1.1 |
| **MO-1.2.1** | Master Orchestrator | Pre-execution hooks validate workspace | Section 1.2 |
| **MO-1.3.1** | Context Middleware | Tier 1 continuation <200 tokens | Section 1.3 |
| **PS-2.1.1** | Planning v5 | Correct folder structure (4 subfolders) | Section 2.1 |
| **PS-2.2.3** | Planning v5 | Final REFACTOR phase exists | Section 2.2 |
| **PS-2.3.1** | Planning v5 | Phase -1 "Knowledge Library" present | Section 2.3 |
| **PS-2.4.1** | Planning v5 | AST scan executes in Phase 0 | Section 2.4 |

### Migration Phase (Phases 5-9)

| Criterion ID | Component | Requirement | Reference |
|--------------|-----------|-------------|-----------|
| **ADO-4.1.1** | ADO Operations | Work item format correct | Section 4.1 |
| **ADO-4.2.1** | ADO Operations | Vision API auto-triggers on images | Section 4.2 |
| **VAC-5.1.1** | Vacuum | Orphaned files detected | Section 5.1 |
| **TDD-3.1.1** | All Orchestrators | RED phase: Test must fail first | Section 3.1 |
| **SKULL-9.1.1** | Git Isolation | CORTEX code never in user repos | Section 9.1 |
| **SKULL-9.3.1** | TDD Enforcement | All orchestrators follow RED→GREEN→REFACTOR | Section 9.3 |

### REFACTOR Phase (Phase 10)

| Criterion ID | Component | Requirement | Reference |
|--------------|-----------|-------------|-----------|
| **SKULL-9.5.1** | REFACTOR | Final REFACTOR phase in all plans | Section 9.5 |
| **SKULL-9.5.2** | REFACTOR | ≥18 cleanup tasks per file category | Section 9.5 |
| **TDD-3.3.1** | REFACTOR | Orphaned function detection runs | Section 3.3 |
| **TDD-3.3.2** | REFACTOR | Duplicate code detection runs | Section 3.3 |
| **ALL-10.3.1** | DoD Validation | DoD checklist in every phase | Section 10.3 |
| **FILE-10.2.1** | File Location | FileLocationValidator integrated into Master Orch | Task 10.2 |
| **FILE-10.2A.1** | File Location | Pre-commit hook blocks direct file writes | Task 10.2A |
| **FILE-10.2A.2** | File Location | CI/CD pipeline fails on file location violations | Task 10.2A |
| **FILE-10.2A.3** | File Location | All 20+ existing violations migrated to write_artifact() | Task 10.2A |
| **REPORT-10.3.1** | Report Removal | No markdown report generation in orchestrators | Task 10.3 |
| **REPORT-10.3.2** | Report Removal | Database query helpers replace report reading | Task 10.3 |
| **REPORT-10.3.3** | Report Removal | 4+ report templates deleted | Task 10.3 |

---

## 🧪 Test Execution Plan

### Phase 10: Final Validation (Before Plan Completion)

```bash
# Step 1: Run all unit tests
pytest tests/unit/ -v --cov=src --cov-report=html

# Step 2: Run integration tests
pytest tests/integration/ -v

# Step 3: Run E2E tests for v5 components
pytest tests/e2e/test_planning_v5_workflow.py -v
pytest tests/e2e/test_master_orchestrator_routing.py -v
pytest tests/e2e/test_cross_session_continuation.py -v

# Step 4: Run SKULL compliance tests
pytest tests/brain_protection/ -v

# Step 5: Run performance benchmarks
pytest tests/benchmarks/test_planning_v5_performance.py --benchmark-only
pytest tests/benchmarks/test_master_orchestrator_routing.py --benchmark-only

# Step 6: Validate file location enforcement (NEW)
python scripts/validate_master_plan.py \
  --plan cortex-v5-holistic-refactor \
  --severity error

# Step 7: Test pre-commit hook (Task 10.2A)
python .github/hooks/pre-commit-file-location-check.py

# Step 8: Validate report removal (Task 10.3)
# Ensure no completion-report templates in orchestrators
grep -r "completion-report" src/orchestrators/ && echo "❌ FAIL: Reports still generated" || echo "✅ PASS: No report generation"

# Step 9: Generate acceptance report
python scripts/generate_acceptance_report.py \
  --plan-id cortex-v5-holistic-refactor \
  --criteria cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md \
  --output cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/reports/final-acceptance-report.md
```

---

## 📊 Acceptance Report Template

The final acceptance report will be generated in Phase 10 using this structure:

```markdown
# CORTEX v5 Holistic Refactor - Final Acceptance Report

**Plan ID:** cortex-v5-holistic-refactor  
**Date:** {timestamp}  
**Tested By:** {tester_name}  
**Test Suite Version:** {version}

## Summary
- **Total Tests:** {total}
- **Passed:** {passed} ({percentage}%)
- **Failed:** {failed}
- **Skipped:** {skipped}

## Bootstrap Phase Results (Phases 0-4.5)
- [x] Master Orchestrator (100%)
  - Pattern matching: 93% accuracy (target: ≥90%) ✅
  - Context middleware: 187 token avg (target: <200) ✅
- [x] Planning System v5 (100%)
  - Folder structure: All 4 subfolders present ✅
  - AST scanning: Executes in Phase 0 ✅
  - Knowledge Library: Phase -1 present ✅

## Migration Phase Results (Phases 5-9)
- [ ] ADO Operations (In Progress)
- [ ] Vacuum Orchestrator (Not Started)
- [ ] Other Orchestrators (Not Started)

## REFACTOR Phase Results (Phase 10)
- [ ] File Location Enforcement (Task 10.2 + 10.2A)
  - [ ] FileLocationValidator integrated into Master Orchestrator
  - [ ] Pre-commit hook blocks direct file writes (100% coverage)
  - [ ] CI/CD pipeline validates file locations
  - [ ] All 20+ existing violations migrated to write_artifact()
  - [ ] Zero bypass methods remaining
- [ ] Report Generation Removal (Task 10.3)
  - [ ] No markdown report generation in 4+ orchestrators
  - [ ] Database query helpers replace report reading
  - [ ] 4+ report templates deleted
  - [ ] Token savings validated (200-500 tokens per execution)
- [ ] Orphaned code detection (Task 10.5+)
- [ ] Duplicate code removal (Task 10.5+)
- [ ] 18+ cleanup tasks (Tasks 10.5-10.9)

## Performance Benchmarks
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pattern matching P95 | <100ms | 87ms | ✅ PASS |
| Planning folder creation | <2s | 1.2s | ✅ PASS |
| Context middleware P95 | <50ms | 41ms | ✅ PASS |

## SKULL Compliance
| Rule | Status | Evidence |
|------|--------|----------|
| TDD_ENFORCEMENT | ✅ PASS | All phases follow RED→GREEN→REFACTOR |
| KNOWLEDGE_LIBRARY_INTEGRATION | ✅ PASS | Phase -1 in all generated plans |
| GIT_ISOLATION | ✅ PASS | No CORTEX files in user repos |
| FILE_ORGANIZATION_ENFORCEMENT | ⏳ IN PROGRESS | Task 10.2 + 10.2A implementation |
| REFACTOR_CODE_CLEANUP_ENFORCEMENT | ⏳ IN PROGRESS | Task 10.3 (report removal) + 18+ tasks |

## Final Verdict
🔄 **IN PROGRESS** (40% complete - Bootstrap phase validated)

**Next Steps:**
- Complete Migration Phase (Phases 5-9)
- Execute REFACTOR Phase (Phase 10)
- Generate final report
```

---

## 🔗 Integration with Planning System v5

### Automatic Acceptance Criteria Generation

Planning System v5 MUST generate plan-specific acceptance criteria during plan creation:

**Implementation Location:** `src/orchestrators/planning/plan_generator_v5.py`

**Method:** `generate_acceptance_criteria(plan_data: Dict[str, Any]) -> str`

**Logic:**
```python
def generate_acceptance_criteria(plan_data: Dict[str, Any]) -> str:
    """
    Generate plan-specific acceptance criteria based on:
    - Phases defined in plan
    - Orchestrators involved
    - SKULL rules applicable
    - Complexity tier
    """
    criteria = []
    
    # Extract orchestrators from phases
    orchestrators = extract_orchestrators(plan_data['phases'])
    
    # Map to acceptance criteria sections
    for orch_id in orchestrators:
        section = ORCHESTRATOR_CRITERIA_MAP.get(orch_id)
        if section:
            criteria.append({
                'orchestrator': orch_id,
                'section': section,
                'criteria_ids': get_criteria_for_orchestrator(orch_id)
            })
    
    # Add SKULL rules
    skull_rules = extract_skull_rules(plan_data)
    for rule in skull_rules:
        criteria.append({
            'rule': rule,
            'section': SKULL_RULE_SECTION_MAP[rule],
            'criteria_ids': get_criteria_for_skull_rule(rule)
        })
    
    # Generate markdown
    return render_acceptance_criteria_markdown(criteria)
```

**Output Location:** `{plan_folder}/artifacts/final-acceptance-criteria-link.md`

---

## 🎯 Success Metrics

This plan is considered **COMPLETE** when:

1. ✅ All test suites pass (≥95% coverage)
2. ✅ All acceptance criteria met (100% in applicable sections)
3. ✅ Performance benchmarks met (all targets)
4. ✅ SKULL compliance validated (100%)
5. ✅ **File location enforcement operational (Tasks 10.2 + 10.2A)**
   - FileLocationValidator integrated into Master Orchestrator
   - Pre-commit hook blocks direct file writes
   - CI/CD pipeline validates file locations
   - All existing violations migrated
6. ✅ **Report generation removed (Task 10.3)**
   - No markdown reports in orchestrators
   - Database is single source of truth
   - Token savings validated
7. ✅ Final acceptance report generated
8. ✅ Stakeholder sign-off obtained

**Rejection Criteria:**
- Any SKULL compliance test failure → Plan incomplete
- Performance benchmark miss by >20% → Requires optimization
- Test coverage <90% → Requires additional tests
- **File location violations detected → Task 10.2A incomplete**
- **Report generation still present → Task 10.3 incomplete**

---

**End of Acceptance Criteria Integration**
