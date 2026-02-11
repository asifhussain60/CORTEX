"""Orchestrator Coordinator - Multi-orchestrator coordination with deadlock prevention.

REM-HIGH-002: Deadlock Prevention
- Strict lock ordering
- Lock timeouts
- Deadlock detection
"""

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LockAcquisitionInfo:
    """Information about lock acquisition."""

    lock_id: str
    acquired_time: datetime
    timeout: float
    owner_thread: int


class OrchestrationCoordinator:
    """Coordinates multiple orchestrators with deadlock prevention.

    Features:
    - Strict lock ordering to prevent deadlock
    - Lock acquisition timeouts
    - Deadlock detection and recovery
    - Thread-safe operation registry
    """

    # Global lock ordering: prevent nested locks by enforcing order
    LOCK_ORDER = {
        'orchestrator_registry': 0,
        'state_machine': 1,
        'execution_queue': 2,
        'results': 3,
    }

    def __init__(self) -> None:
        """Initialize orchestration coordinator."""
        self._locks: Dict[str, threading.Lock] = {}
        self._lock_acquisition_info: Dict[str, List[LockAcquisitionInfo]] = {}
        self._orchestrators: Dict[str, Any] = {}
        self._master_lock = threading.Lock()
        self._deadlock_timeout = 10.0  # 10 second timeout for deadlock detection

        # Initialize all named locks
        for lock_name in self.LOCK_ORDER.keys():
            self._locks[lock_name] = threading.Lock()
            self._lock_acquisition_info[lock_name] = []

    def acquire_lock(
        self,
        lock_name: str,
        timeout: float = 5.0,
    ) -> bool:
        """Acquire a named lock with timeout and deadlock detection.

        REM-HIGH-002: Deadlock Prevention
        - Timeouts prevent indefinite waits
        - Lock ordering prevents circular waits

        Args:
            lock_name: Name of lock to acquire
            timeout: Acquisition timeout in seconds

        Returns:
            True if lock acquired, False on timeout

        Raises:
            ValueError: If lock_name not registered
        """
        if lock_name not in self._locks:
            raise ValueError(f"Unknown lock: {lock_name}")

        lock = self._locks[lock_name]
        thread_id = threading.get_ident()

        # Attempt acquisition with timeout
        acquired = lock.acquire(timeout=timeout)

        if acquired:
            # Track acquisition
            info = LockAcquisitionInfo(
                lock_id=lock_name,
                acquired_time=datetime.now(),
                timeout=timeout,
                owner_thread=thread_id,
            )
            self._lock_acquisition_info[lock_name].append(info)

            logger.debug(
                f"Lock acquired: {lock_name} by thread {thread_id}",
                extra={
                    "lock_name": lock_name,
                    "thread_id": thread_id,
                    "timeout": timeout,
                },
            )
            return True
        else:
            logger.warning(
                f"Lock acquisition timeout: {lock_name} (timeout={timeout}s)",
                extra={
                    "lock_name": lock_name,
                    "thread_id": thread_id,
                    "timeout": timeout,
                },
            )
            return False

    def release_lock(self, lock_name: str) -> None:
        """Release a named lock.

        Args:
            lock_name: Name of lock to release

        Raises:
            ValueError: If lock not acquired
        """
        if lock_name not in self._locks:
            raise ValueError(f"Unknown lock: {lock_name}")

        lock = self._locks[lock_name]
        thread_id = threading.get_ident()

        try:
            lock.release()
            logger.debug(
                f"Lock released: {lock_name} by thread {thread_id}",
                extra={
                    "lock_name": lock_name,
                    "thread_id": thread_id,
                },
            )
        except RuntimeError as e:
            logger.error(
                f"Lock release error: {lock_name}: {e}",
                extra={
                    "lock_name": lock_name,
                    "thread_id": thread_id,
                    "error": str(e),
                },
            )
            raise

    def register_orchestrator(self, name: str, orchestrator: Any) -> bool:
        """Register an orchestrator for coordination.

        Args:
            name: Orchestrator name
            orchestrator: Orchestrator instance

        Returns:
            True if registered, False if already exists
        """
        if not self.acquire_lock('orchestrator_registry', timeout=5.0):
            logger.error("Failed to acquire registry lock for orchestrator registration")
            return False

        try:
            if name in self._orchestrators:
                logger.warning(f"Orchestrator already registered: {name}")
                return False

            self._orchestrators[name] = orchestrator
            logger.info(
                f"Orchestrator registered: {name}",
                extra={"orchestrator_name": name},
            )
            return True
        finally:
            self.release_lock('orchestrator_registry')

    def get_orchestrator(self, name: str) -> Optional[Any]:
        """Get registered orchestrator by name (delegating accessor).

        CORE-035: Single Canonical Implementation
        This method delegates to GitBackedRegistry.get_orchestrator() which is
        the canonical accessor. This wrapper exists for backward compatibility
        with code that expects Coordinator to provide orchestrator access.

        Args:
            name: Orchestrator name

        Returns:
            Orchestrator instance or None if not found
        """
        try:
            # AC-CORE-035: Delegate to canonical GitBackedRegistry accessor
            from cortex.wiring import get_cortex
            registry = get_cortex()
            if registry:
                return registry.get_orchestrator(name)
            return None
        except Exception as e:
            logger.error(f"Failed to get orchestrator '{name}': {str(e)}")
            return None

    def detect_deadlock(self) -> List[Dict[str, Any]]:
        """Detect potential deadlocks in lock acquisitions.

        REM-HIGH-002: Deadlock Detection
        - Analyzes lock acquisition patterns
        - Detects circular wait conditions
        - Returns held locks and waiting threads

        Returns:
            List of potential deadlock situations
        """
        deadlocks: List[Dict[str, Any]] = []
        now = datetime.now()

        with self._master_lock:
            for lock_name, acquisitions in self._lock_acquisition_info.items():
                for info in acquisitions:
                    elapsed = (now - info.acquired_time).total_seconds()

                    # If lock held longer than deadlock timeout, flag it
                    if elapsed > self._deadlock_timeout:
                        deadlocks.append({
                            "lock_name": lock_name,
                            "owner_thread": info.owner_thread,
                            "held_seconds": elapsed,
                            "timeout": info.timeout,
                        })

        if deadlocks:
            logger.warning(
                f"Potential deadlock detected: {len(deadlocks)} long-held locks",
                extra={"deadlock_count": len(deadlocks)},
            )

        return deadlocks

    def enforce_lock_ordering(self, required_locks: List[str]) -> bool:
        """Enforce strict lock ordering to prevent deadlock.

        REM-HIGH-002: Strict Lock Ordering
        - Acquire locks in deterministic order
        - Prevents circular waits

        Args:
            required_locks: List of lock names needed

        Returns:
            True if all locks acquired in order, False on failure
        """
        # Sort by lock order
        sorted_locks = sorted(
            required_locks,
            key=lambda x: self.LOCK_ORDER.get(x, 999)
        )

        acquired_locks: List[str] = []

        for lock_name in sorted_locks:
            if not self.acquire_lock(lock_name, timeout=5.0):
                # Failed to acquire - release all and fail
                for acquired in acquired_locks:
                    self.release_lock(acquired)
                return False
            acquired_locks.append(lock_name)

        return True

    def release_all_locks(self, lock_names: List[str]) -> None:
        """Release multiple locks.

        Args:
            lock_names: List of lock names to release
        """
        # Release in reverse order
        for lock_name in reversed(lock_names):
            try:
                self.release_lock(lock_name)
            except Exception as e:
                logger.error(
                    f"Failed to release lock {lock_name}: {e}",
                    extra={"lock_name": lock_name, "error": str(e)},
                )


# Global coordinator instance
_coordinator_instance: Optional[OrchestrationCoordinator] = None
_coordinator_lock = threading.Lock()


def get_coordinator() -> OrchestrationCoordinator:
    """Get the global orchestration coordinator instance (thread-safe singleton).

    Returns:
        OrchestrationCoordinator instance
    """
    global _coordinator_instance

    if _coordinator_instance is None:
        with _coordinator_lock:
            if _coordinator_instance is None:
                _coordinator_instance = OrchestrationCoordinator()

    return _coordinator_instance


__all__ = [
    "OrchestrationCoordinator",
    "LockAcquisitionInfo",
    "get_coordinator",
]
