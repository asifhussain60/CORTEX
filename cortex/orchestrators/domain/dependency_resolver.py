"""
Dependency Resolver

Extracted from PhaseDependencyAnalyzer (cortex/brain/core/dependency_validator.py).
Resolves phase dependencies using topological sort (Kahn's algorithm).

Authority: Wave 8 Stage 3
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from pathlib import Path
import re
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class ResolutionStatus(Enum):
    """Status of dependency resolution"""
    SUCCESS = "success"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"


@dataclass
class DependencyGraph:
    """Phase dependency graph"""
    phases: Set[str]
    dependencies: Dict[str, Set[str]]  # phase_id → set of required phases

    def __post_init__(self):
        """Validate graph structure"""
        # Ensure all phases in dependencies are in phases set
        for phase_id, deps in self.dependencies.items():
            if phase_id not in self.phases:
                raise ValueError(f"Phase {phase_id} in dependencies but not in phases set")

            for dep in deps:
                if dep not in self.phases:
                    raise ValueError(
                        f"Dependency {dep} of {phase_id} not in phases set"
                    )

    @classmethod
    def from_dict(cls: object, data: Dict[str, List[str]]) -> "DependencyGraph":
        """
        Create graph from dictionary.

        Args:
            data: Dictionary of phase_id → list of dependencies

        Returns:
            DependencyGraph instance
        """
        phases = set(data.keys())

        # Also add dependencies that might not be keys
        for deps in data.values():
            phases.update(deps)

        dependencies = {
            phase_id: set(deps) for phase_id, deps in data.items()
        }

        # Ensure all phases have an entry (even if empty)
        for phase_id in phases:
            if phase_id not in dependencies:
                dependencies[phase_id] = set()

        return cls(phases=phases, dependencies=dependencies)


@dataclass
class ResolutionResult:
    """Result of dependency resolution"""
    status: ResolutionStatus
    execution_order: List[str]
    circular_path: Optional[List[str]] = None
    missing_dependencies: Optional[Dict[str, List[str]]] = None

    @property
    def is_success(self) -> bool:
        """Check if resolution succeeded"""
        return self.status == ResolutionStatus.SUCCESS

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "execution_order": self.execution_order,
            "circular_path": self.circular_path,
            "missing_dependencies": self.missing_dependencies,
        }


@dataclass
class VersionConflict:
    """Represents a version conflict across repos."""

    package: str
    versions: Dict[str, str]  # repo_name → version_spec

    @property
    def recommendation(self) -> str:
        """Return a simple recommendation string."""
        return "upgrade"


@dataclass
class ResolutionStrategy:
    """Suggested resolution for a set of conflicts."""

    package: str
    recommendation: str  # "unified" | "isolated" | "upgrade"
    details: str = ""


class DependencyResolver(OrchestratorProtocolMixin):
    """
    Resolve phase dependencies using topological sort.

    Also supports multi-repo workspace scanning for package-level conflict
    detection (AC-DEP-002-05).

    Uses Kahn's algorithm for cycle-free topological ordering.
    Thread-safe, stateless resolver.

    Example:
        >>> graph = DependencyGraph.from_dict({
        ...     "phase-1": [],
        ...     "phase-2": ["phase-1"],
        ...     "phase-3": ["phase-1", "phase-2"]
        ... })
        >>> resolver = DependencyResolver()
        >>> result = resolver.resolve(graph)
        >>> print(result.execution_order)  # ['phase-1', 'phase-2', 'phase-3']
        >>> print(result.is_success)  # True
    """

    def __init__(self, workspace: Optional[Path] = None) -> None:
        """
        Initialise resolver.

        Args:
            workspace: Optional path to a multi-repo workspace root
                       (directory whose sub-directories each contain a repo).
        """
        super().__init__()
        self.workspace: Optional[Path] = workspace

    # ------------------------------------------------------------------
    # Multi-repo workspace scanning API (AC-DEP-002-05)
    # ------------------------------------------------------------------

    def scan_requirements(self) -> Dict[str, Dict[str, str]]:
        """
        Scan all repos under *workspace* for requirements.txt files.

        Returns:
            Mapping of repo_name → {package: version_spec}.
        """
        if self.workspace is None:
            return {}

        repos: Dict[str, Dict[str, str]] = {}
        for entry in sorted(self.workspace.iterdir()):
            if not entry.is_dir():
                continue
            req_file = entry / "requirements.txt"
            if req_file.exists():
                repos[entry.name] = self._parse_requirements(req_file)
        return repos

    def build_dependency_graph(self) -> Dict[str, Dict[str, str]]:
        """
        Build a package → {repo: version_spec} graph.

        Returns:
            Mapping of package → {repo_name: version_spec}.
        """
        repos = self.scan_requirements()
        graph: Dict[str, Dict[str, str]] = {}
        for repo_name, packages in repos.items():
            for package, version in packages.items():
                graph.setdefault(package, {})[repo_name] = version
        return graph

    def detect_conflicts(self) -> List[VersionConflict]:
        """
        Detect packages with incompatible version constraints across repos.

        Returns:
            List of VersionConflict objects (one per conflicted package).
        """
        graph = self.build_dependency_graph()
        conflicts: List[VersionConflict] = []
        for package, repo_versions in graph.items():
            if len(repo_versions) < 2:
                continue
            if self._has_version_conflict(list(repo_versions.values())):
                conflicts.append(VersionConflict(package=package, versions=repo_versions))
        return conflicts

    def suggest_resolutions(self) -> List[ResolutionStrategy]:
        """
        Suggest resolution strategies for all detected conflicts.

        Returns:
            List of ResolutionStrategy objects.
        """
        conflicts = self.detect_conflicts()
        strategies: List[ResolutionStrategy] = []
        for conflict in conflicts:
            # Simple heuristic: if specs differ by major → isolated; else upgrade
            specs = list(conflict.versions.values())
            majors = {self._major_version(s) for s in specs if self._major_version(s) is not None}
            if len(majors) > 1:
                rec = "isolated"
                detail = f"Major version split {majors} — recommend separate venvs"
            else:
                rec = "upgrade"
                detail = f"Minor conflict in {conflict.package} — upgrade to highest floor"
            strategies.append(ResolutionStrategy(package=conflict.package, recommendation=rec, details=detail))
        return strategies

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a conflict resolution report.

        Returns:
            Dict with 'conflicts' and 'recommendations' keys.
        """
        conflicts = self.detect_conflicts()
        strategies = self.suggest_resolutions()
        return {
            "conflicts": [
                {"package": c.package, "versions": c.versions} for c in conflicts
            ],
            "recommendations": [
                {"package": s.package, "recommendation": s.recommendation, "details": s.details}
                for s in strategies
            ],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_requirements(req_file: Path) -> Dict[str, str]:
        """Parse a requirements.txt into {package: version_spec}."""
        packages: Dict[str, str] = {}
        for line in req_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^([A-Za-z0-9_\-\.]+)(.*)", line)
            if m:
                packages[m.group(1).lower()] = m.group(2).strip()
        return packages

    @staticmethod
    def _has_version_conflict(specs: List[str]) -> bool:
        """Return True if two version specs are incompatible (floor check)."""
        floors: List[tuple] = []
        for spec in specs:
            m = re.search(r">=\s*(\d+)\.(\d+)", spec)
            if m:
                floors.append((int(m.group(1)), int(m.group(2))))
        if len(floors) < 2:
            return False
        floors.sort()
        # Conflict if the highest floor is in a different major than the lowest
        return floors[-1][0] != floors[0][0]

    @staticmethod
    def _major_version(spec: str) -> Optional[int]:
        """Extract major version floor from a spec string."""
        m = re.search(r">=\s*(\d+)", spec)
        return int(m.group(1)) if m else None

    # ------------------------------------------------------------------
    # Phase dependency resolution (original API)
    # ------------------------------------------------------------------

    def resolve(self, graph: DependencyGraph) -> ResolutionResult:
        """
        Resolve dependency order using topological sort.

        Args:
            graph: Dependency graph to resolve

        Returns:
            ResolutionResult with execution order or error details
        """
        # Check for missing dependencies first
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="resolve_dependencies")
        missing = self._check_missing_dependencies(graph)
        if missing:
            return ResolutionResult(
                status=ResolutionStatus.MISSING_DEPENDENCY,
                execution_order=[],
                missing_dependencies=missing
            )

        # Kahn's algorithm for topological sort
        in_degree = dict.fromkeys(graph.phases, 0)

        # Calculate in-degrees: count how many dependencies each phase has
        for phase_id, deps in graph.dependencies.items():
            in_degree[phase_id] = len(deps)

        # Start with phases that have no dependencies
        queue = [phase for phase in in_degree if in_degree[phase] == 0]
        result = []

        while queue:
            # Sort for deterministic ordering
            queue.sort()
            phase = queue.pop(0)
            result.append(phase)

            # Find phases that depend on current phase
            for dependent_phase, deps in graph.dependencies.items():
                if phase in deps:
                    in_degree[dependent_phase] -= 1
                    if in_degree[dependent_phase] == 0:
                        queue.append(dependent_phase)

        # Check if all phases were processed (no cycles)
        if len(result) != len(graph.phases):
            circular_path = self._detect_circular_path(graph)
            return ResolutionResult(
                status=ResolutionStatus.CIRCULAR_DEPENDENCY,
                execution_order=[],
                circular_path=circular_path
            )

        return ResolutionResult(
            status=ResolutionStatus.SUCCESS,
            execution_order=result
        )

    def _check_missing_dependencies(
        self,
        graph: DependencyGraph
    ) -> Optional[Dict[str, List[str]]]:
        """
        Check for dependencies that don't exist in phases set.

        Args:
            graph: Dependency graph

        Returns:
            Dictionary of phase → missing dependencies, or None if all valid
        """
        missing = {}

        for phase_id, deps in graph.dependencies.items():
            missing_deps = [dep for dep in deps if dep not in graph.phases]
            if missing_deps:
                missing[phase_id] = missing_deps

        return missing if missing else None

    def _detect_circular_path(self, graph: DependencyGraph) -> List[str]:
        """
        Detect circular dependency path.

        Args:
            graph: Dependency graph

        Returns:
            List of phases forming the circular path
        """
        visited = set()
        rec_stack = set()

        def has_cycle(phase_id: str, path: List[str]) -> Optional[List[str]]:
            """Detect a cycle starting from *phase_id* via DFS."""
            visited.add(phase_id)
            rec_stack.add(phase_id)

            for dep in graph.dependencies.get(phase_id, set()):
                if dep not in visited:
                    cycle = has_cycle(dep, path + [dep])
                    if cycle:
                        return cycle
                elif dep in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep) if dep in path else 0
                    return path[cycle_start:] + [dep]

            rec_stack.remove(phase_id)
            return None

        for phase_id in graph.phases:
            if phase_id not in visited:
                cycle = has_cycle(phase_id, [phase_id])
                if cycle:
                    return cycle

        return []

    def get_transitive_dependencies(
        self,
        graph: DependencyGraph,
        phase_id: str
    ) -> Set[str]:
        """
        Get all transitive dependencies of a phase.

        Args:
            graph: Dependency graph
            phase_id: Phase to analyze

        Returns:
            Set of all phases that phase_id depends on (directly or indirectly)
        """
        if phase_id not in graph.phases:
            raise ValueError(f"Phase {phase_id} not in graph")

        visited = set()
        to_process = {phase_id}
        transitive = set()

        while to_process:
            current = to_process.pop()

            if current in visited:
                continue

            visited.add(current)

            # Get direct dependencies
            deps = graph.dependencies.get(current, set())
            transitive.update(deps)

            # Add unvisited dependencies to process queue
            for dep in deps:
                if dep not in visited:
                    to_process.add(dep)

        return transitive
