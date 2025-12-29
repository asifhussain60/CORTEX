# Specification Validation Checklist

**API Name:** [API Name]  
**Legacy File:** [Path to legacy file]  
**Specification:** [Path to business-spec.md]  
**Validator:** [Your Name]  
**Date:** [Date]

---

## 📋 Validation Overview

This checklist ensures the specification accurately represents the legacy code behavior
and is complete enough for PM/BA approval and modern implementation.

**Pass Criteria:** ALL sections marked ✅ with no critical issues

---

## 1️⃣ AST Completeness (Automated)

**Tool:** `python tools/ast_completeness_checker.py --legacy [legacy-file] --spec [spec-file]`

### Results

- [ ] **Method Coverage:** ___% (Target: 100%)
  - Total methods in legacy: ___
  - Methods documented in spec: ___
  - Missing methods: [list if any]

- [ ] **Business Rule Coverage:** ___% (Target: 80%+)
  - Total conditions in legacy: ___
  - Rules documented in spec: ___
  - Coverage ratio: ___

- [ ] **Validation Coverage:** ___% (Target: 100%)
  - Total validations in legacy: ___
  - Validations documented in spec: ___
  - Missing validations: [list if any]

- [ ] **Database Operations:** ___% (Target: 100%)
  - Database operations found: ___
  - Data flow section exists: YES / NO
  - All operations documented: YES / NO

**Overall AST Check:** ✅ PASS / ❌ FAIL

**Issues to Address:**
```
[Paste output from ast_completeness_checker.py]
```

---

## 2️⃣ Data Flow Accuracy (Automated)

**Tool:** `python tools/data_flow_validator.py --mermaid [data-flow.mmd] --trace [trace.log]`

### Results

- [ ] **Syntax Validation:** ___% (Target: 100%)
  - sequenceDiagram declared: YES / NO
  - Arrow syntax valid: YES / NO
  - Alt/end blocks balanced: YES / NO

- [ ] **Completeness:** ___% (Target: 100%)
  - Components defined: ___
  - Interactions documented: ___
  - Error paths included: YES / NO

- [ ] **Trace Validation:** ___% (Target: 100%)
  - Execution trace provided: YES / NO
  - All trace paths documented: YES / NO
  - Undocumented paths found: [list if any]

**Overall Data Flow Check:** ✅ PASS / ❌ FAIL

**Quality Score:** ___/100

**Issues to Address:**
```
[Paste output from data_flow_validator.py]
```

---

## 3️⃣ Traceability Coverage (Automated)

**Tool:** `python tools/traceability_calculator.py --legacy [legacy-file] --spec [spec-file] --matrix [matrix-file]`

### Results

- [ ] **Spec Coverage:** ___% (Target: 95%+)
  - Total logic lines: ___
  - Lines referenced in spec: ___

- [ ] **Matrix Coverage:** ___% (Target: 95%+)
  - Total logic lines: ___
  - Lines mapped in matrix: ___
  - Total mappings: ___

- [ ] **Bidirectional Traceability:** PASS / FAIL
  - Spec refs in matrix: YES / NO
  - Matrix entries in spec: YES / NO

- [ ] **Section Coverage:** PASS / FAIL
  - All spec sections mapped: YES / NO
  - Missing sections: [list if any]

**Overall Traceability Check:** ✅ PASS / ❌ FAIL

**Overall Score:** ___/100

**Issues to Address:**
```
[Paste output from traceability_calculator.py]
```

---

## 4️⃣ Business Logic Validation (PM/BA Review)

**Reviewer:** [PM/BA Name]  
**Review Date:** [Date]  
**Duration:** [Hours]

### Specification Clarity

- [ ] **Plain English:** All rules understandable without code knowledge
- [ ] **Examples Provided:** Every rule has concrete examples
- [ ] **Data Values:** Examples use realistic data (not placeholders)
- [ ] **Edge Cases:** Boundary conditions documented

### Business Rule Accuracy

- [ ] **Completeness:** No obvious missing scenarios
- [ ] **Correctness:** Rules match expected business behavior
- [ ] **Consistency:** No contradictions between rules
- [ ] **Traceability:** Can find rule origin in legacy code

### Validation Scenarios

**PM/BA Test Cases:**

| Test Case | Specification Says | Legacy Actual | Match |
|-----------|-------------------|---------------|-------|
| [Scenario 1] | [Expected behavior] | [Actual output] | ✅ / ❌ |
| [Scenario 2] | [Expected behavior] | [Actual output] | ✅ / ❌ |
| [Scenario 3] | [Expected behavior] | [Actual output] | ✅ / ❌ |

**Match Rate:** ___% (Target: 100%)

### Clarification Requests

- [ ] Total questions asked: ___ (Target: <5)
- [ ] All questions resolved: YES / NO

**Issues Raised:**
```
1. [Question/concern from PM/BA]
   Resolution: [How addressed]

2. [Question/concern from PM/BA]
   Resolution: [How addressed]
```

**Overall PM/BA Validation:** ✅ APPROVED / ❌ NEEDS REVISION / ⏳ PENDING

---

## 5️⃣ Layer Mapping Validation (Technical)

**Tool:** `python tools/project_reference_validator.py --validate-mapping --spec [layer-mapping.md]`

### Results

- [ ] **Dependency Coverage:** ___% (Target: 100%)
  - Legacy dependencies identified: ___
  - Dependencies mapped to layers: ___
  - Unmapped dependencies: [list if any]

- [ ] **Layer Isolation:** PASS / FAIL
  - Domain has zero dependencies: YES / NO
  - UseCase depends on Domain only: YES / NO
  - Infrastructure properly isolated: YES / NO

- [ ] **Circular Dependencies:** PASS / FAIL
  - No circular references found: YES / NO
  - Violations: [list if any]

**Overall Layer Mapping Check:** ✅ PASS / ❌ FAIL

**Issues to Address:**
```
[Paste output from project_reference_validator.py]
```

---

## 6️⃣ Differential Testing (Runtime Validation)

**Test Environment:** [DEV/TEST/STAGING]  
**Legacy Version:** [Version/commit]  
**Test Date:** [Date]

### Test Scenarios

**Execute against actual legacy code:**

| Scenario | Input | Spec Prediction | Legacy Output | Match |
|----------|-------|-----------------|---------------|-------|
| Happy Path | [params] | [expected] | [actual] | ✅ / ❌ |
| Invalid Input | [params] | [expected] | [actual] | ✅ / ❌ |
| Error Case 1 | [params] | [expected] | [actual] | ✅ / ❌ |
| Error Case 2 | [params] | [expected] | [actual] | ✅ / ❌ |
| Edge Case | [params] | [expected] | [actual] | ✅ / ❌ |

**Match Rate:** ___% (Target: 100%)

### Discrepancies Found

```
Scenario: [scenario name]
Expected (spec): [what spec predicted]
Actual (legacy): [what legacy did]
Resolution: [Updated spec / Legacy bug documented / etc.]
```

**Overall Differential Testing:** ✅ PASS / ❌ FAIL

---

## 📊 Validation Summary

### Overall Results

| Validation Type | Status | Score/Coverage |
|-----------------|--------|----------------|
| AST Completeness | ✅ / ❌ | ___% |
| Data Flow Accuracy | ✅ / ❌ | ___/100 |
| Traceability Coverage | ✅ / ❌ | ___% |
| PM/BA Validation | ✅ / ❌ | ___ questions |
| Layer Mapping | ✅ / ❌ | ___% |
| Differential Testing | ✅ / ❌ | ___% match |

### Pass/Fail Determination

**Criteria for PASS:**
- ✅ AST Completeness ≥ 95%
- ✅ Data Flow Quality ≥ 85/100
- ✅ Traceability ≥ 95%
- ✅ PM/BA Approved
- ✅ Layer Mapping 100% dependencies mapped
- ✅ Differential Testing 100% match

**Overall Status:** ✅ PASS / ❌ FAIL / ⏳ IN PROGRESS

---

## 🔄 Actions Required

### Before PM/BA Approval

- [ ] Fix AST completeness issues
- [ ] Address data flow validation failures
- [ ] Complete traceability matrix
- [ ] Resolve all clarification requests

### Before Technical Design Phase

- [ ] PM/BA sign-off obtained
- [ ] All validation checks passing
- [ ] Layer mapping validated
- [ ] Differential tests 100% match

### Sign-Off

**PM/BA Approval:**
- Name: ___________________
- Date: ___________________
- Signature: ___________________

**Technical Review:**
- Name: ___________________
- Date: ___________________
- Signature: ___________________

---

## 📝 Notes

**Additional Comments:**
```
[Any additional observations, concerns, or recommendations]
```

**Lessons Learned:**
```
[What worked well, what could be improved for next specification]
```

---

**Validation Complete:** [Date]  
**Next Step:** [Technical Design / Revision / Approval Meeting]
