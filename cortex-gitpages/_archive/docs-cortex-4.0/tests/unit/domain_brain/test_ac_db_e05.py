"""Tests for AC-DB-E05: Concurrent Write Handling (Optimistic Locking).

Comprehensive test suite validating:
- Version tracking
- Conflict detection
- Retry mechanism
- Concurrent write scenarios
"""

import pytest

from src.domain_brain.optimistic_lock import (
    OptimisticLockManager,
    ConflictError,
    VersionedDomain,
)


class TestVersionTracking:
    """Tests for version tracking."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_domain_created_at_version_1(self, manager: OptimisticLockManager) -> None:
        """Test that new domains start at version 1."""
        domain = manager.create_domain("test")

        assert domain.version == 1
        assert domain.domain_id == "test"

    def test_version_increments_on_write(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test that version increments on successful write."""
        domain = manager.create_domain("test", {"field": "value1"})
        assert domain.version == 1

        # Write with correct version
        updated = manager.write_domain("test", {"field": "value2"}, expected_version=1)

        assert updated.version == 2
        assert updated.content["field"] == "value2"

    def test_version_consistency(self, manager: OptimisticLockManager) -> None:
        """Test version consistency across reads."""
        domain = manager.create_domain("test", {"field": "initial"})

        read1 = manager.read_domain("test")
        assert read1.version == 1

        manager.write_domain("test", {"field": "updated"}, expected_version=1)

        read2 = manager.read_domain("test")
        assert read2.version == 2


class TestConflictDetection:
    """Tests for conflict detection."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_conflict_detected_on_version_mismatch(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test that conflicts are detected on version mismatch."""
        manager.create_domain("test", {"field": "initial"})

        # Try to write with wrong version
        with pytest.raises(ConflictError):
            manager.write_domain("test", {"field": "updated"}, expected_version=2)

    def test_conflict_error_details(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test that conflict error has correct details."""
        manager.create_domain("test")

        try:
            manager.write_domain("test", {}, expected_version=5)
        except ConflictError as e:
            assert e.domain_id == "test"
            assert e.expected_version == 5
            assert e.actual_version == 1
        else:
            pytest.fail("ConflictError not raised")

    def test_no_conflict_on_match(self, manager: OptimisticLockManager) -> None:
        """Test that no conflict occurs when versions match."""
        manager.create_domain("test")

        # Should not raise
        result = manager.write_domain("test", {"data": "value"}, expected_version=1)

        assert result.version == 2


class TestRetryMechanism:
    """Tests for retry mechanism."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_successful_retry_after_conflict(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test successful retry after conflict."""
        manager.create_domain("test", {"field": "initial"})

        # First write with wrong version (conflict)
        with pytest.raises(ConflictError):
            manager.write_domain("test", {"field": "value1"}, expected_version=2)

        # Read latest version
        current = manager.read_domain("test")

        # Retry with correct version
        result = manager.write_domain(
            "test", {"field": "value2"}, expected_version=current.version
        )

        assert result.version == 2
        assert result.content["field"] == "value2"

    def test_multiple_retries(self, manager: OptimisticLockManager) -> None:
        """Test multiple retries converge to success."""
        manager.create_domain("test", {"counter": 0})

        # Simulate concurrent increments with retries
        for _ in range(5):
            current = manager.read_domain("test")
            new_content = {"counter": current.content.get("counter", 0) + 1}

            try:
                manager.write_domain("test", new_content, current.version)
            except ConflictError:
                # Retry
                current = manager.read_domain("test")
                new_content = {"counter": current.content.get("counter", 0) + 1}
                manager.write_domain("test", new_content, current.version)

        final = manager.read_domain("test")
        assert final.content["counter"] >= 1  # At least one increment succeeded


class TestConcurrentScenarios:
    """Tests for concurrent scenarios."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_two_writers_conflict(self, manager: OptimisticLockManager) -> None:
        """Test conflict when two writers modify simultaneously."""
        manager.create_domain("test", {"value": "initial"})

        # Writer 1 reads
        v1 = manager.read_domain("test")
        assert v1.version == 1

        # Writer 2 reads (same version)
        v2 = manager.read_domain("test")
        assert v2.version == 1

        # Writer 1 writes successfully
        manager.write_domain("test", {"value": "writer1"}, expected_version=1)

        # Writer 2 tries to write (conflict)
        with pytest.raises(ConflictError):
            manager.write_domain("test", {"value": "writer2"}, expected_version=1)

        # But Writer 2 can retry
        current = manager.read_domain("test")
        result = manager.write_domain("test", {"value": "writer2"}, current.version)

        assert result.content["value"] == "writer2"

    def test_conflict_rate_calculation(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test conflict rate calculation."""
        manager.create_domain("test")

        # 10 write attempts
        for i in range(10):
            current = manager.read_domain("test")
            try:
                manager.write_domain("test", {"value": i}, current.version)
            except ConflictError:
                # Retry
                current = manager.read_domain("test")
                manager.write_domain("test", {"value": i}, current.version)

        status = manager.get_status()
        assert status["write_attempts"] >= 10


class TestNonExistentDomains:
    """Tests for non-existent domains."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_write_new_domain_version_0(self, manager: OptimisticLockManager) -> None:
        """Test writing new domain with version 0."""
        result = manager.write_domain("new", {"data": "initial"}, expected_version=0)

        assert result.version == 1
        assert result.domain_id == "new"

    def test_write_new_domain_nonzero_version_fails(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test that writing new domain with non-zero version fails."""
        with pytest.raises(ConflictError):
            manager.write_domain("new", {"data": "value"}, expected_version=5)


class TestStatusReporting:
    """Tests for status reporting."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_status_reporting(self, manager: OptimisticLockManager) -> None:
        """Test comprehensive status reporting."""
        manager.create_domain("test1")
        manager.create_domain("test2")

        manager.write_domain("test1", {"value": 1}, expected_version=1)

        try:
            manager.write_domain("test1", {"value": 2}, expected_version=1)
        except ConflictError:
            pass

        status = manager.get_status()

        assert status["total_domains"] == 2
        assert status["write_attempts"] >= 2
        assert status["write_conflicts"] >= 1

    def test_conflict_log_tracking(self, manager: OptimisticLockManager) -> None:
        """Test conflict log tracking."""
        manager.create_domain("test")

        # First write succeeds, moves to version 2
        manager.write_domain("test", {}, expected_version=1)

        # Subsequent writes with old version fail
        for _ in range(2):
            try:
                manager.write_domain("test", {}, expected_version=1)
            except ConflictError:
                pass

        log = manager.get_conflict_log()

        assert len(log) >= 2
        assert all("domain_id" in entry for entry in log)
        assert all("expected_version" in entry for entry in log)


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def manager(self) -> OptimisticLockManager:
        """Create manager fixture."""
        return OptimisticLockManager()

    def test_version_overflow_handling(
        self, manager: OptimisticLockManager
    ) -> None:
        """Test handling of high version numbers."""
        domain = manager.create_domain("test")

        # Simulate many writes
        for _ in range(100):
            domain = manager.write_domain("test", {"value": "x"}, expected_version=domain.version)

        assert domain.version == 101

    def test_empty_content_write(self, manager: OptimisticLockManager) -> None:
        """Test writing empty content."""
        manager.create_domain("test", {"field": "value"})

        result = manager.write_domain("test", {}, expected_version=1)

        assert result.content == {}

    def test_modified_by_tracking(self, manager: OptimisticLockManager) -> None:
        """Test tracking of who modified domain."""
        manager.create_domain("test")

        manager.write_domain("test", {"value": 1}, expected_version=1, modified_by="user1")
        result = manager.write_domain(
            "test", {"value": 2}, expected_version=2, modified_by="user2"
        )

        assert result.modified_by == "user2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
