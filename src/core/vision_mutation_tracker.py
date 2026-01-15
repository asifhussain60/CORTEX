"""
Vision Mutation Tracker - AC-AR-015-01

Tracks all vision changes with complete audit trails including:
- Change timestamps and authors
- Motivation for changes
- Impact analysis
- Previous versions for rollback capability
- Change status and approval tracking

This module enables vision evolution while maintaining consistency and
auditability of all changes to the CORTEX vision statement.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Set
import json
import hashlib
from pathlib import Path


class MutationType(Enum):
    """Types of vision mutations that can occur."""
    STATEMENT_UPDATE = "statement_update"
    PRINCIPLE_ADD = "principle_add"
    PRINCIPLE_MODIFY = "principle_modify"
    PRINCIPLE_REMOVE = "principle_remove"
    GOAL_ADD = "goal_add"
    GOAL_MODIFY = "goal_modify"
    GOAL_REMOVE = "goal_remove"
    SCOPE_CHANGE = "scope_change"
    PRIORITY_ADJUSTMENT = "priority_adjustment"


class MutationStatus(Enum):
    """Status of a vision mutation."""
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"


class ImpactArea(Enum):
    """Areas affected by vision mutations."""
    TIER0_GOVERNANCE = "tier0_governance"
    TIER1_ACCEPTANCE = "tier1_acceptance"
    TIER2_RESPONSE = "tier2_response"
    TIER3_ORCHESTRATION = "tier3_orchestration"
    ORCHESTRATOR_BEHAVIOR = "orchestrator_behavior"
    AUDIT_REQUIREMENTS = "audit_requirements"


class ImpactSeverity(Enum):
    """Severity of impact from vision mutations."""
    CRITICAL = "critical"  # Changes core behavior
    HIGH = "high"  # Affects multiple systems
    MEDIUM = "medium"  # Affects specific components
    LOW = "low"  # Minor changes


@dataclass
class VisionImpact:
    """Impact analysis for a vision mutation."""
    affected_areas: Set[ImpactArea]
    severity: ImpactSeverity
    estimated_affected_systems: int
    required_orchestrator_updates: bool
    requires_phase_adjustment: bool
    description: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "affected_areas": [area.value for area in self.affected_areas],
            "severity": self.severity.value,
            "estimated_affected_systems": self.estimated_affected_systems,
            "required_orchestrator_updates": self.required_orchestrator_updates,
            "requires_phase_adjustment": self.requires_phase_adjustment,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict) -> "VisionImpact":
        """Create from dictionary."""
        return VisionImpact(
            affected_areas={ImpactArea(area) for area in data["affected_areas"]},
            severity=ImpactSeverity(data["severity"]),
            estimated_affected_systems=data["estimated_affected_systems"],
            required_orchestrator_updates=data["required_orchestrator_updates"],
            requires_phase_adjustment=data["requires_phase_adjustment"],
            description=data["description"],
        )


@dataclass
class VisionMutation:
    """Represents a single vision mutation."""
    mutation_id: str
    mutation_type: MutationType
    timestamp: datetime
    author: str
    motivation: str
    previous_value: str
    new_value: str
    impact_analysis: VisionImpact
    status: MutationStatus = MutationStatus.PROPOSED
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    applied_timestamp: Optional[datetime] = None
    hash_verification: Optional[str] = None
    depends_on_mutations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "mutation_id": self.mutation_id,
            "mutation_type": self.mutation_type.value,
            "timestamp": self.timestamp.isoformat(),
            "author": self.author,
            "motivation": self.motivation,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "impact_analysis": self.impact_analysis.to_dict(),
            "status": self.status.value,
            "reviewed_by": self.reviewed_by,
            "review_notes": self.review_notes,
            "applied_timestamp": self.applied_timestamp.isoformat() if self.applied_timestamp else None,
            "hash_verification": self.hash_verification,
            "depends_on_mutations": self.depends_on_mutations,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(data: Dict) -> "VisionMutation":
        """Create from dictionary."""
        return VisionMutation(
            mutation_id=data["mutation_id"],
            mutation_type=MutationType(data["mutation_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            author=data["author"],
            motivation=data["motivation"],
            previous_value=data["previous_value"],
            new_value=data["new_value"],
            impact_analysis=VisionImpact.from_dict(data["impact_analysis"]),
            status=MutationStatus(data["status"]),
            reviewed_by=data.get("reviewed_by"),
            review_notes=data.get("review_notes"),
            applied_timestamp=datetime.fromisoformat(data["applied_timestamp"]) if data.get("applied_timestamp") else None,
            hash_verification=data.get("hash_verification"),
            depends_on_mutations=data.get("depends_on_mutations", []),
            tags=data.get("tags", []),
        )


@dataclass
class VisionSnapshot:
    """Snapshot of vision at a specific point in time."""
    snapshot_id: str
    timestamp: datetime
    mutation_id: str  # Mutation that created this snapshot
    vision_content: Dict  # Full vision state
    hash_value: str  # SHA256 of vision content
    description: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "mutation_id": self.mutation_id,
            "vision_content": self.vision_content,
            "hash_value": self.hash_value,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict) -> "VisionSnapshot":
        """Create from dictionary."""
        return VisionSnapshot(
            snapshot_id=data["snapshot_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            mutation_id=data["mutation_id"],
            vision_content=data["vision_content"],
            hash_value=data["hash_value"],
            description=data["description"],
        )


class VisionMutationValidator:
    """Validates vision mutations for consistency and safety."""

    def validate_mutation(self, mutation: VisionMutation) -> Tuple[bool, str]:
        """
        Validate a vision mutation for consistency.
        
        Args:
            mutation: VisionMutation to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check mutation has motivation
        if not mutation.motivation or len(mutation.motivation.strip()) < 10:
            return False, "Mutation motivation must be at least 10 characters"

        # Check values are different
        if mutation.previous_value == mutation.new_value:
            return False, "Mutation must change vision state"

        # Check mutation type matches values
        if not self._type_matches_values(mutation):
            return False, f"Mutation type {mutation.mutation_type.value} doesn't match value changes"

        # Check impact analysis is present
        if not mutation.impact_analysis:
            return False, "Impact analysis is required"

        # Check dependencies exist
        if mutation.depends_on_mutations:
            if not self._all_dependencies_present(mutation):
                return False, "Not all dependency mutations found"

        return True, ""

    def _type_matches_values(self, mutation: VisionMutation) -> bool:
        """Check if mutation type matches the value changes."""
        type_patterns = {
            MutationType.STATEMENT_UPDATE: lambda m: len(m.new_value) > len(m.previous_value) or "statement" in str(m),
            MutationType.PRINCIPLE_ADD: lambda m: m.previous_value == "",
            MutationType.PRINCIPLE_MODIFY: lambda m: m.previous_value != "" and m.new_value != "",
            MutationType.PRINCIPLE_REMOVE: lambda m: m.new_value == "",
            MutationType.GOAL_ADD: lambda m: m.previous_value == "",
            MutationType.GOAL_MODIFY: lambda m: m.previous_value != "" and m.new_value != "",
            MutationType.GOAL_REMOVE: lambda m: m.new_value == "",
        }
        
        check_fn = type_patterns.get(mutation.mutation_type)
        return check_fn(mutation) if check_fn else True

    def _all_dependencies_present(self, mutation: VisionMutation) -> bool:
        """Placeholder for dependency existence check."""
        # Will be implemented when dependency registry is available
        return True


class VisionMutationTracker:
    """
    Central tracker for all vision mutations.
    
    Manages:
    - Recording new mutations with complete metadata
    - Storing mutation history with timestamps
    - Creating snapshots after each mutation
    - Tracking impact analysis
    - Managing mutation status transitions
    - Supporting rollback via snapshots
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize vision mutation tracker.
        
        Args:
            storage_path: Path to JSON file for persistence (optional)
        """
        self.storage_path = storage_path or Path("vision_mutations.json")
        self.mutations: Dict[str, VisionMutation] = {}
        self.snapshots: Dict[str, VisionSnapshot] = {}
        self.mutation_counter = 0
        self.validator = VisionMutationValidator()
        self._load_from_storage()

    def record_mutation(
        self,
        mutation_type: MutationType,
        author: str,
        motivation: str,
        previous_value: str,
        new_value: str,
        impact_analysis: VisionImpact,
        tags: Optional[List[str]] = None,
        depends_on: Optional[List[str]] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Record a new vision mutation.
        
        Args:
            mutation_type: Type of mutation
            author: Author of the mutation
            motivation: Motivation for the change
            previous_value: Previous vision value
            new_value: New vision value
            impact_analysis: Impact analysis
            tags: Optional tags for organization
            depends_on: Optional list of mutation IDs this depends on
            
        Returns:
            Tuple of (success, message, mutation_id)
        """
        # Generate mutation ID
        self.mutation_counter += 1
        mutation_id = f"VMUT-{self.mutation_counter:05d}"

        # Create mutation
        mutation = VisionMutation(
            mutation_id=mutation_id,
            mutation_type=mutation_type,
            timestamp=datetime.now(),
            author=author,
            motivation=motivation,
            previous_value=previous_value,
            new_value=new_value,
            impact_analysis=impact_analysis,
            depends_on_mutations=depends_on or [],
            tags=tags or [],
        )

        # Validate mutation
        is_valid, error_msg = self.validator.validate_mutation(mutation)
        if not is_valid:
            return False, f"Validation failed: {error_msg}", None

        # Calculate hash
        mutation.hash_verification = self._calculate_hash(mutation)

        # Store mutation
        self.mutations[mutation_id] = mutation
        self._save_to_storage()

        return True, f"Mutation {mutation_id} recorded", mutation_id

    def create_snapshot(
        self,
        mutation_id: str,
        vision_content: Dict,
        description: str,
    ) -> Tuple[bool, str]:
        """
        Create a snapshot of vision after a mutation.
        
        Args:
            mutation_id: ID of the mutation that triggered snapshot
            vision_content: Full vision state
            description: Description of snapshot
            
        Returns:
            Tuple of (success, snapshot_id)
        """
        if mutation_id not in self.mutations:
            return False, "Mutation not found"

        snapshot_id = f"SNAP-{len(self.snapshots) + 1:05d}"
        hash_value = self._calculate_vision_hash(vision_content)

        snapshot = VisionSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            mutation_id=mutation_id,
            vision_content=vision_content,
            hash_value=hash_value,
            description=description,
        )

        self.snapshots[snapshot_id] = snapshot
        self._save_to_storage()
        return True, snapshot_id

    def get_mutation_history(
        self,
        limit: Optional[int] = None,
        mutation_type: Optional[MutationType] = None,
        author: Optional[str] = None,
        status: Optional[MutationStatus] = None,
    ) -> List[VisionMutation]:
        """
        Get mutation history with optional filtering.
        
        Args:
            limit: Maximum number of mutations to return
            mutation_type: Filter by mutation type
            author: Filter by author
            status: Filter by status
            
        Returns:
            List of matching mutations (most recent first)
        """
        results = list(self.mutations.values())

        # Apply filters
        if mutation_type:
            results = [m for m in results if m.mutation_type == mutation_type]
        if author:
            results = [m for m in results if m.author == author]
        if status:
            results = [m for m in results if m.status == status]

        # Sort by timestamp (most recent first)
        results.sort(key=lambda m: m.timestamp, reverse=True)

        # Apply limit
        if limit:
            results = results[:limit]

        return results

    def review_mutation(
        self,
        mutation_id: str,
        approved: bool,
        reviewer: str,
        notes: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Review and approve/reject a mutation.
        
        Args:
            mutation_id: ID of mutation to review
            approved: Whether mutation is approved
            reviewer: Name of reviewer
            notes: Optional review notes
            
        Returns:
            Tuple of (success, message)
        """
        if mutation_id not in self.mutations:
            return False, "Mutation not found"

        mutation = self.mutations[mutation_id]

        if mutation.status != MutationStatus.PROPOSED:
            return False, f"Cannot review mutation in {mutation.status.value} status"

        mutation.status = MutationStatus.APPROVED if approved else MutationStatus.REJECTED
        mutation.reviewed_by = reviewer
        mutation.review_notes = notes
        self._save_to_storage()

        return True, f"Mutation {mutation_id} {'approved' if approved else 'rejected'}"

    def apply_mutation(self, mutation_id: str) -> Tuple[bool, str]:
        """
        Apply an approved mutation to the vision.
        
        Args:
            mutation_id: ID of mutation to apply
            
        Returns:
            Tuple of (success, message)
        """
        if mutation_id not in self.mutations:
            return False, "Mutation not found"

        mutation = self.mutations[mutation_id]

        if mutation.status != MutationStatus.APPROVED:
            return False, f"Cannot apply mutation in {mutation.status.value} status"

        mutation.status = MutationStatus.APPLIED
        mutation.applied_timestamp = datetime.now()
        self._save_to_storage()

        return True, f"Mutation {mutation_id} applied"

    def get_mutation_impact_analysis(self, mutation_id: str) -> Optional[VisionImpact]:
        """
        Get impact analysis for a mutation.
        
        Args:
            mutation_id: ID of mutation
            
        Returns:
            VisionImpact or None if not found
        """
        if mutation_id not in self.mutations:
            return None
        return self.mutations[mutation_id].impact_analysis

    def calculate_combined_impact(
        self, mutation_ids: List[str]
    ) -> Tuple[bool, Optional[VisionImpact]]:
        """
        Calculate combined impact of multiple mutations.
        
        Args:
            mutation_ids: List of mutation IDs
            
        Returns:
            Tuple of (success, combined_impact)
        """
        # Check all mutations exist
        for mut_id in mutation_ids:
            if mut_id not in self.mutations:
                return False, None

        if not mutation_ids:
            return True, VisionImpact(
                affected_areas=set(),
                severity=ImpactSeverity.LOW,
                estimated_affected_systems=0,
                required_orchestrator_updates=False,
                requires_phase_adjustment=False,
                description="No mutations",
            )

        # Combine impacts
        all_areas: Set[ImpactArea] = set()
        max_severity = ImpactSeverity.LOW
        total_systems = 0
        needs_orchestrator_updates = False
        needs_phase_adjustment = False

        for mut_id in mutation_ids:
            impact = self.mutations[mut_id].impact_analysis
            all_areas.update(impact.affected_areas)
            
            # Update severity to highest
            severity_order = {ImpactSeverity.LOW: 0, ImpactSeverity.MEDIUM: 1, 
                            ImpactSeverity.HIGH: 2, ImpactSeverity.CRITICAL: 3}
            if severity_order[impact.severity] > severity_order[max_severity]:
                max_severity = impact.severity
            
            total_systems += impact.estimated_affected_systems
            needs_orchestrator_updates = needs_orchestrator_updates or impact.required_orchestrator_updates
            needs_phase_adjustment = needs_phase_adjustment or impact.requires_phase_adjustment

        combined = VisionImpact(
            affected_areas=all_areas,
            severity=max_severity,
            estimated_affected_systems=total_systems,
            required_orchestrator_updates=needs_orchestrator_updates,
            requires_phase_adjustment=needs_phase_adjustment,
            description=f"Combined impact of {len(mutation_ids)} mutations",
        )

        return True, combined

    def get_latest_snapshot(self) -> Optional[VisionSnapshot]:
        """
        Get the most recent vision snapshot.
        
        Returns:
            Most recent VisionSnapshot or None
        """
        if not self.snapshots:
            return None
        return max(self.snapshots.values(), key=lambda s: s.timestamp)

    def get_snapshot_history(self) -> List[VisionSnapshot]:
        """
        Get all vision snapshots in chronological order.
        
        Returns:
            List of snapshots ordered by timestamp
        """
        return sorted(self.snapshots.values(), key=lambda s: s.timestamp)

    def get_mutation_stats(self) -> Dict:
        """
        Get statistics about recorded mutations.
        
        Returns:
            Dictionary with mutation statistics
        """
        if not self.mutations:
            return {
                "total_mutations": 0,
                "by_type": {},
                "by_author": {},
                "by_status": {},
                "total_snapshots": 0,
            }

        by_type = {}
        by_author = {}
        by_status = {}

        for mutation in self.mutations.values():
            # Count by type
            type_key = mutation.mutation_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by author
            by_author[mutation.author] = by_author.get(mutation.author, 0) + 1

            # Count by status
            status_key = mutation.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

        return {
            "total_mutations": len(self.mutations),
            "by_type": by_type,
            "by_author": by_author,
            "by_status": by_status,
            "total_snapshots": len(self.snapshots),
        }

    def _calculate_hash(self, mutation: VisionMutation) -> str:
        """Calculate SHA256 hash of mutation data."""
        data = f"{mutation.mutation_id}{mutation.previous_value}{mutation.new_value}{mutation.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _calculate_vision_hash(self, vision_content: Dict) -> str:
        """Calculate SHA256 hash of vision content."""
        data = json.dumps(vision_content, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def _save_to_storage(self) -> None:
        """Save mutations and snapshots to persistent storage."""
        if not self.storage_path:
            return

        data = {
            "mutations": {k: v.to_dict() for k, v in self.mutations.items()},
            "snapshots": {k: v.to_dict() for k, v in self.snapshots.items()},
            "counter": self.mutation_counter,
        }

        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load_from_storage(self) -> None:
        """Load mutations and snapshots from persistent storage."""
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text())
            
            for mut_id, mut_data in data.get("mutations", {}).items():
                self.mutations[mut_id] = VisionMutation.from_dict(mut_data)
            
            for snap_id, snap_data in data.get("snapshots", {}).items():
                self.snapshots[snap_id] = VisionSnapshot.from_dict(snap_data)
            
            self.mutation_counter = data.get("counter", len(self.mutations))
        except Exception as e:
            # If loading fails, start fresh
            pass

    def export_mutations(self, mutation_ids: Optional[List[str]] = None) -> Dict:
        """
        Export mutations as JSON.
        
        Args:
            mutation_ids: Optional list of specific mutations to export
            
        Returns:
            Dictionary of mutations ready for JSON serialization
        """
        if mutation_ids:
            mutations = {mid: self.mutations[mid].to_dict() for mid in mutation_ids if mid in self.mutations}
        else:
            mutations = {k: v.to_dict() for k, v in self.mutations.items()}

        return {"mutations": mutations, "total": len(mutations)}

    def export_snapshots(self) -> Dict:
        """
        Export all snapshots as JSON.
        
        Returns:
            Dictionary of snapshots ready for JSON serialization
        """
        return {
            "snapshots": {k: v.to_dict() for k, v in self.snapshots.items()},
            "total": len(self.snapshots),
        }
