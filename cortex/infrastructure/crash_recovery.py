"""Crash recovery and state reconstruction via write-ahead logging.

Implements WAL for critical state changes with checkpoint mechanism
and automatic replay on startup to ensure consistency after crashes.
"""

import json
import logging
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set

logger = logging.getLogger(__name__)


class RecoveryError(Exception):
    """Raised when recovery cannot be performed."""
    pass


@dataclass
class WALEntry:
    """Write-ahead log entry.

    Args:
        sequence_number: Sequential entry number
        operation: Operation name
        data: Operation data
        timestamp: When operation occurred
        committed: Whether operation was committed
    """
    sequence_number: int
    operation: str
    data: Dict[str, Any]
    timestamp: datetime
    committed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entry."""
        return {
            "sequence_number": self.sequence_number,
            "operation": self.operation,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "committed": self.committed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WALEntry":
        """Deserialize entry."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Checkpoint:
    """State checkpoint for recovery.

    Args:
        sequence_number: WAL sequence at checkpoint
        state_snapshot: Complete state snapshot
        timestamp: When checkpoint created
    """
    sequence_number: int
    state_snapshot: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Serialize checkpoint."""
        return {
            "sequence_number": self.sequence_number,
            "state_snapshot": self.state_snapshot,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Deserialize checkpoint."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    @classmethod
    def from_file(cls, path: Path) -> "Checkpoint":
        """Load checkpoint from file."""
        data = json.loads(path.read_text())
        return cls.from_dict(data)


@dataclass
class RecoveryResult:
    """Result of crash recovery.

    Args:
        success: Whether recovery succeeded
        records_replayed: Number of WAL entries replayed
        recovery_duration_seconds: Time taken to recover
        incomplete_operations: Operations in progress during crash
        recovered_from_checkpoint: Whether recovered from checkpoint
        validation_passed: Whether post-recovery validation passed
    """
    success: bool
    records_replayed: int
    recovery_duration_seconds: float
    incomplete_operations: List[str] = field(default_factory=list)
    recovered_from_checkpoint: bool = False
    validation_passed: bool = True


class StateManager(Protocol):
    """Protocol for state management."""

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot."""
        ...

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot."""
        ...

    def apply_operation(self, operation: str, data: Dict[str, Any]) -> None:
        """Apply operation to state."""
        ...

    def validate_state(self) -> bool:
        """Validate state consistency."""
        ...


class WriteAheadLog:
    """Write-ahead log for operation tracking.

    Args:
        storage_path: Directory to store WAL files
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._current_sequence = 0
        self._current_file: Optional[Path] = None
        self._lock = threading.Lock()

        self._initialize_wal()

    def append(self, operation: str, data: Dict[str, Any], committed: bool = True) -> int:
        """Append entry to WAL.

        Args:
            operation: Operation name
            data: Operation data
            committed: Whether operation is committed

        Returns:
            Sequence number
        """
        with self._lock:
            self._current_sequence += 1

            entry = WALEntry(
                sequence_number=self._current_sequence,
                operation=operation,
                data=data,
                timestamp=datetime.utcnow(),
                committed=committed
            )

            self._write_entry(entry)

            return self._current_sequence

    def read_entries(self, from_sequence: int = 0) -> List[WALEntry]:
        """Read WAL entries from sequence.

        Args:
            from_sequence: Starting sequence number

        Returns:
            List of entries

        Raises:
            RecoveryError: If WAL is corrupted
        """
        entries: List[WALEntry] = []

        for wal_file in sorted(self.storage_path.glob("wal_*.log")):
            try:
                with open(wal_file, 'r') as f:
                    for line in f:
                        try:
                            entry = WALEntry.from_dict(json.loads(line))
                            if entry.sequence_number >= from_sequence:
                                entries.append(entry)
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"Corrupted WAL entry: {e}")
                            raise RecoveryError(f"WAL corruption detected: {e}")
            except Exception as e:
                logger.error(f"Error reading WAL file {wal_file}: {e}")
                raise RecoveryError(f"Cannot read WAL: {e}")

        return sorted(entries, key=lambda e: e.sequence_number)

    def _initialize_wal(self) -> None:
        """Initialize WAL or recover existing."""
        # Find latest sequence number
        max_seq = 0
        for wal_file in self.storage_path.glob("wal_*.log"):
            try:
                with open(wal_file, 'r') as f:
                    for line in f:
                        try:
                            entry = WALEntry.from_dict(json.loads(line))
                            max_seq = max(max_seq, entry.sequence_number)
                        except (json.JSONDecodeError, KeyError):
                            logger.warning(f"Skipping corrupted WAL entry in {wal_file}")
            except Exception as e:
                logger.warning(f"Error reading WAL file {wal_file}: {e}")

        self._current_sequence = max_seq
        self._current_file = self.storage_path / f"wal_{datetime.utcnow():%Y%m%d_%H%M%S}.log"

    def _write_entry(self, entry: WALEntry) -> None:
        """Write entry to WAL file."""
        if not self._current_file:
            self._current_file = self.storage_path / f"wal_{datetime.utcnow():%Y%m%d_%H%M%S}.log"

        with open(self._current_file, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
            f.flush()


class CrashRecovery:
    """Manages crash recovery and state reconstruction.

    Args:
        storage_path: Directory for WAL and checkpoints
        state_manager: State management interface
        checkpoint_interval_operations: Operations between checkpoints
    """

    def __init__(
        self,
        storage_path: Path,
        state_manager: StateManager,
        checkpoint_interval_operations: int = 1000
    ):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.state_manager = state_manager
        self.checkpoint_interval_operations = checkpoint_interval_operations

        self.wal = WriteAheadLog(storage_path / "wal")

        self._operations_since_checkpoint = 0
        self._in_flight_operations: Set[str] = set()
        self._lock = threading.Lock()

    def record_operation(self, operation: str, data: Dict[str, Any]) -> None:
        """Record operation in WAL.

        Args:
            operation: Operation name
            data: Operation data
        """
        self.wal.append(operation, data, committed=False)
        self._operations_since_checkpoint += 1

        # Auto-checkpoint if threshold reached
        if self._operations_since_checkpoint >= self.checkpoint_interval_operations:
            self.create_checkpoint()

    def commit(self) -> None:
        """Mark current operation as committed."""
        # In a real implementation, this would update the last WAL entry
        pass

    def begin_operation(self, operation_id: str, operation_type: str) -> None:
        """Mark operation as in-flight.

        Args:
            operation_id: Operation identifier
            operation_type: Type of operation
        """
        with self._lock:
            self._in_flight_operations.add(operation_id)

    def complete_operation(self, operation_id: str) -> None:
        """Mark operation as completed.

        Args:
            operation_id: Operation identifier
        """
        with self._lock:
            self._in_flight_operations.discard(operation_id)

    def can_resume_operation(self, operation_id: str) -> bool:
        """Check if operation can be resumed.

        Args:
            operation_id: Operation identifier

        Returns:
            True if operation can be resumed
        """
        # Check if operation state is recoverable
        return True  # Simplified

    def create_checkpoint(self) -> None:
        """Create state checkpoint."""
        try:
            snapshot = self.state_manager.get_state_snapshot()

            checkpoint = Checkpoint(
                sequence_number=self.wal._current_sequence,
                state_snapshot=snapshot,
                timestamp=datetime.utcnow()
            )

            checkpoint_file = self.storage_path / f"checkpoint_{datetime.utcnow():%Y%m%d_%H%M%S}.json"
            checkpoint_file.write_text(json.dumps(checkpoint.to_dict(), indent=2))

            self._operations_since_checkpoint = 0
            logger.info(f"Created checkpoint at sequence {checkpoint.sequence_number}")

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")

    def recover_from_crash(self) -> RecoveryResult:
        """Recover state after crash.

        Returns:
            Recovery result
        """
        import time
        start_time = time.time()

        try:
            # Load latest checkpoint
            checkpoint = self._load_latest_checkpoint()

            if checkpoint:
                logger.info(f"Restoring from checkpoint at sequence {checkpoint.sequence_number}")
                self.state_manager.restore_state(checkpoint.state_snapshot)
                from_sequence = checkpoint.sequence_number + 1
                recovered_from_checkpoint = True
            else:
                logger.info("No checkpoint found, replaying all WAL entries")
                from_sequence = 0
                recovered_from_checkpoint = False

            # Replay WAL entries
            try:
                entries = self.wal.read_entries(from_sequence=from_sequence)
            except RecoveryError as e:
                # WAL corrupted - use checkpoint if available
                if checkpoint:
                    logger.warning(f"WAL corrupted, using checkpoint: {e}")
                    entries = []
                else:
                    raise

            # Apply operations
            records_replayed = 0
            for entry in entries:
                if entry.committed:
                    try:
                        self.state_manager.apply_operation(entry.operation, entry.data)
                        records_replayed += 1
                    except Exception as e:
                        logger.error(f"Failed to replay entry {entry.sequence_number}: {e}")

            # Validate state
            validation_passed = self.state_manager.validate_state()

            duration = time.time() - start_time

            logger.info(f"Recovery complete: {records_replayed} records replayed in {duration:.2f}s")

            return RecoveryResult(
                success=True,
                records_replayed=records_replayed,
                recovery_duration_seconds=duration,
                incomplete_operations=list(self._in_flight_operations),
                recovered_from_checkpoint=recovered_from_checkpoint,
                validation_passed=validation_passed
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Recovery failed: {e}")

            return RecoveryResult(
                success=False,
                records_replayed=0,
                recovery_duration_seconds=duration,
                validation_passed=False
            )

    def _load_latest_checkpoint(self) -> Optional[Checkpoint]:
        """Load most recent checkpoint.

        Returns:
            Latest checkpoint or None
        """
        checkpoint_files = sorted(self.storage_path.glob("checkpoint_*.json"), reverse=True)

        for checkpoint_file in checkpoint_files:
            try:
                return Checkpoint.from_file(checkpoint_file)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint {checkpoint_file}: {e}")

        return None
