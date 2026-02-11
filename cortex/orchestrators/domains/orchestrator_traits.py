"""
Orchestrator Traits - Domain-Specific Behavior Interfaces

AC-AR-016-01: Trait interfaces for domain-specific orchestrator behaviors

Defines Protocol-based traits for:
- ComposableOrchestrator: Can be composed with other orchestrators
- AnalyticalOrchestrator: Provides analysis capabilities
- ExecutiveOrchestrator: Executes workflows and tasks
- ValidatingOrchestrator: Validates state and conditions
- IntegrativeOrchestrator: Integrates with external systems

Traits are implemented as typing.Protocol for structural subtyping.
No circular dependencies - tree structure verified.

Author: Asif Hussain
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Set


class ComposableOrchestrator(Protocol):
    """
    Protocol for orchestrators that can be composed with other orchestrators.

    Used by: Planning, Integration, Execution domains
    """

    @abstractmethod
    def can_compose(self) -> bool:
        """Check if this orchestrator can be composed with others."""
        ...

    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Get expected input schema for composition."""
        ...

    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema produced by this orchestrator."""
        ...


class AnalyticalOrchestrator(Protocol):
    """
    Protocol for orchestrators that provide analysis capabilities.

    Used by: Analysis, Validation domains
    """

    @abstractmethod
    def analyze(self, target: Any) -> Dict[str, Any]:
        """Perform analysis on target."""
        ...

    @abstractmethod
    def get_analysis_depth(self) -> str:
        """Get depth of analysis (shallow, medium, deep)."""
        ...

    @abstractmethod
    def get_supported_analyses(self) -> List[str]:
        """Get list of analyses this orchestrator can perform."""
        ...


class ExecutiveOrchestrator(Protocol):
    """
    Protocol for orchestrators that execute workflows.

    Used by: Execution domain
    """

    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plan and return results."""
        ...

    @abstractmethod
    def can_execute(self, plan: Dict[str, Any]) -> bool:
        """Check if this orchestrator can execute the given plan."""
        ...

    @abstractmethod
    def get_execution_modes(self) -> List[str]:
        """Get supported execution modes."""
        ...


class ValidatingOrchestrator(Protocol):
    """
    Protocol for orchestrators that validate state and conditions.

    Used by: Validation domain
    """

    @abstractmethod
    def validate(self, state: Any) -> Dict[str, Any]:
        """Validate state and return validation result."""
        ...

    @abstractmethod
    def get_validation_rules(self) -> List[str]:
        """Get list of validation rules this orchestrator applies."""
        ...

    @abstractmethod
    def get_validation_severity(self, rule: str) -> str:
        """Get severity level for a validation rule (error, warning, info)."""
        ...


class IntegrativeOrchestrator(Protocol):
    """
    Protocol for orchestrators that integrate with external systems.

    Used by: Integration domain
    """

    @abstractmethod
    def integrate(self, system: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with external system."""
        ...

    @abstractmethod
    def get_integration_points(self) -> List[str]:
        """Get list of integration points this orchestrator provides."""
        ...

    @abstractmethod
    def get_supported_systems(self) -> List[str]:
        """Get list of supported external systems."""
        ...


# Trait Hierarchy Analysis Functions

def get_trait_hierarchy() -> Dict[str, List[str]]:
    """
    Get trait inheritance hierarchy.

    Returns:
        Dict mapping each trait to its parent traits
    """
    return {
        "ComposableOrchestrator": [],
        "AnalyticalOrchestrator": [],
        "ExecutiveOrchestrator": [],
        "ValidatingOrchestrator": [],
        "IntegrativeOrchestrator": [],
    }


def detect_cycles(hierarchy: Dict[str, List[str]]) -> List[List[str]]:
    """
    Detect circular dependencies in trait hierarchy.

    Args:
        hierarchy: Dict mapping traits to parent traits

    Returns:
        List of cycles found (empty if none)
    """
    cycles: List[List[str]] = []
    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    def dfs(node: str, path: List[str]) -> None:
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for parent in hierarchy.get(node, []):
            if parent not in visited:
                dfs(parent, path.copy())
            elif parent in rec_stack:
                # Found cycle
                cycle_start = path.index(parent)
                cycles.append(path[cycle_start:] + [parent])

        rec_stack.discard(node)

    # Check all traits
    for trait in hierarchy:
        if trait not in visited:
            dfs(trait, [])

    return cycles


def is_dag(hierarchy: Dict[str, List[str]]) -> bool:
    """
    Check if trait hierarchy is a directed acyclic graph.

    Args:
        hierarchy: Dict mapping traits to parent traits

    Returns:
        True if hierarchy is a DAG, False if it has cycles
    """
    return len(detect_cycles(hierarchy)) == 0


def get_reachable_traits(
    hierarchy: Dict[str, List[str]],
    start_trait: type,
) -> Set[str]:
    """
    Get all traits reachable from a starting trait.

    Args:
        hierarchy: Trait hierarchy
        start_trait: Starting trait (class or type)

    Returns:
        Set of reachable trait names
    """
    trait_name = getattr(start_trait, "__name__", str(start_trait))
    reachable: Set[str] = {trait_name}
    to_visit = [trait_name]

    while to_visit:
        current = to_visit.pop(0)
        for parent in hierarchy.get(current, []):
            if parent not in reachable:
                reachable.add(parent)
                to_visit.append(parent)

    return reachable
