"""Mutation Tracking - Tracks state mutations for hallucination detection.

Monitors and records state changes to identify inconsistencies and hallucinations.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum


class MutationType(Enum):
    """Types of mutations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    CONTEXT_UPDATE = "context_update"
    STATE_UPDATE = "state_update"
    VISION_CHANGE = "vision_change"
    BOUNDARY_MODIFICATION = "boundary_modification"
    SCHEMA_EVOLUTION = "schema_evolution"
    ROLLBACK = "rollback"


@dataclass
class Mutation:
    """A state mutation event.

    Attributes:
        mutation_id: Unique mutation identifier.
        mutation_type: Type of mutation.
        old_value: Previous value.
        new_value: New value.
        timestamp: When mutation occurred.
        operation_id: ID of operation causing mutation.
        path: Path to mutated value (dot notation).
        source: Source of mutation.
        description: Description of mutation.
        affected_entity: Entity affected by mutation.
        data: Additional data.
        context: Optional context metadata.
        parent_mutation_id: ID of parent mutation (for causality tracking).
    """

    mutation_id: str = ""
    mutation_type: Union[str, MutationType] = ""
    old_value: Any = None
    new_value: Any = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    operation_id: str = ""
    path: str = ""
    source: str = ""
    description: str = ""
    affected_entity: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    parent_mutation_id: Optional[str] = None


@dataclass
class MutationSnapshotRecord:
    """Record of a mutation snapshot.
    
    Attributes:
        snapshot_id: Unique snapshot identifier.
        mutation_id: ID of mutation this is a snapshot of.
        timestamp: When snapshot was created.
        mutation_count: Number of mutations at snapshot time.
    """
    snapshot_id: str
    mutation_id: str
    timestamp: str
    mutation_count: int = 0


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
    """Track mutations in vision/goals with persistence."""
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize vision mutation tracker.
        
        Args:
            db_path: Optional path to database for persistence.
        """
        super().__init__()
        self.db_path = db_path
        self._mutation_counter = 0
        self._snapshots: Dict[str, "MutationSnapshotRecord"] = {}
    
    def track_mutation(
        self,
        mutation_type: Union[str, MutationType] = None,
        source: str = "",
        description: str = "",
        affected_entity: str = "",
        data: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Mutation:
        """Track a mutation with full metadata.
        
        Args:
            mutation_type: Type of mutation.
            source: Source of mutation.
            description: Description of change.
            affected_entity: Entity affected.
            data: Additional data.
            context: Context metadata.
            parent_mutation_id: ID of parent mutation.
            **kwargs: Additional mutation fields.
            
        Returns:
            Mutation record.
        """
        self._mutation_counter += 1
        parent_id = kwargs.get('parent_mutation_id')
        mutation = Mutation(
            mutation_id=f"mutation_{self._mutation_counter}",
            mutation_type=mutation_type if mutation_type else MutationType.UPDATE,
            timestamp=datetime.utcnow(),
            source=source,
            description=description,
            affected_entity=affected_entity,
            data=data or {},
            context=context or {},
            parent_mutation_id=parent_id,
        )
        self.mutations.append(mutation)
        return mutation
    
    def get_mutation(self, mutation_id: str) -> Optional[Mutation]:
        """Get a mutation by ID.
        
        Args:
            mutation_id: ID of mutation to retrieve.
            
        Returns:
            Mutation if found, None otherwise.
        """
        for mutation in self.mutations:
            if mutation.mutation_id == mutation_id:
                return mutation
        return None
    
    def track_vision_change(self, old_vision: str, new_vision: str) -> Mutation:
        """Track vision mutation.
        
        Args:
            old_vision: Previous vision.
            new_vision: New vision.
            
        Returns:
            Mutation record.
        """
        return self.track_mutation(
            mutation_type=MutationType.VISION_CHANGE,
            source="vision",
            description="Vision change",
            data={"old_value": old_vision, "new_value": new_vision},
        )
    
    def get_mutations_by_type(self, mutation_type: MutationType) -> List[Mutation]:
        """Get mutations filtered by type.
        
        Args:
            mutation_type: Type to filter by.
            
        Returns:
            List of matching mutations.
        """
        return [m for m in self.mutations if m.mutation_type == mutation_type]
    
    def get_mutation_history(self, as_dict: bool = True) -> List[Union[Mutation, Dict[str, Any]]]:
        """Get full mutation history.
        
        Args:
            as_dict: If True, return mutations as dictionaries.
        
        Returns:
            List of all mutations in chronological order.
        """
        if as_dict:
            return [self._mutation_to_dict(m) for m in self.mutations]
        return self.mutations.copy()
    
    def _mutation_to_dict(self, mutation: Mutation) -> Dict[str, Any]:
        """Convert Mutation to dictionary.
        
        Args:
            mutation: Mutation to convert.
            
        Returns:
            Dictionary representation.
        """
        return {
            "mutation_id": mutation.mutation_id,
            "mutation_type": mutation.mutation_type.value if isinstance(mutation.mutation_type, MutationType) else str(mutation.mutation_type),
            "timestamp": mutation.timestamp.isoformat() if isinstance(mutation.timestamp, datetime) else str(mutation.timestamp),
            "source": mutation.source,
            "description": mutation.description,
            "affected_entity": mutation.affected_entity,
            "data": mutation.data,
            "context": mutation.context,
        }
    
    def get_mutations_for_entity(self, entity: str) -> List[Dict[str, Any]]:
        """Get mutations for a specific entity.
        
        Args:
            entity: Entity to filter by.
            
        Returns:
            List of mutations affecting the entity.
        """
        return [
            self._mutation_to_dict(m)
            for m in self.mutations
            if m.affected_entity == entity
        ]
    
    def get_mutations_in_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get mutations within a time range.
        
        Args:
            start_time: Start of time range.
            end_time: End of time range.
            
        Returns:
            List of mutations in the time range.
        """
        # Remove timezone info for comparison (handle utcnow vs now mismatch)
        def to_naive(dt: datetime) -> datetime:
            if dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        
        start_naive = to_naive(start_time)
        end_naive = to_naive(end_time)
        
        return [
            self._mutation_to_dict(m)
            for m in self.mutations
            if start_naive <= to_naive(m.timestamp) <= end_naive
        ]
    
    # Alias for backward compatibility
    def get_mutations_in_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Alias for get_mutations_in_time_range."""
        return self.get_mutations_in_time_range(start_time, end_time)
    
    def search_mutations(self, query: str) -> List[Dict[str, Any]]:
        """Search mutations by description or entity.
        
        Args:
            query: Search query string.
            
        Returns:
            List of matching mutations.
        """
        query_lower = query.lower()
        return [
            self._mutation_to_dict(m)
            for m in self.mutations
            if query_lower in m.description.lower()
            or query_lower in m.affected_entity.lower()
            or query_lower in m.source.lower()
        ]
    
    def rollback_to_mutation(self, mutation_id: str) -> Optional[Mutation]:
        """Rollback to a specific mutation state.
        
        Args:
            mutation_id: ID of mutation to rollback to.
            
        Returns:
            Rollback mutation if successful, None otherwise.
        """
        # Find mutation index
        target_idx = None
        for idx, mutation in enumerate(self.mutations):
            if mutation.mutation_id == mutation_id:
                target_idx = idx
                break
        
        if target_idx is None:
            return None
        
        # Track the rollback as a new mutation
        rollback_mutation = self.track_mutation(
            mutation_type=MutationType.ROLLBACK,
            source="rollback",
            description=f"Rollback to {mutation_id}",
            data={"rollback_to": mutation_id, "rolled_back_count": len(self.mutations) - target_idx - 2},
        )
        
        return rollback_mutation
    
    def create_mutation_snapshot(self, mutation_id: str) -> "MutationSnapshotRecord":
        """Create a snapshot of mutation state.
        
        Args:
            mutation_id: ID of mutation to snapshot.
            
        Returns:
            Snapshot record.
        """
        import uuid
        
        snapshot = MutationSnapshotRecord(
            snapshot_id=str(uuid.uuid4()),
            mutation_id=mutation_id,
            timestamp=datetime.now().isoformat(),
            mutation_count=len(self.mutations),
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot


class VisionMutation(Enum):
    """Vision mutation types."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    REPLACED = "replaced"


@dataclass
class MutationSnapshot:
    """Snapshot of a mutation state."""
    timestamp: str
    mutation_type: MutationType
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = ["MutationTracker", "Mutation", "VisionMutationTracker", "VisionMutation", "MutationType", "MutationSnapshot", "MutationSnapshotRecord"]
