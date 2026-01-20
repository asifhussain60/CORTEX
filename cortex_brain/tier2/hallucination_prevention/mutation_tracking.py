"""Mutation Tracking - Tracks state mutations for hallucination detection.

Monitors and records state changes to identify inconsistencies and hallucinations.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Mutation:
    """A state mutation event.

    Attributes:
        operation_id: ID of operation causing mutation.
        path: Path to mutated value (dot notation).
        old_value: Previous value.
        new_value: New value.
        timestamp: When mutation occurred.
    """

    operation_id: str
    path: str
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)


class MutationTracker:
    """Tracks state mutations."""

    def __init__(self) -> None:
        """Initialize mutation tracker."""
        self.mutations: List[Mutation] = []
        self.state_snapshots: Dict[str, Dict[str, Any]] = {}

    def record_mutation(
        self,
        operation_id: str,
        path: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Record a state mutation.

        Args:
            operation_id: ID of operation.
            path: Path to mutated value.
            old_value: Previous value.
            new_value: New value.
        """
        mutation = Mutation(
            operation_id=operation_id,
            path=path,
            old_value=old_value,
            new_value=new_value,
        )
        self.mutations.append(mutation)

    def get_mutations(self, operation_id: Optional[str] = None) -> List[Mutation]:
        """Get mutations for an operation.

        Args:
            operation_id: Optional filter by operation ID.

        Returns:
            List of mutations.
        """
        if operation_id:
            return [m for m in self.mutations if m.operation_id == operation_id]
        return self.mutations.copy()

    def snapshot_state(self, operation_id: str, state: Dict[str, Any]) -> None:
        """Take snapshot of state.

        Args:
            operation_id: Operation ID.
            state: State dictionary.
        """
        self.state_snapshots[operation_id] = state.copy()

    def get_snapshot(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get state snapshot.

        Args:
            operation_id: Operation ID.

        Returns:
            Snapshot or None if not found.
        """
        return self.state_snapshots.get(operation_id)

    def detect_inconsistencies(self, operation_id: str) -> List[str]:
        """Detect state inconsistencies for an operation.

        Args:
            operation_id: Operation ID.

        Returns:
            List of inconsistency descriptions.
        """
        inconsistencies = []
        mutations = self.get_mutations(operation_id)

        # Check for contradictory mutations
        for i, m1 in enumerate(mutations):
            for m2 in mutations[i + 1 :]:
                if m1.path == m2.path and m1.new_value != m2.old_value:
                    inconsistencies.append(
                        f"Inconsistent mutation on {m1.path}: "
                        f"{m1.new_value} != {m2.old_value}"
                    )

        return inconsistencies

    def clear_mutations(self) -> None:
        """Clear all mutations."""
        self.mutations.clear()
        self.state_snapshots.clear()




class VisionMutationTracker(MutationTracker):
    """Track mutations in vision/goals."""
    
    def track_vision_change(self, old_vision: str, new_vision: str) -> Mutation:
        """Track vision mutation."""
        mutation = Mutation(
            mutation_id=f"vision_{len(self.mutations)}",
            mutation_type="vision_change",
            old_value=old_vision,
            new_value=new_vision
        )
        self.track_mutation(mutation)
        return mutation

__all__ = ["MutationTracker", "Mutation", "VisionMutationTracker"]
