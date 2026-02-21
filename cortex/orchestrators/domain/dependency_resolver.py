"""
Dependency Resolver

Extracted from PhaseDependencyAnalyzer (cortex/brain/core/dependency_validator.py).
Resolves phase dependencies using topological sort (Kahn's algorithm).

Authority: Wave 8 Stage 3
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional
from enum import Enum
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
    def from_dict(cls, data: Dict[str, List[str]]) -> "DependencyGraph":
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


class DependencyResolver(OrchestratorProtocolMixin):
    """
    Resolve phase dependencies using topological sort.
    
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
    
    def resolve(self, graph: DependencyGraph) -> ResolutionResult:
        """
        Resolve dependency order using topological sort.
        
        Args:
            graph: Dependency graph to resolve
        
        Returns:
            ResolutionResult with execution order or error details
        """
        # Check for missing dependencies first
        missing = self._check_missing_dependencies(graph)
        if missing:
            return ResolutionResult(
                status=ResolutionStatus.MISSING_DEPENDENCY,
                execution_order=[],
                missing_dependencies=missing
            )
        
        # Kahn's algorithm for topological sort
        in_degree = {phase: 0 for phase in graph.phases}
        
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
