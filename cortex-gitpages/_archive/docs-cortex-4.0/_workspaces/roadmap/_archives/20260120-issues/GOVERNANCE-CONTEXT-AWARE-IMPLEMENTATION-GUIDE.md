# CORTEX Governance Intelligence - Implementation Gap Details
## Code Examples and Remediation Roadmap

**Date**: 2026-01-20  
**Companion to**: GOVERNANCE-INTELLIGENCE-REVIEW-20260120.md  
**Audience**: Architecture, Implementation Team

---

## Executive Summary

This document provides:
1. **Code examples** showing the gap in context-aware rule application
2. **Root cause analysis** of why context-aware logic is incomplete
3. **Specific code locations** where context evaluation is needed
4. **Reference implementation** for situational rule engine
5. **Step-by-step remediation roadmap**

---

## Section 1: The Gap - Code Evidence

### 1.1 Current Rule Evaluator (BROKEN)

**File**: `cortex/brain/core/rule_evaluator.py`  
**Lines**: 158-193  
**Problem**: Rule evaluation function returns None (passes) for almost all rules

```python
def _evaluate_single_rule(
    self, 
    rule: GovernanceRule, 
    context: Dict[str, Any]
) -> Optional[RuleViolation]:
    """
    Evaluate a single rule against context.
    
    Returns violation if rule fails, None if passes
    """
    try:
        # Rule matching logic based on rule_id and context
        # This is a simplified version - real implementation would have complex matching
        #                                                    ↑
        #                                          ADMISSION: INCOMPLETE
        
        # Example: Check if operation type matches rule
        if "operation_type" in context:
            op_type = context["operation_type"]
            
            # SKULL-001: No modifications to Tier 0 rules
            if rule.rule_id == "SKULL-001" and op_type == "MODIFY_TIER0":
                return RuleViolation(...)
        
        # Check if rule should apply based on context
        # Return None if rule passes
        return None  # ← ALL OTHER RULES PASS SILENTLY
        #
        # PROBLEM: There is no logic to:
        # 1. Check if rule is applicable in this context
        # 2. Evaluate rule conditions
        # 3. Return violations for actual failures
        #
        # Result: 28/29 rules skipped, only SKULL-001 checked
        
    except Exception as e:
        return RuleViolation(...)
```

**Impact**: 
- ❌ CORE-008 (TDD) never evaluated
- ❌ CORE-022 (Kebab-case) never evaluated  
- ❌ CORE-028 (Smart naming) never evaluated
- ❌ CORE-030 (Response headers) never evaluated
- Only SKULL-001 is checked

---

### 1.2 Missing Context in RuleContext

**Current State**: `stage2_integration.py` shows context passed to evaluator:

```python
# From GovernanceGate.check_eligibility()
rules: Dict[str, Tuple[RuleSeverity, bool]] = ...
context = {
    "intent": intent.value,
    "confidence": confidence.value,
    "phase": phase.value,
}

# What's MISSING for context-aware evaluation:
# - file_type: "python" | "yaml" | "json" | "md" | "sh"
# - file_context: "generated" | "internal" | "user_facing" | "test"
# - operation: "create_file" | "modify_code" | "refactor" | "run_tests"
# - severity: "critical" | "normal" | "utility"
# - phase_stage: "exploration" | "development" | "production"
```

**Result**: Evaluator cannot determine applicability because context is incomplete.

---

### 1.3 Rule Registration Without Applicability

**File**: `cortex/brain/core/governance_registry.py`

```python
def add_tier1_rule(self, rule: GovernanceRule) -> Result[None]:
    """Add Tier 1 rule to registry"""
    self._tier1_rules[rule.rule_id] = rule
    # ↑ Rule stored but with NO metadata about:
    #   - When it applies
    #   - Which file types it covers
    #   - Which operations trigger it
    #   - What contexts exempt it
    
    return Ok(None)
```

**Missing**: Rule applicability metadata embedded in GovernanceRule dataclass.

---

## Section 2: Rule-by-Rule Gap Analysis

### 2.1 CORE-008: Test-First Development

**Rule Severity**: BLOCKED  
**Current Enforcement**: Universally required

**What SHOULD happen**:

```python
# PSEUDOCODE: Context-aware TDD enforcement

def should_enforce_tdd(context: RuleContext) -> bool:
    """Determine if TDD (test-first) should be enforced"""
    
    # TDD required for production code
    if context.file_context == "production_code":
        # Phase matters
        if context.phase_stage in ["development", "testing", "production"]:
            return True  # ✓ Enforce TDD
        elif context.phase_stage == "exploration":
            return False  # Test-after OK for POC
    
    # TDD relaxed for internal utilities
    if context.file_context in ["internal_utility", "script", "helper"]:
        return False  # Test-after OK
    
    # TDD relaxed for generated code
    if context.is_generated:
        return False  # Scaffolder handles testing
    
    return True  # Default: enforce
```

**What actually happens**:
- Rule defined with universal applicability
- `_evaluate_single_rule()` returns None (passes)
- All code passes CORE-008 check regardless of context

**Evidence of problem**: 
- AC-REM-011-01 report claims CORE-008 validated
- But code shows `_evaluate_single_rule()` never actually checks it

---

### 2.2 CORE-022/CORE-028: File Naming

**Rule Severity**: BLOCKED  
**Current Enforcement**: Universally required (kebab-case, ≤25 chars)

**What SHOULD happen**:

```python
def validate_file_naming(file_path: str, context: FileContext) -> ValidationResult:
    """
    Validate file naming with context awareness.
    
    CORE-022/CORE-028: Kebab-case, ≤25 chars
    """
    
    file_name = Path(file_path).stem
    extension = Path(file_path).suffix
    
    # Determine if naming rule applies
    should_validate = False
    reason = ""
    
    # User-facing files: ALWAYS validate
    if context.file_context == "user_facing":
        should_validate = True
        reason = "user_facing → require kebab-case"
    
    # Configuration/YAML files: ALWAYS validate
    elif extension in [".yaml", ".yml", ".json", ".toml"]:
        should_validate = True
        reason = "config_file → require kebab-case"
    
    # Python files - context-dependent
    elif extension == ".py":
        if context.file_context in ["generated", "internal_utility"]:
            should_validate = False
            reason = "internal_python → snake_case OK"
        elif context.file_context == "user_facing":
            should_validate = True
            reason = "public_tool → require kebab-case"
    
    # Generated code: SKIP validation
    if context.is_generated:
        return ValidationResult(
            valid=True,
            reason="Generated code exempted from naming rules"
        )
    
    # Test fixtures: SKIP validation
    if context.is_test_code:
        return ValidationResult(
            valid=True,
            reason="Test fixtures exempted from naming rules"
        )
    
    # NOW validate if rule applies
    if should_validate:
        if not file_name.islower() or " " in file_name:
            return ValidationResult(
                valid=False,
                reason=f"{reason}: '{file_name}' uses invalid characters"
            )
        
        total_length = len(file_name) + len(extension)
        if total_length > 25:
            return ValidationResult(
                valid=False,
                reason=f"{reason}: '{file_name}{extension}' ({total_length} chars) exceeds 25 limit"
            )
    
    return ValidationResult(valid=True, reason=reason)
```

**What actually happens**:
- Rule validation applied uniformly
- No code checks if file is generated
- No code checks if it's internal vs. user-facing
- Result: Either all files pass or all fail, no nuance

---

### 2.3 CORE-030: Mandatory Response Headers

**Rule Severity**: BLOCKED  
**Declared**: "No exceptions. No variations. This is immutable."

**What SHOULD happen**:

```python
def validate_response_header(response: str, context: ResponseContext) -> bool:
    """
    Validate CORTEX response headers with context awareness.
    
    CORE-030 applies to interactive orchestrator responses,
    but not to error messages or internal debug output.
    """
    
    # Response type filter: Apply header rule to appropriate response types
    response_type_requires_header = {
        "orchestrator_response": True,
        "interactive_output": True,
        "user_facing_result": True,
        "error_message": False,  # Error messages don't need ornamental headers
        "debug_output": False,   # Internal debug doesn't need headers
        "json_api_response": False,  # JSON APIs don't need markdown headers
        "batch_process": False,  # Batch operations don't need headers
    }
    
    if context.response_type not in response_type_requires_header:
        return True  # Unknown type → pass
    
    if not response_type_requires_header[context.response_type]:
        return True  # Header not required for this response type
    
    # NOW check for header
    required_header_pattern = r"^## 🧠 CORTEX \w+\n\*\*Author: Asif Hussain.*\n---"
    
    if not re.match(required_header_pattern, response):
        return False  # Missing required header
    
    return True  # Header present and valid
```

**What actually happens**:
- CORE-030 says "immutable, no exceptions"
- But no code actually enforces it (returns None in evaluator)
- Result: Headers applied selectively, not as immutable rule

---

## Section 3: Root Cause Analysis

### 3.1 Why Situational Logic Was Never Implemented

**Evidence from code comments**:

```python
# From rule_evaluator.py, line 169:
# "This is a simplified version - real implementation would have complex matching"
```

**Interpretation**: Feature was planned but not completed. Likely reasons:

1. **Time pressure**: Needed to lock phases, implemented minimum viable
2. **Complexity**: Context-aware evaluation requires rule-by-rule implementation
3. **Unknown requirements**: What contexts exempt which rules? Unclear
4. **Testing gaps**: Would need comprehensive test matrix for each rule
5. **Premature optimization**: Tried to build generic framework before understanding all rules

### 3.2 Design Debt

**Architectural issue**: Rules defined without applicability metadata

```yaml
# Current: Rules described but not contextualized
- rule_id: CORE-008
  name: Test-First Development
  description: Tests MUST exist BEFORE implementation

# Needed: Rule WITH applicability conditions
- rule_id: CORE-008
  name: Test-First Development
  applies_to:
    - file_types: [".py"]
    - operations: ["create_feature", "implement_ac"]
    - contexts: ["production_code"]
  exempt_in:
    - phase_stage: ["exploration", "poc"]
    - file_context: ["internal_utility", "generated", "script"]
    - environments: ["test_fixture"]
```

---

## Section 4: Reference Implementation

### 4.1 Situational Rule Evaluator (SOLUTION)

```python
# NEW FILE: cortex/brain/core/governance/situational_rule_evaluator.py

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from enum import Enum

class FileContext(Enum):
    """Determines which rules apply to a file"""
    PRODUCTION_CODE = "production_code"      # Main implementation
    INTERNAL_UTILITY = "internal_utility"    # Internal tools/helpers
    USER_FACING = "user_facing"              # Public tools/APIs
    GENERATED = "generated"                  # Scaffolded/auto-generated
    TEST_CODE = "test_code"                  # Test files
    TEST_FIXTURE = "test_fixture"            # Test data
    CONFIG = "config"                        # Configuration
    DOCUMENTATION = "documentation"          # Docs/comments
    EXTERNAL = "external"                    # Third-party

class PhaseStage(Enum):
    """Development phase affects rule applicability"""
    EXPLORATION = "exploration"              # POC, research
    DEVELOPMENT = "development"              # Feature development
    TESTING = "testing"                      # QA, hardening
    PRODUCTION = "production"                # Live code

class OperationType(Enum):
    """Types of operations with different rule requirements"""
    CREATE_FILE = "create_file"
    MODIFY_CODE = "modify_code"
    REFACTOR = "refactor"
    GENERATE_DOCS = "generate_docs"
    RUN_TESTS = "run_tests"
    DEPLOY = "deploy"

@dataclass
class SituationalRuleContext:
    """
    Context for determining rule applicability.
    
    Richer than current RuleContext - includes all factors
    that determine which governance rules should apply.
    """
    operation: OperationType
    file_type: Optional[str]                 # ".py", ".yaml", ".md"
    file_context: Optional[FileContext]      # Where is this file?
    phase_stage: Optional[PhaseStage]        # What development phase?
    is_generated: bool = False               # Auto-generated?
    is_test_code: bool = False               # Test vs. production?
    severity_level: str = "normal"           # critical, normal, utility
    environment: str = "development"         # dev, staging, production
    orchestrator_type: Optional[str] = None  # master, specialized, etc.
    response_type: Optional[str] = None      # For response rules

class RuleApplicabilityMatrix:
    """
    Determines which rules apply in which contexts.
    
    This is the CORE missing piece in CORTEX governance.
    """
    
    # Rule applicability mapping
    _applicability: Dict[str, Dict] = {
        "CORE-008": {  # TDD
            "applies_when": {
                "file_type": [".py"],
                "file_context": ["production_code", "user_facing"],
                "operation": ["create_file", "modify_code"],
                "phase_stage": ["development", "testing", "production"]
            },
            "exempt_when": {
                "file_context": ["generated", "internal_utility", "script"],
                "phase_stage": ["exploration"],
                "is_generated": True
            }
        },
        "CORE-022": {  # Kebab-case
            "applies_when": {
                "file_type": [".sh", ".yaml", ".yml", ".json", ".toml", ".md"],
                "file_context": ["user_facing", "config", "documentation"]
            },
            "exempt_when": {
                "file_context": ["generated", "external"],
                "is_generated": True
            }
        },
        "CORE-028": {  # Smart naming
            "applies_when": {
                "operation": ["create_file"],
                "file_context": ["user_facing", "config"]
            },
            "exempt_when": {
                "is_generated": True,
                "is_test_code": True,
                "file_context": ["external"]
            }
        },
        "CORE-030": {  # Response headers
            "applies_when": {
                "response_type": ["orchestrator_response", "user_facing"],
                "orchestrator_type": ["master", "specialized"]
            },
            "exempt_when": {
                "response_type": ["error_message", "debug", "json_api", "batch"]
            }
        }
    }
    
    def should_apply(
        self,
        rule_id: str,
        context: SituationalRuleContext
    ) -> bool:
        """
        Determine if a rule should be enforced in this context.
        
        Returns True if rule applies, False if exempt.
        """
        if rule_id not in self._applicability:
            return True  # Unknown rule → default to apply
        
        rules = self._applicability[rule_id]
        
        # Check exemptions FIRST (priority)
        if self._matches_conditions(context, rules.get("exempt_when", {})):
            return False  # Rule exempt in this context
        
        # Check applicability conditions
        applies_to = rules.get("applies_when", {})
        if not applies_to:
            return True  # No conditions specified → always apply
        
        return self._matches_conditions(context, applies_to)
    
    def _matches_conditions(
        self,
        context: SituationalRuleContext,
        conditions: Dict
    ) -> bool:
        """Check if context matches all conditions"""
        for key, required_values in conditions.items():
            if key == "file_type":
                if context.file_type not in required_values:
                    return False
            elif key == "file_context":
                if context.file_context.value not in required_values:
                    return False
            elif key == "operation":
                if context.operation.value not in required_values:
                    return False
            elif key == "phase_stage":
                if context.phase_stage.value not in required_values:
                    return False
            elif key == "response_type":
                if context.response_type not in required_values:
                    return False
            elif key == "is_generated":
                if context.is_generated != required_values:
                    return False
            elif key == "is_test_code":
                if context.is_test_code != required_values:
                    return False
        
        return True

class SituationalRuleEvaluator:
    """
    Updated rule evaluator with context awareness.
    
    Replaces _evaluate_single_rule() logic with intelligent
    applicability checking BEFORE rule evaluation.
    """
    
    def __init__(self):
        self.applicability = RuleApplicabilityMatrix()
    
    def evaluate_single_rule(
        self,
        rule: GovernanceRule,
        context: SituationalRuleContext
    ) -> Optional[RuleViolation]:
        """
        Evaluate a rule with context awareness.
        
        NEW: Check if rule applies FIRST
        THEN: Evaluate rule conditions
        """
        # STEP 1: Check applicability
        if not self.applicability.should_apply(rule.rule_id, context):
            return None  # Rule doesn't apply → pass (no violation)
        
        # STEP 2: Now evaluate rule (previously missing logic)
        violation = self._evaluate_rule_conditions(rule, context)
        return violation
    
    def _evaluate_rule_conditions(
        self,
        rule: GovernanceRule,
        context: SituationalRuleContext
    ) -> Optional[RuleViolation]:
        """Actual rule validation logic (to be implemented per rule)"""
        # This would contain the actual rule checks
        # For now, return None (placeholder)
        return None
```

### 4.2 Integration into Existing Evaluator

```python
# MODIFIED: cortex/brain/core/rule_evaluator.py

class RuleEvaluator:
    """Updated with situational evaluation"""
    
    def __init__(self):
        self.logger = EnhancedAuditLogger.instance()
        self.registry = GovernanceRegistry.instance()
        self.situational_evaluator = SituationalRuleEvaluator()  # NEW
    
    def evaluate_rules(
        self,
        context: Dict[str, Any],
        tier_filter: Optional[int] = None,
        category_filter: Optional[str] = None
    ) -> Result[EvaluationResult]:
        """Updated to use situational evaluation"""
        
        # Convert legacy context dict to new SituationalRuleContext
        situational_context = self._build_situational_context(context)
        
        # Rest of method...
        violations: List[RuleViolation] = []
        
        for tier in [0, 1, 2]:
            for rule in self._get_rules_by_tier(tier):
                if category_filter and rule.category != category_filter:
                    continue
                
                # NEW: Use situational evaluator
                violation = self.situational_evaluator.evaluate_single_rule(
                    rule, 
                    situational_context
                )
                
                if violation:
                    violations.append(violation)
        
        # ... logging and result return ...
```

---

## Section 5: Implementation Roadmap

### Phase 1: Foundation (Days 1-2)

**Goal**: Create situational evaluation framework

**Tasks**:
1. Create `situational_rule_evaluator.py` with:
   - `SituationalRuleContext` dataclass
   - `FileContext` and `PhaseStage` enums
   - `RuleApplicabilityMatrix` class
   - `should_apply()` method

2. Write tests in `tests/unit/governance/test_situational_rules.py`:
   - Test each rule's applicability matrix
   - Test context combinations
   - Test exemption conditions

**Deliverable**: Situational evaluator framework (not yet integrated)

---

### Phase 2: Integration (Days 3-4)

**Goal**: Wire situational evaluator into existing system

**Tasks**:
1. Modify `RuleEvaluator`:
   - Instantiate `SituationalRuleEvaluator`
   - Update `_evaluate_single_rule()` to use situational logic
   - Update context building to populate new fields

2. Update `stage2_integration.py`:
   - Enhance context dictionary passed to evaluator
   - Add file_type, file_context, operation fields

3. Integration tests:
   - Test rules apply/exempt correctly
   - Test legacy rule evaluation still works
   - Test new context fields properly populated

**Deliverable**: Situational evaluator integrated into rule engine

---

### Phase 3: Rule Implementation (Days 5-7)

**Goal**: Implement actual rule validation logic

**Tasks**:
1. Implement `_evaluate_rule_conditions()` for each rule:
   - CORE-008: Check test file exists
   - CORE-022/028: Validate file naming
   - CORE-030: Check response headers
   - CORE-005: Validate portable paths
   - Others as applicable

2. Comprehensive test suite for each rule

3. Integration with pre-commit hooks

**Deliverable**: Full situational rule enforcement

---

### Phase 4: Documentation & Hardening (Days 8)

**Goal**: Document and harden solution

**Tasks**:
1. Update governance documentation:
   - Document applicability rules
   - Document exemption conditions
   - Provide examples

2. Update prompts to reference situational rules

3. Performance testing and optimization

**Deliverable**: Complete, documented situational governance system

---

## Section 6: Testing Strategy

### 6.1 Unit Tests for Applicability Matrix

```python
# File: tests/unit/governance/test_situational_applicability.py

class TestCORE008Applicability(unittest.TestCase):
    """Test TDD rule applicability"""
    
    def setUp(self):
        self.matrix = RuleApplicabilityMatrix()
    
    def test_applies_to_production_code(self):
        """TDD should apply to production code"""
        context = SituationalRuleContext(
            operation=OperationType.CREATE_FILE,
            file_type=".py",
            file_context=FileContext.PRODUCTION_CODE,
            phase_stage=PhaseStage.DEVELOPMENT
        )
        assert self.matrix.should_apply("CORE-008", context) == True
    
    def test_exempt_for_exploration_phase(self):
        """TDD should NOT apply during exploration"""
        context = SituationalRuleContext(
            operation=OperationType.CREATE_FILE,
            file_type=".py",
            file_context=FileContext.PRODUCTION_CODE,
            phase_stage=PhaseStage.EXPLORATION
        )
        assert self.matrix.should_apply("CORE-008", context) == False
    
    def test_exempt_for_generated_code(self):
        """TDD should NOT apply to generated code"""
        context = SituationalRuleContext(
            operation=OperationType.CREATE_FILE,
            file_type=".py",
            is_generated=True
        )
        assert self.matrix.should_apply("CORE-008", context) == False
    
    def test_exempt_for_internal_utility(self):
        """TDD should NOT apply to internal utilities"""
        context = SituationalRuleContext(
            operation=OperationType.CREATE_FILE,
            file_type=".py",
            file_context=FileContext.INTERNAL_UTILITY
        )
        assert self.matrix.should_apply("CORE-008", context) == False
```

---

## Section 7: Expected Outcomes

### 7.1 Before: Broken Enforcement

```
Rule Evaluation Chain:
  └─> _evaluate_single_rule(rule, context)
      └─> if rule_id == "SKULL-001": check something
      └─> else: return None (SKIP)
      
Result: All rules except SKULL-001 pass silently
```

### 7.2 After: Intelligent Enforcement

```
Rule Evaluation Chain:
  └─> situational_evaluator.evaluate_single_rule(rule, context)
      └─> should_apply(rule_id, context)?
          ├─> Yes → Evaluate rule conditions
          │   └─> Return violation if failed
          └─> No → Return None (exempt, pass)
      
Result: Rules applied intelligently based on context
```

---

## Appendix A: Rule Applicability Examples

### Example 1: CORE-008 (TDD) Context Evaluation

```
Scenario 1: Creating production feature
─────────────────────────────────────
Context: {
  operation: CREATE_FILE,
  file_type: ".py",
  file_context: PRODUCTION_CODE,
  phase_stage: DEVELOPMENT
}
Evaluation: should_apply("CORE-008", context) → TRUE
Result: TDD enforced ✓

Scenario 2: POC in exploration phase
─────────────────────────────────────
Context: {
  operation: CREATE_FILE,
  file_type: ".py",
  file_context: PRODUCTION_CODE,
  phase_stage: EXPLORATION
}
Evaluation: should_apply("CORE-008", context) → FALSE
Result: TDD relaxed ✓ (allows test-after pattern)

Scenario 3: Scaffolded orchestrator
─────────────────────────────────────
Context: {
  operation: CREATE_FILE,
  file_type: ".py",
  is_generated: TRUE
}
Evaluation: should_apply("CORE-008", context) → FALSE
Result: TDD skipped ✓ (scaffolder provides templates)
```

### Example 2: CORE-022 (Kebab-case) Context Evaluation

```
Scenario 1: User-facing tool
─────────────────────────────
Filename: "cortex-vacuum.py"
Context: {
  file_type: ".py",
  file_context: USER_FACING,
  operation: CREATE_FILE
}
Evaluation: should_apply("CORE-022", context) → TRUE
Result: Validate kebab-case ✓

Scenario 2: Internal Python module
───────────────────────────────────
Filename: "ac_populator.py"
Context: {
  file_type: ".py",
  file_context: INTERNAL_UTILITY,
  operation: CREATE_FILE
}
Evaluation: should_apply("CORE-022", context) → FALSE
Result: Snake_case allowed ✓ (Python convention)

Scenario 3: Generated scaffolder output
────────────────────────────────────────
Filename: "orchestrator_generated.py"
Context: {
  file_type: ".py",
  is_generated: TRUE,
  operation: CREATE_FILE
}
Evaluation: should_apply("CORE-022", context) → FALSE
Result: Generated naming allowed ✓
```

---

## Appendix B: Files to Create/Modify

### Create:
- `cortex/brain/core/governance/situational_rule_evaluator.py` (new)
- `tests/unit/governance/test_situational_rules.py` (new)
- `cortex_brain/tier0/rule-applicability-matrix.yaml` (new)

### Modify:
- `cortex/brain/core/rule_evaluator.py` (integrate situational logic)
- `cortex/brain/core/governance/stage2_integration.py` (enhance context)
- `cortex_brain/tier0/governance-loading-sequence.yaml` (reference situational evaluator)

### Update Documentation:
- `docs/GOVERNANCE-CONTEXT-AWARE-APPLICATION.md` (new guide)
- `.github/prompts/cortex-builder.prompt.md` (reference situational rules)
- `cortex/core/governance/core-rules.yaml` (add applicability sections)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
