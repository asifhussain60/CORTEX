"""Unit tests for orphaned resource detection and cleanup."""

import pytest
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time

from cortex.core.recovery.orphan_cleaner import (
    OrphanedResourceCleaner,
    ResourceType,
    OrphanedResource,
    CleanupStrategy,
    CleanupResult,
    CleanupError,
)


class TestOrphanedResource:
    """Test orphaned resource detection."""
    
    def test_resource_creation(self) -> None:
        """Test creating orphaned resource record."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={"owner": "process-456"}
        )
        
        assert resource.resource_id == "lock-123"
        assert resource.resource_type == ResourceType.LOCK
        assert resource.metadata["owner"] == "process-456"
    
    def test_is_orphaned_by_time(self) -> None:
        """Test orphan detection based on inactivity."""
        resource = OrphanedResource(
            resource_id="lock-1",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=20),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={}
        )
        
        # Lock held >10 minutes is orphaned
        assert resource.is_orphaned(lock_threshold_minutes=10)
    
    def test_not_orphaned_if_active(self) -> None:
        """Test active resources not marked orphaned."""
        resource = OrphanedResource(
            resource_id="lock-1",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=20),
            last_activity=datetime.utcnow() - timedelta(minutes=2),
            metadata={}
        )
        
        # Lock active within 10 minutes
        assert not resource.is_orphaned(lock_threshold_minutes=10)
    
    def test_operation_stuck_threshold(self) -> None:
        """Test stuck operation detection."""
        resource = OrphanedResource(
            resource_id="op-123",
            resource_type=ResourceType.OPERATION,
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(hours=2),
            metadata={"status": "IN_PROGRESS"}
        )
        
        # Operation stuck >1 hour
        assert resource.is_orphaned(operation_threshold_hours=1)


class TestCleanupStrategy:
    """Test cleanup strategy selection."""
    
    def test_lock_release_strategy(self) -> None:
        """Test lock cleanup releases the lock."""
        strategy = CleanupStrategy.for_resource_type(ResourceType.LOCK)
        
        assert strategy.action == "release_lock"
        assert "Force release" in strategy.description
    
    def test_operation_mark_failed_strategy(self) -> None:
        """Test operation cleanup marks as failed."""
        strategy = CleanupStrategy.for_resource_type(ResourceType.OPERATION)
        
        assert strategy.action == "mark_failed"
        assert "Mark as failed" in strategy.description
    
    def test_state_reset_strategy(self) -> None:
        """Test state cleanup resets to consistent state."""
        strategy = CleanupStrategy.for_resource_type(ResourceType.STATE)
        
        assert strategy.action == "reset_state"
        assert "Reset" in strategy.description


class TestOrphanedResourceCleaner:
    """Test orphan cleaner orchestration."""
    
    @pytest.fixture
    def mock_lock_manager(self) -> Mock:
        """Mock lock manager."""
        manager = Mock()
        manager.get_all_locks.return_value = []
        manager.release_lock = Mock()
        manager.is_lock_held.return_value = False
        return manager
    
    @pytest.fixture
    def mock_operation_tracker(self) -> Mock:
        """Mock operation tracker."""
        tracker = Mock()
        tracker.get_all_operations.return_value = []
        tracker.mark_operation_failed = Mock()
        return tracker
    
    @pytest.fixture
    def cleaner(
        self,
        mock_lock_manager: Mock,
        mock_operation_tracker: Mock
    ) -> OrphanedResourceCleaner:
        """Create cleaner with mocked dependencies."""
        return OrphanedResourceCleaner(
            lock_manager=mock_lock_manager,
            operation_tracker=mock_operation_tracker,
            scan_interval_seconds=300,
            lock_threshold_minutes=10,
            operation_threshold_hours=1
        )
    
    def test_scan_detects_orphaned_locks(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test scanner detects orphaned locks."""
        old_lock = {
            "lock_id": "lock-123",
            "acquired_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "last_heartbeat": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "owner": "process-456"
        }
        mock_lock_manager.get_all_locks.return_value = [old_lock]
        
        orphans = cleaner.scan_for_orphans()
        
        assert len(orphans) == 1
        assert orphans[0].resource_id == "lock-123"
        assert orphans[0].resource_type == ResourceType.LOCK
    
    def test_scan_ignores_active_locks(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test scanner ignores recently active locks."""
        active_lock = {
            "lock_id": "lock-123",
            "acquired_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "last_heartbeat": (datetime.utcnow() - timedelta(minutes=1)).isoformat(),
            "owner": "process-456"
        }
        mock_lock_manager.get_all_locks.return_value = [active_lock]
        
        orphans = cleaner.scan_for_orphans()
        
        assert len(orphans) == 0
    
    def test_cleanup_releases_orphaned_lock(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test cleanup releases orphaned lock."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=15),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={"owner": "process-456"}
        )
        
        result = cleaner.cleanup_resource(resource)
        
        assert result.success is True
        assert result.resource_id == "lock-123"
        mock_lock_manager.release_lock.assert_called_once_with("lock-123", force=True)
    
    def test_cleanup_verifies_liveness_before_releasing(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test cleanup verifies resource not active before cleanup."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=15),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={}
        )
        
        # Lock is actually still held (active)
        mock_lock_manager.is_lock_held.return_value = True
        
        result = cleaner.cleanup_resource(resource)
        
        # Should not clean up active resource
        assert result.success is False
        assert "still active" in result.message.lower()
        mock_lock_manager.release_lock.assert_not_called()
    
    def test_cleanup_marks_operation_failed(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_operation_tracker: Mock
    ) -> None:
        """Test cleanup marks stuck operation as failed."""
        resource = OrphanedResource(
            resource_id="op-123",
            resource_type=ResourceType.OPERATION,
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(hours=2),
            metadata={"status": "IN_PROGRESS"}
        )
        
        result = cleaner.cleanup_resource(resource)
        
        assert result.success is True
        mock_operation_tracker.mark_operation_failed.assert_called_once_with(
            "op-123",
            reason="Orphaned: no activity for 2.0 hours"
        )
    
    def test_cleanup_failure_tracked(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test cleanup failure is tracked."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=15),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={}
        )
        
        mock_lock_manager.release_lock.side_effect = RuntimeError("release failed")
        
        result = cleaner.cleanup_resource(resource)
        
        assert result.success is False
        assert "release failed" in result.message
        assert result.retry_count == 0
    
    def test_cleanup_retries_on_failure(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test cleanup retries failed cleanups."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=15),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={}
        )
        
        # First call fails, second succeeds
        mock_lock_manager.release_lock.side_effect = [
            RuntimeError("temporary failure"),
            None
        ]
        
        # First attempt
        result1 = cleaner.cleanup_resource(resource)
        assert result1.success is False
        
        # Retry
        result2 = cleaner.cleanup_resource(resource, retry_count=1)
        assert result2.success is True
        assert result2.retry_count == 1
    
    def test_cleanup_audit_trail(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test cleanup creates audit trail."""
        resource = OrphanedResource(
            resource_id="lock-123",
            resource_type=ResourceType.LOCK,
            created_at=datetime.utcnow() - timedelta(minutes=15),
            last_activity=datetime.utcnow() - timedelta(minutes=15),
            metadata={"owner": "process-456"}
        )
        
        cleaner.cleanup_resource(resource)
        
        audit = cleaner.get_audit_trail("lock-123")
        
        assert len(audit) > 0
        assert audit[0]["event"] == "cleanup_executed"
        assert audit[0]["resource_id"] == "lock-123"
        assert "justification" in audit[0]
    
    def test_manual_cleanup_override(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock
    ) -> None:
        """Test operator can force cleanup."""
        # Force cleanup even if resource appears active
        mock_lock_manager.is_lock_held.return_value = True
        
        result = cleaner.force_cleanup("lock-123", ResourceType.LOCK, reason="operator override")
        
        assert result.success is True
        assert "operator override" in result.message
        mock_lock_manager.release_lock.assert_called_once()
    
    def test_cascading_cleanup(
        self,
        cleaner: OrphanedResourceCleaner,
        mock_lock_manager: Mock,
        mock_operation_tracker: Mock
    ) -> None:
        """Test related resources cleaned together."""
        # Operation has associated lock
        resource = OrphanedResource(
            resource_id="op-123",
            resource_type=ResourceType.OPERATION,
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_activity=datetime.utcnow() - timedelta(hours=2),
            metadata={"lock_id": "lock-456"}
        )
        
        result = cleaner.cleanup_resource(resource, cascade=True)
        
        assert result.success is True
        # Both operation and associated lock cleaned
        mock_operation_tracker.mark_operation_failed.assert_called_once()
        mock_lock_manager.release_lock.assert_called_once_with("lock-456", force=True)
    
    def test_automatic_scan_schedule(self, cleaner: OrphanedResourceCleaner) -> None:
        """Test automatic scanning runs on schedule."""
        with patch.object(cleaner, 'scan_for_orphans', return_value=[]) as mock_scan:
            cleaner.start_automatic_scan()
            time.sleep(0.1)  # Let scan run
            cleaner.stop_automatic_scan()
            
            # Should have run at least once
            assert mock_scan.call_count >= 1


class TestCleanupIntegration:
    """Integration tests for orphan cleanup scenarios."""
    
    def test_end_to_end_orphan_cleanup(self) -> None:
        """Test complete orphan detection and cleanup flow."""
        lock_manager = Mock()
        operation_tracker = Mock()
        
        # Setup orphaned resources
        old_lock = {
            "lock_id": "lock-orphan",
            "acquired_at": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "last_heartbeat": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "owner": "dead-process"
        }
        lock_manager.get_all_locks.return_value = [old_lock]
        lock_manager.is_lock_held.return_value = False
        
        cleaner = OrphanedResourceCleaner(
            lock_manager=lock_manager,
            operation_tracker=operation_tracker,
            lock_threshold_minutes=10
        )
        
        # Scan and cleanup
        orphans = cleaner.scan_for_orphans()
        assert len(orphans) == 1
        
        result = cleaner.cleanup_resource(orphans[0])
        assert result.success is True
        
        # Verify cleanup executed
        lock_manager.release_lock.assert_called_once_with("lock-orphan", force=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
