# CORTEX Tier 0: Instinct Layer

**Version:** 1.0  
**Status:** 🚧 IMMUTABLE GOVERNANCE  
**Storage:** YAML (human-readable)

---

## What is Tier 0?

Tier 0 is CORTEX's **cognitive DNA** - the immutable governance rules that define system behavior. These rules CANNOT be overridden and form the foundation of all CORTEX operations.

**Think of it as:** The hardcoded instincts that protect CORTEX integrity

---

## Core Principles

### The 22 Governance Rules

1. **Dual Interface Enforcement** - User vs internal separation
2. **Live Design Document** - Update after every change
3. **Delete Over Archive** - Trust git, remove obsolete
4. **One Prompt Per File** - Single responsibility
5. **Test-First Development (TDD)** - RED → GREEN → REFACTOR
6. **Governance Self-Enforcement** - Rules apply to rules
7. **Single Responsibility (SRP)** - One job per agent
8. **Interface Segregation (ISP)** - Dedicated specialists
9. **Dependency Inversion (DIP)** - Abstractions required
10. **Tier Boundary Enforcement** - Data in correct tier
11. **FIFO Queue Management** - 20 conversation limit
12. **Pattern Confidence Decay** - Unused patterns deleted
13. **Anomaly Detection** - Track violations
14. **Dev Context Throttling** - 1-hour minimum
15. **Git Commit Automation** - Auto-commit on completion
16. **Automatic Brain Updates** - 50 events OR 24h
17. **Conversation Auto-Recording** - 71%+ auto rate
18. **Challenge User Changes** - Protect quality
19. **Checkpoint Strategy** - Enable rollback
20. **Definition of DONE** - Quality gate
21. **Definition of READY** - Entry gate
22. **Brain Protection System** - Multi-layer protection

---

## File Structure

```
CORTEX/src/tier0/
├── governance.yaml          # All 22 rules (main file)
├── dor.yaml                 # Definition of Ready
├── dod.yaml                 # Definition of Done
├── tdd-enforcement.yaml     # TDD workflow rules
└── protection-rules.yaml    # Brain protection config
```

---

## Rule Storage Format

**File:** `governance.yaml`

```yaml
version: 1.0
last_updated: "2025-11-05"
rule_count: 22
immutable: true

rules:
  - id: TEST_FIRST_TDD
    number: 5
    severity: CRITICAL
    category: quality
    description: "Test-Driven Development workflow enforcement"
    workflow:
      RED:
        - "Write failing test FIRST"
        - "Verify test fails"
        - "Commit RED state"
      GREEN:
        - "Implement minimum code"
        - "Verify test passes"
        - "Commit GREEN state"
      REFACTOR:
        - "Clean up code"
        - "Verify tests still pass"
        - "Commit REFACTOR state"
    enforcement:
      agent: "brain-protector"
      pre_commit_hook: true
      challenge_on_violation: true
    
  - id: DEFINITION_OF_DONE
    number: 20
    severity: CRITICAL
    category: quality
    description: "Quality gate for work completion"
    criteria:
      compilation:
        - "Zero errors"
        - "Zero warnings"
        - "Clean build"
      testing:
        - "All tests pass"
        - "New tests for new code"
        - "TDD cycle complete"
      quality:
        - "Code formatted"
        - "No linting violations"
        - "Documentation updated"
      runtime:
        - "App runs without errors"
        - "No exceptions in logs"
        - "Functionality verified"
    enforcement:
      agent: "health-validator"
      validation_point: "pre-commit"
      blocker: true
```

---

## Enforcement Mechanism

### 1. Challenge Protocol (Rule #18)

When user violates rule:

```yaml
challenge_process:
  step_1:
    action: "Detect violation"
    detection: "Pattern match, rule check, anomaly detection"
    
  step_2:
    action: "Query knowledge graph"
    evidence: "Success rates, historical data, similar violations"
    
  step_3:
    action: "Present challenge"
    format: |
      ═══════════════════════════════════════════════
      🧠 GOVERNANCE CHALLENGE (Tier 0)
      
      Request: [User's request]
      Violation: [Rule violated]
      
      ⚠️ RISK DETECTED:
        - [Specific risk with evidence]
        - [Historical failure rate: X%]
      
      SAFE ALTERNATIVES:
        1. [Alternative 1] ✅ RECOMMENDED
           - [Benefit]
           - [Success rate: Y%]
        
        2. [Alternative 2]
           - [Benefit]
           - [Trade-off]
      
      RECOMMENDATION: [Number]
      ═══════════════════════════════════════════════
      
      Options:
        1. Accept recommended alternative (SAFE)
        2. Provide different approach (REVIEW)
        3. Type 'OVERRIDE' with justification (RISKY)
    
  step_4:
    action: "Await user decision"
    timeout: "No automatic proceed"
    
  step_5:
    action: "Log challenge outcome"
    storage: "cortex-brain/tier0/challenges.jsonl"
```

### 2. Pre-Commit Validation (Rule #20 DoD)

```yaml
pre_commit_gates:
  gate_1_build:
    check: "dotnet build"
    pass_criteria: "Exit code 0, zero errors, zero warnings"
    
  gate_2_tests:
    check: "Run all tests"
    pass_criteria: "100% tests passing"
    
  gate_3_tdd:
    check: "Verify tests exist for new code"
    pass_criteria: "Every .cs file has .cs test file"
    
  gate_4_runtime:
    check: "App startup validation"
    pass_criteria: "No exceptions in first 5 seconds"
    
  gate_5_quality:
    check: "Linting, formatting"
    pass_criteria: "Zero violations"

on_failure:
  action: "Block commit"
  message: "DoD not met - fix issues before commit"
  report: "Show specific failures"
```

---

## Integration with Other Tiers

### Tier 0 → Tier 1 (Working Memory)
- Validates conversation format before storage
- Enforces FIFO eviction (Rule #11)
- Protects against malformed data

### Tier 0 → Tier 2 (Knowledge Graph)
- Validates pattern confidence (Rule #12)
- Enforces tier boundaries (Rule #10)
- Triggers anomaly detection (Rule #13)

### Tier 0 → Tier 3 (Context)
- Enforces throttling (Rule #14, 1-hour minimum)
- Validates metric freshness
- Protects against excessive git queries

---

## Testing Strategy

### Unit Tests (15 tests)

**File:** `CORTEX/tests/tier0/test_governance.py`

```python
import pytest
from cortex.src.tier0 import GovernanceEngine

def test_tdd_enforcement_challenges_implementation_without_test():
    """Rule #5: TDD enforcement"""
    engine = GovernanceEngine()
    request = "Implement UserService.CreateUser() method"
    
    result = engine.validate_request(request)
    
    assert result.challenge_issued == True
    assert result.rule_violated == "TEST_FIRST_TDD"
    assert "Create test first" in result.challenge_message

def test_dod_validates_all_criteria():
    """Rule #20: Definition of DONE"""
    engine = GovernanceEngine()
    
    # Simulate work completion
    context = {
        "build_errors": 0,
        "build_warnings": 0,
        "tests_passed": 45,
        "tests_total": 45,
        "tdd_cycle": "REFACTOR",
        "runtime_errors": 0
    }
    
    result = engine.validate_done(context)
    
    assert result.is_done == True
    assert result.all_gates_passed == True

def test_tier_boundary_violation_detected():
    """Rule #10: Tier boundary enforcement"""
    engine = GovernanceEngine()
    
    # Try to store conversation in Tier 0
    violation = {
        "tier": "tier0",
        "data_type": "conversation",
        "content": {"title": "Test conversation"}
    }
    
    result = engine.validate_tier_boundary(violation)
    
    assert result.violation_detected == True
    assert result.correct_tier == "tier1"
    assert result.auto_migrate == True

# ... 12 more tests for other rules
```

---

## Quick Reference

### Loading Tier 0 Rules

```python
from cortex.src.tier0 import load_governance

# Load all rules
rules = load_governance()

# Get specific rule
tdd_rule = rules.get_rule("TEST_FIRST_TDD")

# Check if action violates rules
violation = rules.check_violation(user_request)

if violation:
    challenge = rules.create_challenge(violation)
    present_to_user(challenge)
```

### Checking DoD

```python
from cortex.src.tier0 import check_dod

# After work completion
dod_result = check_dod({
    "build": build_status,
    "tests": test_results,
    "runtime": runtime_check
})

if not dod_result.passed:
    print(f"DoD not met: {dod_result.failures}")
    block_commit()
```

---

## Migration from KDS

### Changes Made

1. **Renamed References:**
   - `kds-brain` → `cortex-brain`
   - `prompts/user/kds.md` → `cortex-agents/user/cortex.md`

2. **Simplified Rules:**
   - Removed duplicate enforcement (consolidated)
   - Clearer rule numbering (1-22)

3. **Storage Format:**
   - YAML (same as KDS for Tier 0)
   - Added rule metadata (severity, category)
   - Structured for programmatic access

### Preserved Rules

All 22 KDS governance rules preserved with updated references.

---

## Next Steps

**After Tier 0 complete:**
1. Implement Tier 1 (Working Memory - SQLite)
2. Implement Tier 2 (Knowledge Graph - SQLite + FTS5)
3. Implement Tier 3 (Context Intelligence - JSON)
4. Refactor agents for CORTEX
5. Feature parity validation

---

**Status:** 📋 DESIGNED (Implementation in progress)  
**Last Updated:** 2025-11-05  
**Next:** Implement `governance.yaml` and `GovernanceEngine` class
