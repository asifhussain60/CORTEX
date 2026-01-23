"""Tests for REM-HIGH-002: Orchestrator Coordinator Deadlock Prevention.

Verifies that orchestrator coordination prevents deadlocks through:
- Strict lock ordering
- Lock acquisition timeouts
- Deadlock detection
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from typing import List

import pytest

from cortex.orchestrators.coordinator import (
    OrchestrationCoordinator,
    get_coordinator,
)


class TestOrchestrationCoordinator:
    """Test orchestration coordinator."""

    def test_coordinator_initialization(self) -> None:
        """Verify coordinator initializes with all locks."""
        coordinator = OrchestrationCoordinator()
        
        # Should have locks for all ordered names
        expected_locks = [
            'orchestrator_registry',
            'state_machine',
            'execution_queue',
            'results',
        ]
        
        for lock_name in expected_locks:
            assert lock_name in coordinator._locks
            assert coordinator._locks[lock_name] is not None

    def test_lock_acquisition_with_timeout(self) -> None:
        """Verify lock acquisition with timeout."""
        coordinator = OrchestrationCoordinator()
        
        # Should acquire lock
        result = coordinator.acquire_lock('orchestrator_registry', timeout=5.0)
        assert result is True
        
        # Release it
        coordinator.release_lock('orchestrator_registry')

    def test_lock_ordering_enforcement(self) -> None:
        """Verify strict lock ordering is enforced."""
        coordinator = OrchestrationCoordinator()
        
        locks = [
            'results',
            'orchestrator_registry',
            'execution_queue',
            'state_machine',
        ]
        
        # Should acquire in deterministic order
        result = coordinator.enforce_lock_ordering(locks)
        assert result is True
        
        # Release all
        coordinator.release_all_locks(locks)

    def test_deadlock_timeout_protection(self) -> None:
        """Verify deadlock detection timeout."""
        coordinator = OrchestrationCoordinator()
        
        # Acquire lock
        coordinator.acquire_lock('orchestrator_registry', timeout=5.0)
        
        # Check for deadlocks (shouldn't find any - just acquired)
        deadlocks = coordinator.detect_deadlock()
        assert len(deadlocks) == 0
        
        coordinator.release_lock('orchestrator_registry')

    def test_orchestrator_registration(self) -> None:
        """Verify orchestrator registration is thread-safe."""
        coordinator = OrchestrationCoordinator()
        
        class MockOrchestrator:
            def __init__(self, name: str):
                self.name = name
        
        # Register orchestrator
        orch = MockOrchestrator("test")
        result = coordinator.register_orchestrator("test_orch", orch)
        assert result is True
        
        # Get orchestrator
        retrieved = coordinator.get_orchestrator("test_orch")
        assert retrieved is not None
        assert retrieved.name == "test"

    def test_concurrent_lock_operations(self) -> None:
        """Verify concurrent lock operations don't deadlock."""
        coordinator = OrchestrationCoordinator()
        
        success_count = [0]
        
        def lock_operation(op_id: int) -> None:
            """Perform lock operation from thread."""
            try:
                # Acquire multiple locks in order
                locks_needed = [
                    'orchestrator_registry',
                    'state_machine',
                    'execution_queue',
                ]
                
                if coordinator.enforce_lock_ordering(locks_needed):
                    sleep(0.001)  # Simulate work
                    coordinator.release_all_locks(locks_needed)
                    success_count[0] += 1
            except Exception as e:
                pytest.fail(f"Lock operation failed: {e}")
        
        # 20 concurrent operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(lock_operation, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()
        
        assert success_count[0] == 20

    def test_timeout_prevents_hanging(self) -> None:
        """Verify lock acquisition timeout prevents hanging."""
        coordinator = OrchestrationCoordinator()
        
        # Acquire lock first
        coordinator.acquire_lock('orchestrator_registry', timeout=5.0)
        
        # Try to acquire same lock from different thread - should timeout
        timeout_result = [None]
        
        def try_acquire() -> None:
            result = coordinator.acquire_lock(
                'orchestrator_registry',
                timeout=0.1  # Very short timeout
            )
            timeout_result[0] = result
        
        import threading
        thread = threading.Thread(target=try_acquire)
        thread.start()
        thread.join()
        
        # Should have timed out
        assert timeout_result[0] is False
        
        # Release original lock
        coordinator.release_lock('orchestrator_registry')

    def test_lock_ordering_prevents_deadlock(self) -> None:
        """Verify lock ordering prevents potential deadlock situations."""
        coordinator = OrchestrationCoordinator()
        
        results: List[bool] = []
        
        def acquire_in_order(thread_id: int) -> None:
            """Acquire locks in different orders."""
            if thread_id % 2 == 0:
                # Even threads: order A
                locks = ['orchestrator_registry', 'state_machine', 'execution_queue']
            else:
                # Odd threads: order B (would normally cause deadlock)
                locks = ['execution_queue', 'state_machine', 'orchestrator_registry']
            
            # But enforce_lock_ordering forces deterministic order
            success = coordinator.enforce_lock_ordering(locks)
            results.append(success)
            coordinator.release_all_locks(locks)
        
        # 50 concurrent threads with potentially conflicting lock orders
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(acquire_in_order, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()
        
        # All should succeed (no deadlock)
        assert len(results) == 50
        assert all(results)


class TestGlobalCoordinator:
    """Test global coordinator singleton."""

    def test_singleton_instance(self) -> None:
        """Verify global coordinator is a singleton."""
        coord1 = get_coordinator()
        coord2 = get_coordinator()
        
        assert coord1 is coord2

    def test_concurrent_singleton_access(self) -> None:
        """Verify concurrent access to singleton is thread-safe."""
        coordinators = []
        
        def get_coord() -> None:
            coordinator = get_coordinator()
            coordinators.append(coordinator)
        
        # 50 concurrent accesses
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(get_coord) for _ in range(50)]
            for future in as_completed(futures):
                future.result()
        
        # All should be same instance
        assert len(set(id(c) for c in coordinators)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
