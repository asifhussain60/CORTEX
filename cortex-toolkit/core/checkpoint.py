"""
Checkpoint data model for RecoveryManager.

Phase 3 of Toolkit Manager Implementation
Provides checkpoint state snapshots for rollback capability.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


class CheckpointState(Enum):
    """State of a checkpoint in its lifecycle."""
    PENDING = "pending"       # Created but not yet finalized
    ACTIVE = "active"         # Available for rollback
    ROLLED_BACK = "rolled_back"  # Has been used for rollback
    EXPIRED = "expired"       # Pruned or marked for deletion


@dataclass
class Checkpoint:
    """
    Immutable snapshot of system state before a destructive operation.
    
    Attributes:
        id: Unique identifier (UUID)
        timestamp: When checkpoint was created
        tool: Name of tool being executed
        args: Arguments passed to tool
        affected_paths: Files that may be modified
        git_sha: Git commit SHA at checkpoint time (if in repo)
        state_snapshot: Map of file paths to their contents
        state: Current lifecycle state of checkpoint
    """
    id: str
    timestamp: datetime
    tool: str
    args: List[str]
    affected_paths: List[Path]
    git_sha: Optional[str]
    state_snapshot: Dict[str, str]
    state: CheckpointState = CheckpointState.ACTIVE
    
    def to_json(self) -> str:
        """Serialize checkpoint to JSON string."""
        data = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "tool": self.tool,
            "args": self.args,
            "affected_paths": [str(p) for p in self.affected_paths],
            "git_sha": self.git_sha,
            "state_snapshot": self.state_snapshot,
            "state": self.state.value,
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> 'Checkpoint':
        """Deserialize checkpoint from JSON string."""
        parsed = json.loads(data)
        return cls(
            id=parsed["id"],
            timestamp=datetime.fromisoformat(parsed["timestamp"]),
            tool=parsed["tool"],
            args=parsed["args"],
            affected_paths=[Path(p) for p in parsed["affected_paths"]],
            git_sha=parsed.get("git_sha"),
            state_snapshot=parsed["state_snapshot"],
            state=CheckpointState(parsed.get("state", "active")),
        )
    
    def __hash__(self) -> int:
        """Make checkpoint hashable by ID."""
        return hash(self.id)
    
    def __eq__(self, other: Any) -> bool:
        """Checkpoints are equal if IDs match."""
        if not isinstance(other, Checkpoint):
            return False
        return self.id == other.id
