# Phase [N]: [Phase Name]

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** [X-Y] hours + 1 hour holistic review  
**Dependencies:** Phase [N-1] complete + reviewed  
**Storage:** [SQLite/Config/etc.]  
**Performance Target:** [Specific targets]  

---

## 🎯 Overview

**Purpose:** [What this phase builds]

**Key Deliverables:**
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

---

## 📊 What We're Building

[Detailed description of components, schemas, APIs, etc.]

---

## 🏗️ Implementation Tasks

### Task 1: [Task Name]
**File:** [Path]
**Duration:** [X] hours  
**Tests:** [N] unit tests

**Description:**
[What this task accomplishes]

**Implementation Details:**
```python
# Code examples
```

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

---

### Task 2: [Task Name]
**File:** [Path]
**Duration:** [X] hours  
**Tests:** [N] unit tests

[Similar structure...]

---

## 📋 Test Plan ([N] Unit + [M] Integration = [Total] Total)

### Unit Tests ([N] tests)
**[Component] ([X] tests):**
- [ ] `test_[feature]()`
- [ ] `test_[another_feature]()`
[...]

### Integration Tests ([M] tests)
- [ ] `test_[integration_scenario]()`
[...]

---

## ⚡ Performance Benchmarks

### [Benchmark Category]
```python
def test_[benchmark_name]():
    """Ensure [metric] meets target"""
    # Test code
    assert metric < target
```

**Targets:**
- [Metric 1]: [Target]
- [Metric 2]: [Target]

---

## 🎯 Success Criteria

**Phase [N] complete when:**
- ✅ All [N] unit tests passing
- ✅ All [M] integration tests passing
- ✅ [Benchmark 1] met
- ✅ [Benchmark 2] met
- ✅ Integration with Phase [N-1] validated
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **[Doc Type]:** `[path/to/doc.md]`
2. **[Doc Type]:** `[path/to/doc.md]`

---

## 🔍 MANDATORY: Holistic Review (Phase [N] Complete)

**⚠️ DO NOT PROCEED TO PHASE [N+1] UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase [N] Section

#### 1. Design Alignment ✅
- [ ] [Design question 1]?
- [ ] [Design question 2]?
- [ ] [Design question 3]?

#### 2. Implementation Quality ✅
- [ ] All unit tests passing?
- [ ] All integration tests passing?
- [ ] Code quality high?
- [ ] Documentation complete?

#### 3. Performance Validation ✅
- [ ] [Benchmark 1] met?
- [ ] [Benchmark 2] met?
- [ ] [Benchmark 3] met?

#### 4. Integration with Previous Phases ✅
- [ ] Phase [N-1] integration working?
- [ ] Cross-tier queries tested?
- [ ] Governance rules enforced?

#### 5. Integration Readiness for Next Phase ✅
- [ ] APIs ready for Phase [N+1]?
- [ ] Data format compatible?
- [ ] No blocking issues?

#### 6. Adjustments Needed
- [ ] [Potential adjustment area 1]?
- [ ] [Potential adjustment area 2]?
- [ ] [Potential adjustment area 3]?

### Review Output Document
**Create:** `cortex-design/reviews/phase-[N]-review.md`

**Template:**
```markdown
# Phase [N] Review Report

**Date:** [Date]
**Phase:** [Phase Name]
**Status:** ✅ Pass / ⚠️ Pass with Adjustments / ❌ Fail

## Summary
[1-2 paragraphs on overall assessment]

## Design Alignment
[Checklist results]

## Implementation Quality
[Checklist results]

## Performance Validation
[Benchmark results]

## Integration Assessment
[Integration test results]

## Adjustments Required
[List of changes needed before next phase]

## Plan Updates
[Changes to subsequent phases based on learnings]

## Recommendation
[Proceed / Fix Issues / Major Revision]
```

### Actions After Review

#### If Review PASSES ✅
1. **Commit review document:**
   ```bash
   git add cortex-design/reviews/phase-[N]-review.md
   git commit -m "docs(cortex): Phase [N] holistic review complete - PASS"
   ```

2. **Update next phase plan based on findings:**
   ```bash
   git add cortex-design/phase-plans/phase-[N+1]-*.md
   git commit -m "docs(cortex): Update Phase [N+1] plan with Phase [N] learnings"
   ```

3. **THEN proceed to Phase [N+1] implementation**

#### If Review REQUIRES ADJUSTMENTS ⚠️
1. Document minor issues in review report
2. Create quick fix checklist
3. Implement fixes
4. Re-validate affected tests
5. Update review report with "PASS with adjustments"
6. Proceed to next phase

#### If Review FAILS ❌
1. Document critical issues in review report
2. Create detailed fix plan with estimates
3. Implement fixes
4. Re-run complete test suite
5. Re-run review checklist
6. Only proceed when PASS achieved

### Success Metrics for Phase [N]
- ✅ All tests passing ([Total] total)
- ✅ All benchmarks met
- ✅ Integration validated
- ✅ Review report created and approved
- ✅ Next phase plan updated with learnings

### Learning Capture
**Document in review:**
- What worked well?
- What was harder than expected?
- What assumptions were wrong?
- What should change in next phases?

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 + Task 2 | [X] | [X] |
| 2 | Task 3 + Task 4 | [X] | [Y] |
| 3 | Integration tests + Docs | [X] | [Z] |
| 4 | **Holistic Review** | 1 | [Total] |

**Total Estimated:** [X-Y] hours implementation + 1 hour review = [Total] hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All unit tests written and passing
- [ ] All integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Next phase plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase [N+1] ready to start

---

**Status:** Ready for implementation  
**Next:** Begin after Phase [N-1] review complete  
**Estimated Completion:** [X-Y] hours + 1 hour review  
**⚠️ CRITICAL:** Complete holistic review before Phase [N+1]!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-[N-1]-[name].md` - Previous phase
- `phase-[N+1]-[name].md` - Next phase  
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
