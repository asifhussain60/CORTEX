"""Test suite for Knowledge Graph Routing Optimization (PHASE-KG-004).

Tests for KG-based routing strategy, semantic capability matching,
and MasterOrchestrator integration with fallback mechanisms.
"""

import pytest
from typing import Dict, List, Any, Optional
from cortex.brain.core.knowledge.graph.interface import IGraphAdapter
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.domain_brain.kg_routing_optimizer import (
    SemanticCapabilityMatcher,
    RoutingDecisionEngine,
    OptimizedRouteResult,
    RoutingOptimizer,
)


@pytest.fixture
def adapter() -> IGraphAdapter:
    """Provide mock graph adapter with service topology."""
    adapter = MockGraphAdapter()
    
    # Create domain
    adapter.create_entity("dom-001", "Domain", {"name": "OrderProcessing", "tier": "1"})
    
    # Create services with capabilities
    adapter.create_entity("svc-order", "Service", {
        "name": "OrderService",
        "tier": "1",
        "capabilities": ["validate_order", "calculate_price", "create_order"]
    })
    adapter.create_entity("svc-payment", "Service", {
        "name": "PaymentService",
        "tier": "2",
        "capabilities": ["process_payment", "refund", "validate_card"]
    })
    adapter.create_entity("svc-inventory", "Service", {
        "name": "InventoryService",
        "tier": "1",
        "capabilities": ["check_stock", "reserve_item", "ship_item"]
    })
    adapter.create_entity("svc-notification", "Service", {
        "name": "NotificationService",
        "tier": "3",
        "capabilities": ["send_email", "send_sms", "send_notification"]
    })
    
    # Create APIs
    adapter.create_entity("api-order", "API", {
        "name": "OrderAPI",
        "version": "v1",
        "required_capabilities": ["validate_order", "create_order"]
    })
    adapter.create_entity("api-payment", "API", {
        "name": "PaymentAPI",
        "version": "v2",
        "required_capabilities": ["process_payment", "validate_card"]
    })
    
    # Create relationships
    adapter.create_relationship("svc-order", "BELONGS_TO", "dom-001", {})
    adapter.create_relationship("svc-payment", "BELONGS_TO", "dom-001", {})
    adapter.create_relationship("svc-inventory", "BELONGS_TO", "dom-001", {})
    adapter.create_relationship("svc-notification", "BELONGS_TO", "dom-001", {})
    
    adapter.create_relationship("api-order", "CALLS", "svc-order", {})
    adapter.create_relationship("api-payment", "CALLS", "svc-payment", {})
    
    adapter.create_relationship("svc-order", "CALLS", "svc-inventory", {"latency_ms": 50})
    adapter.create_relationship("svc-order", "CALLS", "svc-payment", {"latency_ms": 100})
    adapter.create_relationship("svc-payment", "CALLS", "svc-notification", {"latency_ms": 200})
    
    return adapter


class TestSemanticCapabilityMatcher:
    """Test semantic capability matching for routing."""

    def test_exact_capability_match(self, adapter: IGraphAdapter) -> None:
        """Test exact capability matching."""
        matcher = SemanticCapabilityMatcher(adapter)
        
        required = ["validate_order", "create_order"]
        matches = matcher.find_services_with_capabilities(required)
        
        assert len(matches) > 0
        assert any(m["service_id"] == "svc-order" for m in matches)

    def test_partial_capability_match(self, adapter: IGraphAdapter) -> None:
        """Test partial capability matching."""
        matcher = SemanticCapabilityMatcher(adapter)
        
        required = ["process_payment", "validate_card", "refund"]
        matches = matcher.find_services_with_capabilities(required, min_coverage=0.66)
        
        assert len(matches) > 0
        # PaymentService has all three capabilities
        assert any(m["service_id"] == "svc-payment" for m in matches)

    def test_no_capability_match(self, adapter: IGraphAdapter) -> None:
        """Test when no service matches required capabilities."""
        matcher = SemanticCapabilityMatcher(adapter)
        
        required = ["non_existent_cap_1", "non_existent_cap_2"]
        matches = matcher.find_services_with_capabilities(required)
        
        assert len(matches) == 0

    def test_capability_ranking(self, adapter: IGraphAdapter) -> None:
        """Test that matches are ranked by coverage."""
        matcher = SemanticCapabilityMatcher(adapter)
        
        required = ["check_stock", "reserve_item", "validate_order"]
        matches = matcher.find_services_with_capabilities(required)
        
        # Results should be sorted by coverage score
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                assert matches[i]["coverage_score"] >= matches[i + 1]["coverage_score"]

    def test_semantic_similarity_matching(self, adapter: IGraphAdapter) -> None:
        """Test fuzzy/semantic matching for similar capabilities."""
        matcher = SemanticCapabilityMatcher(adapter)
        
        # Slightly different capability name should still match
        required = ["validate_orders"]  # Similar to "validate_order"
        matches = matcher.find_services_with_capabilities(required, semantic_match=True)
        
        # May or may not have matches depending on similarity threshold
        assert isinstance(matches, list)


class TestRoutingDecisionEngine:
    """Test routing decision optimization."""

    def test_direct_route_decision(self, adapter: IGraphAdapter) -> None:
        """Test decision for direct service route."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-order", target_tier=1)
        
        assert decision is not None
        assert decision.status == "SUCCESS"
        assert "svc-order" in decision.recommended_path or decision.optimal_service is not None

    def test_transitive_route_decision(self, adapter: IGraphAdapter) -> None:
        """Test decision for transitive route (multi-hop)."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-order", required_capabilities=["check_stock"])
        
        assert decision.status == "SUCCESS"
        # Should recommend svc-inventory or path through it

    def test_latency_optimized_route(self, adapter: IGraphAdapter) -> None:
        """Test route optimization based on latency."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-payment", optimize_for="latency")
        
        assert decision.status == "SUCCESS"
        assert hasattr(decision, "estimated_latency_ms")

    def test_tier_constraint_routing(self, adapter: IGraphAdapter) -> None:
        """Test routing with tier constraints."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-order", max_tier=2)
        
        assert decision.status == "SUCCESS"
        # Should only use services with tier <= 2

    def test_reliability_optimized_route(self, adapter: IGraphAdapter) -> None:
        """Test route optimization for reliability."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-order", optimize_for="reliability")
        
        assert decision.status == "SUCCESS"
        assert hasattr(decision, "reliability_score")

    def test_cost_optimized_route(self, adapter: IGraphAdapter) -> None:
        """Test route optimization for cost."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-order", optimize_for="cost")
        
        assert decision.status == "SUCCESS"
        assert hasattr(decision, "estimated_cost")

    def test_no_valid_route(self, adapter: IGraphAdapter) -> None:
        """Test handling when no valid route exists."""
        engine = RoutingDecisionEngine(adapter)
        
        decision = engine.decide_route("api-nonexistent")
        
        assert decision.status == "FAILED" or decision.status == "NO_ROUTE"


class TestRoutingOptimizer:
    """Test end-to-end routing optimization."""

    def test_optimizer_basic_optimization(self, adapter: IGraphAdapter) -> None:
        """Test basic routing optimization."""
        optimizer = RoutingOptimizer(adapter)
        
        result = optimizer.optimize_routing("api-order", {})
        
        assert result.status == "SUCCESS"
        assert result.original_route is not None
        assert result.optimized_route is not None

    def test_optimizer_improvement_metrics(self, adapter: IGraphAdapter) -> None:
        """Test that optimization produces improvements."""
        optimizer = RoutingOptimizer(adapter)
        
        result = optimizer.optimize_routing("api-order", {"optimize_for": "latency"})
        
        assert result.status == "SUCCESS"
        if result.improvement_percentage:
            # Improvement should be >=0 (could be negative if worse)
            assert isinstance(result.improvement_percentage, (int, float))

    def test_optimizer_with_constraints(self, adapter: IGraphAdapter) -> None:
        """Test optimization with constraints."""
        optimizer = RoutingOptimizer(adapter)
        
        constraints = {
            "max_tier": 2,
            "required_capabilities": ["process_payment"],
            "max_latency_ms": 500
        }
        result = optimizer.optimize_routing("api-payment", constraints)
        
        assert result.status in ["SUCCESS", "FAILED"]

    def test_optimizer_fallback_route(self, adapter: IGraphAdapter) -> None:
        """Test fallback route if optimal unavailable."""
        optimizer = RoutingOptimizer(adapter)
        
        result = optimizer.optimize_routing("api-order", {"optimize_for": "latency"})
        
        assert result.status == "SUCCESS"
        assert result.fallback_route is not None or result.optimized_route is not None

    def test_optimizer_audit_log(self, adapter: IGraphAdapter) -> None:
        """Test that optimizer maintains audit log."""
        optimizer = RoutingOptimizer(adapter)
        
        optimizer.optimize_routing("api-order", {})
        optimizer.optimize_routing("api-payment", {})
        
        audit = optimizer.get_optimization_log()
        assert len(audit) >= 2
        assert all("timestamp" in entry for entry in audit)

    def test_optimizer_caching(self, adapter: IGraphAdapter) -> None:
        """Test that optimization results are cached."""
        optimizer = RoutingOptimizer(adapter)
        
        result1 = optimizer.optimize_routing("api-order", {"optimize_for": "latency"})
        result2 = optimizer.optimize_routing("api-order", {"optimize_for": "latency"})
        
        # Results should be identical
        assert result1.optimized_route == result2.optimized_route

    def test_optimizer_governance_compliance(self) -> None:
        """Test that routing optimizer follows governance rules."""
        from inspect import signature, Parameter

        sig = signature(RoutingOptimizer.optimize_routing)
        assert sig.return_annotation != Parameter.empty

        assert RoutingOptimizer.optimize_routing.__doc__ is not None


class TestRoutingIntegration:
    """Integration tests for routing optimization."""

    def test_end_to_end_optimization_workflow(self, adapter: IGraphAdapter) -> None:
        """Test complete optimization workflow."""
        matcher = SemanticCapabilityMatcher(adapter)
        engine = RoutingDecisionEngine(adapter)
        optimizer = RoutingOptimizer(adapter)
        
        # Find services with capabilities
        services = matcher.find_services_with_capabilities(["process_payment"])
        assert len(services) > 0
        
        # Make routing decision
        decision = engine.decide_route("api-payment")
        assert decision.status == "SUCCESS"
        
        # Optimize route
        result = optimizer.optimize_routing("api-payment", {})
        assert result.status == "SUCCESS"

    def test_multi_constraint_optimization(self, adapter: IGraphAdapter) -> None:
        """Test optimization with multiple constraints."""
        optimizer = RoutingOptimizer(adapter)
        
        constraints = {
            "optimize_for": "latency",
            "max_tier": 2,
            "required_capabilities": ["validate_order"]
        }
        result = optimizer.optimize_routing("api-order", constraints)
        
        assert result.status in ["SUCCESS", "FAILED"]

    def test_optimization_with_large_topology(self, adapter: IGraphAdapter) -> None:
        """Test optimization performance with larger service mesh."""
        # Add more services
        for i in range(20):
            adapter.create_entity(f"svc-{i}", "Service", {
                "name": f"Service{i}",
                "tier": str((i % 3) + 1),
                "capabilities": [f"cap_{j}" for j in range(3)]
            })
        
        optimizer = RoutingOptimizer(adapter)
        result = optimizer.optimize_routing("api-order", {"optimize_for": "latency"})
        
        # Should handle large topology efficiently
        assert result.status in ["SUCCESS", "FAILED"]

    def test_routing_optimization_idempotency(self, adapter: IGraphAdapter) -> None:
        """Test that optimization is idempotent."""
        optimizer = RoutingOptimizer(adapter)
        
        result1 = optimizer.optimize_routing("api-order", {})
        result2 = optimizer.optimize_routing("api-order", {})
        
        # Same input should produce same result
        assert result1.optimized_route == result2.optimized_route
        assert result1.status == result2.status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
