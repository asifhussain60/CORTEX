"""
Phase Dependency Validation for Holistic Change Control

Prevents modifications that would break phase dependencies or introduce
circular dependencies. Ensures all phase requirements remain satisfied.

Design: Validates entire dependency chain before allowing modifications.
"""

import yaml
from typing import Tuple, Dict, List, Set, Any, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class DependencyValidationResult(Enum):
    """Result of dependency validation."""
    VALID = "valid"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    BROKEN_REQUIREMENT = "broken_requirement"
    MISSING_PHASE = "missing_phase"
    INVALID_MODIFICATION = "invalid_modification"


@dataclass
class DependencyPath:
    """Path of dependencies between phases."""
    source: str  # Starting phase
    target: str  # Ending phase
    path: List[str]  # Full dependency chain
    distance: int = None  # Number of hops
    
    def __post_init__(self):
        if self.distance is None:
            self.distance = len(self.path) - 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "path": self.path,
            "distance": self.distance
        }


@dataclass
class DependencyValidationStatus:
    """Result of dependency validation."""
    is_valid: bool
    result_code: str  # DependencyValidationResult value
    reason: str
    affected_phases: List[str] = None
    circular_path: List[str] = None
    broken_requirements: Dict[str, List[str]] = None  # phase → [missing_requires]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "result_code": self.result_code,
            "reason": self.reason,
            "affected_phases": self.affected_phases or [],
            "circular_path": self.circular_path or [],
            "broken_requirements": self.broken_requirements or {}
        }


# =============================================================================
# PHASE DEPENDENCY ANALYZER
# =============================================================================

class PhaseDependencyAnalyzer:
    """Analyzes phase dependencies and detects issues."""
    
    def __init__(self, phase_tracker: Dict[str, Dict[str, Any]]):
        """
        Initialize analyzer with phase tracker.
        
        Args:
            phase_tracker: Dictionary of phases with metadata
        """
        self.phase_tracker = phase_tracker
        self.dependency_graph = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Build dependency graph from phase tracker.
        
        Returns:
            Dictionary of phase_id → set of required phases
        """
        graph = {}
        
        for phase_id, phase_info in self.phase_tracker.items():
            requires = phase_info.get("requires")
            
            if requires:
                # Single requirement
                if isinstance(requires, str):
                    graph[phase_id] = {requires}
                # Multiple requirements
                elif isinstance(requires, list):
                    graph[phase_id] = set(requires)
                else:
                    graph[phase_id] = set()
            else:
                graph[phase_id] = set()
        
        return graph
    
    def get_phase_dependencies(self, phase_id: str) -> Set[str]:
        """
        Get all phases that phase_id depends on (direct).
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Set of required phase IDs
        """
        return self.dependency_graph.get(phase_id, set())
    
    def get_transitive_dependencies(self, phase_id: str) -> Set[str]:
        """
        Get all phases that phase_id transitively depends on.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Set of all required phases (direct and indirect)
        """
        visited = set()
        to_process = {phase_id}
        transitive = set()
        
        while to_process:
            current = to_process.pop()
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Get direct dependencies
            deps = self.get_phase_dependencies(current)
            transitive.update(deps)
            
            # Add unvisited dependencies to process queue
            for dep in deps:
                if dep not in visited:
                    to_process.add(dep)
        
        return transitive
    
    def get_dependents(self, phase_id: str) -> Set[str]:
        """
        Get all phases that depend on phase_id (direct dependents).
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Set of phases that require this phase
        """
        dependents = set()
        
        for phase, requires in self.dependency_graph.items():
            if phase_id in requires:
                dependents.add(phase)
        
        return dependents
    
    def get_transitive_dependents(self, phase_id: str) -> Set[str]:
        """
        Get all phases that transitively depend on phase_id.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Set of all phases that depend on this phase (direct and indirect)
        """
        visited = set()
        to_process = {phase_id}
        transitive = set()
        
        while to_process:
            current = to_process.pop()
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Get phases that depend on current
            deps = self.get_dependents(current)
            transitive.update(deps)
            
            # Add unvisited dependents to process queue
            for dep in deps:
                if dep not in visited:
                    to_process.add(dep)
        
        return transitive
    
    def find_path(self, source: str, target: str) -> Optional[DependencyPath]:
        """
        Find dependency path from source to target.
        
        Args:
            source: Starting phase
            target: Ending phase
        
        Returns:
            DependencyPath if path exists, None otherwise
        """
        # BFS to find shortest path
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return DependencyPath(source, target, path)
            
            deps = self.get_phase_dependencies(current)
            
            for dep in deps:
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, path + [dep]))
        
        return None
    
    def detect_circular_dependencies(self) -> Optional[List[str]]:
        """
        Detect if there are any circular dependencies.
        
        Returns:
            List representing circular path if found, None otherwise
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(phase_id: str, path: List[str]) -> Optional[List[str]]:
            visited.add(phase_id)
            rec_stack.add(phase_id)
            
            for dep in self.get_phase_dependencies(phase_id):
                if dep not in visited:
                    cycle = has_cycle(dep, path + [dep])
                    if cycle:
                        return cycle
                elif dep in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep)
                    return path[cycle_start:] + [dep]
            
            rec_stack.remove(phase_id)
            return None
        
        for phase_id in self.phase_tracker:
            if phase_id not in visited:
                cycle = has_cycle(phase_id, [phase_id])
                if cycle:
                    return cycle
        
        return None


# =============================================================================
# DEPENDENCY MODIFICATION VALIDATOR
# =============================================================================

class DependencyModificationValidator:
    """Validates modifications to phase dependencies."""
    
    def __init__(self, phase_tracker: Dict[str, Dict[str, Any]]):
        """
        Initialize validator with phase tracker.
        
        Args:
            phase_tracker: Dictionary of phases with metadata
        """
        self.phase_tracker = phase_tracker
        self.analyzer = PhaseDependencyAnalyzer(phase_tracker)
    
    def validate_dependency_removal(self, phase_id: str, required_phase: str) -> DependencyValidationStatus:
        """
        Validate removing a dependency from a phase.
        
        Args:
            phase_id: Phase losing the dependency
            required_phase: Phase being removed from requirements
        
        Returns:
            DependencyValidationStatus
        """
        # Check if phase exists
        if phase_id not in self.phase_tracker:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.MISSING_PHASE.value,
                reason=f"Phase {phase_id} not found"
            )
        
        # Check if required_phase exists
        if required_phase not in self.phase_tracker:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.MISSING_PHASE.value,
                reason=f"Required phase {required_phase} not found"
            )
        
        # Get current dependencies
        current_requires = self.phase_tracker[phase_id].get("requires")
        
        if not current_requires:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.INVALID_MODIFICATION.value,
                reason=f"Phase {phase_id} has no dependencies"
            )
        
        if isinstance(current_requires, str):
            current_requires = {current_requires}
        else:
            current_requires = set(current_requires) if current_requires else set()
        
        # Check if removal would break anything
        if required_phase not in current_requires:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.INVALID_MODIFICATION.value,
                reason=f"Phase {phase_id} does not require {required_phase}"
            )
        
        # Simulate removal
        new_requires = current_requires - {required_phase}
        
        # Check if this breaks locked phases
        transitive_dependents = self.analyzer.get_transitive_dependents(phase_id)
        
        for dependent in transitive_dependents:
            if self.phase_tracker[dependent].get("locked"):
                return DependencyValidationStatus(
                    is_valid=False,
                    result_code=DependencyValidationResult.BROKEN_REQUIREMENT.value,
                    reason=f"Cannot remove dependency: locked phase {dependent} depends on this chain",
                    affected_phases=list(transitive_dependents)
                )
        
        return DependencyValidationStatus(
            is_valid=True,
            result_code=DependencyValidationResult.VALID.value,
            reason=f"Safe to remove dependency {required_phase} from {phase_id}"
        )
    
    def validate_dependency_addition(self, phase_id: str, new_requirement: str) -> DependencyValidationStatus:
        """
        Validate adding a new dependency to a phase.
        
        Args:
            phase_id: Phase gaining the dependency
            new_requirement: Phase being added to requirements
        
        Returns:
            DependencyValidationStatus
        """
        # Check if phases exist
        if phase_id not in self.phase_tracker:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.MISSING_PHASE.value,
                reason=f"Phase {phase_id} not found"
            )
        
        if new_requirement not in self.phase_tracker:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.MISSING_PHASE.value,
                reason=f"New requirement {new_requirement} not found"
            )
        
        # Check for self-dependency
        if phase_id == new_requirement:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.CIRCULAR_DEPENDENCY.value,
                reason="Phase cannot depend on itself",
                circular_path=[phase_id, phase_id]
            )
        
        # Check if this would create a circular dependency
        # (if new_requirement depends on phase_id, adding phase_id → new_requirement creates cycle)
        transitive_deps = self.analyzer.get_transitive_dependencies(new_requirement)
        
        if phase_id in transitive_deps:
            # Would create cycle: phase_id → new_requirement → ... → phase_id
            path = self.analyzer.find_path(new_requirement, phase_id)
            if path:
                cycle = [phase_id] + path.path
                return DependencyValidationStatus(
                    is_valid=False,
                    result_code=DependencyValidationResult.CIRCULAR_DEPENDENCY.value,
                    reason=f"Would create circular dependency: {' → '.join(cycle)}",
                    circular_path=cycle
                )
        
        return DependencyValidationStatus(
            is_valid=True,
            result_code=DependencyValidationResult.VALID.value,
            reason=f"Safe to add dependency on {new_requirement} to {phase_id}"
        )
    
    def validate_phase_modification(self, phase_id: str, new_requires: Optional[List[str]] = None) -> DependencyValidationStatus:
        """
        Validate modifying a phase's requirements.
        
        Args:
            phase_id: Phase being modified
            new_requires: New list of required phases
        
        Returns:
            DependencyValidationStatus
        """
        if phase_id not in self.phase_tracker:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.MISSING_PHASE.value,
                reason=f"Phase {phase_id} not found"
            )
        
        new_requires = new_requires or []
        
        # Check if all new requirements exist
        for req in new_requires:
            if req not in self.phase_tracker:
                return DependencyValidationStatus(
                    is_valid=False,
                    result_code=DependencyValidationResult.MISSING_PHASE.value,
                    reason=f"Required phase {req} not found"
                )
        
        # Check for self-dependency
        if phase_id in new_requires:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.CIRCULAR_DEPENDENCY.value,
                reason="Phase cannot depend on itself",
                circular_path=[phase_id, phase_id]
            )
        
        # Check for circular dependencies
        new_graph = dict(self.analyzer.dependency_graph)
        new_graph[phase_id] = set(new_requires)
        
        # Simple cycle detection: check if any new requirement transitively depends on phase_id
        for req in new_requires:
            visited = set()
            to_check = {req}
            
            while to_check:
                current = to_check.pop()
                if current in visited:
                    continue
                visited.add(current)
                
                if current == phase_id:
                    path = self._find_cycle_path(phase_id, req, new_graph)
                    return DependencyValidationStatus(
                        is_valid=False,
                        result_code=DependencyValidationResult.CIRCULAR_DEPENDENCY.value,
                        reason=f"Would create circular dependency",
                        circular_path=path
                    )
                
                to_check.update(new_graph.get(current, set()))
        
        # Check if this breaks locked phases
        current_requires = self.phase_tracker[phase_id].get("requires")
        removed = set(current_requires or []) - set(new_requires)
        
        if removed:
            transitive_dependents = self.analyzer.get_transitive_dependents(phase_id)
            
            for dependent in transitive_dependents:
                if self.phase_tracker[dependent].get("locked"):
                    return DependencyValidationStatus(
                        is_valid=False,
                        result_code=DependencyValidationResult.BROKEN_REQUIREMENT.value,
                        reason=f"Cannot modify: locked phase {dependent} depends on this phase",
                        affected_phases=list(transitive_dependents)
                    )
        
        return DependencyValidationStatus(
            is_valid=True,
            result_code=DependencyValidationResult.VALID.value,
            reason=f"Safe to modify dependencies for {phase_id}"
        )
    
    def _find_cycle_path(self, target: str, source: str, graph: Dict[str, Set[str]]) -> List[str]:
        """Find path from source back to target."""
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            for dep in graph.get(current, set()):
                if dep == target:
                    return path + [dep]
                
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, path + [dep]))
        
        return [source, target]


# =============================================================================
# HOLISTIC DEPENDENCY VALIDATOR
# =============================================================================

class HolisticDependencyValidator:
    """
    Validates all phase dependencies holistically.
    
    Ensures:
    - No circular dependencies
    - All locked phase requirements preserved
    - No broken dependency chains
    """
    
    def __init__(self, phase_tracker: Dict[str, Dict[str, Any]]):
        """
        Initialize validator.
        
        Args:
            phase_tracker: Dictionary of phases with metadata
        """
        self.phase_tracker = phase_tracker
        self.analyzer = PhaseDependencyAnalyzer(phase_tracker)
        self.modification_validator = DependencyModificationValidator(phase_tracker)
    
    def validate_all_dependencies(self) -> DependencyValidationStatus:
        """
        Validate entire dependency graph.
        
        Returns:
            DependencyValidationStatus
        """
        # Check for circular dependencies
        cycle = self.analyzer.detect_circular_dependencies()
        
        if cycle:
            return DependencyValidationStatus(
                is_valid=False,
                result_code=DependencyValidationResult.CIRCULAR_DEPENDENCY.value,
                reason=f"Circular dependency detected: {' → '.join(cycle)}",
                circular_path=cycle
            )
        
        # Check that all required phases exist
        for phase_id, phase_info in self.phase_tracker.items():
            requires = phase_info.get("requires")
            
            if requires:
                if isinstance(requires, str):
                    requires = [requires]
                
                for req in requires:
                    if req not in self.phase_tracker:
                        return DependencyValidationStatus(
                            is_valid=False,
                            result_code=DependencyValidationResult.MISSING_PHASE.value,
                            reason=f"Phase {phase_id} requires non-existent phase {req}",
                            affected_phases=[phase_id]
                        )
        
        return DependencyValidationStatus(
            is_valid=True,
            result_code=DependencyValidationResult.VALID.value,
            reason="All dependencies valid"
        )
    
    def validate_locked_phases_safe(self) -> DependencyValidationStatus:
        """
        Validate that all locked phases have their requirements satisfied.
        
        Returns:
            DependencyValidationStatus
        """
        for phase_id, phase_info in self.phase_tracker.items():
            if phase_info.get("locked"):
                # Check that all requirements exist and are either completed or in progress
                requires = phase_info.get("requires")
                
                if requires:
                    if isinstance(requires, str):
                        requires = [requires]
                    
                    for req in requires:
                        if req not in self.phase_tracker:
                            return DependencyValidationStatus(
                                is_valid=False,
                                result_code=DependencyValidationResult.MISSING_PHASE.value,
                                reason=f"Locked phase {phase_id} requires non-existent phase {req}",
                                affected_phases=[phase_id]
                            )
                        
                        req_info = self.phase_tracker[req]
                        if req_info.get("status") not in ["COMPLETED", "IN_PROGRESS"]:
                            return DependencyValidationStatus(
                                is_valid=False,
                                result_code=DependencyValidationResult.BROKEN_REQUIREMENT.value,
                                reason=f"Locked phase {phase_id} requires {req} which is {req_info.get('status')}",
                                affected_phases=[phase_id]
                            )
        
        return DependencyValidationStatus(
            is_valid=True,
            result_code=DependencyValidationResult.VALID.value,
            reason="All locked phase requirements satisfied"
        )
    
    def get_dependency_graph_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive dependency graph summary.
        
        Returns:
            Dictionary with graph analysis
        """
        summary = {
            "phases": {},
            "cycles": [],
            "locked_phases": [],
            "orphaned_phases": []
        }
        
        # Detect cycles
        cycle = self.analyzer.detect_circular_dependencies()
        if cycle:
            summary["cycles"].append(cycle)
        
        # Analyze each phase
        for phase_id, phase_info in self.phase_tracker.items():
            phase_summary = {
                "locked": phase_info.get("locked", False),
                "status": phase_info.get("status"),
                "direct_requires": list(self.analyzer.get_phase_dependencies(phase_id)),
                "transitive_requires": list(self.analyzer.get_transitive_dependencies(phase_id)),
                "direct_dependents": list(self.analyzer.get_dependents(phase_id)),
                "transitive_dependents": list(self.analyzer.get_transitive_dependents(phase_id))
            }
            
            summary["phases"][phase_id] = phase_summary
            
            if phase_info.get("locked"):
                summary["locked_phases"].append(phase_id)
            
            # Check if orphaned (no requirements, no dependents)
            if not phase_summary["direct_requires"] and not phase_summary["direct_dependents"]:
                summary["orphaned_phases"].append(phase_id)
        
        return summary
