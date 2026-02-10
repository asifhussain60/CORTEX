"""
Tests for MCP Learning Gateway Interceptor - Phase 71 S3.

AC-ID: PHASE-71-S3
Purpose: Verify learning capture from MCP tool execution

Test Coverage:
1. Interception of MCP tool execution
2. Pattern extraction from tool results
3. Deduplication of identical patterns
4. Metrics tracking
5. Integration with UniversalLearningLoop
6. Non-blocking failure handling
7. Operation type inference

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.learning_gateway_interceptor import (
    MCPLearningInterceptor,
    InterceptedOperation,
    LearningInterceptorMetrics,
    get_mcp_learning_interceptor,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_learning_loop():
    """Create mock learning loop."""
    with patch('cortex.learning.get_learning_loop') as mock:  # Patch at source
        loop = MagicMock()
        loop.capture_from_operation.return_value = [
            MagicMock(pattern_type="TECHNICAL", pattern_description="Test pattern")
        ]
        mock.return_value = loop
        yield loop


@pytest.fixture
def interceptor():
    """Create fresh interceptor for each test."""
    interceptor = MCPLearningInterceptor()
    # Skip learning loop initialization for fast tests
    interceptor._learning_loop = None
    yield interceptor


# =============================================================================
# Test: InterceptedOperation
# =============================================================================

class TestInterceptedOperation:
    """Tests for InterceptedOperation data class."""
    
    def test_operation_creation(self):
        """InterceptedOperation should be creatable with standard fields."""
        op = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={"input": "test"},
            result={"output": "success"},
            execution_time_ms=123.45,
            timestamp="2026-02-10T12:00:00",
        )
        
        assert op.tool_name == "cortex_test_tool"
        assert op.parameters == {"input": "test"}
        assert op.result == {"output": "success"}
        assert op.execution_time_ms == 123.45
    
    def test_operation_to_context(self):
        """Operation should convert to learning context."""
        op = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={"input": "test"},
            result={"output": "success"},
            execution_time_ms=123.45,
            timestamp="2026-02-10T12:00:00",
        )
        
        context = op.to_context()
        
        assert context["tool"] == "cortex_test_tool"
        assert context["parameters"] == {"input": "test"}
        assert context["result"] == {"output": "success"}
        assert "source" not in context  # Not added by to_context (added by after_execution)
    
    def test_operation_pattern_hash(self):
        """Operation should generate consistent pattern hash."""
        op1 = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={"input": "test"},
            result={"output": "success"},
            execution_time_ms=100.0,
            timestamp="2026-02-10T12:00:00",
        )
        
        op2 = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={"input": "different"},  # Different parameters
            result={"output": "success"},  # Same result
            execution_time_ms=200.0,  # Different timing
            timestamp="2026-02-10T12:01:00",  # Different time
        )
        
        # Same result = same hash (hash based on tool + result)
        hash1 = op1.get_pattern_hash()
        hash2 = op2.get_pattern_hash()
        assert hash1 == hash2
    
    def test_operation_different_results_different_hash(self):
        """Operations with different results should have different hashes."""
        op1 = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
            timestamp="2026-02-10T12:00:00",
        )
        
        op2 = InterceptedOperation(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "failure"},  # Different result
            execution_time_ms=100.0,
            timestamp="2026-02-10T12:00:00",
        )
        
        hash1 = op1.get_pattern_hash()
        hash2 = op2.get_pattern_hash()
        assert hash1 != hash2


# =============================================================================
# Test: Metrics Tracking
# =============================================================================

class TestMetricsTracking:
    """Tests for LearningInterceptorMetrics."""
    
    def test_metrics_initialization(self):
        """Metrics should initialize with zeros."""
        metrics = LearningInterceptorMetrics()
        
        assert metrics.operations_intercepted == 0
        assert metrics.patterns_extracted == 0
        assert metrics.patterns_deduplicated == 0
        assert metrics.merge_failures == 0
        assert metrics.total_execution_time_ms == 0.0
    
    def test_metrics_record_operation(self):
        """Metrics should track recorded operations."""
        metrics = LearningInterceptorMetrics()
        op = InterceptedOperation(
            tool_name="test",
            parameters={},
            result={},
            execution_time_ms=50.0,
            timestamp="2026-02-10",
        )
        
        metrics.record_operation(op)
        
        assert metrics.operations_intercepted == 1
        assert metrics.total_execution_time_ms == 50.0
    
    def test_metrics_duplicate_detection(self):
        """Metrics should detect duplicate patterns."""
        metrics = LearningInterceptorMetrics()
        
        # Mark pattern as seen
        metrics.mark_pattern("hash123")
        
        # Check if duplicate
        assert metrics.is_duplicate("hash123")
        assert not metrics.is_duplicate("hash456")
    
    def test_metrics_deduplication_tracking(self):
        """Metrics should track unique patterns."""
        metrics = LearningInterceptorMetrics()
        
        metrics.mark_pattern("hash1")
        metrics.mark_pattern("hash2")
        metrics.mark_pattern("hash3")
        
        assert len(metrics.pattern_hashes) == 3


# =============================================================================
# Test: MCP Learning Interceptor
# =============================================================================

class TestMCPLearningInterceptor:
    """Tests for MCPLearningInterceptor."""
    
    def test_interceptor_initialization(self):
        """Interceptor should initialize with metrics."""
        interceptor = MCPLearningInterceptor()
        
        assert interceptor._metrics is not None
        assert interceptor._metrics.operations_intercepted == 0
    
    def test_after_execution_without_learning_loop(self, interceptor):
        """after_execution should work without learning loop."""
        # Learning loop is None (set in fixture)
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={"input": "test"},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        # Metrics should still update
        assert interceptor._metrics.operations_intercepted == 1
    
    def test_after_execution_with_learning_loop(self, interceptor, mock_learning_loop):
        """after_execution should call learning loop."""
        interceptor._learning_loop = mock_learning_loop
        
        interceptor.after_execution(
            tool_name="cortex_demo_tool",  # Changed to not contain "test"
            parameters={"input": "test"},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        # Learning loop should be called
        mock_learning_loop.capture_from_operation.assert_called_once()
        call_kwargs = mock_learning_loop.capture_from_operation.call_args.kwargs
        assert call_kwargs["orchestrator"] == "MCPGateway"
        assert call_kwargs["operation"] == "generic"
    
    def test_duplicate_pattern_skipped(self, interceptor, mock_learning_loop):
        """Duplicate patterns should be skipped."""
        interceptor._learning_loop = mock_learning_loop
        
        # First operation
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        call_count_1 = mock_learning_loop.capture_from_operation.call_count
        
        # Second operation with same result (duplicate)
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={"different": "params"},
            result={"output": "success"},  # Same result
            execution_time_ms=200.0,
        )
        
        # Second call should be skipped
        call_count_2 = mock_learning_loop.capture_from_operation.call_count
        assert call_count_2 == call_count_1  # No additional call
        assert interceptor._metrics.patterns_deduplicated == 1
    
    def test_different_results_not_deduplicated(self, interceptor, mock_learning_loop):
        """Different results should NOT be deduplicated."""
        interceptor._learning_loop = mock_learning_loop
        
        # First operation
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        call_count_1 = mock_learning_loop.capture_from_operation.call_count
        
        # Second operation with different result
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "failure"},  # Different result
            execution_time_ms=200.0,
        )
        
        # Both should be learned
        call_count_2 = mock_learning_loop.capture_from_operation.call_count
        assert call_count_2 == call_count_1 + 1  # One additional call
        assert interceptor._metrics.patterns_deduplicated == 0


# =============================================================================
# Test: Operation Type Inference
# =============================================================================

class TestOperationTypeInference:
    """Tests for tool name → operation type inference."""
    
    def test_tdd_tool_inference(self, interceptor):
        """TDD tools should be identified correctly."""
        assert interceptor._get_operation_type("cortex_run_tests") == "tdd"
        assert interceptor._get_operation_type("cortex_tdd_cycle") == "tdd"
        assert interceptor._get_operation_type("test_validator") == "tdd"
    
    def test_refactoring_tool_inference(self, interceptor):
        """Refactoring tools should be identified correctly."""
        assert interceptor._get_operation_type("cortex_refactor_code") == "refactoring"
        assert interceptor._get_operation_type("refactor_analyzer") == "refactoring"
    
    def test_review_tool_inference(self, interceptor):
        """Review/approval tools should be interaction."""
        assert interceptor._get_operation_type("cortex_review_pr") == "interaction"
        assert interceptor._get_operation_type("cortex_auto_approve") == "interaction"
    
    def test_governance_tool_inference(self, interceptor):
        """Governance tools should be identified correctly."""
        assert interceptor._get_operation_type("cortex_enforce_policy") == "governance"
        assert interceptor._get_operation_type("governance_check") == "governance"
    
    def test_planning_tool_inference(self, interceptor):
        """Planning tools should be coordination."""
        assert interceptor._get_operation_type("cortex_plan_migration") == "coordination"
        assert interceptor._get_operation_type("schedule_task") == "coordination"
    
    def test_analysis_tool_inference(self, interceptor):
        """Analysis tools should be analysis type."""
        assert interceptor._get_operation_type("cortex_lens_analyze") == "analysis"
        assert interceptor._get_operation_type("analyze_performance") == "analysis"
    
    def test_unknown_tool_inference(self, interceptor):
        """Unknown tools should default to generic."""
        assert interceptor._get_operation_type("cortex_custom_tool") == "generic"
        assert interceptor._get_operation_type("random_tool") == "generic"


# =============================================================================
# Test: Metrics Reporting
# =============================================================================

class TestMetricsReporting:
    """Tests for metrics retrieval."""
    
    def test_get_metrics_initial_state(self, interceptor):
        """Initial metrics should all be zero."""
        metrics = interceptor.get_metrics()
        
        assert metrics["operations_intercepted"] == 0
        assert metrics["patterns_extracted"] == 0
        assert metrics["patterns_deduplicated"] == 0
        assert metrics["unique_patterns_tracked"] == 0
    
    def test_get_metrics_after_operation(self, interceptor):
        """Metrics should update after operations."""
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        metrics = interceptor.get_metrics()
        
        assert metrics["operations_intercepted"] == 1
        assert metrics["total_execution_time_ms"] == 100.0
    
    def test_reset_metrics(self, interceptor):
        """Metrics should reset."""
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        assert interceptor.get_metrics()["operations_intercepted"] == 1
        
        interceptor.reset_metrics()
        
        assert interceptor.get_metrics()["operations_intercepted"] == 0


# =============================================================================
# Test: Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error resilience."""
    
    def test_learning_loop_failure_non_blocking(self, interceptor):
        """Learning loop failures should not raise."""
        mock_loop = MagicMock()
        mock_loop.capture_from_operation.side_effect = Exception("Learning failed!")
        interceptor._learning_loop = mock_loop
        
        # Should not raise
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        assert interceptor._metrics.merge_failures == 1
    
    def test_metrics_update_before_learning(self, interceptor, mock_learning_loop):
        """Metrics should update even if learning fails."""
        mock_learning_loop.capture_from_operation.side_effect = Exception("Learning failed!")
        interceptor._learning_loop = mock_learning_loop
        
        interceptor.after_execution(
            tool_name="cortex_test_tool",
            parameters={},
            result={"output": "success"},
            execution_time_ms=100.0,
        )
        
        # Metrics should be recorded despite learning failure
        assert interceptor._metrics.operations_intercepted == 1


# =============================================================================
# Test: Singleton Pattern
# =============================================================================

class TestSingleton:
    """Tests for singleton interceptor."""
    
    def test_get_mcp_learning_interceptor_singleton(self):
        """get_mcp_learning_interceptor should return same instance."""
        interceptor1 = get_mcp_learning_interceptor()
        interceptor2 = get_mcp_learning_interceptor()
        
        assert interceptor1 is interceptor2
    
    def test_metrics_persist_across_calls(self):
        """Metrics should persist across singleton calls."""
        # Reset first
        interceptor = get_mcp_learning_interceptor()
        interceptor.reset_metrics()
        
        # First call
        get_mcp_learning_interceptor().after_execution(
            tool_name="test1",
            parameters={},
            result={"a": 1},
            execution_time_ms=10.0,
        )
        
        # Get metrics from different reference
        metrics = get_mcp_learning_interceptor().get_metrics()
        assert metrics["operations_intercepted"] == 1


# =============================================================================
# Test: Integration
# =============================================================================

class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.integration
    def test_real_learning_loop_integration(self):
        """Test integration with real UniversalLearningLoop."""
        try:
            from cortex.learning import get_learning_loop
            
            # Create fresh interceptor
            interceptor = MCPLearningInterceptor()
            
            # Execute operation
            interceptor.after_execution(
                tool_name="cortex_test_tool",
                parameters={"test": "param"},
                result={"success": True},
                execution_time_ms=50.0,
            )
            
            # Verify metrics updated
            assert interceptor.get_metrics()["operations_intercepted"] == 1
            
        except ImportError:
            pytest.skip("UniversalLearningLoop not available")
