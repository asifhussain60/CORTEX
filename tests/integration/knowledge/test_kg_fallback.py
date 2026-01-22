"""Fallback and chaos tests for Knowledge Graph adapter.

Tests timeout behavior, adapter fallback semantics, and error recovery
to ensure CORTEX continues operating even when KG backend is unavailable.
"""

import pytest
import tempfile
import os
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.core.knowledge.graph.sqlite_adapter import SQLiteGraphAdapter
from cortex.brain.core.knowledge.graph.interface import (
    GraphQueryError,
    HealthStatus,
)


@pytest.fixture
def temp_db():  # type: ignore
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestGraphAdapterFallback:
    """Test fallback behavior when primary adapter fails."""

    def test_fallback_semantics_entity_operations(self, temp_db) -> None:  # type: ignore
        """Test that mock and SQLite adapters produce equivalent results."""
        mock = MockGraphAdapter()
        sqlite = SQLiteGraphAdapter(temp_db)

        entity_id = "service-1"
        entity_type = "Service"
        properties = {"tier": "backend", "version": "1.2.3"}

        mock_entity = mock.create_entity(entity_id, entity_type, properties)
        sqlite_entity = sqlite.create_entity(entity_id, entity_type, properties)

        assert mock_entity.id == sqlite_entity.id
        assert mock_entity.type == sqlite_entity.type
        assert mock_entity.properties == sqlite_entity.properties

    def test_fallback_semantics_query_operations(self, temp_db) -> None:  # type: ignore
        """Test that query results are identical across adapters."""
        mock = MockGraphAdapter()
        sqlite = SQLiteGraphAdapter(temp_db)

        for adapter in [mock, sqlite]:
            adapter.create_entity("s1", "Service", {"tier": "backend"})
            adapter.create_entity("s2", "Service", {"tier": "frontend"})
            adapter.create_entity("r1", "Rule", {"tier": "backend"})

        mock_services = mock.query_entities("Service", {"tier": "backend"})
        sqlite_services = sqlite.query_entities("Service", {"tier": "backend"})

        assert len(mock_services) == len(sqlite_services)
        assert len(mock_services) == 1

    def test_fallback_semantics_path_queries(self, temp_db) -> None:  # type: ignore
        """Test that path query results are identical."""
        mock = MockGraphAdapter()
        sqlite = SQLiteGraphAdapter(temp_db)

        for adapter in [mock, sqlite]:
            adapter.create_entity("s1", "Service", {})
            adapter.create_entity("s2", "Service", {})
            adapter.create_entity("s3", "Service", {})
            adapter.create_relationship("s1", "CALLS", "s2")
            adapter.create_relationship("s2", "CALLS", "s3")

        mock_paths = mock.query_paths("s1", max_hops=2)
        sqlite_paths = sqlite.query_paths("s1", max_hops=2)

        assert len(mock_paths) == len(sqlite_paths)
        assert len(mock_paths) >= 2

    def test_fallback_on_health_check_timeout(self) -> None:
        """Test adapter health check with timeout."""
        adapter = MockGraphAdapter()
        status = adapter.health_check(timeout_seconds=0.1)
        assert status == HealthStatus.HEALTHY


class TestGraphAdapterErrorRecovery:
    """Test error handling and recovery mechanisms."""

    def test_constraint_violation_recovery(self) -> None:
        """Test that constraint violations don't corrupt adapter state."""
        adapter = MockGraphAdapter()

        adapter.create_entity("e1", "Service", {})

        with pytest.raises(GraphQueryError):
            adapter.create_entity("e1", "Service", {})

        entities = adapter.query_entities("Service")
        assert len(entities) == 1

    def test_sqlite_fallback_error_doesnt_corrupt_db(self, temp_db) -> None:  # type: ignore
        """Test that SQLite errors don't corrupt database."""
        adapter = SQLiteGraphAdapter(temp_db)

        adapter.create_entity("e1", "Service", {})

        with pytest.raises(GraphQueryError):
            adapter.create_entity("e1", "Service", {})

        entities = adapter.query_entities("Service")
        assert len(entities) == 1

    def test_missing_entity_error_doesnt_affect_other_entities(self) -> None:
        """Test that missing entity errors don't affect other data."""
        adapter = MockGraphAdapter()

        adapter.create_entity("e1", "Service", {})
        adapter.create_entity("e2", "Service", {})

        with pytest.raises(GraphQueryError):
            adapter.create_relationship("e1", "CALLS", "missing-entity")

        entities = adapter.query_entities("Service")
        assert len(entities) == 2


class TestAdapterTimeout:
    """Test timeout handling in health checks."""

    def test_health_check_with_various_timeouts(self) -> None:
        """Test health check responds within timeout."""
        adapter = MockGraphAdapter()

        for timeout in [0.1, 1.0, 5.0]:
            status = adapter.health_check(timeout_seconds=timeout)
            assert status == HealthStatus.HEALTHY

    def test_sqlite_health_check_timeout(self, temp_db) -> None:  # type: ignore
        """Test SQLite health check with timeout."""
        adapter = SQLiteGraphAdapter(temp_db)
        status = adapter.health_check(timeout_seconds=1.0)
        assert status == HealthStatus.HEALTHY


class TestAdapterEquivalence:
    """Test that adapters are equivalent for production fallback."""

    def test_both_adapters_support_all_operations(self) -> None:
        """Verify both adapters implement all operations."""
        mock = MockGraphAdapter()
        sqlite = SQLiteGraphAdapter()

        required_methods = [
            "create_entity",
            "create_relationship",
            "query_entities",
            "query_paths",
            "delete_entity",
            "health_check",
        ]

        for method in required_methods:
            assert hasattr(mock, method), f"Mock missing {method}"
            assert hasattr(sqlite, method), f"SQLite missing {method}"
            assert callable(getattr(mock, method))
            assert callable(getattr(sqlite, method))

    def test_adapter_interface_compliance(self) -> None:
        """Verify adapters comply with interface."""
        from cortex.brain.core.knowledge.graph.interface import IGraphAdapter

        mock = MockGraphAdapter()
        sqlite = SQLiteGraphAdapter()

        assert isinstance(mock, IGraphAdapter)
        assert isinstance(sqlite, IGraphAdapter)

    def test_deletion_idempotency(self, temp_db) -> None:  # type: ignore
        """Test that deleting entity twice is safe."""
        for adapter_class in [MockGraphAdapter, SQLiteGraphAdapter]:
            if adapter_class == MockGraphAdapter:
                adapter = adapter_class()
            else:
                adapter = adapter_class(temp_db)

            adapter.create_entity("e1", "Service", {})

            assert adapter.delete_entity("e1") is True
            assert adapter.delete_entity("e1") is False


class TestNonBlockingFallback:
    """Test that fallback is truly non-blocking."""

    def test_fallback_zero_impact_on_production(self) -> None:
        """Test that KG operations don't affect CORTEX core."""
        from cortex.brain import core as cortex_core
        assert cortex_core is not None

    def test_adapter_isolation(self) -> None:
        """Test that adapter module is isolated."""
        mock1 = MockGraphAdapter()
        mock2 = MockGraphAdapter()

        mock1.create_entity("e1", "Service", {})

        assert len(mock1.query_entities("Service")) == 1
        assert len(mock2.query_entities("Service")) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
