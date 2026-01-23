# REMEDIATION-INTENT-VALIDATION-INTEGRATION
## Architecture Integration Guide

**Version:** 1.0  
**Date:** 2026-01-23  
**Authority:** cortex-total-recall.prompt.md + cortex-builder.prompt.md  
**Status:** DESIGN PHASE - Ready for Implementation

---

## Executive Summary

This document describes how the intent validation architecture from CORTEX-5.5 archive branch integrates into the current CORTEX system via the wiring harness. Eight components restore per-turn validation, challenge injection, and confidence-driven routing without requiring architectural refactoring.

**Key Finding:** The archive pattern maps perfectly to the current 4-stage pipeline with clean integration points. No circular dependencies or conflicts detected.

---

## Architecture Integration Points

### Stage 1: Comprehension → ComprehensionSession

**Current State:** `MasterOrchestrationStage1` performs language analysis and intent detection

**Enhancement:** Add ComprehensionSession state machine for multi-turn tracking

```
MasterOrchestrationStage1.comprehend()
  → Stage1ComprehensionContext (input)
  → [NEW] ComprehensionSession.create_session()
  → Stage1Output (existing structure)
  → [NEW] ComprehensionSession.record_comprehension()
  ↓
Stage 1 Output = Stage1Output + ComprehensionSession reference
```

**Integration Mechanics:**
- `ComprehensionSession` created at conversation start
- Comprehension output stored in session with timestamp
- Approval status tracked (PENDING → APPROVED/REJECTED/NEEDS_CLARIFICATION)
- Revision history maintained for iterative refinement

**Wiring Priority:** CRITICAL-0 (highest - needed by Stage 2)

---

### Stage 2: Routing → ConfidenceRouter

**Current State:** `IntentRouter` routes based on intent type only

**Enhancement:** Add confidence gates before routing

```
Stage1Output (comprehension result)
  → [NEW] ConfidenceRouter.apply_confidence_rules()
    - confidence_score ≥ 0.85 → route normally, caution_flag=False
    - confidence_score 0.70-0.84 → route normally, caution_flag=True
    - confidence_score < 0.70 → reroute to INTERACTION (except QUERY)
  → RoutingDecision + caution_flag
  ↓
Downstream handlers see caution_flag and adjust behavior
```

**Confidence Thresholds:**
- **0.85+:** High confidence - proceed without additional gates
- **0.70-0.84:** Medium confidence - include in response, request confirmation
- **<0.70:** Low confidence - return for clarification (queries always safe)

**Special Case - Query Intents:**
- QUERY, ANALYZE, STATUS always route to DIRECT_RESPONSE
- Treated as safe operations regardless of confidence
- Reasoning: Queries don't modify state, safe to return even with low confidence

**Wiring Priority:** CRITICAL-2 (needed by downstream stages)

---

### Stage 3: Knowledge → ChallengeGenerator

**Current State:** Stage 3 returns domain context for execution

**Enhancement:** Inject proactive risk analysis before execution

```
RoutingDecision + Domain Knowledge
  → [NEW] ChallengeGenerator.generate_all()
    ├─ analyze_governance() → governance risks
    ├─ analyze_performance() → perf anti-patterns
    ├─ analyze_coverage() → test gaps
    ├─ analyze_changes() → breaking changes
    └─ check_historical_issues() → known patterns
  → List[Challenge] (sorted by severity)
  → [NEW] ComprehensionSession.record_challenges()
  ↓
Challenges prepared for Stage 4 presentation
```

**Challenge Categories:**
1. **BREAKING_CHANGE:** Interface/contract changes that affect consumers
2. **TEST_GAP:** Missing test coverage for changed functionality
3. **GOVERNANCE_RISK:** TIER 0-3 rule violations
4. **HISTORICAL_ISSUE:** Known problematic patterns from git history
5. **PERFORMANCE_RISK:** O(n²) algorithms, N+1 queries, memory leaks
6. **SECURITY_RISK:** eval(), exec(), pickle.load, SQL injection patterns

**Severity Levels (sorted):**
- CRITICAL: Must fix before execution
- HIGH: Strong warning, proceed with caution
- MEDIUM: Informational, recommended improvement
- LOW: Nice-to-have, future optimization

**Evidence & Mitigation:**
- Each challenge includes evidence (line numbers, examples)
- Mitigation strategy provided (how to fix)
- Confidence score (0-1) indicating certainty

**Wiring Priority:** CRITICAL-1 (needed by Stage 4)

---

### Stage 4: Execution → ResponseChallengeInjector

**Current State:** Direct output of execution results

**Enhancement:** Inject challenges before showing execution

```
Execution Result
  → [NEW] ResponseChallengeInjector.inject_challenges()
    ├─ Format CORTEX header (CORE-029)
    ├─ Add operation summary
    ├─ Present challenges (severity-sorted)
    ├─ Request user approval if CRITICAL challenges
    ├─ Present recommendations
    └─ Show execution output (if approved)
  → User sees challenges FIRST, execution SECOND
  → [NEW] ComprehensionSession.record_approval()
  ↓
If user dismisses challenges → logged for governance audit
```

**Response Order:**
1. Header (CORE-029 mandatory format)
2. Operation summary (1-2 sentences)
3. Challenges (CRITICAL → HIGH → MEDIUM → LOW)
4. User approval prompt (if CRITICAL challenges exist)
5. Recommendations (if challenges found)
6. Execution results (code output, metrics, etc.)
7. Footer (copyright, governance metadata)

**Dismissible Challenges:**
- Users can acknowledge challenges and proceed
- Dismissed challenges logged for audit trail
- Governance compliance maintained via audit
- Operator override options for low-risk dismissals

**Wiring Priority:** HIGH-6 (needs all prior stages)

---

### MultiTurn: ConversationProtocol → TurnValidationGate

**Current State:** `ConversationProtocol.execute_turn()` lacks governance context

**Enhancement:** Add per-turn validation gates

```
ConversationProtocol.execute_turn(user_input, round_number, context)
  → [NEW] TurnValidationGate.validate_pre_comprehension()
    - Check previous turn context
    - Evaluate TIER 0 rules
  → MasterOrchestrationStage1.comprehend()
  → [NEW] TurnValidationGate.validate_post_routing()
    - Check routing decision
    - Verify confidence score appropriate for context
  → [NEW] TurnValidationGate.validate_pre_execution()
    - Final TIER 0 block check
    - Escalate TIER 1-2 as warnings
  → Execute operation
  → Inject challenges
  → [NEW] ComprehensionSession.record_turn_completion()
  ↓
Next turn sees full context from previous turns
```

**Turn Context Flow:**
- turn_number: Integer incrementing per turn (1, 2, 3, ...)
- conversation_context: User-provided context from previous turns
- comprehension_history: Intents detected in prior turns
- challenges_dismissed: Challenges user acknowledged in prior turns
- approval_status: Overall conversation approval state

**Governance per Turn:**
- TIER 0 rules evaluated against turn context
- Violations block execution (fail-fast)
- TIER 1-2 rules evaluated with escalation
- Turn-level audit trail maintained

**Wiring Priority:** HIGH-3 (needed by ConversationProtocol)

---

## Wiring Harness Integration

All 8 components registered in `cortex/testing/wiring_harness_inventory.py` with:

### 1. ComprehensionSession (CRITICAL-0)
```yaml
Entry Point: cortex.orchestrators.core.comprehension_session
Initialization: 
  session = ComprehensionSession()
Hook Type: Stage 1 output wrapper
Dependencies: 
  - EnhancedAuditLogger
  - ComprehensionYAML
```

### 2. ChallengeGenerator (CRITICAL-1)
```yaml
Entry Point: cortex.orchestrators.challenge_generator
Initialization:
  generator = ChallengeGenerator()
Hook Type: Stage 3 knowledge injection
Dependencies:
  - ast (Python stdlib)
  - re (Python stdlib)
  - GovernanceRegistry
```

### 3. ConfidenceRouter (CRITICAL-2)
```yaml
Entry Point: cortex.intent_router.confidence_router
Initialization:
  router = ConfidenceRouter()
Hook Type: Stage 2 routing enhancement
Dependencies:
  - IntentRouter
  - CanonicalizedIntent
  - RoutingDecision
```

### 4. TurnValidationGate (HIGH-3)
```yaml
Entry Point: cortex.orchestrators.turn_validation_gate
Initialization:
  gate = TurnValidationGate()
Hook Type: ConversationProtocol middleware
Dependencies:
  - GovernanceRegistry
  - EnhancedAuditLogger
  - ConversationProtocol
```

### 5. ComprehensionYAML (HIGH-4)
```yaml
Entry Point: cortex.orchestrators.comprehension_yaml
Initialization:
  yaml_obj = ComprehensionYAML(metadata=..., intent=..., challenges=...)
Hook Type: Stage 1 output data structure
Dependencies:
  - yaml module
  - dataclasses module
```

### 6. CautionFlagMechanism (MEDIUM-5)
```yaml
Entry Point: cortex.intent_router.routing_decision
Initialization:
  # Enhanced existing RoutingDecision with caution_flag field
Hook Type: RoutingDecision enhancement
Dependencies:
  - RoutingDecision
```

### 7. ResponseChallengeInjector (HIGH-6)
```yaml
Entry Point: cortex.orchestrators.response_challenge_injector
Initialization:
  injector = ResponseChallengeInjector()
Hook Type: Stage 4 response formatting
Dependencies:
  - ResponseHeaderInjector
  - ConversationProtocol
  - EnhancedAuditLogger
```

### 8. WiringHarnessIntegration (MEDIUM-7)
```yaml
Entry Point: cortex.testing.wiring_harness_inventory
Initialization:
  # Registry entries for components 1-7
Hook Type: Auto-discovery and initialization
Dependencies:
  - TotalRecallAgent
```

---

## Auto-Wiring Flow (via TotalRecallAgent)

```
TotalRecallAgent.__init__()
  → Load wiring_harness_inventory.get_critical_wiring_order()
  → Returns: [ComprehensionSession, ChallengeGenerator, ConfidenceRouter, ...]
  
  FOR EACH component IN order:
    → Import from entry_point
    → Initialize with params
    → Register in MasterOrchestrator at hook_point
    → Add to _wired_components registry
    → Log auto-wiring success
  
  → MasterOrchestrator now has all 8 components wired
  → ConversationProtocol ready for multi-turn
  → ChallengeGenerator active in pipeline
```

**No Manual Wiring Required:**
- Components auto-discovered from wiring harness
- Initialization happens automatically
- No magic strings or manual configuration
- All auto-wiring logged for audit trail

---

## Test Strategy

### Unit Tests (Per Component)
- **ComprehensionSession:** 24 tests covering state transitions, revision tracking
- **ChallengeGenerator:** 28 tests covering all 6 categories, severity sorting
- **ConfidenceRouter:** 35 tests covering all confidence thresholds
- **TurnValidationGate:** 18 tests covering governance validation
- **ComprehensionYAML:** 15 tests covering serialization/deserialization
- **CautionFlagMechanism:** 10 tests covering flag propagation
- **ResponseChallengeInjector:** 15 tests covering response formatting
- **WiringHarnessIntegration:** 12 tests covering discovery and auto-wiring

**Total Unit Tests:** 157 tests

### Integration Tests
- **Multi-turn E2E:** 16 tests covering full conversation flows
- **Full Pipeline:** 12 tests covering all stages in sequence

**Total Integration Tests:** 28 tests

**Total Test Suite:** 185 tests (target: 154 minimum)

### Test Execution
```bash
# Run all tests
pytest tests/unit/orchestrators/ tests/unit/intent_router/ \
        tests/unit/testing/ tests/integration/ -v

# Run with coverage
pytest tests/ --cov=cortex --cov-report=html

# Expected output
======================== 185 passed in X.XXs ========================
Coverage: 95%+ of intent validation code
```

---

## Governance Compliance

### CORE Rules Enforced

| Rule | Requirement | Validation |
|------|-------------|-----------|
| CORE-008 | Tests BEFORE code | TDD test files created first |
| CORE-011 | Type hints on ALL functions | Mypy validates 100% |
| CORE-012 | Google docstrings | Pylint validates docstrings |
| CORE-013 | No bare except | Linter validates per file |
| CORE-027 | AC_START → EXECUTE → COMPLETE | EnhancedAuditLogger logs all phases |
| CORE-029 | Response headers mandatory | CORE-029 header in all responses |

### Tier Rule Validation

- **TIER 0:** Core rules (29 rules) - ALL must pass
- **TIER 1:** Domain rules - Must not conflict with TIER 0
- **TIER 2:** Context rules - Must not conflict with TIER 0-1
- **TIER 3:** Knowledge rules - Must not conflict with TIER 0-2

**Per-Turn Validation:**
- All TIER rules evaluated at each turn boundary
- TIER 0 violations block execution
- TIER 1-2 violations escalated as warnings
- Audit trail maintains governance compliance record

---

## Integration Checklist

### Pre-Integration
- [ ] Archive branch analysis complete (✓ Done)
- [ ] Architecture mapping validated (✓ Done)
- [ ] Wiring harness inventory reviewed (✓ Done)
- [ ] Test strategy documented (✓ Done)
- [ ] Phase YAML created (✓ Done)
- [ ] Integration guide written (✓ Done)

### During Implementation (Subphases 1-8)
- [ ] ComprehensionSession implemented and tested (24 tests)
- [ ] ChallengeGenerator implemented and tested (28 tests)
- [ ] ConfidenceRouter implemented and tested (35 tests)
- [ ] TurnValidationGate implemented and tested (18 tests)
- [ ] ComprehensionYAML implemented and tested (15 tests)
- [ ] CautionFlagMechanism implemented and tested (10 tests)
- [ ] ResponseChallengeInjector implemented and tested (15 tests)
- [ ] WiringHarnessIntegration completed and tested (12 tests)
- [ ] Multi-turn tests pass (16 tests)
- [ ] Full pipeline tests pass (12 tests)

### Post-Integration
- [ ] All 185 tests passing (100%)
- [ ] Governance compliance ≥95%
- [ ] Intent validation accuracy ≥90%
- [ ] Challenge precision ≥95%
- [ ] Auto-discovery validates all 8 components
- [ ] Git commits with AC-IDs
- [ ] Merged with origin/CORTEX

---

## Risk Mitigation

### Potential Issues & Mitigations

**Issue 1: Confidence Scoring Inaccuracy**
- Mitigation: Baseline tests with known intents
- Validation: 90% accuracy target with fuzzy matching
- Fallback: Manual override via caution flags

**Issue 2: Challenge False Positives**
- Mitigation: Precision-focused test suite
- Validation: 95% precision requirement
- Fallback: Dismissible challenges for low-risk false positives

**Issue 3: Performance Regression**
- Mitigation: Per-turn validation is lightweight
- Validation: <50ms overhead per turn
- Fallback: Async challenge generation for large codebases

**Issue 4: Wiring Harness Discovery Failure**
- Mitigation: Auto-discovery tests before deployment
- Validation: 100% component discovery rate
- Fallback: Manual wiring via dependency injection

**Issue 5: Governance Rule Conflicts**
- Mitigation: TIER precedence enforced (TIER 0 > TIER 1 > TIER 2 > TIER 3)
- Validation: Conflict detection tests
- Fallback: GovernanceRegistry precedence rules

---

## Deployment Path

### Phase Sequence
1. **REMEDIATION-INTENT-001:** ComprehensionSession (8 hrs, 24 tests)
2. **REMEDIATION-INTENT-002:** ChallengeGenerator (6 hrs, 28 tests)
3. **REMEDIATION-INTENT-003:** ConfidenceRouter (10 hrs, 35 tests)
4. **REMEDIATION-INTENT-004:** TurnValidationGate (8 hrs, 18 tests)
5. **REMEDIATION-INTENT-005:** WiringHarnessIntegration (4 hrs, 12 tests)
6. **REMEDIATION-INTENT-006:** ResponseChallengeInjector (6 hrs, 15 tests)
7. **REMEDIATION-INTENT-007:** Multi-turn Tests (5 hrs, 16 tests)
8. **REMEDIATION-INTENT-008:** Verification & Compliance (3 hrs, 8 tests)

### Critical Path
- ComprehensionSession → ConfidenceRouter → ChallengeGenerator → ResponseChallengeInjector
- All others can be parallel

### Parallelization Potential
- Could reduce 40-50 hours to 15-20 hours with 3 developers
- Subphases 2,4,5,6 can run in parallel with 1
- Subphase 7-8 must wait for all prior phases

---

## Success Criteria

### Functional Criteria
1. ComprehensionSession properly tracks state transitions
2. ChallengeGenerator detects all 6 challenge categories
3. ConfidenceRouter applies all 3 threshold gates
4. TurnValidationGate enforces TIER 0 blocking
5. ResponseChallengeInjector presents challenges before execution
6. Wiring harness discovers all 8 components
7. Auto-wiring initializes all components correctly

### Quality Criteria
1. Test pass rate = 100% (185/185 tests)
2. Code coverage = 95%+ for intent validation
3. Governance compliance = 95%+
4. Type hints = 100% (CORE-011)
5. Docstrings = 100% Google style (CORE-012)
6. No bare except clauses (CORE-013)

### Performance Criteria
1. Per-turn validation overhead < 50ms
2. Challenge generation < 200ms for 1000-line file
3. No memory leaks in multi-turn conversation
4. Confidence scoring ≥90% accuracy

### Governance Criteria
1. TIER 0 rules enforced (100%)
2. TIER 1-2 rules enforced (100%)
3. Audit trail complete per turn
4. AC-IDs tracked per component

---

## Conclusion

The intent validation architecture from CORTEX-5.5 integrates cleanly into the current system via 8 well-defined components. No architectural refactoring required. Wiring harness enables auto-discovery and initialization. 185-test suite validates all aspects. Ready for implementation.

**Recommendation:** PROCEED with implementation starting with ComprehensionSession (subphase 1).

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
