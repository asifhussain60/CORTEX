# PHASE-REMEDIATION-09 Execution Checklist

## Pre-Execution Verification ✅

- [x] Issue #9 reviewed and fully understood
- [x] Phase YAML created: `phase-remediation-09-challenge-integration.yaml`
- [x] Master roadmap updated with 10 ACs
- [x] Dependencies verified: PHASE-REMEDIATION-08 ✅ COMPLETE
- [x] Roadmap sync verified: IN-SYNC
- [x] Git committed: checkpoint 521958dc8
- [x] All 188 tests specified in ACs
- [x] Governance rules mapped (CORE-008, 011, 012, 013, 027, INT-RULE-009, CORE-029)

## Execution Plan (Per cortex-builder.prompt.md)

### Day 1: Layer 1 - Core Components (12 hours)

**AC-CIG-001-01: Challenge Integration Orchestrator** (4 hours)
- [ ] Create `src/core/orchestrator/challenge_integration.py`
- [ ] Implement ChallengeIntegrationOrchestrator class
- [ ] Confidence filtering (0.30 threshold)
- [ ] Severity sorting logic
- [ ] Write 20 unit tests
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-001-02: Holistic Context Builder** (4 hours)
- [ ] Create `src/core/orchestrator/holistic_context_builder.py`
- [ ] Implement HolisticContextBuilder class
- [ ] YAML serialization per CORTEX.prompt.md format
- [ ] Merge all dimensions (intent, analysis, challenges, recommendations, git)
- [ ] Write 18 unit tests
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-001-03: Turn Response With Challenges Integration** (4 hours)
- [ ] Create `src/orchestrators/response/turn_response_with_challenges.py`
- [ ] Implement TurnResponseWithChallenges class
- [ ] Wrap TurnResponseGenerator
- [ ] Add challenges_segment, recommendations_segment, holistic_context_segment
- [ ] Write 15 unit tests
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**Day 1 Validation**:
- [ ] 53 tests passing (20+18+15)
- [ ] Zero regressions to existing tests
- [ ] Type hints 100% complete
- [ ] Docstrings complete (Google style)
- [ ] Audit trail entries logged

---

### Day 2: Layer 2 - Orchestrator Integration (6 hours)

**AC-CIG-002-01: Stage 2.5 Gate Challenge Integration** (3 hours)
- [ ] Modify `src/orchestrators/core/stage_2_5_gate.py`
- [ ] Add call to ChallengeIntegrationOrchestrator in evaluate()
- [ ] Attach challenges to ConfirmationContext
- [ ] Include challenges in decision rationale
- [ ] Write 12 integration tests
- [ ] All tests passing
- [ ] Zero regressions to gate tests
- [ ] Update master: status = COMPLETED

**AC-CIG-002-02: Turn Response Generator Challenge Hook** (3 hours)
- [ ] Modify `src/orchestrators/response/turn_response_generator.py`
- [ ] Add call to TurnResponseWithChallenges
- [ ] Maintain backward compatibility
- [ ] Write 16 integration tests
- [ ] All tests passing
- [ ] Zero regressions to existing response tests
- [ ] Update master: status = COMPLETED

**Day 2 Validation**:
- [ ] 28 new integration tests passing (12+16)
- [ ] All 81 tests so far passing (53+28)
- [ ] No breaking changes to existing API
- [ ] Audit trail complete

---

### Days 3-5: Layer 3 - Comprehensive Testing (11 hours)

**AC-CIG-003-01: Unit Tests - Challenge Integration** (3 hours)
- [ ] Create `tests/unit/core/orchestrator/test_challenge_integration.py`
- [ ] 25 unit tests for ChallengeIntegrationOrchestrator
- [ ] Coverage: >=95%
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-003-02: Unit Tests - Holistic Context Builder** (2 hours)
- [ ] Create `tests/unit/core/orchestrator/test_holistic_context_builder.py`
- [ ] 20 unit tests for HolisticContextBuilder
- [ ] Coverage: >=95%
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-003-03: Unit Tests - Turn Response With Challenges** (2 hours)
- [ ] Create `tests/unit/orchestrators/response/test_response_with_challenges.py`
- [ ] 22 unit tests for TurnResponseWithChallenges
- [ ] Coverage: >=95%
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-004-01: Integration Tests - Stage 2.5 With Challenges** (2 hours)
- [ ] Create `tests/integration/test_stage_2_5_gate_with_challenges.py`
- [ ] 18 integration tests
- [ ] Gate behavior with challenges
- [ ] Decision quality validation
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**AC-CIG-004-02: Integration Tests - End-to-End Challenge Flow** (4 hours)
- [ ] Create `tests/integration/test_challenge_end_to_end.py`
- [ ] 35 end-to-end tests
- [ ] Real-world scenarios
- [ ] Challenge generation on every turn
- [ ] Holistic context validation
- [ ] INT-RULE-009 enforcement
- [ ] All tests passing
- [ ] Update master: status = COMPLETED

**Days 3-5 Validation**:
- [ ] 107 new tests passing (25+20+22+18+35)
- [ ] **Total: 188 tests passing** (53+28+107)
- [ ] Coverage: >=95% across all components
- [ ] Zero regressions to any existing tests
- [ ] Audit trail complete for all 10 ACs
- [ ] Hash chain integrity verified

---

## Phase Completion Tasks

- [ ] All 10 ACs marked COMPLETED in master
- [ ] All 188 tests passing (100% pass rate)
- [ ] Validator passes: `python3 scripts/validate_phase_sync.py`
- [ ] Phase locked: `locked: true` in master
- [ ] Git checkpoint created
- [ ] Phase completion report generated
- [ ] Executive summary created

## Governance Compliance Checklist

### CORE-008: Test-Driven Development
- [ ] Tests written before implementation ✅ (specs in phase YAML)
- [ ] All tests passing ✅
- [ ] 188 tests total ✅

### CORE-011: Type Hints (100%)
- [ ] All functions have type hints
- [ ] All parameters typed
- [ ] All returns typed
- [ ] No `Any` without explicit justification

### CORE-012: Docstrings (Google Style)
- [ ] All public functions documented
- [ ] All classes documented
- [ ] All parameters documented
- [ ] All returns documented

### CORE-013: No Bare Except
- [ ] All except clauses specify exception type
- [ ] No `except:` anywhere

### CORE-027: Audit Trail
- [ ] AC_START logged on AC beginning
- [ ] AC_EXECUTE logged during execution
- [ ] AC_COMPLETE logged on success
- [ ] AC_EXECUTE_FAILED logged on failure
- [ ] Hash chain integrity maintained

### INT-RULE-009: Mandatory Intelligent Challenge
- [ ] Challenge generation on every turn ✅
- [ ] Confidence filtering (0.30 threshold) ✅
- [ ] Severity sorting ✅
- [ ] No challenges < 0.3 confidence ✅

### CORE-029: Response Headers
- [ ] Challenge headers in response ✅
- [ ] Formatted per spec ✅
- [ ] Includes severity & count ✅

## Sign-Off Template

```
PHASE-REMEDIATION-09 COMPLETION REPORT

Date Completed: [DATE]
Completed By: [DEVELOPER]
Duration: 5 days (44 hours)
Actual Hours: [ACTUAL]

✅ All 10 ACs COMPLETED
✅ All 188 tests PASSING (100%)
✅ Governance compliance: 100%
✅ INT-RULE-009 enforced
✅ Phase locked: true
✅ Git checkpoint: [SHA]

Ready for PHASE-DEPLOYMENT.

Signed: _________________ Date: __________
```

---

## Troubleshooting Guide

### If Tests Fail
1. Review test output carefully
2. Check assertion messages
3. Verify implementation matches AC spec
4. Debug with: `pytest -vv tests/unit/core/orchestrator/test_challenge_integration.py::test_name`
5. Fix code, re-run tests
6. DO NOT skip to next AC - complete current AC first

### If Confidence Filtering Logic Wrong
- Review: "skip individual challenge if confidence < 0.3" requirement
- Check: ChallengeGenerator.generate_all() output
- Verify: Each Challenge object has `.confidence` attribute
- Test: `test_confidence_filtering_below_threshold()` and `test_confidence_filtering_above_threshold()`

### If Integration Tests Fail
- Verify: Both modified files (gate + response generator) have new calls
- Check: Module imports are correct
- Test: New orchestrator classes are instantiated correctly
- Debug: Add print statements to trace flow (remove after fixing)

### If Sync Validator Complains
- Run: `python3 scripts/validate_phase_sync.py --verbose`
- Check: Phase tracker counts match reality
- Fix: Update metadata `total_ac_ids`, `ac_breakdown` sections
- Note: Some warnings (orphan phases) are OK, just don't block commit

---

**Checklist Version**: 1.0  
**Date Created**: 2026-01-19  
**Status**: READY FOR EXECUTION  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
