"""
Test suite for AC-NFR-002-01: Graceful Degradation Framework

Tests the GracefulDegradationFramework and related components for
enabling system continuation with reduced functionality on component failure.

Test Plan:
- 12 unit tests for core functionality
- 5 integration tests for multi-component scenarios
- 100% pass rate required
"""

import pytest
from unittest.mock import Mock, patch, call
from typing import Any
from datetime import datetime

from cortex_brain.tier2.resilience import (
    GracefulDegradationFramework,
    FallbackStrategy,
    PartialFunctionalityMode,
    ComponentFailure,
    DegradedResponse,
)


class TestGracefulDegradationFramework:
    """Unit tests for GracefulDegradationFramework (12 tests)"""
    
    def test_init_framework(self):
        """Test: Framework initializes with empty registry"""
        framework = GracefulDegradationFramework()
        assert len(framework._components) == 0
        assert len(framework._component_states) == 0
    
    def test_register_component_success(self):
        """Test: Component registration succeeds"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock(return_value="primary_result")
        fallback = Mock(return_value="fallback_result")
        
        framework.register_component("db", primary, [fallback])
        assert "db" in framework._components
    
    def test_register_component_duplicate_error(self):
        """Test: Duplicate registration raises ValueError"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock()
        framework.register_component("db", primary, [])
        
        with pytest.raises(ValueError, match="already registered"):
            framework.register_component("db", primary, [])
    
    def test_execute_primary_strategy_success(self):
        """Test: Primary strategy executes successfully"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock(return_value="success")
        framework.register_component("service", primary, [])
        
        result, mode = framework.execute_with_degradation("service")
        assert result == "success"
        assert mode == "primary"
        assert not framework.is_degraded("service")
    
    def test_execute_primary_failure_fallback_success(self):
        """Test: Primary fails, fallback succeeds"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock(side_effect=Exception("Failed"))
        fallback = Mock(return_value="fallback_result")
        framework.register_component("service", primary, [fallback])
        
        result, mode = framework.execute_with_degradation("service")
        assert result == "fallback_result"
        assert mode == "fallback_1"
        assert framework.is_degraded("service")
    
    def test_execute_all_strategies_fail(self):
        """Test: All strategies fail, raises ComponentFailure"""
        from cortex_brain.tier2.resilience import (
            GracefulDegradationFramework,
            ComponentFailure
        )
        framework = GracefulDegradationFramework()
        primary = Mock(side_effect=Exception("Primary failed"))
        fallback = Mock(side_effect=Exception("Fallback failed"))
        framework.register_component("service", primary, [fallback])
        
        with pytest.raises(ComponentFailure) as exc_info:
            framework.execute_with_degradation("service")
        assert "service" in str(exc_info.value)
        assert exc_info.value.strategies_tried == 2
    
    def test_is_degraded_check(self):
        """Test: is_degraded correctly identifies degradation status"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock(return_value="success")
        fallback = Mock(return_value="fallback")
        framework.register_component("service", primary, [fallback])
        
        # Primary mode - not degraded
        framework.execute_with_degradation("service")
        assert not framework.is_degraded("service")
        
        # Switch to fallback
        primary.side_effect = Exception()
        framework.execute_with_degradation("service")
        assert framework.is_degraded("service")
    
    def test_partial_functionality_disable_feature(self):
        """Test: Feature disables successfully"""
        from cortex_brain.tier2.resilience import PartialFunctionalityMode
        mode = PartialFunctionalityMode()
        mode.disable_feature("search", "Database offline")
        
        assert not mode.is_feature_available("search")
    
    def test_partial_functionality_enable_feature(self):
        """Test: Feature re-enables successfully"""
        from cortex_brain.tier2.resilience import PartialFunctionalityMode
        mode = PartialFunctionalityMode()
        mode.disable_feature("search", "Database offline")
        mode.enable_feature("search")
        
        assert mode.is_feature_available("search")
    
    def test_get_available_features(self):
        """Test: get_available_features returns correct list"""
        from cortex_brain.tier2.resilience import PartialFunctionalityMode
        mode = PartialFunctionalityMode()
        mode.disable_feature("search", "reason1")
        mode.disable_feature("analytics", "reason2")
        
        available = mode.get_available_features()
        assert "search" not in available
        assert "analytics" not in available
    
    def test_degraded_response_wrapper(self):
        """Test: DegradedResponse wraps data correctly"""
        from cortex_brain.tier2.resilience import DegradedResponse
        response = DegradedResponse(
            data={"results": []},
            degradation_reason="Database offline",
            mode="fallback_1",
            original_request_id="req-123"
        )
        
        assert response.get_data() == {"results": []}
        assert response.is_degraded()
        metadata = response.get_metadata()
        assert metadata["mode"] == "fallback_1"
    
    def test_component_failure_exception(self):
        """Test: ComponentFailure exception contains context"""
        from cortex_brain.tier2.resilience import ComponentFailure
        last_exc = Exception("Last failure")
        failure = ComponentFailure(
            component_name="api",
            reason="All strategies exhausted",
            strategies_tried=3,
            last_exception=last_exc
        )
        
        assert failure.component_name == "api"
        assert failure.strategies_tried == 3
        assert "api" in str(failure)


class TestGracefulDegradationIntegration:
    """Integration tests for multi-component scenarios (5 tests)"""
    
    def test_multi_component_degradation(self):
        """Test: Multiple components manage independent states"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        
        # Register component 1
        db_primary = Mock(return_value="db_success")
        framework.register_component("database", db_primary, [])
        
        # Register component 2
        cache_primary = Mock(side_effect=Exception())
        cache_fallback = Mock(return_value="cache_fallback")
        framework.register_component("cache", cache_primary, [cache_fallback])
        
        # Execute both
        framework.execute_with_degradation("database")
        framework.execute_with_degradation("cache")
        
        # DB is healthy, cache is degraded
        assert not framework.is_degraded("database")
        assert framework.is_degraded("cache")
    
    def test_degradation_recovery(self):
        """Test: System recovers when component becomes available"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        primary = Mock(side_effect=Exception())
        fallback = Mock(return_value="fallback")
        framework.register_component("service", primary, [fallback])
        
        # First execution uses fallback
        result1, mode1 = framework.execute_with_degradation("service")
        assert mode1 == "fallback_1"
        assert framework.is_degraded("service")
        
        # Primary becomes available
        primary.side_effect = None
        primary.return_value = "primary_recovered"
        
        # Next execution uses primary
        result2, mode2 = framework.execute_with_degradation("service")
        assert mode2 == "primary"
        assert not framework.is_degraded("service")
    
    def test_concurrent_component_access(self):
        """Test: Thread-safe concurrent access"""
        import threading
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        
        framework = GracefulDegradationFramework()
        primary = Mock(return_value="result")
        framework.register_component("service", primary, [])
        
        results = []
        def execute():
            result, mode = framework.execute_with_degradation("service")
            results.append(result)
        
        threads = [threading.Thread(target=execute) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        assert all(r == "result" for r in results)
    
    def test_get_degradation_status(self):
        """Test: Status reporting for all components"""
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        framework = GracefulDegradationFramework()
        
        # Setup components
        framework.register_component("db", Mock(return_value="ok"), [])
        framework.register_component("cache", Mock(side_effect=Exception()), [Mock()])
        
        # Execute
        framework.execute_with_degradation("db")
        framework.execute_with_degradation("cache")
        
        # Get status
        status = framework.get_degradation_status()
        assert status["db"]["is_degraded"] == False
        assert status["cache"]["is_degraded"] == True
        assert status["db"]["current_mode"] == "primary"
        assert status["cache"]["current_mode"] == "fallback_1"
    
# ===== Pytest Configuration & Markers =====

@pytest.mark.unit
class TestGracefulDegradationFrameworkUnit:
    """Marked unit tests"""
    pass


@pytest.mark.integration  
class TestGracefulDegradationIntegrationMarked:
    """Marked integration tests"""
    pass


# ===== Test Execution Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
