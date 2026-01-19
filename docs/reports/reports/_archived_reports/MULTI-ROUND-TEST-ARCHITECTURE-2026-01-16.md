# MULTI-ROUND INTERACTION TEST ARCHITECTURE - ANALYSIS & SOLUTION
**Challenge: Better Test Pattern for Orchestrator Continuity & State Persistence**

Generated: 2026-01-16  
Status: READY FOR IMPLEMENTATION  
Scope: Planning, ADO, Interaction, Master, and All Domain Orchestrators

---

## YOUR INTENT - REFLECTED USING LENS PROTOCOL

### What You're Asking For

**Language Phase (Parse Request)**:
- Update tests to check for **multiple rounds of interaction**
- Apply pattern to: Planning, ADO, Interaction orchestrators
- **Holistically review** current pattern
- **Challenge** with better solution that **adheres with CORTEX architecture**
- **Update the roadmap** with new approach

**Examination Phase (Code Analysis)**:
- Current tests: Single-turn, isolated operations
- Gap identified: No multi-round/multi-turn persistence testing
- Issue-001 identified: Intent Router bypassed after Turn 1 (CRIT-002)
- Current fix: IR-004-02 tests persistence, but only within Comprehension Loop
- Gap: **NO cross-orchestrator multi-turn continuity tests exist**

**Navigation Phase (Relationship Analysis)**:
```
Current Architecture:
├── Planning Orchestrator (single operations: plan_status, next_ac)
├── ADO Orchestrator (single operations: sync_workitems, get_status)
├── Interaction Orchestrator (manages conversation state)
├── Master Orchestrator (delegates to sub-orchestrators)
└── PROBLEM: Each orchestrator tested in isolation, not in multi-round conversation

Required Architecture:
├── ConversationSession (tracks state across multiple turns)
├── RoundContext (maintains context from previous round)
├── OrchestratorChain (hands off from one to next with state)
├── AuditTrail (captures Turn N: [LENS→Route→Approve→Execute])
└── Continuity Validation (asserts state persists & is reused)
```

**Synthesis Phase (Better Solution)**:
I'm proposing a **Conversation-Driven Test Framework** that adheres to CORTEX architecture:

```yaml
current_pattern: "Single-turn isolation tests"
problem: "No validation of multi-turn state persistence, approval gate continuity"

proposed_pattern: "ConversationSession-based round-trip tests"
benefits:
  - Tests state persistence across rounds
  - Validates LENS protocol re-executes per turn
  - Verifies approval gates on every turn (not just Turn 1)
  - Captures realistic multi-round audit trails
  - Enables end-to-end conversation continuity validation
  - Better reflects actual LLM interaction patterns
```

---

## CURRENT STATE ANALYSIS

### What Exists Today

| Component | Current Test | Status | Gap |
|-----------|--------------|--------|-----|
| Planning Orchestrator | Single operations tested | ✅ Exists | ❌ No multi-turn |
| ADO Orchestrator | Single operations tested | ✅ Exists | ❌ No multi-turn |
| Interaction Orchestrator | ComprehensionLoop tests | ✅ Exists | ⚠️ Only Turn 1→2 in loop |
| Master Orchestrator | Integration test exists | ✅ Exists | ❌ No multi-round |
| LENS Protocol | IR-004-02 tests (2 turns) | ✅ Exists | ⚠️ Only in Interaction context |
| Approval Gate | IR-004-02 tests per-turn | ✅ Exists | ⚠️ Only in Interaction context |
| Multi-Round Flow | NO TESTS | ❌ MISSING | 🔴 CRITICAL GAP |

### What's NOT Being Tested

```python
# ❌ MISSING: Multi-round orchestrator conversation
Turn 1:
  User: "Create a plan for Phase 01"
  → Master receives request
  → Delegates to Planning Orchestrator
  → Planning → Interaction (comprehension)
  → User approves
  → Planning executes
  → Response returned

Turn 2:
  User: "Show me next AC-ID"
  → Master receives request (should re-run LENS, not skip it!)
  → Delegates to Planning Orchestrator
  → Planning → Interaction (NEW comprehension)  ← MISSING TEST
  → User approves (re-requested)              ← MISSING TEST
  → Planning executes
  → Response returned (state from Turn 1 available)  ← MISSING TEST

Turn 3, 4, N... (same pattern)
```

---

## PROPOSED SOLUTION: CONVERSATION-DRIVEN TEST FRAMEWORK

### Architecture (CORTEX-Aligned)

```yaml
cortex_test_architecture:
  principle: "Tests should mirror actual LLM conversation patterns"
  scope: "Turn-by-turn orchestrator interaction"
  
  components:
    conversation_session:
      purpose: "Track state across multiple turns in single conversation"
      lifetime: "Created at Turn 1, lives through all turns"
      tracks:
        - previous_context: "What was decided in Turn N-1"
        - turn_number: "Which turn is this"
        - audit_entries: "All audit events this turn"
        - state_snapshot: "Mutable state that persists"
    
    round_context:
      purpose: "What this specific turn needs to know"
      contains:
        - user_input: "What user asked in THIS turn"
        - session_history: "Reference to previous turns"
        - approval_status: "Was this turn approved"
        - execution_result: "What happened"
    
    orchestrator_chain:
      purpose: "How orchestrators hand off with state"
      flow:
        1: "Master receives request (user_input + session_history)"
        2: "Master delegates to domain orchestrator"
        3: "Domain calls Interaction for comprehension"
        4: "Interaction generates context (can reference session history)"
        5: "Master presents to user for approval"
        6: "If approved, executes"
        7: "Records Turn N completion in session"
        8: "Returns to user with state ready for Turn N+1"
    
    continuity_validation:
      purpose: "Assertions that state persisted correctly"
      checks:
        - "Turn N+1 sees Turn N results"
        - "Approval gate called each turn"
        - "LENS protocol re-executed per turn"
        - "Audit trail shows [AC_START/LENS/APPROVE/EXECUTE] per turn"
        - "Hash chain unbroken across turns"
```

### Test Pattern (Pseudo-Code)

```python
class TestMultiRoundOrchestratorContinuity:
    """
    Test multi-round conversation with state persistence.
    
    Adheres to CORTEX architecture:
    - LENS protocol executed on EVERY turn
    - Approval gate requested on EVERY turn
    - State persists across turns
    - Audit trail captures turn sequence
    """
    
    def test_multi_round_planning_orchestrator_continuity(self):
        """
        CORTEX Multi-Round Pattern Test:
        
        Turn 1: Get phase status for PHASE-01
        Turn 2: Show next AC-ID (uses Turn 1 context)
        Turn 3: Get next AC-ID again (uses Turn 1-2 context)
        
        Validates:
        - State from Turn 1 available in Turn 2
        - LENS protocol runs on Turn 2 (not skipped)
        - Approval gate presented on Turn 2
        - Audit trail shows distinct Turn N entries
        - Hash chain unbroken
        """
        
        # =====================================================================
        # TURN 1: Get Phase Status
        # =====================================================================
        
        # 1.1: Create conversation session (lives through all turns)
        session = ConversationSession(
            id="conv-2026-01-16-001",
            orchestrator="PlanningOrchestrator",
            user_id="asif",
            created_at=datetime.utcnow()
        )
        
        # 1.2: User makes request
        turn_1_input = RoundInput(
            session_id=session.id,
            turn_number=1,
            user_request="Show me the status of PHASE-01",
            phase_id="PHASE-01"
        )
        
        # 1.3: Master receives request
        master = MasterOrchestrator.instance()
        
        # 1.4: LENS Protocol executes (Stage 1: Language Phase)
        lang_result = IntentReflectionEngine.language_phase(turn_1_input.user_request)
        assert lang_result["intent"] == "GET_PHASE_STATUS"
        assert lang_result["parameters"]["phase_id"] == "PHASE-01"
        
        # 1.5: Interaction Orchestrator builds context (Stage 2: Examination)
        context = InteractionOrchestrator.build_comprehension(
            intent=lang_result["intent"],
            parameters=lang_result["parameters"],
            session=session
        )
        assert "phase_status" in context
        assert context["phase_status"]["phase_id"] == "PHASE-01"
        
        # 1.6: User approval (Stage 3: Approval)
        approval = ApprovalGate.request_approval(
            context=context,
            turn_number=1
        )
        # Simulate user approval
        approval.approve()
        
        # 1.7: Execution (Stage 4: Execute)
        execution = PlanningOrchestrator.execute_with_comprehension(
            operation="plan_status",
            parameters={"phase_id": "PHASE-01"},
            session=session
        )
        assert execution.is_ok()
        turn_1_result = execution.unwrap()
        assert turn_1_result["phase_id"] == "PHASE-01"
        
        # 1.8: Record Turn 1 completion
        session.record_turn(
            turn_number=1,
            context=context,
            result=turn_1_result,
            audit_entries=[
                {"operation": "AC_START", "turn": 1},
                {"operation": "LENS_LANGUAGE", "turn": 1},
                {"operation": "LENS_EXAMINATION", "turn": 1},
                {"operation": "APPROVAL_GATE", "turn": 1, "status": "APPROVED"},
                {"operation": "AC_EXECUTE", "turn": 1},
                {"operation": "AC_COMPLETE", "turn": 1}
            ]
        )
        
        # =====================================================================
        # TURN 2: Show Next AC-ID (WITH STATE FROM TURN 1)
        # =====================================================================
        
        # 2.1: User makes new request (session still alive!)
        turn_2_input = RoundInput(
            session_id=session.id,  # SAME session
            turn_number=2,
            user_request="Show me the next AC-ID to implement",
            # Note: NO phase_id provided - should infer from Turn 1
        )
        
        # 2.2: Master receives request
        # CRITICAL: Master should NOT skip LENS protocol on Turn 2!
        
        # 2.3: LENS Protocol executes AGAIN (Stage 1: Language Phase)
        lang_result_2 = IntentReflectionEngine.language_phase(turn_2_input.user_request)
        assert lang_result_2["intent"] == "GET_NEXT_AC_ID"
        
        # 2.4: Interaction Orchestrator builds context (Stage 2: Examination)
        # NOTE: Can reference session history from Turn 1!
        context_2 = InteractionOrchestrator.build_comprehension(
            intent=lang_result_2["intent"],
            parameters=lang_result_2["parameters"],
            session=session,  # Session has Turn 1 data
            previous_context=session.get_turn(1)["context"]  # Reference Turn 1
        )
        
        # 2.5: Validate context includes Turn 1 data
        assert context_2["phase_id"] == session.get_turn(1)["result"]["phase_id"]
        assert "next_ac_id" in context_2
        
        # 2.6: User approval requested AGAIN (not skipped!)
        approval_2 = ApprovalGate.request_approval(
            context=context_2,
            turn_number=2
        )
        # Simulate user approval
        approval_2.approve()
        
        # 2.7: Execution
        execution_2 = PlanningOrchestrator.execute_with_comprehension(
            operation="next_ac",
            parameters={"phase_id": context_2["phase_id"]},
            session=session
        )
        assert execution_2.is_ok()
        turn_2_result = execution_2.unwrap()
        
        # 2.8: Record Turn 2 completion
        session.record_turn(
            turn_number=2,
            context=context_2,
            result=turn_2_result,
            audit_entries=[
                {"operation": "AC_START", "turn": 2},
                {"operation": "LENS_LANGUAGE", "turn": 2},  # ← RE-RUN per CORTEX
                {"operation": "LENS_EXAMINATION", "turn": 2},
                {"operation": "APPROVAL_GATE", "turn": 2, "status": "APPROVED"},  # ← RE-REQUESTED
                {"operation": "AC_EXECUTE", "turn": 2},
                {"operation": "AC_COMPLETE", "turn": 2}
            ]
        )
        
        # =====================================================================
        # VALIDATION: MULTI-ROUND CONTINUITY
        # =====================================================================
        
        # Verify Turn 1 → Turn 2 state flow
        assert session.get_turn(1)["result"]["phase_id"] == session.get_turn(2)["context"]["phase_id"]
        
        # Verify LENS executed both turns
        turn_1_audit = session.get_turn(1)["audit"]
        turn_2_audit = session.get_turn(2)["audit"]
        
        assert any(e["operation"] == "LENS_LANGUAGE" for e in turn_1_audit)
        assert any(e["operation"] == "LENS_LANGUAGE" for e in turn_2_audit)
        
        # Verify approval gate called both turns
        assert any(e["operation"] == "APPROVAL_GATE" for e in turn_1_audit)
        assert any(e["operation"] == "APPROVAL_GATE" for e in turn_2_audit)
        
        # Verify audit trail shows turn progression
        all_audit = session.get_all_audit_entries()
        turn_1_entries = [e for e in all_audit if e.get("turn") == 1]
        turn_2_entries = [e for e in all_audit if e.get("turn") == 2]
        
        assert len(turn_1_entries) == 6  # START/LENS_LANG/LENS_EXAM/APPROVE/EXECUTE/COMPLETE
        assert len(turn_2_entries) == 6
        
        # Verify hash chain unbroken
        assert session.verify_hash_chain() is True
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Create Test Infrastructure (Week 1)

| Component | Purpose | Effort | Status |
|-----------|---------|--------|--------|
| ConversationSession | Track state across turns | 2h | TODO |
| RoundInput/RoundContext | Represent single turn | 1h | TODO |
| RoundOutput/RoundContext | Return multi-turn data | 1h | TODO |
| ApprovalGate.request_approval() | Track approval per turn | 1h | TODO |
| OrchestratorChain | Hand off with state | 2h | TODO |
| ContinuityValidator | Assert state persistence | 1h | TODO |

**Subtotal**: 8 hours

### Phase 2: Update Orchestrator Tests (Week 1-2)

| Orchestrator | Test Type | Effort | Status |
|--------------|-----------|--------|--------|
| Planning Orchestrator | Multi-round (3-5 turns) | 3h | TODO |
| ADO Orchestrator | Multi-round (3-5 turns) | 3h | TODO |
| Interaction Orchestrator | Multi-round with rejection path | 3h | TODO |
| Master Orchestrator | Full E2E orchestration chain | 4h | TODO |
| Domain Orchestrators | Multi-round template | 2h per orchestrator | TODO |

**Subtotal**: 15-20 hours

### Phase 3: Audit Trail Validation (Week 2)

| Component | Purpose | Effort |
|-----------|---------|--------|
| Audit Trail Capture | Record per-turn events | 2h |
| Hash Chain Validation | Verify unbroken chain | 2h |
| Turn Progression Asserts | Validate turn N→N+1 | 1h |
| Multi-Round Reports | Generate test reports | 1h |

**Subtotal**: 6 hours

**Total Effort**: 29-34 hours

---

## FILES TO CREATE/UPDATE

### New Files (Test Infrastructure)

```
tests/fixtures/
├── conversation_session.py          # ConversationSession class
├── round_context.py                 # RoundInput/RoundOutput classes
├── approval_gate_mock.py            # Mock approval gate for testing
└── continuity_validator.py          # Assertions for multi-round validation

tests/integration/
├── test_multi_round_planning.py     # Planning orchestrator 5-turn test
├── test_multi_round_ado.py          # ADO orchestrator multi-turn test
├── test_multi_round_interaction.py  # Interaction orchestrator test
├── test_multi_round_master.py       # Master orchestrator full chain
└── test_multi_round_audit_trail.py  # Audit trail validation
```

### Updated Files

```
.github/roadmap/cortex-master.yaml
  └── Add: multi_round_testing pattern requirements
  └── Add: ConversationSession as pattern standard
  └── Add: Per-turn LENS + Approval validation requirement

.github/roadmap/phases/phase-07-intent-router.yaml
  └── Add: IR-005: Multi-round conversation continuity (NEW AC)
  └── Add: Test requirements for all IR-xxx ACs

tests/unit/test_planning_orchestrator.py
  └── Add: Multi-round planning tests

tests/unit/orchestrators/
  └── Add: Multi-round tests for all orchestrators
```

---

## CORTEX ARCHITECTURE ALIGNMENT

### How This Solution Adheres to CORTEX

| CORTEX Principle | How Multi-Round Tests Implement It |
|------------------|-----------------------------------|
| **LENS Protocol** | Executed on EVERY turn (not skipped) |
| **Approval Gates** | Requested on EVERY turn (not cached) |
| **Audit Trail** | Per-turn entries with turn numbers |
| **State Persistence** | ConversationSession maintains across turns |
| **Governance (CORE-027)** | AC_START/EXECUTE/COMPLETE per turn |
| **Hash Chain** | Unbroken validation across all turns |
| **Multi-Orchestrator** | Turn handoff with state passing |
| **Intent Routing** | Master re-routes on each turn |

### Specific CORTEX Rules Enforced

```yaml
governance_compliance:
  CORE-017: "Strict governance - enforced via approval gate per turn"
  CORE-019: "TDD-Master routing - LENS on every turn (not cached)"
  CORE-027: "Audit trail - AC_START/EXECUTE/COMPLETE per turn"
  CORE-026: "Git checkpoints - per-session completion"
  INT-RULE-009: "Auto-challenge - comprehension re-evaluated each turn"
```

---

## EXPECTED TEST RESULTS

### After Implementation

```
Test Results:
✅ test_multi_round_planning_orchestrator_continuity (Turn 1-5)
   ├─ Turn 1: Get phase status
   ├─ Turn 2: Get next AC (with Turn 1 context)
   ├─ Turn 3: Execute AC (with Turn 1-2 context)
   ├─ Turn 4: Request approval re-execution (rejections path)
   └─ Turn 5: Final status with all turns integrated

✅ test_multi_round_ado_orchestrator_continuity (Turn 1-3)
   ├─ Turn 1: Sync work items
   ├─ Turn 2: Check pipeline status (with Turn 1 context)
   └─ Turn 3: Update based on feedback

✅ test_multi_round_interaction_orchestrator (Turn 1-4)
   ├─ Turn 1: Initial comprehension + approval
   ├─ Turn 2: Refined comprehension (APPROVED)
   ├─ Turn 3: Refinement loop (CLARIFICATION_REQUESTED)
   └─ Turn 4: Final context with decision

✅ test_master_orchestrator_full_chain (Turn 1-5 across multiple orchestrators)
   ├─ Master routes to Planning (Turn 1-2)
   ├─ Master routes to ADO (Turn 3)
   ├─ Master routes to Interaction (Turn 4)
   └─ Master aggregates and returns (Turn 5)

✅ test_audit_trail_multi_round (Validation)
   ├─ 5 turns × 6 events/turn = 30+ audit entries
   ├─ Hash chain validation: PASS
   ├─ Turn progression: PASS
   └─ Governance compliance: PASS

Aggregate Stats:
├─ Total Tests: 15-20
├─ Total Turns Tested: 40-60
├─ Total Audit Entries Validated: 200+
└─ CORTEX Compliance: 100%
```

---

## ROADMAP UPDATE REQUIREMENTS

### In `cortex-master.yaml`

```yaml
# ADD to phase_tracker section:

testing_patterns:
  multi_round_conversation:
    status: "NEW STANDARD (from 2026-01-16)"
    applies_to:
      - "All orchestrator tests"
      - "Master orchestrator integration"
      - "Domain orchestrator suites"
    requirement: |
      Each orchestrator test suite MUST include multi-round continuity tests
      that validate:
      1. LENS protocol executes on EVERY turn (not cached/skipped)
      2. Approval gate requested on EVERY turn
      3. State persists from Turn N to Turn N+1
      4. Audit trail captures turn-by-turn progression
      5. Hash chain remains unbroken across all turns
    
    minimum_rounds: 3
    test_file_pattern: "test_multi_round_*orchestrator*.py"
    
    governance_compliance:
      - CORE-019: "TDD-Master routing - re-evaluated per turn"
      - CORE-027: "Audit trail - AC_START/EXECUTE/COMPLETE per turn"
      - INT-RULE-009: "Auto-challenge per turn"

# ADD to metadata section:

testing_framework:
  conversation_driven_testing:
    status: "ADOPTED 2026-01-16"
    rationale: "Better reflects LLM multi-turn interaction patterns"
    components:
      - ConversationSession: "Track state across turns"
      - RoundContext: "Single turn input/output"
      - ApprovalGate: "Per-turn approval requirement"
      - ContinuityValidator: "Assertions for state persistence"
```

### In `phase-07-intent-router.yaml`

```yaml
# ADD new AC-ID:

acceptance_criteria:
  - ac_id: "AC-IR-005-01"
    title: "Multi-Round Conversation Continuity"
    description: |
      Verify that Interaction Orchestrator maintains conversation state
      across multiple user turns, with LENS protocol re-execution on
      each turn and approval gates re-requested (not cached).
    
    tests:
      - test_ir_005_01_multi_round_planning_continuity
      - test_ir_005_01_multi_round_ado_continuity
      - test_ir_005_01_multi_round_master_chain
      - test_ir_005_01_audit_trail_per_turn
      - test_ir_005_01_hash_chain_unbroken
    
    audit_trail_requirements:
      - "AC_START (Turn 1, 2, 3...)"
      - "LENS_LANGUAGE per turn"
      - "LENS_EXAMINATION per turn"
      - "APPROVAL_GATE per turn"
      - "AC_EXECUTE per turn"
      - "AC_COMPLETE per turn"
```

---

## SUMMARY - WHAT CHANGED

### Current State (❌ PROBLEMS)

```
✗ Tests are single-turn, isolated operations
✗ No validation of LENS re-execution per turn
✗ No verification of approval gate re-request
✗ Intent router tested in isolation (IR-004 only)
✗ Multi-orchestrator conversation not tested end-to-end
✗ Issue-001 CRIT-002 gap: "Intent Router bypassed after Turn 1"
```

### Proposed State (✅ SOLUTIONS)

```
✓ Tests are multi-round with ConversationSession state tracking
✓ LENS protocol validated to execute on EVERY turn
✓ Approval gate validated to be requested on EVERY turn
✓ Interaction orchestrator tested within Master orchestration context
✓ Multi-orchestrator conversation tested end-to-end (5+ turn sequences)
✓ Issue-001 CRIT-002 RESOLVED: All turns re-evaluate intent
✓ Audit trail captures Turn N progression with full details
✓ Hash chain validation across all turns
✓ CORTEX architecture rules enforced via tests
```

---

## NEXT STEPS

### Immediate (Next 2 Hours)

1. **Review** this analysis
2. **Confirm** proposed architecture matches your vision
3. **Approve** implementation roadmap
4. **Create** git checkpoint: `checkpoint: before multi-round-testing`

### This Week

1. **Create** test infrastructure (ConversationSession, etc.) - 8h
2. **Update** Planning Orchestrator tests - 3h
3. **Update** ADO Orchestrator tests - 3h
4. **Validate** audit trail per-turn - 2h

### Next Week

1. **Update** Interaction Orchestrator tests - 3h
2. **Update** Master Orchestrator tests - 4h
3. **Update** roadmap with new pattern - 1h
4. **Full validation** across all phases - 2h

**Total**: 26-31 hours

---

**Status**: ✅ READY FOR IMPLEMENTATION  
**Architecture Alignment**: 100% CORTEX-compliant  
**Compliance**: CORE-019, CORE-027, INT-RULE-009  
**Expected Impact**: Resolves Issue-001 CRIT-002, validates multi-round continuity

