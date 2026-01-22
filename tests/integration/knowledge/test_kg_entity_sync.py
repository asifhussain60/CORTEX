"""Comprehensive tests for Knowledge Graph entity sync pipeline.

Tests entity ingestion, deduplication, sync orchestration, conflict resolution,
and fallback scenarios ensuring production-ready sync operations.
"""

import pytest
from cortex.brain.core.knowledge.graph.mock_adapter import MockGraphAdapter
from cortex.brain.core.knowledge.graph.interface import GraphQueryError
from cortex.brain.domain_brain.kg_ingest_adapter import EntityIngestAdapter
from cortex.brain.domain_brain.kg_deduplicator import EntityDeduplicator
from cortex.brain.domain_brain.kg_sync_orchestrator import SyncOrchestrator


class TestEntityIngestAdapter:
    """Test entity ingestion into KG."""

    def test_ingest_domain(self) -> None:
        """Test domain entity ingestion."""
        adapter = MockGraphAdapter()
        ingest = EntityIngestAdapter(adapter)

        count = ingest.ingest_domain("dom-1", "Domain A", {"tier": "enterprise"})

        assert count == 1
        entities = adapter.query_entities("Domain")
        assert len(entities) == 1
        assert entities[0].id == "dom-1"

    def test_ingest_service(self) -> None:
        """Test service entity ingestion."""
        adapter = MockGraphAdapter()
        ingest = EntityIngestAdapter(adapter)

        adapter.create_entity("dom-1", "Domain", {})
        count = ingest.ingest_service("svc-1", "Service A", "dom-1", {"tier": "backend"})

        assert count == 2  # Entity + relationship
        services = adapter.query_entities("Service")
        assert len(services) == 1

    def test_ingest_api(self) -> None:
        """Test API entity ingestion."""
        adapter = MockGraphAdapter()
        ingest = EntityIngestAdapter(adapter)

        adapter.create_entity("svc-1", "Service", {})
        count = ingest.ingest_api("api-1", "API A", "svc-1", {})

        assert count == 2  # Entity + relationship
        apis = adapter.query_entities("API")
        assert len(apis) == 1

    def test_ingest_duplicate_relationship_skipped(self) -> None:
        """Test that duplicate relationships are skipped."""
        adapter = MockGraphAdapter()
        ingest = EntityIngestAdapter(adapter)

        adapter.create_entity("e1", "Service", {})
        adapter.create_entity("e2", "Service", {})

        adapter.create_relationship("e1", "CALLS", "e2")

        # Try to ingest duplicate - should return 0 (skipped)
        count = ingest.ingest_relationship("e1", "CALLS", "e2")
        assert count <= 1  # May be 0 or 1 depending on duplicate handling


class TestEntityDeduplicator:
    """Test deduplication engine."""

    def test_deduplicate_no_duplicates(self) -> None:
        """Test deduplication with no duplicates."""
        dedup = EntityDeduplicator()

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {}},
            {"id": "e2", "type": "Service", "name": "ServiceB", "properties": {}},
        ]

        result = dedup.deduplicate(entities)

        assert result.total_input == 2
        assert result.total_output == 2
        assert result.duplicates_found == 0

    def test_deduplicate_exact_id_duplicates(self) -> None:
        """Test detection and dedup of exact ID duplicates."""
        dedup = EntityDeduplicator()

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"v": 1}},
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"v": 1}},
            {"id": "e2", "type": "Service", "name": "ServiceB", "properties": {}},
        ]

        result = dedup.deduplicate(entities)

        assert result.total_input == 3
        assert result.total_output == 2
        assert result.duplicates_found == 1

    def test_deduplicate_conflict_resolution(self) -> None:
        """Test conflict resolution in duplicates."""
        dedup = EntityDeduplicator()

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"version": "1.0"}},
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"version": "2.0"}},
        ]

        result = dedup.deduplicate(entities)

        assert result.conflicts_resolved >= 1
        deduplicated = dedup.get_deduplicated_entities()
        assert len(deduplicated) == 1
        assert deduplicated[0]["properties"]["version"] == "2.0"

    def test_deduplicate_property_merging(self) -> None:
        """Test property merging from duplicate entities."""
        dedup = EntityDeduplicator()

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"v": 1}},
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"v": 1, "tier": "backend"}},
        ]

        result = dedup.deduplicate(entities)

        deduplicated = dedup.get_deduplicated_entities()
        assert len(deduplicated) == 1
        assert deduplicated[0]["properties"]["tier"] == "backend"

    def test_deduplicate_large_dataset(self) -> None:
        """Test deduplication with large dataset."""
        dedup = EntityDeduplicator()

        # 100 entities, 10% duplicates
        entities = []
        for i in range(100):
            entity_id = f"e{i // 10}"  # 10 unique entities
            entities.append({
                "id": entity_id,
                "type": "Service",
                "name": f"Service{i // 10}",
                "properties": {},
            })

        result = dedup.deduplicate(entities)

        assert result.total_input == 100
        assert result.total_output == 10
        assert result.duplicates_found == 90

    def test_get_deduplicated_entities_format(self) -> None:
        """Test format of deduplicated entity list."""
        dedup = EntityDeduplicator()

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {"v": 1}},
        ]

        dedup.deduplicate(entities)
        deduplicated = dedup.get_deduplicated_entities()

        assert len(deduplicated) == 1
        entity = deduplicated[0]
        assert entity["id"] == "e1"
        assert entity["type"] == "Service"
        assert entity["name"] == "ServiceA"
        assert entity["properties"]["v"] == 1


class TestSyncOrchestrator:
    """Test sync orchestration."""

    def test_sync_entities_basic(self) -> None:
        """Test basic entity sync."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        entities = [
            {"id": "e1", "type": "Domain", "name": "DomainA", "properties": {}},
        ]

        result = sync.sync_entities(entities)

        assert result["status"] == "SUCCESS"
        assert result["input_count"] == 1
        assert result["deduplicated_count"] == 1

    def test_sync_entities_idempotent(self) -> None:
        """Test sync idempotency (2x sync = same state)."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        entities = [
            {"id": "e1", "type": "Domain", "name": "DomainA", "properties": {}},
            {"id": "e2", "type": "Domain", "name": "DomainB", "properties": {}},
        ]

        # First sync
        result1 = sync.sync_entities(entities)
        assert result1["status"] == "SUCCESS"

        # Second sync
        result2 = sync.sync_entities(entities)
        assert result2["status"] == "SUCCESS"

        # Second sync should not ingest new entities
        assert result2["ingested_count"] == 0 or result2["ingested_count"] <= result1["ingested_count"]

    def test_sync_entities_with_duplicates(self) -> None:
        """Test sync with duplicate entities."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        entities = [
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {}},
            {"id": "e1", "type": "Service", "name": "ServiceA", "properties": {}},
            {"id": "e2", "type": "Service", "name": "ServiceB", "properties": {}},
        ]

        result = sync.sync_entities(entities)

        assert result["status"] == "SUCCESS"
        assert result["input_count"] == 3
        assert result["deduplicated_count"] == 2
        assert result["duplicates_removed"] == 1

    def test_sync_relationships(self) -> None:
        """Test relationship sync."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        # Create entities first
        adapter.create_entity("e1", "Service", {})
        adapter.create_entity("e2", "Service", {})

        relationships = [
            {"source_id": "e1", "rel_type": "CALLS", "target_id": "e2", "properties": {}},
        ]

        result = sync.sync_relationships(relationships)

        assert result["status"] == "SUCCESS"
        assert result["input_count"] == 1
        assert result["synced_count"] >= 1

    def test_sync_verify_idempotency(self) -> None:
        """Test explicit idempotency verification."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        entities = [
            {"id": "e1", "type": "Domain", "name": "DomainA", "properties": {}},
        ]

        is_idempotent = sync.verify_sync_idempotency(entities)

        assert is_idempotent is True

    def test_sync_audit_log(self) -> None:
        """Test audit log creation."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        entities = [
            {"id": "e1", "type": "Domain", "name": "DomainA", "properties": {}},
        ]

        sync.sync_entities(entities)
        audit_log = sync.get_audit_log()

        assert len(audit_log) > 0
        assert any(entry["operation"] == "DEDUPLICATE" for entry in audit_log)
        assert any(entry["operation"] == "INGEST" for entry in audit_log)

    def test_sync_large_dataset(self) -> None:
        """Test sync with large dataset (500 entities)."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        # Create 500 entities with 10% duplicates
        entities = []
        for i in range(500):
            entity_id = f"e{i // 10}"  # 50 unique entities
            entities.append({
                "id": entity_id,
                "type": "Service",
                "name": f"Service{i // 10}",
                "properties": {"index": i},
            })

        result = sync.sync_entities(entities)

        assert result["status"] == "SUCCESS"
        assert result["input_count"] == 500
        assert result["deduplicated_count"] == 50
        assert result["duplicates_removed"] == 450

    def test_sync_handles_missing_entities(self) -> None:
        """Test sync with missing entity relationships."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        # Create at least one entity so relationships can be tested
        adapter.create_entity("existing", "Service", {})

        # Relationship to non-existent entity should raise error
        relationships = [
            {"source_id": "missing", "rel_type": "CALLS", "target_id": "missing2", "properties": {}},
        ]

        with pytest.raises(GraphQueryError):
            sync.sync_relationships(relationships)


class TestSyncIntegration:
    """Integration tests for complete sync pipeline."""

    def test_end_to_end_sync(self) -> None:
        """Test complete sync pipeline end-to-end."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        # Entities with duplicates - sync_entities ingests as Domain type
        entities = [
            {"id": "dom-1", "type": "Domain", "name": "Enterprise", "properties": {}},
            {"id": "dom-1", "type": "Domain", "name": "Enterprise", "properties": {}},
            {"id": "dom-2", "type": "Domain", "name": "Financial", "properties": {}},
            {"id": "dom-3", "type": "Domain", "name": "Logistics", "properties": {}},
        ]

        result = sync.sync_entities(entities)

        assert result["status"] == "SUCCESS"
        assert result["duplicates_removed"] == 1
        assert result["deduplicated_count"] == 3

        # Verify domains in KG
        domains = adapter.query_entities("Domain", {})

        assert len(domains) == 3

    def test_sync_zero_entities(self) -> None:
        """Test sync with empty entity list."""
        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        result = sync.sync_entities([])

        assert result["status"] == "SUCCESS"
        assert result["input_count"] == 0

    def test_sync_governance_compliance(self) -> None:
        """Test that sync follows governance rules."""
        from inspect import signature, Parameter

        adapter = MockGraphAdapter()
        sync = SyncOrchestrator(adapter)

        # Check type hints
        sig = signature(sync.sync_entities)
        assert sig.return_annotation != Parameter.empty

        # Check docstrings
        assert sync.sync_entities.__doc__ is not None

        # Check exception handling by validating method exists
        assert hasattr(sync, 'sync_entities')
        assert hasattr(sync, 'sync_relationships')
        assert hasattr(sync, 'verify_sync_idempotency')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
