# PHASE-E Implementation Roadmap - Quick Wins Analysis

**Generated:** 2025-01-21  
**Machine Track:** mac  
**Strategy:** Maximize pass rate through tactical focus on high-ROI modules

## Current State by Module (Core)

### Tier 1: Already Complete ✅
| Module | Tests | Pass | Rate | Status |
|--------|-------|------|------|--------|
| `lens` | 6 | 6 | 100% | ✅ DONE |
| `state` | 40 | 40 | 100% | ✅ DONE |
| `repository` | 28 | 28 | 100% | ✅ DONE |
| **Subtotal** | **74** | **74** | **100%** | **168 tests** |

### Tier 2: High Pass Rate - Focus for 100%
| Module | Tests | Pass | Rate | Status | Effort |
|--------|-------|------|------|--------|--------|
| `orchestrator` | 593 | 407 | 69% | ⏳ 186 failing | M |
| `hallucination_prevention` | 160 | 29 | 18% | ⏳ 131 failing | H |
| `intelligence` | 130 | 42 | 32% | ⏳ 88 failing | H |

### Tier 3: Requires Implementation
| Module | Tests | Pass | Rate | Status | Effort |
|--------|-------|------|------|--------|--------|
| `intent` | 247 | 4 | 2% | ⏳ 243 failing | VH |
| `knowledge` | 288 | 9 | 3% | ⏳ 279 failing | VH |

## Recommended Implementation Order

### Phase 1: Orchestrator to 100% (Highest ROI - 2-3 hours)
**Why:** Already 69% (407/593), minimal effort for big gains

**Failing Areas:**
- `approval_gate`: 20 failures (fixture/method signature issues)
- `intent_router`: 35 failures (missing implementations)
- `action_executor`: 28 failures (missing implementations)
- `conversation_protocol`: Only 5 failures from 24 tests! ✅ Nearly done

**Tactical Approach:**
1. Quick-fix approval_gate fixture (pass gate_id to constructor)
2. Implement missing ApprovalGateLogic methods
3. Review conversation_protocol failures (likely 1-2 line fixes)
4. Target: 550+/593 tests (92%+)

**Time Estimate:** 2 hours

### Phase 2: Hallucination Prevention Foundation (1-2 hours)
**Why:** Core security module, 28/28 boundary rules done, foundation strong

**Failing Areas:**
- `confidence_scoring`: 24 errors (missing class exports)
- `hallucination_detection`: 23 failures (implementation gaps)
- `intent_canonicalization`: 36 failures (missing logic)
- `vision_mutations`: 23 errors (import issues)
- `execution_sandbox`: 25 failures (sandbox implementation)

**Tactical Approach:**
1. Export missing classes from confidence_scoring (5 min)
2. Implement confidence_scoring core logic (30 min)
3. Fix hallucination_detection basic tests (45 min)
4. Target: 60+/160 tests (37%+)

**Time Estimate:** 1.5-2 hours

### Phase 3: Intelligence Module Boost (1 hour)
**Why:** 32% pass rate means basic structure exists

**Failing Areas:**
- Likely missing implementations for feature extraction
- Pattern recognition logic gaps

**Time Estimate:** 1 hour

### Phase 4: Intent Module Foundation (2-3 hours)
**Why:** Only 4/247 passing, but needed for router integration

**Time Estimate:** 2-3 hours

## Implementation Checklist - Orchestrator

### test_approval_gate.py (20 tests - ALL ERRORING)
```
Status: BLOCKED on fixture
Action: Update gate fixture to pass gate_id
  
def gate():
    return ApprovalGateLogic(gate_id="test-gate-001")
```

**Methods to Implement:**
- `ApprovalGateLogic.evaluate_approval(assessment, operation_id)` → ApprovalDecision
- `ApprovalDecision.requires_confirmation` property
- `ApprovalDecision.escalated` property

**Estimated Time:** 30 min

### test_conversation_protocol.py (5 failures from 24 tests - 79% already passing!)
```
Status: ALMOST DONE - Review the 5 failing tests
Likely Issues: Message validation, protocol state transitions

Estimated Time:** 30 min
```

### test_intent_router.py (35 failures)
```
Status: Missing route evaluation logic
Methods Needed:
  - route_to_handler(intent, context)
  - register_handler(intent_type, handler)

Estimated Time:** 1 hour
```

## Quick-Fix Checklist (< 5 min each)

### 1. Confidence Scoring Exports
```python
# cortex_brain/tier2/hallucination_prevention/confidence_scoring.py

# Add these classes to __all__ and implement:
@dataclass
class ConfidenceAssessment:
    assessment_id: str
    confidence_score: float
    factors: Dict[str, float]

@dataclass
class ScoringFactor:
    name: str
    value: float
    weight: float

@dataclass
class ScoringModel:
    model_id: str
    factors: List[ScoringFactor]

@dataclass
class ReviewTrigger:
    trigger_id: str
    threshold: float
    action: str
```

**Time:** 15 min

### 2. Fix Conversation Protocol State
```python
# Likely in tests/unit/core/orchestrator/test_conversation_protocol.py
# Review test failures, likely state machine issues

Time:** 15-30 min
```

### 3. Export Missing Approval Gate Types
```python
# cortex/core/orchestrator/approval_gate.py
# Ensure all @dataclass types have default values or are properly initialized

Time:** 10 min
```

## Pass Rate Improvement Timeline

```
Current:  565/1509 (37.4%)
  ↓ After Orchestrator (Phase 1):  750/1509 (49.7%)
  ↓ After Hallucination Prev (Phase 2):  850/1509 (56.3%)
  ↓ After Intelligence (Phase 3):  900/1509 (59.6%)
  ↓ After Intent Foundation (Phase 4):  1000/1509 (66.3%)
  ↓ Full PHASE-E (Continued): 1400+/1509 (92%+)
```

## By-Module Breakdown

### Orchestrator (593 tests, currently 69%)
- conversation_protocol: 24 tests, ~20 passing (83%) ← LOW HANGING FRUIT
- approval_gate: 20 tests, 0 passing (0%) ← FIXTURE ISSUE (easy)
- intent_router: 35 tests, ~10 passing
- action_executor: 28 tests, ~8 passing
- Other: 486 tests, ~369 passing (76%)

**Win Potential:** +60 tests to 100% with focused work

### Hallucination Prevention (160 tests, currently 18%)
- behavioral_boundaries: 28 tests, 28 passing (100%) ✅
- confidence_scoring: 24 tests, 0 passing (errors)
- execution_sandbox: 25 tests, 1 passing (4%)
- hallucination_detection: 23 tests, failing
- intent_canonicalization: 36 tests, failing
- vision_mutations: 24 tests, erroring

**Win Potential:** +80 tests with focused class/method implementation

## Implementation Strategy for TDD Loop

### Orchestrator Focus (Next 2 hours)

**1. Fix Fixtures (10 min)**
```python
# tests/unit/core/orchestrator/test_approval_gate.py
@pytest.fixture
def gate():
    return ApprovalGateLogic(gate_id="test-gate-001")
```

**2. Implement evaluate_approval (20 min)**
```python
class ApprovalGateLogic:
    def evaluate_approval(self, assessment, operation_id):
        # Basic implementation:
        # - Trivial: auto-approve
        # - Simple: auto-approve with summary
        # - Moderate: request confirmation
        # - Complex/Critical: escalate
        
        if assessment.complexity_level == "trivial":
            return ApprovalDecision(
                approved=True,
                requires_confirmation=False,
                escalated=False,
                reason="Auto-approved: trivial operation"
            )
        # ... etc for other levels
```

**3. Review Conversation Protocol (20 min)**
- Run `pytest tests/unit/core/orchestrator/test_conversation_protocol.py -v`
- Identify 5 failing tests
- Likely state machine transitions, fix inline

**4. Implement Route Logic (30 min)**
- `IntentRouter.route_to_handler()`
- Handler registration system
- Context passing

**Result:** +100 tests passing, 507/593 → 85%

### Hallucination Prevention Focus (1.5 hours)

**1. Export Missing Classes (10 min)**
- Add dataclasses to confidence_scoring.py
- Fix __all__ exports

**2. Implement Confidence Scorer (30 min)**
```python
class ConfidenceScorer:
    def score_confidence(self, operation, context):
        # Calculate overall confidence as weighted average
        # of input/processing/output confidence
        
        overall = (
            0.3 * context.get("input_confidence", 0.5) +
            0.4 * context.get("processing_confidence", 0.5) +
            0.3 * context.get("output_confidence", 0.5)
        )
        
        return ConfidenceAssessment(
            assessment_id=str(uuid.uuid4()),
            confidence_score=overall,
            factors={...}
        )
```

**3. Fix Sandbox Tests (30 min)**
- Implement execution_sandbox with basic isolation
- Add simple rollback capability

**Result:** +50 tests passing, 29/160 → 80/160 (50%)

## Environment & Tools Ready
- ✅ pytest-monitor: Real-time progress tracking
- ✅ test-analytics.py: Comprehensive reporting
- ✅ pytest.ini: Automatic progress plugin
- ✅ Zero-output-mode: One-line notifications only

## Success Criteria

| Metric | Target | Estimated After Phase 1-2 |
|--------|--------|---------------------------|
| Overall Pass Rate | 98%+ | 56% |
| Orchestrator | 100% | 85% |
| Hallucination Prev | 90%+ | 50% |
| Core Health Score | 80+/100 | 60/100 |
| Test Execution Time | <5min | 0.3s (monitored) |

## Next Actions (Immediate - Now)

1. ✅ Identify quick wins (DONE - This document)
2. ⏳ Fix orchestrator fixtures (5 min)
3. ⏳ Implement evaluate_approval method (20 min)
4. ⏳ Review conversation_protocol failures (20 min)
5. ⏳ Export confidence_scoring classes (10 min)

---

**Timeline:** Phases 1-2 should take 3-4 hours total to execute
**Parallel Path:** Can work on Intent and Knowledge while orchestrator builds
**Status:** Ready for aggressive implementation mode
