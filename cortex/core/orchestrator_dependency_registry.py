"""
Tier-Orchestrator Dependency Registry - AC-AR-015-02

Tracks dependencies between orchestrators and tiers:
- Which tiers each orchestrator depends on
- Transitive dependencies across orchestrator hierarchy
- Circular dependency detection
- Impact analysis for tier changes
- Consistency validation

Enables orchestrator composition and vision evolution while
maintaining consistency between vision and implementation.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class TierLevel(Enum):
    """Tier levels in the CORTEX system."""
    TIER0 = "tier0"  # Governance rules
    TIER1 = "tier1"  # Acceptance criteria
    TIER2 = "tier2"  # Response templates
    TIER3 = "tier3"  # Orchestration


class DependencyType(Enum):
    """Types of dependencies between orchestrators and tiers."""
    DIRECT = "direct"  # Orchestrator directly uses tier
    TRANSITIVE = "transitive"  # Via other orchestrator
    INHERITED = "inherited"  # From parent orchestrator


class RegistryValidationResult(Enum):
    """Results of registry validation."""
    VALID = "valid"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_TIER = "missing_tier"
    INCONSISTENT = "inconsistent"
    UNRESOLVED_ORCHESTRATOR = "unresolved_orchestrator"


@dataclass
class TierDependency:
    """Represents a dependency on a specific tier."""
    tier: TierLevel
    dependency_type: DependencyType
    via_orchestrator: Optional[str] = None  # If transitive/inherited
    required_features: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tier": self.tier.value,
            "dependency_type": self.dependency_type.value,
            "via_orchestrator": self.via_orchestrator,
            "required_features": self.required_features,
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict) -> "TierDependency":
        """Create from dictionary."""
        return TierDependency(
            tier=TierLevel(data["tier"]),
            dependency_type=DependencyType(data["dependency_type"]),
            via_orchestrator=data.get("via_orchestrator"),
            required_features=data.get("required_features", []),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
        )


@dataclass
class OrchestratorProfile:
    """Profile of an orchestrator and its tier dependencies."""
    orchestrator_id: str
    name: str
    parent_orchestrator: Optional[str] = None
    tier_dependencies: Dict[str, TierDependency] = field(default_factory=dict)  # key is tier.value
    description: str = ""
    created_timestamp: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "orchestrator_id": self.orchestrator_id,
            "name": self.name,
            "parent_orchestrator": self.parent_orchestrator,
            "tier_dependencies": {k: v.to_dict() for k, v in self.tier_dependencies.items()},
            "description": self.description,
            "created_timestamp": self.created_timestamp.isoformat(),
            "last_modified": self.last_modified.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict) -> "OrchestratorProfile":
        """Create from dictionary."""
        return OrchestratorProfile(
            orchestrator_id=data["orchestrator_id"],
            name=data["name"],
            parent_orchestrator=data.get("parent_orchestrator"),
            tier_dependencies={k: TierDependency.from_dict(v)
                             for k, v in data.get("tier_dependencies", {}).items()},
            description=data.get("description", ""),
            created_timestamp=datetime.fromisoformat(data.get("created_timestamp", datetime.now().isoformat())),
            last_modified=datetime.fromisoformat(data.get("last_modified", datetime.now().isoformat())),
        )


@dataclass
class DependencyPath:
    """Represents a path of dependencies."""
    path: List[str]  # Sequence of orchestrator IDs
    involves_tiers: Set[str] = field(default_factory=set)
    distance: int = field(default=0)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "involves_tiers": list(self.involves_tiers),
            "distance": self.distance,
        }


@dataclass
class RegistryValidationReport:
    """Comprehensive validation report for the registry."""
    is_valid: bool
    result: RegistryValidationResult
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    total_orchestrators: int = 0
    total_tier_dependencies: int = 0
    circular_paths: List[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "result": self.result.value,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
            "total_orchestrators": self.total_orchestrators,
            "total_tier_dependencies": self.total_tier_dependencies,
            "circular_paths": self.circular_paths,
        }


class OrchestratorDependencyRegistry:
    """
    Central registry for orchestrator-tier dependencies.

    Manages:
    - Tracking which tiers each orchestrator depends on
    - Building transitive dependency relationships
    - Detecting circular dependencies
    - Validating consistency
    - Supporting impact analysis
    - Enabling orchestrator composition
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the dependency registry.

        Args:
            storage_path: Path to JSON file for persistence (optional)
        """
        self.storage_path = storage_path or Path("orchestrator_registry.json")
        self.orchestrators: Dict[str, OrchestratorProfile] = {}
        self.tier_assignments: Dict[str, Set[str]] = {  # tier -> set of orchestrator IDs
            tier.value: set() for tier in TierLevel
        }
        self._load_from_storage()

    def register_orchestrator(
        self,
        orchestrator_id: str,
        name: str,
        description: str = "",
        parent_orchestrator: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Register a new orchestrator in the registry.

        Args:
            orchestrator_id: Unique identifier for orchestrator
            name: Human-readable name
            description: Description of orchestrator
            parent_orchestrator: Optional parent orchestrator ID

        Returns:
            Tuple of (success, message)
        """
        if orchestrator_id in self.orchestrators:
            return False, f"Orchestrator {orchestrator_id} already registered"

        # Validate parent if provided
        if parent_orchestrator and parent_orchestrator not in self.orchestrators:
            return False, f"Parent orchestrator {parent_orchestrator} not found"

        profile = OrchestratorProfile(
            orchestrator_id=orchestrator_id,
            name=name,
            parent_orchestrator=parent_orchestrator,
            description=description,
        )

        self.orchestrators[orchestrator_id] = profile
        self._save_to_storage()

        return True, f"Orchestrator {orchestrator_id} registered"

    def add_tier_dependency(
        self,
        orchestrator_id: str,
        tier: TierLevel,
        dependency_type: DependencyType = DependencyType.DIRECT,
        via_orchestrator: Optional[str] = None,
        required_features: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Add a tier dependency for an orchestrator.

        Args:
            orchestrator_id: ID of orchestrator
            tier: Which tier is required
            dependency_type: Type of dependency
            via_orchestrator: If transitive, which orchestrator mediates
            required_features: List of required features from tier

        Returns:
            Tuple of (success, message)
        """
        if orchestrator_id not in self.orchestrators:
            return False, f"Orchestrator {orchestrator_id} not found"

        # Validate via_orchestrator if provided
        if via_orchestrator and via_orchestrator not in self.orchestrators:
            return False, f"Via orchestrator {via_orchestrator} not found"

        if via_orchestrator and orchestrator_id == via_orchestrator:
            return False, "Orchestrator cannot depend on itself"

        profile = self.orchestrators[orchestrator_id]
        tier_key = tier.value

        # Check if dependency already exists
        if tier_key in profile.tier_dependencies:
            return False, f"Dependency on {tier_key} already exists"

        dependency = TierDependency(
            tier=tier,
            dependency_type=dependency_type,
            via_orchestrator=via_orchestrator,
            required_features=required_features or [],
        )

        profile.tier_dependencies[tier_key] = dependency
        self.tier_assignments[tier_key].add(orchestrator_id)
        profile.last_modified = datetime.now()
        self._save_to_storage()

        return True, f"Added {tier_key} dependency to {orchestrator_id}"

    def remove_tier_dependency(
        self,
        orchestrator_id: str,
        tier: TierLevel,
    ) -> Tuple[bool, str]:
        """
        Remove a tier dependency from an orchestrator.

        Args:
            orchestrator_id: ID of orchestrator
            tier: Tier to remove dependency from

        Returns:
            Tuple of (success, message)
        """
        if orchestrator_id not in self.orchestrators:
            return False, f"Orchestrator {orchestrator_id} not found"

        profile = self.orchestrators[orchestrator_id]
        tier_key = tier.value

        if tier_key not in profile.tier_dependencies:
            return False, f"No dependency on {tier_key} found"

        del profile.tier_dependencies[tier_key]
        self.tier_assignments[tier_key].discard(orchestrator_id)
        profile.last_modified = datetime.now()
        self._save_to_storage()

        return True, f"Removed {tier_key} dependency from {orchestrator_id}"

    def get_tier_dependencies(
        self,
        orchestrator_id: str,
        include_inherited: bool = False,
    ) -> Dict[str, TierDependency]:
        """
        Get tier dependencies for an orchestrator.

        Args:
            orchestrator_id: ID of orchestrator
            include_inherited: Whether to include parent dependencies

        Returns:
            Dictionary of tier dependencies
        """
        if orchestrator_id not in self.orchestrators:
            return {}

        profile = self.orchestrators[orchestrator_id]
        dependencies = dict(profile.tier_dependencies)

        if include_inherited and profile.parent_orchestrator:
            parent_deps = self.get_tier_dependencies(
                profile.parent_orchestrator,
                include_inherited=True
            )
            for tier_key, dep in parent_deps.items():
                if tier_key not in dependencies:
                    inherited_dep = TierDependency(
                        tier=dep.tier,
                        dependency_type=DependencyType.INHERITED,
                        via_orchestrator=profile.parent_orchestrator,
                        required_features=dep.required_features.copy(),
                    )
                    dependencies[tier_key] = inherited_dep

        return dependencies

    def get_orchestrators_for_tier(self, tier: TierLevel) -> Set[str]:
        """
        Get all orchestrators that depend on a tier.

        Args:
            tier: The tier to query

        Returns:
            Set of orchestrator IDs depending on this tier
        """
        return set(self.tier_assignments.get(tier.value, set()))

    def find_transitive_dependencies(
        self,
        orchestrator_id: str,
    ) -> Set[str]:
        """
        Find all transitive orchestrator dependencies.

        Args:
            orchestrator_id: ID of orchestrator

        Returns:
            Set of all orchestrator IDs this one depends on (transitively)
        """
        if orchestrator_id not in self.orchestrators:
            return set()

        visited = set()
        to_visit = [orchestrator_id]
        transitive_deps = set()

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)

            profile = self.orchestrators[current]
            if profile.parent_orchestrator and profile.parent_orchestrator not in transitive_deps:
                transitive_deps.add(profile.parent_orchestrator)
                to_visit.append(profile.parent_orchestrator)

        return transitive_deps

    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in orchestrator hierarchy.

        Returns:
            List of circular dependency paths
        """
        circular_paths = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            profile = self.orchestrators.get(node)
            if profile and profile.parent_orchestrator:
                parent = profile.parent_orchestrator
                if parent not in visited:
                    dfs(parent, path.copy())
                elif parent in rec_stack:
                    # Found cycle
                    cycle_start = path.index(parent) if parent in path else 0
                    cycle = path[cycle_start:] + [parent]
                    if cycle not in circular_paths:
                        circular_paths.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for orch_id in self.orchestrators:
            if orch_id not in visited:
                dfs(orch_id, [])

        return circular_paths

    def validate_registry(self) -> RegistryValidationReport:
        """
        Validate the entire registry for consistency.

        Returns:
            RegistryValidationReport with detailed findings
        """
        report = RegistryValidationReport(
            is_valid=True,
            result=RegistryValidationResult.VALID,
            total_orchestrators=len(self.orchestrators),
        )

        # Check for circular dependencies
        circular_paths = self.detect_circular_dependencies()
        if circular_paths:
            report.is_valid = False
            report.result = RegistryValidationResult.CIRCULAR_DEPENDENCY
            report.errors.append(f"Found {len(circular_paths)} circular dependencies")
            report.circular_paths = circular_paths

        # Check for broken references
        for orch_id, profile in self.orchestrators.items():
            if profile.parent_orchestrator and profile.parent_orchestrator not in self.orchestrators:
                report.is_valid = False
                report.result = RegistryValidationResult.UNRESOLVED_ORCHESTRATOR
                report.errors.append(f"Orchestrator {orch_id} references unknown parent {profile.parent_orchestrator}")

            for dep in profile.tier_dependencies.values():
                if dep.via_orchestrator and dep.via_orchestrator not in self.orchestrators:
                    report.is_valid = False
                    report.result = RegistryValidationResult.UNRESOLVED_ORCHESTRATOR
                    report.errors.append(f"Orchestrator {orch_id} references unknown via orchestrator {dep.via_orchestrator}")

            report.total_tier_dependencies += len(profile.tier_dependencies)

        report.timestamp = datetime.now()
        return report

    def analyze_tier_change_impact(
        self,
        tier: TierLevel,
        change_severity: str,
    ) -> Dict:
        """
        Analyze impact of a tier change on orchestrators.

        Args:
            tier: Which tier is changing
            change_severity: Severity of change (minor, major, breaking)

        Returns:
            Impact analysis dictionary
        """
        affected_orchestrators = self.get_orchestrators_for_tier(tier)
        direct_count = len(affected_orchestrators)

        affected_via_orchestrator = set()
        for orch_id in self.orchestrators:
            deps = self.find_transitive_dependencies(orch_id)
            matching_deps = {d for d in deps if d in affected_orchestrators}
            if matching_deps:
                affected_via_orchestrator.add(orch_id)

        return {
            "tier": tier.value,
            "change_severity": change_severity,
            "directly_affected_orchestrators": direct_count,
            "indirectly_affected_orchestrators": len(affected_via_orchestrator),
            "total_affected": direct_count + len(affected_via_orchestrator),
            "affected_orchestrators": sorted(list(affected_orchestrators)),
            "affected_via_orchestrator": sorted(list(affected_via_orchestrator)),
        }

    def get_registry_stats(self) -> Dict:
        """
        Get statistics about the registry.

        Returns:
            Dictionary with registry statistics
        """
        if not self.orchestrators:
            return {
                "total_orchestrators": 0,
                "by_tier": {},
                "has_circular_dependencies": False,
            }

        by_tier = {}
        for tier in TierLevel:
            count = len(self.tier_assignments.get(tier.value, set()))
            by_tier[tier.value] = count

        circular = self.detect_circular_dependencies()

        return {
            "total_orchestrators": len(self.orchestrators),
            "by_tier": by_tier,
            "has_circular_dependencies": len(circular) > 0,
            "circular_dependency_count": len(circular),
            "orchestrators_with_parents": len([
                o for o in self.orchestrators.values()
                if o.parent_orchestrator
            ]),
        }

    def export_registry(self) -> Dict:
        """
        Export entire registry as JSON-serializable dictionary.

        Returns:
            Dictionary ready for JSON serialization
        """
        return {
            "orchestrators": {
                orch_id: profile.to_dict()
                for orch_id, profile in self.orchestrators.items()
            },
            "tier_assignments": {
                tier: sorted(list(orch_ids))
                for tier, orch_ids in self.tier_assignments.items()
            },
            "generated_timestamp": datetime.now().isoformat(),
        }

    def _save_to_storage(self) -> None:
        """Save registry to persistent storage."""
        if not self.storage_path:
            return

        data = self.export_registry()
        self.storage_path.write_text(json.dumps(data, indent=2))

    def _load_from_storage(self) -> None:
        """Load registry from persistent storage."""
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text())

            for orch_id, orch_data in data.get("orchestrators", {}).items():
                profile = OrchestratorProfile.from_dict(orch_data)
                self.orchestrators[orch_id] = profile

            for tier_str, orch_ids in data.get("tier_assignments", {}).items():
                self.tier_assignments[tier_str] = set(orch_ids)
        except Exception:
            # If loading fails, start fresh
            pass
