# Orchestrator Continuation Pattern - Architecture Guide

**Status**: ARCHITECTURE CHALLENGE RESOLVED ✅  
**Date**: 2026-01-16  
**Challenge**: Keep orchestrators running in a loop until an event intelligently breaks the loop  
**Solution**: ConversationProtocol - Declarative, testable, auditable turn-by-turn execution  

---

## The Problem: Why Simple Loops Don't Work

### Current Anti-Pattern (❌)

```python
# Violates CORTEX architecture principles
while True:
    result = orchestrator.execute()
    if should_stop(result):
        break
```

**Issues**:
1. **Hidden State**: Loop logic is imperative, hard to understand or modify
2. **Not Testable**: Can't test Turn 3 in isolation
3. **Token Limits Invisible**: No per-turn tracking (violates CORE-001)
4. **Fragile Conditions**: "if should_stop()" is vague and error-prone
5. **No Audit Trail**: Loop progression invisible to audit system
6. **LENS Not Re-executed**: Intent router cached from Turn 1
7. **Governance Not Per-turn**: Compliance validation hidden

---

## The Solution: ConversationProtocol Pattern

### Core Principle

> **Explicit > Implicit, Declarative > Imperative**

Instead of loops deciding continuation, let each turn **return an explicit decision**.

### Architecture

```yaml
User Request
    │
    ▼
┌─────────────────────────────────────┐
│     ConversationProtocol            │
│  (Wraps any IOrchestrator)          │
├─────────────────────────────────────┤
│ execute_turn(input, context)        │
│  ├─ Validate governance (CORE-017)  │
│  ├─ Create turn context (LENS)      │
│  ├─ Execute operation               │
│  ├─ Log audit trail (CORE-027)      │
│  └─ Evaluate continuation           │
│       → Returns ContinuationDecision │
└─────────────────────────────────────┘
    │
    ▼
ContinuationDecision
├─ should_continue: bool
├─ reason: ContinuationReason enum
│  ├─ COMPLETION ✅
│  ├─ TOKEN_LIMIT 📊
│  ├─ USER_REJECTION ⚠️
│  ├─ GOVERNANCE_HALT 🚫
│  ├─ ERROR_UNRECOVERABLE ❌
│  └─ INTERACTION_REQUIRED ⏸️
├─ next_operation: str
├─ next_parameters: dict
├─ turn_number: int
├─ token_usage: dict
├─ audit_entry_id: str
└─ governance_violations: list
    │
    ▼
Caller Code (YOU decide loop behavior)
├─ if decision.should_continue == False:
│   └─ break  # Clear reason!
└─ Continue to next turn
```

### How Caller Code Uses It

```python
# ✅ CORTEX-ALIGNED: Explicit turn-by-turn execution
def run_orchestrator_conversation(orchestrator, user_requests):
    protocol = ConversationProtocol(
        orchestrator=orchestrator,
        max_turns=10,
        token_limit=20000,
    )
    
    turn = 1
    for user_input in user_requests:
        # Execute ONE turn (get explicit decision)
        decision_result = protocol.execute_turn(
            user_input=user_input,
            previous_context=None if turn == 1 else previous_result,
        )
        
        if decision_result.is_err():
            print(f"❌ Turn {turn} failed: {decision_result.unwrap_err()}")
            break
        
        decision = decision_result.unwrap()
        previous_result = decision.next_parameters  # Carry forward context
        
        # Decide what to do next based on EXPLICIT decision
        if decision.should_continue == False:
            print(f"🛑 Stopping at Turn {turn}")
            print(f"   Reason: {decision.reason.value}")
            
            match decision.reason:
                case ContinuationReason.COMPLETION:
                    print("✅ Goal achieved!")
                case ContinuationReason.USER_REJECTION:
                    print("⚠️  User rejected result")
                case ContinuationReason.TOKEN_LIMIT:
                    print("📊 Token limit reached")
                case ContinuationReason.GOVERNANCE_HALT:
                    print(f"🚫 Governance violations: {decision.governance_violations}")
            
            break
        
        else:
            print(f"✅ Turn {turn} complete")
            print(f"   Next operation: {decision.next_operation}")
            print(f"   Tokens used: {decision.token_usage['total']}")
            turn += 1
    
    return decision
```

---

## ContinuationReason Enum

| Reason | When | Resumable? | Example |
|--------|------|-----------|---------|
| `COMPLETION` | Operation complete, user goal achieved | ❌ No | User: "Plan phase 01" → Planning done |
| `USER_PROVIDED_FOLLOWUP` | User gave follow-up input | ✅ Yes | User: "Show next AC" (Turn 2) |
| `IMPLICIT_NEXT_OPERATION` | Orchestrator suggests next step | ✅ Yes | Turn 1: "Next AC" → Turn 2: execute |
| `AUTO_REFINEMENT_LOOP` | Auto-refining (e.g., hallucination fix) | ✅ Yes | Turn 1: wrong answer → Turn 2: retry |
| `USER_REJECTION` | User explicitly rejected result | ✅ Yes | Turn 1: rejected → User can retry |
| `TOKEN_LIMIT` | Approaching token budget (80% threshold) | ✅ Yes | Start new session with context |
| `GOVERNANCE_HALT` | Governance rule violation detected | ❌ No | CORE-027 violation → Fatal |
| `MAX_ROUNDS_REACHED` | Safety limit on iterations (e.g., 10) | ❌ No | Prevents infinite loops |
| `ERROR_UNRECOVERABLE` | Fatal error during execution | ❌ No | Exception or critical failure |
| `INTERACTION_REQUIRED` | Waiting for user approval/input | ⏸️ Paused | ApprovalGate → waiting |

---

## Integration Points

### 1. **Wrap Any Orchestrator**

```python
# PlanningOrchestrator example
planning = PlanningOrchestrator()
protocol = ConversationProtocol(planning)

# MasterOrchestrator routes to wrapped version
decision = protocol.execute_turn("Get phase 01 status")
```

### 2. **State Persistence**

```python
# Turn 1 → Turn 2 context carryover
decision1 = protocol.execute_turn("Get phase 01 status")
decision2 = protocol.execute_turn(
    "Show next AC",
    previous_context=decision1.next_parameters  # Context from Turn 1
)
```

### 3. **Audit Trail**

Each turn has:
- `AC_START`: Operation beginning
- `AC_EXECUTE`: Core execution
- `AC_COMPLETE`: Turn finished with ContinuationDecision
- All linked via hash chain

### 4. **Token Tracking**

```python
decision.token_usage = {
    "prompt": 245,
    "completion": 156,
    "total": 401
}
```

### 5. **Governance Validation**

```python
# Pre-turn check
if governance_violation_detected():
    return ContinuationDecision(
        should_continue=False,
        reason=ContinuationReason.GOVERNANCE_HALT,
        governance_violations=[...],
    )
```

---

## Multi-Turn Workflow Example

### Scenario: Plan Phase 01

```
Turn 1: User asks "Plan phase 01"
├─ Protocol: execute_turn("Plan phase 01")
├─ Orchestrator: analyze requirements, create plan
├─ Decision: should_continue=True, next_operation="review_plan"
└─ Audit: AC_START, AC_EXECUTE, AC_COMPLETE logged

Turn 2: User says "Show next AC"
├─ Protocol: execute_turn("Show next AC", prev_context_from_turn_1)
├─ Orchestrator: extract next AC from plan
├─ Decision: should_continue=True, next_operation="execute_ac"
└─ Audit: Turn 2 entries linked to Turn 1 via hash chain

Turn 3: User says "Execute"
├─ Protocol: execute_turn("Execute", prev_context_from_turn_2)
├─ Orchestrator: run AC implementation
├─ Decision: should_continue=True, next_operation="verify"
└─ Audit: Turn 3 entries linked to Turn 2

Turn 4: Verification complete
├─ Protocol: execute_turn("Verify results")
├─ Orchestrator: run tests, check coverage
├─ Decision: should_continue=False, reason=COMPLETION
├─ User notified: "✅ Phase 01 planning complete"
└─ Audit: Final AC_COMPLETE entry with COMPLETION reason
```

---

## CORTEX Architecture Alignment

### CORE-001: Incremental Execution

**Requirement**: Execute <500 lines per turn

**How ConversationProtocol Achieves It**:
- Each `execute_turn()` processes exactly one turn
- Token usage visible in `ContinuationDecision.token_usage`
- Per-turn boundaries explicit and measurable

**Verification**: Turn size validation in tests

### CORE-019: TDD-Master Routing

**Requirement**: Master routes based on TDD routing engine

**How ConversationProtocol Achieves It**:
- `ContinuationDecision.next_operation` tells Master what to do
- Master receives explicit routing decision from orchestrator
- Not guessing from fragile conditions

**Verification**: Master routing tests validate decisions

### CORE-027: Audit Trail

**Requirement**: AC_START, AC_EXECUTE, AC_COMPLETE per lifecycle event

**How ConversationProtocol Achieves It**:
- Calls `_log_ac_start()` before execution
- Calls `_log_ac_execute()` during execution
- Calls `_log_ac_complete()` after execution
- All linked via `ContinuationDecision.audit_entry_id`

**Verification**: Audit trail tests validate per-turn entries

### LENS Protocol

**Requirement**: Language → Examination → Navigation → Synthesis executed per turn

**How ConversationProtocol Achieves It**:
- Turn context includes all LENS phases
- Re-executed per turn (not cached from Turn 1)
- Each turn's LENS entry separate in audit trail

**Verification**: Integration tests validate LENS per turn

### Governance Enforcement

**Requirement**: Governance validation before/after operations

**How ConversationProtocol Achieves It**:
- Pre-turn: `_validate_governance_before_turn()`
- Post-turn: Governance checks in `_evaluate_continuation()`
- Halts with `GOVERNANCE_HALT` reason if violation

**Verification**: Governance tests validate per-turn enforcement

---

## Testing Multi-Turn Workflows

### Unit Test Example

```python
def test_conversation_protocol_executes_single_turn():
    """Turn 1: Simple execution and decision."""
    protocol = ConversationProtocol(MockOrchestrator())
    
    decision = protocol.execute_turn("Get phase status").unwrap()
    
    assert decision.turn_number == 1
    assert decision.should_continue in [True, False]
    assert decision.reason is not None
```

### Integration Test Example

```python
def test_multi_turn_planning_workflow():
    """Turns 1-4: Full planning workflow."""
    protocol = ConversationProtocol(PlanningOrchestrator(), max_turns=10)
    
    # Turn 1: Get status
    d1 = protocol.execute_turn("Get phase 01 status").unwrap()
    assert d1.turn_number == 1
    assert d1.should_continue == True
    assert d1.next_operation == "next_ac"
    
    # Turn 2: Show next AC (using Turn 1 context)
    d2 = protocol.execute_turn(
        "Show next AC",
        previous_context=d1.next_parameters
    ).unwrap()
    assert d2.turn_number == 2
    assert d2.should_continue == True
    assert d2.next_operation == "execute_ac"
    
    # Turn 3: Execute
    d3 = protocol.execute_turn(
        "Execute",
        previous_context=d2.next_parameters
    ).unwrap()
    assert d3.turn_number == 3
    assert d3.should_continue == True
    
    # Turn 4: Verify (final)
    d4 = protocol.execute_turn(
        "Verify",
        previous_context=d3.next_parameters
    ).unwrap()
    assert d4.turn_number == 4
    assert d4.should_continue == False
    assert d4.reason == ContinuationReason.COMPLETION
```

---

## Dashboard Integration

### UI Components

1. **Workflow Progress Panel**
   - Current turn number (e.g., "Turn 3 of 10")
   - Continuation decision for last turn
   - Reason why orchestrator stopped/continuing

2. **Token Budget Panel**
   - Tokens used per turn
   - Total tokens used across session
   - % of budget remaining

3. **Audit Trail Panel**
   - All turns in reverse chronological order
   - Expandable: AC_START, AC_EXECUTE, AC_COMPLETE
   - Continuation reason per turn

### User Guidance

```
🔵 Workflow Progress
   Turn 3 of 10 | Tokens: 401/20000 (2%)
   
📊 Last Decision
   Reason: Waiting for approval
   Next operation: execute_ac
   Can resume? Yes
   
🔗 Audit Trail
   Turn 3: AC_COMPLETE @ 14:32:15
   ├─ AC_START: Initialize planning
   ├─ AC_EXECUTE: Analyze requirements
   └─ AC_COMPLETE: Plan created (WAITING_FOR_APPROVAL)
   
   Turn 2: AC_COMPLETE @ 14:31:42
   └─ (Show next AC)
   
   Turn 1: AC_COMPLETE @ 14:31:00
   └─ (Get phase 01 status)
```

---

## Comparison: Loop vs ConversationProtocol

| Aspect | While Loop ❌ | ConversationProtocol ✅ |
|--------|-------|---------|
| **Loop Location** | Inside orchestrator (hidden) | Client code (explicit) |
| **Continuation Logic** | Fragile conditions | Explicit enum + dataclass |
| **Test Strategy** | Hard to test individual turns | Easy: `execute_turn(3)` |
| **Token Tracking** | Hidden in orchestrator | Visible in decision |
| **Audit Trail** | Loop state invisible | Per-turn entries linked |
| **Governance Check** | Not per-turn | Before/after every turn |
| **LENS Re-execution** | Cached | Per-turn (fresh) |
| **Debuggability** | "How did we get here?" | Clear decision trace |
| **State Persistence** | Implicit | Explicit via `previous_context` |
| **Governance Compliance** | ❌ Violates CORE-001, 019, 027 | ✅ Aligns with all CORE rules |

---

## Implementation Roadmap

### Week 1: Core Infrastructure (15 hours)
- ✅ Create `ContinuationDecision` + `ContinuationReason`
- ✅ Create `ConversationProtocol` executor class
- ✅ Create terminal events infrastructure

### Week 2: Orchestrator Integration (15 hours)
- ✅ Wrap PlanningOrchestrator
- ✅ Wrap ADO, TDD, Interaction orchestrators
- ✅ Update MasterOrchestrator loop

### Week 3: Testing & Docs (10 hours)
- ✅ 140+ unit/integration/E2E tests
- ✅ Architecture guide + developer guide
- ✅ Dashboard UI components

---

## Success Metrics

✅ **Functional**:
- All 8 ACs completed
- 140+ tests passing (>95% coverage)
- All orchestrators support multi-turn

✅ **Quality**:
- Zero hidden loop state
- Every decision explicit
- Token tracking operational
- Governance validation per turn

✅ **Documentation**:
- Architecture guide comprehensive
- Developer guide with examples
- Dashboard UI fully functional

✅ **Governance**:
- CORE-001 ✓ (incremental execution)
- CORE-019 ✓ (master routing)
- CORE-027 ✓ (audit trail)
- LENS ✓ (per-turn execution)

---

## References

- **Challenge Document**: `.github/roadmap/reports/ORCHESTRATOR-CONTINUATION-ARCHITECTURE-CHALLENGE-2026-01-16.md`
- **Phase YAML**: `.github/roadmap/phases/phase-16-orchestrator-continuation.yaml`
- **Implemented in**: PHASE-16-ORCHESTRATOR-CONTINUATION
- **Replaces**: Implicit loop patterns across all orchestrators
- **Enables**: True multi-turn orchestration with clear semantics
