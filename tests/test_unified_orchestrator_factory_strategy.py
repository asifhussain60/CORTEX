"""
Tests for Unified Orchestrator Factory Strategy - Track 3 Part A.

Tests orchestrator creation, composition, and wiring capabilities.

AC_START: AC-WAVE7T3-PA-TEST-001
Tests: 18 total (composition: 5, wiring: 5, factory: 5, integration: 3)
"""

import pytest
from cortex.orchestrators.unified_orchestrator_factory_strategy import (
    OrchestratorFactoryStrategy,
    OrchestratorCompositionStrategy,
    OrchestratorWiringStrategy,
    OrchestratorConfig,
    OrchestrationContext,
    OrchestrationWiring,
)


class TestOrchestratorCompositionStrategy:
    """Tests for orchestrator composition."""

    def test_composition_initialization(self):
        """Test initialization."""
        composition = OrchestratorCompositionStrategy()
        assert composition is not None
        assert len(composition.get_supported_operations()) > 0

    def test_compose_sequential(self):
        """Test sequential composition."""
        composition = OrchestratorCompositionStrategy()
        result = composition.compose_sequential([{}, {}, {}])
        assert result["composition_type"] == "sequential"
        assert result["order_preserved"] is True

    def test_compose_parallel(self):
        """Test parallel composition."""
        composition = OrchestratorCompositionStrategy()
        result = composition.compose_parallel([{}, {}, {}])
        assert result["composition_type"] == "parallel"
        assert result["concurrent_execution"] is True

    def test_compose_hierarchical(self):
        """Test hierarchical composition."""
        composition = OrchestratorCompositionStrategy()
        result = composition.compose_hierarchical({"level_1": [{}], "level_2": [{}, {}]})
        assert result["composition_type"] == "hierarchical"
        assert result["levels"] == 2

    def test_resolve_dependencies(self):
        """Test dependency resolution."""
        composition = OrchestratorCompositionStrategy()
        config1 = OrchestratorConfig(
            name="orch1",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap1"],
            dependencies=["orch2"]
        )
        config2 = OrchestratorConfig(
            name="orch2",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap2"]
        )
        result = composition.resolve_dependencies([config1, config2])
        assert len(result) == 2


class TestOrchestratorWiringStrategy:
    """Tests for orchestrator wiring."""

    def test_wiring_initialization(self):
        """Test initialization."""
        wiring = OrchestratorWiringStrategy()
        assert wiring is not None
        assert len(wiring.get_supported_operations()) > 0

    def test_direct_wiring(self):
        """Test direct wiring."""
        from cortex.orchestrators.unified_orchestrator_factory_strategy import OrchestratorInstance
        
        wiring = OrchestratorWiringStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=[]
        )
        instance = OrchestratorInstance(
            name="test",
            instance={},
            capabilities=[],
            status="created",
            created_at=0,
            config=config
        )
        
        result = wiring.direct_wiring([instance])
        assert result["wiring_type"] == "direct"
        assert result["latency_profile"] == "synchronous"

    def test_event_bus_wiring(self):
        """Test event-driven wiring."""
        from cortex.orchestrators.unified_orchestrator_factory_strategy import OrchestratorInstance
        
        wiring = OrchestratorWiringStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.EVENT_DRIVEN,
            capabilities=[]
        )
        instance = OrchestratorInstance(
            name="test",
            instance={},
            capabilities=[],
            status="created",
            created_at=0,
            config=config
        )
        
        result = wiring.event_bus_wiring([instance])
        assert result["wiring_type"] == "event_driven"
        assert result["latency_profile"] == "asynchronous"

    def test_message_queue_wiring(self):
        """Test message queue wiring."""
        from cortex.orchestrators.unified_orchestrator_factory_strategy import OrchestratorInstance
        
        wiring = OrchestratorWiringStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.MESSAGE_QUEUE,
            capabilities=[]
        )
        instance = OrchestratorInstance(
            name="test",
            instance={},
            capabilities=[],
            status="created",
            created_at=0,
            config=config
        )
        
        result = wiring.message_queue_wiring([instance])
        assert result["wiring_type"] == "message_queue"
        assert result["reliability"] == "guaranteed_delivery"

    def test_service_mesh_wiring(self):
        """Test service mesh wiring."""
        from cortex.orchestrators.unified_orchestrator_factory_strategy import OrchestratorInstance
        
        wiring = OrchestratorWiringStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.SERVICE_MESH,
            capabilities=[]
        )
        instance = OrchestratorInstance(
            name="test",
            instance={},
            capabilities=[],
            status="created",
            created_at=0,
            config=config
        )
        
        result = wiring.service_mesh_wiring([instance])
        assert result["wiring_type"] == "service_mesh"
        assert result["deployment_model"] == "distributed"


class TestOrchestratorFactoryStrategy:
    """Tests for factory strategy."""

    def test_factory_initialization(self):
        """Test initialization."""
        factory = OrchestratorFactoryStrategy()
        assert factory is not None
        assert factory.composition is not None
        assert factory.wiring is not None

    def test_get_metadata(self):
        """Test metadata."""
        factory = OrchestratorFactoryStrategy()
        metadata = factory.get_metadata()
        assert metadata["name"] == "OrchestratorFactoryStrategy"
        assert "composition" in metadata["components"]

    def test_create_orchestrator(self):
        """Test orchestrator creation."""
        factory = OrchestratorFactoryStrategy()
        config = OrchestratorConfig(
            name="test_orch",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap1", "cap2"]
        )
        instance = factory.create_orchestrator(config)
        assert instance.name == "test_orch"
        assert instance.status == "created"
        assert len(instance.capabilities) == 2

    def test_compose_orchestrators_sequential(self):
        """Test sequential composition."""
        factory = OrchestratorFactoryStrategy()
        config1 = OrchestratorConfig(
            name="orch1",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap1"]
        )
        config2 = OrchestratorConfig(
            name="orch2",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap2"]
        )
        
        instance1 = factory.create_orchestrator(config1)
        instance2 = factory.create_orchestrator(config2)
        
        result = factory.compose_orchestrators([instance1, instance2], "sequential")
        assert result["composition_type"] == "sequential"

    def test_wire_orchestrators_direct(self):
        """Test direct wiring via factory."""
        factory = OrchestratorFactoryStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap1"]
        )
        instance = factory.create_orchestrator(config)
        
        result = factory.wire_orchestrators([instance], "direct")
        assert result["wiring_type"] == "direct"

    def test_get_created_instances(self):
        """Test getting created instances."""
        factory = OrchestratorFactoryStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=[]
        )
        factory.create_orchestrator(config)
        
        instances = factory.get_created_instances()
        assert "test" in instances

    def test_get_instance_status(self):
        """Test getting instance status."""
        factory = OrchestratorFactoryStrategy()
        config = OrchestratorConfig(
            name="test",
            context=OrchestrationContext.LOCAL,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["cap1", "cap2"]
        )
        factory.create_orchestrator(config)
        
        status = factory.get_instance_status("test")
        assert status is not None
        assert status["status"] == "created"
        assert len(status["capabilities"]) == 2


class TestFactoryStrategyIntegration:
    """Integration tests for factory strategy."""

    def test_complete_workflow(self):
        """Test complete create-compose-wire workflow."""
        factory = OrchestratorFactoryStrategy()
        
        # Create orchestrators
        config1 = OrchestratorConfig(
            name="orch1",
            context=OrchestrationContext.PRODUCTION,
            wiring=OrchestrationWiring.DIRECT,
            capabilities=["analyze", "plan"]
        )
        config2 = OrchestratorConfig(
            name="orch2",
            context=OrchestrationContext.PRODUCTION,
            wiring=OrchestrationWiring.EVENT_DRIVEN,
            capabilities=["execute", "monitor"]
        )
        
        instance1 = factory.create_orchestrator(config1)
        instance2 = factory.create_orchestrator(config2)
        
        # Compose
        composition = factory.compose_orchestrators([instance1, instance2], "sequential")
        assert composition["composition_type"] == "sequential"
        
        # Wire
        wiring = factory.wire_orchestrators([instance1, instance2], "direct")
        assert wiring["wiring_type"] == "direct"

    def test_multiple_wiring_strategies(self):
        """Test multiple wiring strategies."""
        factory = OrchestratorFactoryStrategy()
        
        config = OrchestratorConfig(
            name="multi_wire",
            context=OrchestrationContext.DISTRIBUTED,
            wiring=OrchestrationWiring.SERVICE_MESH,
            capabilities=["multi"]
        )
        instance = factory.create_orchestrator(config)
        
        # Test different wirings
        wirings = ["direct", "event_driven", "message_queue", "service_mesh"]
        for wiring_type in wirings:
            result = factory.wire_orchestrators([instance], wiring_type)
            assert result["wiring_type"] == wiring_type

    def test_context_preservation(self):
        """Test that context is preserved through creation."""
        factory = OrchestratorFactoryStrategy()
        
        contexts = [
            OrchestrationContext.LOCAL,
            OrchestrationContext.TESTING,
            OrchestrationContext.PRODUCTION
        ]
        
        for context in contexts:
            config = OrchestratorConfig(
                name=f"orch_{context.value}",
                context=context,
                wiring=OrchestrationWiring.DIRECT,
                capabilities=[]
            )
            instance = factory.create_orchestrator(config)
            assert instance.config.context == context


# AC_COMPLETE: AC-WAVE7T3-PA-TEST-001 ✅ 18 test cases for factory strategy
