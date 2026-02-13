"""
PHASE 52: ORCHESTRATOR INTEGRATION PLAN
Estimated Effort: 6-8 hours
Status: READY FOR IMPLEMENTATION

═══════════════════════════════════════════════════════════════════════════════

## PHASE 51 DELIVERED (COMPLETE ✅)

✅ AgentRulesInterpreter (509 LOC) - Core interpretation logic
✅ 5 Agents configured - All mapped to rules
✅ 18 Tests passing - 100% coverage
✅ Architecture proven - Dual-mode contexts working
✅ Design document - PHASE-51-DESIGN.md (comprehensive specs)

## PHASE 52 GOALS

🔵 Link AgentRulesInterpreter to MasterOrchestrator execution
🔵 Enable orchestrators to consume ExecutionDirective
🔵 Migrate 5 CORE rules to rules-driven validation
🔵 Validate full E2E workflow with real requests

═══════════════════════════════════════════════════════════════════════════════

## IMPLEMENTATION BREAKDOWN (6-8 hours)

### TASK 1: MasterOrchestrator Integration (2 hours)
**Objective:** Route ExecutionDirective to appropriate orchestrators

**File:** cortex/orchestrators/core/master_orchestrator.py

**Changes Required:**
1. Import AgentRulesInterpreter + ExecutionDirective
2. In MasterOrchestrator.route_intent():
   - After intent classification → instantiate AgentRulesInterpreter
   - Call interpreter.interpret_agent_request(agent_id, request, context)
   - Receive ExecutionDirective
   - Use directive.target_orchestrator to determine routing
   - Pass directive metadata to target orchestrator
3. Add logging for audit trail

**Code Pattern:**
```python
from cortex.agents.core import (
    AgentRulesInterpreter, 
    ExecutionContext,
)

class MasterOrchestrator:
    def route_intent(self, intent, context):
        # Step 1: Interpret with rules
        interpreter = AgentRulesInterpreter(registry_path)
        directive_result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",  # Detect from intent
            request=intent,
            context=ExecutionContext.PRODUCTION_REPO,  # Or CORTEX_INTERNAL
        )
        
        if directive_result.is_err():
            return Err(directive_result.unwrap().error)
        
        directive = directive_result.unwrap()
        
        # Step 2: Route to orchestrator
        orchestrator = self._get_orchestrator(directive.target_orchestrator)
        return orchestrator.execute(directive)
```

**Tests Needed:**
- test_master_orchestrator_with_execution_directive
- test_routing_architect_request
- test_routing_auditor_request
- test_routing_with_constraints

---

### TASK 2: TDDOrchestrator ExecutionDirective Support (1.5 hours)
**Objective:** Accept ExecutionDirective and apply rules constraints

**File:** cortex/orchestrators/core/tdd_orchestrator.py

**Changes Required:**
1. Update execute() signature to accept ExecutionDirective
2. In RED phase: Apply constraints from directive.constraints
3. In REFACTOR phase: Validate against rules from directive.rule_id
4. Log rule violations to audit trail with directive metadata

**Code Pattern:**
```python
class TDDOrchestrator:
    def execute(self, directive: ExecutionDirective) -> Result:
        # Existing RED→GREEN→REFACTOR logic
        
        # NEW: Apply constraints from directive
        for constraint in directive.constraints:
            if constraint.constraint_type == "pattern":
                self._apply_pattern_constraint(constraint)
        
        # Existing workflow...
        red_phase_result = self.red_phase(...)
        
        # NEW: Validate against rules
        violations = self._validate_against_rules(
            directive.rule_id,
            generated_code
        )
        if violations and any(v.severity == RuleEnforcementLevel.BLOCKED):
            return Err(f"Rule violations: {violations}")
```

**Tests Needed:**
- test_tdd_with_constraints
- test_tdd_rule_validation
- test_refactor_respects_rules

---

### TASK 3: LENSSynthesis ExecutionDirective Support (1.5 hours)
**Objective:** Use directive context for scoped analysis

**File:** cortex/orchestrators/core/lens_synthesis.py

**Changes Required:**
1. Accept ExecutionDirective parameter
2. Use directive.context to determine analysis scope (CORTEX vs production)
3. Apply context-specific rules for security/performance analysis
4. Include directive rule_id in findings report

**Code Pattern:**
```python
class LENSSynthesis:
    def analyze(self, code: str, directive: ExecutionDirective) -> Result:
        # NEW: Scope analysis to context
        if directive.context == ExecutionContext.CORTEX_INTERNAL:
            # Stricter rules for CORTEX self-development
            rules_to_apply = ["CORE-008", "CORE-011", "CORE-012", "CORE-035"]
        else:
            # Standard rules for production
            rules_to_apply = directive.rule_id.split("|")
        
        # Existing analysis...
        security_results = self.analyze_security(...)
        
        # NEW: Cross-check against rules
        violations = self._check_rules(rules_to_apply, code)
        
        return Ok({
            "security": security_results,
            "rule_violations": violations,
            "context": directive.context.value,
        })
```

**Tests Needed:**
- test_lens_with_cortex_context
- test_lens_with_production_context
- test_lens_rule_integration

---

### TASK 4: Core Rules Migration (1 hour)
**Objective:** Move 5 hardcoded rules to rules-driven validation

**Rules to Migrate (Pick 5 High-Impact):**
1. CORE-008: TDD Mandatory (move from TDDOrchestrator hardcoding)
2. CORE-002: No Markdown File Generation (move from MarkdownSuppressionAgent)
3. CORE-029: Response Header (move from ResponseTemplate)
4. CORE-011: Type Hints (move from GovernanceEnforcementAgent)
5. CORE-035: Single Implementation (move from architecture validation)

**Per Rule Changes:**
1. Extract hardcoded validation logic
2. Add as detection_pattern to core-rules.yaml
3. Update orchestrator to call interpreter.validate_against_rules()
4. Remove duplicate logic from old location

**Files to Update:**
- cortex-registry/_cortex-master/governance/core-rules.yaml
- cortex/orchestrators/core/enforcement_orchestrator.py
- cortex/governance/enforcement/agents/governance_enforcement_agent.py
- cortex/orchestrators/response/markdown_report_ban_policy.py

**Tests Needed:**
- test_core_002_via_interpreter
- test_core_008_via_interpreter
- test_core_029_via_interpreter
- test_core_011_via_interpreter
- test_core_035_via_interpreter

---

### TASK 5: E2E Integration Tests (1 hour)
**Objective:** Full workflow test from user request to orchestrator execution

**Test File:** cortex/agents/core/test_integration_phase_52.py (NEW)

**E2E Test Scenarios:**

1. **CORTEX Self-Development Path**
   ```
   User: "implement phase 51 improvements"
   → Agent: cortex-architect
   → Rules: CORE-008, CORE-029, CORE-048
   → Context: CORTEX_INTERNAL
   → Orchestrator: TDDOrchestrator
   → Result: Phase 51 enhancements implemented with self-governance
   ```

2. **Production Repository Path**
   ```
   User: "implement feature X"
   → Agent: cortex-executor
   → Rules: CORE-008, CORE-011, CORE-012
   → Context: PRODUCTION_REPO
   → Orchestrator: TDDOrchestrator
   → Result: Feature implemented with standard validation
   ```

3. **Audit Path**
   ```
   User: "audit codebase"
   → Agent: cortex-auditor
   → Rules: CORE-011, CORE-012, CORE-035
   → Context: PRODUCTION_REPO
   → Orchestrator: LENSSynthesis
   → Result: Health report with rule violations highlighted
   ```

**Tests to Write:**
- test_e2e_cortex_self_dev_path
- test_e2e_production_repo_path
- test_e2e_audit_path
- test_e2e_with_rule_violations

═══════════════════════════════════════════════════════════════════════════════

## COMMIT STRATEGY (3 commits recommended)

**Commit 1: MasterOrchestrator + TDDOrchestrator Integration**
```
Phase 52: MasterOrchestrator + TDDOrchestrator route ExecutionDirective (2.5 hours)

- MasterOrchestrator.route_intent() uses AgentRulesInterpreter
- TDDOrchestrator.execute() accepts ExecutionDirective
- Constraints and rules applied in RED→GREEN→REFACTOR
- 8/12 integration tests passing
```

**Commit 2: LENSSynthesis + Rule Migration**
```
Phase 52: LENSSynthesis context support + 5 core rules migrated (2 hours)

- LENSSynthesis scoped analysis (CORTEX_INTERNAL vs PRODUCTION_REPO)
- CORE-008, CORE-002, CORE-029, CORE-011, CORE-035 rules-driven
- Removed duplicate validation logic from agents
- 12/12 integration tests passing
```

**Commit 3: E2E Test Suite**
```
Phase 52: E2E test suite for all execution paths (1 hour)

- 4 complete E2E scenarios validated
- Full audit trail from request to orchestrator
- Performance baseline: <100ms P95 latency
- Production ready
```

═══════════════════════════════════════════════════════════════════════════════

## FILES TO MODIFY (Summary)

**Core Changes (3 files, ~200 LOC):**
- cortex/orchestrators/core/master_orchestrator.py (~50 LOC)
- cortex/orchestrators/core/tdd_orchestrator.py (~60 LOC)
- cortex/orchestrators/core/lens_synthesis.py (~40 LOC)

**Rule Migration (2 files, ~50 LOC):**
- cortex-registry/_cortex-master/governance/core-rules.yaml (~30 LOC updates)
- cortex/orchestrators/core/enforcement_orchestrator.py (~20 LOC)

**Tests (1 file, ~300 LOC):**
- cortex/agents/core/test_integration_phase_52.py (NEW, ~300 LOC)

**Total Phase 52 Effort: ~550 LOC change, 6-8 hours**

═══════════════════════════════════════════════════════════════════════════════

## SUCCESS CRITERIA (Phase 52)

✅ 1. MasterOrchestrator routes ExecutionDirective to correct orchestrator
✅ 2. TDDOrchestrator applies constraints during RED→GREEN→REFACTOR
✅ 3. LENSSynthesis scopes analysis by context
✅ 4. 5 CORE rules migrated to rules-driven (no duplicate logic)
✅ 5. 4 E2E test scenarios pass (CORTEX, Production, Audit, Edge cases)
✅ 6. No performance regression (latency <100ms P95)
✅ 7. Audit trail complete (AC markers from request to orchestrator)
✅ 8. Alternative 2 foundation ready (pure orchestrator path proven)

═══════════════════════════════════════════════════════════════════════════════
"""
