# CORTEX Composite Requests - Real-World Examples & Best Practices

**Version:** 1.0 | **Updated:** 2026-01-22 | **Authority:** cortex/brain/core/orchestrator/conversation_protocol.py

---

## 🧠 Overview

**Composite Requests** are the final output of the CORTEX Brain system—efficient, multi-tier prompts that guide GitHub Copilot to execute tasks with full governance compliance, project context, domain expertise, and optimized token usage.

**Core Value:**
- **Efficient:** 95-96% token compression vs. naive prompts
- **Compliant:** 100% TIER 0 governance enforcement
- **Contextual:** Project + domain knowledge integrated
- **Traceable:** Linked to AC-IDs for audit trails
- **Reusable:** Templates enable pattern replication

---

## 📊 Composite Request Anatomy

### Structure

```json
{
  "metadata": {
    "request_id": "REQ-2026-01-22-001",
    "timestamp": "2026-01-22T10:30:00Z",
    "phase": "PHASE-E-IMPLEMENTATION",
    "ac_ids": ["AC-FR-001-01", "AC-FR-001-02"],
    "user": "developer@company.com",
    "domain": "cortex-brain-governance"
  },
  
  "governance": {
    "tier0_rules": ["TDD", "Types", "Docs", "Result[T]", "SRP"],
    "enforcement": "strict",
    "violations_allowed": 0
  },
  
  "context": {
    "tier1": {
      "ac_ids_summary": "FR-001✅[E:4] FR-002⏳[E:2]",
      "phase": "PHASE-E",
      "gates_passed": true
    },
    "tier2": {
      "template": "impl_multi_step",
      "verbosity": "minimal",
      "tokens_allocated": 600
    },
    "tier3": {
      "knowledge": ["KB: python-best-practices", "KB: governance-3tier"],
      "domain_rules": "governance_system"
    }
  },
  
  "request": {
    "type": "implementation",
    "user_query": "Implement AC-FR-001-01 governance validation",
    "priority": "normal"
  },
  
  "optimization": {
    "tokens": {
      "uncompressed": 7240,
      "compressed": 290,
      "efficiency_percent": 96.0
    },
    "stages": {
      "rule_compression": "86%",
      "ac_id_condensing": "67%",
      "template_reference": "97%",
      "knowledge_abstraction": "87%"
    }
  }
}
```

---

## 🎯 Real-World Examples

### Example 1: Feature Implementation

**Scenario:** Implement a governance validation feature

**User Request:**
```
Implement AC-FR-001-01: Add governance rule validator
```

**Composite Request Generated:**

```json
{
  "metadata": {
    "request_id": "REQ-2026-01-22-G001",
    "phase": "PHASE-E-IMPLEMENTATION",
    "ac_ids": ["AC-FR-001-01"],
    "domain": "cortex-brain-governance"
  },
  
  "governance": {
    "tier0_rules": [
      "TDD: [RED→GREEN→REFACTOR]",
      "Types: Annotate all functions",
      "Docs: Google-style docstrings",
      "Result[T]: Return type safety",
      "SRP: Single responsibility",
      "SOLID: Principles enforced",
      "Errors: No bare except",
      "Naming: kebab-case <25 chars"
    ]
  },
  
  "context": {
    "tier1": {
      "ac_id": "AC-FR-001-01",
      "status": "IN_PROGRESS",
      "evidence": ["Code:governance.py:1-50", "Test:validator_test.py:1-100"],
      "phase": "PHASE-E",
      "gates": "PASSED"
    },
    "tier2": {
      "template": "impl_multi_step",
      "sections": [
        "Test skeleton (RED phase)",
        "Implementation (GREEN phase)",
        "Refactoring (REFACTOR phase)",
        "Validation"
      ]
    },
    "tier3": {
      "knowledge": [
        "KB: governance-3tier (3-tier model)",
        "KB: python-best-practices (typing, errors)",
        "Pattern: GovernanceRule class structure"
      ]
    }
  },
  
  "request": {
    "type": "implementation",
    "task": "Implement rule validator for AC-FR-001-01",
    "ac_ids": ["AC-FR-001-01"],
    "priority": "high"
  },
  
  "optimization": {
    "tokens_budget": 4000,
    "tokens_used": 285,
    "efficiency": 92.9,
    "breakdown": {
      "governance": 200,
      "context": 35,
      "task": 50
    }
  }
}
```

**Flow in GitHub Copilot:**

1. **RED Phase:** Copilot generates test
   ```python
   def test_governance_validator():
       validator = GovernanceValidator()
       result = validator.validate(rule)
       assert result.is_ok()
   ```

2. **GREEN Phase:** Minimal implementation
   ```python
   class GovernanceValidator:
       def validate(self, rule):
           return Ok(True)
   ```

3. **REFACTOR Phase:** Copilot improves
   ```python
   @dataclass
   class GovernanceValidator:
       """Validate governance rules against TIER 0."""
       
       def validate(self, rule: GovernanceRule) -> Result[bool]:
           """Validate rule compliance."""
           if not rule.rule_id:
               return Err("Missing rule_id")
           return Ok(True)
   ```

4. **Verification:** All governance rules applied
   - ✅ Type hints present
   - ✅ Docstrings (Google style)
   - ✅ Result[T] return type
   - ✅ SRP maintained
   - ✅ Kebab-case naming (validator.py)

---

### Example 2: Refactoring Task

**Scenario:** Refactor orchestrator to follow SOLID principles

**User Request:**
```
Refactor AC-REFACTOR-05-02: Decompose MasterOrchestrator per SOLID
```

**Composite Request:**

```json
{
  "metadata": {
    "request_id": "REQ-2026-01-22-R002",
    "phase": "PHASE-F-REFACTORING",
    "ac_ids": ["AC-REFACTOR-05-02"]
  },
  
  "governance": {
    "tier0_rules": [
      "SOLID: All 5 principles required",
      "SRP: Single responsibility",
      "OCP: Open/closed principle",
      "Types: Complete type hints",
      "Errors: Explicit exception handling"
    ]
  },
  
  "context": {
    "tier1": {
      "ac_id": "AC-REFACTOR-05-02",
      "status": "IN_PROGRESS",
      "dependency": "AC-REFACTOR-05-01", 
      "phase": "PHASE-F"
    },
    "tier2": {
      "template": "refactoring_solid",
      "sections": [
        "Current issues analysis",
        "SOLID violations",
        "Refactoring plan",
        "Decomposed classes",
        "Validation"
      ]
    },
    "tier3": {
      "knowledge": [
        "KB: SOLID-principles",
        "Pattern: Dependency-injection",
        "Anti-pattern: God objects",
        "Example: MasterOrchestrator decomposition"
      ]
    }
  },
  
  "request": {
    "type": "refactoring",
    "task": "Decompose MasterOrchestrator per SOLID",
    "metrics": {
      "current_complexity": 8,
      "target_complexity": 5,
      "target_singletons": 1
    }
  }
}
```

**Copilot Output (SOLID-Guided):**

```python
# Before: God object (violates SRP)
class MasterOrchestrator:
    def route_intent(self): pass
    def execute_workflow(self): pass
    def apply_governance(self): pass
    def log_audit(self): pass
    def cache_result(self): pass

# After: Decomposed per SOLID (SRP)
class IntentRouter:
    """Route requests to appropriate orchestrator."""
    def route(self, intent: Intent) -> Result[Route]: pass

class WorkflowExecutor:
    """Execute workflow stages."""
    def execute(self, workflow: Workflow) -> Result[ExecutionResult]: pass

class GovernanceEnforcer:
    """Apply governance rules."""
    def enforce(self, rules: List[Rule]) -> Result[None]: pass

class MasterOrchestrator:
    """Coordinate orchestration (SRP: delegation only)."""
    
    def __init__(
        self,
        router: IntentRouter,
        executor: WorkflowExecutor,
        enforcer: GovernanceEnforcer
    ):
        self._router = router
        self._executor = executor
        self._enforcer = enforcer
    
    def execute(self, request: Request) -> Result[None]:
        """Execute with delegated responsibilities."""
        self._enforcer.enforce(request.rules)
        route = self._router.route(request.intent)
        return self._executor.execute(route.workflow)
```

✅ **SOLID Principles Applied:**
- SRP: Each class has one responsibility
- OCP: Easy to extend (new router, executor)
- LSP: All components interchangeable
- ISP: Minimal, focused interfaces
- DIP: Depends on abstractions, not concrete classes

---

### Example 3: Documentation Task

**Scenario:** Document new orchestrator

**Composite Request:**

```json
{
  "metadata": {
    "request_id": "REQ-2026-01-22-D003",
    "phase": "PHASE-DOC-REMEDIATION",
    "ac_ids": ["AC-DOC-008-01"]
  },
  
  "governance": {
    "tier0_rules": [
      "Docs: Google-style docstrings",
      "Types: Type hints in examples",
      "Naming: kebab-case in references",
      "NO_MARKDOWN_IN_BRAIN: YAML only for cortex_brain"
    ]
  },
  
  "context": {
    "tier1": {
      "ac_id": "AC-DOC-008-01",
      "status": "IN_PROGRESS",
      "phase": "PHASE-DOC"
    },
    "tier2": {
      "template": "documentation_technical",
      "sections": [
        "Overview",
        "Architecture",
        "How it works",
        "Integration points",
        "Code examples",
        "API reference"
      ]
    },
    "tier3": {
      "knowledge": [
        "KB: documentation-patterns",
        "Pattern: Architecture explanation",
        "Example: Orchestrator documentation"
      ]
    }
  },
  
  "request": {
    "type": "documentation",
    "task": "Document AdaptiveRouter orchestrator",
    "output_location": "docs/08-orchestrators/07-adaptive-router.md"
  }
}
```

**Generated Documentation Includes:**
- Architecture diagram reference
- Integration with master orchestrator
- Real-world usage examples
- Performance characteristics
- Complete API reference with type hints

---

## 🔄 Composite Request Lifecycle

### State Machine

```
[CREATED]
    ↓
[TIER_LOADING] → Load all applicable tiers
    ↓
[COMPRESSION] → Compress rules, AC-IDs, templates, knowledge
    ↓
[ASSEMBLY] → Assemble composite request structure
    ↓
[VALIDATION] → Verify all rules, tokens, compliance
    ↓
[READY] → Available for execution
    ↓
[SENT_TO_COPILOT] → Transmitted to GitHub Copilot
    ↓
[EXECUTION] → Copilot processes request
    ↓
[RESPONSE_RECEIVED] → Process Copilot response
    ↓
[AUDIT_LOGGED] → Log to audit trail with hash
    ↓
[COMPLETED]
```

### Implementation

```python
class CompositeRequestLifecycle:
    """Manage composite request state transitions."""
    
    async def create_and_execute(
        self,
        user_request: str,
        ac_ids: List[str]
    ) -> Result[ExecutionResult]:
        """Execute full composite request lifecycle."""
        
        # State: CREATED
        composite = CompositeRequest(
            user_request=user_request,
            ac_ids=ac_ids,
            state="CREATED"
        )
        
        # State: TIER_LOADING
        tier_context = await self.load_tiers(ac_ids)
        composite.state = "TIER_LOADING"
        
        # State: COMPRESSION
        compressed = await self.compress_tiers(tier_context)
        composite.state = "COMPRESSION"
        
        # State: ASSEMBLY
        assembled = await self.assemble_request(compressed)
        composite.state = "ASSEMBLY"
        
        # State: VALIDATION
        validation = self.validate_request(assembled)
        if validation.is_err():
            return Err(f"Validation failed: {validation.error()}")
        composite.state = "VALIDATION"
        
        # State: READY
        composite.state = "READY"
        
        # State: SENT_TO_COPILOT
        composite.state = "SENT_TO_COPILOT"
        response = await github_copilot.execute(assembled)
        
        # State: RESPONSE_RECEIVED
        composite.state = "RESPONSE_RECEIVED"
        
        # State: AUDIT_LOGGED
        await self.audit_log(composite, response)
        composite.state = "AUDIT_LOGGED"
        
        # State: COMPLETED
        composite.state = "COMPLETED"
        
        return Ok(ExecutionResult(response=response, composite=composite))
```

---

## 🎯 Best Practices

### DO ✅

- ✅ Always include TIER 0 rules
- ✅ Reference templates instead of embedding
- ✅ Use AC-ID condensing for state
- ✅ Cache knowledge indices for reuse
- ✅ Log all composite requests to audit trail
- ✅ Verify compression efficiency > 90%
- ✅ Check token usage ≤ budget

### DON'T ❌

- ❌ Modify TIER 0 rules in composite
- ❌ Repeat full template definitions
- ❌ Include all AC-ID details (use summaries)
- ❌ Embed knowledge instead of referencing
- ❌ Skip governance compliance checks
- ❌ Exceed token budget
- ❌ Lose audit trail linkage

---

## 📊 Quality Metrics

```python
@dataclass
class CompositeRequestMetrics:
    """Metrics for composite request quality."""
    
    # Efficiency
    tokens_uncompressed: int
    tokens_compressed: int
    efficiency_percent: float
    
    # Compliance
    tier0_rules_present: bool
    ac_id_context_valid: bool
    template_reference_valid: bool
    knowledge_accessible: bool
    
    # Governance
    violations_detected: int
    compliance_percentage: float
    
    # Performance
    assembly_time_ms: float
    validation_time_ms: float
    
    @property
    def is_production_ready(self) -> bool:
        """Check if composite ready for production."""
        return (
            self.efficiency_percent >= 90 and
            self.tier0_rules_present and
            self.compliance_percentage == 100 and
            self.violations_detected == 0
        )
```

---

## ✅ Verification Checklist

Before sending composite request to Copilot:

- [ ] TIER 0 rules complete and compliant
- [ ] AC-ID context accurate and condensed
- [ ] Template reference valid and accessible
- [ ] Knowledge indices retrievable
- [ ] Total tokens ≤ 4000
- [ ] Efficiency > 90%
- [ ] All governance checks pass
- [ ] Audit trail linked
- [ ] User request clear and actionable
- [ ] Request will fit in AI context window

---

## 🔗 Related Documentation

- [Brain Index](00-brain-index.md) - System overview
- [Token Optimization](05-token-optimization.md) - Compression details
- [TIER 0 Governance](01-tier0-governance.md) - Rule requirements
- [TIER 1 Acceptance](02-tier1-acceptance.md) - AC-ID structure
- [TIER 2 Templates](03-tier2-response-templates.md) - Template references
- [TIER 3 Knowledge](04-tier3-knowledge.md) - Knowledge retrieval

---


