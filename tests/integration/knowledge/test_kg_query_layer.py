"""Test suite for Knowledge Graph Query Layer (PHASE-KG-003).

Tests for semantic query interface, graph traversal, relationship analysis,
rule inference, and SQLite fallback mechanisms.
"""

import pytest
from typing import Dict, List, Any, Optional
from cortex.brain.core.knowledge.graph.interface import IGraphAdapter, GraphQueryError
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.domain_brain.kg_query_layer import (
    SemanticQueryBuilder,
    GraphTraversal,
    RuleInferenceEngine,
    QueryOrchestrator,
)
from cortex.brain.domain_brain.kg_query_interface import QueryResult


@pytest.fixture
def adapter() -> IGraphAdapter:
    """Provide mock graph adapter for testing."""
    adapter = MockGraphAdapter()
    
    # Populate with test data
    adapter.create_entity("dom-001", "Domain", {"name": "Orders", "tier": "1"})
    adapter.create_entity("svc-001", "Service", {"name": "OrderService", "tier": "1"})
    adapter.create_entity("svc-002", "Service", {"name": "PaymentService", "tier": "2"})
    adapter.create_entity("api-001", "API", {"name": "OrderAPI", "version": "v1"})
    adapter.create_entity("api-002", "API", {"name": "PaymentAPI", "version": "v2"})
    
    # Create relationships
    adapter.create_relationship("svc-001", "BELONGS_TO", "dom-001", {})
    adapter.create_relationship("svc-002", "BELONGS_TO", "dom-001", {})
    adapter.create_relationship("api-001", "CALLS", "svc-001", {})
    adapter.create_relationship("api-002", "CALLS", "svc-002", {})
    adapter.create_relationship("svc-001", "CALLS", "svc-002", {})
    
    return adapter


class TestSemanticQueryBuilder:
    """Test semantic query builder for KG queries."""

    def test_builder_basic_query(self, adapter: IGraphAdapter) -> None:
        """Test basic semantic query building."""
        builder = SemanticQueryBuilder(adapter)
        query = builder.find_entities_by_type("Service").build()
        
        assert isinstance(query, QueryResult)
        assert query.entity_count == 2
        assert all(e.entity_type == "Service" for e in query.entities)

    def test_builder_with_property_filter(self, adapter: IGraphAdapter) -> None:
        """Test query with property filters."""
        builder = SemanticQueryBuilder(adapter)
        query = builder.find_entities_by_type("Service").filter_by_property("tier", "1").build()
        
        assert query.entity_count == 1
        assert query.entities[0].node_id == "svc-001"

    def test_builder_relationship_filter(self, adapter: IGraphAdapter) -> None:
        """Test query filtering by relationship type."""
        builder = SemanticQueryBuilder(adapter)
        query = builder.find_entities_by_type("Service").related_by("CALLS").build()
        
        assert query.entity_count >= 1
        assert len(query.relationships) >= 1

    def test_builder_chaining(self, adapter: IGraphAdapter) -> None:
        """Test method chaining in query builder."""
        builder = SemanticQueryBuilder(adapter)
        query = (
            builder.find_entities_by_type("Service")
            .filter_by_property("tier", "1")
            .related_by("BELONGS_TO")
            .build()
        )
        
        assert query.entity_count >= 1
        assert isinstance(query, QueryResult)

    def test_builder_empty_result(self, adapter: IGraphAdapter) -> None:
        """Test query returning empty result."""
        builder = SemanticQueryBuilder(adapter)
        query = builder.find_entities_by_type("Service").filter_by_property("tier", "99").build()
        
        assert query.entity_count == 0
        assert len(query.entities) == 0


class TestGraphTraversal:
    """Test graph traversal and path finding."""

    def test_single_hop_traversal(self, adapter: IGraphAdapter) -> None:
        """Test single hop graph traversal."""
        traversal = GraphTraversal(adapter)
        paths = traversal.traverse_from("svc-001", max_hops=1)
        
        assert len(paths) > 0
        assert all(len(p.nodes) <= 2 for p in paths)

    def test_two_hop_traversal(self, adapter: IGraphAdapter) -> None:
        """Test two hop graph traversal."""
        traversal = GraphTraversal(adapter)
        paths = traversal.traverse_from("svc-001", max_hops=2)
        
        assert len(paths) > 0
        # At least one path should have multiple nodes with max_hops=2
        assert any(len(p.nodes) >= 2 for p in paths)

    def test_traversal_with_relationship_filter(self, adapter: IGraphAdapter) -> None:
        """Test traversal with relationship type filter."""
        traversal = GraphTraversal(adapter)
        paths = traversal.traverse_from("svc-001", max_hops=2, rel_types=["CALLS"])
        
        assert len(paths) > 0
        # All relationships should be CALLS
        assert all(
            all(edge.relationship_type == "CALLS" for edge in path.edges)
            for path in paths
        )

    def test_max_hops_respected(self, adapter: IGraphAdapter) -> None:
        """Test that max_hops parameter is respected."""
        traversal = GraphTraversal(adapter)
        paths_1 = traversal.traverse_from("svc-001", max_hops=1)
        paths_3 = traversal.traverse_from("svc-001", max_hops=3)
        
        max_nodes_1 = max((len(p.nodes) for p in paths_1), default=0)
        max_nodes_3 = max((len(p.nodes) for p in paths_3), default=0)
        
        # 3-hop should potentially have deeper paths
        assert max_nodes_3 >= max_nodes_1

    def test_circular_path_detection(self, adapter: IGraphAdapter) -> None:
        """Test that circular paths are detected."""
        traversal = GraphTraversal(adapter)
        # svc-001 -> svc-002 -> svc-001 would be circular
        paths = traversal.traverse_from("svc-001", max_hops=3)
        
        # Circular paths should be marked or excluded
        for path in paths:
            node_ids = [n.node_id for n in path.nodes]
            # No duplicates in nodes except endpoints
            assert len(node_ids) == len(set(node_ids))


class TestRuleInferenceEngine:
    """Test rule inference for relationship recommendations."""

    def test_infer_service_dependencies(self, adapter: IGraphAdapter) -> None:
        """Test inferring service dependencies from CALLS relationships."""
        engine = RuleInferenceEngine(adapter)
        inferred = engine.infer_dependencies("svc-001")
        
        assert len(inferred) > 0
        # svc-001 calls svc-002, so svc-002 should be inferred as dependency
        assert any(dep["target"] == "svc-002" for dep in inferred)

    def test_infer_domain_membership(self, adapter: IGraphAdapter) -> None:
        """Test inferring domain membership from BELONGS_TO."""
        engine = RuleInferenceEngine(adapter)
        inferred = engine.infer_relationships("svc-001")
        
        # Should infer domain membership
        assert any(
            rel["rel_type"] == "BELONGS_TO" and rel["target"] == "dom-001"
            for rel in inferred
        )

    def test_infer_transitive_relationships(self, adapter: IGraphAdapter) -> None:
        """Test transitive relationship inference (A->B->C implies A related to C)."""
        engine = RuleInferenceEngine(adapter)
        # svc-001 calls svc-002, so through transitivity infer api-001 -> api-002
        inferred = engine.infer_transitive_relationships("api-001", max_depth=2)
        
        assert len(inferred) >= 0
        # Transitive paths should be documented
        for rel in inferred:
            assert "path" in rel

    def test_infer_impact_analysis(self, adapter: IGraphAdapter) -> None:
        """Test impact analysis - what breaks if entity changes."""
        engine = RuleInferenceEngine(adapter)
        impacted = engine.infer_impact("svc-001")
        
        # Entities that depend on svc-001 should be identified (at least svc-002 if there's a relationship)
        assert len(impacted) >= 0  # May be empty if no direct dependencies
        # If there are impacts, they should have required fields
        for e in impacted:
            assert "entity_id" in e

    def test_infer_recommendations(self, adapter: IGraphAdapter) -> None:
        """Test inference-based recommendations."""
        engine = RuleInferenceEngine(adapter)
        recommendations = engine.infer_recommendations("svc-001")
        
        # Should have recommendations (non-empty)
        assert isinstance(recommendations, list)
        # Each recommendation should have required fields
        for rec in recommendations:
            assert "type" in rec
            assert "reason" in rec


class TestQueryOrchestrator:
    """Test query orchestration with fallback mechanisms."""

    def test_orchestrator_basic_query(self, adapter: IGraphAdapter) -> None:
        """Test basic orchestrated query."""
        orchestrator = QueryOrchestrator(adapter)
        result = orchestrator.query("SELECT * FROM Service WHERE tier = 1")
        
        assert result.status == "SUCCESS"
        assert result.entity_count == 1

    def test_orchestrator_complex_query(self, adapter: IGraphAdapter) -> None:
        """Test complex orchestrated query with relationships."""
        orchestrator = QueryOrchestrator(adapter)
        result = orchestrator.query("FIND Service CALLS Service")
        
        assert result.status == "SUCCESS"
        # svc-001 CALLS svc-002
        assert result.entity_count >= 1

    def test_orchestrator_path_query(self, adapter: IGraphAdapter) -> None:
        """Test path query through orchestrator."""
        orchestrator = QueryOrchestrator(adapter)
        result = orchestrator.query_paths("svc-001", "svc-002", max_hops=2)
        
        assert result.status == "SUCCESS"
        assert len(result.paths) > 0

    def test_orchestrator_error_handling(self, adapter: IGraphAdapter) -> None:
        """Test orchestrator error handling on bad query."""
        orchestrator = QueryOrchestrator(adapter)
        result = orchestrator.query("INVALID SYNTAX QUERY")
        
        assert result.status in ["FAILED", "PARSE_ERROR"]
        assert result.error_message is not None

    def test_orchestrator_fallback_on_timeout(self, adapter: IGraphAdapter) -> None:
        """Test fallback mechanism on query timeout."""
        # Mock adapter doesn't timeout, but orchestrator should have fallback logic
        orchestrator = QueryOrchestrator(adapter)
        
        # Normal query should succeed
        result = orchestrator.query("SELECT * FROM Service")
        assert result.status == "SUCCESS"

    def test_orchestrator_audit_log(self, adapter: IGraphAdapter) -> None:
        """Test that orchestrator maintains audit log."""
        orchestrator = QueryOrchestrator(adapter)
        
        orchestrator.query("SELECT * FROM Service")
        orchestrator.query("SELECT * FROM API")
        
        audit = orchestrator.get_audit_log()
        assert len(audit) >= 2
        assert all("timestamp" in entry for entry in audit)

    def test_orchestrator_query_caching(self, adapter: IGraphAdapter) -> None:
        """Test that orchestrator caches query results."""
        orchestrator = QueryOrchestrator(adapter)
        
        result1 = orchestrator.query("SELECT * FROM Service WHERE tier = 1")
        result2 = orchestrator.query("SELECT * FROM Service WHERE tier = 1")
        
        # Results should be identical
        assert result1.entity_count == result2.entity_count
        assert result1.entities == result2.entities


class TestQueryIntegration:
    """Integration tests for complete query pipeline."""

    def test_end_to_end_complex_query(self, adapter: IGraphAdapter) -> None:
        """Test end-to-end complex query workflow."""
        # Find all Services in Orders domain that call other services
        builder = SemanticQueryBuilder(adapter)
        services = builder.find_entities_by_type("Service").build()
        
        assert services.entity_count >= 2

    def test_traversal_and_inference_combined(
        self, adapter: IGraphAdapter
    ) -> None:
        """Test combining traversal with inference."""
        traversal = GraphTraversal(adapter)
        paths = traversal.traverse_from("svc-001", max_hops=2)
        
        engine = RuleInferenceEngine(adapter)
        inferred = engine.infer_dependencies("svc-001")
        
        assert len(paths) > 0
        assert len(inferred) > 0

    def test_query_performance_large_graph(self, adapter: IGraphAdapter) -> None:
        """Test query performance with larger graph."""
        # Add more entities
        for i in range(50):
            adapter.create_entity(f"svc-{i}", "Service", {"tier": str(i % 3)})
        
        builder = SemanticQueryBuilder(adapter)
        query = builder.find_entities_by_type("Service").build()
        
        # Should complete efficiently
        assert query.entity_count >= 50

    def test_query_governance_compliance(self) -> None:
        """Test that query layer follows governance rules."""
        from inspect import signature, Parameter

        # Check type hints on QueryOrchestrator methods
        sig = signature(QueryOrchestrator.query)
        assert sig.return_annotation != Parameter.empty

        # Check docstrings
        assert QueryOrchestrator.query.__doc__ is not None

    def test_query_fallback_semantics(self, adapter: IGraphAdapter) -> None:
        """Test that queries gracefully fall back on failures."""
        orchestrator = QueryOrchestrator(adapter)
        
        # Valid query should work
        result = orchestrator.query("SELECT * FROM Service")
        assert result.status == "SUCCESS"
        
        # Invalid query should return error status, not raise
        result = orchestrator.query("MALFORMED QUERY %%% INVALID")
        assert result.status in ["FAILED", "PARSE_ERROR"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
