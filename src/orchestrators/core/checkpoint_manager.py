"""
Checkpoint Manager - Design Specification (v1.0)

Purpose:
- Define the checkpoint format and storage strategy for the TODO Orchestrator.
- Provide a minimal design scaffold to be implemented in Phase 3 tasks.

Format (per tracker spec):
- version: "1.0"
- timestamp: ISO8601 string
- dag_snapshot: Serialized DAG
- state_snapshot: Complete state snapshot at checkpoint
- metadata:
  - correlation_id
  - executor
  - tasks_completed
  - tasks_remaining

Storage:
- Location: cortex-brain/state/checkpoints/
- Naming: checkpoint_{timestamp}_{correlation_id}.json
- Retention: 7 days (enforced by cleanup routine in later tasks)

Notes:
- Atomic write will be implemented in task-3.3
- Recovery & rollback will be implemented in tasks-3.4/3.5
- Auto-checkpoint will be implemented in task-3.6
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import json
import os


CHECKPOINTS_DIR = Path("cortex-brain/state/checkpoints")


@dataclass
class CheckpointMetadata:
    correlation_id: str
    executor: str
    tasks_completed: int
    tasks_remaining: int
    created_at: str  # ISO8601


@dataclass
class CheckpointRecord:
    version: str
    timestamp: str  # ISO8601
    dag_snapshot: Dict[str, Any]
    state_snapshot: Dict[str, Any]
    metadata: CheckpointMetadata


class CheckpointManager:
    """
    Design scaffold for Checkpoint Manager.

    Responsibilities (to be implemented across Phase 3 tasks):
    - Create checkpoints atomically
    - List and retrieve checkpoints
    - Validate and recover from checkpoints
    - Rollback and cascade rollback of tasks
    - Auto-checkpoint configuration and cleanup
    """

    def __init__(self, base_dir: Path = CHECKPOINTS_DIR):
        self.base_dir = base_dir
        # Ensure storage directory exists (design-time safeguard)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-checkpoint configuration
        self._auto_checkpoint_interval = 0  # 0 = disabled
        self._max_checkpoints = 10
        self._retention_days = 7
        self._tasks_since_checkpoint = 0

    @staticmethod
    def design_spec() -> Dict[str, Any]:
        """Return the formal design specification dictionary."""
        return {
            "version": "1.0",
            "timestamp": "ISO8601",
            "dag_snapshot": "Serialized DAG",
            "state_snapshot": "All state at checkpoint",
            "metadata": [
                "correlation_id",
                "executor",
                "tasks_completed",
                "tasks_remaining",
            ],
            "storage": {
                "location": str(CHECKPOINTS_DIR),
                "naming": "checkpoint_{timestamp}_{correlation_id}.json",
                "retention": "7 days",
            },
        }

    def _build_filename(self, timestamp: str, correlation_id: str) -> Path:
        name = f"checkpoint_{timestamp}_{correlation_id}.json"
        return self.base_dir / name

    # ---- Placeholders for future implementation (Phase 3 tasks) ----
    def create_checkpoint(self, correlation_id: str) -> str:
        """Create a checkpoint record and persist it atomically.

        Returns the checkpoint file name relative to the base_dir.
        """
        # Build timestamp in ISO8601 with Z
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        target_path = self._build_filename(timestamp=timestamp, correlation_id=correlation_id)

        record = self._serialize_state(timestamp=timestamp, correlation_id=correlation_id)
        self._write_checkpoint_atomic(target_path, record)
        return target_path.name

    def _serialize_state(self, timestamp: str, correlation_id: str) -> Dict[str, Any]:
        """Minimal serialization per design spec; expand in future tasks."""
        metadata = CheckpointMetadata(
            correlation_id=correlation_id,
            executor="GitHub Copilot",
            tasks_completed=0,
            tasks_remaining=0,
            created_at=timestamp,
        )
        record = CheckpointRecord(
            version="1.0",
            timestamp=timestamp,
            dag_snapshot={},
            state_snapshot={},
            metadata=metadata,
        )
        # Convert dataclasses to plain dict for JSON dump
        out = asdict(record)
        out["metadata"] = asdict(metadata)
        return out

    def _write_checkpoint_atomic(self, final_path: Path, data: Dict[str, Any]) -> None:
        """Write JSON to a temp file, fsync, then atomically replace final path."""
        tmp_path = final_path.with_suffix(final_path.suffix + ".tmp")
        # Ensure directory exists
        final_path.parent.mkdir(parents=True, exist_ok=True)

        # Write temp file
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Atomic replace
        os.replace(tmp_path, final_path)

    def recover_from_checkpoint(self, checkpoint_id: str) -> bool:
        """Recover from a checkpoint file.
        
        Returns True if recovery succeeds, False otherwise.
        """
        checkpoint_path = self.base_dir / checkpoint_id
        
        if not checkpoint_path.exists():
            return False
        
        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            
            # Validate checkpoint structure
            if not self._validate_checkpoint(data):
                return False
            
            # Deserialize state (minimal for now - expand in future tasks)
            state = self._deserialize_state(data)
            
            # Recovery successful
            return True
        except (json.JSONDecodeError, KeyError, ValueError):
            return False

    def _validate_checkpoint(self, data: Dict[str, Any]) -> bool:
        """Validate checkpoint has required fields per design spec."""
        required_keys = ["version", "timestamp", "dag_snapshot", "state_snapshot", "metadata"]
        if not all(key in data for key in required_keys):
            return False
        
        # Validate metadata structure
        meta = data.get("metadata", {})
        required_meta = ["correlation_id", "executor", "tasks_completed", "tasks_remaining"]
        if not all(key in meta for key in required_meta):
            return False
        
        return True

    def _deserialize_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize checkpoint data into state structure.
        
        Minimal implementation for now - expand when integrating with TodoOrchestrator.
        """
        return {
            "version": data["version"],
            "timestamp": data["timestamp"],
            "dag_snapshot": data["dag_snapshot"],
            "state_snapshot": data["state_snapshot"],
            "metadata": data["metadata"],
        }

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints with metadata."""
        checkpoints = []
        
        if not self.base_dir.exists():
            return checkpoints
        
        for cp_file in self.base_dir.glob("checkpoint_*.json"):
            try:
                data = json.loads(cp_file.read_text(encoding="utf-8"))
                checkpoints.append({
                    "id": cp_file.name,
                    "timestamp": data.get("timestamp"),
                    "correlation_id": data.get("metadata", {}).get("correlation_id"),
                    "executor": data.get("metadata", {}).get("executor"),
                })
            except (json.JSONDecodeError, KeyError):
                # Skip corrupted checkpoints
                continue
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return checkpoints

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the most recent checkpoint ID."""
        checkpoints = self.list_checkpoints()
        if checkpoints:
            return checkpoints[0]["id"]
        return None

    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback state to a specific checkpoint.
        
        This includes:
        - Restoring DAG and state from checkpoint
        - Rolling back tasks and their dependents (cascade)
        
        Returns True if rollback succeeds, False otherwise.
        """
        checkpoint_path = self.base_dir / checkpoint_id
        
        if not checkpoint_path.exists():
            return False
        
        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            
            # Validate checkpoint
            if not self._validate_checkpoint(data):
                return False
            
            # Restore state from checkpoint
            state = self._deserialize_state(data)
            
            # TODO: When integrated with TodoOrchestrator:
            # 1. Load DAG snapshot
            # 2. Identify tasks to rollback
            # 3. Call _rollback_task() for each
            # 4. Call _cascade_rollback() for dependents
            
            # For now, minimal implementation passes validation
            return True
        except (json.JSONDecodeError, KeyError, ValueError):
            return False

    def _rollback_task(self, task_id: str) -> bool:
        """Rollback a single task.
        
        Placeholder: Will integrate with TodoOrchestrator to reset task status.
        """
        # TODO: Integration with TodoOrchestrator
        # Reset task status to previous state
        # Clear completion timestamps
        # Remove task outputs if any
        return True

    def _rollback_dependents(self, task_id: str) -> List[str]:
        """Get list of tasks that depend on the given task.
        
        Placeholder: Will integrate with DAG to find dependents.
        """
        # TODO: Integration with DAG
        # Query DAG for tasks with edges pointing from task_id
        return []

    def _cascade_rollback(self, task_ids: List[str]) -> bool:
        """Rollback multiple tasks in cascade.
        
        Placeholder: Will integrate with TodoOrchestrator.
        """
        # TODO: Integration with TodoOrchestrator
        # For each task in task_ids:
        #   1. Get dependents
        #   2. Rollback task
        #   3. Recursively rollback dependents
        return True

    def configure_auto_checkpoint(self, interval: int = 5) -> None:
        """Configure automatic checkpoint creation.
        
        Args:
            interval: Number of tasks between automatic checkpoints. 0 to disable.
        """
        self._auto_checkpoint_interval = interval

    def _should_checkpoint(self) -> bool:
        """Check if it's time to create an automatic checkpoint.
        
        Returns True if checkpoint should be created based on interval.
        """
        if self._auto_checkpoint_interval <= 0:
            return False
        
        return self._tasks_since_checkpoint >= self._auto_checkpoint_interval

    def _cleanup_old_checkpoints(self) -> None:
        """Remove old checkpoints beyond retention limits.
        
        Keeps up to _max_checkpoints based on timestamp.
        """
        checkpoints = self.list_checkpoints()
        
        # If under limit, nothing to clean
        if len(checkpoints) <= self._max_checkpoints:
            return
        
        # Remove oldest checkpoints beyond the limit
        to_remove = checkpoints[self._max_checkpoints:]
        for cp in to_remove:
            cp_path = self.base_dir / cp["id"]
            if cp_path.exists():
                cp_path.unlink()


if __name__ == "__main__":
    # Simple design-spec introspection for smoke check
    mgr = CheckpointManager()
    spec = mgr.design_spec()
    print(json.dumps(spec, indent=2))
