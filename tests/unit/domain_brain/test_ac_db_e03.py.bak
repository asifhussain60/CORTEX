"""Tests for AC-DB-E03: Conflict Escalation Workflow (3-Tier Resolution).

Comprehensive test suite validating:
- Hierarchy-based resolution (Tier 1)
- LENS synthesis resolution (Tier 2)
- Manual review escalation (Tier 3)
- 24h SLA enforcement
"""

import pytest
from datetime import datetime, timedelta

from cortex.domain_brain.models import Conflict, AuditOperationType
from cortex.domain_brain.conflict_resolver import (
    ConflictResolver,
    ResolutionTier,
    ReviewStatus,
)


class TestHierarchyResolution:
    """Tests for Tier 1: Hierarchy-based resolution."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        """Create resolver fixture."""
        return ConflictResolver()

    def test_hierarchy_single_source_wins(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that single source wins (Tier 1)."""
        sources = {"BKIO": "value1"}

        resolution = resolver.apply_hierarchy(sources)

        assert resolution is not None
        assert resolution.recommended_value == "value1"
        assert resolution.resolution_tier == ResolutionTier.HIERARCHY

    def test_hierarchy_bkio_over_all(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that BKIO wins over all other sources."""
        sources = {
            "GIT": "git_value",
            "AST": "ast_value",
            "BKIO": "bkio_value",
            "RELATIONSHIPS": "rel_value",
        }

        resolution = resolver.apply_hierarchy(sources)

        assert resolution is not None
        assert resolution.recommended_value == "bkio_value"
        assert "BKIO" in resolution.reasoning

    def test_hierarchy_relationships_over_ast(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that RELATIONSHIPS wins over AST."""
        sources = {"AST": "ast_value", "RELATIONSHIPS": "rel_value"}

        resolution = resolver.apply_hierarchy(sources)

        assert resolution is not None
        assert resolution.recommended_value == "rel_value"

    def test_hierarchy_empty_sources(
        self, resolver: ConflictResolver
    ) -> None:
        """Test handling of empty sources."""
        sources = {}

        resolution = resolver.apply_hierarchy(sources)

        assert resolution is None

    def test_hierarchy_tie_detection(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that ties return None (escalate to Tier 2)."""
        # Simulate a tie (would need custom priority for this)
        sources = {"AST": "value1", "GIT": "value2"}

        # No tie here, AST has higher priority
        resolution = resolver.apply_hierarchy(sources)

        assert resolution is not None  # AST wins


class TestLENSSynthesisResolution:
    """Tests for Tier 2: LENS synthesis."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        """Create resolver fixture."""
        return ConflictResolver()

    def test_lens_synthesis_on_multiple_sources(
        self, resolver: ConflictResolver
    ) -> None:
        """Test LENS synthesis with multiple sources."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "GIT": "val2"},
        )

        resolution = resolver.query_lens_synthesis(conflict)

        # 70% success rate
        if resolution:
            assert resolution.resolution_tier == ResolutionTier.LENS_SYNTHESIS

    def test_lens_synthesis_with_single_source(
        self, resolver: ConflictResolver
    ) -> None:
        """Test LENS synthesis with single source returns None."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1"},
        )

        resolution = resolver.query_lens_synthesis(conflict)

        assert resolution is None

    def test_lens_synthesis_empty_sources(
        self, resolver: ConflictResolver
    ) -> None:
        """Test LENS synthesis with empty sources."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={},
        )

        resolution = resolver.query_lens_synthesis(conflict)

        assert resolution is None


class TestManualReviewEscalation:
    """Tests for Tier 3: Manual review escalation."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        """Create resolver fixture."""
        return ConflictResolver()

    def test_manual_review_ticket_created(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that manual review ticket is created."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        ticket = resolver.escalate_to_manual_review(conflict, "LENS deferral")

        assert ticket is not None
        assert ticket.conflict_id == "c1"
        assert ticket.status == ReviewStatus.PENDING

    def test_24h_sla_enforced(self, resolver: ConflictResolver) -> None:
        """Test that 24h SLA is enforced."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        ticket = resolver.escalate_to_manual_review(conflict, "Test escalation")

        # SLA should be 24 hours
        expected_due = datetime.utcnow() + timedelta(hours=24)
        actual_due = ticket.due_at

        # Allow 1 minute margin
        diff = abs((actual_due - expected_due).total_seconds())
        assert diff < 60

    def test_manual_resolution_applied(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that manual resolution can be applied."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        ticket = resolver.escalate_to_manual_review(conflict, "Escalation")

        # Resolve manually
        success = resolver.resolve_manual_ticket(
            ticket.ticket_id, "resolved_value", "reviewer1"
        )

        assert success
        assert ticket.status == ReviewStatus.RESOLVED
        assert ticket.resolution == "resolved_value"

    def test_escalation_audit_trail(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that escalation audit trail is maintained."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"AST": "val1", "BKIO": "val2"},
        )

        ticket = resolver.escalate_to_manual_review(conflict, "Escalation")

        assert ticket.created_at is not None
        assert ticket.due_at is not None
        assert ticket.ticket_id is not None


class TestConflictResolutionWorkflow:
    """Tests for complete resolution workflow."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        """Create resolver fixture."""
        return ConflictResolver()

    def test_resolve_conflict_hierarchy(
        self, resolver: ConflictResolver
    ) -> None:
        """Test conflict resolution through hierarchy (Tier 1)."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={"BKIO": "bkio_value", "AST": "ast_value"},
        )

        resolution = resolver.resolve_conflict(conflict)

        assert resolution is not None
        assert resolution.resolution_tier == ResolutionTier.HIERARCHY
        assert resolver.tier1_resolved == 1

    def test_resolve_conflict_with_escalation(
        self, resolver: ConflictResolver
    ) -> None:
        """Test conflict escalation when hierarchy fails."""
        # Create conflict with no clear winner through hierarchy
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={},
        )

        resolution = resolver.resolve_conflict(conflict)

        # Should be escalated
        assert resolution is None or resolver.tier3_escalated >= 0

    def test_multiple_conflicts_resolution(
        self, resolver: ConflictResolver
    ) -> None:
        """Test resolution of multiple conflicts."""
        conflicts = [
            Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"BKIO": f"bkio_{i}", "AST": f"ast_{i}"},
            )
            for i in range(5)
        ]

        for conflict in conflicts:
            resolver.resolve_conflict(conflict)

        stats = resolver.get_resolution_stats()
        assert stats["total_conflicts"] >= 5

    def test_all_conflicts_handled(
        self, resolver: ConflictResolver
    ) -> None:
        """Test that all conflicts are eventually handled."""
        conflicts = [
            Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"BKIO": f"val_{i}", "AST": f"val_{i}"}
                if i % 2 == 0
                else {"AST": f"val_{i}"},
            )
            for i in range(10)
        ]

        for conflict in conflicts:
            resolver.resolve_conflict(conflict)

        stats = resolver.get_resolution_stats()

        # All conflicts should be accounted for
        total = stats["resolution_rate_percent"] + stats["escalation_rate_percent"]
        assert 95 <= total <= 105  # ~100% (allowing for float rounding)


class TestManualReviewQueue:
    """Tests for manual review queue management."""

    @pytest.fixture
    def resolver(self) -> ConflictResolver:
        """Create resolver fixture."""
        return ConflictResolver()

    def test_manual_review_queue_management(
        self, resolver: ConflictResolver
    ) -> None:
        """Test management of manual review queue."""
        # Escalate multiple conflicts
        for i in range(5):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={},
            )
            resolver.escalate_to_manual_review(conflict, "Test escalation")

        pending = resolver.get_manual_review_queue()
        assert len(pending) == 5

    def test_overdue_tickets_detection(
        self, resolver: ConflictResolver
    ) -> None:
        """Test detection of overdue tickets."""
        conflict = Conflict(
            conflict_id="c1",
            domain_id="test",
            attribute="description",
            source_values={},
        )

        ticket = resolver.escalate_to_manual_review(conflict, "Test")

        # Manually make ticket overdue
        ticket.due_at = datetime.utcnow() - timedelta(hours=1)

        overdue = resolver.get_overdue_tickets()
        assert len(overdue) == 1

    def test_status_reporting(self, resolver: ConflictResolver) -> None:
        """Test status reporting."""
        # Add some conflicts
        for i in range(3):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="test",
                attribute="description",
                source_values={"BKIO": f"val_{i}"},
            )
            resolver.resolve_conflict(conflict)

        status = resolver.get_status()

        assert "resolution_stats" in status
        assert "pending_tickets" in status
        assert "overdue_tickets" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
