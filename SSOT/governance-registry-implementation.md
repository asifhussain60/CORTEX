# GovernanceRegistry: Starter Implementation

**Purpose:** Reference implementation to start Phase 1  
**Status:** Ready to code  
**Effort:** 2-3 days for core + 5 rules

---

## File Structure (Phase 1)

```
cortex-brain/tier0/governance/
├─ rules.yaml                           (YAML rule definitions)
├─ enforcement_registry.py               (Core GovernanceRegistry)
├─ enforcement_base.py                   (GovernanceMiddleware base class)
└─ __init__.py

tests/governance/
├─ test_enforcement_registry.py          (Registry loading + instantiation)
├─ test_enforcement_base.py              (Middleware interface)
└─ test_first_five_rules.py              (CORE-001, 004, 002, 008, 019)
```

---

## Step 1: Create `enforcement_base.py` (Base Class)

```python
"""
GovernanceMiddleware Base Class

Purpose: Standard interface for all governance enforcement
All enforcement middleware inherits from this class
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class ExecutionContext:
    """Context about operation being executed"""
    operation: str  # 'file_creation', 'code_execution', 'orchestration', etc.
    user: str = "github-copilot"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    workspace_root: Optional[str] = None
    file_path: Optional[str] = None  # For file operations
    code_lines: Optional[int] = None  # For code operations
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'operation': self.operation,
            'user': self.user,
            'timestamp': self.timestamp.isoformat(),
            'workspace_root': self.workspace_root,
            'file_path': self.file_path,
            'code_lines': self.code_lines,
            'metadata': self.metadata
        }


@dataclass
class EnforcementResult:
    """Result of governance check"""
    passed: bool
    rule_id: Optional[str] = None
    violation_reason: Optional[str] = None
    severity: Optional[str] = None  # 'blocked', 'warning', 'audit_only'
    
    @property
    def should_block(self) -> bool:
        """Determine if operation should be blocked"""
        return (not self.passed) and (self.severity == 'blocked')


class GovernanceMiddleware(ABC):
    """
    Base class for all governance enforcement middleware
    
    Philosophy:
    - Each rule (CORE-001, CORE-002, etc.) has ONE enforcement middleware
    - Middleware is instantiated once at startup (by GovernanceRegistry)
    - check() method called for each operation
    - Simple, testable, repeatable
    
    Example:
        class TokenBudgetEnforcer(GovernanceMiddleware):
            def __init__(self, max_tokens: int = 2000):
                self.max_tokens = max_tokens
            
            def check(self, context: ExecutionContext) -> EnforcementResult:
                if context.operation != 'code_execution':
                    return EnforcementResult(passed=True)
                
                tokens = estimate_tokens(context.code)
                if tokens > self.max_tokens:
                    return EnforcementResult(
                        passed=False,
                        rule_id='CORE-004',
                        violation_reason=f'Token budget exceeded: {tokens} > {self.max_tokens}',
                        severity='blocked'
                    )
                return EnforcementResult(passed=True)
    """
    
    def __init__(self, **config):
        """
        Initialize middleware with configuration from YAML
        
        Args:
            **config: Rule-specific configuration from rules.yaml
        """
        self.config = config
    
    @abstractmethod
    def check(self, context: ExecutionContext) -> EnforcementResult:
        """
        Check if operation violates this rule
        
        Args:
            context: ExecutionContext with operation details
        
        Returns:
            EnforcementResult indicating if check passed/failed
        
        Notes:
            - Return EnforcementResult(passed=True) if rule not applicable
            - Return EnforcementResult(passed=False, ...) if violation detected
            - Set severity to determine if operation should be blocked
        """
        pass
```

---

## Step 2: Create `rules.yaml` (First 5 Rules)

```yaml
# CORTEX 7.0 Governance Rules Registry
# Phase 1: First 5 core rules
# Status: Alpha (read-only, non-blocking)

schema_version: '7.0'
enforcement_mode: declarative
auto_wire: true

metadata:
  created: "2026-01-14"
  phase: 1
  rules_count: 5
  mode: read_only  # Change to active when validated

rules:
  # =========================================================================
  # CORE-001: Incremental Execution
  # =========================================================================
  CORE-001:
    name: Incremental Autonomous Execution
    category: orchestration_lifecycle
    severity: blocked
    description: |
      All orchestrators MUST work in incremental chunks.
      Operations exceeding 500 lines or 2000 tokens risk HTTP 502 errors.
      
      This rule ensures autonomous execution without manual intervention.
    
    enforcement:
      middleware_class: src.orchestrators.middleware.incremental_executor.IncrementalExecutor
      hook: pre_execution
      priority: 100
      config:
        max_operation_lines: 500
        max_tokens: 2000
        checkpoint_enabled: true
        autonomous_mode: true
    
    validation:
      - operation_lines < max_operation_lines
      - estimated_tokens < max_tokens
      - checkpoint_created
    
    examples:
      pass:
        - "Processing 50 files in Phase 1; 50 in Phase 2 (incremental)"
        - "Token usage at 75%; checkpoint and resume"
      fail:
        - "Trying to process all 1000 files in single execution"
        - "Token usage exceeding 2000"
  
  # =========================================================================
  # CORE-002: No Root-Level Markdown
  # =========================================================================
  CORE-002:
    name: No Root-Level Markdown Files
    category: response_formatting
    severity: blocked
    description: |
      .md files cannot be created in repository root.
      All documentation must go to cortex-brain/documents/ or docs/
      
      Prevents repository clutter and enforces organization standards.
    
    enforcement:
      middleware_class: src.orchestrators.middleware.file_creation_guard.FileCreationGuard
      hook: pre_file_creation
      priority: 95
      config:
        blocked_patterns:
          - "^[^/]+\\.md$"
        allowed_paths:
          - "cortex-brain/documents/.*\\.md"
          - "docs/.*\\.md"
          - ".github/.*\\.md"
          - "SSOT/.*\\.md"
    
    validation:
      - file_path matches blocked_patterns → NOT in allowed_paths
    
    examples:
      pass:
        - "Creating cortex-brain/documents/analysis.md"
        - "Creating docs/README.md"
      fail:
        - "Creating summary.md in root"
        - "Creating plan.md in root"
  
  # =========================================================================
  # CORE-004: Token Budget Enforcement
  # =========================================================================
  CORE-004:
    name: Token Budget Enforcement
    category: response_formatting
    severity: blocked
    description: |
      Operations must respect token budget limits.
      Prevent context window exhaustion that causes failures.
      
      Monitoring at:
      1. Pre-execution: Estimate operation size
      2. Runtime: Monitor actual token usage
      3. Post-execution: Log final metrics
    
    enforcement:
      middleware_class: src.utils.token_counter.TokenBudgetMonitor
      hook: pre_execution
      priority: 90
      config:
        token_limit: 2000
        warning_threshold: 0.75
        critical_threshold: 0.95
        include_response: true
    
    validation:
      - estimated_tokens < token_limit
      - warning issued if > warning_threshold
      - operation blocked if > critical_threshold
    
    examples:
      pass:
        - "Operation estimated at 1500 tokens (75% of budget)"
      fail:
        - "Operation estimated at 2500 tokens (exceeds limit)"
  
  # =========================================================================
  # CORE-008: TDD Enforcement
  # =========================================================================
  CORE-008:
    name: Test-Driven Development Required
    category: development_workflow
    severity: blocked
    description: |
      All code must be developed test-first.
      Tests must exist BEFORE implementation.
      
      This rule enforces TDD workflow:
      1. RED: Write failing test
      2. GREEN: Write minimal code to pass
      3. REFACTOR: Improve code
    
    enforcement:
      middleware_class: src.orchestrators.middleware.development_router.TddValidator
      hook: pre_code_execution
      priority: 85
      config:
        require_tests: true
        test_framework: pytest
        coverage_minimum: 0.80
    
    validation:
      - test_file_exists_for_source_file
      - test_file_modified_after_source_file OR no_source_file_yet
      - tests_pass
    
    examples:
      pass:
        - "Created test_feature.py BEFORE feature.py"
        - "All tests passing"
      fail:
        - "Trying to create feature.py without test_feature.py"
        - "Test file exists but hasn't been modified"
  
  # =========================================================================
  # CORE-019: TDD-Master Required
  # =========================================================================
  CORE-019:
    name: All Development Routes Through TDD-Master
    category: orchestration_lifecycle
    severity: blocked
    description: |
      ALL code implementation (planned or unplanned) must route through
      TDD-Master orchestrator.
      
      This prevents:
      - Direct coding without test framework
      - Implementation without architecture review
      - Untested code in production
    
    enforcement:
      middleware_class: src.orchestrators.middleware.development_router.DevelopmentRouter
      hook: pre_code_execution
      priority: 80
      config:
        require_orchestrator: TddMaster
        allowed_alternatives: []  # No bypasses
    
    validation:
      - operation_type == code_implementation
      - routed_to == TddMaster
    
    examples:
      pass:
        - "Implementation request routed to TDD-Master"
        - "User calls 'implement feature X' → auto-routes to TDD-Master"
      fail:
        - "Direct implementation without TDD-Master routing"
```

---

## Step 3: Create `enforcement_registry.py` (Core Class)

```python
"""
GovernanceRegistry - Core Enforcement System

Responsibilities:
1. Load rules from YAML (run once at startup)
2. Instantiate enforcement middleware (auto-injection)
3. Provide query interface (get rules by hook, evaluate context)
4. Log all evaluations (audit trail)
"""

from pathlib import Path
from typing import Dict, List, Optional, Type
import yaml
import importlib
import logging
from dataclasses import dataclass, field

from .enforcement_base import GovernanceMiddleware, ExecutionContext, EnforcementResult


@dataclass
class EnforcementPoint:
    """Metadata about one enforcement checkpoint"""
    rule_id: str
    rule_name: str
    middleware_class: Type  # Actual Python class
    hook: str  # pre_execution, pre_file_creation, etc.
    priority: int  # Higher = earlier
    config: Dict  # Config passed to middleware
    audit_event_type: str


@dataclass
class GovernanceEvaluation:
    """Result of evaluating all rules for a hook"""
    hook: str
    applied_rules: List[str] = field(default_factory=list)
    violations: List[Dict] = field(default_factory=list)
    should_block: bool = False
    timestamp: Optional[str] = None


class GovernanceRegistry:
    """
    Load rules from YAML; auto-instantiate enforcement; provide query interface
    
    Usage:
        registry = GovernanceRegistry(
            governance_yaml=Path("cortex-brain/tier0/governance/rules.yaml"),
            logger=logger
        )
        
        # Before operation
        eval = registry.evaluate(hook='pre_execution', context=ctx)
        if eval.should_block:
            return error_response(eval.violations)
        
        # Execute operation
        ...
        
        # After operation
        eval = registry.evaluate(hook='post_execution', context=ctx)
        if eval.violations:
            log_warnings(eval.violations)
    """
    
    def __init__(self, governance_yaml: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize registry from YAML file
        
        Args:
            governance_yaml: Path to rules.yaml
            logger: Logger instance for audit trail
        """
        self.governance_yaml = governance_yaml
        self.logger = logger or logging.getLogger(__name__)
        
        self.rules: Dict[str, dict] = {}
        self.enforcement_points: Dict[str, EnforcementPoint] = {}
        self.middleware_instances: Dict[str, GovernanceMiddleware] = {}
        
        # Load and initialize
        self._load_rules()
        self._instantiate_enforcement()
    
    def _load_rules(self) -> None:
        """Load rule definitions from YAML"""
        try:
            with open(self.governance_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            self.rules = config.get('rules', {})
            
            self.logger.info(
                f"[GOVERNANCE] Loaded {len(self.rules)} rules from {self.governance_yaml.name}",
                extra={'rule_count': len(self.rules), 'rule_ids': list(self.rules.keys())}
            )
        except FileNotFoundError:
            self.logger.error(f"[GOVERNANCE] rules.yaml not found: {self.governance_yaml}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"[GOVERNANCE] Invalid YAML: {e}")
            raise
    
    def _instantiate_enforcement(self) -> None:
        """
        CRITICAL: Create middleware instances for each rule
        This transforms declarative YAML into active enforcement
        """
        failed_count = 0
        
        for rule_id, rule_def in self.rules.items():
            try:
                enforcement_def = rule_def.get('enforcement', {})
                if not enforcement_def:
                    self.logger.warning(f"[GOVERNANCE] No enforcement defined for {rule_id}")
                    continue
                
                # Dynamically import middleware class
                middleware_path = enforcement_def['middleware_class']
                module_name, class_name = middleware_path.rsplit('.', 1)
                
                try:
                    module = importlib.import_module(module_name)
                    middleware_class = getattr(module, class_name)
                except (ImportError, AttributeError) as e:
                    self.logger.error(
                        f"[GOVERNANCE] Failed to import {middleware_path}: {e}",
                        extra={'rule_id': rule_id}
                    )
                    failed_count += 1
                    continue
                
                # Instantiate with config
                config = enforcement_def.get('config', {})
                try:
                    instance = middleware_class(**config)
                except Exception as e:
                    self.logger.error(
                        f"[GOVERNANCE] Failed to instantiate {middleware_path}: {e}",
                        extra={'rule_id': rule_id, 'config': config}
                    )
                    failed_count += 1
                    continue
                
                # Create enforcement point
                enforcement_point = EnforcementPoint(
                    rule_id=rule_id,
                    rule_name=rule_def.get('name', 'Unknown'),
                    middleware_class=middleware_class,
                    hook=enforcement_def.get('hook'),
                    priority=enforcement_def.get('priority', 50),
                    config=config,
                    audit_event_type=rule_def.get('audit_event_type', 'GOVERNANCE_CHECK')
                )
                
                self.enforcement_points[rule_id] = enforcement_point
                self.middleware_instances[rule_id] = instance
                
                self.logger.debug(
                    f"[GOVERNANCE] Registered {rule_id}",
                    extra={'hook': enforcement_point.hook, 'priority': enforcement_point.priority}
                )
                
            except Exception as e:
                self.logger.error(f"[GOVERNANCE] Unexpected error for {rule_id}: {e}")
                failed_count += 1
        
        success_count = len(self.middleware_instances)
        self.logger.info(
            f"[GOVERNANCE] Instantiation complete: {success_count} success, {failed_count} failed",
            extra={'success': success_count, 'failed': failed_count}
        )
    
    def get_active_rules_by_hook(self, hook: str) -> List[EnforcementPoint]:
        """
        Get all active enforcement points for a specific hook
        Sorted by priority (higher first)
        """
        points = [
            ep for ep in self.enforcement_points.values()
            if ep.hook == hook
        ]
        return sorted(points, key=lambda x: x.priority, reverse=True)
    
    def evaluate(self, hook: str, context: ExecutionContext) -> GovernanceEvaluation:
        """
        Evaluate all active rules for a hook against execution context
        
        Returns:
            GovernanceEvaluation with violations and should_block flag
        """
        evaluation = GovernanceEvaluation(hook=hook)
        
        active_rules = self.get_active_rules_by_hook(hook)
        
        for enforcement_point in active_rules:
            middleware = self.middleware_instances[enforcement_point.rule_id]
            
            try:
                result = middleware.check(context)
                evaluation.applied_rules.append(enforcement_point.rule_id)
                
                if not result.passed:
                    evaluation.violations.append({
                        'rule_id': enforcement_point.rule_id,
                        'rule_name': enforcement_point.rule_name,
                        'message': result.violation_reason or 'Rule violation',
                        'severity': self.rules[enforcement_point.rule_id].get('severity', 'warning')
                    })
            
            except Exception as e:
                self.logger.error(
                    f"[GOVERNANCE] Error checking {enforcement_point.rule_id}: {e}",
                    extra={'rule_id': enforcement_point.rule_id, 'hook': hook}
                )
        
        # Determine if operation should be blocked
        evaluation.should_block = any(
            v['severity'] == 'blocked'
            for v in evaluation.violations
        )
        
        # Log evaluation
        self._log_evaluation(evaluation, context)
        
        return evaluation
    
    def _log_evaluation(self, evaluation: GovernanceEvaluation, context: ExecutionContext) -> None:
        """Log governance evaluation for audit trail"""
        if evaluation.violations:
            self.logger.warning(
                f"[GOVERNANCE] {len(evaluation.violations)} violations in {evaluation.hook}",
                extra={
                    'hook': evaluation.hook,
                    'violations': evaluation.violations,
                    'should_block': evaluation.should_block,
                    'context': context.to_dict()
                }
            )
        else:
            self.logger.debug(
                f"[GOVERNANCE] All checks passed for {evaluation.hook}",
                extra={
                    'applied_rules': evaluation.applied_rules,
                    'context': context.to_dict()
                }
            )
```

---

## Step 4: Unit Tests

```python
# tests/governance/test_enforcement_registry.py

import pytest
from pathlib import Path
import tempfile
import yaml

from src.orchestrators.governance.enforcement_registry import (
    GovernanceRegistry,
    ExecutionContext,
)


@pytest.fixture
def temp_rules_yaml():
    """Create temporary rules.yaml for testing"""
    content = {
        'schema_version': '7.0',
        'enforcement_mode': 'declarative',
        'auto_wire': True,
        'rules': {
            'CORE-001': {
                'name': 'Test Rule 1',
                'category': 'orchestration',
                'severity': 'blocked',
                'description': 'Test',
                'enforcement': {
                    'middleware_class': 'tests.governance.mock_middleware.MockPassMiddleware',
                    'hook': 'pre_execution',
                    'priority': 100,
                    'config': {}
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(content, f)
        return Path(f.name)


def test_registry_loads_rules(temp_rules_yaml):
    """Registry successfully loads rules from YAML"""
    registry = GovernanceRegistry(temp_rules_yaml)
    
    assert len(registry.rules) == 1
    assert 'CORE-001' in registry.rules


def test_registry_instantiates_middleware(temp_rules_yaml):
    """Registry successfully instantiates enforcement middleware"""
    registry = GovernanceRegistry(temp_rules_yaml)
    
    assert len(registry.middleware_instances) == 1
    assert 'CORE-001' in registry.middleware_instances


def test_get_active_rules_by_hook(temp_rules_yaml):
    """Registry returns rules filtered by hook"""
    registry = GovernanceRegistry(temp_rules_yaml)
    
    active = registry.get_active_rules_by_hook('pre_execution')
    assert len(active) == 1
    assert active[0].rule_id == 'CORE-001'
    
    # Wrong hook
    active = registry.get_active_rules_by_hook('post_execution')
    assert len(active) == 0


def test_evaluate_passing_check(temp_rules_yaml):
    """Evaluate returns passed=True when middleware check succeeds"""
    registry = GovernanceRegistry(temp_rules_yaml)
    
    context = ExecutionContext(operation='test')
    eval = registry.evaluate('pre_execution', context)
    
    assert eval.should_block is False
    assert len(eval.violations) == 0
    assert 'CORE-001' in eval.applied_rules


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Step 5: Integration Checklist

- [ ] Create `cortex-brain/tier0/governance/enforcement_base.py`
- [ ] Create `cortex-brain/tier0/governance/enforcement_registry.py`
- [ ] Create `cortex-brain/tier0/governance/rules.yaml` (with first 5 rules)
- [ ] Create `cortex-brain/tier0/governance/__init__.py`
- [ ] Create unit test files in `tests/governance/`
- [ ] Run tests locally (should all pass)
- [ ] Add to CI/CD pipeline
- [ ] Document in README

---

## Next Steps

1. **Implement Phase 1 code** (above)
2. **Test locally** (MAC + WIN)
3. **Get feedback** before integrating into MasterOrchestrator
4. **Phase 2:** Integrate into MasterOrchestrator (non-breaking)
5. **Phase 3:** Convert remaining 23 rules
6. **Phase 4:** Validate and harden

---

## Key Takeaway

**This is the foundation.** Once GovernanceRegistry works, everything else flows from it:
- New rules? Just add to YAML. Auto-wired.
- New middleware? Create class, reference in YAML. Auto-instantiated.
- New hook? Just use it in YAML. Registry handles it.

"Once configured in CORTEX, enforcement stays configured."
