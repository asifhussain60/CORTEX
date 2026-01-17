# OC-005-01: Explicit Context Carryover Framework

**Date**: January 16, 2026  
**Status**: PLANNED (Added to PHASE-16)  
**AC-ID**: OC-005-01  
**Estimated Hours**: 5  
**Relates to**: Conversation Protocol Research, AI Context Management

---

## Problem Statement

When implementing **multi-turn orchestrator conversations** using AI agents, we discovered a critical limitation:

> **AI Context is ⚠️ CONDITIONAL across conversation turns**

### Implications

| Aspect | Impact |
|--------|--------|
| **Automatic Context Carryover** | NOT guaranteed across turns; token window limits may cause loss |
| **Implicit Assumptions** | "Turn N+1 will have Turn N's context" → fragile, causes bugs |
| **Context Recovery** | No standard mechanism for re-acquiring lost context |
| **Auditability** | Context assumptions not logged; hard to debug |

### Examples of Failures Without Explicit Management

```
Turn 1: "Get status of PHASE-01"
  → Response: "PHASE-01 has 36 ACs, all complete"
  
Turn 2: "What's the next AC?"
  ❌ PROBLEM: Model may not remember we were talking about PHASE-01
  ❌ Context window refilled with other data
  ❌ No way to recover prior context automatically
```

---

## CORTEX Solution: ConversationSession

### Design Principles

1. **Explicit Over Implicit** — Context is never assumed; always provided
2. **Deterministic Recovery** — If context lost, restore from governance.db
3. **Auditable State** — Every context change logged with AC_START/EXECUTE/COMPLETE
4. **Window-Aware** — Recognizes context window limits; summarizes when needed

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ ConversationSession (Explicit State Container)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ conversation_id: UUID (immutable, unique per multi-turn flow)  │
│ turn_number: int (1, 2, 3, ...)                               │
│                                                                  │
│ state_dict: {                                                  │
│   turn_1: {input, output, decisions, context_available}       │
│   turn_2: {input, output, decisions, context_available}       │
│   turn_N: {...}                                               │
│ }                                                              │
│                                                                  │
│ hash_chain: [hash_1, hash_2, hash_N]  (integrity checking)    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                        │
│  • get_full_context() → dict  (all turns)                     │
│  • get_context_summary() → str  (condensed for window limits)  │
│  • add_turn(turn_num, input, output, decision)               │
│  • verify_integrity() → bool  (check hash chain)             │
│  • summarize_old_turns(keep_recent_n=3) → summary_str        │
│  • restore_from_audit_logs(conversation_id) → Session        │
└─────────────────────────────────────────────────────────────────┘
```

### Per-Turn Execution Pattern

#### BEFORE (Implicit, Fragile)

```python
# ❌ ANTI-PATTERN: Hidden context assumption
while turn <= max_turns:
    result = orchestrator.execute(user_input)  # "Hope" prior context is somehow there
    if should_stop(result):
        break
    turn += 1
```

**Problems:**
- Implicit assumption that context carries over
- If context lost, no recovery mechanism
- Non-deterministic behavior
- Audit trail doesn't show context state

#### AFTER (Explicit, Robust)

```python
# ✅ CORTEX PATTERN: Explicit context management
session = ConversationSession.restore_if_exists(conversation_id)

while session.turn_number <= max_turns:
    # Get FULL context from prior turns (explicit, not implicit)
    full_context = session.get_full_context()
    
    # If context too large, get summary instead (window-aware)
    if len(full_context) > context_window_limit:
        context = session.get_context_summary()
    else:
        context = full_context
    
    # Execute turn with COMPLETE context provided
    decision = orchestrator.execute_turn(user_input, context)
    
    # Record turn and verify integrity
    session.add_turn(
        turn_number=session.turn_number,
        input=user_input,
        output=decision,
        context_provided=context
    )
    session.verify_integrity()
    session.turn_number += 1
    
    if not decision.should_continue:
        break

# Persist session before exit
session.save()
```

**Benefits:**
- ✅ Context is **explicit** (not assumed)
- ✅ Deterministic (same inputs → same context every time)
- ✅ Recoverable (restore from governance.db if needed)
- ✅ Auditable (every context decision logged)
- ✅ Window-aware (summarizes large contexts)
- ✅ Integrity-checked (hash chain ensures no tampering)

---

## Implementation Strategy

### Phase 1: Core Infrastructure (2 hours)

```python
# src/core/orchestrator/conversation_session.py

@dataclass(frozen=True)
class TurnRecord:
    turn_number: int
    timestamp: datetime
    input: str
    output: ContinuationDecision
    context_provided: dict
    hash: str  # SHA-256(prior_hash + this_turn_data)

class ConversationSession:
    def __init__(self, conversation_id: str, orchestrator_type: str):
        self.conversation_id = conversation_id
        self.orchestrator_type = orchestrator_type
        self.turn_records: List[TurnRecord] = []
        self.hash_chain: List[str] = []
    
    def get_full_context(self) -> dict:
        """Return complete state from all prior turns."""
        return {
            "turns": [
                {
                    "number": r.turn_number,
                    "input": r.input,
                    "output": r.output.to_dict(),
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.turn_records
            ],
            "conversation_id": self.conversation_id,
            "current_turn": len(self.turn_records) + 1,
        }
    
    def get_context_summary(self, keep_recent_n: int = 3) -> str:
        """Return condensed context for window-limited scenarios."""
        recent = self.turn_records[-keep_recent_n:]
        summaries = []
        for r in recent:
            summaries.append(
                f"Turn {r.turn_number}: {r.input} → {r.output.reason}"
            )
        
        return "\n".join(summaries)
    
    def add_turn(self, turn_number: int, input_text: str,
                output: ContinuationDecision, context_provided: dict):
        """Record a turn and update hash chain."""
        record = TurnRecord(
            turn_number=turn_number,
            timestamp=datetime.now(),
            input=input_text,
            output=output,
            context_provided=context_provided,
            hash=self._compute_hash(turn_number)
        )
        self.turn_records.append(record)
        self.hash_chain.append(record.hash)
    
    def verify_integrity(self) -> bool:
        """Verify hash chain (detects tampering)."""
        for i, record in enumerate(self.turn_records):
            computed = self._compute_hash(record.turn_number)
            if computed != record.hash:
                return False  # Tampering detected
        return True
    
    @staticmethod
    def restore_from_audit_logs(conversation_id: str) -> "ConversationSession":
        """Restore from governance.db audit trail (deterministic recovery)."""
        # Query: SELECT * FROM audit_log WHERE conversation_id = ?
        # Reconstruct from AC_START, AC_EXECUTE, AC_COMPLETE entries
        pass
```

### Phase 2: Protocol Integration (2 hours)

Update `ConversationProtocol.execute_turn()` to use session:

```python
def execute_turn(self, user_input: str, conversation_id: str) -> Result[ContinuationDecision]:
    # Restore session (creates new if doesn't exist)
    session = ConversationSession.restore_if_exists(conversation_id)
    
    # Get explicit context from prior turns
    context = session.get_full_context()
    
    # Check governance before turn
    result = self._validate_governance_before_turn()
    if result.is_err:
        return Result.err(result.error)
    
    # Log AC_START
    self._log_ac_start()
    
    # Execute turn (with FULL context provided explicitly)
    decision = self.orchestrator.execute(user_input, context)
    
    # Record turn
    session.add_turn(
        turn_number=self.turn_number,
        input_text=user_input,
        output=decision,
        context_provided=context
    )
    
    # Verify integrity
    if not session.verify_integrity():
        return Result.err("Context integrity violation detected")
    
    # Log AC_EXECUTE and AC_COMPLETE
    self._log_ac_execute()
    self._log_ac_complete()
    
    # Save session
    session.save()
    
    return Result.ok(decision)
```

### Phase 3: Testing (1 hour)

Test scenarios:

```python
# tests/integration/test_context_carryover_scenarios.py

def test_single_turn_context():
    """Turn 1: minimal context"""
    session = ConversationSession("conv-001", "PlanningOrchestrator")
    ctx = session.get_full_context()
    assert ctx["current_turn"] == 1
    assert len(ctx["turns"]) == 0

def test_five_turn_accumulation():
    """Turns 1-5: context accumulates"""
    session = ConversationSession("conv-002", "PlanningOrchestrator")
    for i in range(1, 6):
        decision = ContinuationDecision(
            should_continue=(i < 5),
            reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
            turn_number=i
        )
        session.add_turn(i, f"input-{i}", decision, {})
    
    ctx = session.get_full_context()
    assert ctx["current_turn"] == 6
    assert len(ctx["turns"]) == 5

def test_context_window_limit():
    """Summarization triggered when context too large"""
    session = ConversationSession("conv-003", "PlanningOrchestrator")
    # Add 100 turns...
    full = session.get_full_context()
    assert len(full) > 100000  # Too large
    
    summary = session.get_context_summary(keep_recent_n=3)
    assert len(summary) < 1000  # Summarized to ~3 turns

def test_context_recovery_from_audit_logs():
    """Lost context restored from governance.db"""
    # Session lost mid-conversation
    # Restore from audit logs
    restored = ConversationSession.restore_from_audit_logs("conv-004")
    assert restored is not None
    assert len(restored.turn_records) == 5  # Recovered 5 prior turns

def test_hash_chain_integrity():
    """Detect tampering in hash chain"""
    session = ConversationSession("conv-005", "PlanningOrchestrator")
    session.add_turn(1, "input-1", decision, {})
    
    # Tamper with hash
    session.hash_chain[0] = "invalid_hash"
    
    assert not session.verify_integrity()
```

---

## Governance Alignment

| CORTEX Rule | How OC-005-01 Fulfills It |
|-------------|--------------------------|
| **CORE-001** | Each turn executes <500 lines; context bounded per turn |
| **CORE-011** | Type hints on all session methods |
| **CORE-012** | Google-style docstrings on ConversationSession |
| **CORE-019** | Master orchestrator has full context for routing decisions |
| **CORE-027** | AC_START/EXECUTE/COMPLETE logged with context state |
| **AR-001-03** | Governance context immutable during session lifetime |

---

## Key Insights

### Why This Matters

From earlier research:

> "Does each round factor in the previous cumulated knowledge to respond intelligently without losing prior context?"
>
> **Answer**: ⚠️ **CONDITIONAL** — Only if files are in context window OR explicitly re-read

OC-005-01 makes this **EXPLICIT**:

- **Before**: Hope context carries over (fragile)
- **After**: Guarantee context by managing it explicitly (robust)

### Architectural Philosophy

**CORTEX Principle**: "Explicit > Implicit, Deterministic > Hopeful"

This AC embodies that principle for multi-turn conversations.

---

## Files to Create/Modify

### Create
- `src/core/orchestrator/conversation_session.py` (150 lines)
- `tests/unit/core/orchestrator/test_conversation_session.py` (250 lines)
- `tests/integration/test_context_carryover_scenarios.py` (200 lines)

### Modify
- `src/core/orchestrator/conversation_protocol.py` (add session integration)
- `src/orchestrators/master/master_orchestrator.py` (use session)

---

## Success Metrics

- ✅ ConversationSession tracks state across 5+ turns
- ✅ Context recovery from governance.db successful
- ✅ Hash chain integrity verified (detects tampering)
- ✅ 38 tests passing (22 unit + 16 integration)
- ✅ >95% code coverage for session classes
- ✅ All governance rules CORE-001, 011, 012, 019, 027 satisfied

---

## Timeline

- **Day 1**: Infrastructure + integration (4h)
- **Day 2**: Testing + documentation (1h)
- **Total**: 5 hours (fits in PHASE-16 schedule)

---

**Author**: Asif Hussain  
**Date**: January 16, 2026  
**Related**: PHASE-16-ORCHESTRATOR-CONTINUATION, ConversationProtocol Architecture
