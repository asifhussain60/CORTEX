"""
Tests for OrchestratorBase - Base Orchestrator Abstract Class

Tests the interface, lifecycle management, governance context injection,
and audit trail integration.
"""

import pytest
from datetime import datetime
from typing import Any, List

from src.core.orchestrator_base import (
    OrchestratorBase,
    OrchestrationContext,
    OrchestrationResult,
    OrchestrationStatus,
)


# =============================================================================
# Test Orchestrator Implementation (For testing base class)
# =============================================================================

class MinimalOrchestrator(OrchestratorBase):
    """Minimal orchestrator for testing base class"""
    
    def execute(self) -> Any:
        return {"status": "success", "message": "Minimal orchestrator executed"}


class ValidatingOrchestrator(OrchestratorBase):
    """Orchestrator with validation"""
    
    def validate_context(self) -> List[str]:
        """Validate that required_param is present"""
        errors = super().validate_context()
        if "required_param" not in self.context.parameters:
            errors.append("required_param is missing from parameters")
        return errors
    
    def execute(self) -> Any:
        return self.context.parameters.get("required_param")


class HookTestOrchestrator(OrchestratorBase):
    """Orchestrator that tests lifecycle hooks"""
    
    def __init__(self, context: OrchestrationContext):
        super().__init__(context)
        self.on_start_called = False
        self.on_complete_called = False
    
    def on_start(self) -> None:
        self.on_start_called = True
        self._log("on_start hook executed")
    
    def on_complete(self) -> None:
        self.on_complete_called = True
        self._log("on_complete hook executed")
    
    def execute(self) -> Any:
        return {"hooks_executed": True}


class FailingOrchestrator(OrchestratorBase):
    """Orchestrator that fails during execution"""
    
    def execute(self) -> Any:
        raise RuntimeError("Intentional failure for testing")


class TierAccessOrchestrator(OrchestratorBase):
    """Orchestrator that declares tier dependencies"""
    
    def __init__(self, context: OrchestrationContext):
        super().__init__(context)
        # Override tier access: only allow tier 0 and 1
        self.context.tier_access = {0, 1}
    
    def execute(self) -> Any:
        return {
            "tier_access": list(self.get_tier_access()),
            "can_access_tier_0": self.can_access_tier(0),
            "can_access_tier_2": self.can_access_tier(2),
        }


# =============================================================================
# Tests: OrchestrationContext
# =============================================================================

class TestOrchestrationContext:
    """Test OrchestrationContext dataclass"""
    
    def test_context_creation(self):
        """Test basic context creation"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="TestOrchestrator"
        )
        
        assert context.orchestrator_id == "test-orch-001"
        assert context.orchestrator_name == "TestOrchestrator"
        assert context.execution_id is not None
        assert context.status == OrchestrationStatus.INITIALIZED
    
    def test_context_with_parameters(self):
        """Test context with parameters"""
        params = {"key": "value", "number": 42}
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="TestOrchestrator",
            parameters=params
        )
        
        assert context.parameters == params
    
    def test_context_validates_id_requirement(self):
        """Test that context requires orchestrator_id"""
        with pytest.raises(ValueError):
            OrchestrationContext(
                orchestrator_id="",
                orchestrator_name="TestOrchestrator"
            )
    
    def test_context_validates_name_requirement(self):
        """Test that context requires orchestrator_name"""
        with pytest.raises(ValueError):
            OrchestrationContext(
                orchestrator_id="test-orch-001",
                orchestrator_name=""
            )
    
    def test_context_generates_execution_id(self):
        """Test that execution_id is auto-generated"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="TestOrchestrator"
        )
        
        assert context.execution_id is not None
        assert len(context.execution_id) > 0


# =============================================================================
# Tests: OrchestratorBase Lifecycle
# =============================================================================

class TestOrchestratorLifecycle:
    """Test orchestrator lifecycle management"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator creation"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch = MinimalOrchestrator(context)
        
        assert orch.context == context
        assert orch.result is None
    
    def test_orchestrator_requires_valid_context_type(self):
        """Test that orchestrator requires OrchestrationContext"""
        with pytest.raises(TypeError):
            MinimalOrchestrator("not a context")  # type: ignore
    
    def test_successful_execution(self):
        """Test full successful execution lifecycle"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch = MinimalOrchestrator(context)
        result = orch.run()
        
        assert result.success is True
        assert result.status == OrchestrationStatus.COMPLETED
        assert result.output == {"status": "success", "message": "Minimal orchestrator executed"}
        assert result.duration_seconds >= 0
    
    def test_execution_hooks_called(self):
        """Test that on_start and on_complete hooks are called"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="HookTestOrchestrator"
        )
        orch = HookTestOrchestrator(context)
        result = orch.run()
        
        assert orch.on_start_called is True
        assert orch.on_complete_called is True
        assert result.success is True
    
    def test_execution_failure_handling(self):
        """Test that exceptions are caught and converted to failure result"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="FailingOrchestrator"
        )
        orch = FailingOrchestrator(context)
        result = orch.run()
        
        assert result.success is False
        assert result.status == OrchestrationStatus.FAILED
        assert "Intentional failure" in result.message
        assert result.error_code == "RuntimeError"


# =============================================================================
# Tests: Validation
# =============================================================================

class TestValidation:
    """Test validation hooks"""
    
    def test_validation_failure(self):
        """Test that validation errors prevent execution"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="ValidatingOrchestrator",
            parameters={}  # Missing required_param
        )
        orch = ValidatingOrchestrator(context)
        result = orch.run()
        
        assert result.success is False
        assert result.status == OrchestrationStatus.VALIDATING
        assert "required_param is missing" in result.message
    
    def test_validation_success(self):
        """Test that valid context allows execution"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="ValidatingOrchestrator",
            parameters={"required_param": "test-value"}
        )
        orch = ValidatingOrchestrator(context)
        result = orch.run()
        
        assert result.success is True
        assert result.output == "test-value"


# =============================================================================
# Tests: Tier Access Control
# =============================================================================

class TestTierAccess:
    """Test governance tier access control"""
    
    def test_default_tier_access(self):
        """Test that all tiers accessible by default"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch = MinimalOrchestrator(context)
        
        tier_access = orch.get_tier_access()
        assert 0 in tier_access
        assert 1 in tier_access
        assert 2 in tier_access
        assert 3 in tier_access
    
    def test_can_access_tier(self):
        """Test can_access_tier method"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="TierAccessOrchestrator",
            tier_access={0, 1}
        )
        orch = TierAccessOrchestrator(context)
        
        assert orch.can_access_tier(0) is True
        assert orch.can_access_tier(1) is True
        assert orch.can_access_tier(2) is False
        assert orch.can_access_tier(3) is False
    
    def test_tier_access_in_result(self):
        """Test that tier access is accessible during execution"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="TierAccessOrchestrator"
        )
        orch = TierAccessOrchestrator(context)
        result = orch.run()
        
        assert result.success is True
        output = result.output
        assert output["can_access_tier_0"] is True
        assert output["can_access_tier_2"] is False


# =============================================================================
# Tests: Logging & Audit
# =============================================================================

class TestLogging:
    """Test execution logging"""
    
    def test_execution_log_created(self):
        """Test that execution log is populated"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="HookTestOrchestrator"
        )
        orch = HookTestOrchestrator(context)
        orch.run()
        
        log = orch.get_execution_log()
        assert len(log) > 0
        assert any("Validation" in entry for entry in log)
        assert any("execution" in entry.lower() for entry in log)
    
    def test_log_entries_have_timestamps(self):
        """Test that log entries include timestamps"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="HookTestOrchestrator"
        )
        orch = HookTestOrchestrator(context)
        orch.run()
        
        log = orch.get_execution_log()
        for entry in log:
            assert "[" in entry and "]" in entry  # Timestamp format


# =============================================================================
# Tests: Metadata
# =============================================================================

class TestMetadata:
    """Test orchestrator metadata"""
    
    def test_orchestrator_repr(self):
        """Test orchestrator string representation"""
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch = MinimalOrchestrator(context)
        
        repr_str = repr(orch)
        assert "MinimalOrchestrator" in repr_str
        assert "test-orch-001" in repr_str
        assert "initialized" in repr_str


# =============================================================================
# Tests: OrchestrationResult
# =============================================================================

class TestOrchestrationResult:
    """Test OrchestrationResult dataclass"""
    
    def test_result_creation(self):
        """Test result creation"""
        result = OrchestrationResult(
            orchestrator_id="test-orch-001",
            execution_id="exec-001",
            status=OrchestrationStatus.COMPLETED,
            success=True
        )
        
        assert result.orchestrator_id == "test-orch-001"
        assert result.execution_id == "exec-001"
        assert result.success is True
    
    def test_result_timing(self):
        """Test result includes execution timing"""
        start = datetime.utcnow()
        context = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch = MinimalOrchestrator(context)
        result = orch.run()
        end = datetime.utcnow()
        
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.start_time >= start
        assert result.end_time <= end
        assert result.duration_seconds >= 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for orchestrator lifecycle"""
    
    def test_end_to_end_execution(self):
        """Test complete end-to-end orchestrator execution"""
        context = OrchestrationContext(
            orchestrator_id="integration-test-001",
            orchestrator_name="IntegrationTestOrchestrator",
            parameters={"test": "value"},
            environment="staging"
        )
        orch = MinimalOrchestrator(context)
        result = orch.run()
        
        # Verify complete result
        assert result.success is True
        assert result.status == OrchestrationStatus.COMPLETED
        assert result.orchestrator_id == "integration-test-001"
        assert result.execution_id is not None
        assert result.output is not None
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration_seconds >= 0
    
    def test_multiple_executions(self):
        """Test that orchestrator can be re-used with different contexts"""
        # First execution
        context1 = OrchestrationContext(
            orchestrator_id="test-orch-001",
            orchestrator_name="MinimalOrchestrator"
        )
        orch1 = MinimalOrchestrator(context1)
        result1 = orch1.run()
        
        # Second execution (different instance, different context)
        context2 = OrchestrationContext(
            orchestrator_id="test-orch-002",
            orchestrator_name="MinimalOrchestrator"
        )
        orch2 = MinimalOrchestrator(context2)
        result2 = orch2.run()
        
        # Verify they are independent
        assert result1.execution_id != result2.execution_id
        assert result1.orchestrator_id == "test-orch-001"
        assert result2.orchestrator_id == "test-orch-002"
        assert result1.success is True
        assert result2.success is True
