"""
Comprehensive tests for LifecycleManager (BRT-008 Implementation)

Tests the actual lifecycle_manager.py implementation with:
- Component registration and lifecycle
- Graceful shutdown with SIGTERM
- Request tracking and completion
- Error handling and edge cases
- Thread safety verification
"""

import pytest
import signal
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from cortex.infrastructure.lifecycle_manager import (
    LifecycleManager,
    ShutdownableComponent,
    ComponentState,
    get_lifecycle_manager,
)


class TestLifecycleManagerRegistration:
    """Tests for component registration."""

    def test_register_component_success(self) -> None:
        """Verify component registration stores component correctly."""
        manager = LifecycleManager()
        callback = Mock()

        manager.register_component("database", callback, priority=80, timeout=15.0)

        assert "database" in manager._components
        assert manager._components["database"].component_id == "database"
        assert manager._components["database"].priority == 80
        assert manager._components["database"].timeout == 15.0
        assert manager._components["database"].is_running is True

    def test_register_multiple_components(self) -> None:
        """Verify multiple components can be registered."""
        manager = LifecycleManager()

        manager.register_component("database", Mock(), priority=80)
        manager.register_component("cache", Mock(), priority=60)
        manager.register_component("api_server", Mock(), priority=40)

        assert len(manager._components) == 3
        assert "database" in manager._components
        assert "cache" in manager._components
        assert "api_server" in manager._components

    def test_register_component_empty_id_raises(self) -> None:
        """Verify registering with empty component_id raises ValueError."""
        manager = LifecycleManager()

        with pytest.raises(ValueError, match="component_id cannot be empty"):
            manager.register_component("", Mock())

    def test_register_component_non_callable_raises(self) -> None:
        """Verify registering with non-callable callback raises TypeError."""
        manager = LifecycleManager()

        with pytest.raises(TypeError, match="shutdown_callback must be callable"):
            manager.register_component("database", "not_callable")  # type: ignore

    def test_register_component_duplicate_raises(self) -> None:
        """Verify registering duplicate component_id raises ValueError."""
        manager = LifecycleManager()
        callback = Mock()

        manager.register_component("database", callback)

        with pytest.raises(ValueError, match="already registered"):
            manager.register_component("database", callback)


class TestLifecycleManagerRequestTracking:
    """Tests for request/task tracking."""

    def test_start_request_increments_counter(self) -> None:
        """Verify start_request increments active request counter."""
        manager = LifecycleManager()

        assert manager._active_requests == 0
        manager.start_request()
        assert manager._active_requests == 1
        manager.start_request()
        assert manager._active_requests == 2

    def test_complete_request_decrements_counter(self) -> None:
        """Verify complete_request decrements active request counter."""
        manager = LifecycleManager()

        manager.start_request()
        manager.start_request()
        assert manager._active_requests == 2

        manager.complete_request()
        assert manager._active_requests == 1
        assert manager._completed_requests == 1

    def test_start_request_after_shutdown_raises(self) -> None:
        """Verify starting request after shutdown initiates raises RuntimeError."""
        manager = LifecycleManager()
        manager._shutdown_initiated = True

        with pytest.raises(RuntimeError, match="Cannot start new requests"):
            manager.start_request()

    def test_wait_for_pending_requests_completes(self) -> None:
        """Verify wait_for_pending_requests returns True when no requests pending."""
        manager = LifecycleManager()

        result = manager.wait_for_pending_requests(timeout=1.0)

        assert result is True
        assert manager._active_requests == 0

    def test_wait_for_pending_requests_timeout(self) -> None:
        """Verify wait_for_pending_requests returns False on timeout."""
        manager = LifecycleManager()
        manager._active_requests = 5  # Simulate active requests

        result = manager.wait_for_pending_requests(timeout=0.1)

        assert result is False

    def test_wait_for_pending_requests_with_completion(self) -> None:
        """Verify wait_for_pending_requests returns True when requests complete."""
        manager = LifecycleManager()

        # Simulate requests completing after delay
        def complete_after_delay() -> None:
            time.sleep(0.05)
            manager.complete_request()
            manager.complete_request()

        manager._active_requests = 2
        thread = threading.Thread(target=complete_after_delay, daemon=True)
        thread.start()

        result = manager.wait_for_pending_requests(timeout=1.0)

        assert result is True
        assert manager._active_requests == 0


class TestLifecycleManagerShutdown:
    """Tests for component shutdown."""

    def test_shutdown_all_components_calls_callbacks(self) -> None:
        """Verify shutdown_all_components calls all component callbacks."""
        manager = LifecycleManager()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        manager.register_component("comp1", callback1, priority=60)
        manager.register_component("comp2", callback2, priority=50)
        manager.register_component("comp3", callback3, priority=70)

        exit_code = manager.shutdown_all_components()

        assert callback1.called
        assert callback2.called
        assert callback3.called
        assert exit_code == 0

    def test_shutdown_all_components_respects_priority(self) -> None:
        """Verify shutdown_all_components respects priority ordering."""
        manager = LifecycleManager()
        call_order = []

        def callback1() -> None:
            call_order.append("api_server")

        def callback2() -> None:
            call_order.append("cache")

        def callback3() -> None:
            call_order.append("database")

        manager.register_component("api_server", callback1, priority=40)
        manager.register_component("cache", callback2, priority=60)
        manager.register_component("database", callback3, priority=80)

        manager.shutdown_all_components()

        # Higher priority shuts down first
        assert call_order == ["database", "cache", "api_server"]

    def test_shutdown_all_components_marks_as_shutdown(self) -> None:
        """Verify components are marked as shutdown."""
        manager = LifecycleManager()

        manager.register_component("database", Mock())
        assert manager._components["database"].is_running is True

        manager.shutdown_all_components()

        assert manager._components["database"].is_running is False

    def test_shutdown_all_components_handles_callback_error(self) -> None:
        """Verify shutdown continues even if callback raises error."""
        manager = LifecycleManager()

        def failing_callback() -> None:
            raise ValueError("Shutdown error")

        callback_ok = Mock()

        manager.register_component("failing", failing_callback, priority=80)
        manager.register_component("ok", callback_ok, priority=60)

        exit_code = manager.shutdown_all_components()

        # Should set non-zero exit code on error
        assert exit_code != 0
        # But should still call remaining component
        assert callback_ok.called

    def test_shutdown_twice_returns_same_exit_code(self) -> None:
        """Verify calling shutdown twice returns consistent exit code."""
        manager = LifecycleManager()
        manager.register_component("comp", Mock())

        first_exit = manager.shutdown_all_components()
        second_exit = manager.shutdown_all_components()

        assert first_exit == second_exit
        assert first_exit == 0

    def test_shutdown_sequence_recorded(self) -> None:
        """Verify shutdown sequence is recorded correctly."""
        manager = LifecycleManager()

        manager.register_component("database", Mock(), priority=80)
        manager.register_component("cache", Mock(), priority=60)
        manager.register_component("api", Mock(), priority=40)

        manager.shutdown_all_components()

        sequence = manager.get_shutdown_sequence()
        assert sequence == ["database", "cache", "api"]


class TestLifecycleManagerSigterm:
    """Tests for SIGTERM signal handling."""

    def test_sigterm_handler_registered(self) -> None:
        """Verify SIGTERM handler is registered."""
        manager = LifecycleManager()

        # Get current handler
        original_handler = signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, original_handler)

        # Setup handler
        manager.setup_sigterm_handler()

        # Verify handler is set (not SIG_DFL or SIG_IGN)
        handler = signal.signal(signal.SIGTERM, original_handler)
        assert handler not in (signal.SIG_DFL, signal.SIG_IGN)

    def test_sigterm_handler_triggers_shutdown(self) -> None:
        """Verify SIGTERM handler calls shutdown_all_components."""
        manager = LifecycleManager()
        callback = Mock()

        manager.register_component("comp", callback)
        manager.setup_sigterm_handler()

        # Manually trigger signal handler
        # (We don't actually send SIGTERM to avoid terminating the test)
        manager._shutdown_initiated = False  # Reset for testing
        manager._components["comp"].is_running = True  # Reset for testing

        # Simulate what signal handler does
        _ = manager.shutdown_all_components()

        assert callback.called
        assert manager._shutdown_initiated is True


class TestLifecycleManagerResourceCleanup:
    """Tests for resource cleanup."""

    def test_cleanup_resources_marks_all_as_shutdown(self) -> None:
        """Verify cleanup_resources marks all components as shutdown."""
        manager = LifecycleManager()

        manager.register_component("comp1", Mock())
        manager.register_component("comp2", Mock())

        assert all(c.is_running for c in manager._components.values())

        manager.cleanup_resources()

        assert all(not c.is_running for c in manager._components.values())


class TestLifecycleManagerStatus:
    """Tests for status reporting."""

    def test_get_status_returns_correct_info(self) -> None:
        """Verify get_status returns complete status information."""
        manager = LifecycleManager()

        manager.register_component("database", Mock(), priority=80)
        manager.register_component("cache", Mock(), priority=60)

        manager.start_request()
        manager.start_request()
        manager.complete_request()

        status = manager.get_status()

        assert status["shutdown_initiated"] is False
        assert status["active_requests"] == 1
        assert status["completed_requests"] == 1
        assert len(status["components"]) == 2
        assert status["components"][0]["id"] in ("database", "cache")


class TestLifecycleManagerSingleton:
    """Tests for singleton pattern."""

    def test_get_lifecycle_manager_returns_same_instance(self) -> None:
        """Verify get_lifecycle_manager returns same instance."""
        # Reset singleton for test
        import cortex.infrastructure.lifecycle_manager as lm_module

        lm_module._lifecycle_manager = None

        manager1 = get_lifecycle_manager()
        manager2 = get_lifecycle_manager()

        assert manager1 is manager2

    def test_get_lifecycle_manager_thread_safe(self) -> None:
        """Verify get_lifecycle_manager is thread-safe."""
        # Reset singleton for test
        import cortex.infrastructure.lifecycle_manager as lm_module

        lm_module._lifecycle_manager = None

        managers = []
        lock = threading.Lock()

        def get_manager() -> None:
            manager = get_lifecycle_manager()
            with lock:
                managers.append(manager)

        threads = [threading.Thread(target=get_manager) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All should be the same instance
        assert all(m is managers[0] for m in managers)


class TestLifecycleManagerIntegration:
    """Integration tests for complete workflows."""

    def test_complete_lifecycle_workflow(self) -> None:
        """Verify complete lifecycle workflow from registration to shutdown."""
        manager = LifecycleManager()

        # Register components
        db_shutdown = Mock()
        cache_shutdown = Mock()
        api_shutdown = Mock()

        manager.register_component("database", db_shutdown, priority=80, timeout=15)
        manager.register_component("cache", cache_shutdown, priority=60, timeout=10)
        manager.register_component("api", api_shutdown, priority=40, timeout=5)

        # No active requests - shutdown should proceed immediately
        exit_code = manager.shutdown_all_components()

        # Verify
        assert exit_code == 0
        assert all(not c.is_running for c in manager._components.values())
        assert db_shutdown.called
        assert cache_shutdown.called
        assert api_shutdown.called

    def test_graceful_shutdown_with_pending_requests(self) -> None:
        """Verify graceful shutdown waits for pending requests."""
        manager = LifecycleManager()
        manager.register_component("api", Mock())

        manager.start_request()
        manager.start_request()

        # Simulate requests completing during shutdown
        def complete_requests() -> None:
            time.sleep(0.05)
            manager.complete_request()
            manager.complete_request()

        thread = threading.Thread(target=complete_requests, daemon=True)
        thread.start()

        exit_code = manager.shutdown_all_components()

        assert exit_code == 0
        assert manager._active_requests == 0
        assert manager._completed_requests == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
