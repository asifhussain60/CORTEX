# Contributing to Golden Test Framework

**Authority:** AC-GOLDEN-FRAMEWORK-001  
**Purpose:** Guide for adding new orchestrator tests

## Adding Tests for a New Orchestrator

### 1. Choose Test Category

Determine which orchestrator tier:
- **Core** (8 orchestrators): MasterOrchestrator, TDDOrchestrator, LENSSynthesis, etc.
- **Domain** (6 orchestrators): RefactoringOrchestrator, PlanOrchestrator, etc.
- **Support** (14 orchestrators): OnboardingOrchestrator, ToolDiscoveryOrchestrator, etc.

### 2. Create Test Files

Use **kebab-case** naming (CORE-028):

```bash
# Core orchestrator (28 tests total)
tests/orchestrators/core/positive/test-{orchestrator-name}.py        # 8 tests
tests/orchestrators/core/negative/test-{orchestrator-name}-forbidden.py  # 8 tests
tests/orchestrators/core/edge-cases/test-{orchestrator-name}-boundaries.py  # 6 tests
tests/orchestrators/core/recovery/test-{orchestrator-name}-crash-recovery.py  # 6 tests

# Domain orchestrator (16 tests total)
tests/orchestrators/domain/positive/test-{orchestrator-name}.py     # 6 tests
tests/orchestrators/domain/negative/test-{orchestrator-name}-forbidden.py  # 6 tests
tests/orchestrators/domain/edge-cases/test-{orchestrator-name}-boundaries.py  # 2 tests
tests/orchestrators/domain/recovery/test-{orchestrator-name}-recovery.py  # 2 tests

# Support orchestrator (12 tests total)
tests/orchestrators/support/positive/test-{orchestrator-name}.py    # 4 tests
tests/orchestrators/support/negative/test-{orchestrator-name}-forbidden.py  # 4 tests
tests/orchestrators/support/edge-cases/test-{orchestrator-name}-boundaries.py  # 2 tests
tests/orchestrators/support/recovery/test-{orchestrator-name}-recovery.py  # 2 tests
```

### 3. Use Base Test Classes

```python
"""
Test MasterOrchestrator positive scenarios.

Authority: AC-GOLDEN-FRAMEWORK-002
"""
from tests.orchestrators.base_orchestrator_test import BaseOrchestratorTest


class TestMasterOrchestratorPositive(BaseOrchestratorTest):
    """Positive tests for MasterOrchestrator."""
    
    def test_routes_request_to_correct_child_orchestrator(
        self,
        real_event_bus,
        audit_db,
        real_registry
    ):
        """Should route request to correct child orchestrator."""
        # Use real components (no mocks)
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator(
            event_bus=real_event_bus,
            registry=real_registry
        )
        
        context = self.create_test_context(intent="IMPLEMENT")
        result = orchestrator.coordinate_operation(context)
        
        assert result["routed_to"] == "TDDOrchestrator"
        self.assert_audit_trail(audit_db, "AC-MASTER-001")
        self.assert_no_mocks_used(self)
```

### 4. Negative Test Example

```python
"""
Test MasterOrchestrator forbidden actions.

Authority: AC-GOLDEN-FRAMEWORK-002
"""
from tests.orchestrators.base_negative_test import BaseNegativeTest


class TestMasterOrchestratorNegative(BaseNegativeTest):
    """Negative tests for MasterOrchestrator."""
    
    def test_blocks_bypass_mcp_gateway(self, real_event_bus, audit_db):
        """Should BLOCK attempts to bypass MCP gateway."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator(event_bus=real_event_bus)
        
        # Attempt to bypass MCP gateway
        def bypass_action():
            context = self.create_test_context(source="direct")
            return orchestrator.coordinate_operation(context)
        
        self.assert_blocked(
            action=bypass_action,
            expected_error=ValueError,
            expected_message_contains="MCP gateway required"
        )
        
        self.assert_violation_logged(audit_db, "MCP_BYPASS")
```

### 5. Edge Case Example

```python
"""
Test MasterOrchestrator edge cases.

Authority: AC-GOLDEN-FRAMEWORK-002
"""
from tests.orchestrators.base_edge_case_test import BaseEdgeCaseTest


class TestMasterOrchestratorEdgeCases(BaseEdgeCaseTest):
    """Edge case tests for MasterOrchestrator."""
    
    def test_handles_zero_registered_orchestrators(self, real_event_bus):
        """Should handle gracefully when 0 orchestrators registered."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        # Create extreme context
        context = self.create_extreme_context("zero_orchestrators")
        
        orchestrator = MasterOrchestrator(event_bus=real_event_bus)
        
        result = self.assert_graceful_degradation(
            action=lambda: orchestrator.coordinate_operation(context),
            expected_fallback={"status": "degraded", "message": "No orchestrators available"},
            timeout_seconds=5.0
        )
        
        assert result["status"] == "degraded"
```

### 6. Recovery Test Example

```python
"""
Test MasterOrchestrator crash recovery.

Authority: AC-GOLDEN-FRAMEWORK-002
"""
from tests.orchestrators.base_recovery_test import BaseRecoveryTest


class TestMasterOrchestratorRecovery(BaseRecoveryTest):
    """Recovery tests for MasterOrchestrator."""
    
    def test_recovers_from_mid_execution_crash(
        self,
        real_event_bus,
        audit_db
    ):
        """Should recover state after mid-execution crash."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        orchestrator = MasterOrchestrator(event_bus=real_event_bus)
        context = self.create_test_context()
        
        # Simulate crash
        crash = self.simulate_crash(
            action=lambda: orchestrator.coordinate_operation(context),
            crash_point="mid_execution"
        )
        
        assert isinstance(crash, Exception)
        
        # Verify recovery
        self.assert_state_recovered(audit_db, "routing_complete")
        self.assert_rollback_complete(audit_db, "AC-MASTER-001")
```

## Test Checklist

Before submitting:
- [ ] File names use kebab-case (CORE-028)
- [ ] No SCREAMING_CASE or CamelCase
- [ ] No version suffixes (_v2, -v3)
- [ ] Zero mocks (use real_event_bus, real_registry, audit_db fixtures)
- [ ] All tests inherit from base test classes
- [ ] Audit trail assertions included
- [ ] Governance violations logged (negative tests)
- [ ] Test count matches tier (28 core / 16 domain / 12 support)
- [ ] Tests pass: `pytest tests/orchestrators/{tier}/{category}/test-{name}.py -v`

## Running Tests

```bash
# Run all tests for an orchestrator
pytest tests/orchestrators/core/positive/test-master-orchestrator.py -v

# Run specific category
pytest tests/orchestrators/core/negative/ -v

# Run with coverage
pytest tests/orchestrators/ --cov=cortex --cov-report=term --cov-fail-under=85

# Check file naming compliance
python3 scripts/enforce-test-naming.py --check
```

## Common Patterns

### Pattern 1: EventBus Integration
```python
def test_publishes_events(self, real_event_bus):
    """Should publish events to EventBus."""
    events = []
    real_event_bus.subscribe("test_event", lambda e: events.append(e))
    
    # ... trigger event ...
    
    assert len(events) > 0
```

### Pattern 2: Audit Trail Verification
```python
def test_creates_audit_trail(self, audit_db):
    """Should create audit trail with AC markers."""
    # ... execute operation ...
    
    self.assert_audit_trail(audit_db, "AC-TEST-001")
```

### Pattern 3: Zero Mock Enforcement
```python
def test_uses_no_mocks(self):
    """Should use zero mocks (golden test requirement)."""
    self.assert_no_mocks_used(self)
```

## Questions?

See:
- `tests/orchestrators/README.md` - Framework overview
- `tests/fixtures/README.md` - Fixture usage guide
- `.github/prompts/cortex-architect.prompt.md` - Governance rules
