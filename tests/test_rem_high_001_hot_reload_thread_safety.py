"""Tests for REM-HIGH-001: Hot Reload Thread-Safety.

Verifies that hot reload state transitions are thread-safe and protected by locks.

Test Coverage:
- State transitions are atomic
- Concurrent state changes don't cause race conditions
- Timeout protection on lock acquisition
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

import pytest

from cortex.devx.hot_reload import HotReloadOrchestrator, ReloadState


class TestHotReloadThreadSafety:
    """Test thread-safety of hot reload state management."""

    def test_state_lock_exists(self) -> None:
        """Verify hot reload orchestrator has state lock."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        assert hasattr(orchestrator, '_state_lock'), "State lock not found"
        # threading.Lock is a factory function, not a type
        # Check that the lock has the expected acquire/release methods
        assert hasattr(orchestrator._state_lock, 'acquire'), "State lock missing acquire method"
        assert hasattr(orchestrator._state_lock, 'release'), "State lock missing release method"

    def test_state_property_get(self) -> None:
        """Verify state getter is thread-safe."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        # Should return IDLE initially
        assert orchestrator.state == ReloadState.IDLE

    def test_state_property_set(self) -> None:
        """Verify state setter is thread-safe."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        # Should be able to set state
        orchestrator.state = ReloadState.WATCHING
        assert orchestrator.state == ReloadState.WATCHING
        
        orchestrator.state = ReloadState.PAUSED
        assert orchestrator.state == ReloadState.PAUSED

    def test_state_transition_atomic(self) -> None:
        """Verify state transitions are atomic."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        # Sequence of atomic transitions
        states = [
            ReloadState.IDLE,
            ReloadState.WATCHING,
            ReloadState.PAUSED,
            ReloadState.RELOADING,
            ReloadState.COMPLETED,
        ]
        
        for state in states:
            orchestrator.state = state
            assert orchestrator.state == state

    def test_concurrent_state_reads(self) -> None:
        """Verify concurrent state reads work safely."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        orchestrator.state = ReloadState.WATCHING
        
        read_states = []
        
        def read_state() -> None:
            """Read state from thread."""
            state = orchestrator.state
            read_states.append(state)
        
        # 50 concurrent reads
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(read_state) for _ in range(50)]
            for future in as_completed(futures):
                future.result()
        
        # All reads should get WATCHING
        assert len(read_states) == 50
        assert all(s == ReloadState.WATCHING for s in read_states)

    def test_concurrent_state_transitions(self) -> None:
        """Verify concurrent state transitions are safe."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        states_sequence = [
            ReloadState.IDLE,
            ReloadState.WATCHING,
            ReloadState.PAUSED,
            ReloadState.WATCHING,
            ReloadState.RELOADING,
            ReloadState.COMPLETED,
        ]
        
        def set_state(state: ReloadState) -> None:
            """Set state from thread."""
            orchestrator.state = state
            sleep(0.001)
        
        # Sequential transitions via threads
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(set_state, s) for s in states_sequence]
            for future in as_completed(futures):
                future.result()
        
        # Final state should be valid
        final = orchestrator.state
        assert final in states_sequence

    def test_state_lock_timeout(self) -> None:
        """Verify state lock has timeout protection."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        assert hasattr(orchestrator, '_state_timeout')
        assert orchestrator._state_timeout > 0

    def test_concurrent_mixed_operations(self) -> None:
        """Verify concurrent mixed read/write operations."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        operation_count = [0]
        
        def mixed_operation(op_id: int) -> None:
            """Mixed state operation."""
            try:
                if op_id % 2 == 0:
                    # Read
                    _ = orchestrator.state
                else:
                    # Write
                    orchestrator.state = ReloadState.WATCHING
                operation_count[0] += 1
            except Exception as e:
                pytest.fail(f"Operation failed: {e}")
        
        # 100 mixed operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(100)]
            for future in as_completed(futures):
                future.result()
        
        assert operation_count[0] == 100


class TestReloadStateConsistency:
    """Test reload state consistency under load."""

    def test_state_never_corrupted(self) -> None:
        """Verify state integrity under high concurrency."""
        orchestrator = HotReloadOrchestrator("/tmp/test")
        
        all_states = [
            ReloadState.IDLE,
            ReloadState.WATCHING,
            ReloadState.PAUSED,
            ReloadState.RELOADING,
            ReloadState.COMPLETED,
            ReloadState.ERROR,
        ]
        
        read_states = []
        
        def stress_state_operations() -> None:
            """Stress test state management."""
            for state in all_states:
                orchestrator.state = state
                current = orchestrator.state
                read_states.append(current)
        
        # 30 concurrent stress threads
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(stress_state_operations) for _ in range(30)]
            for future in as_completed(futures):
                future.result()
        
        # All state reads should be valid
        assert len(read_states) > 0
        assert all(s in all_states for s in read_states)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
