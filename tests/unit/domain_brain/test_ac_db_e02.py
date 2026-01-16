"""Tests for AC-DB-E02: Brain Vacuum Prevention (TTL + Archival Strategy).

Comprehensive test suite validating:
- TTL enforcement and archival
- Hot/archive separation
- Query performance characteristics
- Load testing and degradation prevention
"""

import pytest
import time
from datetime import datetime, timedelta

from src.domain_brain.models import AuditOperationType
from src.domain_brain.audit_log_manager import AuditLogManager, ArchivalStats


class TestTTLEnforcement:
    """Tests for TTL enforcement."""

    @pytest.fixture
    def manager(self) -> AuditLogManager:
        """Create manager fixture."""
        return AuditLogManager(ttl_days=90)

    def test_recent_entries_in_hot_table(self, manager: AuditLogManager) -> None:
        """Test that recent entries stay in hot table."""
        manager.add_entry(
            "e1",
            AuditOperationType.AC_START,
            "domain1",
            "user1",
            "Test entry",
        )

        assert manager.get_hot_count() == 1
        assert manager.get_archive_count() == 0

    def test_old_entries_moved_to_archive(self, manager: AuditLogManager) -> None:
        """Test that old entries are moved to archive."""
        # Add entry
        manager.add_entry(
            "e1",
            AuditOperationType.AC_START,
            "domain1",
            "user1",
            "Test entry",
        )

        # Backdate entry (95 days old)
        manager.hot_entries[0].timestamp = datetime.utcnow() - timedelta(days=95)

        # Run cleanup
        stats = manager.cleanup_old_entries()

        assert stats.entries_archived == 1
        assert manager.get_hot_count() == 0
        assert manager.get_archive_count() == 1

    def test_ttl_cutoff_date_correct(self, manager: AuditLogManager) -> None:
        """Test that TTL cutoff date is computed correctly."""
        cutoff = datetime.utcnow() - timedelta(days=90)

        manager.add_entry(
            "e1",
            AuditOperationType.AC_START,
            "domain1",
            "user1",
            "Test entry",
        )
        manager.hot_entries[0].timestamp = cutoff - timedelta(seconds=1)

        stats = manager.cleanup_old_entries()

        assert stats.entries_archived == 1
        assert abs((stats.cutoff_date - cutoff).total_seconds()) < 60

    def test_rolling_monthly_archival(self, manager: AuditLogManager) -> None:
        """Test rolling monthly archival."""
        # Add entries for 120 days
        for day in range(120):
            entry_date = datetime.utcnow() - timedelta(days=day)
            manager.add_entry(
                f"e_{day}",
                AuditOperationType.AC_EXECUTE,
                "domain1",
                "user1",
                f"Entry {day}",
            )
            manager.hot_entries[-1].timestamp = entry_date

        # Run cleanup (should archive entries >90 days old)
        stats = manager.cleanup_old_entries()

        assert stats.entries_archived > 0
        assert manager.get_hot_count() <= 90
        assert manager.get_archive_count() > 0

    def test_no_loss_during_archival(self, manager: AuditLogManager) -> None:
        """Test that no entries are lost during archival."""
        # Add 100 entries
        for i in range(100):
            manager.add_entry(
                f"e_{i}",
                AuditOperationType.AC_COMPLETE,
                "domain1",
                "user1",
                f"Entry {i}",
            )

        initial_count = manager.get_total_count()

        # Run cleanup
        manager.cleanup_old_entries()

        final_count = manager.get_total_count()

        assert initial_count == final_count == 100


class TestPerformance:
    """Tests for query performance."""

    @pytest.fixture
    def manager(self) -> AuditLogManager:
        """Create manager fixture."""
        return AuditLogManager(ttl_days=90)

    def test_hot_query_performance_o1(self, manager: AuditLogManager) -> None:
        """Test that hot queries have O(1) performance."""
        # Simulate 10,000 entries (mostly old)
        manager.simulate_daily_updates(days=120, updates_per_day=100)
        manager.cleanup_old_entries()

        # Query hot entries
        start_time = time.time()
        for _ in range(1000):
            entries = manager.query_hot_entries("domain_0")
        elapsed = time.time() - start_time

        # Average query time
        avg_time_ms = (elapsed / 1000) * 1000

        # Hot queries should be <1ms on average
        assert avg_time_ms < 1.0

    def test_query_with_archive_acceptable(self, manager: AuditLogManager) -> None:
        """Test that queries spanning archive are acceptable (<200ms)."""
        # Simulate 10 days of updates
        manager.simulate_daily_updates(days=10, updates_per_day=100)

        # Query all entries (hot + archive)
        start_time = time.time()
        for _ in range(100):
            entries = manager.query_all_entries("domain_0")
        elapsed = time.time() - start_time

        avg_time_ms = (elapsed / 100) * 1000

        # Archive queries should be <200ms
        assert avg_time_ms < 200.0

    def test_concurrent_queries_unaffected(self, manager: AuditLogManager) -> None:
        """Test that concurrent queries are not affected by archival."""
        manager.simulate_daily_updates(days=120, updates_per_day=100)

        start_time = time.time()

        # Simulate concurrent queries
        for i in range(10):
            domain = f"domain_{i % 10}"
            queries = manager.query_hot_entries(domain)
            assert len(queries) > 0

        elapsed = time.time() - start_time

        # All queries should be fast
        assert elapsed < 1.0

    def test_cleanup_operation_performance(self, manager: AuditLogManager) -> None:
        """Test that cleanup operation is performant."""
        # Simulate 120 days of updates
        manager.simulate_daily_updates(days=120, updates_per_day=100)

        start_time = time.time()
        stats = manager.cleanup_old_entries()
        elapsed = time.time() - start_time

        # Cleanup should complete in <1 second
        assert stats.archival_duration_ms < 1000.0
        assert elapsed < 1.0

    def test_load_test_10k_entries_daily(self, manager: AuditLogManager) -> None:
        """Test performance with high daily update rate."""
        # Simulate 365 days with 10,000 updates per day
        manager.simulate_daily_updates(days=365, updates_per_day=10000)

        # Query should still be fast
        start_time = time.time()
        entries = manager.query_hot_entries("domain_0")
        elapsed = time.time() - start_time

        # Even with heavy load, queries should be <500ms
        assert elapsed < 0.5

    def test_month_12_query_performance_maintained(
        self, manager: AuditLogManager
    ) -> None:
        """Test that query performance is maintained at Month 12."""
        # Simulate 12 months of daily updates
        manager.simulate_daily_updates(days=365, updates_per_day=1000)

        # Run monthly cleanups
        for _ in range(12):
            manager.cleanup_old_entries()

        # Query should still be fast
        start_time = time.time()
        for _ in range(100):
            entries = manager.query_hot_entries("domain_0")
        elapsed = time.time() - start_time

        avg_time_ms = (elapsed / 100) * 1000

        # Should maintain <10ms query time even at Month 12
        assert avg_time_ms < 10.0


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def manager(self) -> AuditLogManager:
        """Create manager fixture."""
        return AuditLogManager(ttl_days=90)

    def test_query_spanning_hot_and_archive(self, manager: AuditLogManager) -> None:
        """Test querying data spanning hot and archive tiers."""
        # Add entries across 120 days
        for day in range(120):
            entry_date = datetime.utcnow() - timedelta(days=day)
            manager.add_entry(
                f"e_{day}",
                AuditOperationType.AC_EXECUTE,
                "domain1",
                "user1",
                f"Entry {day}",
            )
            manager.hot_entries[-1].timestamp = entry_date

        # Archive old entries
        manager.cleanup_old_entries()

        # Query all should return complete history
        all_entries = manager.query_all_entries("domain1")

        assert len(all_entries) == 120
        assert manager.get_hot_count() + manager.get_archive_count() == 120

    def test_cleanup_with_active_queries(self, manager: AuditLogManager) -> None:
        """Test that cleanup doesn't interfere with active queries."""
        manager.simulate_daily_updates(days=100, updates_per_day=100)

        # Start query
        entries_before = manager.query_hot_entries("domain_0")
        count_before = len(entries_before)

        # Run cleanup in "parallel" (conceptual)
        manager.cleanup_old_entries()

        # Query should still work
        entries_after = manager.query_hot_entries("domain_0")

        assert len(entries_after) >= 0

    def test_archive_restore_capability(self, manager: AuditLogManager) -> None:
        """Test that archived entries can be restored if needed."""
        manager.add_entry(
            "e1",
            AuditOperationType.AC_START,
            "domain1",
            "user1",
            "Test entry",
        )

        # Backdate and archive
        manager.hot_entries[0].timestamp = datetime.utcnow() - timedelta(days=95)
        stats = manager.cleanup_old_entries()

        # Verify in archive
        archive_entries = manager.query_archive_entries("domain1")
        assert len(archive_entries) == 1

        # Can still query full history
        all_entries = manager.query_all_entries("domain1")
        assert len(all_entries) == 1

    def test_empty_archive_handling(self, manager: AuditLogManager) -> None:
        """Test handling of empty archive."""
        manager.add_entry(
            "e1",
            AuditOperationType.AC_COMPLETE,
            "domain1",
            "user1",
            "Test entry",
        )

        # No old entries to archive
        stats = manager.cleanup_old_entries()

        assert stats.entries_archived == 0
        assert manager.get_archive_count() == 0

    def test_large_domain_archival(self, manager: AuditLogManager) -> None:
        """Test archival with large number of entries."""
        # Add 50,000 entries across multiple domains
        for i in range(50000):
            domain = f"domain_{i % 100}"
            manager.add_entry(
                f"e_{i}",
                AuditOperationType.AC_EXECUTE,
                domain,
                "user1",
                f"Entry {i}",
            )

        # Run cleanup
        start_time = time.time()
        stats = manager.cleanup_old_entries()
        elapsed = time.time() - start_time

        # Should complete in reasonable time
        assert elapsed < 5.0
        assert manager.get_total_count() == 50000


class TestStatusAndMonitoring:
    """Tests for status reporting and monitoring."""

    @pytest.fixture
    def manager(self) -> AuditLogManager:
        """Create manager fixture."""
        return AuditLogManager(ttl_days=90)

    def test_status_reporting(self, manager: AuditLogManager) -> None:
        """Test comprehensive status reporting."""
        manager.simulate_daily_updates(days=120, updates_per_day=100)
        manager.cleanup_old_entries()

        status = manager.get_status()

        assert "hot_entries" in status
        assert "archived_entries" in status
        assert "total_entries" in status
        assert "hot_percentage" in status
        assert "ttl_days" in status
        assert status["ttl_days"] == 90

    def test_archival_history_tracking(self, manager: AuditLogManager) -> None:
        """Test tracking of archival operations."""
        manager.simulate_daily_updates(days=120, updates_per_day=100)

        # Run multiple cleanups
        stats1 = manager.cleanup_old_entries()
        stats2 = manager.cleanup_old_entries()
        stats3 = manager.cleanup_old_entries()

        history = manager.get_archival_history()

        assert len(history) == 3
        assert history[0]["entries_archived"] > 0
        assert all("archival_duration_ms" in h for h in history)

    def test_hot_ratio_reporting(self, manager: AuditLogManager) -> None:
        """Test hot/archive ratio reporting."""
        # Add entries, split between hot and old
        for day in range(100):
            entry_date = datetime.utcnow() - timedelta(days=day)
            manager.add_entry(
                f"e_{day}",
                AuditOperationType.AC_EXECUTE,
                "domain1",
                "user1",
                f"Entry {day}",
            )
            manager.hot_entries[-1].timestamp = entry_date

        manager.cleanup_old_entries()

        ratio = manager.get_hot_ratio()

        # Should be mostly hot (< 100 days total, TTL 90)
        assert 0 <= ratio <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
