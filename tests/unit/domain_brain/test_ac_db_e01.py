"""Tests for AC-DB-E01: Duplicate Upload Detection (Hash-Based Deduplication).

Comprehensive test suite validating:
- Hash computation consistency
- Duplicate detection accuracy
- Audit trail preservation
- Performance characteristics
"""

import pytest
from datetime import datetime, timedelta
import time

from src.domain_brain.models import (
    Domain,
    Entity,
    EntityType,
    Conflict,
)
from src.domain_brain.deduplication import DuplicateDetector, DuplicateEntry


class TestHashComputation:
    """Tests for hash computation."""

    @pytest.fixture
    def detector(self) -> DuplicateDetector:
        """Create detector fixture."""
        return DuplicateDetector()

    def test_hash_consistent_same_domain(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that identical domains produce identical hashes."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        entity = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Description",
            source="AST",
        )
        domain.entities["e1"] = entity

        hash1 = detector.compute_domain_hash(domain)
        hash2 = detector.compute_domain_hash(domain)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest length

    def test_hash_differs_modified_domain(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that modified domain produces different hash."""
        domain1 = Domain(domain_id="test", name="Test", description="Test")
        entity1 = Entity(
            entity_id="e1",
            entity_type=EntityType.SERVICE,
            name="Service",
            description="Original",
            source="AST",
        )
        domain1.entities["e1"] = entity1

        hash1 = detector.compute_domain_hash(domain1)

        # Modify domain
        entity1.description = "Modified"
        hash2 = detector.compute_domain_hash(domain1)

        assert hash1 != hash2

    def test_hash_collision_unlikely(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that different domains produce different hashes."""
        domain1 = Domain(domain_id="test1", name="Test1", description="Test1")
        domain2 = Domain(domain_id="test2", name="Test2", description="Test2")

        hash1 = detector.compute_domain_hash(domain1)
        hash2 = detector.compute_domain_hash(domain2)

        assert hash1 != hash2

    def test_hash_computation_performance(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that hash computation is fast (<1ms per domain)."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        
        # Add 50 entities
        for i in range(50):
            entity = Entity(
                entity_id=f"e{i}",
                entity_type=EntityType.SERVICE,
                name=f"Service {i}",
                description=f"Description {i}",
                source="AST",
            )
            domain.entities[f"e{i}"] = entity

        start_time = time.time()
        for _ in range(100):
            detector.compute_domain_hash(domain)
        elapsed = time.time() - start_time

        # Average time per hash
        avg_time = (elapsed / 100) * 1000  # Convert to ms

        # Should be <1ms per domain
        assert avg_time < 1.0


class TestDuplicateDetection:
    """Tests for duplicate detection."""

    @pytest.fixture
    def detector(self) -> DuplicateDetector:
        """Create detector fixture."""
        return DuplicateDetector()

    def test_first_upload_not_duplicate(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that first upload is not detected as duplicate."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        is_duplicate = detector.process_domain_upload(domain)

        assert is_duplicate is False
        assert detector.unique_uploads_processed == 1

    def test_identical_reupload_detected(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that identical re-upload is detected as duplicate."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        # First upload
        is_duplicate1 = detector.process_domain_upload(domain)
        assert is_duplicate1 is False

        # Identical re-upload
        domain_copy = Domain(domain_id="test", name="Test", description="Test")
        is_duplicate2 = detector.process_domain_upload(domain_copy)

        assert is_duplicate2 is True
        assert detector.duplicate_uploads_prevented == 1

    def test_modified_reupload_not_duplicate(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that modified re-upload is not detected as duplicate."""
        domain = Domain(domain_id="test", name="Test", description="Original")

        # First upload
        is_duplicate1 = detector.process_domain_upload(domain)
        assert is_duplicate1 is False

        # Modified re-upload
        domain.description = "Modified"
        is_duplicate2 = detector.process_domain_upload(domain)

        assert is_duplicate2 is False
        assert detector.unique_uploads_processed == 2
        assert detector.duplicate_uploads_prevented == 0

    def test_duplicate_audit_trail_preserved(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that audit trail is preserved for duplicates."""
        domain = Domain(domain_id="test", name="Test", description="Test")

        # First upload
        detector.process_domain_upload(domain, original_upload_time=datetime.utcnow())

        # Duplicate re-upload
        domain_copy = Domain(domain_id="test", name="Test", description="Test")
        detector.process_domain_upload(domain_copy)

        # Check duplicate log
        status = detector.get_deduplication_status()
        assert status["duplicate_uploads_prevented"] == 1
        assert status["unique_uploads_processed"] == 1

    def test_duplicate_metrics_recorded(
        self, detector: DuplicateDetector
    ) -> None:
        """Test that duplicate metrics are accurately recorded."""
        domain1 = Domain(domain_id="test1", name="Test1", description="Test1")
        domain2 = Domain(domain_id="test2", name="Test2", description="Test2")

        # Upload unique domains
        detector.process_domain_upload(domain1)
        detector.process_domain_upload(domain2)

        # Upload duplicates
        domain1_dup = Domain(domain_id="test1", name="Test1", description="Test1")
        domain2_dup = Domain(domain_id="test2", name="Test2", description="Test2")
        domain2_dup2 = Domain(domain_id="test2", name="Test2", description="Test2")

        detector.process_domain_upload(domain1_dup)
        detector.process_domain_upload(domain2_dup)
        detector.process_domain_upload(domain2_dup2)

        status = detector.get_deduplication_status()
        assert status["unique_uploads_processed"] == 2
        assert status["duplicate_uploads_prevented"] == 3
        assert status["total_uploads_attempted"] == 5
        assert status["duplicate_rate_percent"] == 60.0


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def detector(self) -> DuplicateDetector:
        """Create detector fixture."""
        return DuplicateDetector()

    def test_empty_domain_hash(self, detector: DuplicateDetector) -> None:
        """Test hash computation for empty domain."""
        domain = Domain(domain_id="empty", name="Empty", description="")

        hash_value = detector.compute_domain_hash(domain)

        assert hash_value is not None
        assert len(hash_value) == 64

    def test_large_domain_performance(self, detector: DuplicateDetector) -> None:
        """Test hash computation performance for large domain."""
        domain = Domain(domain_id="large", name="Large", description="Large")

        # Add 100 entities
        for i in range(100):
            entity = Entity(
                entity_id=f"e{i}",
                entity_type=EntityType.SERVICE,
                name=f"Service {i}",
                description=f"Description {i}",
                source="AST",
            )
            domain.entities[f"e{i}"] = entity

        # Add 50 conflicts
        for i in range(50):
            conflict = Conflict(
                conflict_id=f"c{i}",
                domain_id="large",
                attribute="description",
                source_values={"AST": f"val{i}", "BKIO": f"updated{i}"},
            )
            domain.conflicts.append(conflict)

        start_time = time.time()
        hash_value = detector.compute_domain_hash(domain)
        elapsed = time.time() - start_time

        assert hash_value is not None
        assert elapsed < 0.1  # Should be fast even with large domain

    def test_concurrent_duplicate_detection(
        self, detector: DuplicateDetector
    ) -> None:
        """Test duplicate detection with concurrent uploads."""
        domains = []
        for i in range(10):
            domain = Domain(
                domain_id=f"test{i}",
                name=f"Test{i}",
                description=f"Test{i}",
            )
            domains.append(domain)

        # Upload all once
        for domain in domains:
            detector.process_domain_upload(domain)

        # Upload all again (should all be duplicates)
        for domain in domains:
            domain_copy = Domain(
                domain_id=domain.domain_id,
                name=domain.name,
                description=domain.description,
            )
            is_duplicate = detector.process_domain_upload(domain_copy)
            assert is_duplicate is True

        status = detector.get_deduplication_status()
        assert status["unique_uploads_processed"] == 10
        assert status["duplicate_uploads_prevented"] == 10

    def test_duplicate_entry_structure(
        self, detector: DuplicateDetector
    ) -> None:
        """Test DuplicateEntry data structure."""
        domain = Domain(domain_id="test", name="Test", description="Test")
        hash_val = detector.compute_domain_hash(domain)
        original_time = datetime.utcnow()

        detector.log_duplicate("test", hash_val, original_time)

        log = detector.get_duplicate_log()
        assert hash_val in log
        assert log[hash_val]["domain_id"] == "test"
        assert log[hash_val]["times_detected"] == 1

    def test_duplicate_log_clear(self, detector: DuplicateDetector) -> None:
        """Test clearing duplicate log."""
        domain1 = Domain(domain_id="test1", name="Test1", description="Test1")
        domain2 = Domain(domain_id="test2", name="Test2", description="Test2")

        # Upload and generate duplicates
        detector.process_domain_upload(domain1)
        detector.process_domain_upload(domain2)

        domain1_dup = Domain(domain_id="test1", name="Test1", description="Test1")
        domain2_dup = Domain(domain_id="test2", name="Test2", description="Test2")

        detector.process_domain_upload(domain1_dup)
        detector.process_domain_upload(domain2_dup)

        # Clear duplicates
        cleared_count = detector.clear_duplicates()

        assert cleared_count == 2
        assert len(detector.get_duplicate_log()) == 0


class TestDeduplicationIntegration:
    """Integration tests for deduplication workflow."""

    @pytest.fixture
    def detector(self) -> DuplicateDetector:
        """Create detector fixture."""
        return DuplicateDetector()

    def test_domain_with_entities_deduplicated(
        self, detector: DuplicateDetector
    ) -> None:
        """Test deduplication of domain with entities."""
        domain = Domain(domain_id="service-registry", name="Services", description="All services")
        
        entity1 = Entity(
            entity_id="api-gateway",
            entity_type=EntityType.SERVICE,
            name="API Gateway",
            description="Main API entry point",
            source="AST",
        )
        entity2 = Entity(
            entity_id="auth-service",
            entity_type=EntityType.SERVICE,
            name="Auth Service",
            description="Authentication service",
            source="AST",
        )
        domain.entities["api-gateway"] = entity1
        domain.entities["auth-service"] = entity2

        # First upload
        is_dup1 = detector.process_domain_upload(domain)
        assert is_dup1 is False

        # Create identical domain
        domain2 = Domain(domain_id="service-registry", name="Services", description="All services")
        entity1_copy = Entity(
            entity_id="api-gateway",
            entity_type=EntityType.SERVICE,
            name="API Gateway",
            description="Main API entry point",
            source="AST",
        )
        entity2_copy = Entity(
            entity_id="auth-service",
            entity_type=EntityType.SERVICE,
            name="Auth Service",
            description="Authentication service",
            source="AST",
        )
        domain2.entities["api-gateway"] = entity1_copy
        domain2.entities["auth-service"] = entity2_copy

        # Second upload (should be duplicate)
        is_dup2 = detector.process_domain_upload(domain2)
        assert is_dup2 is True

    def test_status_reporting(self, detector: DuplicateDetector) -> None:
        """Test comprehensive status reporting."""
        # Create and upload multiple domains
        for i in range(5):
            domain = Domain(domain_id=f"test{i}", name=f"Test{i}", description=f"Test{i}")
            detector.process_domain_upload(domain)

        # Upload duplicates
        for i in range(5):
            domain = Domain(domain_id=f"test{i}", name=f"Test{i}", description=f"Test{i}")
            detector.process_domain_upload(domain)

        status = detector.get_deduplication_status()

        assert status["unique_uploads_processed"] == 5
        assert status["duplicate_uploads_prevented"] == 5
        assert status["total_uploads_attempted"] == 10
        assert status["duplicate_rate_percent"] == 50.0
        assert status["unique_hashes_stored"] == 5
        assert status["duplicate_events_logged"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
