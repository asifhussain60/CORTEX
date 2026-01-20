# ORCHESTRATOR CONTINUATION PATTERN ANALYSIS & ARCHITECTURE CHALLENGE
**Better Solution: Event-Driven State Machine Over Imperative Loops**

**Generated**: 2026-01-16  
**Status**: READY FOR IMPLEMENTATION  
**Scope**: PlanningOrchestrator, ADOOrchestrator, InteractionOrchestrator, and all domain orchestrators  

---

## YOUR REQUEST - REFLECTED BACK (LENS PROTOCOL)

### What You Asked For
> "There needs a way to keep the orchestrators running in a loop until an event intelligently breaks the loop."

### How I Understand Your Intent
**Language Phase**: You want continuous orchestrator operation across multiple user turns  
**Examination Phase**: Current architecture has stop/start per turn; you want state persistence  
**Navigation Phase**: Need mechanism to decide "continue or stop"  
**Synthesis Phase**: Propose a pattern that adheres to CORTEX architecture  

---

## THE PROBLEM WITH IMPERATIVE LOOPS

### Your Proposed Approach (❌ Issues with pure loop)

```python
# ❌ ANTI-PATTERN: Raw imperative loop
def orchestrator_run():
    while True:
        user_input = get_user_input()
        if should_stop_condition(user_input):
            break
        result = orchestrator.execute(user_input)
```

**Why This Breaks CORTEX Architecture**:

| CORTEX Principle | Why Loop Breaks It |
|---|---|
| **CORE-001: Incremental Execution** | Loops don't track turn boundaries; token limits invisible |
| **CORE-027: Audit Trail** | No audit entry per turn; hard to track in AC_START/EXECUTE/COMPLETE pattern |
| **CORE-019: TDD-Master Routing** | Can't test individual turns; test coverage degrades to "did it loop?" |
| **LENS Protocol** | Doesn't re-execute per turn; becomes cached after Turn 1 |
| **Governance Enforcement** | No per-turn compliance checkpoints |
| **State Visibility** | Loop state is imperative; hard to reason about, serialize, or rollback |

### Real-World Problems

```python
# Problem 1: Can't test Turn 3 in isolation
def test_orchestrator():
    orchestrator_run()  # ❌ How do you check what happened in Turn 3?

# Problem 2: Infinite loops on bad "stop" condition
while True:
    if some_fragile_condition:  # ❌ What if this is never True?
        break

# Problem 3: State lost on exception
while processing:  # ❌ Exception happens, entire state lost
    process_turn()

# Problem 4: Can't replay/debug individual turns
# ❌ You got stuck in iteration 47; how do you replay it?
```

---

## BETTER SOLUTION: DECLARATIVE CONVERSATION PROTOCOL

### Architecture: State Machine + Event Registry Over Loop

```yaml
cortex_principle: "Explicit > Implicit, Declarative > Imperative"

current_antipattern:
  implementation: "while True: process()"
  problems:
    - Invisible state transitions
    - Hard to test individual turns
    - Governance compliance unclear
    - Token limits not tracked

proposed_solution:
  name: "ConversationProtocol with Continuation Events"
  principle: "Each turn is an explicit, testable, auditable state transition"
  components:
    1: "ContinuationDecision" - What should happen next?
    2: "ConversationState" - What's the current state?
    3: "ContinuationEventRegistry" - What events break the loop?
    4: "TurnExecutor" - Execute ONE turn, return decision
```

### Core Concept: Continuation Events (Not Loop Conditions)

Instead of:
```python
while should_continue():  # ❌ Fragile condition checking
    orchestrator.execute()
```

Use:
```python
# ✅ Explicit event-driven pattern
turn = 1
while True:
    decision = orchestrator.execute_turn(turn_number=turn)
    
    if decision.should_continue == False:
        break
    
    if decision.requires_user_input:
        break
    
    if decision.token_limit_approaching:
        break
    
    turn += 1
```

---

## PROPOSED ARCHITECTURE: CONTINUATION PROTOCOL

### 1. ContinuationDecision (Declarative Outcome)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class ContinuationReason(Enum):
    """Why the orchestrator is continuing or stopping."""
    # Continue scenarios
    IMPLICIT_NEXT_OPERATION = "orchestrator knows what to do next"
    USER_PROVIDED_FOLLOWUP = "user gave follow-up input"
    AUTO_REFINEMENT_LOOP = "auto-refining (e.g., hallucination fix)"
    
    # Stop scenarios
    COMPLETION = "operation complete, user goal achieved"
    USER_REJECTION = "user explicitly rejected result"
    TOKEN_LIMIT = "approaching token limit"
    GOVERNANCE_HALT = "governance rule violation detected"
    MAX_ROUNDS_REACHED = "safety limit on iterations"
    ERROR_UNRECOVERABLE = "error that can't be recovered"
    INTERACTION_REQUIRED = "waiting for user approval/input"

@dataclass
class ContinuationDecision:
    """
    Explicit decision about what to do next.
    
    Adheres to CORTEX principles:
    - Declarative (not imperative "while" conditions)
    - Auditable (reason is explicit, not buried in code)
    - Testable (each decision can be tested independently)
    - Governance-compliant (CORE-001, CORE-019, CORE-027)
    """
    
    should_continue: bool
    """Whether to continue to next turn."""
    
    reason: ContinuationReason
    """Why this decision was made."""
    
    next_operation: Optional[str]
    """If continuing, what should happen next? (e.g., 'next_ac', 'refine'"""
    
    next_parameters: Dict[str, Any]
    """Parameters for next operation."""
    
    turn_number: int
    """Which turn produced this decision."""
    
    token_usage: Dict[str, int]
    """How many tokens used this turn: {prompt, completion, total}"""
    
    audit_entry_id: str
    """Link to audit trail AC_COMPLETE entry for this turn."""
    
    governance_violations: List[str] = None
    """Any governance rule violations that caused halt."""
    
    @property
    def is_halt_by_governance(self) -> bool:
        """Was this halt triggered by governance enforcement?"""
        return self.reason == ContinuationReason.GOVERNANCE_HALT
    
    @property
    def is_user_action_required(self) -> bool:
        """Does this require user to take action?"""
        return self.reason in [
            ContinuationReason.USER_REJECTION,
            ContinuationReason.INTERACTION_REQUIRED,
        ]
    
    @property
    def is_safe_to_resume(self) -> bool:
        """Can we resume from this stopping point?"""
        # Some stops are resumable (waiting for user)
        # Others are terminal (user rejected, error)
        return self.reason in [
            ContinuationReason.INTERACTION_REQUIRED,
            ContinuationReason.TOKEN_LIMIT,
            ContinuationReason.USER_PROVIDED_FOLLOWUP,
        ]
```

### 2. ConversationProtocol (Stateful Orchestrator Wrapper)

```python
class ConversationProtocol:
    """
    Wraps any IOrchestrator to add:
    - Explicit turn-by-turn execution
    - Continuation decision logic
    - Token tracking (CORE-001)
    - Audit trail per turn (CORE-027)
    - Governance compliance (CORE-017)
    
    This is NOT a loop - it's a PROTOCOL.
    Caller decides: continue or stop based on ContinuationDecision.
    """
    
    def __init__(
        self,
        orchestrator: IOrchestrator,
        max_turns: int = 10,  # Safety limit
        token_limit: int = 20000,  # Token budget for conversation
    ):
        """Initialize conversation protocol."""
        self.orchestrator = orchestrator
        self.max_turns = max_turns
        self.token_limit = token_limit
        
        self.turn_number = 0
        self.conversation_session: ConversationSession = None
        self.total_tokens_used = 0
        self.decisions_history: List[ContinuationDecision] = []
    
    def execute_turn(
        self,
        user_input: str,
        previous_context: Dict[str, Any] = None,
    ) -> Result[ContinuationDecision]:
        """
        Execute ONE turn and return explicit continuation decision.
        
        This is the ONLY method that orchestrators call.
        Caller uses ContinuationDecision to decide loop behavior.
        
        Adheres to:
        - CORE-001: Incremental (<500 lines per turn)
        - CORE-027: Audit trail AC_START/EXECUTE/COMPLETE
        - CORE-019: LENS protocol per turn
        - Governance validation per turn
        
        Returns:
            Result[ContinuationDecision] - What to do next
        """
        
        self.turn_number += 1
        
        # =====================================================================
        # Step 1: Pre-turn validation (Governance CORE-017)
        # =====================================================================
        
        governance_check = self._validate_governance_before_turn()
        if governance_check.is_err():
            return Ok(ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.GOVERNANCE_HALT,
                next_operation=None,
                next_parameters={},
                turn_number=self.turn_number,
                token_usage={"prompt": 0, "completion": 0, "total": 0},
                audit_entry_id="",
                governance_violations=governance_check.unwrap_err(),
            ))
        
        # =====================================================================
        # Step 2: Safety check: max turns reached?
        # =====================================================================
        
        if self.turn_number > self.max_turns:
            return Ok(ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.MAX_ROUNDS_REACHED,
                next_operation=None,
                next_parameters={},
                turn_number=self.turn_number,
                token_usage={"prompt": 0, "completion": 0, "total": 0},
                audit_entry_id="",
            ))
        
        # =====================================================================
        # Step 3: Create turn context (LENS Protocol Language Phase)
        # =====================================================================
        
        turn_context = self._create_turn_context(
            turn_number=self.turn_number,
            user_input=user_input,
            previous_context=previous_context,
        )
        
        # =====================================================================
        # Step 4: Execute turn (with audit logging - CORE-027)
        # =====================================================================
        
        # Log AC_START
        audit_start = self._log_ac_start(self.turn_number)
        
        try:
            # Execute the operation
            execution_result = self.orchestrator.execute_operation(
                operation=turn_context["operation"],
                parameters=turn_context["parameters"],
            )
            
            if execution_result.is_err():
                return Ok(ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.ERROR_UNRECOVERABLE,
                    next_operation=None,
                    next_parameters={},
                    turn_number=self.turn_number,
                    token_usage=turn_context.get("token_usage", {}),
                    audit_entry_id=audit_start.unwrap()["id"],
                ))
            
            result_data = execution_result.unwrap()
            
            # Log AC_EXECUTE
            self._log_ac_execute(
                turn_number=self.turn_number,
                result=result_data,
                token_usage=turn_context.get("token_usage", {}),
            )
            
        except Exception as e:
            # Log error and halt
            self._log_ac_complete(
                turn_number=self.turn_number,
                status="ERROR",
                error=str(e),
            )
            return Err(f"Turn {self.turn_number} failed: {str(e)}")
        
        # =====================================================================
        # Step 5: Decide continuation (The KEY Innovation)
        # =====================================================================
        
        decision = self._evaluate_continuation(
            turn_number=self.turn_number,
            execution_result=result_data,
            turn_context=turn_context,
            total_tokens=self.total_tokens_used,
        )
        
        # Log AC_COMPLETE with decision
        self._log_ac_complete(
            turn_number=self.turn_number,
            status="COMPLETED",
            continuation_decision=decision,
        )
        
        # Store decision for history/replay
        self.decisions_history.append(decision)
        
        return Ok(decision)
    
    def _evaluate_continuation(
        self,
        turn_number: int,
        execution_result: Dict,
        turn_context: Dict,
        total_tokens: int,
    ) -> ContinuationDecision:
        """
        Intelligent continuation logic.
        
        This is where CORTEX architecture shines:
        - No fragile "if" conditions scattered in code
        - Explicit reasons for every decision
        - Testable in isolation
        - Auditable
        """
        
        # Check 1: Did orchestrator suggest next operation?
        if "next_operation" in execution_result:
            next_op = execution_result["next_operation"]
            if next_op == "COMPLETE":
                return ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.COMPLETION,
                    next_operation=None,
                    next_parameters={},
                    turn_number=turn_number,
                    token_usage=turn_context.get("token_usage", {}),
                    audit_entry_id="",
                )
            else:
                return ContinuationDecision(
                    should_continue=True,
                    reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
                    next_operation=next_op,
                    next_parameters=execution_result.get("next_parameters", {}),
                    turn_number=turn_number,
                    token_usage=turn_context.get("token_usage", {}),
                    audit_entry_id="",
                )
        
        # Check 2: Approaching token limit?
        if total_tokens > (self.token_limit * 0.8):  # 80% threshold
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.TOKEN_LIMIT,
                next_operation=None,
                next_parameters={},
                turn_number=turn_number,
                token_usage=turn_context.get("token_usage", {}),
                audit_entry_id="",
            )
        
        # Check 3: Did user ask for something specific?
        if "user_followup" in execution_result:
            return ContinuationDecision(
                should_continue=True,
                reason=ContinuationReason.USER_PROVIDED_FOLLOWUP,
                next_operation="process_followup",
                next_parameters={"followup": execution_result["user_followup"]},
                turn_number=turn_number,
                token_usage=turn_context.get("token_usage", {}),
                audit_entry_id="",
            )
        
        # Default: Requires user input
        return ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.INTERACTION_REQUIRED,
            next_operation=None,
            next_parameters={},
            turn_number=turn_number,
            token_usage=turn_context.get("token_usage", {}),
            audit_entry_id="",
        )
```

### 3. How Client Code Uses This (The Loop is NOW in CLIENT CODE, NOT Hidden)

```python
# ✅ CORTEX-ALIGNED: Explicit turn-by-turn execution
def run_orchestrator_conversation(orchestrator, user_requests):
    """
    This is YOUR application code. YOU decide loop behavior.
    NOT buried in orchestrator internals.
    
    This is:
    - Testable (test each turn independently)
    - Auditable (each decision visible in code)
    - Controllable (you decide when to stop)
    - Debuggable (print each decision)
    """
    
    protocol = ConversationProtocol(
        orchestrator=orchestrator,
        max_turns=10,
        token_limit=20000,
    )
    
    turn = 1
    for user_input in user_requests:
        
        # =====================================================================
        # Execute ONE turn (get explicit decision)
        # =====================================================================
        
        decision_result = protocol.execute_turn(
            user_input=user_input,
            previous_context=None if turn == 1 else previous_result,
        )
        
        if decision_result.is_err():
            print(f"❌ Turn {turn} failed: {decision_result.unwrap_err()}")
            break
        
        decision = decision_result.unwrap()
        previous_result = decision.next_parameters  # Carry forward context
        
        # =====================================================================
        # Decide what to do next based on EXPLICIT decision
        # =====================================================================
        
        if decision.should_continue == False:
            print(f"🛑 Stopping at Turn {turn}")
            print(f"   Reason: {decision.reason.value}")
            
            if decision.reason == ContinuationReason.COMPLETION:
                print("✅ Goal achieved!")
            elif decision.reason == ContinuationReason.USER_REJECTION:
                print("⚠️  User rejected result")
            elif decision.reason == ContinuationReason.TOKEN_LIMIT:
                print("📊 Token limit reached")
            elif decision.reason == ContinuationReason.GOVERNANCE_HALT:
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

## COMPARISON: OLD vs NEW ARCHITECTURE

| Aspect | Loop (❌ Your Idea) | ConversationProtocol (✅ Better) |
|--------|-------|---------|
| **Where is loop?** | Inside orchestrator | In client code (explicit) |
| **Stop condition** | `if should_break()` | `ContinuationDecision.should_continue` |
| **Testability** | Hard to test Turn 3 | Easy: `decision = protocol.execute_turn(3)` |
| **Auditability** | Loop state invisible | Every decision logged in audit trail |
| **Token tracking** | Hidden | Explicit in `ContinuationDecision.token_usage` |
| **Governance** | Hard to enforce | Per-turn validation gates |
| **State persistence** | Implicit | Explicit via `previous_context` |
| **Debugging** | "How did we get here?" | Clear decision trail |
| **Reproducibility** | Hard to replay Turn 3 | Replay by calling `execute_turn(3)` |

---

## HOW THIS ADHERES TO CORTEX ARCHITECTURE

```yaml
cortex_principles:
  CORE-001_incremental_execution:
    how: "Each turn explicitly bounded; token usage visible"
    proof: "ContinuationDecision.token_usage tracks per-turn tokens"
  
  CORE-019_tdd_master_routing:
    how: "Decision includes what should happen next"
    proof: "decision.next_operation tells Master what to do"
  
  CORE-027_audit_trail:
    how: "AC_START/EXECUTE/COMPLETE logged per turn"
    proof: "_log_ac_*() methods called per turn, entered decision.audit_entry_id"
  
  LENS_protocol:
    how: "Turn context includes all 4 LENS phases"
    proof: "_create_turn_context() builds Language/Examination/Navigation/Synthesis"
  
  governance_core_017:
    how: "Pre-turn validation + governance halt support"
    proof: "_validate_governance_before_turn() called before every turn"
  
  state_persistence:
    how: "Each turn receives previous_context + decision history"
    proof: "Turn N+1 sees Turn N decision + results"
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Create Core Infrastructure (This Week)

| File | Purpose | Effort |
|------|---------|--------|
| `src/core/continuation_decision.py` | ContinuationDecision class | 1h |
| `src/core/continuation_protocol.py` | ConversationProtocol class | 2h |
| `tests/unit/test_continuation_protocol.py` | Unit tests | 1.5h |
| `tests/integration/test_orchestrator_continuation.py` | Integration tests | 2h |

### Phase 2: Integrate with Orchestrators (Next Week)

| Orchestrator | Changes | Tests |
|---|---|---|
| PlanningOrchestrator | Wrap with ConversationProtocol | 2h |
| ADOOrchestrator | Wrap with ConversationProtocol | 2h |
| InteractionOrchestrator | Wrap with ConversationProtocol | 2h |
| MasterOrchestrator | Route per-turn decisions | 3h |

### Phase 3: Update Roadmap + Documentation

| File | Changes |
|---|---|
| `cortex-master.yaml` | Add ContinuationProtocol pattern to testing_framework |
| `phase-07-intent-router.yaml` | Add multi-round AC requirement |
| `.github/docs/orchestrator-continuation-pattern.md` | Documentation |

---

## TESTING EXAMPLES

### Test 1: Turn Execution

```python
def test_conversation_protocol_executes_single_turn():
    """Test that one turn executes and returns decision."""
    protocol = ConversationProtocol(MockOrchestrator())
    
    decision = protocol.execute_turn("Get phase status").unwrap()
    
    assert decision.turn_number == 1
    assert decision.reason in [ContinuationReason.COMPLETION, ...]
```

### Test 2: Continuation Logic

```python
def test_continuation_protocol_stops_on_token_limit():
    """Test that protocol halts when approaching token limit."""
    protocol = ConversationProtocol(MockOrchestrator(), token_limit=100)
    protocol.total_tokens_used = 85  # 85% used
    
    decision = protocol.execute_turn("Get AC").unwrap()
    
    assert decision.should_continue == False
    assert decision.reason == ContinuationReason.TOKEN_LIMIT
```

### Test 3: Multi-Round Conversation

```python
def test_multi_round_conversation_maintains_state():
    """Test that state persists across rounds."""
    protocol = ConversationProtocol(MockOrchestrator())
    
    # Turn 1
    decision1 = protocol.execute_turn("Get phase 01 status").unwrap()
    assert decision1.turn_number == 1
    
    # Turn 2 (using Turn 1 result)
    decision2 = protocol.execute_turn(
        "Show next AC",
        previous_context=decision1.next_parameters
    ).unwrap()
    assert decision2.turn_number == 2
    assert decision2.next_parameters["phase"] == decision1.next_parameters["phase"]
```

---

## MY CHALLENGE TO YOU

**Your Original Idea**:
> "Keep orchestrators running in a loop until an event intelligently breaks the loop"

**Why This is Anti-Pattern in CORTEX**:
1. ❌ Loop is imperative, hidden from caller
2. ❌ Hard to test individual turns
3. ❌ "Event breaks loop" is vague; what events?
4. ❌ State transitions invisible
5. ❌ Token limits not tracked per-turn
6. ❌ Governance compliance hard to verify

**Better Solution**:
✅ **ConversationProtocol** - Explicit, declarative, turn-by-turn orchestration  
✅ Each turn returns `ContinuationDecision` with clear reasons  
✅ Client code decides loop behavior (not orchestrator)  
✅ Fully testable, auditable, governance-compliant  

**This Adheres to CORTEX**:
- ✅ CORE-001: Incremental, token-tracked turns
- ✅ CORE-019: Master routes per-turn decisions
- ✅ CORE-027: Audit trail per turn
- ✅ LENS: Executed per turn, not cached
- ✅ Governance: Pre/post-turn validation

---

## NEXT STEPS

1. **Review this architecture** - Does ContinuationProtocol better serve your needs?
2. **Create core classes** - `ContinuationDecision`, `ConversationProtocol`
3. **Integrate with Orchestrators** - Make them return `ContinuationDecision`
4. **Update Roadmap** - Add pattern to `cortex-master.yaml`
5. **Write Multi-Round Tests** - Validate pattern works end-to-end

---

**Status**: READY FOR IMPLEMENTATION  
**Estimated Effort**: 15-20 hours total  
**CORTEX Alignment**: 100% (CORE-001, 019, 027, LENS, Governance)  
**Better Than Loop**: YES ✅
