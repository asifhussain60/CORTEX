# ADR-005: Conversation Protocol (ContinuationDecision Pattern)

> Architecture Decision Record

**Status:** Accepted  
**Date:** 2026-01-18  
**Deciders:** CORTEX Architecture Team  
**Technical Story:** PHASE-16-ORCHESTRATOR-CONTINUATION

## Context

Orchestrators need explicit, testable control over when to continue or terminate execution. Traditional loop-based approaches make it difficult to test termination conditions and can lead to infinite loops or unclear exit paths.

## Decision

Implement the **ContinuationDecision Pattern** for all orchestrators, replacing implicit loops with explicit turn-by-turn decisions.

### Pattern Definition

```python
@dataclass
class ContinuationDecision:
    """Explicit decision about orchestrator continuation."""
    should_continue: bool
    reason: ContinuationReason
    next_operation: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ContinuationReason(Enum):
    """Terminal events that break the orchestration loop."""
    COMPLETION = "goal_achieved"
    USER_REJECTION = "user_rejected_result"
    TOKEN_LIMIT = "approaching_token_budget"
    GOVERNANCE_HALT = "rule_violation_detected"
    MAX_ROUNDS_REACHED = "safety_limit_exceeded"
    ERROR_UNRECOVERABLE = "fatal_error_occurred"
    INTERACTION_REQUIRED = "waiting_for_user_input"
    CONFIRMATION_REQUESTED = "complexity_gate_triggered"
```

### Implementation

```python
class BaseOrchestrator:
    async def execute_turn(self, context: TurnContext) -> ContinuationDecision:
        """Execute a single turn and return continuation decision."""
        try:
            result = await self._do_work(context)
            
            if result.is_complete:
                return ContinuationDecision(
                    should_continue=False,
                    reason=ContinuationReason.COMPLETION
                )
            
            return ContinuationDecision(
                should_continue=True,
                reason=None,
                next_operation=result.next_step
            )
        except GovernanceViolation:
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.GOVERNANCE_HALT
            )
```

### Benefits

| Aspect | Traditional Loop | ContinuationDecision |
|--------|-----------------|---------------------|
| Testability | Hard to test exit conditions | Each decision testable |
| Debugging | Implicit state | Explicit reason logged |
| Safety | Risk of infinite loop | MAX_ROUNDS guaranteed |
| Auditability | Loop iterations unclear | Each turn audited |

## Consequences

### Positive

- Every termination has explicit reason
- Easy to test specific termination paths
- Clear audit trail for each turn
- Safety limits enforced consistently
- Complexity gate integration natural

### Negative

- More verbose than simple loops
- Additional dataclass overhead
- Orchestrator implementations more complex

### Test Coverage

155 tests validate the pattern:

```python
def test_completion_terminates():
    decision = orchestrator.execute_turn(complete_context)
    assert not decision.should_continue
    assert decision.reason == ContinuationReason.COMPLETION

def test_max_rounds_safety():
    for _ in range(MAX_ROUNDS + 1):
        decision = orchestrator.execute_turn(context)
    assert decision.reason == ContinuationReason.MAX_ROUNDS_REACHED
```

## Alternatives Considered

1. **While loops with break** - Rejected: Implicit exit conditions
2. **Generator/yield** - Rejected: Less explicit than dataclass
3. **State machine** - Considered: ContinuationDecision is simpler state machine

## Related

- [Orchestration Engine](../3-orchestration-engine.md)
- [Orchestration Flow Diagram](../_diagrams/orchestration-flow.mmd)
- `cortex/core/orchestrator/conversation_protocol.py`
