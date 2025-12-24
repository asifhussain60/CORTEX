# Phase 4: DoR/DoD Validation System - Architecture Design

**Version:** 1.0  
**Date:** 2025-11-27  
**Author:** Asif Hussain  
**Status:** Design Complete, Implementation In Progress

---

## 1. Executive Summary

Phase 4 implements Definition of Ready (DoR) and Definition of Done (DoD) validation systems with automated quality gates and approval workflows. This ensures work items meet quality standards before starting work and before marking complete.

**Key Goals:**
- ✅ Automated DoR validation (80% minimum score to start work)
- ✅ Automated DoD validation (85% minimum score to complete)
- ✅ Quality gates at key workflow transitions
- ✅ Approval workflow with state management
- ✅ Comprehensive reporting and metrics

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           ADOWorkItemOrchestrator (Entry Point)             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  create_work_item()                                 │   │
│  │     ↓                                                │   │
│  │  validate_dor() → [Gate: Pre-Implementation]        │   │
│  │     ↓                                                │   │
│  │  approve_plan() → Transition to "active"            │   │
│  │     ↓                                                │   │
│  │  [Work Execution - Manual]                          │   │
│  │     ↓                                                │   │
│  │  validate_dod() → [Gate: Pre-Completion]            │   │
│  │     ↓                                                │   │
│  │  mark_complete() → Transition to "completed"        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 Core Components

**1. DoR Validator**
- Validates work item readiness before starting
- 5 categories: Completeness, Clarity, Testability, Security, Context
- Weighted scoring (0-100%)
- Generates validation report

**2. DoD Validator**
- Validates work completion criteria
- 5 categories: Implementation, Testing, Documentation, Quality, Integration
- Weighted scoring (0-100%)
- Generates completion report

**3. Quality Gates**
- Pre-Implementation Gate (DoR >= 80%)
- Pre-Completion Gate (DoD >= 85%)
- Optional Mid-Development Gate

**4. Approval Workflow**
- State transitions: planning → active → review → completed
- Approval stages with requirements
- Auto-approval conditions (optional)

---

## 3. DoR Validation System

### 3.1 Categories and Weights

| Category | Weight | Focus |
|----------|--------|-------|
| Completeness | 30% | All required fields present |
| Clarity | 25% | No ambiguity, clear approach |
| Testability | 20% | Testable acceptance criteria |
| Security | 15% | Security considerations |
| Context | 10% | Git history, clarifications |

### 3.2 Checklist Items

**Completeness (30 points):**
- Title present and descriptive (10 pts)
- Description detailed (10 pts)
- Acceptance criteria (2+ items) (30 pts)
- Work item type specified (10 pts)
- Priority specified (10 pts)
- Assignee identified (5 pts, optional)

**Clarity (25 points):**
- Minimal vague language (ambiguity < 3) (20 pts)
- Technical approach clear (15 pts)
- User flow defined (15 pts)
- Dependencies identified (10 pts, optional)

**Testability (20 points):**
- Acceptance criteria testable (30 pts)
- Test approach mentioned (20 pts)
- Edge cases considered (10 pts, optional)

**Security (15 points):**
- Security review for sensitive work (40 pts)
- PII/GDPR handling addressed (30 pts)
- Access control defined (30 pts)

**Context (10 points):**
- Git history enriched (20 pts)
- Quality score >= 60% (20 pts)
- Clarifications resolved (30 pts)
- High-risk files reviewed (30 pts)

### 3.3 Scoring Algorithm

```python
dor_score = (
    (completeness_score * 0.30) +
    (clarity_score * 0.25) +
    (testability_score * 0.20) +
    (security_score * 0.15) +
    (context_score * 0.10)
)

# Bonus points
if all_optional_complete:
    dor_score += 5
if ambiguity_score == 0:
    dor_score += 5

# Cap at 100
dor_score = min(dor_score, 100)
```

---

## 4. DoD Validation System

### 4.1 Categories and Weights

| Category | Weight | Focus |
|----------|--------|-------|
| Implementation | 30% | Code complete, no placeholders |
| Testing | 30% | Tests created, passing, coverage |
| Documentation | 15% | Docs created, decisions recorded |
| Quality | 15% | Reviewed, no issues, criteria met |
| Integration | 10% | Dependencies resolved, tested |

### 4.2 Checklist Items

**Implementation (30 points):**
- Code implemented (30 pts)
- Files created documented (20 pts)
- Files modified documented (20 pts)
- No placeholder code (10 pts, manual)

**Testing (30 points):**
- Tests created (40 pts)
- Test coverage >= 60% (30 pts)
- All tests passing (30 pts)

**Documentation (15 points):**
- Documentation created (40 pts)
- Technical decisions documented (30 pts)
- API changes documented (15 pts, optional)

**Quality (15 points):**
- Code reviewed (30 pts, manual)
- No known issues (30 pts)
- Acceptance criteria met (40 pts)

**Integration (10 points):**
- Dependencies resolved (30 pts)
- Integration tested (40 pts)
- Deployment ready (30 pts)

### 4.3 Scoring Algorithm

```python
dod_score = (
    (implementation_score * 0.30) +
    (testing_score * 0.30) +
    (documentation_score * 0.15) +
    (quality_score * 0.15) +
    (integration_score * 0.10)
)

# Bonus points
if test_coverage >= 80:
    dod_score += 5
if known_issues == 0:
    dod_score += 5

# Cap at 100
dod_score = min(dod_score, 100)
```

---

## 5. Quality Gates

### 5.1 Pre-Implementation Gate

**Triggered:** When transitioning from "planning" to "active"

**Checks:**
- DoR score >= 80%
- Ambiguity score < 5
- Clarifications complete (if triggered)

**Actions:**
- ✅ Pass: Transition to "active" allowed
- ❌ Fail: Block transition, generate improvement report

### 5.2 Pre-Completion Gate

**Triggered:** When transitioning from "review" to "completed"

**Checks:**
- DoD score >= 85%
- All tests passing
- Documentation present

**Actions:**
- ✅ Pass: Transition to "completed" allowed
- ❌ Fail: Block transition, generate completion report

### 5.3 Mid-Development Gate (Optional)

**Triggered:** Manual check during development

**Checks:**
- Tests created
- Code coverage >= 50%

**Actions:**
- ⚠️ Warning only, doesn't block work

---

## 6. Approval Workflow

### 6.1 Workflow States

```
planning → [DoR Gate] → active → review → [DoD Gate] → completed
             ↓                      ↓
           blocked ← ← ← ← ← ← ← ← blocked
```

**States:**
- `planning` - Initial state, gathering requirements
- `active` - Work in progress
- `review` - Implementation complete, awaiting validation
- `completed` - All gates passed, work done
- `blocked` - Blocked by dependencies or issues

### 6.2 Approval Stages

**Stage 1: DoR Validation**
- Auto-execute: Yes
- Required: Yes
- Validates: Requirements quality
- Output: DoR validation report

**Stage 2: Work Execution**
- Auto-execute: No (manual work)
- Required: Yes
- Validates: N/A
- Output: Implementation summary

**Stage 3: DoD Validation**
- Auto-execute: Yes
- Required: Yes
- Validates: Completion quality
- Output: DoD validation report

**Stage 4: Final Approval**
- Auto-execute: No (manual approval)
- Required: Yes
- Validates: Overall quality
- Output: Approval report

### 6.3 Transition Rules

| From | To | Requirements |
|------|-----|-------------|
| planning | active | DoR score >= 80% |
| active | review | Work summary created |
| review | completed | DoD score >= 85%, Final approval |
| active | blocked | Blockers present |
| blocked | active | Blockers resolved |

---

## 7. Data Structures

### 7.1 Validation Result

```python
@dataclass
class ChecklistItem:
    id: str
    text: str
    passed: bool
    points_earned: int
    points_possible: int
    optional: bool = False
    manual: bool = False
    validation_message: str = ""

@dataclass
class CategoryScore:
    category: str
    score: float  # 0-100
    weight: float  # Decimal (0.30 = 30%)
    items: List[ChecklistItem]
    weighted_score: float  # score * weight

@dataclass
class ValidationResult:
    validation_type: str  # "dor" or "dod"
    overall_score: float  # 0-100
    passed: bool  # True if score >= threshold
    threshold: float  # Minimum passing score
    categories: List[CategoryScore]
    timestamp: datetime
    recommendations: List[str]
```

### 7.2 Approval Record

```python
@dataclass
class ApprovalRecord:
    work_item_id: str
    approval_stage: str
    dor_score: Optional[float]
    dod_score: Optional[float]
    approved: bool
    approver: str  # User or "CORTEX (auto)"
    approval_date: datetime
    comments: str
    quality_gates_passed: List[str]
```

---

## 8. Implementation Plan

### Phase 4.1: DoR Validation (2 hours)

**Tasks:**
1. Create DoRValidator class
2. Implement checklist evaluation
3. Implement category scoring
4. Implement overall scoring with bonuses
5. Generate validation report
6. Unit tests (5 tests)

### Phase 4.2: DoD Validation (2 hours)

**Tasks:**
1. Create DoDValidator class
2. Implement checklist evaluation
3. Implement category scoring
4. Implement overall scoring with bonuses
5. Generate completion report
6. Unit tests (5 tests)

### Phase 4.3: Approval Workflow (1.5 hours)

**Tasks:**
1. Implement approve_plan() method
2. Implement quality gate checks
3. Implement state transitions
4. Generate approval report
5. Integration tests (4 tests)

### Phase 4.4: Testing & Documentation (1.5 hours)

**Tasks:**
1. End-to-end workflow tests (3 tests)
2. Edge case tests (2 tests)
3. Completion report
4. Usage guide
5. Progress update

**Total Time:** ~7 hours (within 6-8 hour estimate)

---

## 9. Report Formats

### 9.1 DoR Validation Report

```markdown
# Definition of Ready - Validation Report

**Work Item:** ADO-12345 - User Authentication Feature  
**Validation Date:** 2025-11-27 14:30:00  
**Overall Score:** 87% ✅ PASS (Threshold: 80%)

## Category Scores

### Completeness (30% weight): 90%
- ✅ Title present and descriptive (10/10 pts)
- ✅ Description detailed (10/10 pts)
- ✅ Acceptance criteria (30/30 pts) - 3 items
- ✅ Work item type specified (10/10 pts)
- ✅ Priority specified (10/10 pts)
- ✅ Assignee identified (5/5 pts)

### Clarity (25% weight): 85%
- ✅ Minimal vague language (20/20 pts) - Score: 2
- ✅ Technical approach clear (15/15 pts)
- ⚠️  User flow needs refinement (10/15 pts)
- ✅ Dependencies identified (10/10 pts)

### Testability (20% weight): 80%
...

## Recommendations

1. Refine user flow description in clarity section
2. Consider adding edge case handling to acceptance criteria
3. Excellent completeness and context scores!

## Approval Decision

✅ **APPROVED** - Ready to start work
```

### 9.2 Approval Report

```markdown
# Work Item Approval Report

**Work Item:** ADO-12345 - User Authentication Feature  
**Approval Stage:** Final Approval  
**Approval Date:** 2025-11-27 16:45:00  
**Approver:** CORTEX (auto)

## Quality Scores

- **DoR Score:** 87% ✅
- **DoD Score:** 92% ✅

## Quality Gates

- ✅ Pre-Implementation Gate: PASSED (DoR 87% >= 80%)
- ✅ Pre-Completion Gate: PASSED (DoD 92% >= 85%)

## Approval Decision

✅ **APPROVED** - Work item complete and ready for deployment

**Status Transition:** review → completed
```

---

## 10. Integration Points

### 10.1 Phase 1 (Git History) Integration

DoR validation includes git context:
- Quality score from git history
- High-risk files identified
- SME suggestions considered

### 10.2 Phase 2 (YAML Tracking) Integration

Validation results stored in YAML:
```yaml
validation:
  dor:
    score: 87.0
    passed: true
    validated_date: "2025-11-27T14:30:00"
  dod:
    score: 92.0
    passed: true
    validated_date: "2025-11-27T16:45:00"
  
approval:
  approved: true
  approved_by: "CORTEX (auto)"
  approved_date: "2025-11-27T16:45:00"
```

### 10.3 Phase 3 (Clarification) Integration

DoR validation checks clarification completion:
- Were clarifications triggered?
- Are all rounds complete?
- Is ambiguity score low enough?

---

## 11. Success Metrics

**Phase 4 Complete When:**
- ✅ DoR validation working (80% threshold)
- ✅ DoD validation working (85% threshold)
- ✅ Quality gates enforced
- ✅ Approval workflow operational
- ✅ State transitions correct
- ✅ 12+ tests passing (100% coverage)
- ✅ Integration with Phases 1-3 complete
- ✅ Documentation complete

---

## 12. Configuration Reference

### Key Thresholds

```yaml
definition_of_ready:
  minimum_score_to_approve: 80  # Adjust for team
  
definition_of_done:
  minimum_score_to_complete: 85  # Adjust for team
  
quality_gates:
  gate_before_work:
    checks:
      - dor_score >= 80
      - ambiguity_score < 5
```

### Customization

Teams can:
- Adjust category weights
- Add custom checklist items
- Change score thresholds
- Enable/disable quality gates
- Configure auto-approval

---

## 13. Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement DoR validator
3. ⏳ Implement DoD validator
4. ⏳ Implement approval workflow
5. ⏳ Testing (12+ tests)
6. ⏳ Documentation

**Current Status:** Design complete, ready for implementation

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-27  
**Next Review:** After Phase 4 implementation complete
