# Orchestrator Base Protocol

**Version:** 1.0  
**Status:** ACTIVE  
**Governance:** ARCH-012, CORE-029, AC-PERMANENT-FIX-006

---

## 🎯 Overview

**OrchestratorBaseProtocol** is the mandatory base class for ALL CORTEX orchestrators. It enforces a consistent 5-phase execution pattern that ensures:

- **Intelligence** — LENS synthesis provides deep context
- **Security** — Threat assessment blocks dangerous operations
- **Quality** — Challenge system detects suboptimal approaches
- **Confidence** — DoR gate validates intent clarity
- **Auditability** — Full protocol execution logged

---

## 🏗️ Architecture

### 5-Phase Execution Protocol

```
┌─────────────────────────────────────────────────────────┐
│                    USER REQUEST                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: LENS Context Building                         │
│ ├─ Language: Parse natural language                    │
│ ├─ Examination: Analyze code/docs/tests                │
│ ├─ Navigation: Explore codebase paths                  │
│ └─ Synthesis: Build unified understanding              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Security Threat Assessment ⚠️ HARD GATE       │
│ ├─ Analyze code for vulnerabilities                    │
│ ├─ Detect CRITICAL/HIGH threats                        │
│ └─ BLOCK execution if threats found                    │
└─────────────────┬───────────────────────────────────────┘
                  ↓ [Security passed or no code context]
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Challenge Generation                          │
│ ├─ Compare user approach vs CORTEX knowledge           │
│ ├─ Generate challenges when better solution exists     │
│ ├─ HARD GATE: Security/harmful actions → BLOCK         │
│ ├─ SOFT GATE: Architectural issues → SUGGEST           │
│ └─ CONTEXT GATE: Missing info → REQUEST                │
└─────────────────┬───────────────────────────────────────┘
                  ↓ [No hard gate challenge]
┌─────────────────────────────────────────────────────────┐
│ PHASE 4: DoR Confidence Gate ⚠️ THRESHOLD GATE         │
│ ├─ Classify intent (IMPLEMENT, FIX, etc.)              │
│ ├─ Calculate DoR confidence (0-100%)                   │
│ └─ BLOCK if confidence <60%                            │
└─────────────────┬───────────────────────────────────────┘
                  ↓ [DoR ≥60%]
┌─────────────────────────────────────────────────────────┐
│ PHASE 5: Domain Execution                              │
│ ├─ TDDOrchestrator: RED → GREEN → REFACTOR             │
│ ├─ RefactoringOrchestrator: Analyze → Plan → Execute   │
│ ├─ PlanningOrchestrator: Estimate → Plan → Schedule    │
│ └─ (Subclass-specific implementation)                  │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│                    SUCCESS / ERROR                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🚪 Gate Types

### HARD GATE (Blocks Execution)
- **Security threats** — CRITICAL/HIGH vulnerabilities
- **Harmful actions** — Destructive operations
- **Challenge disagreements** — When CORTEX strongly disagrees

### SOFT GATE (Suggests but Allows)
- **Architectural violations** — SRP, SOLID issues
- **Better solutions** — More efficient approaches
- **Redundant work** — Feature already exists

### THRESHOLD GATE (Confidence-Based)
- **DoR Confidence <60%** — Request unclear, needs clarification
- **DoR Confidence ≥60%** — Request clear, proceed to execution

---

## 💻 Implementation

### Creating a New Orchestrator

```python
from cortex.orchestrators.core.orchestrator_base_protocol import OrchestratorBaseProtocol
from cortex.core.result import Result, Ok, Err
from typing import Dict, Any, Optional

class MyOrchestrator(OrchestratorBaseProtocol):
    """
    Custom orchestrator with mandatory protocol enforcement.
    
    ARCH-012: Inherits LENS → Security → Challenge → DoR
    """
    
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result[Any]:
        """
        Implement domain-specific orchestration logic.
        
        This method is called AFTER all protocol phases pass.
        
        Args:
            user_request: Original user request text
            lens_context: LENS synthesis result (may be None if LENS unavailable)
            context: Request context with additional data
        
        Returns:
            Result[Any]: Success with output or Error with reason
        """
        # Your orchestration logic here
        try:
            # Example: Plan → Execute → Validate workflow
            plan = self._create_plan(user_request, lens_context)
            execution_result = self._execute_plan(plan, context)
            validation = self._validate_result(execution_result)
            
            return Ok({
                "plan": plan,
                "execution": execution_result,
                "validation": validation,
            })
        
        except Exception as e:
            return Err(f"Orchestration failed: {e}")
```

### Using the Orchestrator

```python
# Instantiate orchestrator
orchestrator = MyOrchestrator()

# Execute with protocol enforcement
result = orchestrator.execute_with_protocol(
    user_request="Implement authentication module",
    context={
        "target_file": "auth.py",
        "domain": "security",
    }
)

# Handle result
if result.is_ok():
    output = result.unwrap()
    print(f"Success: {output}")
else:
    error = result.unwrap_err()
    print(f"Error: {error}")
```

### Handling Protocol Responses

```python
result = orchestrator.execute_with_protocol(
    user_request="Delete production database",
    context={}
)

if result.is_ok():
    output = result.unwrap()
    
    # Check for challenge
    if output.get("type") == "challenge":
        challenge = output["challenge"]
        
        if output.get("blocked"):
            # HARD GATE: User must choose alternative
            print(f"BLOCKED: {challenge['reasoning']}")
            print(f"Alternative: {challenge['recommended_alternative']}")
            print("Options:")
            for i, option in enumerate(challenge.get("options", []), 1):
                print(f"  {i}. {option}")
        else:
            # SOFT GATE: Suggestion but can proceed
            print(f"Suggestion: {challenge['reasoning']}")
            # Continue execution...
    else:
        # Normal success response
        print(f"Result: {output}")
else:
    error = result.unwrap_err()
    
    # Check error type
    if "SECURITY BLOCK" in str(error):
        print(f"Security threat detected: {error}")
    elif "DoR NOT MET" in str(error):
        print(f"Request unclear: {error}")
    else:
        print(f"Execution error: {error}")
```

---

## 🔧 Protocol Components

### 1. LENSOrchestrator
**Purpose:** Build deep context via Language→Examination→Navigation→Synthesis

**Output:**
```python
{
    "language": "User wants to implement authentication",
    "examination": {
        "files": ["auth.py", "users.py"],
        "dependencies": ["flask", "bcrypt"],
    },
    "navigation": ["/cortex/auth/", "/cortex/models/"],
    "synthesis": "Auth module partially exists, needs completion",
    "confidence": 0.85
}
```

### 2. SecurityThreatAnalyzer
**Purpose:** Detect security vulnerabilities in code context

**Hard Gate Conditions:**
- CRITICAL severity threats (SQL injection, command execution)
- HIGH severity threats (XSS, path traversal)

**Output:**
```python
{
    "has_threats": True,
    "block_execution": True,
    "threat_summary": "CRITICAL: Command injection via os.system()",
    "threats": [...]
}
```

### 3. ChallengeEngine
**Purpose:** Generate intelligent challenges when CORTEX disagrees

**Gate Types:**
- **HARD:** Security, harmful actions → blocks
- **SOFT:** Better solutions, architecture → suggests
- **CONTEXT:** Missing info → requests clarification

**Output:**
```python
{
    "has_disagreement": True,
    "disagreement_type": "better_solution",
    "recommended_alternative": "Use OAuth library instead of custom auth",
    "reasoning": "Don't reinvent authentication (security risk + maintenance burden)",
    "gate_type": "soft",
    "block_execution": False
}
```

### 4. DoRApprovalGate
**Purpose:** Validate intent clarity and readiness

**Threshold:** 60% confidence minimum

**Output:**
```python
{
    "dor_confidence": 0.75,
    "intent_type": "IMPLEMENT",
    "target_handler": "TDDOrchestrator",
    "key_entities": ["auth.py", "User model"],
    "governance_rules": ["CORE-008", "CORE-011", "CORE-012"]
}
```

---

## ⚙️ Configuration

### Component Availability

Protocol gracefully handles missing components:

```python
orchestrator = MyOrchestrator()
status = orchestrator.get_protocol_status()

# Check component availability
print(status["components"])
# {
#     "lens": True,
#     "challenge": True,
#     "dor_gate": True,
#     "security": True
# }
```

### Degraded Mode Operation

If components unavailable:
- **LENS missing:** Proceeds without context synthesis
- **Challenge missing:** Proceeds without disagreement detection
- **DoR missing:** Proceeds without confidence gate
- **Security missing:** Proceeds without threat assessment (non-code)

**Note:** Protocol **attempts** all phases but continues if components fail.

---

## 📊 Governance

| Rule | Requirement |
|------|-------------|
| **ARCH-012** | All orchestrators MUST inherit OrchestratorBaseProtocol |
| **CORE-029** | LENS + Challenge automatic on EVERY turn (cannot be disabled) |
| **AC-PERMANENT-FIX-006** | Challenge system mandatory (enable_challenges forced True) |
| **CORE-008** | TDD (tests in tests/unit/orchestrators/test_orchestrator_base_protocol.py) |
| **CORE-011** | Type hints 100% |
| **CORE-012** | Google-style docstrings |
| **CORE-027** | Audit trail logging |

---

## 🧪 Testing

### Test Coverage

Run full test suite:

```bash
pytest tests/unit/orchestrators/test_orchestrator_base_protocol.py -v
```

**Coverage:**
- Protocol initialization (3 tests)
- LENS context building (2 tests)
- Security threat assessment (3 tests)
- Challenge generation (3 tests)
- DoR confidence gate (2 tests)
- Domain execution (2 tests)
- End-to-end protocol (2 tests)
- Governance compliance (2 tests)

**Total:** 19 tests, 100% passing

---

## 🔗 Related Documentation

- [LENS Protocol](../05-lens-protocol/01-overview.md)
- [Challenge Engine](../02-orchestrators/06-challenge-engine.md)
- [DoR Approval Gate](../02-orchestrators/07-dor-approval-gate.md)
- [Security Threat Analyzer](../12-infrastructure/security-threat-analyzer.md)
- [TDD Orchestrator](../02-orchestrators/01-tdd-orchestrator.md)

---

## 📝 Examples

### Example 1: Simple Implementation Request

```python
orchestrator = TDDOrchestrator()

result = orchestrator.execute_with_protocol(
    user_request="Implement user login functionality in auth.py",
    context={"domain": "authentication"}
)

# Phase 1: LENS builds context (finds existing auth code)
# Phase 2: Security passes (no code context)
# Phase 3: No challenge (straightforward request)
# Phase 4: DoR confidence 85% (clear intent)
# Phase 5: TDD workflow executes (RED → GREEN → REFACTOR)

assert result.is_ok()
output = result.unwrap()
assert output["tdd_phase"] == "RED"
```

### Example 2: Security Block

```python
orchestrator = TDDOrchestrator()

result = orchestrator.execute_with_protocol(
    user_request="Implement admin panel",
    context={"code": "exec(request.POST['cmd'])"}
)

# Phase 1: LENS builds context
# Phase 2: Security detects CRITICAL threat → BLOCKS
# Execution stops

assert result.is_err()
assert "SECURITY BLOCK" in str(result.unwrap_err())
```

### Example 3: Challenge Hard Gate

```python
orchestrator = PlanningOrchestrator()

result = orchestrator.execute_with_protocol(
    user_request="Delete all user data",
    context={}
)

# Phase 1: LENS builds context
# Phase 2: Security passes (no code)
# Phase 3: Challenge detects harmful action → HARD GATE
# Execution stops, requires user choice

assert result.is_ok()
output = result.unwrap()
assert output["type"] == "challenge"
assert output["blocked"] is True
assert "harmful" in output["challenge"]["disagreement_type"]
```

### Example 4: DoR Confidence Block

```python
orchestrator = RefactoringOrchestrator()

result = orchestrator.execute_with_protocol(
    user_request="Make it better",  # Vague request
    context={}
)

# Phase 1: LENS builds minimal context
# Phase 2: Security passes
# Phase 3: Challenge passes (no disagreement)
# Phase 4: DoR confidence 35% (<60%) → BLOCKS
# Execution stops, needs clarification

assert result.is_err()
assert "DoR NOT MET" in str(result.unwrap_err())
assert "35%" in str(result.unwrap_err())
```

---

## 🚀 Migration Guide

### Refactoring Existing Orchestrators

**Before (No Protocol):**

```python
class MyOrchestrator:
    def execute(self, request: str) -> Dict[str, Any]:
        # Direct execution, no gates
        return self.do_work(request)
```

**After (With Protocol):**

```python
class MyOrchestrator(OrchestratorBaseProtocol):
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result[Any]:
        # Same work, but protected by protocol
        result = self.do_work(user_request)
        return Ok(result)
```

**Benefits:**
- ✅ Automatic LENS context
- ✅ Security threat assessment
- ✅ Challenge generation
- ✅ DoR confidence validation
- ✅ Audit trail logging

---

**Last Updated:** 2026-01-31  
**Author:** Asif Hussain  
**AC-ID:** ARCH-012
