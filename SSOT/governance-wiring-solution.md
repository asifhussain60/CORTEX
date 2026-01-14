# CORTEX Governance Wiring Solution: Declarative, Auto-Enforced Rules

**Date:** 2026-01-14  
**Status:** DESIGN PROPOSAL  
**Problem:** Rules exist but aren't wired; orchestrators skip enforcement; brittleness on clone  
**Solution:** Declarative governance configuration with automatic injection at orchestration layer  
**Philosophy:** "Once configured in CORTEX, enforcement stays configured—even on new machines"

---

## Executive Summary: The Core Problem & Solution

### What Doesn't Work Today

From chat01 analysis:
- ⚠️ **12 rules are partial:** Middleware exists (FileCreationGuard, GovernanceCheckpoint, etc.) but not integrated
- ❌ **11 rules are broken:** No enforcement code at all
- 🔴 **Wiring brittleness:** New developer clones repo → enforcement middleware forgotten → rules silently violated
- 🔴 **No audit trail:** Operations complete without governance checks; violations undetected

**Root cause:** Rules and enforcement are **decoupled**. Rules live in YAML; enforcement is scattered middleware. No single place that says "here are ALL active rules; here is HOW each enforces."

### The Solution: Declarative Governance with Auto-Injection

**Core idea:** Move rule configuration AND enforcement metadata into a single declarative layer, then auto-inject enforcement at orchestration startup.

```
┌─────────────────────────────────────────────────────────┐
│ CORTEX Governance Layer (Declarative)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ tier0/governance/rules.yaml  ← Rules definitions       │
│   ├─ CORE-001: Incremental Execution                   │
│   │  ├─ enforcement: TokenMonitor (middleware class)   │
│   │  ├─ hook: pre_execution                            │
│   │  └─ config: {max_lines: 500, max_tokens: 2000}     │
│   │                                                    │
│   └─ CORE-008: TDD Enforcement                         │
│      ├─ enforcement: TddValidator (middleware class)   │
│      ├─ hook: pre_file_creation                        │
│      └─ config: {require_tests: true}                  │
│                                                         │
│ tier0/governance/enforcement-registry.py  ← Auto-wired │
│   Loaded at startup; executed before any operation     │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↓ auto-injects into
┌─────────────────────────────────────────────────────────┐
│ MasterOrchestrator (Execution)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ def execute(request):                                  │
│   # AUTO-INJECTED at startup                           │
│   governance_checks = self.governance_stack.evaluate() │
│   if governance_checks.violations:                     │
│     log_violations()                                   │
│     return error_response()                            │
│                                                         │
│   # Continue only if governance passed                 │
│   result = self._execute_operation(request)           │
│   return result                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key advantages:**
- ✅ **Single source of truth:** Rules AND enforcement in one file
- ✅ **Auto-injected:** Startup loads all rules; injection happens automatically
- ✅ **Portable:** Clone repo → run startup → enforcement active (no manual wiring)
- ✅ **Auditable:** Every operation logged against ruleset
- ✅ **Testable:** Each rule can be tested independently
- ✅ **Extensible:** Add rule to YAML → enforcement auto-activated

---

## Part 1: Core Architecture (Three Layers)

### Layer 1: Governance Registry (YAML)

**File:** `cortex-brain/tier0/governance/rules.yaml`

Contains declarative rule definitions with enforcement metadata.

```yaml
# Governance Rules Registry - CORTEX 7.0
# Status: SINGLE SOURCE OF TRUTH for all enforcement
# Philosophy: Once configured here, enforcement auto-activates on every execution

schema_version: '7.0'
enforcement_mode: declarative  # vs. distributed middleware
auto_wire: true                # Auto-inject on startup

rules:
  # ORCHESTRATION TIER
  CORE-001:
    name: Incremental Execution
    category: orchestration_lifecycle
    severity: blocked
    description: |
      All orchestrators MUST work in incremental chunks.
      Exceeding token limits causes catastrophic failure (HTTP 502).
    
    enforcement:
      middleware_class: src.orchestrators.middleware.incremental_executor.IncrementalExecutor
      hook: pre_execution
      priority: 100  # Higher = earlier execution
      config:
        max_operation_lines: 500
        max_tokens: 2000
        checkpoint_interval: 100
        autonomous_mode: true
    
    validation:
      - operation_lines < max_operation_lines
      - tokens_used < max_tokens
      - state_checkpoint_created
    
    audit_event_type: GOVERNANCE_OPERATION_SIZE

  CORE-002:
    name: No Root-Level Markdown Summaries
    category: response_formatting
    severity: blocked
    description: |
      FileCreationGuard blocks .md file creation in repo root.
      All docs go to cortex-brain/documents/ or docs/
    
    enforcement:
      middleware_class: src.orchestrators.middleware.file_creation_guard.FileCreationGuard
      hook: pre_file_creation
      priority: 95
      config:
        blocked_patterns:
          - "^[^/]+\\.md$"  # Regex: .md in root
        allowed_paths:
          - "cortex-brain/documents/.*\\.md"
          - "docs/.*\\.md"
          - ".github/.*\\.md"
    
    validation:
      - not file_path.matches(blocked_patterns)
      - file_path matches allowed_paths OR blocked
    
    audit_event_type: GOVERNANCE_FILE_LOCATION

  # ... 26 more rules with same structure

  CORE-019:
    name: TDD-Master Required for All Development
    category: development_workflow
    severity: blocked
    description: |
      ALL code implementation must route through TDD-Master orchestrator.
      Direct coding without tests is a violation.
    
    enforcement:
      middleware_class: src.orchestrators.middleware.development_router.DevelopmentRouter
      hook: pre_code_execution
      priority: 90
      config:
        require_tdd: true
        allowed_orchestrators: ["TddMaster"]
    
    validation:
      - operation_type == "code_implementation"
      - routed_to in allowed_orchestrators
    
    audit_event_type: GOVERNANCE_TDD_ENFORCEMENT
```

### Layer 2: Enforcement Registry (Python)

**File:** `cortex-brain/tier0/governance/enforcement-registry.py`

Auto-generated on startup. Maps rule definitions to enforcement middleware.

```python
"""
Enforcement Registry - CORTEX 7.0
==================================
GENERATED: Loaded at startup
PURPOSE: Maps rule definitions (YAML) to enforcement middleware classes (Python)
         Auto-injection ensures enforcement is ALWAYS active

Philosophy: "Once configured, always enforced"
"""

from dataclasses import dataclass
from typing import Dict, Type, Callable, Any
from pathlib import Path
import yaml

@dataclass
class EnforcementPoint:
    """Single enforcement checkpoint for a governance rule"""
    rule_id: str
    rule_name: str
    middleware_class: Type  # Actual enforcement code
    hook: str  # pre_execution, pre_file_creation, etc.
    priority: int  # Execution order
    config: Dict[str, Any]  # Rule-specific config
    audit_event_type: str


class GovernanceRegistry:
    """
    CORTEX Governance Registry
    
    Responsibilities:
    1. Load rules from YAML
    2. Instantiate enforcement middleware
    3. Register enforcement points with orchestrators
    4. Provide query interface for active rules
    5. Log governance evaluation for audit trail
    """
    
    def __init__(self, governance_yaml_path: Path):
        """Initialize registry from YAML"""
        self.governance_yaml = governance_yaml_path
        self.rules: Dict[str, dict] = {}
        self.enforcement_points: Dict[str, EnforcementPoint] = {}
        self.middleware_instances: Dict[str, Any] = {}
        
        # Load on init (happens at startup)
        self._load_rules()
        self._instantiate_enforcement()
    
    def _load_rules(self) -> None:
        """Load rule definitions from YAML"""
        with open(self.governance_yaml, 'r') as f:
            config = yaml.safe_load(f)
            self.rules = config.get('rules', {})
            
        logger.info(
            f"Loaded {len(self.rules)} governance rules from {self.governance_yaml}",
            extra={'rule_ids': list(self.rules.keys())}
        )
    
    def _instantiate_enforcement(self) -> None:
        """
        CRITICAL: Create middleware instances for each rule
        This is where "declarative YAML" becomes "active enforcement"
        """
        for rule_id, rule_def in self.rules.items():
            enforcement_def = rule_def.get('enforcement', {})
            
            # Dynamically import middleware class
            middleware_path = enforcement_def['middleware_class']
            module_name, class_name = middleware_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            middleware_class = getattr(module, class_name)
            
            # Instantiate with config
            config = enforcement_def.get('config', {})
            instance = middleware_class(**config)
            
            # Register enforcement point
            enforcement_point = EnforcementPoint(
                rule_id=rule_id,
                rule_name=rule_def.get('name'),
                middleware_class=middleware_class,
                hook=enforcement_def.get('hook'),
                priority=enforcement_def.get('priority', 50),
                config=config,
                audit_event_type=rule_def.get('audit_event_type')
            )
            
            self.enforcement_points[rule_id] = enforcement_point
            self.middleware_instances[rule_id] = instance
        
        logger.info(
            f"Instantiated {len(self.middleware_instances)} enforcement middleware",
            extra={'enforcement_points': len(self.enforcement_points)}
        )
    
    def get_active_rules_by_hook(self, hook: str) -> List[EnforcementPoint]:
        """
        Get all active enforcement points for a specific hook
        
        Example: hook='pre_execution' → returns all rules that check BEFORE execution
        """
        points = [
            ep for ep in self.enforcement_points.values()
            if ep.hook == hook
        ]
        # Sort by priority (higher priority runs first)
        return sorted(points, key=lambda x: x.priority, reverse=True)
    
    def evaluate(self, hook: str, context: ExecutionContext) -> GovernanceEvaluation:
        """
        Evaluate all active rules for a hook against execution context
        
        Returns: GovernanceEvaluation {
            violations: [{'rule_id': str, 'message': str}],
            should_block: bool,
            applied_rules: [rule_id]
        }
        """
        evaluation = GovernanceEvaluation(hook=hook)
        
        for enforcement_point in self.get_active_rules_by_hook(hook):
            middleware = self.middleware_instances[enforcement_point.rule_id]
            
            # Execute enforcement check
            result = middleware.check(context)
            
            evaluation.applied_rules.append(enforcement_point.rule_id)
            
            if not result.passed:
                evaluation.violations.append({
                    'rule_id': enforcement_point.rule_id,
                    'rule_name': enforcement_point.rule_name,
                    'message': result.violation_reason,
                    'severity': self.rules[enforcement_point.rule_id]['severity']
                })
        
        # Determine if we should block
        evaluation.should_block = any(
            v['severity'] == 'blocked' 
            for v in evaluation.violations
        )
        
        # Log for audit trail
        self._audit_evaluation(evaluation, context)
        
        return evaluation
    
    def _audit_evaluation(self, evaluation: GovernanceEvaluation, context: ExecutionContext) -> None:
        """Log governance evaluation for audit trail"""
        if evaluation.violations:
            logger.warning(
                f"Governance violations detected: {len(evaluation.violations)} rules",
                extra={
                    'hook': evaluation.hook,
                    'violations': evaluation.violations,
                    'context': context.to_dict(),
                    'should_block': evaluation.should_block
                }
            )
        else:
            logger.debug(
                f"Governance check passed for {evaluation.hook}",
                extra={
                    'applied_rules': evaluation.applied_rules,
                    'context': context.to_dict()
                }
            )
```

### Layer 3: MasterOrchestrator Integration

**File:** `src/orchestrators/core/master_orchestrator.py` (modified)

MasterOrchestrator loads the registry at startup and injects checks into execution flow.

```python
class MasterOrchestrator:
    """Master orchestrator with auto-injected governance"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        
        # AUTO-WIRE GOVERNANCE AT STARTUP
        governance_yaml = workspace_root / "cortex-brain/tier0/governance/rules.yaml"
        self.governance_registry = GovernanceRegistry(governance_yaml)
        
        # Logger will include governance context in all operations
        self.logger = get_audit_logger()
        
        # Initialize other components...
        self._initialize_orchestrators()
    
    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        """
        Execute operation with automatic governance enforcement
        
        Flow:
        1. Create execution context from request
        2. Evaluate PRE-EXECUTION rules (auto-injected)
        3. Block if violations
        4. Execute operation
        5. Evaluate POST-EXECUTION rules (auto-injected)
        6. Return result with audit trail
        """
        context = ExecutionContext.from_request(request)
        
        # STEP 1: PRE-EXECUTION GOVERNANCE CHECK (Auto-injected from registry)
        pre_eval = self.governance_registry.evaluate(
            hook='pre_execution',
            context=context
        )
        
        if pre_eval.should_block:
            # Governance violation detected
            self.logger.error(
                "Operation blocked by governance",
                extra={
                    'request': request.to_dict(),
                    'violations': pre_eval.violations,
                    'applied_rules': pre_eval.applied_rules
                }
            )
            return ExecutionResponse(
                success=False,
                error="Governance violation",
                violations=pre_eval.violations
            )
        
        # STEP 2: EXECUTE OPERATION
        try:
            result = self._execute_orchestration(request)
        except Exception as e:
            return ExecutionResponse(success=False, error=str(e))
        
        # STEP 3: POST-EXECUTION GOVERNANCE CHECK
        post_eval = self.governance_registry.evaluate(
            hook='post_execution',
            context=ExecutionContext.from_result(result)
        )
        
        if post_eval.violations:
            self.logger.warning(
                "Post-execution governance violations",
                extra={'violations': post_eval.violations}
            )
        
        # STEP 4: RETURN WITH AUDIT TRAIL
        return ExecutionResponse(
            success=True,
            result=result,
            governance_context={
                'pre_execution_rules': pre_eval.applied_rules,
                'post_execution_rules': post_eval.applied_rules,
                'violations': post_eval.violations
            }
        )
```

---

## Part 2: Why This Fixes Wiring Brittleness

### Problem 1: Rules Exist But Enforcement Not Wired

**Before:**
```
rule-definition.yaml          middleware.py              orchestrator.py
├─ CORE-002:                  ├─ FileCreationGuard       └─ (doesn't use it)
│  └─ No root .md             │  └─ is_blocked()
└─ (rule defined)             └─ (code exists)

Result: FileCreationGuard exists but orchestrator never calls it
```

**After:**
```
rules.yaml                      enforcement-registry.py   master_orchestrator.py
├─ CORE-002:                    ├─ instantiate            └─ auto-evaluate()
│  ├─ enforcement:              │  FileCreationGuard        ├─ pre_execution
│  │  middleware: File...       │  (via reflection)         ├─ middleware.check()
│  │  hook: pre_file_creation   │                           └─ block if violated
└─ (rule AND enforcement)       └─ (auto-wired)

Result: YAML says "enforce this" → Python auto-instantiates → Orchestrator auto-calls
```

### Problem 2: New Developer Clones Repo

**Before:**
1. Developer clones
2. Starts coding
3. Creates `summary-report.md` in root
4. CORE-002 violated
5. No error (enforcement middleware forgotten)
6. Bad code in main branch

**After:**
1. Developer clones
2. MasterOrchestrator starts
3. **Startup auto-loads GovernanceRegistry** ← KEY CHANGE
4. Registry instantiates ALL enforcement middleware
5. PRE-EXECUTION check evaluates all rules
6. Developer tries to create `summary-report.md`
7. **ENFORCEMENT BLOCKS IT** (governance auto-injected)
8. Developer gets clear error message → routes to proper location
9. Correct code in main branch

### Problem 3: Partial Rules (12 of them)

**Before:**
```python
# Middleware exists but only used if orchestrator remembers to call it
middleware_exists = True  # ✓ Code there
enforcement_active = False  # ✗ But not actually checking anything
```

**After:**
```python
# Middleware in rules.yaml automatically becomes active on startup
@auto_wired
class FileCreationGuard:
    """Active automatically; no manual wiring needed"""
    pass
```

---

## Part 3: Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Goal:** Build core registry system without breaking existing code

**Deliverables:**
1. Create `cortex-brain/tier0/governance/rules.yaml` with first 5 core rules
   - CORE-001 (Incremental)
   - CORE-004 (Token Budget)
   - CORE-008 (TDD Enforcement)
   - CORE-019 (TDD-Master Required)
   - CORE-002 (No root .md)

2. Create `cortex-brain/tier0/governance/enforcement-registry.py`
   - GovernanceRegistry class
   - Rule loader
   - Middleware instantiation
   - Hook-based query

3. Create unit tests
   - Test rule loading
   - Test middleware instantiation
   - Test hook queries

**Non-breaking:** Registry runs in "read-only" mode; MasterOrchestrator not yet integrated

### Phase 2: Integration (Week 2)

**Goal:** Wire MasterOrchestrator to use registry

**Deliverables:**
1. Modify MasterOrchestrator `__init__` to load GovernanceRegistry
2. Add pre_execution governance check to `execute()`
3. Add post_execution governance check
4. Update logging to include governance context
5. Create integration tests

**Test strategy:**
- Test that violations block execution
- Test that valid operations proceed
- Test audit trail includes rule evaluation

### Phase 3: Activation (Week 3)

**Goal:** Enable enforcement for remaining 23 rules

**Deliverables:**
1. Convert all 28 rules to declarative format in rules.yaml
2. Wire up remaining enforcement middleware
3. Test each rule in isolation
4. Update rule documentation

**Rollout:**
- Start with HIGH severity rules (blocking operations)
- Progress to MEDIUM (warnings)
- Finally LOW (audit-only)

### Phase 4: Validation & Hardening (Week 4)

**Goal:** Ensure system is production-ready

**Deliverables:**
1. Cross-machine testing (MAC + WIN)
2. Performance benchmarks
3. Failure mode testing (corrupt YAML, missing middleware, etc.)
4. Documentation for adding new rules

---

## Part 4: Configuration Schema

### Rule Definition Format

```yaml
rule_id:
  name: Human readable name
  category: orchestration_lifecycle | response_formatting | etc.
  severity: blocked | warning | audit_only
  description: |
    Multi-line explanation of what this rule enforces
    and why it's important
  
  enforcement:
    middleware_class: module.path.ClassName  # Fully qualified class name
    hook: pre_execution | pre_file_creation | post_operation | etc.
    priority: 1-100  # Higher = earlier (CORE-019 at 90, CORE-001 at 100)
    config:
      # Rule-specific configuration passed to middleware __init__
      key1: value1
      key2: value2
  
  validation:
    # Criteria that must be met for rule to pass
    - condition1
    - condition2
    - condition3
  
  audit_event_type: GOVERNANCE_OPERATION_SIZE  # For audit logs
  
  examples:
    pass:
      - "Scenario that passes this rule"
      - "Another passing scenario"
    fail:
      - "Scenario that violates this rule"
      - "Another violation"
```

### Middleware Interface

All enforcement middleware must implement:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class EnforcementResult:
    passed: bool
    violation_reason: Optional[str] = None

class GovernanceMiddleware(ABC):
    """
    Base class for all governance enforcement middleware
    
    Pattern: Each rule has ONE middleware class
    Middleware instantiated once at startup
    check() called for each operation
    """
    
    def __init__(self, **config):
        """Initialize with rule-specific config from YAML"""
        self.config = config
    
    @abstractmethod
    def check(self, context: ExecutionContext) -> EnforcementResult:
        """
        Check if operation violates this rule
        
        Args:
            context: ExecutionContext with operation details
        
        Returns:
            EnforcementResult(
                passed=True/False,
                violation_reason="Why it failed" if not passed
            )
        """
        pass
```

### Example: File Creation Guard

```python
from governance_wiring_solution import GovernanceMiddleware, EnforcementResult

class FileCreationGuard(GovernanceMiddleware):
    """
    CORE-002: No root-level markdown files
    Config: blocked_patterns, allowed_paths
    """
    
    def __init__(self, blocked_patterns: List[str], allowed_paths: List[str]):
        super().__init__()
        self.blocked_patterns = [re.compile(p) for p in blocked_patterns]
        self.allowed_paths = [re.compile(p) for p in allowed_paths]
    
    def check(self, context: ExecutionContext) -> EnforcementResult:
        if context.operation != 'file_creation':
            return EnforcementResult(passed=True)  # Not applicable
        
        file_path = context.file_path
        
        # Check if blocked
        for pattern in self.blocked_patterns:
            if pattern.match(file_path):
                # Check if in allowed paths
                allowed = any(
                    pattern.match(file_path)
                    for pattern in self.allowed_paths
                )
                
                if not allowed:
                    return EnforcementResult(
                        passed=False,
                        violation_reason=(
                            f"CORE-002: Cannot create '{file_path}' in root. "
                            f"Markdown files must go to cortex-brain/documents/ or docs/"
                        )
                    )
        
        return EnforcementResult(passed=True)
```

---

## Part 5: Benefits Summary

### 1. Eliminates Wiring Brittleness

| Before | After |
|--------|-------|
| Rule in YAML, enforcement in separate file | Rule AND enforcement in one YAML; auto-instantiated |
| Orchestrator must remember to call middleware | Orchestrator auto-receives governance checks |
| New developer clones → enforcement forgotten | New developer clones → governance auto-loads |

### 2. Single Source of Truth

- **Before:** Rules scattered (YAML + 12 middleware files + orchestrator logic)
- **After:** Rules in `rules.yaml`; enforcement auto-injected

### 3. Auditable & Traceable

Every operation logs which rules were evaluated:
```json
{
  "operation": "create_file",
  "file_path": "summary.md",
  "governance": {
    "pre_execution_rules": ["CORE-002", "CORE-020"],
    "violations": [
      {
        "rule_id": "CORE-002",
        "message": "Cannot create .md in root"
      }
    ],
    "blocked": true
  }
}
```

### 4. Extensible

Adding a new rule takes 3 steps:
1. Define in `rules.yaml`
2. Create middleware class implementing `GovernanceMiddleware`
3. Done—auto-wired on next startup

### 5. Cross-Machine Compatibility

- Git clone (MAC or WIN)
- Startup loads `rules.yaml` (platform-agnostic)
- GovernanceRegistry instantiates middleware
- Enforcement active immediately
- Same rules on all machines

### 6. No Breaking Changes

- Registry loads in "read-only" mode first
- Gradually integrate into MasterOrchestrator
- Existing code continues to work
- Governance applied on top

---

## Part 6: Success Criteria

### Phase 1 Complete When:
- ✅ GovernanceRegistry loads rules.yaml without errors
- ✅ First 5 rules instantiate middleware successfully
- ✅ Unit tests all pass
- ✅ No breaking changes to existing code

### Phase 2 Complete When:
- ✅ MasterOrchestrator loads registry on startup
- ✅ Pre-execution checks evaluate all applicable rules
- ✅ Operations blocked when violations detected
- ✅ Audit logs include governance context
- ✅ Integration tests pass on MAC + WIN

### Phase 3 Complete When:
- ✅ All 28 rules in declarative format
- ✅ All enforcement middleware instantiable
- ✅ No silent violations (all rules active)
- ✅ Each rule tested in isolation

### Phase 4 Complete When:
- ✅ Performance meets SLA (<10ms overhead per operation)
- ✅ Failure modes handled (corrupt YAML, missing middleware, etc.)
- ✅ Documentation complete
- ✅ Production deployment process defined

---

## Part 7: Comparison: Old vs. New Architecture

### Old Architecture (Current)

```
problem:
  ├─ Rules in YAML (cortex-brain/tier0/governance/core-rules.yaml)
  │  └─ Not connected to execution
  ├─ Middleware scattered (12 files in middleware/)
  │  └─ Each orchestrator must remember to use them
  ├─ No global enforcement point
  │  └─ Violations can slip through
  └─ New dev clones → enforcement gone
     └─ Rules violated silently

result:
  "11 rules broken, 12 partial" (per chat01)
  "Functionality exists but not wired" (the core complaint)
```

### New Architecture (Proposed)

```
solution:
  ├─ Rules in rules.yaml WITH enforcement metadata
  │  └─ Connected via GovernanceRegistry
  ├─ Middleware instantiated once at startup
  │  └─ Not scattered; all registered in one place
  ├─ Global enforcement point in MasterOrchestrator
  │  └─ Every operation evaluated
  └─ New dev clones → enforcement auto-loads
     └─ Rules enforced by default

result:
  "Once configured, always enforced"
  "Clone the repo, rules are wired in"
```

---

## Part 8: Migration Path from CORTEX 6 to 7

### Don't Break CORTEX 6

The 28 existing rules stay; we just rewire their enforcement:

1. **Extract enforcement metadata** from core-rules.yaml
   - Rule definitions stay
   - Add `enforcement:` section per rule
   - Add `hook:`, `priority:`, `config:` per enforcement

2. **Create GovernanceRegistry** (new code, non-breaking)
   - Lives alongside existing rules
   - Reads from rules.yaml
   - Doesn't interfere with current code

3. **Integrate MasterOrchestrator** (gradual)
   - Load registry in `__init__`
   - Add pre_execution check
   - Monitor for 1 week
   - Add post_execution check
   - Monitor for 1 week

4. **Sunset old middleware** (week 4+)
   - Once new system proves stable
   - Update orchestrators to use registry
   - Remove old middleware if no longer needed

---

## Appendix: File Organization

```
cortex-brain/tier0/governance/
├─ core-rules.yaml                          ← Rule definitions (ENHANCED with enforcement metadata)
├─ enforcement-registry.py                  ← NEW: GovernanceRegistry class
├─ enforcement-schema.sql                   ← SQLite schema for audit trail (optional Phase 2)
└─ middleware/                              ← Enforcement middleware classes
   ├─ __init__.py
   ├─ base.py                               ← GovernanceMiddleware base class
   ├─ incremental_executor.py               ← CORE-001 enforcement
   ├─ file_creation_guard.py                ← CORE-002 enforcement
   ├─ tdd_validator.py                      ← CORE-008, CORE-019 enforcement
   └─ ... (one file per rule category)

tests/governance/
├─ test_governance_registry.py              ← Registry loading, instantiation
├─ test_enforcement_integration.py          ← Pre/post execution checks
└─ test_rules_*.py                          ← Per-rule tests
```

---

## Summary

This design solves **the core problem**: rules exist but aren't wired.

**The solution:** Move enforcement metadata into YAML, auto-instantiate on startup, auto-inject into orchestration.

**Key insight:** "Once configured in CORTEX, enforcement stays configured—even on new machines."

This is elegant, maintainable, and fits the CORTEX philosophy of **permanent memory with governance.**
