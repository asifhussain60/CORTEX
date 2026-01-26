# MasterGateway Architecture Design

**Document:** AC-PERMANENT-FIX-010 Phase 1  
**Author:** CORTEX Orchestrator  
**Date:** 2026-01-26  
**Status:** Design Phase (Phase 1)

---

## 1. Purpose

MasterGateway serves as the **single mandatory entry point** for all CORTEX operation execution, enforcing:

1. **All operations route through MasterGateway.execute()**
2. Specifications loaded and validated before execution
3. Governance validation before delegation
4. Structured decision making (JSON, never markdown)
5. Centralized audit trail and enforcement

---

## 2. Architecture Overview

### 2.1 Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Caller (API, CLI, etc.)                                     │
│ → MasterGateway.execute(operation_spec: Dict)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MasterGateway Layer                                         │
│  1. Validate spec format                                    │
│  2. Load applicable specifications                          │
│  3. Validate governance preconditions                       │
│  4. Determine target handler                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ SpecRegistry                                                │
│ - Load routing-rules.yaml                                   │
│ - Load orchestrator-dispatch.yaml                           │
│ - Load governance-gates.yaml                                │
│ - Return applicable specs (cached)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ GovernanceGate Validator                                    │
│ - Check pre-execution governance rules                      │
│ - Validate CORE rules compliance                            │
│ - Return violations as structured codes (JSON)              │
└────────────────────┬────────────────────────────────────────┘
                     │
              ┌──────┴──────┐
              │             │
         ✅ PASS       ❌ FAIL
              │             │
              ▼             ▼
    ┌────────────────┐  ┌──────────────────┐
    │ Delegate to    │  │ Return Error     │
    │ MasterOrch     │  │ (Violation Codes)│
    │ .execute_op()  │  │ JSON format      │
    └────────┬───────┘  └──────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ MasterOrchestrator │
    │ .execute_operation()
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ StructuredDecision │
    │ Formatter          │
    │ .to_dict()         │ (JSON)
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Return Result      │
    │ (JSON/Dict, not MD)│
    └────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | CORE Rule |
|-----------|-----------------|-----------|
| **MasterGateway** | Single entry point, orchestration | CORE-040 |
| **GatewayValidator** | Spec format validation | CORE-040 |
| **SpecRegistry** | Load, cache, and serve specs | CORE-040 |
| **GovernanceGate** | Pre-execution validation | CORE-040 |
| **StructuredDecisionFormatter** | Format output as JSON | CORE-040 |
| **GatewayEnforcer** | Runtime enforcement (Phase 3) | CORE-040 |

---

## 3. Key Classes

### 3.1 MasterGateway

**Purpose:** Single entry point for operation execution

**Signature:**
```python
class MasterGateway:
    """Single entry point for all operation execution."""
    
    def execute(
        self,
        operation_spec: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute operation via specifications."""
```

**Responsibilities:**
- Accept operation specification (Dict/JSON)
- Validate spec format against schema
- Load applicable specs from registry
- Delegate to MasterOrchestrator
- Format response as JSON (never markdown)
- Log all decisions to audit trail

**Error Handling:**
- Raise `SpecValidationError` on invalid spec
- Raise `GovernanceViolationError` on governance failure
- Return structured error dict (JSON) with violation codes

### 3.2 GatewayValidator

**Purpose:** Validate operation specifications before execution

**Signature:**
```python
class GatewayValidator:
    """Validates operation specs before execution."""
    
    def validate_spec_format(self, spec: Dict) -> Result[None]:
        """Check spec against schema."""
        
    def validate_governance_preconditions(self, spec: Dict) -> Result[None]:
        """Check governance rules allow execution."""
        
    def validate_orchestrator_availability(self, handler: str) -> Result[None]:
        """Check handler orchestrator is available."""
```

**Error Codes (Structured, not English):**
- `GOVE_001`: Spec format invalid
- `GOVE_002`: Governance violation
- `GOVE_003`: Orchestrator not found

### 3.3 SpecRegistry

**Purpose:** Load, cache, and serve execution specifications

**Responsibilities:**
- Load YAML specs at startup (one-time cost)
- Cache in memory (LRU cache)
- Validate specs on load
- Return applicable specs for operation
- Thread-safe access

**Performance Targets:**
- Spec lookup < 5ms
- Cache hit rate > 95%
- Memory overhead < 10MB

### 3.4 StructuredDecisionFormatter

**Purpose:** Convert various decision types to JSON format

**Signature:**
```python
class StructuredDecisionFormatter:
    """Formats execution decisions as structured JSON."""
    
    @staticmethod
    def format_approval_decision(
        intent_reflection: IntentReflection
    ) -> Dict[str, Any]:
        """Convert to JSON dict (REMOVES markdown)."""
        
    @staticmethod
    def format_routing_decision(
        decision: RoutingDecision
    ) -> Dict[str, Any]:
        """Format routing decision as JSON."""
```

**Guarantees:**
- NEVER includes markdown in output
- ALWAYS returns pure JSON-serializable dict
- Preserves all decision information

### 3.5 GatewayEnforcer

**Purpose:** Runtime enforcement that all operations route through gateway

**Signature:**
```python
class GatewayEnforcer:
    """Enforces all operations route through MasterGateway."""
    
    @staticmethod
    def check_execution_path(stack_trace: List) -> Result[None]:
        """Verify call stack includes MasterGateway.execute()."""
```

**Enforcement Strategy (Phase 3):**
- Check call stack for `MasterGateway.execute()`
- Log direct orchestrator calls to audit trail
- Configurable: warn vs. block
- Helps identify code needing migration

---

## 4. Integration Points

### 4.1 With MasterOrchestrator

- MasterGateway calls `MasterOrchestrator.execute_operation()`
- MasterOrchestrator behavior unchanged (backward compatible)
- Optional gateway hook: `if ENFORCE_GATEWAY_MODE`

### 4.2 With SpecRegistry

- MasterGateway queries SpecRegistry for applicable specs
- SpecRegistry returns cached specifications
- Validation happens before delegation

### 4.3 With GovernanceRegistry

- MasterGateway calls governance validation before execution
- GovernanceRegistry returns structured violation codes
- Violations returned as JSON dict (not English text)

### 4.4 With Audit Trail

- All gateway decisions logged to audit trail
- Log entries include: timestamp, spec, decision, result
- Enables traceability and debugging

---

## 5. Specification Format

### 5.1 Operation Specification (Input)

```python
operation_spec = {
    "operation": "implement_feature",      # Operation name
    "intent": "IMPLEMENT",                 # Intent type
    "context": {                           # Operation context
        "feature_name": "audit logging",
        "requirements": {...}
    },
    "governance_context": {                # Governance parameters
        "enforce_tdd": True,
        "min_coverage": 80
    }
}
```

### 5.2 Result Format (Output)

```python
result = {
    "success": True,                       # Operation success
    "operation": "implement_feature",      # Echo back
    "handler": "TDDOrchestrator",          # Used orchestrator
    "execution_time_ms": 2500,             # Duration
    "violations": [],                      # Governance violations (codes)
    "output": {...},                       # Operation output
    "audit_entry_id": "uuid"               # Audit trail reference
}
```

### 5.3 Error Format (Output)

```python
error_result = {
    "success": False,
    "error_code": "GOVE_002",              # Structured code (not English)
    "error_message": "governance_violation",
    "violations": [
        {
            "code": "GOVE_002",
            "rule": "CORE-008",            # Which CORE rule
            "details": {                   # Structured details
                "required": "tests",
                "found": "0"
            }
        }
    ]
}
```

---

## 6. Deployment Strategy

### Phase 1: Foundation (Week 1)
- ✅ Create specs and schema
- ✅ Implement MasterGateway (optional mode)
- ✅ No production changes yet

### Phase 2: Refactoring (Week 2-3)
- ✅ Update code to use specs
- ✅ Make gateway optional hook
- ✅ Test equivalence (old vs. new)

### Phase 3: Enforcement (Week 4)
- ✅ Make gateway mandatory
- ✅ CI/CD blocks violations
- ✅ Runtime enforcement active

---

## 7. CORE Rules Applied

| Rule | Requirement |
|------|-------------|
| **CORE-008** | TDD: Tests written before implementation |
| **CORE-011** | Type hints mandatory on all functions |
| **CORE-012** | Google-style docstrings |
| **CORE-026** | Git checkpoints at phase boundaries |
| **CORE-027** | Audit trail for all decisions |
| **CORE-030** | Implementation Truth: Code-verified |
| **CORE-040** | Execution Specification Mandate |

---

## 8. Success Criteria

- [ ] MasterGateway fully implemented
- [ ] GatewayValidator comprehensive coverage
- [ ] SpecRegistry loads and caches specs
- [ ] StructuredDecisionFormatter JSON-only output
- [ ] All decisions logged to audit trail
- [ ] 6,900+ tests still passing
- [ ] Spec lookup latency < 5ms
- [ ] Zero markdown in execution paths

---

## 9. Testing Strategy

See `test-test-strategy.md` for comprehensive testing plan including:
- Unit tests for each component
- Integration tests for gateway flow
- Equivalence tests (old vs. new)
- Performance benchmarks
- Governance compliance tests

---

## 10. References

- **CORE Rules:** `cortex_brain/tier0/governance/`
- **Specs:** `cortex/execution/specs/`
- **Tests:** `tests/unit/cortex/execution/`
- **Integration Tests:** `tests/integration/test-exec-specs.py`

---

**Document Status:** DESIGN PHASE  
**Next Phase:** Phase 2 - Specification Implementation  
**Target Completion:** 2026-02-09
