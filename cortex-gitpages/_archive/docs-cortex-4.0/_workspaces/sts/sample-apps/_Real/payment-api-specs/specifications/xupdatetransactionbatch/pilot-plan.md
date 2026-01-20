# Pilot Project: XUpdateTransactionBatch Legacy API Modernization

**Project ID:** PILOT-001  
**API:** XUpdateTransactionBatch  
**Status:** 🎯 READY TO START  
**Timeline:** 1 week  
**Date:** December 15, 2025

---

## 🎯 Objectives

Validate the **3-phase specification-first migration workflow** with a simple, low-risk API:

1. **Phase 1:** Generate business specification from legacy code
2. **Phase 2:** Design Clean Architecture implementation
3. **Phase 3:** Implement with TDD (RED→GREEN→REFACTOR)

**Success Criteria:**
- ✅ Complete all 3 phases in 1 week
- ✅ PM/BA approval on business specification
- ✅ Zero domain boundary violations
- ✅ 80%+ test coverage
- ✅ 100% spec-to-code traceability

---

## 📋 Why XUpdateTransactionBatch?

**Complexity:** LOW (ideal for pilot)
- Simple PATCH operation
- Minimal business logic (status update + invoice association)
- No complex calculations
- No cross-domain calls

**Legacy Location:** `Platform.Classic/Segment4/PaymentTransactions/XUpdateTransactionBatch.cs`

**Existing Complexity Metrics:**
- Cyclomatic Complexity: 3 (well below threshold)
- Lines of Code: ~50-80 (estimated)
- Business Rules: 2-3 simple rules

**Risk:** MINIMAL
- Won't impact critical transaction flows
- Easy to rollback
- Existing tests can validate parity

---

## 📅 Timeline (1 Week)

### Day 1-2: Phase 1 - Business Specification

**Agent:** `legacy-specification-generator`

**Tasks:**
- [ ] Parse `XUpdateTransactionBatch.cs`
- [ ] Extract business rules (status update, invoice linking)
- [ ] Identify preconditions and validation rules
- [ ] Document data flow (input → validate → update → persist)
- [ ] Create layer mapping (Domain/UseCase/Infrastructure)
- [ ] Generate Mermaid diagrams

**Deliverables:**
- `business-spec.md`
- `data-flow.mmd`
- `layer-mapping.md`
- `review-checklist.md`

**Review:** PM/BA approval checkpoint (2-hour meeting)

---

### Day 3: Phase 2 - Technical Design

**Agent:** `modern-architecture-designer`

**Tasks:**
- [ ] Design 5-layer project structure
- [ ] Create REST endpoint: `PATCH /api/v1/ra/transaction-batches/{id}`
- [ ] Define entities (TransactionBatch in Domain)
- [ ] Define repository interface (ITransactionBatchRepository in Domain)
- [ ] Design UseCase (UpdateTransactionBatchUseCase)
- [ ] Create DTO wrappers (UpdateTransactionBatchRequest, TransactionBatchResponse)
- [ ] Validate project references

**Deliverables:**
- `technical-design.md`
- `project-structure.txt`
- `architecture.mmd`
- `dependency-matrix.md`
- `traceability-template.csv`

**Validation:**
- Run `project_reference_validator.py`
- Verify layer dependencies
- Ensure NO cross-domain entity exposure

---

### Day 4-5: Phase 3 - TDD Implementation

**Agent:** `tdd-implementation-orchestrator`

**RED Phase (Day 4 AM):**
- [ ] Write failing domain validator tests
- [ ] Write failing use case tests (mocked dependencies)
- [ ] Write failing controller integration tests
- [ ] Run tests → ALL FAIL ✅

**GREEN Phase (Day 4 PM - Day 5 AM):**
- [ ] Implement Domain entities (TransactionBatch)
- [ ] Implement Domain validator
- [ ] Implement UseCase (UpdateTransactionBatchUseCase)
- [ ] Implement Repository (TransactionBatchRepository with EF Core)
- [ ] Implement Controller (TransactionBatchController)
- [ ] Run tests → ALL PASS ✅

**REFACTOR Phase (Day 5 PM):**
- [ ] Remove any custom implementations (use OOB .NET)
- [ ] Add XML documentation with spec traceability
- [ ] Run `domain_boundary_checker.py` → ZERO violations
- [ ] Verify project references → ALL valid
- [ ] Final test run → 100% pass, 80%+ coverage

**Deliverables:**
- `HealthEquity.PaymentProcessor.DomainCore/Entities/TransactionBatch.cs`
- `HealthEquity.PaymentProcessor.DomainCore/Repositories/ITransactionBatchRepository.cs`
- `HealthEquity.PaymentProcessor.UseCase/Batches/UpdateTransactionBatchUseCase.cs`
- `HealthEquity.PaymentProcessor.Data.SqlServer/Repositories/TransactionBatchRepository.cs`
- `HealthEquity.PaymentProcessor.Api.Host/Controllers/TransactionBatchController.cs`
- Test projects (unit + integration tests)
- `traceability.csv` (updated with actual code references)

---

## 🧪 Validation Checklist

### Business Specification Quality
- [ ] PM can understand all business rules without code knowledge
- [ ] BA validated all preconditions and error scenarios
- [ ] All legacy behavior documented
- [ ] Layer mapping complete (Domain/UseCase/Infrastructure)
- [ ] <5% clarification requests

### Technical Design Quality
- [ ] 5 separate .csproj files created
- [ ] All project references valid (validated by tool)
- [ ] No domain boundary violations (validated by tool)
- [ ] All external entities wrapped in DTOs
- [ ] Sequence diagram matches data flow

### Implementation Quality
- [ ] All tests pass (100% pass rate)
- [ ] Test coverage ≥ 80%
- [ ] Every business rule has corresponding test
- [ ] Spec-to-code traceability complete
- [ ] Zero compiler warnings
- [ ] Code review approved

### Process Metrics
- [ ] Total time ≤ 5 days (1 week)
- [ ] PM/BA approval time ≤ 2 hours
- [ ] Rework cycles ≤ 1 (minimal iterations)
- [ ] Documentation complete and useful

---

## 🎓 Learning Objectives

### What We Want to Learn

1. **Specification Quality:**
   - Can agents extract business rules accurately from legacy code?
   - Can PM/BA validate specifications without technical expertise?
   - How complete is the auto-generated specification?

2. **Architecture Design:**
   - Do agents correctly apply Clean Architecture layers?
   - Are project references valid on first attempt?
   - How well do agents map legacy components to layers?

3. **Implementation Speed:**
   - Does TDD workflow produce correct code faster?
   - How effective is RED→GREEN→REFACTOR for quality?
   - Are tests comprehensive enough to catch regressions?

4. **Process Efficiency:**
   - Is 3-phase workflow faster than direct migration?
   - Where are bottlenecks (specification, design, implementation)?
   - What tooling gaps exist?

5. **Artifact Value:**
   - Are specifications useful for future maintenance?
   - Do diagrams help onboarding?
   - Is traceability matrix actionable?

---

## 📊 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Time to Complete** | ≤ 5 days | ___ | ⏳ |
| **PM/BA Approval** | 1st attempt | ___ | ⏳ |
| **Spec Clarifications** | < 5% | ___% | ⏳ |
| **Test Coverage** | ≥ 80% | ___% | ⏳ |
| **Boundary Violations** | 0 | ___ | ⏳ |
| **Project Reference Errors** | 0 | ___ | ⏳ |
| **Traceability** | 100% | ___% | ⏳ |
| **Rework Cycles** | ≤ 1 | ___ | ⏳ |

---

## 🚀 Next Steps After Pilot

### If Successful (Metrics Met):
1. **Scale to Complex APIs:**
   - XGenerateTransactionInvoice (medium complexity)
   - XCloseTransactionBatch (high complexity)
   
2. **Refine Process:**
   - Update agent prompts based on learnings
   - Enhance validation tools
   - Create reusable templates

3. **Build Knowledge Base:**
   - Add common PaymentProcessor patterns to `domain-patterns.yaml`
   - Document anti-patterns discovered
   - Create onboarding guide

### If Unsuccessful (Metrics Not Met):
1. **Identify Gaps:**
   - Where did process break down?
   - What agent capabilities missing?
   - What tooling needed?

2. **Adjust Workflow:**
   - Simplify phases if needed
   - Add human checkpoints
   - Improve prompts

3. **Retry with Adjustments:**
   - Same API, refined process
   - Measure improvement

---

## 📁 Artifact Storage

**Location:** `cortex_brain/documents/pilot-projects/xupdatetransactionbatch/`

**Structure:**
```
xupdatetransactionbatch/
├── phase1-specification/
│   ├── business-spec.md
│   ├── data-flow.mmd
│   ├── layer-mapping.md
│   └── review-checklist.md
├── phase2-design/
│   ├── technical-design.md
│   ├── project-structure.txt
│   ├── architecture.mmd
│   ├── dependency-matrix.md
│   └── traceability-template.csv
├── phase3-implementation/
│   ├── test-results.md
│   ├── coverage-report.html
│   ├── traceability.csv (final)
│   └── code-review.md
└── pilot-retrospective.md (lessons learned)
```

---

## 🔍 Retrospective Template

After completion, document:

**What Went Well:**
- ...

**What Didn't Go Well:**
- ...

**Surprises:**
- ...

**Action Items:**
- ...

**Recommendations:**
- Process changes?
- Tooling enhancements?
- Agent improvements?

---

**Pilot Owner:** [Assign PM/Lead]  
**Start Date:** TBD  
**Expected Completion:** 1 week from start

---

**Status:** 🎯 READY TO LAUNCH  
**Prerequisites:** ✅ All documentation complete, tooling ready
