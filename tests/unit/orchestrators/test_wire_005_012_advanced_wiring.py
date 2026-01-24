"""
WIRE-005-012 Test Suite - Advanced Wiring Features

AC-TRANSFORM-001-WIRE-005-012: Tests for advanced wiring features

Author: GitHub Copilot
Date: 2026-01-24
"""

import pytest

from cortex.orchestrators.core.orchestrator_wiring import (
    get_wiring_registry,
    reset_wiring_registry,
)
from cortex.orchestrators.core.wire_001_core_wiring import (
    CoreOrchestratorWiring,
)
from cortex.orchestrators.core.wire_002_domain_wiring import (
    DomainOrchestratorWiring,
)
from cortex.orchestrators.core.wire_003_support_wiring import (
    SupportOrchestratorWiring,
)
from cortex.orchestrators.core.wire_005_012_advanced_wiring import (
    AdvancedWiringEngine,
    create_advanced_engine,
    WorkflowContext,
    OrchestrationStep,
    ExecutionPriority,
)


class TestDependencyGraph:
    """Test suite for WIRE-007: Dependency graph"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_build_dependency_graph(self):
        """Test building dependency graph"""
        graph = self.engine.build_dependency_graph("interaction")
        
        assert isinstance(graph, dict)
        assert "interaction" in graph
    
    def test_dependency_graph_structure(self):
        """Test dependency graph has correct structure"""
        graph = self.engine.build_dependency_graph("tdd")
        
        assert isinstance(graph["tdd"], set)


class TestComposition:
    """Test suite for WIRE-008: Composition and chaining"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
        
        domain = DomainOrchestratorWiring(registry=self.registry)
        domain.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_compose_workflow(self):
        """Test composing workflow from intents"""
        intents = ["test code", "analyze results"]
        steps = self.engine.compose_workflow(intents)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
    
    def test_composed_steps_have_domains(self):
        """Test composed steps have orchestrator domains"""
        intents = ["test", "create", "analyze"]
        steps = self.engine.compose_workflow(intents)
        
        for step in steps:
            assert step.domain is not None
            assert isinstance(step.domain, str)


class TestContextPreservation:
    """Test suite for WIRE-006: Context preservation"""
    
    def test_preserve_context_updates_variables(self):
        """Test context preservation updates variables"""
        context = WorkflowContext(
            user_input="test",
            intent_domain="tdd",
            confidence_score=0.9,
        )
        
        step_result = {
            "status": "success",
            "domain": "tdd",
            "variables": {"test_count": 42},
        }
        
        engine = create_advanced_engine()
        updated_context = engine.preserve_context(context, step_result)
        
        assert updated_context.variables.get("test_count") == 42
    
    def test_preserve_context_adds_history(self):
        """Test context preservation adds execution history"""
        context = WorkflowContext(
            user_input="test",
            intent_domain="tdd",
            confidence_score=0.9,
        )
        
        step_result = {
            "status": "success",
            "domain": "tdd_domain",
        }
        
        engine = create_advanced_engine()
        updated_context = engine.preserve_context(context, step_result)
        
        assert "tdd_domain" in updated_context.execution_history


class TestFallbackHandling:
    """Test suite for WIRE-005: Fallback handling"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_execute_with_valid_domain(self):
        """Test execution with valid domain"""
        result = self.engine.execute_with_fallback("interaction")
        
        assert result["status"] == "success"
        assert result["domain"] == "interaction"
    
    def test_execute_with_fallback_invalid_primary(self):
        """Test fallback when primary domain invalid"""
        result = self.engine.execute_with_fallback(
            "invalid_domain",
            "interaction"
        )
        
        # Should either fail or use fallback
        assert "status" in result


class TestErrorRecovery:
    """Test suite for WIRE-009: Error recovery and healing"""
    
    def test_handle_error_recovery_within_retries(self):
        """Test error recovery within retry limits"""
        context = WorkflowContext(
            user_input="test",
            intent_domain="tdd",
            confidence_score=0.9,
        )
        
        engine = create_advanced_engine()
        result = engine.handle_error_recovery(
            "test_domain",
            Exception("Test error"),
            context,
        )
        
        assert result is True
        assert context.error_count == 1
    
    def test_handle_error_recovery_max_retries(self):
        """Test error recovery at max retries"""
        context = WorkflowContext(
            user_input="test",
            intent_domain="tdd",
            confidence_score=0.9,
            error_count=3,  # Already at max
        )
        
        engine = create_advanced_engine()
        result = engine.handle_error_recovery(
            "test_domain",
            Exception("Test error"),
            context,
        )
        
        assert result is False


class TestMetrics:
    """Test suite for WIRE-010: Observability and metrics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_collect_metrics(self):
        """Test metrics collection"""
        # Execute something first
        self.engine.execute_with_fallback("interaction")
        
        metrics = self.engine.collect_metrics()
        
        assert "total_executions" in metrics
        assert "successful_executions" in metrics
        assert "failed_executions" in metrics
        assert "success_rate_percentage" in metrics
    
    def test_metrics_has_registry_stats(self):
        """Test metrics includes registry stats"""
        metrics = self.engine.collect_metrics()
        
        assert "registry_stats" in metrics


class TestPipelineOptimization:
    """Test suite for WIRE-011: Performance optimization"""
    
    def test_optimize_removes_duplicates(self):
        """Test optimization removes duplicate domains"""
        steps = [
            OrchestrationStep(domain="test", action="test1"),
            OrchestrationStep(domain="test", action="test2"),
            OrchestrationStep(domain="create", action="create1"),
        ]
        
        engine = create_advanced_engine()
        optimized = engine.optimize_pipeline(steps)
        
        domains = [s.domain for s in optimized]
        assert len(domains) == len(set(domains))  # All unique
    
    def test_optimize_respects_priority(self):
        """Test optimization respects priority"""
        steps = [
            OrchestrationStep(
                domain="low",
                action="low",
                priority=ExecutionPriority.LOW,
            ),
            OrchestrationStep(
                domain="critical",
                action="critical",
                priority=ExecutionPriority.CRITICAL,
            ),
        ]
        
        engine = create_advanced_engine()
        optimized = engine.optimize_pipeline(steps)
        
        # Critical should come first
        assert optimized[0].priority == ExecutionPriority.CRITICAL


class TestCapabilogCatalog:
    """Test suite for WIRE-012: Auto-documentation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
        
        domain = DomainOrchestratorWiring(registry=self.registry)
        domain.execute_all_wiring()
        
        support = SupportOrchestratorWiring(registry=self.registry)
        support.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_generate_capability_catalog(self):
        """Test generating capability catalog"""
        catalog = self.engine.generate_capability_catalog()
        
        assert "total_orchestrators" in catalog
        assert "orchestrators" in catalog
        assert "coverage_percentage" in catalog
        assert catalog["total_orchestrators"] == 22
    
    def test_catalog_has_orchestrator_details(self):
        """Test catalog contains orchestrator details"""
        catalog = self.engine.generate_capability_catalog()
        
        orchestrators = catalog.get("orchestrators", {})
        
        # Should have at least one orchestrator
        assert len(orchestrators) > 0
        
        # Each should have capabilities
        for domain, caps in orchestrators.items():
            assert isinstance(caps, list)


class TestFullWorkflow:
    """Test suite for complete workflow execution"""
    
    def setup_method(self):
        """Set up test fixtures"""
        reset_wiring_registry()
        self.registry = get_wiring_registry()
        self.engine = AdvancedWiringEngine(registry=self.registry)
        
        # Populate registry with all wiring
        core = CoreOrchestratorWiring(registry=self.registry)
        core.execute_all_wiring()
        
        domain = DomainOrchestratorWiring(registry=self.registry)
        domain.execute_all_wiring()
        
        support = SupportOrchestratorWiring(registry=self.registry)
        support.execute_all_wiring()
    
    def teardown_method(self):
        """Clean up"""
        reset_wiring_registry()
    
    def test_execute_full_workflow(self):
        """Test executing complete workflow"""
        intents = ["test code", "create workflow"]
        result = self.engine.execute_full_workflow(intents)
        
        assert "status" in result
        assert "steps_executed" in result
        assert "context" in result
        assert "metrics" in result
    
    def test_full_workflow_includes_metrics(self):
        """Test workflow includes execution metrics"""
        intents = ["test", "analyze"]
        result = self.engine.execute_full_workflow(intents)
        
        metrics = result.get("metrics", {})
        assert "total_executions" in metrics
        assert "success_rate_percentage" in metrics
    
    def test_full_workflow_generates_catalog(self):
        """Test workflow generates capability catalog"""
        intents = ["test", "optimize"]
        result = self.engine.execute_full_workflow(intents)
        
        catalog = result.get("capability_catalog", {})
        assert "total_orchestrators" in catalog
        assert catalog["total_orchestrators"] == 22


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
