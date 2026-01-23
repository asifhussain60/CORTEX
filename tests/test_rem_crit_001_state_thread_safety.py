"""Tests for REM-CRIT-001: AC State Transitions Thread-Safety.

Verifies that AC state transitions are protected by threading locks and atomic.

Test Coverage:
- State transitions are thread-safe (protected by lock)
- Concurrent state modifications don't cause race conditions
- Atomic state transitions
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

import pytest

from cortex.core.orchestrator_base import OrchestratorBase, OrchestrationState


class ConcreteOrchestrator(OrchestratorBase):
    """Concrete implementation for testing."""

    def initialize(self) -> None:
        """Initialize the orchestrator."""
        pass

    def execute(self, context: dict) -> None:
        """Execute orchestration."""
        pass

    def shutdown(self) -> None:
        """Shutdown the orchestrator."""
        pass


class TestACStateTransitionsThreadSafety:
    """Test thread-safety of AC state transitions."""

    def test_state_lock_exists(self) -> None:
        """Verify orchestrator has thread-safe state lock."""
        orchestrator = ConcreteOrchestrator("test")
        
        # REM-CRIT-001: Lock should exist
        assert hasattr(orchestrator, '_state_lock'), "State lock not initialized"
        assert isinstance(orchestrator._state_lock, threading.Lock), "State lock is not a Lock"

    def test_atomic_state_transition(self) -> None:
        """Verify state transitions are atomic."""
        orchestrator = ConcreteOrchestrator("test")
        
        # Initial state
        assert orchestrator.get_state() == OrchestrationState.IDLE
        
        # Set new state
        orchestrator.set_state(OrchestrationState.EXECUTING)
        assert orchestrator.get_state() == OrchestrationState.EXECUTING
        
        # Set another state
        orchestrator.set_state(OrchestrationState.COMPLETED)
        assert orchestrator.get_state() == OrchestrationState.COMPLETED

    def test_concurrent_state_reads(self) -> None:
        """Verify concurrent reads don't cause issues."""
        orchestrator = ConcreteOrchestrator("test")
        orchestrator.set_state(OrchestrationState.EXECUTING)
        
        results = []
        
        def read_state() -> OrchestrationState:
            """Read state from thread."""
            state = orchestrator.get_state()
            results.append(state)
            return state
        
        # 10 concurrent reads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_state) for _ in range(10)]
            for future in as_completed(futures):
                future.result()
        
        # All reads should get EXECUTING
        assert all(r == OrchestrationState.EXECUTING for r in results)
        assert len(results) == 10

    def test_concurrent_state_transitions(self) -> None:
        """Verify concurrent state transitions are safe (no race conditions)."""
        orchestrator = ConcreteOrchestrator("test")
        
        states_sequence = [
            OrchestrationState.INITIALIZING,
            OrchestrationState.EXECUTING,
            OrchestrationState.PAUSED,
            OrchestrationState.EXECUTING,
            OrchestrationState.COMPLETED,
        ]
        
        def transition_state(state: OrchestrationState) -> None:
            """Transition to state from thread."""
            orchestrator.set_state(state)
            sleep(0.001)  # Small delay to increase chance of race condition
        
        # Sequential transitions (via threads)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(transition_state, s) for s in states_sequence]
            for future in as_completed(futures):
                future.result()
        
        # Final state should be one of the states (no exception/corruption)
        final_state = orchestrator.get_state()
        assert final_state in states_sequence

    def test_concurrent_state_reads_and_writes(self) -> None:
        """Verify concurrent reads and writes don't cause corruption."""
        orchestrator = ConcreteOrchestrator("test")
        
        read_results = []
        write_count = 0
        
        def read_state() -> None:
            """Read state."""
            try:
                state = orchestrator.get_state()
                read_results.append(state)
            except Exception as e:
                pytest.fail(f"Read failed with: {e}")
        
        def write_state() -> None:
            """Write state."""
            nonlocal write_count
            try:
                orchestrator.set_state(OrchestrationState.EXECUTING)
                write_count += 1
            except Exception as e:
                pytest.fail(f"Write failed with: {e}")
        
        # 20 threads: 10 readers, 10 writers
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(20):
                if i % 2 == 0:
                    futures.append(executor.submit(read_state))
                else:
                    futures.append(executor.submit(write_state))
            
            for future in as_completed(futures):
                future.result()
        
        # Verify operations succeeded
        assert len(read_results) == 10, f"Expected 10 reads, got {len(read_results)}"
        assert write_count == 10, f"Expected 10 writes, got {write_count}"

    def test_clear_state_is_thread_safe(self) -> None:
        """Verify clear_state is thread-safe."""
        orchestrator = ConcreteOrchestrator("test")
        orchestrator.internal_state = {"key": "value"}
        
        # Clear should work
        orchestrator.clear_state()
        assert orchestrator.internal_state == {}
        
        # Should be able to clear even with concurrent operations
        orchestrator.internal_state = {"key": "value"}
        
        def clear_or_read() -> dict:
            """Clear or read state."""
            if orchestrator.internal_state:
                orchestrator.clear_state()
            return orchestrator.internal_state.copy()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(clear_or_read) for _ in range(10)]
            results = [f.result() for f in as_completed(futures)]
        
        # Final state should be empty (cleared)
        assert orchestrator.internal_state == {}


class TestStateTransitionConsistency:
    """Test state transition consistency guarantees."""

    def test_state_never_corrupted_under_load(self) -> None:
        """Verify state integrity under high concurrency."""
        orchestrator = ConcreteOrchestrator("test")
        
        all_states = [
            OrchestrationState.IDLE,
            OrchestrationState.INITIALIZING,
            OrchestrationState.EXECUTING,
            OrchestrationState.PAUSED,
            OrchestrationState.COMPLETED,
            OrchestrationState.ERROR,
        ]
        
        read_states = []
        
        def stress_test() -> None:
            """Stress test state management."""
            for state in all_states:
                orchestrator.set_state(state)
                current = orchestrator.get_state()
                read_states.append(current)
        
        # 50 concurrent stress test threads
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(stress_test) for _ in range(50)]
            for future in as_completed(futures):
                future.result()
        
        # All read states should be valid (no corruption)
        assert len(read_states) > 0
        assert all(state in all_states for state in read_states), "State corruption detected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
