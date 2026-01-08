# Phase 3: TDD Test Harness for Planning

**Phase ID:** P003 | **Duration:** 2 weeks | **Status:** ⏸️ NOT STARTED | **Priority:** 🔥 HIGH

---

## 🎯 Phase Objective

Build comprehensive 15-test suite validating all planning workflows with RED→GREEN→REFACTOR enforcement and regression prevention.

---

## 📦 Features Included

| Feature ID | Name | Status | Dependencies | Priority |
|------------|------|--------|--------------|----------|
| **F004** | Testing Framework | ⏸️ Pending | F001, F003 | 🔥 HIGH |

---

## ✅ Acceptance Criteria

- [ ] 15-test suite covering all planning workflows
- [ ] Epic parent detection tests (3 tests)
- [ ] Folder structure validation tests (4 tests)
- [ ] Orphan detection tests (2 tests)
- [ ] Goal inheritance tests (3 tests)
- [ ] Script consolidation tests (3 tests)
- [ ] RED→GREEN→REFACTOR cycle enforced
- [ ] Test coverage ≥90% for planning modules
- [ ] Regression test harness (prevents future breaks)
- [ ] CI/CD integration (auto-run on commits)

---

## 🔗 Dependencies

**Requires:**
- Phase 1 (F001 Planning System)
- Phase 1.5 (F003 Toolkit Orchestration)
- Phase 2 (F009 Goal Inheritance) - optional, can run parallel

**Enables:**
- Phase 4 (Response Templates) - validated templates
- Phase 7 (Script Orchestration Testing)

---

## 📋 Implementation Tasks

### Week 1: Test Suite Development
1. **Epic Parent Detection Tests (3 tests)**
   - Test regex pattern matching (7 patterns)
   - Test orphan detection
   - Test nested epic structures

2. **Folder Structure Validation Tests (4 tests)**
   - Test 5-subfolder enforcement
   - Test meaningful naming (max 22 chars)
   - Test file organization rules
   - Test plan-viewer.html generation

3. **Goal Inheritance Tests (3 tests)**
   - Test cascading inheritance
   - Test conflict detection
   - Test mandatory goal validation

4. **Testing Infrastructure**
   - Setup pytest fixtures
   - Mock planning system components
   - Test data generators
   - Assertion helpers

### Week 2: Integration & CI/CD
1. **Script Consolidation Tests (3 tests)**
   - Test duplicate detection
   - Test script merging
   - Test catalog registration

2. **Orphan Detection Tests (2 tests)**
   - Test child plans without parents
   - Test dangling references

3. **RED→GREEN→REFACTOR Enforcement**
   - TDD workflow validation
   - Test-first development checks
   - Refactor quality gates

4. **CI/CD Integration**
   - GitHub Actions workflow
   - Pre-commit hooks
   - Coverage reporting
   - Regression alerts

---

## 🧪 Test Coverage Map

| Module | Tests | Coverage Target |
|--------|-------|----------------|
| `PlanningSystem.detect_epic_parent()` | 3 | 95% |
| `FolderStructureValidator` | 4 | 90% |
| `OrphanDetector` | 2 | 100% |
| `GoalInheritanceResolver` | 3 | 90% |
| `ToolkitOrchestrator` | 3 | 85% |
| **Total** | **15** | **90%** |

---

## 📈 Success Metrics

- **Test Count:** 15 tests (all passing)
- **Coverage:** ≥90% for planning modules
- **Regression Prevention:** 0 broken workflows after changes
- **CI/CD Pass Rate:** 100%
- **Test Execution Time:** <30s

---

## 🔍 Sample Test Cases

### Test: Epic Parent Detection
```python
def test_epic_parent_detection_with_nested_structure():
    """Test regex detects parent epic in nested folder structure"""
    path = "cortex-brain/documents/planning/active/cortex5-epic/child-feature-plan"
    result = PlanningSystem.detect_epic_parent(path)
    assert result == "cortex5-epic"
    assert result.confidence > 0.9
```

### Test: Orphan Detection
```python
def test_orphan_detection_prevents_standalone_child_plans():
    """Test that child plans without parent epic are rejected"""
    with pytest.raises(OrphanPlanError):
        PlanningSystem.create_plan(
            name="child-plan",
            parent=None,  # Missing parent
            plan_type="feature"
        )
```

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test maintenance overhead | 🟡 MEDIUM | Modular test design + fixtures |
| Flaky tests | 🟡 MEDIUM | Deterministic mocks + retry logic |
| Slow test execution | 🟢 LOW | Parallel testing + fast fixtures |

---

## 🚀 Next Phase

**Phase 4:** Response Templates & Accessibility (F005)

**Handoff Criteria:**
- All 15 tests passing
- Coverage ≥90%
- CI/CD pipeline active
- Test documentation complete
