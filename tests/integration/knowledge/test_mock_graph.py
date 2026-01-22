"""Integration tests for MockGraphAdapter implementation.

Verifies that the mock graph adapter correctly implements all IGraphAdapter
operations including entity lifecycle, relationship creation, multi-hop
queries, and error handling.
"""

import pytest
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.core.knowledge.graph.interface import (
    GraphQueryError,
    HealthStatus,
)


class TestMockGraphAdapterEntityOperations:
    """Test entity creation and management in mock adapter."""

    def test_create_entity_basic(self) -> None:
        """Test basic entity creation."""
        adapter = MockGraphAdapter()

        entity = adapter.create_entity(
            entity_id="entity-001",
            entity_type="Service",
            properties={"name": "OrderService"},
        )

        assert entity.id == "entity-001"
        assert entity.type == "Service"
        assert entity.properties["name"] == "OrderService"

    def test_create_entity_with_empty_properties(self) -> None:
        """Test entity creation with no properties."""
        adapter = MockGraphAdapter()

        entity = adapter.create_entity(
            entity_id="entity-002", entity_type="Service", properties={}
        )

        assert entity.id == "entity-002"
        assert entity.properties == {}

    def test_create_entity_duplicate_raises_error(self) -> None:
        """Test that duplicate entity ID raises GraphQueryError."""
        adapter = MockGraphAdapter()

        adapter.create_entity("entity-001", "Service", {})

        with pytest.raises(GraphQueryError) as exc_info:
            adapter.create_entity("entity-001", "Service", {})

        assert "already exists" in str(exc_info.value)

    def test_create_entity_all_valid_types(self) -> None:
        """Test entity creation with all valid types."""
        adapter = MockGraphAdapter()

        for entity_type in ["Entity", "Rule", "Service", "API", "Domain"]:
            entity = adapter.create_entity(
                entity_id=f"entity-{entity_type}",
                entity_type=entity_type,
                properties={},
            )
            assert entity.type == entity_type


class TestMockGraphAdapterRelationshipOperations:
    """Test relationship creation and management."""

    def test_create_relationship_basic(self) -> None:
        """Test basic relationship creation."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {})
        adapter.create_entity("service-2", "Service", {})

        rel = adapter.create_relationship(
            source_id="service-1",
            rel_type="CALLS",
            target_id="service-2",
            properties={"count": 1},
        )

        assert rel.source_id == "service-1"
        assert rel.rel_type == "CALLS"
        assert rel.target_id == "service-2"
        assert rel.properties["count"] == 1

    def test_create_relationship_missing_source(self) -> None:
        """Test error when source entity missing."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-2", "Service", {})

        with pytest.raises(GraphQueryError) as exc_info:
            adapter.create_relationship("missing-service", "CALLS", "service-2")

        assert "not found" in str(exc_info.value)

    def test_create_relationship_missing_target(self) -> None:
        """Test error when target entity missing."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {})

        with pytest.raises(GraphQueryError) as exc_info:
            adapter.create_relationship("service-1", "CALLS", "missing-service")

        assert "not found" in str(exc_info.value)

    def test_create_relationship_with_none_properties(self) -> None:
        """Test relationship creation with None properties."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {})
        adapter.create_entity("service-2", "Service", {})

        rel = adapter.create_relationship(
            source_id="service-1",
            rel_type="CALLS",
            target_id="service-2",
            properties=None,
        )

        assert rel.properties == {}


class TestMockGraphAdapterQuerying:
    """Test entity and path querying."""

    def test_query_entities_by_type(self) -> None:
        """Test querying entities by type."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {"name": "ServiceA"})
        adapter.create_entity("service-2", "Service", {"name": "ServiceB"})
        adapter.create_entity("rule-1", "Rule", {"name": "RuleA"})

        services = adapter.query_entities("Service")

        assert len(services) == 2
        assert all(e.type == "Service" for e in services)

    def test_query_entities_no_matches(self) -> None:
        """Test querying when no entities match."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {})

        rules = adapter.query_entities("Rule")

        assert len(rules) == 0

    def test_query_entities_with_filters(self) -> None:
        """Test querying entities with property filters."""
        adapter = MockGraphAdapter()

        adapter.create_entity("service-1", "Service", {"tier": "backend"})
        adapter.create_entity("service-2", "Service", {"tier": "frontend"})
        adapter.create_entity("service-3", "Service", {"tier": "backend"})

        backend_services = adapter.query_entities("Service", {"tier": "backend"})

        assert len(backend_services) == 2
        assert all(e.properties["tier"] == "backend" for e in backend_services)

    def test_query_entities_invalid_type_raises_error(self) -> None:
        """Test querying with empty type raises error."""
        adapter = MockGraphAdapter()

        with pytest.raises(GraphQueryError):
            adapter.query_entities("")

    def test_query_paths_single_hop(self) -> None:
        """Test single-hop path queries."""
        adapter = MockGraphAdapter()

        adapter.create_entity("s1", "Service", {})
        adapter.create_entity("s2", "Service", {})
        adapter.create_entity("s3", "Service", {})

        adapter.create_relationship("s1", "CALLS", "s2")
        adapter.create_relationship("s1", "CALLS", "s3")

        paths = adapter.query_paths("s1", max_hops=1)

        assert len(paths) == 2
        assert all(p.length == 1 for p in paths)
        assert all(p.nodes[0] == "s1" for p in paths)

    def test_query_paths_multi_hop(self) -> None:
        """Test multi-hop path queries."""
        adapter = MockGraphAdapter()

        adapter.create_entity("s1", "Service", {})
        adapter.create_entity("s2", "Service", {})
        adapter.create_entity("s3", "Service", {})

        adapter.create_relationship("s1", "CALLS", "s2")
        adapter.create_relationship("s2", "CALLS", "s3")

        paths = adapter.query_paths("s1", max_hops=2)

        # Should find: s1->s2 (1 hop) and s1->s2->s3 (2 hops)
        assert len(paths) >= 2
        assert any(p.length == 1 for p in paths)
        assert any(p.length == 2 for p in paths)

    def test_query_paths_with_rel_type_filter(self) -> None:
        """Test path queries with relationship type filter."""
        adapter = MockGraphAdapter()

        adapter.create_entity("s1", "Service", {})
        adapter.create_entity("s2", "Service", {})
        adapter.create_entity("s3", "Service", {})

        adapter.create_relationship("s1", "CALLS", "s2")
        adapter.create_relationship("s1", "DEPENDS_ON", "s3")

        calls_paths = adapter.query_paths("s1", rel_types=["CALLS"], max_hops=1)

        assert len(calls_paths) == 1
        assert calls_paths[0].nodes == ["s1", "s2"]

    def test_query_paths_invalid_source_raises_error(self) -> None:
        """Test error when source entity doesn't exist."""
        adapter = MockGraphAdapter()

        with pytest.raises(GraphQueryError):
            adapter.query_paths("missing-entity")

    def test_query_paths_invalid_max_hops_raises_error(self) -> None:
        """Test error for invalid max_hops values."""
        adapter = MockGraphAdapter()

        adapter.create_entity("s1", "Service", {})

        with pytest.raises(GraphQueryError):
            adapter.query_paths("s1", max_hops=0)

        with pytest.raises(GraphQueryError):
            adapter.query_paths("s1", max_hops=4)


class TestMockGraphAdapterDeletion:
    """Test entity and relationship deletion."""

    def test_delete_entity_success(self) -> None:
        """Test successful entity deletion."""
        adapter = MockGraphAdapter()

        adapter.create_entity("entity-1", "Service", {})

        result = adapter.delete_entity("entity-1")

        assert result is True
        assert len(adapter.query_entities("Service")) == 0

    def test_delete_entity_not_found(self) -> None:
        """Test deleting non-existent entity returns False."""
        adapter = MockGraphAdapter()

        result = adapter.delete_entity("missing-entity")

        assert result is False

    def test_delete_entity_removes_relationships(self) -> None:
        """Test that deleting entity also deletes its relationships."""
        adapter = MockGraphAdapter()

        adapter.create_entity("s1", "Service", {})
        adapter.create_entity("s2", "Service", {})
        adapter.create_relationship("s1", "CALLS", "s2")

        adapter.delete_entity("s1")

        # Query s2 - should have no incoming relationships
        paths = adapter.query_paths("s2")
        assert len(paths) == 0


class TestMockGraphAdapterHealth:
    """Test health check functionality."""

    def test_health_check_healthy(self) -> None:
        """Test health check on healthy adapter."""
        adapter = MockGraphAdapter()

        status = adapter.health_check()

        assert status.value == "healthy"

    def test_health_check_can_set_unhealthy(self) -> None:
        """Test setting adapter to unhealthy state."""
        adapter = MockGraphAdapter()

        adapter.set_health(False)
        status = adapter.health_check()

        assert status.value == "unhealthy"

    def test_health_check_respects_timeout_parameter(self) -> None:
        """Test that health check accepts timeout parameter."""
        adapter = MockGraphAdapter()

        # Should not raise even with timeout parameter
        status = adapter.health_check(timeout_seconds=1.0)

        assert status.value == "healthy"


class TestMockGraphAdapterIntegration:
    """Integration tests with complex scenarios."""

    def test_complete_entity_lifecycle(self) -> None:
        """Test complete entity lifecycle: create, query, delete."""
        adapter = MockGraphAdapter()

        # Create
        e1 = adapter.create_entity("service-1", "Service", {"tier": "backend"})
        assert e1.id == "service-1"

        # Query
        services = adapter.query_entities("Service")
        assert len(services) == 1

        # Delete
        deleted = adapter.delete_entity("service-1")
        assert deleted is True

        # Query again
        services = adapter.query_entities("Service")
        assert len(services) == 0

    def test_complex_relationship_network(self) -> None:
        """Test building and querying complex relationship network."""
        adapter = MockGraphAdapter()

        # Create network: s1 -> s2 -> s3, s1 -> s4
        for i in range(1, 5):
            adapter.create_entity(f"s{i}", "Service", {})

        adapter.create_relationship("s1", "CALLS", "s2")
        adapter.create_relationship("s2", "CALLS", "s3")
        adapter.create_relationship("s1", "DEPENDS_ON", "s4")

        # Query paths from s1
        all_paths = adapter.query_paths("s1", max_hops=3)

        # Should find s1->s2, s1->s2->s3, s1->s4
        assert len(all_paths) >= 3

        # Query only CALLS relationships
        call_paths = adapter.query_paths("s1", rel_types=["CALLS"], max_hops=3)

        # Should find s1->s2, s1->s2->s3
        assert len(call_paths) >= 2

    def test_adapter_clear(self) -> None:
        """Test clearing all data from adapter."""
        adapter = MockGraphAdapter()

        adapter.create_entity("e1", "Service", {})
        adapter.create_entity("e2", "Service", {})

        assert len(adapter.query_entities("Service")) == 2

        adapter.clear()

        assert len(adapter.query_entities("Service")) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
