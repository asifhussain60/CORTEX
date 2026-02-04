"""
Phase 9 Tests - Orchestrator Instantiation & Runtime Wiring

Comprehensive test suite for:
- OrchestratorFactory
- Dependency injection
- Event subscription registration
- Health check integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Any, Dict

from cortex.wiring.orchestrator_factory import (
    OrchestratorFactory,
    OrchestrationBootstrap,
    OrchestrationSpec,
    OrchestrationContext,
)
from cortex.wiring.dependency_injection import (
    DIContainer,
    DIProvider,
    DIParameter,
    ParameterResolver,
)
from cortex.wiring.event_subscription_manager import (
    EventSubscriptionRegistry,
    EventSubscriptionBuilder,
    EventSubscriptionManager,
    EventSubscription,
    EventEmission,
    SubscriptionGraph,
)
from cortex.wiring.health_check import (
    HealthStatus,
    HealthCheckResult,
    HealthCheckExecutor,
    SystemHealthMonitor,
    SystemHealthReport,
)


# ============================================================================
# ORCHESTRATOR FACTORY TESTS
# ============================================================================

class TestOrchestratorFactory:
    """Tests for OrchestratorFactory"""

    def test_factory_initialization(self, tmp_path):
        """Test factory initializes with wiring file"""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
version: "2.0"
orchestrators:
  core: []
""")
        factory = OrchestratorFactory(str(wiring_file))
        assert factory.spec is not None
        assert factory.spec.version == "2.0"

    def test_parse_orchestrator_specs(self, tmp_path):
        """Test parsing orchestrator specifications"""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
version: "2.0"
orchestrators:
  core:
    - name: "TestOrchestrator"
      module: "test.module"
      class: "TestClass"
      tier: 1
      priority: 10
      capabilities: ["test"]
      dependencies: []
""")
        factory = OrchestratorFactory(str(wiring_file))
        factory.parse_orchestrator_specs()
        assert "TestOrchestrator" in factory.orchestration_specs
        assert factory.orchestration_specs["TestOrchestrator"].priority == 10

    def test_resolve_dependencies(self, tmp_path):
        """Test dependency resolution with topological sort"""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
version: "2.0"
orchestrators:
  core:
    - name: "OrchA"
      module: "test.module"
      class: "ClassA"
      tier: 1
      priority: 1
      dependencies: []
    - name: "OrchB"
      module: "test.module"
      class: "ClassB"
      tier: 1
      priority: 2
      dependencies: ["OrchA"]
    - name: "OrchC"
      module: "test.module"
      class: "ClassC"
      tier: 1
      priority: 3
      dependencies: ["OrchA", "OrchB"]
""")
        factory = OrchestratorFactory(str(wiring_file))
        factory.parse_orchestrator_specs()
        factory.resolve_dependencies()
        
        assert factory.context.instantiation_order == ["OrchA", "OrchB", "OrchC"]

    def test_circular_dependency_detection(self, tmp_path):
        """Test detection of circular dependencies"""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
version: "2.0"
orchestrators:
  core:
    - name: "OrchA"
      module: "test.module"
      class: "ClassA"
      tier: 1
      priority: 1
      dependencies: ["OrchB"]
    - name: "OrchB"
      module: "test.module"
      class: "ClassB"
      tier: 1
      priority: 2
      dependencies: ["OrchA"]
""")
        factory = OrchestratorFactory(str(wiring_file))
        factory.parse_orchestrator_specs()
        
        with pytest.raises(ValueError, match="Circular dependencies"):
            factory.resolve_dependencies()


# ============================================================================
# DEPENDENCY INJECTION TESTS
# ============================================================================

class TestDependencyInjection:
    """Tests for DI system"""

    def test_container_register_singleton(self):
        """Test registering singleton instances"""
        container = DIContainer()
        instance = Mock()
        container.register_singleton("test", instance)
        
        retrieved = container.get_instance("test")
        assert retrieved is instance

    def test_container_register_factory(self):
        """Test registering factory functions"""
        container = DIContainer()
        factory = Mock(return_value="created_instance")
        container.register_factory("test", factory)
        
        retrieved = container.get_instance("test")
        assert retrieved == "created_instance"
        factory.assert_called_once()

    def test_container_circular_dependency_detection(self):
        """Test detection of circular dependencies in DI"""
        container = DIContainer()
        
        def factory_a():
            return container.get_instance("b")
        
        def factory_b():
            return container.get_instance("a")
        
        container.register_factory("a", factory_a)
        container.register_factory("b", factory_b)
        
        with pytest.raises(ValueError, match="Circular dependency"):
            container.get_instance("a")

    def test_di_provider_inject(self):
        """Test injecting dependencies into class"""
        provider = DIProvider()
        dep = Mock()
        provider.container.register_singleton("dependency", dep)
        
        class TestClass:
            def __init__(self, dependency):
                self.dependency = dependency
        
        instance = provider.container.inject(TestClass)
        assert instance.dependency is dep


# ============================================================================
# EVENT SUBSCRIPTION TESTS
# ============================================================================

class TestEventSubscriptionRegistry:
    """Tests for event subscription registry"""

    def test_register_subscription(self):
        """Test registering event subscription"""
        registry = EventSubscriptionRegistry()
        sub = EventSubscription("Orch1", "EVENT_TYPE", "on_event_type")
        registry.register_subscription(sub)
        
        subs = registry.get_subscribers("EVENT_TYPE")
        assert len(subs) == 1
        assert subs[0].orchestrator_name == "Orch1"

    def test_register_emission(self):
        """Test registering event emission"""
        registry = EventSubscriptionRegistry()
        emission = EventEmission("Orch1", "EVENT_TYPE")
        registry.register_emission(emission)
        
        emissions = registry.get_emissions("Orch1")
        assert len(emissions) == 1
        assert emissions[0].event_type == "EVENT_TYPE"

    def test_validate_subscriptions(self):
        """Test validation of subscriptions"""
        registry = EventSubscriptionRegistry()
        
        # Register emission
        emission = EventEmission("Orch1", "EVENT_TYPE")
        registry.register_emission(emission)
        
        # Register matching subscription
        sub = EventSubscription("Orch2", "EVENT_TYPE", "on_event_type")
        registry.register_subscription(sub)
        
        assert registry.validate_subscriptions() is True

    def test_validate_subscriptions_missing_emitter(self):
        """Test validation fails for missing emitter"""
        registry = EventSubscriptionRegistry()
        
        # Register subscription without emitter
        sub = EventSubscription("Orch1", "EVENT_TYPE", "on_event_type")
        registry.register_subscription(sub)
        
        assert registry.validate_subscriptions() is False


class TestEventSubscriptionBuilder:
    """Tests for subscription builder"""

    def test_build_from_wiring_spec(self):
        """Test building subscriptions from wiring spec"""
        wiring_spec = {
            'orchestrators': {
                'core': [
                    {
                        'name': 'Orch1',
                        'event_subscriptions': ['EVENT_TYPE'],
                        'event_emissions': []
                    },
                    {
                        'name': 'Orch2',
                        'event_subscriptions': [],
                        'event_emissions': ['EVENT_TYPE']
                    }
                ]
            }
        }
        
        registry = EventSubscriptionBuilder.from_wiring_spec(wiring_spec)
        assert registry.validate_subscriptions() is True


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

class TestHealthCheckExecutor:
    """Tests for health check executor"""

    def test_health_check_healthy_orchestrator(self):
        """Test health check for healthy orchestrator"""
        orch = Mock()
        orch.__class__.__name__ = "TestOrch"
        orch.health_check = Mock(return_value=True)
        
        result = HealthCheckExecutor.execute_health_check(orch)
        assert result.status == HealthStatus.HEALTHY
        assert result.orchestrator_name == "TestOrch"

    def test_health_check_unhealthy_orchestrator(self):
        """Test health check for unhealthy orchestrator"""
        orch = Mock()
        orch.__class__.__name__ = "TestOrch"
        orch.health_check = Mock(return_value=False)
        
        result = HealthCheckExecutor.execute_health_check(orch)
        assert result.status == HealthStatus.UNHEALTHY

    def test_health_check_missing_method(self):
        """Test health check when orchestrator lacks health_check method"""
        orch = Mock(spec=[])  # No health_check method
        orch.__class__.__name__ = "TestOrch"
        
        result = HealthCheckExecutor.execute_health_check(orch)
        assert result.status == HealthStatus.UNKNOWN
        assert "No health_check method" in result.message

    def test_health_check_exception(self):
        """Test health check when health_check raises exception"""
        orch = Mock()
        orch.__class__.__name__ = "TestOrch"
        orch.health_check = Mock(side_effect=Exception("Test error"))
        
        result = HealthCheckExecutor.execute_health_check(orch)
        assert result.status == HealthStatus.UNHEALTHY
        assert "Test error" in result.error


class TestSystemHealthMonitor:
    """Tests for system health monitor"""

    def test_monitor_all_orchestrators(self):
        """Test monitoring health of all orchestrators"""
        orch1 = Mock()
        orch1.__class__.__name__ = "Orch1"
        orch1.health_check = Mock(return_value=True)
        
        orch2 = Mock()
        orch2.__class__.__name__ = "Orch2"
        orch2.health_check = Mock(return_value=True)
        
        orchestrators = {"Orch1": orch1, "Orch2": orch2}
        monitor = SystemHealthMonitor(orchestrators)
        
        results = monitor.check_all_orchestrators()
        assert len(results) == 2
        assert all(r.status == HealthStatus.HEALTHY for r in results.values())

    def test_system_health_report(self):
        """Test generating system health report"""
        orch = Mock()
        orch.__class__.__name__ = "TestOrch"
        orch.health_check = Mock(return_value=True)
        
        orchestrators = {"TestOrch": orch}
        monitor = SystemHealthMonitor(orchestrators)
        
        report = monitor.generate_system_health_report()
        assert report.overall_status == HealthStatus.HEALTHY
        assert report.total_orchestrators == 1
        assert report.healthy_orchestrators == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase9Integration:
    """Integration tests for Phase 9 orchestrator instantiation"""

    def test_end_to_end_orchestration_build(self, tmp_path):
        """Test complete orchestration build process"""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
version: "2.0"
orchestrators:
  core:
    - name: "TestOrch"
      module: "test.module"
      class: "TestClass"
      tier: 1
      priority: 10
      dependencies: []
""")
        
        # Create mock class
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_class = Mock()
            mock_module.TestClass = mock_class
            mock_import.return_value = mock_module
            
            factory = OrchestratorFactory(str(wiring_file))
            context = factory.build()
            
            assert len(context.orchestrators) > 0


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("status,expected", [
    (True, HealthStatus.HEALTHY),
    (False, HealthStatus.UNHEALTHY),
])
def test_health_check_boolean_result(status, expected):
    """Test health check with boolean result"""
    orch = Mock()
    orch.__class__.__name__ = "TestOrch"
    orch.health_check = Mock(return_value=status)
    
    result = HealthCheckExecutor.execute_health_check(orch)
    assert result.status == expected


@pytest.mark.parametrize("tier,priority", [
    (1, 1),
    (2, 50),
    (3, 100),
])
def test_orchestrator_spec_creation(tier, priority):
    """Test creating orchestrator specs with different tiers"""
    spec = OrchestrationSpec(
        name="TestOrch",
        module="test.module",
        class_name="TestClass",
        tier=tier,
        priority=priority,
    )
    assert spec.tier == tier
    assert spec.priority == priority
