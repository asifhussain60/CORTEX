"""
Tests for OrchestratorBaseProtocol - Phase 71 S2 Learning Capture.

AC-ID: PHASE-71-S2
Purpose: Verify automatic learning capture in base protocol

Test Coverage:
1. Learning phase executes after successful domain execution
2. Learning phase skipped on domain failure
3. @skip_learning decorator works
4. Learning failures don't block execution
5. Operation type detection works correctly
6. Protocol status includes learning info
7. Integration with UniversalLearningLoop

Author: Asif Hussain
Date: 2026-02-09
"""

import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.core.orchestrator_base_protocol import (
    OrchestratorBaseProtocol,
    ProtocolExecutionResult,
    skip_learning,
)


# =============================================================================
# Test Fixtures
# =============================================================================

class ConcreteOrchestrator(OrchestratorBaseProtocol):
    """Concrete implementation for testing."""
    
    def __init__(self, return_success: bool = True, result_data: Any = None):
        """Initialize with configurable result."""
        super().__init__()
        self._return_success = return_success
        self._result_data = result_data or {"status": "success"}
        self._domain_executed = False
        # Clear DoR gate for testing to bypass DoR check
        self.dor_gate = None
    
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result:
        """Test implementation of domain logic."""
        self._domain_executed = True
        if self._return_success:
            return Ok(self._result_data)
        else:
            return Err("Domain execution failed")


@skip_learning
class SkipLearningOrchestrator(OrchestratorBaseProtocol):
    """Orchestrator with learning disabled."""
    
    def __init__(self):
        """Initialize with DoR gate cleared for testing."""
        super().__init__()
        self.dor_gate = None  # Disable DoR for testing
    
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result:
        """Test implementation."""
        return Ok({"status": "success"})


class TDDTestOrchestrator(OrchestratorBaseProtocol):
    """Test TDD orchestrator for operation type detection."""
    
    def __init__(self):
        """Initialize with DoR gate cleared."""
        super().__init__()
        self.dor_gate = None
    
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result:
        """Test implementation."""
        return Ok({"status": "success"})


class RefactoringTestOrchestrator(OrchestratorBaseProtocol):
    """Test refactoring orchestrator for operation type detection."""
    
    def __init__(self):
        """Initialize with DoR gate cleared."""
        super().__init__()
        self.dor_gate = None
    
    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any],
    ) -> Result:
        """Test implementation."""
        return Ok({"status": "success"})


@pytest.fixture
def mock_learning_loop():
    """Create mock learning loop."""
    with patch('cortex.orchestrators.core.orchestrator_base_protocol.get_learning_loop') as mock:
        loop = MagicMock()
        loop.capture_from_operation.return_value = [
            MagicMock(pattern_type="TECHNICAL", pattern_description="Test pattern")
        ]
        mock.return_value = loop
        yield loop


# =============================================================================
# Test: Learning Phase Execution
# =============================================================================

class TestLearningPhaseExecution:
    """Tests for Phase 6 learning capture execution."""
    
    def test_learning_phase_executes_on_success(self, mock_learning_loop):
        """Learning phase should execute after successful domain execution."""
        # Arrange
        orchestrator = ConcreteOrchestrator(return_success=True)
        
        # Act
        result = orchestrator.execute_with_protocol(
            user_request="Test request",
            context={"test": "context"},
        )
        
        # Assert
        assert result.is_ok()
        mock_learning_loop.capture_from_operation.assert_called_once()
        call_args = mock_learning_loop.capture_from_operation.call_args
        assert call_args.kwargs["orchestrator"] == "ConcreteOrchestrator"
        assert call_args.kwargs["operation"] == "generic"
    
    def test_learning_phase_skipped_on_failure(self, mock_learning_loop):
        """Learning phase should NOT execute when domain fails."""
        # Arrange
        orchestrator = ConcreteOrchestrator(return_success=False)
        
        # Act
        result = orchestrator.execute_with_protocol(
            user_request="Test request",
            context={},
        )
        
        # Assert
        assert result.is_err()
        mock_learning_loop.capture_from_operation.assert_not_called()
    
    def test_learning_phase_passes_correct_context(self, mock_learning_loop):
        """Learning phase should pass correct context to learning loop."""
        # Arrange
        orchestrator = ConcreteOrchestrator(
            return_success=True,
            result_data={"key": "value", "count": 42}
        )
        
        # Act
        orchestrator.execute_with_protocol(
            user_request="Specific request",
            context={"input_param": "test_value"},
        )
        
        # Assert
        call_args = mock_learning_loop.capture_from_operation.call_args
        context = call_args.kwargs["context"]
        result = call_args.kwargs["result"]
        
        assert context["request"] == "Specific request"
        assert context["input_param"] == "test_value"
        assert result["key"] == "value"
        assert result["count"] == 42


# =============================================================================
# Test: Skip Learning Decorator
# =============================================================================

class TestSkipLearningDecorator:
    """Tests for @skip_learning decorator."""
    
    def test_skip_learning_decorator_prevents_capture(self, mock_learning_loop):
        """@skip_learning decorator should prevent learning capture."""
        # Arrange
        orchestrator = SkipLearningOrchestrator()
        
        # Act
        result = orchestrator.execute_with_protocol(
            user_request="Test request",
            context={},
        )
        
        # Assert
        assert result.is_ok()
        mock_learning_loop.capture_from_operation.assert_not_called()
    
    def test_skip_learning_sets_class_attribute(self):
        """@skip_learning should set _skip_learning attribute on class."""
        assert hasattr(SkipLearningOrchestrator, '_skip_learning')
        assert SkipLearningOrchestrator._skip_learning is True
    
    def test_non_decorated_class_has_no_skip_attribute(self):
        """Non-decorated classes should not have _skip_learning=True."""
        assert not getattr(ConcreteOrchestrator, '_skip_learning', False)


# =============================================================================
# Test: Learning Failure Handling
# =============================================================================

class TestLearningFailureHandling:
    """Tests for learning failure resilience."""
    
    def test_learning_failure_does_not_block_execution(self):
        """Learning failures should not block domain execution result."""
        # Arrange
        with patch('cortex.orchestrators.core.orchestrator_base_protocol.get_learning_loop') as mock:
            loop = MagicMock()
            loop.capture_from_operation.side_effect = Exception("Learning failed!")
            mock.return_value = loop
            
            orchestrator = ConcreteOrchestrator(return_success=True)
            
            # Act
            result = orchestrator.execute_with_protocol(
                user_request="Test request",
                context={},
            )
            
            # Assert - execution still succeeds
            assert result.is_ok()
            assert result.unwrap()["status"] == "success"
    
    def test_learning_loop_unavailable_degrades_gracefully(self):
        """When learning loop unavailable, execution continues normally."""
        # Arrange - Patch to return None (simulates unavailable)
        with patch('cortex.orchestrators.core.orchestrator_base_protocol.get_learning_loop', return_value=None):
            orchestrator = ConcreteOrchestrator(return_success=True)
            
            # Act
            result = orchestrator.execute_with_protocol(
                user_request="Test request",
                context={},
            )
            
            # Assert - execution still succeeds
            assert result.is_ok()


# =============================================================================
# Test: Operation Type Detection
# =============================================================================

class TestOperationTypeDetection:
    """Tests for _get_learning_operation_type()."""
    
    def test_tdd_orchestrator_returns_tdd_type(self):
        """TDD orchestrators should return 'tdd' operation type."""
        orchestrator = TDDTestOrchestrator()
        assert orchestrator._get_learning_operation_type() == "tdd"
    
    def test_refactoring_orchestrator_returns_refactoring_type(self):
        """Refactoring orchestrators should return 'refactoring' type."""
        orchestrator = RefactoringTestOrchestrator()
        assert orchestrator._get_learning_operation_type() == "refactoring"
    
    def test_generic_orchestrator_returns_generic_type(self):
        """Generic orchestrators should return 'generic' type."""
        orchestrator = ConcreteOrchestrator()
        assert orchestrator._get_learning_operation_type() == "generic"
    
# =============================================================================
# Test: Protocol Status
# =============================================================================

class TestProtocolStatus:
    """Tests for get_protocol_status() with learning info."""
    
    def test_protocol_status_includes_learning_component(self, mock_learning_loop):
        """Protocol status should include learning component status."""
        orchestrator = ConcreteOrchestrator()
        
        status = orchestrator.get_protocol_status()
        
        assert "learning" in status["components"]
        assert status["components"]["learning"] is True
    
    def test_protocol_status_includes_learning_enabled(self, mock_learning_loop):
        """Protocol status should include learning_enabled flag."""
        orchestrator = ConcreteOrchestrator()
        
        status = orchestrator.get_protocol_status()
        
        assert "learning_enabled" in status["enforcement"]
        assert status["enforcement"]["learning_enabled"] is True
    
    def test_protocol_status_learning_disabled_for_skip_decorated(self, mock_learning_loop):
        """Protocol status should show learning_enabled=False for @skip_learning."""
        orchestrator = SkipLearningOrchestrator()
        
        status = orchestrator.get_protocol_status()
        
        assert status["enforcement"]["learning_enabled"] is False
    
    def test_protocol_status_includes_phase_71_governance(self):
        """Protocol status should include PHASE-71-S2 governance rule."""
        orchestrator = ConcreteOrchestrator()
        
        status = orchestrator.get_protocol_status()
        
        assert "PHASE-71-S2" in status["governance"]
    
    def test_protocol_version_is_2_0(self):
        """Protocol version should be 2.0 after Phase 71."""
        orchestrator = ConcreteOrchestrator()
        
        status = orchestrator.get_protocol_status()
        
        assert status["protocol_version"] == "2.0"


# =============================================================================
# Test: Integration with UniversalLearningLoop
# =============================================================================

class TestLearningLoopIntegration:
    """Integration tests with actual UniversalLearningLoop."""
    
    @pytest.mark.integration
    def test_real_learning_loop_integration(self):
        """Test with real UniversalLearningLoop (integration test)."""
        # Import real learning loop
        try:
            from cortex.learning import get_learning_loop
            
            # Get real loop
            loop = get_learning_loop()
            
            # Orchestrator should capture to real loop
            orchestrator = ConcreteOrchestrator(
                return_success=True,
                result_data={"patterns_found": 3, "test_passed": True}
            )
            
            # Execute
            result = orchestrator.execute_with_protocol(
                user_request="Implement feature X",
                context={"file_path": "test.py"},
            )
            
            # Verify execution succeeded
            assert result.is_ok()
            
            # Verify metrics updated (if loop has metrics)
            if hasattr(loop, 'get_learning_metrics'):
                metrics = loop.get_learning_metrics()
                assert "total_learnings" in metrics
            
        except ImportError:
            pytest.skip("UniversalLearningLoop not available")


# =============================================================================
# Test: Protocol Phases Ordering
# =============================================================================

class TestProtocolPhasesOrdering:
    """Tests for correct phase ordering with learning."""
    
    def test_learning_phase_runs_after_domain(self, mock_learning_loop):
        """Learning phase (6) should run AFTER domain phase (5)."""
        # Arrange
        call_order = []
        
        class OrderTrackingOrchestrator(OrchestratorBaseProtocol):
            def __init__(self):
                super().__init__()
                self.dor_gate = None  # Disable DoR for testing
            
            def _execute_domain_logic(self, user_request, lens_context, context):
                call_order.append("domain")
                return Ok({"status": "success"})
        
        # Track learning call
        def track_learning(*args, **kwargs):
            call_order.append("learning")
            return []
        
        mock_learning_loop.capture_from_operation.side_effect = track_learning
        
        # Act
        orchestrator = OrderTrackingOrchestrator()
        orchestrator.execute_with_protocol(
            user_request="Test",
            context={},
        )
        
        # Assert
        assert call_order == ["domain", "learning"]
    
    def test_phases_completed_includes_learning(self, mock_learning_loop):
        """Audit log should include 'learning' in phases_completed."""
        # Arrange
        orchestrator = ConcreteOrchestrator()
        
        with patch.object(orchestrator.logger, 'log_operation_complete') as mock_log:
            # Act
            orchestrator.execute_with_protocol(
                user_request="Test",
                context={},
            )
            
            # Assert
            mock_log.assert_called()
            call_args = mock_log.call_args
            phases = call_args.kwargs.get("details", {}).get("phases_completed", [])
            assert "learning" in phases


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestLearningEdgeCases:
    """Edge case tests for learning capture."""
    
    def test_empty_result_handled(self, mock_learning_loop):
        """Empty result dict should be handled gracefully."""
        orchestrator = ConcreteOrchestrator(
            return_success=True,
            result_data={}
        )
        
        result = orchestrator.execute_with_protocol(
            user_request="Test",
            context={},
        )
        
        assert result.is_ok()
        mock_learning_loop.capture_from_operation.assert_called_once()
    
    def test_non_dict_result_wrapped(self, mock_learning_loop):
        """Non-dict result should be wrapped in result dict."""
        orchestrator = ConcreteOrchestrator(
            return_success=True,
            result_data="string_result"
        )
        
        orchestrator.execute_with_protocol(
            user_request="Test",
            context={},
        )
        
        call_args = mock_learning_loop.capture_from_operation.call_args
        result = call_args.kwargs["result"]
        assert result == {"result": "string_result"}
    
    def test_none_context_handled(self, mock_learning_loop):
        """None context should be handled gracefully."""
        orchestrator = ConcreteOrchestrator()
        
        result = orchestrator.execute_with_protocol(
            user_request="Test",
            context=None,  # Explicitly None
        )
        
        assert result.is_ok()
