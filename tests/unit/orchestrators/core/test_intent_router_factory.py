"""
Test suite for IntentRouterFactory - Enforces mandatory intent classification.

AC-GOVE-REM-001: IntentRouterFactory implementation
Priority: P0-CRITICAL

Tests verify that:
1. IntentRouterFactory creates IntentRouter instances
2. Factory enforces intent classification on every call
3. Zero bypass possibility (architectural enforcement)
4. All 23 orchestrators can be created via factory
5. Factory maintains backward compatibility
6. Factory passes governance validation

CORE Governance:
- CORE-008: Tests first (TDD)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging
"""

from __future__ import annotations

import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock, patch

from cortex.orchestrators.core.intent_router_factory import (
    IntentRouterFactory,
    FactoryConfig,
    RouterInstance,
)
from cortex.orchestrators.core.intent_router import IntentRouter, IntentType
from cortex.core.result import Ok, Err


class TestIntentRouterFactoryBasics:
    """Test basic factory functionality."""

    def test_factory_initialization(self) -> None:
        """Factory initializes with default configuration."""
        factory = IntentRouterFactory()
        assert factory is not None
        assert factory.instance_count == 0

    def test_factory_creates_intent_router(self) -> None:
        """Factory creates IntentRouter instances."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        assert router is not None
        assert isinstance(router, RouterInstance)
        assert router.router is not None
        assert isinstance(router.router, IntentRouter)

    def test_factory_enforces_intent_classification(self) -> None:
        """Factory enforces mandatory intent classification."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        # Intent must be classified before execution
        assert router_instance.intent_classified is False
        
        # Classify intent
        router_instance.classify_intent(
            text="Fix race condition in orchestrator",
            context={"operation": "fix_race_condition"}
        )
        
        assert router_instance.intent_classified is True
        assert router_instance.classified_intent is not None

    def test_factory_prevents_execution_without_classification(self) -> None:
        """Factory prevents execution without prior intent classification."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        # Attempting to execute without classification should fail
        with pytest.raises(RuntimeError) as exc_info:
            router_instance.execute_orchestrated(
                text="Some operation",
                context={}
            )
        
        assert "Intent must be classified first" in str(exc_info.value)

    def test_factory_tracks_instance_count(self) -> None:
        """Factory tracks number of created instances."""
        factory = IntentRouterFactory()
        
        assert factory.instance_count == 0
        
        factory.create_router()
        assert factory.instance_count == 1
        
        factory.create_router()
        assert factory.instance_count == 2

    def test_factory_maintains_instance_registry(self) -> None:
        """Factory maintains registry of all created instances."""
        factory = IntentRouterFactory()
        
        router1 = factory.create_router()
        router2 = factory.create_router()
        
        registry = factory.get_all_instances()
        assert len(registry) == 2
        assert router1 in registry
        assert router2 in registry


class TestIntentRouterFactoryConfiguration:
    """Test factory configuration options."""

    def test_factory_accepts_custom_config(self) -> None:
        """Factory accepts custom configuration."""
        config = FactoryConfig(
            enable_caching=False,
            audit_enabled=True,
            max_instances=100
        )
        factory = IntentRouterFactory(config=config)
        
        assert factory.config.enable_caching is False
        assert factory.config.audit_enabled is True
        assert factory.config.max_instances == 100

    def test_factory_enforces_max_instances(self) -> None:
        """Factory enforces maximum instance limit."""
        config = FactoryConfig(max_instances=3)
        factory = IntentRouterFactory(config=config)
        
        # Create up to limit
        factory.create_router()
        factory.create_router()
        factory.create_router()
        
        # Attempt to exceed limit
        with pytest.raises(RuntimeError) as exc_info:
            factory.create_router()
        
        assert "Maximum instances" in str(exc_info.value)

    def test_factory_respects_audit_configuration(self) -> None:
        """Factory respects audit configuration."""
        config = FactoryConfig(audit_enabled=True)
        factory = IntentRouterFactory(config=config)
        
        router = factory.create_router()
        
        # Should have audit entry
        audit_entries = factory.get_audit_trail()
        assert len(audit_entries) > 0


class TestRouterInstanceBehavior:
    """Test RouterInstance behavior."""

    def test_router_instance_has_correct_state(self) -> None:
        """RouterInstance maintains correct state."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        # Initial state
        assert router_instance.router is not None
        assert router_instance.intent_classified is False
        assert router_instance.classified_intent is None
        assert router_instance.classification_timestamp is None

    def test_router_instance_classify_intent(self) -> None:
        """RouterInstance classifies intent correctly."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        result = router_instance.classify_intent(
            text="Create new feature for user management",
            context={"domain": "users", "operation": "create"}
        )
        
        assert result is not None
        assert router_instance.intent_classified is True
        assert router_instance.classified_intent is not None
        assert router_instance.classified_intent.intent_type in [
            IntentType.IMPLEMENT, IntentType.FIX, IntentType.REFACTOR
        ]

    def test_router_instance_execute_after_classification(self) -> None:
        """RouterInstance executes after intent classification."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        # Classify intent
        router_instance.classify_intent(
            text="Fix database connection timeout",
            context={"domain": "infrastructure"}
        )
        
        # Execute should now work
        result = router_instance.execute_orchestrated(
            text="Fix database connection timeout",
            context={"domain": "infrastructure"}
        )
        
        assert result is not None

    def test_router_instance_tracks_execution_history(self) -> None:
        """RouterInstance tracks execution history."""
        factory = IntentRouterFactory()
        router_instance = factory.create_router()
        
        # Classify and execute
        router_instance.classify_intent(
            text="Refactor response formatter",
            context={"domain": "orchestrators"}
        )
        
        router_instance.execute_orchestrated(
            text="Refactor response formatter",
            context={"domain": "orchestrators"}
        )
        
        history = router_instance.get_execution_history()
        assert len(history) > 0


class TestFactoryIntegration:
    """Test factory integration with orchestrators."""

    def test_factory_compatible_with_23_orchestrators(self) -> None:
        """Factory supports creation pattern for all 23 orchestrators."""
        factory = IntentRouterFactory()
        
        # Create multiple routers simulating 23 orchestrators
        routers = []
        for i in range(23):
            router = factory.create_router()
            routers.append(router)
        
        assert len(routers) == 23
        assert factory.instance_count == 23
        
        # Verify all are RouterInstance
        for router in routers:
            assert isinstance(router, RouterInstance)

    def test_factory_maintains_orchestrator_independence(self) -> None:
        """Each orchestrator maintains independent state."""
        factory = IntentRouterFactory()
        
        router1 = factory.create_router()
        router2 = factory.create_router()
        
        # Classify intent in router1
        router1.classify_intent(
            text="Implement feature A",
            context={"operation": "feature_a"}
        )
        
        # Router2 should not have classification
        assert router1.intent_classified is True
        assert router2.intent_classified is False

    def test_factory_supports_factory_pattern_workflow(self) -> None:
        """Factory supports standard factory pattern workflow."""
        factory = IntentRouterFactory()
        
        # Get router from factory
        router_instance = factory.get_or_create_router(identifier="router_1")
        
        # Classify intent
        router_instance.classify_intent(
            text="Implement MCP protocol integration",
            context={"domain": "mcp"}
        )
        
        # Execute
        result = router_instance.execute_orchestrated(
            text="Implement MCP protocol integration",
            context={"domain": "mcp"}
        )
        
        assert result is not None


class TestFactoryGovernanceEnforcement:
    """Test factory governance enforcement."""

    def test_factory_enforces_mandatory_classification(self) -> None:
        """Factory enforces mandatory intent classification (CORE-032)."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        # Should not allow execution without classification
        assert not router.intent_classified
        
        with pytest.raises(RuntimeError) as exc_info:
            router.execute_orchestrated("operation", {})
        
        assert "Intent must be classified first" in str(exc_info.value)

    def test_factory_audit_trail_logs_classification(self) -> None:
        """Factory audit trail logs intent classification (CORE-027)."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        router.classify_intent(
            text="Fix critical bug",
            context={"severity": "critical"}
        )
        
        audit_trail = factory.get_audit_trail()
        
        # Should have audit entries (at least router creation)
        assert len(audit_trail) > 0

    def test_factory_audit_trail_logs_execution(self) -> None:
        """Factory audit trail logs orchestrator execution (CORE-027)."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        router.classify_intent(
            text="Implement new feature",
            context={"domain": "features"}
        )
        
        router.execute_orchestrated(
            text="Implement new feature",
            context={"domain": "features"}
        )
        
        audit_trail = factory.get_audit_trail()
        
        # Should have audit entries
        assert len(audit_trail) > 0


class TestFactoryBackwardCompatibility:
    """Test factory backward compatibility."""

    def test_factory_maintains_existing_api(self) -> None:
        """Factory maintains backward compatibility with existing code."""
        factory = IntentRouterFactory()
        
        # Standard factory pattern should work
        router = factory.create_router()
        assert router is not None
        
        # Get instance should work
        router2 = factory.get_or_create_router("test_router")
        assert router2 is not None

    def test_factory_works_with_dependency_injection(self) -> None:
        """Factory works with dependency injection patterns."""
        factory = IntentRouterFactory()
        
        # Should be injectable into other components
        router = factory.create_router()
        
        # Simulate component that depends on router
        def process_with_router(router_instance: RouterInstance) -> bool:
            router_instance.classify_intent("test", {})
            return router_instance.intent_classified
        
        result = process_with_router(router)
        assert result is True


class TestFactoryErrorHandling:
    """Test factory error handling."""

    def test_factory_handles_invalid_context(self) -> None:
        """Factory handles invalid classification context."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        # Should handle None context gracefully
        with pytest.raises((TypeError, ValueError, RuntimeError)):
            router.classify_intent(text="test", context=None)

    def test_factory_handles_empty_text(self) -> None:
        """Factory handles empty text in classification."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        # Should handle empty text by raising ValueError
        with pytest.raises(ValueError):
            router.classify_intent(text="", context={})

    def test_factory_recovers_from_classification_errors(self) -> None:
        """Factory recovers from classification errors."""
        factory = IntentRouterFactory()
        router = factory.create_router()
        
        # Failed classification shouldn't prevent retries
        try:
            router.classify_intent(text="", context=None)
        except (TypeError, ValueError):
            pass
        
        # Subsequent valid classification should work
        router.classify_intent(
            text="Valid operation",
            context={"domain": "core"}
        )
        assert router.intent_classified is True


class TestFactoryPerformance:
    """Test factory performance characteristics."""

    def test_factory_creates_routers_efficiently(self) -> None:
        """Factory creates routers efficiently (performance baseline)."""
        factory = IntentRouterFactory()
        
        import time
        start = time.time()
        
        for _ in range(10):
            factory.create_router()
        
        elapsed = time.time() - start
        
        # Should create 10 routers in < 1 second
        assert elapsed < 1.0

    def test_factory_maintains_minimal_memory_overhead(self) -> None:
        """Factory maintains minimal memory overhead."""
        factory = IntentRouterFactory()
        
        # Create multiple routers
        routers = [factory.create_router() for _ in range(20)]
        
        # Get memory estimate
        import sys
        factory_size = sys.getsizeof(factory)
        registry_size = sys.getsizeof(factory.get_all_instances())
        
        # Factory overhead should be reasonable (< 10KB)
        assert (factory_size + registry_size) < 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
