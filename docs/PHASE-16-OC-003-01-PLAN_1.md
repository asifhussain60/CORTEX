# OC-003-01: Orchestrator Wrapping - Implementation Plan

## Objective
Wrap existing orchestrators (Planning, ADO, TDD) with ConversationProtocol to enable multi-turn, event-driven execution.

## Current State
- ✅ ContinuationDecision: Captures explicit halt/continue decisions
- ✅ ConversationProtocol: Single-turn executor with event integration
- ✅ Terminal Events: Break conditions fire events with listener veto
- ✅ EventRegistry: Listener management and veto mechanism

## Next: Orchestrator Wrapping Pattern

### Component 1: IOrchestrator Interface Enhancement
**File:** `src/core/orchestrator/orchestrator_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.orchestrator.continuation_decision import ContinuationDecision
from src.core.result import Result

class IOrchestrator(ABC):
    """Enhanced orchestrator interface for multi-turn support."""
    
    @abstractmethod
    def execute(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Single turn execution."""
        pass
    
    @abstractmethod
    def get_next_operation(self, result: Dict[str, Any]) -> Optional[str]:
        """Determine next operation from result."""
        pass
    
    @abstractmethod
    def get_domain_name(self) -> str:
        """Return domain/orchestrator name."""
        pass
```

### Component 2: Wrapped Orchestrators
**Pattern:** Each orchestrator wrapped with ConversationProtocol

**Locations:**
- `src/core/planning/planning_orchestrator.py` → wrap existing class
- `src/core/ado/ado_orchestrator.py` → wrap existing class
- `src/core/tdd/tdd_orchestrator.py` → wrap existing class

**Example Wrapper:**

```python
class WrappedPlanningOrchestrator:
    def __init__(self, planning_orchestrator: PlanningOrchestrator):
        self.orchestrator = planning_orchestrator
        self.protocol = ConversationProtocol(
            self.orchestrator,
            max_turns=5,
            token_limit=30000
        )
    
    def execute_with_continuation(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Result[List[ContinuationDecision]]:
        """Execute multi-turn workflow, yielding decisions."""
        decisions = []
        current_context = context
        
        while True:
            result = self.protocol.execute_turn(user_input, current_context)
            if result.is_err():
                return Err(result.unwrap_err())
            
            decision = result.unwrap()
            decisions.append(decision)
            
            if not decision.should_continue:
                break
            
            # For next turn, use next_operation if available
            user_input = decision.next_operation
            current_context = decision.next_parameters or current_context
        
        return Ok(decisions)
```

### Component 3: Test Suite Requirements

**Test Classes (estimated 24 tests):**

1. **TestPlanningOrchestratorWrapping** (6 tests)
   - Single turn execution
   - Multi-turn workflow
   - Event firing for planning phases
   - Continuation logic
   - Error handling
   - Token tracking

2. **TestADOOrchestratorWrapping** (6 tests)
   - Single turn execution
   - Multi-turn workflow
   - Event firing for ADO phases
   - Continuation logic
   - Error handling
   - Token tracking

3. **TestTDDOrchestratorWrapping** (6 tests)
   - Single turn execution
   - Multi-turn workflow
   - Event firing for TDD phases
   - Continuation logic
   - Error handling
   - Token tracking

4. **TestOrchestratorIntegration** (6 tests)
   - Cross-orchestrator next operations
   - Domain-specific routing
   - Multi-domain workflows
   - Consistency across domains
   - Shared context propagation
   - Event aggregation

### Component 4: Domain-Specific Next Operations

**Planning Domain:**
```python
# After planning completes, suggest:
next_operation = "begin_ado"  # or "refine_plan" if incomplete
```

**ADO Domain:**
```python
# After ADO completes, suggest:
next_operation = "begin_tdd"  # or "refine_architecture" if incomplete
```

**TDD Domain:**
```python
# After TDD completes, suggest:
next_operation = "complete"  # or "refactor" if needed
```

## Implementation Checklist

### Phase 1: Test Suite (2 hours)
- [ ] Create `test_wrapped_orchestrators.py` with 24 tests
- [ ] All tests RED (failing)

### Phase 2: Implementation (1.5 hours)
- [ ] Enhance IOrchestrator interface
- [ ] Wrap PlanningOrchestrator
- [ ] Wrap ADOOrchestrator
- [ ] Wrap TDDOrchestrator
- [ ] Implement get_next_operation() for each

### Phase 3: Verification (0.5 hours)
- [ ] All 24 tests GREEN
- [ ] No regressions in existing tests
- [ ] Git commit with clear message

## Files to Create/Modify

### Create
- `tests/unit/core/orchestrator/test_wrapped_orchestrators.py` (400+ lines)
- `src/core/orchestrator/orchestrator_interface.py` (50 lines, if new)

### Modify
- `src/core/planning/planning_orchestrator.py` (add wrapper)
- `src/core/ado/ado_orchestrator.py` (add wrapper)
- `src/core/tdd/tdd_orchestrator.py` (add wrapper)

## Success Criteria

✅ All 24 tests passing
✅ Each orchestrator supports 4+ turn workflows
✅ Events fire at appropriate break points
✅ Domain-specific next operations correct
✅ Token tracking accurate across turns
✅ Context propagated correctly between turns
✅ Zero regressions in orchestrator tests
✅ Git history clean and auditable

## Estimated Effort
- **Time:** 4 hours
- **Tests:** 24
- **Code Lines:** 300-400
- **Commits:** 1 major + intermediate checkpoints

## Governance Rules
✅ CORE-001: Incremental (<500 lines/turn)
✅ CORE-008: TDD (tests RED → GREEN)
✅ CORE-011: Type hints
✅ CORE-012: Docstrings
✅ CORE-027: Audit trail
✅ CORE-028: Naming conventions
