# Phase 7: Script Orchestration Testing

**Phase ID:** P007 | **Duration:** 1 week | **Status:** ⏸️ NOT STARTED | **Priority:** 🔥 HIGH

---

## 🎯 Phase Objective

Validate script consolidation from Phase 1.5 with comprehensive testing of toolkit orchestrator and governance rule enforcement.

---

## 📦 Features Included

| Feature ID | Name | Status | Dependencies | Priority |
|------------|------|--------|--------------|----------|
| **F004** | Testing Framework (Extension) | ⏸️ Pending | F003, F004 | 🔥 HIGH |
| **F002** | Governance Rules (Rule #7 Enforcement) | ⏸️ Pending | F003 | 🔥 HIGH |

---

## ✅ Acceptance Criteria

- [ ] Toolkit orchestrator integration tests (10 tests)
- [ ] Script consolidation validation (zero regression)
- [ ] Duplicate detection accuracy tests (5 tests)
- [ ] Catalog registration tests (3 tests)
- [ ] Pre-commit hook validation tests (2 tests)
- [ ] CI/CD pipeline tests (2 tests)
- [ ] Rule #7 enforcement validation (4 tests)
- [ ] Performance benchmarks (<30s for 17 scripts)

---

## 🔗 Dependencies

**Requires:**
- Phase 1.5 (F003 Toolkit Orchestration) complete
- Phase 3 (F004 Testing Framework) complete

**Enables:**
- Phase 8 (Knowledge Integration) - clean codebase

---

## 📋 Implementation Tasks

### Week 1: Comprehensive Testing
1. **Toolkit Orchestrator Tests (10 tests)**
   - Master orchestrator workflow
   - Scanner child agent accuracy
   - Consolidator child agent merging
   - Cataloger child agent registration
   - Error handling & rollback
   - Concurrent execution safety

2. **Regression Validation (Zero Failures)**
   - Test all 17 original scripts still work
   - Test consolidated scripts maintain functionality
   - Test import path updates
   - Test backward compatibility

3. **Duplicate Detection Tests (5 tests)**
   - AST similarity detection (≥80% threshold)
   - False positive handling
   - Edge case detection (similar but different)
   - Cross-file dependency mapping

4. **Catalog Registration Tests (3 tests)**
   - script-catalog.yaml completeness
   - Metadata accuracy (purpose, inputs, outputs)
   - Deprecation warnings generated

5. **Governance Enforcement Tests (4 tests)**
   - Pre-commit hook prevents duplicates
   - CI/CD pipeline validates catalog
   - Rule #7 violation detection
   - Enforcement logging

6. **Performance Benchmarks**
   - Consolidation time: 17 scripts → <10 in <30s
   - Memory usage: <500MB peak
   - Catalog generation: <5s

---

## 🧪 Testing Requirements

- **Unit Tests:** 15 tests (orchestrator + children)
- **Integration Tests:** 10 tests (end-to-end workflows)
- **Regression Tests:** 17 tests (original script equivalence)
- **Performance Tests:** 3 benchmarks
- **Coverage Target:** ≥90%

---

## 📈 Success Metrics

- **Regression Rate:** 0% (all scripts work)
- **Duplicate Detection Accuracy:** ≥95%
- **Catalog Completeness:** 100%
- **Consolidation Time:** <30s
- **Test Coverage:** ≥90%

---

## 🔍 Critical Test Scenarios

### Test: Zero Regression
```python
@pytest.mark.parametrize("original_script", ORIGINAL_SCRIPTS)
def test_consolidated_script_maintains_functionality(original_script):
    """Verify consolidated scripts produce same output as originals"""
    original_output = run_script(original_script, test_inputs)
    consolidated_output = run_consolidated_equivalent(original_script, test_inputs)
    assert original_output == consolidated_output
```

### Test: Duplicate Detection
```python
def test_duplicate_detection_accuracy():
    """Verify AST-based duplicate detection with known duplicates"""
    duplicates = [
        ("planning_utils_v1.py", "planning_utils_v2.py"),
        ("validator_old.py", "validator_new.py")
    ]
    for script1, script2 in duplicates:
        similarity = scanner.calculate_similarity(script1, script2)
        assert similarity >= 0.8  # 80% threshold
```

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hidden regression bugs | 🔥 CRITICAL | Extensive test coverage + manual QA |
| Performance degradation | 🟡 MEDIUM | Profiling + optimization |
| Catalog drift | 🟡 MEDIUM | Automated sync + validation |

---

## 🚀 Next Phase

**Phase 8:** Knowledge Graph Integration (F010)

**Handoff Criteria:**
- All tests passing (zero failures)
- Regression rate: 0%
- Performance benchmarks met
- Rule #7 enforcement validated
