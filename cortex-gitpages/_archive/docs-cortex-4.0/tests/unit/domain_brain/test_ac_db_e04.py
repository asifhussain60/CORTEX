"""Tests for AC-DB-E04: Orphan Reference Detection (Stale Link Handling).

Comprehensive test suite validating:
- Reference validation
- Orphan detection
- Deprecation marking
- Weekly sweep functionality
"""

import pytest
import time

from src.domain_brain.orphan_detector import (
    ReferenceValidator,
    OrphanEntry,
    OrphanStats,
)


class TestReferenceValidation:
    """Tests for reference validation."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_valid_reference_passes(self, validator: ReferenceValidator) -> None:
        """Test that valid references pass validation."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.add_reference("entity1", "entity2")

        is_valid = validator.validate_reference("entity1", "entity2")

        assert is_valid is True

    def test_missing_reference_fails(self, validator: ReferenceValidator) -> None:
        """Test that missing references fail validation."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "missing_entity")

        is_valid = validator.validate_reference("entity1", "missing_entity")

        assert is_valid is False

    def test_circular_reference_detected(self, validator: ReferenceValidator) -> None:
        """Test detection of circular references."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.add_reference("entity1", "entity2")
        validator.add_reference("entity2", "entity1")

        # Both should be valid (circular refs are allowed)
        assert validator.validate_reference("entity1", "entity2") is True
        assert validator.validate_reference("entity2", "entity1") is True

    def test_transitive_reference_validation(
        self, validator: ReferenceValidator
    ) -> None:
        """Test validation with transitive references."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.register_entity("entity3")

        validator.add_reference("entity1", "entity2")
        validator.add_reference("entity2", "entity3")

        # All should be valid
        assert validator.validate_reference("entity1", "entity2") is True
        assert validator.validate_reference("entity2", "entity3") is True


class TestDeprecation:
    """Tests for deprecation marking."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_mark_deprecated(self, validator: ReferenceValidator) -> None:
        """Test marking reference as deprecated."""
        validator.mark_deprecated("entity1", "missing_entity", "Not found")

        deprecated = validator.get_deprecated_references()

        assert len(deprecated) == 1
        assert deprecated[0]["entity_id"] == "entity1"
        assert deprecated[0]["referenced_entity_id"] == "missing_entity"

    def test_deprecated_queries_show_status(
        self, validator: ReferenceValidator
    ) -> None:
        """Test that deprecated status is queryable."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "missing")
        validator.mark_deprecated("entity1", "missing")

        deprecated = validator.get_deprecated_references()

        assert len(deprecated) == 1
        assert deprecated[0]["is_restorable"] is True

    def test_permanent_deletion_option(self, validator: ReferenceValidator) -> None:
        """Test permanent deletion marking."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.add_reference("entity1", "entity2")

        # Delete entity2
        orphaned_count = validator.delete_entity("entity2")

        assert orphaned_count == 1
        assert "entity2" not in validator.entity_ids
        assert validator.validate_reference("entity1", "entity2") is False


class TestOrphanSweep:
    """Tests for orphan sweep."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_weekly_orphan_sweep(self, validator: ReferenceValidator) -> None:
        """Test weekly orphan sweep operation."""
        # Set up entities and references
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.add_reference("entity1", "entity2")
        validator.add_reference("entity1", "missing1")

        stats = validator.sweep_orphans()

        assert stats.total_references_checked == 2
        assert stats.orphaned_references_found == 1
        assert stats.deprecations_marked == 1

    def test_orphan_stats_accurate(self, validator: ReferenceValidator) -> None:
        """Test accuracy of orphan statistics."""
        # Create multiple orphaned references
        validator.register_entity("entity1")
        validator.register_entity("entity2")

        for i in range(5):
            validator.add_reference("entity1", f"missing{i}")

        validator.add_reference("entity1", "entity2")

        stats = validator.sweep_orphans()

        assert stats.total_references_checked == 6
        assert stats.orphaned_references_found == 5
        assert stats.deprecations_marked == 5

    def test_orphan_recovery_audit_trail(
        self, validator: ReferenceValidator
    ) -> None:
        """Test audit trail for orphan recovery."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "missing")

        stats1 = validator.sweep_orphans()

        # Should have one orphan
        assert stats1.deprecations_marked == 1

        # Re-register missing entity
        validator.register_entity("missing")

        stats2 = validator.sweep_orphans()

        # Sweep should find no new orphans (reference is now valid)
        assert stats2.orphaned_references_found == 0


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_empty_references(self, validator: ReferenceValidator) -> None:
        """Test sweep with no references."""
        validator.register_entity("entity1")

        stats = validator.sweep_orphans()

        assert stats.total_references_checked == 0
        assert stats.orphaned_references_found == 0

    def test_self_reference_valid(self, validator: ReferenceValidator) -> None:
        """Test that self-references are valid."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "entity1")

        is_valid = validator.validate_reference("entity1", "entity1")

        assert is_valid is True

    def test_multiple_references_same_target(
        self, validator: ReferenceValidator
    ) -> None:
        """Test multiple entities referencing same target."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.register_entity("target")

        validator.add_reference("entity1", "target")
        validator.add_reference("entity2", "target")

        # Delete target
        orphaned = validator.delete_entity("target")

        assert orphaned == 2

    def test_large_reference_graph(self, validator: ReferenceValidator) -> None:
        """Test performance with large reference graph."""
        # Create 100 entities with 500 references
        for i in range(100):
            validator.register_entity(f"entity{i}")

        # Add references
        for i in range(100):
            for j in range(5):
                target = f"entity{(i + j) % 100}"
                validator.add_reference(f"entity{i}", target)

        # Add some orphaned references
        for i in range(50):
            validator.add_reference("entity0", f"missing{i}")

        start_time = time.time()
        stats = validator.sweep_orphans()
        elapsed = time.time() - start_time

        assert stats.total_references_checked == 550
        assert stats.orphaned_references_found == 50
        assert elapsed < 1.0  # Should be fast


class TestStatusReporting:
    """Tests for status reporting."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_orphan_status_reporting(self, validator: ReferenceValidator) -> None:
        """Test comprehensive orphan status reporting."""
        validator.register_entity("entity1")
        validator.register_entity("entity2")
        validator.add_reference("entity1", "entity2")
        validator.add_reference("entity1", "missing")

        validator.sweep_orphans()

        status = validator.get_orphan_status()

        assert status["total_entities"] == 2
        assert status["total_references"] == 2
        assert status["deprecated_references"] == 1
        assert status["sweep_operations"] == 1

    def test_sweep_history_tracking(self, validator: ReferenceValidator) -> None:
        """Test tracking of sweep history."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "missing1")

        validator.sweep_orphans()
        validator.sweep_orphans()
        validator.sweep_orphans()

        history = validator.get_sweep_history()

        assert len(history) == 3
        assert all("sweep_duration_ms" in h for h in history)


class TestIntegration:
    """Integration tests."""

    @pytest.fixture
    def validator(self) -> ReferenceValidator:
        """Create validator fixture."""
        return ReferenceValidator()

    def test_reference_lifecycle(self, validator: ReferenceValidator) -> None:
        """Test complete reference lifecycle."""
        # Create entities
        validator.register_entity("api-gateway")
        validator.register_entity("auth-service")
        validator.register_entity("user-db")

        # Add references
        validator.add_reference("api-gateway", "auth-service")
        validator.add_reference("api-gateway", "user-db")
        validator.add_reference("auth-service", "user-db")

        # All should be valid
        assert validator.validate_reference("api-gateway", "auth-service") is True
        assert validator.validate_reference("api-gateway", "user-db") is True

        # Delete user-db
        orphaned = validator.delete_entity("user-db")

        assert orphaned == 2

        # Sweep should detect orphans
        stats = validator.sweep_orphans()

        assert stats.orphaned_references_found == 2

    def test_orphan_recovery_workflow(self, validator: ReferenceValidator) -> None:
        """Test orphan recovery workflow."""
        validator.register_entity("entity1")
        validator.add_reference("entity1", "entity2")

        # Entity2 is missing (orphaned)
        stats1 = validator.sweep_orphans()
        assert stats1.orphaned_references_found == 1

        # Re-register entity2 (recovery)
        validator.register_entity("entity2")

        # New sweep should find no orphans
        stats2 = validator.sweep_orphans()
        assert stats2.orphaned_references_found == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
