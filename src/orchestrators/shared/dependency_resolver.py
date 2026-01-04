"""
Dependency Resolver - Graph-based dependency management for plans and phases

Provides topological sorting, cycle detection, and dependency validation
for both epic-level (plan dependencies) and feature-level (phase dependencies).

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies."""
    REQUIRED = "required"  # Must complete before dependent can start
    OPTIONAL = "optional"  # Recommended but not blocking
    PARALLEL = "parallel"  # Can run in parallel


@dataclass
class DependencyNode:
    """Node in dependency graph."""
    node_id: str
    node_name: str
    node_type: str  # "plan" or "phase"
    dependencies: List[str] = field(default_factory=list)
    dependency_types: Dict[str, DependencyType] = field(default_factory=dict)
    status: str = "not-started"
    
    def add_dependency(self, dep_id: str, dep_type: DependencyType = DependencyType.REQUIRED) -> None:
        """Add a dependency to this node."""
        if dep_id not in self.dependencies:
            self.dependencies.append(dep_id)
            self.dependency_types[dep_id] = dep_type
    
    def is_ready(self, completed_nodes: Set[str]) -> Tuple[bool, List[str]]:
        """
        Check if node is ready to execute (all required dependencies met).
        
        Returns:
            (is_ready, blocking_dependencies)
        """
        blocking = []
        for dep_id in self.dependencies:
            dep_type = self.dependency_types.get(dep_id, DependencyType.REQUIRED)
            if dep_type == DependencyType.REQUIRED and dep_id not in completed_nodes:
                blocking.append(dep_id)
        
        return (len(blocking) == 0, blocking)


class DependencyGraph:
    """
    Dependency graph for plans or phases.
    
    Features:
    - Topological sorting (execution order)
    - Cycle detection (circular dependencies)
    - Readiness checking (unblocking)
    - Critical path calculation
    """
    
    def __init__(self):
        """Initialize empty dependency graph."""
        self.nodes: Dict[str, DependencyNode] = {}
    
    def add_node(self, node: DependencyNode) -> None:
        """Add node to graph."""
        self.nodes[node.node_id] = node
    
    def add_dependency(
        self,
        from_node: str,
        to_node: str,
        dep_type: DependencyType = DependencyType.REQUIRED
    ) -> None:
        """
        Add dependency: from_node depends on to_node.
        
        Args:
            from_node: Dependent node ID
            to_node: Dependency node ID
            dep_type: Type of dependency
        """
        if from_node not in self.nodes:
            raise ValueError(f"Node {from_node} not in graph")
        if to_node not in self.nodes:
            raise ValueError(f"Node {to_node} not in graph")
        
        self.nodes[from_node].add_dependency(to_node, dep_type)
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node_id: str) -> bool:
            """DFS with cycle detection."""
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            node = self.nodes[node_id]
            for dep_id in node.dependencies:
                if dep_id not in visited:
                    if dfs(dep_id):
                        return True
                elif dep_id in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep_id)
                    cycles.append(path[cycle_start:] + [dep_id])
                    return True
            
            rec_stack.remove(node_id)
            path.pop()
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)
        
        return cycles
    
    def topological_sort(self) -> List[str]:
        """
        Get execution order using Kahn's algorithm.
        
        Returns:
            List of node IDs in execution order
        
        Raises:
            ValueError: If graph has cycles
        """
        # Check for cycles first
        cycles = self.detect_cycles()
        if cycles:
            cycle_str = " -> ".join(cycles[0])
            raise ValueError(f"Circular dependency detected: {cycle_str}")
        
        # Build in-degree map
        in_degree = {node_id: 0 for node_id in self.nodes}
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                if self.nodes[dep_id].dependency_types.get(node.node_id) == DependencyType.REQUIRED:
                    in_degree[node.node_id] += 1
        
        # Find nodes with no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Update in-degrees
            for other_id, other_node in self.nodes.items():
                if node_id in other_node.dependencies:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)
        
        return result
    
    def get_ready_nodes(self, completed_nodes: Set[str]) -> List[str]:
        """
        Get nodes that are ready to execute (all dependencies met).
        
        Args:
            completed_nodes: Set of completed node IDs
        
        Returns:
            List of ready node IDs
        """
        ready = []
        for node_id, node in self.nodes.items():
            if node.status == "not-started":
                is_ready, _ = node.is_ready(completed_nodes)
                if is_ready:
                    ready.append(node_id)
        
        return ready
    
    def get_blocking_nodes(self, node_id: str, completed_nodes: Set[str]) -> List[str]:
        """
        Get nodes blocking execution of specified node.
        
        Args:
            node_id: Node to check
            completed_nodes: Set of completed node IDs
        
        Returns:
            List of blocking node IDs
        """
        if node_id not in self.nodes:
            return []
        
        _, blocking = self.nodes[node_id].is_ready(completed_nodes)
        return blocking
    
    def calculate_critical_path(self, duration_map: Dict[str, float]) -> Tuple[List[str], float]:
        """
        Calculate critical path (longest path through graph).
        
        Args:
            duration_map: Map of node_id -> duration
        
        Returns:
            (critical_path_nodes, total_duration)
        """
        order = self.topological_sort()
        
        # Calculate earliest start times
        earliest_start = {node_id: 0.0 for node_id in self.nodes}
        for node_id in order:
            node = self.nodes[node_id]
            for dep_id in node.dependencies:
                earliest_start[node_id] = max(
                    earliest_start[node_id],
                    earliest_start[dep_id] + duration_map.get(dep_id, 0)
                )
        
        # Find critical path by backtracking from longest duration
        max_duration = max(
            earliest_start[node_id] + duration_map.get(node_id, 0)
            for node_id in self.nodes
        )
        
        # Find node with max finish time
        critical_node = max(
            self.nodes.keys(),
            key=lambda n: earliest_start[n] + duration_map.get(n, 0)
        )
        
        # Backtrack to find critical path
        critical_path = [critical_node]
        current = critical_node
        
        while self.nodes[current].dependencies:
            # Find dependency that determines earliest start
            critical_dep = max(
                self.nodes[current].dependencies,
                key=lambda d: earliest_start[d] + duration_map.get(d, 0)
            )
            critical_path.insert(0, critical_dep)
            current = critical_dep
        
        return (critical_path, max_duration)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate dependency graph.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Check for cycles
        cycles = self.detect_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                errors.append(f"Circular dependency: {cycle_str}")
        
        # Check for missing dependencies
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                if dep_id not in self.nodes:
                    errors.append(
                        f"Node {node.node_id} depends on missing node {dep_id}"
                    )
        
        # Check for self-dependencies
        for node_id, node in self.nodes.items():
            if node_id in node.dependencies:
                errors.append(f"Node {node_id} depends on itself")
        
        return (len(errors) == 0, errors)


class DependencyResolver:
    """
    High-level dependency resolution for orchestrators.
    
    Provides convenience methods for common dependency operations.
    """
    
    @staticmethod
    def create_phase_graph(phases: List[Dict]) -> DependencyGraph:
        """
        Create dependency graph from phase data.
        
        Args:
            phases: List of phase dictionaries with 'phase_number' and 'dependencies'
        
        Returns:
            Configured dependency graph
        """
        graph = DependencyGraph()
        
        # Add all nodes first
        for phase in phases:
            node = DependencyNode(
                node_id=str(phase['phase_number']),
                node_name=phase.get('phase_name', f"Phase {phase['phase_number']}"),
                node_type="phase",
                status=phase.get('status', 'not-started')
            )
            graph.add_node(node)
        
        # Add dependencies
        for phase in phases:
            from_id = str(phase['phase_number'])
            for dep_num in phase.get('dependencies', []):
                graph.add_dependency(from_id, str(dep_num))
        
        return graph
    
    @staticmethod
    def create_plan_graph(plans: List[Dict]) -> DependencyGraph:
        """
        Create dependency graph from plan data.
        
        Args:
            plans: List of plan dictionaries with 'plan_id' and 'dependencies'
        
        Returns:
            Configured dependency graph
        """
        graph = DependencyGraph()
        
        # Add all nodes first
        for plan in plans:
            node = DependencyNode(
                node_id=plan['plan_id'],
                node_name=plan.get('plan_name', plan['plan_id']),
                node_type="plan",
                status=plan.get('status', 'not-started')
            )
            graph.add_node(node)
        
        # Add dependencies
        for plan in plans:
            from_id = plan['plan_id']
            for dep_id in plan.get('dependencies', []):
                graph.add_dependency(from_id, dep_id)
        
        return graph
    
    @staticmethod
    def get_execution_order(
        items: List[Dict],
        id_key: str = 'plan_id',
        dep_key: str = 'dependencies'
    ) -> List[str]:
        """
        Get recommended execution order for items.
        
        Args:
            items: List of items with dependencies
            id_key: Key for item ID
            dep_key: Key for dependencies list
        
        Returns:
            List of item IDs in execution order
        """
        graph = DependencyGraph()
        
        # Add nodes
        for item in items:
            node = DependencyNode(
                node_id=str(item[id_key]),
                node_name=item.get('name', str(item[id_key])),
                node_type="item"
            )
            graph.add_node(node)
        
        # Add dependencies
        for item in items:
            from_id = str(item[id_key])
            for dep_id in item.get(dep_key, []):
                graph.add_dependency(from_id, str(dep_id))
        
        return graph.topological_sort()
