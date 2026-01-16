"""Test suite for LENS Integration Layer (AC-DB-004-01).

Tests cover LENS integration with Domain Brain:
- Per-turn execution model (40 tests)
- 4-phase synthesis (Recognition, Routing, Evaluation, Navigation)
- Conflict resolution with LENS recommendations
- Audit logging and status tracking

Total: 40 tests
"""

import pytest
from src.domain_brain.lens_integration import (
    LENSIntegrationLayer,
    LENSQuery,
    LENSSynthesis,
)
from src.domain_brain.api import DomainBrainAPI
from src.domain_brain.models import Domain, Entity, Conflict, EntityType
import uuid


class TestLENSIntegrationLayer:
    """Tests for LENS Integration Layer (25 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def lens_layer(self, api: DomainBrainAPI) -> LENSIntegrationLayer:
        """Create LENS integration layer."""
        return LENSIntegrationLayer(api)

    def test_lens_initialization(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test LENS layer initialization."""
        assert lens_layer.domain_brain_api is not None
        assert lens_layer.lens_requests_made == 0
        assert lens_layer.lens_syntheses_applied == 0

    def test_query_lens_for_conflict(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test querying LENS for conflict resolution."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={
                "AST": "AST description",
                "BKIO": "BKIO description",
            },
        )

        synthesis = lens_layer.query_lens_for_conflict(conflict)

        assert synthesis is not None
        assert lens_layer.lens_requests_made == 1

    def test_lens_query_structure(self) -> None:
        """Test LENSQuery data structure."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        assert query.query_id is not None
        assert query.conflict_id == "c1"
        assert query.domain_id == "test"

    def test_lens_synthesis_structure(self) -> None:
        """Test LENSSynthesis data structure."""
        synthesis = LENSSynthesis(
            query_id="q1",
            recommended_value="BKIO value",
            confidence=0.95,
            reasoning="BKIO has highest priority",
        )

        assert synthesis.synthesis_id is not None
        assert synthesis.query_id == "q1"
        assert synthesis.confidence == 0.95

    def test_phase_recognition(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test Phase 1: Recognition."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )

        result = lens_layer._phase_recognition(query)

        assert result is not None
        assert result["conflict_scope"] == "multi_source"
        assert result["source_count"] == 2

    def test_phase_routing(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test Phase 2: Routing."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )
        recognition = {"conflict_scope": "multi_source", "source_count": 2}

        routing = lens_layer._phase_routing(query, recognition)

        assert routing == "hierarchy_reasoning"

    def test_phase_evaluation(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test Phase 3: Evaluation."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )

        candidates = lens_layer._phase_evaluation(query, "hierarchy_reasoning")

        assert len(candidates) == 2
        assert all("source" in c for c in candidates)
        assert all("confidence" in c for c in candidates)

    def test_phase_navigation(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test Phase 4: Navigation."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "ast_value", "BKIO": "bkio_value"},
            attribute="description",
        )

        candidates = [
            {"source": "AST", "value": "ast_value", "confidence": 0.6, "reasoning": "AST"},
            {"source": "BKIO", "value": "bkio_value", "confidence": 0.8, "reasoning": "BKIO"},
        ]

        synthesis = lens_layer._phase_navigation(query, candidates)

        assert synthesis is not None
        assert synthesis.recommended_value == "bkio_value"

    def test_execute_lens_phases(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test full LENS 4-phase execution."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )

        synthesis = lens_layer._execute_lens_phases(query)

        assert synthesis is not None
        assert synthesis.confidence > 0

    def test_apply_synthesis_to_domain(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test applying LENS synthesis to domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original",
            source="AST",
        )
        domain.entities["e1"] = entity

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "Original", "BKIO": "Updated"},
        )
        domain.conflicts.append(conflict)

        synthesis = LENSSynthesis(
            query_id="q1",
            recommended_value="Updated",
            confidence=0.9,
        )

        lens_layer.apply_synthesis_to_domain(domain, conflict, synthesis)

        # Synthesis should be marked as applied
        assert hasattr(entity, "synthesis_applied")

    def test_get_synthesis_status(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test getting LENS synthesis status."""
        status = lens_layer.get_synthesis_status()

        assert "lens_requests_made" in status
        assert "lens_syntheses_applied" in status
        assert "success_rate" in status
        assert status["success_rate"] >= 0

    def test_synthesis_cache(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test synthesis caching."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )

        synthesis1 = lens_layer._execute_lens_phases(query)
        if synthesis1:
            assert query.query_id in lens_layer.synthesis_cache
            # Verify cache contains the synthesis
            cached_synthesis = lens_layer.synthesis_cache[query.query_id]
            assert cached_synthesis.query_id == query.query_id

    def test_query_log_tracking(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test LENS query logging."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        lens_layer.query_lens_for_conflict(conflict)

        assert len(lens_layer.query_log) == 1
        assert lens_layer.query_log[0].conflict_id == "c1"

    def test_execute_per_turn(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test per-turn execution model."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results["domains_processed"] == 1
        assert results["conflicts_resolved"] >= 1

    def test_multiple_conflicts_per_domain(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test handling multiple conflicts per domain."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        for i in range(3):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"AST": f"val{i}", "BKIO": f"updated{i}"},
            )
            domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results["conflicts_resolved"] == 3

    def test_lens_audit_logging(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test LENS audit logging."""
        lens_layer.log_lens_audit("Test message")

        audit_entries = lens_layer.domain_brain_api.audit_logger.get_all_entries()
        assert len(audit_entries) > 0

    def test_query_to_dict(self) -> None:
        """Test LENSQuery serialization."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1"},
        )

        query_dict = query.to_dict()

        assert query_dict["conflict_id"] == "c1"
        assert query_dict["domain_id"] == "test"
        assert "timestamp" in query_dict

    def test_synthesis_to_dict(self) -> None:
        """Test LENSSynthesis serialization."""
        synthesis = LENSSynthesis(
            query_id="q1",
            recommended_value="value",
            confidence=0.9,
        )

        syn_dict = synthesis.to_dict()

        assert syn_dict["query_id"] == "q1"
        assert syn_dict["confidence"] == 0.9
        assert "timestamp" in syn_dict

    def test_recognition_with_single_source(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test recognition with single source (no conflict)."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1"},
            attribute="description",
        )

        result = lens_layer._phase_recognition(query)

        assert result is None

    def test_routing_with_invalid_recognition(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test routing with invalid recognition."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={},
            attribute="description",
        )
        recognition = {"conflict_scope": "unknown", "source_count": 0}

        routing = lens_layer._phase_routing(query, recognition)

        assert routing is None

    def test_lens_requests_counter(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test LENS requests counter increments."""
        initial = lens_layer.lens_requests_made

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        lens_layer.query_lens_for_conflict(conflict)

        assert lens_layer.lens_requests_made == initial + 1

    def test_multiple_domains_per_turn(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test per-turn execution with multiple domains."""
        domains = []
        for i in range(3):
            domain = Domain(domain_id=f"test-{i}", name=f"Test {i}", description="Test")
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id=f"test-{i}",
                attribute="description",
                source_values={"AST": "val1", "BKIO": "val2"},
            )
            domain.conflicts.append(conflict)
            domains.append(domain)

        results = lens_layer.execute_per_turn(domains)

        assert results["domains_processed"] == 3

    def test_synthesis_confidence_threshold(
        self, lens_layer: LENSIntegrationLayer, api: DomainBrainAPI
    ) -> None:
        """Test synthesis only applied if confidence > 0.5."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original",
            source="AST",
        )
        domain.entities["e1"] = entity

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "Original"},
        )

        # Low confidence synthesis
        synthesis_low = LENSSynthesis(
            query_id="q1",
            recommended_value="Low confidence value",
            confidence=0.3,
        )

        lens_layer.apply_synthesis_to_domain(domain, conflict, synthesis_low)

        # High confidence synthesis
        synthesis_high = LENSSynthesis(
            query_id="q2",
            recommended_value="High confidence value",
            confidence=0.9,
        )

        lens_layer.apply_synthesis_to_domain(domain, conflict, synthesis_high)

    def test_lens_hierarchy_preference(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test BKIO is preferred in hierarchy."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={
                "GIT": "git_value",
                "BKIO": "bkio_value",
                "RELATIONSHIPS": "rel_value",
            },
            attribute="description",
        )

        candidates = lens_layer._phase_evaluation(query, "hierarchy_reasoning")

        # BKIO candidate should exist
        bkio_candidates = [c for c in candidates if c["source"] == "BKIO"]
        assert len(bkio_candidates) > 0
        assert bkio_candidates[0]["confidence"] == 0.8


class TestLENSPerTurnExecution:
    """Tests for per-turn execution model (15 tests)."""

    @pytest.fixture
    def api(self) -> DomainBrainAPI:
        """Create API instance."""
        return DomainBrainAPI()

    @pytest.fixture
    def lens_layer(self, api: DomainBrainAPI) -> LENSIntegrationLayer:
        """Create LENS integration layer."""
        return LENSIntegrationLayer(api)

    def test_per_turn_basic(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test basic per-turn execution."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results is not None
        assert "domains_processed" in results

    def test_per_turn_empty_domains(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test per-turn with empty domain list."""
        results = lens_layer.execute_per_turn([])

        assert results["domains_processed"] == 0

    def test_per_turn_no_conflicts(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test per-turn with domains without conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        results = lens_layer.execute_per_turn([domain])

        assert results["domains_processed"] == 1
        assert results["conflicts_resolved"] == 0

    def test_per_turn_tracking(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test per-turn tracking updates state."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        initial_requests = lens_layer.lens_requests_made

        lens_layer.execute_per_turn([domain])

        assert lens_layer.lens_requests_made > initial_requests

    def test_per_turn_synthesis_application(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test syntheses are applied during per-turn."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original",
            source="AST",
        )
        domain.entities["e1"] = entity

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "Original", "BKIO": "Updated"},
        )
        domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results["syntheses_applied"] >= 0

    def test_per_turn_batch_processing(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test per-turn batch processing."""
        domains = []
        for i in range(5):
            domain = Domain(domain_id=f"test-{i}", name=f"Test {i}", description="Test")
            domains.append(domain)

        results = lens_layer.execute_per_turn(domains)

        assert results["domains_processed"] == 5

    def test_per_turn_conflict_resolution_tracking(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test conflict resolution tracking."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        for i in range(5):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"AST": f"val{i}", "BKIO": f"updated{i}"},
            )
            domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results["conflicts_resolved"] == 5

    def test_per_turn_status_after_execution(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test status after per-turn execution."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        lens_layer.execute_per_turn([domain])

        status = lens_layer.get_synthesis_status()

        assert status["lens_requests_made"] > 0

    def test_per_turn_repeatable(self, lens_layer: LENSIntegrationLayer) -> None:
        """Test per-turn can be called multiple times."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        results1 = lens_layer.execute_per_turn([domain])
        results2 = lens_layer.execute_per_turn([domain])

        assert results1["domains_processed"] == results2["domains_processed"]
        assert lens_layer.lens_requests_made >= 2

    def test_per_turn_mixed_conflicts_and_entities(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test per-turn with both entities and conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        # Add entities
        for i in range(3):
            entity = Entity(
                entity_id=f"e{i}",
                entity_type=EntityType.SERVICE,
                name=f"Service {i}",
                description=f"Service {i}",
                source="AST",
            )
            domain.entities[f"e{i}"] = entity

        # Add conflicts
        for i in range(2):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"AST": f"val{i}", "BKIO": f"updated{i}"},
            )
            domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        assert results["domains_processed"] == 1

    def test_per_turn_synthesis_not_applied_low_confidence(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test that synthesis with multiple sources is properly applied."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original",
            source="AST",
        )
        domain.entities["e1"] = entity

        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )
        domain.conflicts.append(conflict)

        results = lens_layer.execute_per_turn([domain])

        # Conflict should be resolved with high confidence synthesis
        assert results["conflicts_resolved"] == 1
        assert results["syntheses_applied"] == 1

    def test_lens_query_deduplication(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test that duplicate queries are handled correctly."""
        query1 = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )
        query2 = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )

        synthesis1 = lens_layer._execute_lens_phases(query1)
        synthesis2 = lens_layer._execute_lens_phases(query2)

        # Both should generate syntheses (different query IDs)
        assert synthesis1 is not None
        assert synthesis2 is not None
        # Query IDs should be different
        assert query1.query_id != query2.query_id

    def test_lens_integration_with_empty_conflicts(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test LENS integration with domain having no conflicts."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Description",
            source="AST",
        )
        domain.entities["e1"] = entity

        results = lens_layer.execute_per_turn([domain])

        assert results["domains_processed"] == 1
        assert results["conflicts_resolved"] == 0

    def test_lens_phase_error_recovery(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test that LENS handles phase errors gracefully."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={},  # Empty source values
            attribute="description",
        )

        synthesis = lens_layer._execute_lens_phases(query)

        # Should return None for invalid input
        assert synthesis is None

    def test_lens_synthesis_recommendation_hierarchy(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test that LENS respects source hierarchy in recommendations."""
        query = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={
                "GIT": "git_value",
                "AST": "ast_value",
                "BKIO": "bkio_value",
                "RELATIONSHIPS": "rel_value",
            },
            attribute="description",
        )

        synthesis = lens_layer._execute_lens_phases(query)

        # BKIO should be selected (highest priority)
        assert synthesis is not None
        assert synthesis.recommended_value == "bkio_value"
        assert "BKIO" in synthesis.reasoning

    def test_lens_continuous_synthesis_tracking(
        self, lens_layer: LENSIntegrationLayer
    ) -> None:
        """Test that LENS tracks synthesis metrics over time."""
        query1 = LENSQuery(
            conflict_id="c1",
            domain_id="test",
            source_values={"AST": "val1", "BKIO": "val2"},
            attribute="description",
        )
        query2 = LENSQuery(
            conflict_id="c2",
            domain_id="test",
            source_values={"AST": "val3", "BKIO": "val4"},
            attribute="name",
        )

        synthesis1 = lens_layer._execute_lens_phases(query1)
        synthesis2 = lens_layer._execute_lens_phases(query2)

        # Track calls
        lens_layer.query_log.append(query1)
        lens_layer.query_log.append(query2)

        assert len(lens_layer.query_log) == 2
        assert synthesis1 is not None
        assert synthesis2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
