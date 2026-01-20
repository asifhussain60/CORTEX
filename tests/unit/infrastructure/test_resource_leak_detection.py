"""
Tests for Resource Tracking and Leak Detection.

AC-INFRA-001-06: Resource Tracking
Tests comprehensive resource tracking, automatic cleanup,
and leak detection for connections, file handles, and memory.
"""

import pytest
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

from cortex.infrastructure.resource_tracker import (
    ResourceTracker,
    ResourceType,
    TrackedResource,
    ResourceLeakError,
)


@pytest.fixture
def resource_tracker() -> ResourceTracker:
    """Create resource tracker instance."""
    tracker = ResourceTracker(leak_detection_enabled=True)
    yield tracker
    tracker.shutdown()


class TestResourceRegistration:
    """Test resource registration and tracking."""

    def test_registers_connection(self, resource_tracker: ResourceTracker) -> None:
        """Should register database connection."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        )
        
        assert resource_id is not None
        assert resource_tracker.get_active_count(ResourceType.CONNECTION) == 1

    def test_registers_file_handle(self, resource_tracker: ResourceTracker) -> None:
        """Should register file handle."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            file_path = f.name
            resource_id = resource_tracker.register(
                resource=f,
                resource_type=ResourceType.FILE,
                name=file_path
            )
            
            assert resource_id is not None
            assert resource_tracker.get_active_count(ResourceType.FILE) == 1
        
        # Cleanup
        Path(file_path).unlink(missing_ok=True)

    def test_registers_lock(self, resource_tracker: ResourceTracker) -> None:
        """Should register threading lock."""
        lock = threading.Lock()
        resource_id = resource_tracker.register(
            resource=lock,
            resource_type=ResourceType.LOCK,
            name="test_lock"
        )
        
        assert resource_id is not None
        assert resource_tracker.get_active_count(ResourceType.LOCK) == 1


class TestResourceRelease:
    """Test resource release and cleanup."""

    def test_releases_registered_resource(self, resource_tracker: ResourceTracker) -> None:
        """Should release resource by ID."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        )
        
        resource_tracker.release(resource_id)
        assert resource_tracker.get_active_count(ResourceType.CONNECTION) == 0

    def test_calls_cleanup_function(self, resource_tracker: ResourceTracker) -> None:
        """Should call cleanup function on release."""
        conn = Mock()
        cleanup_called = False
        
        def cleanup(res):
            nonlocal cleanup_called
            cleanup_called = True
            res.close()
        
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection",
            cleanup_func=cleanup
        )
        
        resource_tracker.release(resource_id)
        assert cleanup_called
        assert conn.close.called

    def test_handles_cleanup_exception(self, resource_tracker: ResourceTracker) -> None:
        """Should handle exceptions during cleanup gracefully."""
        conn = Mock()
        
        def cleanup(res):
            raise RuntimeError("Cleanup failed")
        
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection",
            cleanup_func=cleanup
        )
        
        # Should not raise exception
        resource_tracker.release(resource_id)


class TestAutomaticCleanup:
    """Test automatic cleanup on exception."""

    def test_cleans_up_on_context_exit(self, resource_tracker: ResourceTracker) -> None:
        """Should automatically clean up resources in context manager."""
        conn = Mock()
        
        with resource_tracker.track(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        ):
            assert resource_tracker.get_active_count(ResourceType.CONNECTION) == 1
        
        assert resource_tracker.get_active_count(ResourceType.CONNECTION) == 0

    def test_cleans_up_on_exception(self, resource_tracker: ResourceTracker) -> None:
        """Should clean up resources even on exception."""
        conn = Mock()
        
        try:
            with resource_tracker.track(
                resource=conn,
                resource_type=ResourceType.CONNECTION,
                name="test_connection"
            ):
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        assert resource_tracker.get_active_count(ResourceType.CONNECTION) == 0


class TestLeakDetection:
    """Test resource leak detection."""

    def test_detects_leaked_connection(self, resource_tracker: ResourceTracker) -> None:
        """Should detect leaked database connection."""
        conn = Mock()
        resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="leaked_connection",
            leak_timeout_seconds=0.2
        )
        
        # Wait for leak detection
        time.sleep(0.3)
        
        leaks = resource_tracker.get_leaked_resources()
        assert len(leaks) >= 1

    def test_warns_on_leaked_resources(self, resource_tracker: ResourceTracker) -> None:
        """Should issue warnings for leaked resources."""
        conn = Mock()
        resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="leaked_connection",
            leak_timeout_seconds=0.1
        )
        
        time.sleep(0.2)
        
        # Manually trigger leak check (background thread may not run in time)
        resource_tracker._check_for_leaks()
        
        warnings = resource_tracker.get_leak_warnings()
        assert len(warnings) >= 1

    def test_no_leak_when_properly_released(self, resource_tracker: ResourceTracker) -> None:
        """Should not detect leak when resource is properly released."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="proper_connection",
            leak_timeout_seconds=0.1
        )
        
        resource_tracker.release(resource_id)
        time.sleep(0.2)
        
        leaks = resource_tracker.get_leaked_resources()
        assert len(leaks) == 0


class TestForcedCleanup:
    """Test forced cleanup on shutdown."""

    def test_cleans_all_resources_on_shutdown(self, resource_tracker: ResourceTracker) -> None:
        """Should forcibly clean up all resources on shutdown."""
        conns = [Mock() for _ in range(3)]
        for i, conn in enumerate(conns):
            resource_tracker.register(
                resource=conn,
                resource_type=ResourceType.CONNECTION,
                name=f"conn_{i}"
            )
        
        assert resource_tracker.get_total_active_count() == 3
        
        resource_tracker.shutdown()
        
        assert resource_tracker.get_total_active_count() == 0

    def test_calls_all_cleanup_functions(self, resource_tracker: ResourceTracker) -> None:
        """Should call cleanup functions for all resources on shutdown."""
        cleanup_counts = {"count": 0}
        
        def cleanup(res):
            cleanup_counts["count"] += 1
            res.close()
        
        conns = [Mock() for _ in range(3)]
        for i, conn in enumerate(conns):
            resource_tracker.register(
                resource=conn,
                resource_type=ResourceType.CONNECTION,
                name=f"conn_{i}",
                cleanup_func=cleanup
            )
        
        resource_tracker.shutdown()
        
        assert cleanup_counts["count"] == 3


class TestResourceMetrics:
    """Test resource tracking metrics."""

    def test_tracks_total_created(self, resource_tracker: ResourceTracker) -> None:
        """Should track total resources created."""
        conns = [Mock() for _ in range(3)]
        for i, conn in enumerate(conns):
            resource_tracker.register(
                resource=conn,
                resource_type=ResourceType.CONNECTION,
                name=f"conn_{i}"
            )
        
        metrics = resource_tracker.get_metrics()
        assert metrics["total_created"] >= 3

    def test_tracks_total_released(self, resource_tracker: ResourceTracker) -> None:
        """Should track total resources released."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        )
        
        resource_tracker.release(resource_id)
        
        metrics = resource_tracker.get_metrics()
        assert metrics["total_released"] >= 1

    def test_tracks_active_by_type(self, resource_tracker: ResourceTracker) -> None:
        """Should track active resources by type."""
        conn1 = Mock()
        conn2 = Mock()
        lock = threading.Lock()
        
        resource_tracker.register(conn1, ResourceType.CONNECTION, "conn1")
        resource_tracker.register(conn2, ResourceType.CONNECTION, "conn2")
        resource_tracker.register(lock, ResourceType.LOCK, "lock1")
        
        metrics = resource_tracker.get_metrics()
        assert metrics["active_by_type"][ResourceType.CONNECTION.value] == 2
        assert metrics["active_by_type"][ResourceType.LOCK.value] == 1


class TestConcurrency:
    """Test thread-safe resource tracking."""

    def test_concurrent_registration(self, resource_tracker: ResourceTracker) -> None:
        """Should handle concurrent resource registration."""
        def register_resources():
            for i in range(10):
                conn = Mock()
                resource_tracker.register(
                    resource=conn,
                    resource_type=ResourceType.CONNECTION,
                    name=f"conn_{threading.current_thread().name}_{i}"
                )
        
        threads = [threading.Thread(target=register_resources) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert resource_tracker.get_total_active_count() == 50

    def test_concurrent_release(self, resource_tracker: ResourceTracker) -> None:
        """Should handle concurrent resource release."""
        # Register resources
        resource_ids = []
        for i in range(50):
            conn = Mock()
            rid = resource_tracker.register(
                resource=conn,
                resource_type=ResourceType.CONNECTION,
                name=f"conn_{i}"
            )
            resource_ids.append(rid)
        
        # Release concurrently
        def release_batch(ids):
            for rid in ids:
                resource_tracker.release(rid)
        
        batch_size = 10
        threads = [
            threading.Thread(target=release_batch, args=(resource_ids[i:i+batch_size],))
            for i in range(0, len(resource_ids), batch_size)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert resource_tracker.get_total_active_count() == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_handles_double_release(self, resource_tracker: ResourceTracker) -> None:
        """Should handle double release gracefully."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        )
        
        resource_tracker.release(resource_id)
        # Second release should not error
        resource_tracker.release(resource_id)

    def test_handles_invalid_resource_id(self, resource_tracker: ResourceTracker) -> None:
        """Should handle invalid resource ID gracefully."""
        # Should not raise exception
        resource_tracker.release("invalid_id")

    def test_tracks_resource_lifetime(self, resource_tracker: ResourceTracker) -> None:
        """Should track resource lifetime."""
        conn = Mock()
        resource_id = resource_tracker.register(
            resource=conn,
            resource_type=ResourceType.CONNECTION,
            name="test_connection"
        )
        
        time.sleep(0.1)
        
        info = resource_tracker.get_resource_info(resource_id)
        assert info is not None
        assert info["lifetime_seconds"] >= 0.1
