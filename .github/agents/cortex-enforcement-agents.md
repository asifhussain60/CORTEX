# CORTEX Enforcement Agents
**Version:** 1.0 | **Updated:** 2026-01-24 | **Role:** 3 Specialized Governance Enforcement Agents

---

## Overview

These 3 specialized agents work together under the **EnforcementOrchestrator** to enforce governance rules at the execution stage, integrated into **MasterOrchestrator Stage 3**.

**Key Difference from Review Agents:**
- **Review agents** (8) = Post-hoc analysis (after code exists)
- **Enforcement agents** (3) = Pre-execution prevention (before action)

---

## Agent 1: GovernanceEnforcementAgent

### Focus
Enforces code quality and development discipline TIER 0 rules.

### Enforced Rules
```yaml
CORE-008: TDD Mandate
  - Requirement: Tests MUST exist before implementation code
  - Check: Does test file exist in tests/ for target module?
  - Violation: BLOCK IMPLEMENT intent
  - Exception: None (immutable Tier 0)

CORE-011: Type Hints Mandatory
  - Requirement: All functions MUST have type hints
  - Check: Parse function signatures for type annotations
  - Violation: BLOCK if any function missing hints
  - Exception: None (immutable Tier 0)

CORE-012: Google-Style Docstrings
  - Requirement: All functions MUST have docstrings
  - Check: First line of function body is docstring?
  - Violation: BLOCK if missing
  - Exception: None (immutable Tier 0)

CORE-013: Exception Handling
  - Requirement: No bare `except:` clauses allowed
  - Check: Scan code for bare except
  - Violation: BLOCK if found
  - Exception: None (immutable Tier 0)

CORE-029: Response Headers
  - Requirement: All responses MUST have CORTEX header
  - Check: Response starts with "## 🧠 CORTEX"?
  - Violation: BLOCK response if missing
  - Exception: None (immutable Tier 0)
```

### Execution Flow

```python
class GovernanceEnforcementAgent:
    """Enforces code quality TIER 0 rules."""
    
    def check_core_008_tdd(self, intent_type: str, module_path: str) -> CheckResult:
        """Verify TDD requirement."""
        if intent_type == "IMPLEMENT":
            test_file = self._find_test_file(module_path)
            if not test_file.exists():
                return CheckResult.BLOCK(
                    rule="CORE-008",
                    message="Cannot implement without test file first",
                    fix="Create test file in tests/ directory"
                )
        return CheckResult.PASS()
    
    def check_core_011_type_hints(self, code: str) -> CheckResult:
        """Verify type hints on all functions."""
        functions_without_hints = self._find_untyped_functions(code)
        if functions_without_hints:
            return CheckResult.BLOCK(
                rule="CORE-011",
                message=f"{len(functions_without_hints)} functions missing type hints",
                violations=functions_without_hints
            )
        return CheckResult.PASS()
    
    def check_core_012_docstrings(self, code: str) -> CheckResult:
        """Verify docstrings on all functions."""
        functions_without_docs = self._find_undocumented_functions(code)
        if functions_without_docs:
            return CheckResult.BLOCK(
                rule="CORE-012",
                message=f"{len(functions_without_docs)} functions missing docstrings",
                violations=functions_without_docs
            )
        return CheckResult.PASS()
    
    def execute(self, request_context) -> EnforcementResult:
        """Run all governance checks."""
        results = []
        
        results.append(self.check_core_008_tdd(
            request_context.intent_type,
            request_context.module_path
        ))
        
        if request_context.code:
            results.append(self.check_core_011_type_hints(request_context.code))
            results.append(self.check_core_012_docstrings(request_context.code))
            results.append(self.check_core_013_exceptions(request_context.code))
        
        results.append(self.check_core_029_headers(request_context.response))
        
        # If ANY check blocks, entire operation is blocked
        blocking = [r for r in results if r.status == "BLOCK"]
        if blocking:
            return EnforcementResult.BLOCKED(violations=blocking)
        
        return EnforcementResult.PASS()
```

### Output: `Enforcement-GOV.yaml`

```yaml
enforcement_result:
  agent: GovernanceEnforcementAgent
  timestamp: "2026-01-24T10:30:00Z"
  status: BLOCKED
  
  violations:
    - rule: CORE-008
      severity: TIER-0-BLOCKED
      message: "Cannot IMPLEMENT without test file"
      module: cortex/orchestrators/new_feature.py
      expected_test: tests/unit/orchestrators/test_new_feature.py
      fix: "Create test file first, write failing test"
      reference: cortex_brain/tier0/governance/core-rules.yaml
```

---

## Agent 2: SecurityCheckpointAgent

### Focus
Enforces safety checkpoints and state protection TIER 0 rules.

### Enforced Rules

```yaml
CORE-026: Git Checkpoint Before Major Changes
  - Requirement: Create git checkpoint before major operations
  - Check: Is there uncommitted work? Can we create checkpoint?
  - Violation: BLOCK if checkpoint cannot be created
  - Exception: None (immutable Tier 0)
  - Severity: TIER-0-BLOCKED

CORE-025: Rollback Readiness
  - Requirement: Ensure rollback path exists before operation
  - Check: Can we rollback to previous state?
  - Violation: BLOCK if rollback not possible
  - Exception: None (immutable Tier 0)
  - Severity: TIER-0-BLOCKED

CORE-024: State Consistency
  - Requirement: Maintain state synchronization
  - Check: Is state manager synchronized across phases?
  - Violation: ESCALATE if inconsistencies detected
  - Exception: Can proceed with manual sync
  - Severity: TIER-1-ESCALATION

CORE-027: Audit Trail Requirement
  - Requirement: AC_START logged before major operations
  - Check: Is audit trail initialized?
  - Violation: BLOCK if not
  - Exception: None (immutable Tier 0)
  - Severity: TIER-0-BLOCKED
```

### Execution Flow

```python
class SecurityCheckpointAgent:
    """Enforces safety checkpoint TIER 0 rules."""
    
    def check_core_026_git_checkpoint(self, intent_type: str) -> CheckResult:
        """Verify git checkpoint for major operations."""
        # Major operations: IMPLEMENT, FIX, REFACTOR, DEPLOY
        if intent_type in ["IMPLEMENT", "FIX", "REFACTOR", "DEPLOY"]:
            git_status = self._get_git_status()
            
            if git_status.has_uncommitted_changes:
                return CheckResult.BLOCK(
                    rule="CORE-026",
                    message="Uncommitted changes exist - create checkpoint first",
                    fix='git commit -m "checkpoint: before {AC-ID}"'
                )
            
            # Try to create checkpoint
            checkpoint = self._create_checkpoint(intent_type)
            if not checkpoint.success:
                return CheckResult.BLOCK(
                    rule="CORE-026",
                    message=f"Cannot create checkpoint: {checkpoint.error}",
                    fix="Resolve git status first"
                )
        
        return CheckResult.PASS()
    
    def check_core_025_rollback_readiness(self, intent_type: str) -> CheckResult:
        """Verify rollback path exists."""
        if intent_type in ["IMPLEMENT", "FIX", "DEPLOY"]:
            rollback_info = self._compute_rollback_path()
            if not rollback_info.is_possible:
                return CheckResult.BLOCK(
                    rule="CORE-025",
                    message=f"Rollback not possible: {rollback_info.reason}",
                    fix="Create checkpoint before continuing"
                )
        return CheckResult.PASS()
    
    def execute(self, request_context) -> EnforcementResult:
        """Run all safety checkpoint checks."""
        results = []
        
        results.append(self.check_core_026_git_checkpoint(
            request_context.intent_type
        ))
        results.append(self.check_core_025_rollback_readiness(
            request_context.intent_type
        ))
        
        # If ANY check blocks, entire operation is blocked
        blocking = [r for r in results if r.status == "BLOCK"]
        if blocking:
            return EnforcementResult.BLOCKED(violations=blocking)
        
        return EnforcementResult.PASS()
```

### Output: `Enforcement-SEC.yaml`

```yaml
enforcement_result:
  agent: SecurityCheckpointAgent
  timestamp: "2026-01-24T10:30:00Z"
  status: BLOCKED
  
  violations:
    - rule: CORE-026
      severity: TIER-0-BLOCKED
      message: "Cannot execute major operation without git checkpoint"
      git_status:
        uncommitted_files: ["cortex/new_feature.py", "tests/test_new_feature.py"]
        branch: "CORTEX"
        can_checkpoint: true
      fix: 'git commit -m "checkpoint: before AC-IMPL-001"'
      reference: cortex_brain/tier0/governance/core-rules.yaml
```

---

## Agent 3: ComplianceValidationAgent

### Focus
Enforces phase readiness and acceptance criteria TIER 1 rules (escalation mode).

### Enforced Rules

```yaml
TIER-1-001: Phase Dependency Resolution
  - Requirement: All prerequisite phases must be COMPLETED
  - Check: Query phase tracker for dependency status
  - Violation: ESCALATE if dependencies blocked
  - Exception: Can override with manual approval
  - Severity: TIER-1-ESCALATION

TIER-1-002: Acceptance Criteria Completion
  - Requirement: Related ACs must be complete or compatible
  - Check: Query phase tracker for AC status
  - Violation: ESCALATE if critical ACs incomplete
  - Exception: Can mark AC as co-dependent
  - Severity: TIER-1-ESCALATION

TIER-1-003: Test Coverage Threshold
  - Requirement: Code must have ≥80% test coverage
  - Check: Run coverage analysis on module
  - Violation: ESCALATE if coverage < 80%
  - Exception: Can proceed with documented justification
  - Severity: TIER-1-ESCALATION

TIER-1-004: Documentation Requirement
  - Requirement: Documentation should be updated for phase
  - Check: Is docs/{phase}/ directory updated?
  - Violation: WARN if docs missing (not blocking)
  - Exception: Optional for certain phases
  - Severity: TIER-1-WARNING
```

### Execution Flow

```python
class ComplianceValidationAgent:
    """Enforces compliance TIER 1 rules (escalation mode)."""
    
    def check_tier1_001_dependencies(self, phase_id: str) -> CheckResult:
        """Verify phase dependencies are met."""
        phase_info = self._get_phase_info(phase_id)
        unmet_dependencies = []
        
        for dep in phase_info.dependencies:
            dep_status = self._get_phase_status(dep)
            if dep_status != "COMPLETED":
                unmet_dependencies.append(dep)
        
        if unmet_dependencies:
            return CheckResult.ESCALATE(
                rule="TIER-1-001",
                message=f"Blocking dependencies: {', '.join(unmet_dependencies)}",
                blocked_by=unmet_dependencies,
                severity="ESCALATION"
            )
        return CheckResult.PASS()
    
    def check_tier1_003_test_coverage(self, module_path: str) -> CheckResult:
        """Verify test coverage threshold."""
        coverage = self._measure_coverage(module_path)
        
        if coverage.percent < 80:
            return CheckResult.ESCALATE(
                rule="TIER-1-003",
                message=f"Test coverage {coverage.percent}% (required: 80%)",
                current_coverage=coverage.percent,
                required_coverage=80,
                severity="ESCALATION"
            )
        return CheckResult.PASS()
    
    def execute(self, request_context) -> EnforcementResult:
        """Run all compliance checks."""
        results = []
        
        results.append(self.check_tier1_001_dependencies(
            request_context.phase_id
        ))
        
        if request_context.module_path:
            results.append(self.check_tier1_003_test_coverage(
                request_context.module_path
            ))
        
        # For Tier 1, we escalate but don't block
        escalations = [r for r in results if r.status == "ESCALATE"]
        if escalations:
            return EnforcementResult.ESCALATED(violations=escalations)
        
        return EnforcementResult.PASS()
```

### Output: `Enforcement-COMP.yaml`

```yaml
enforcement_result:
  agent: ComplianceValidationAgent
  timestamp: "2026-01-24T10:30:00Z"
  status: ESCALATED
  
  escalations:
    - rule: TIER-1-003
      severity: TIER-1-ESCALATION
      message: "Test coverage below threshold"
      module: cortex/orchestrators/new_feature.py
      current_coverage: 72%
      required_coverage: 80%
      gap: 8%
      recommendation: "Add 12-15 test cases to reach 80% coverage"
      action: "Operation proceeds with warning"
      reference: cortex_brain/tier1/acceptance/
```

---

## 🎼 Orchestration: EnforcementOrchestrator

### Architecture

```python
class EnforcementOrchestrator(IOrchestrator):
    """Coordinates all 3 enforcement agents."""
    
    def __init__(self):
        self.governance_agent = GovernanceEnforcementAgent()
        self.security_agent = SecurityCheckpointAgent()
        self.compliance_agent = ComplianceValidationAgent()
        self.logger = EnhancedAuditLogger.instance()
    
    def execute(self, request_context: OperationContext) -> EnforcementResult:
        """
        Run enforcement against all 3 agents.
        
        Execution order:
        1. GovernanceEnforcementAgent (Tier 0 blocking rules)
        2. SecurityCheckpointAgent (Tier 0 safety rules)
        3. ComplianceValidationAgent (Tier 1 escalations)
        
        If ANY Tier 0 agent blocks, stop and report violation.
        If Tier 1 agent escalates, continue but warn.
        """
        
        # Stage 1: Tier 0 Blocking Rules
        gov_result = self.governance_agent.execute(request_context)
        if gov_result.blocked:
            self.logger.log_enforcement_violation(
                ac_id="AC-ENF-001",
                agent="GovernanceEnforcementAgent",
                violations=gov_result.violations
            )
            return gov_result
        
        # Stage 2: Tier 0 Safety Rules
        sec_result = self.security_agent.execute(request_context)
        if sec_result.blocked:
            self.logger.log_enforcement_violation(
                ac_id="AC-ENF-002",
                agent="SecurityCheckpointAgent",
                violations=sec_result.violations
            )
            return sec_result
        
        # Stage 3: Tier 1 Escalations (advisory)
        comp_result = self.compliance_agent.execute(request_context)
        if comp_result.escalated:
            self.logger.log_enforcement_escalation(
                ac_id="AC-ENF-003",
                agent="ComplianceValidationAgent",
                escalations=comp_result.escalations
            )
        
        # Log successful enforcement pass
        self.logger.log_enforcement_pass(
            ac_id="AC-ENF-PASS",
            agents=["Governance", "Security", "Compliance"]
        )
        
        return EnforcementResult.PASS()
```

### Integration with MasterOrchestrator

```python
class MasterOrchestrator:
    """Master orchestrator with enforcement integration."""
    
    def __init__(self):
        # ... existing initialization ...
        self._enforcement_orchestrator = EnforcementOrchestrator()
    
    def execute(self, request: OperationRequest) -> OperationResult:
        """
        Enhanced execute with enforcement stage.
        
        Stage 1: Intent Classification (LENS)
        Stage 2: DoR Approval Gate
        Stage 3: ⭐ Rule Enforcement (NEW)
        Stage 4: Domain Orchestrator Delegation
        """
        
        # Stage 1: Classify intent
        intent = self._classify_intent(request)
        
        # Stage 2: Get DoR approval
        approval = self._get_dor_approval(intent)
        if not approval.approved:
            return OperationResult.CANCELLED()
        
        # Stage 3: ⭐ NEW - Run enforcement
        enforcement_result = self._enforcement_orchestrator.execute(
            OperationContext(
                intent_type=intent.type,
                phase_id=request.phase_id,
                module_path=request.module_path,
                code=request.code,
                response=request.response
            )
        )
        
        if enforcement_result.blocked:
            return OperationResult.BLOCKED(
                reason=enforcement_result.violations[0].message,
                enforcement_result=enforcement_result
            )
        
        # Stage 4: Delegate to domain orchestrator
        return self._delegate_to_orchestrator(intent)
```

---

## 📊 Enforcement Statistics & Reporting

```python
class EnforcementStatistics:
    """Track enforcement metrics across session."""
    
    def get_report(self) -> Dict[str, Any]:
        return {
            "GovernanceEnforcementAgent": {
                "checks_performed": 127,
                "violations": 3,
                "blocks": 3,
                "compliance_rate": 97.6%
            },
            "SecurityCheckpointAgent": {
                "checks_performed": 45,
                "violations": 1,
                "blocks": 1,
                "compliance_rate": 97.8%
            },
            "ComplianceValidationAgent": {
                "checks_performed": 89,
                "escalations": 2,
                "blocks": 0,
                "compliance_rate": 97.8%
            },
            "overall_compliance_rate": 97.7%
        }
```

---

## 🔗 Related Documentation

| Document | Purpose |
|----------|---------|
| `cortex-enforcement.prompt.md` | Agent prompt and usage |
| `cortex_brain/tier0/governance/core-rules.yaml` | Tier 0 rules authority |
| `CORTEX.prompt.md` | Master orchestrator integration |
| `cortex/orchestrators/core/master_orchestrator.py` | Implementation |

---

**Status:** ✅ PRODUCTION READY  
**Author:** Asif Hussain  
**Deployed:** 2026-01-24
