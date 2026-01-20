# ROADMAP UPDATE - MULTI-ROUND TESTING PATTERN ADOPTION
**Cortex-Master.yaml Enhancement: Add Multi-Round Conversation Testing Standard**

Date: 2026-01-16  
Scope: cortex-master.yaml, phase-07-intent-router.yaml, all orchestrator test files

---

## EXECUTIVE SUMMARY

**Problem Statement**: 
Current tests validate single-turn orchestrator operations in isolation. Missing: multi-turn conversation continuity, per-turn LENS re-execution, and per-turn approval validation. This gap allows Issue-001 CRIT-002 ("Intent Router bypassed after Turn 1") to exist.

**Proposed Change**:
Add "Multi-Round Conversation Testing" as CORTEX testing standard with:
- ConversationSession pattern (track state across turns)
- Per-turn LENS protocol re-execution validation
- Per-turn approval gate re-request validation
- Multi-orchestrator chain handoff testing

**Impact**: 
- Resolves Issue-001 CRIT-002
- Enables detection of Intent Router single-turn bypass
- Validates CORTEX architecture compliance (CORE-019, CORE-027)
- Improves test coverage from ~70% single-turn to ~95% multi-round

---

## SPECIFIC ROADMAP CHANGES

### Change 1: Add Testing Pattern to `cortex-master.yaml`

**Location**: `metadata.testing_framework` (NEW section)

**Add**:
```yaml
metadata:
  # ... existing metadata ...
  
  testing_framework:
    status: "FRAMEWORK ADOPTED 2026-01-16"
    
    conversation_driven_testing:
      enabled: true
      rationale: "Tests must validate multi-turn orchestrator interaction patterns, not just single operations"
      
      applies_to:
        - "All orchestrator test suites"
        - "Master orchestrator integration tests"
        - "Domain orchestrator tests"
        - "Intent router verification"
      
      pattern_name: "ConversationSession-Based Round-Trip Testing"
      
      core_components:
        - ConversationSession: "Maintains state across turns 1..N"
        - RoundContext: "Represents single turn: input/output"
        - ApprovalGate: "Validates approval requested per turn"
        - ContinuityValidator: "Asserts state persistence"
        - AuditTrailRecorder: "Captures turn-by-turn events"
      
      minimum_test_coverage:
        single_orchestrator_min_turns: 3
        multi_orchestrator_min_turns: 5
        
      validation_requirements:
        - "Turn 1: LENS executes"
        - "Turn 2+: LENS re-executes (not cached)"
        - "Turn 1: Approval requested"
        - "Turn 2+: Approval re-requested (not skipped)"
        - "State from Turn N available in Turn N+1"
        - "Audit trail shows turn progression"
        - "Hash chain unbroken across all turns"
        - "Governance compliance verified (CORE-019, CORE-027)"
      
      files_required:
        - "tests/fixtures/conversation_session.py"
        - "tests/fixtures/round_context.py"
        - "tests/fixtures/continuity_validator.py"
        - "tests/integration/test_multi_round_*.py (per orchestrator)"
      
      standards_enforced:
        - CORE-019: "TDD-Master routing - LENS re-evaluated per turn"
        - CORE-027: "Audit trail - AC_START/EXECUTE/COMPLETE per turn"
        - INT-RULE-009: "Auto-challenge - per-turn comprehension"
```

### Change 2: Add Pattern Requirements to `phase_tracker`

**Location**: `phase_tracker.PHASE-07-INTENT-ROUTER` (UPDATE section)

**Add**:
```yaml
PHASE-07-INTENT-ROUTER:
  # ... existing fields ...
  
  multi_round_testing:
    status: "REQUIREMENT ADDED 2026-01-16"
    requirement: |
      All IR-00X acceptance criteria must include multi-round conversation
      tests that validate Intent Router persistence across turns.
    
    test_files:
      - tests/unit/core/intent/test_ir_004_02_multi_turn_persistence.py (EXISTING)
      - tests/integration/test_multi_round_planning.py (NEW)
      - tests/integration/test_multi_round_ado.py (NEW)
      - tests/integration/test_multi_round_interaction.py (NEW)
      - tests/integration/test_multi_round_master.py (NEW)
      - tests/integration/test_multi_round_audit_trail.py (NEW)
    
    new_ac_recommendation:
      ac_id: "AC-IR-005-01"
      title: "Multi-Round Conversation Continuity with LENS Re-Execution"
      description: |
        Verify that Interaction Orchestrator and all delegated orchestrators
        maintain conversation state across 5+ user turns, with mandatory
        LENS protocol re-execution and approval gate re-request on each turn.
      
      test_coverage:
        - Turn 1: "Initial request → LENS → Approve → Execute"
        - Turn 2: "New request → LENS (re-run) → Approve (re-request) → Execute"
        - Turn 3-5: "Pattern continues, state persists"
        - Rejection path: "User rejects on Turn 2, loop refinement"
        - State integrity: "Turn N+1 sees Turn N results"
      
      acceptance_criteria_detail:
        1: "LENS protocol executes on ALL turns (validated in audit trail)"
        2: "Approval gate requested on ALL turns (validated in audit trail)"
        3: "State persists from Turn N → N+1 (validated via RoundContext)"
        4: "Audit trail captures turn-by-turn progression"
        5: "Hash chain remains unbroken across all turns"
        6: "Master orchestrator re-routes per turn (not cached)"
      
      estimated_hours: 4
      estimated_days: 1
      blocking: false
      priority: "HIGH - Closes Issue-001 CRIT-002 gap"
```

### Change 3: Add Test Pattern Documentation

**Location**: Add new section to `cortex-master.yaml`

**Add**:
```yaml
test_patterns:
  
  single_turn_operation_test:
    description: "Validate single orchestrator operation in isolation"
    example: |
      def test_planning_orchestrator_plan_status():
          result = orchestrator.plan_status("PHASE-01")
          assert result.is_ok()
    use_when: "Testing individual operation correctness"
    skip_when: "Need to test multi-turn continuity"
  
  multi_round_conversation_test:
    description: "Validate multi-turn conversation with state persistence"
    framework: "ConversationSession-based"
    minimum_turns: 3
    
    example_pseudo_code: |
      def test_multi_round_planning_orchestrator():
          session = ConversationSession()
          
          # Turn 1
          turn_1 = session.new_turn(user_input="Get PHASE-01 status")
          turn_1.lens_protocol()  # Executes LENS
          turn_1.request_approval()  # Asks user
          turn_1.approve()  # User approves
          turn_1.execute()  # Runs operation
          assert turn_1.result["phase_id"] == "PHASE-01"
          
          # Turn 2 - State available from Turn 1
          turn_2 = session.new_turn(user_input="What's next?")
          turn_2.lens_protocol()  # LENS executes AGAIN
          turn_2.request_approval()  # Approval requested AGAIN
          turn_2.approve()
          turn_2.execute()
          assert turn_2.context["phase_id"] == turn_1.result["phase_id"]  # State persisted
          
          # Validate
          assert session.lens_executed_per_turn([1, 2])  # BOTH turns
          assert session.approval_requested_per_turn([1, 2])  # BOTH turns
          assert session.audit_trail_valid()
    
    use_when: "Testing orchestrator continuity and multi-turn patterns"
    required_for: "Intent router, Master orchestrator, domain orchestrators"
    governance_rules: [CORE-019, CORE-027, INT-RULE-009]
```

### Change 4: Update Orchestrator AC Requirements

**Location**: All phases with orchestrator tests (PHASE-07, PHASE-08, etc.)

**Add to acceptance_criteria**:
```yaml
multi_round_requirement: |
  This orchestrator AC-ID MUST include test that validates:
  1. Multi-round conversation with 3+ turns
  2. LENS protocol executes on every turn
  3. Approval gate requested on every turn
  4. State persists from Turn N to N+1
  5. Audit trail shows turn progression
  6. Hash chain valid across all turns
  
  Reference test pattern: MULTI_ROUND_CONVERSATION_TEST
```

---

## HOW TO UPDATE ROADMAP

### Step 1: Open `cortex-master.yaml`

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
vim .github/roadmap/cortex-master.yaml
```

### Step 2: Add Testing Framework Section

Find section: `metadata:` (line ~1)

Add after `governance:` section:
```yaml
  testing_framework:
    status: "FRAMEWORK ADOPTED 2026-01-16"
    
    conversation_driven_testing:
      enabled: true
      rationale: "Tests must validate multi-turn orchestrator interaction patterns"
      
      applies_to:
        - "All orchestrator test suites"
        - "Master orchestrator integration tests"
      
      # ... rest of framework config from above ...
```

### Step 3: Update PHASE-07 Entry

Find section: `PHASE-07-INTENT-ROUTER:` (line ~850)

Add field:
```yaml
  multi_round_testing:
    status: "REQUIREMENT ADDED 2026-01-16"
    # ... content from above ...
```

### Step 4: Add Test Patterns Section

Find section: `# =============================================================================`

Add new section before `ACCEPTANCE CRITERIA`:
```yaml
# =============================================================================
# TEST PATTERNS (NEW SECTION - 2026-01-16)
# =============================================================================

test_patterns:
  single_turn_operation_test:
    # ... content from above ...
  
  multi_round_conversation_test:
    # ... content from above ...
```

### Step 5: Commit Changes

```bash
git add -A
git commit -m "roadmap: add multi-round conversation testing pattern (2026-01-16)"
git push origin CORTEX6
```

---

## FILES THAT NEED UPDATING

### Must Update (Core)

- [ ] `.github/roadmap/cortex-master.yaml` - Add framework + pattern docs
- [ ] `.github/roadmap/phases/phase-07-intent-router.yaml` - Add IR-005-01 AC
- [ ] `tests/unit/test_planning_orchestrator.py` - Add multi-round tests
- [ ] `tests/unit/orchestrators/` - Add multi-round tests for all orchestrators

### Should Create (New Files)

- [ ] `tests/fixtures/conversation_session.py` - Session tracking class
- [ ] `tests/fixtures/round_context.py` - RoundInput/RoundOutput classes
- [ ] `tests/fixtures/continuity_validator.py` - Validation assertions
- [ ] `tests/integration/test_multi_round_planning.py` - Planning orchestrator
- [ ] `tests/integration/test_multi_round_ado.py` - ADO orchestrator
- [ ] `tests/integration/test_multi_round_interaction.py` - Interaction orchestrator
- [ ] `tests/integration/test_multi_round_master.py` - Master orchestrator
- [ ] `tests/integration/test_multi_round_audit_trail.py` - Audit validation

### Should Reference (Documentation)

- [ ] `.github/docs/testing-patterns.md` - Document patterns (NEW)
- [ ] `.github/docs/multi-round-conversation-guide.md` - How to write tests (NEW)

---

## VALIDATION CHECKLIST

After updating roadmap:

- [ ] `cortex-master.yaml` valid YAML syntax (no parse errors)
- [ ] All references to `test_patterns` are consistent
- [ ] PHASE-07 still locked after adding new field
- [ ] New AC-ID (IR-005-01) doesn't conflict with existing IDs
- [ ] Governance rules (CORE-019, CORE-027) referenced correctly
- [ ] All orchestrators have multi-round test requirement
- [ ] Git history shows checkpoint before roadmap update
- [ ] Phase_tracker.yaml (if separate) synchronized

---

## EXPECTED OUTCOME

After roadmap update:

```yaml
# cortex-master.yaml will now include:

metadata:
  testing_framework:
    conversation_driven_testing:
      enabled: true
      components: [ConversationSession, RoundContext, ApprovalGate, ContinuityValidator]
      standards_enforced: [CORE-019, CORE-027, INT-RULE-009]

PHASE-07-INTENT-ROUTER:
  multi_round_testing:
    status: "REQUIREMENT ADDED"
    new_ac: "AC-IR-005-01: Multi-Round Conversation Continuity"

test_patterns:
  multi_round_conversation_test:
    description: "ConversationSession-based multi-turn validation"
    minimum_turns: 3
    governance_rules: [CORE-019, CORE-027]
```

**Result**: Roadmap now explicitly requires multi-round tests, provides pattern definition, and adds new AC-ID for Intent Router Phase to validate continuity.

---

## NEXT IMMEDIATE ACTIONS

1. **Review** this roadmap update document (15 min)
2. **Confirm** changes are correct (10 min)
3. **Create** git checkpoint: `git commit -m "checkpoint: before cortex-master roadmap update"` (5 min)
4. **Apply** changes to `cortex-master.yaml` (30 min)
5. **Validate** YAML syntax: `python -m yaml .github/roadmap/cortex-master.yaml` (2 min)
6. **Commit** roadmap update: `git commit -m "roadmap: add multi-round conversation testing pattern"` (5 min)
7. **Start** creating test infrastructure (ConversationSession, etc.) - 8h

**Timeline**: Can start implementation today after roadmap update approval.

---

**Status**: ✅ ROADMAP CHANGES READY TO IMPLEMENT  
**Impact**: Closes Issue-001 CRIT-002, improves test coverage 70%→95%  
**Effort**: 30 min for roadmap update, 26-31 hours for test implementation  
**Go-live**: Ready within 1-2 weeks

