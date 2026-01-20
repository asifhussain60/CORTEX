"""
Implementation of AC-GC-004-01: Dependency Resolution via DAG Builder

Builds directed acyclic graph (DAG) from rule dependencies with:
- Cycle detection: Prevent invalid dependency graphs
- Topological sorting: Determine evaluable rule ordering
- Transitive closure: Compute all direct and indirect dependencies
- Isolation levels: Evaluate subsets in topological order
- O(V+E) performance for all operations

Used by composite evaluator to determine rule evaluation sequence while
respecting dependency constraints.

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class RuleNode:
    """
    Represents a rule in dependency graph.
    
    Attributes:
        rule_id: Unique rule identifier
        dependencies: Set of rules this rule depends on
    """
    rule_id: str
    dependencies: Set[str] = field(default_factory=set)
    
    def add_dependency(self, dep_id: str) -> None:
        """
        Add dependency on another rule.
        
        Args:
            dep_id: Rule ID to depend on
        """
        self.dependencies.add(dep_id)
    
    def remove_dependency(self, dep_id: str) -> None:
        """
        Remove dependency.
        
        Args:
            dep_id: Rule ID to stop depending on
        """
        self.dependencies.discard(dep_id)


class DAGBuilder:
    """
    Builds directed acyclic graph from rule dependencies.
    
    Core operations:
    - Add rules and dependencies
    - Detect cycles (prevents invalid graphs)
    - Topological sort (evaluation ordering)
    - Transitive closure (all direct/indirect dependencies)
    - Isolation groups (evaluate subsets consistently)
    
    All operations are O(V+E) where V=rules, E=dependencies.
    Used by composite evaluator to determine rule evaluation sequence.
    """
    
    def __init__(self) -> None:
        """Initialize empty DAG."""
        self._nodes: Dict[str, RuleNode] = {}
        self._adj_list: Dict[str, Set[str]] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def add_rule(self, rule_id: str) -> None:
        """
        Add rule to graph.
        
        Args:
            rule_id: Unique rule identifier
        """
        if rule_id not in self._nodes:
            self._nodes[rule_id] = RuleNode(rule_id)
            self._adj_list[rule_id] = set()
            self._logger.debug(f"Added rule: {rule_id}")
    
    def add_dependency(self, rule_id: str, depends_on: str) -> None:
        """
        Add dependency edge (rule_id depends on depends_on).
        
        Creates both nodes if needed. Logs all edges to audit trail.
        
        Args:
            rule_id: Rule that has dependency
            depends_on: Rule it depends on
        """
        # Ensure both nodes exist
        self.add_rule(rule_id)
        self.add_rule(depends_on)
        
        # Add edge
        self._nodes[rule_id].add_dependency(depends_on)
        self._adj_list[rule_id].add(depends_on)
        
        self._logger.debug(
            f"Added dependency: {rule_id} → {depends_on}",
            extra={"from_rule": rule_id, "to_rule": depends_on}
        )
    
    def remove_dependency(self, rule_id: str, depends_on: str) -> None:
        """
        Remove dependency edge.
        
        Args:
            rule_id: Rule with dependency
            depends_on: Rule to stop depending on
        """
        if rule_id in self._nodes and depends_on in self._nodes[rule_id].dependencies:
            self._nodes[rule_id].remove_dependency(depends_on)
            self._adj_list[rule_id].discard(depends_on)
            self._logger.debug(
                f"Removed dependency: {rule_id} → {depends_on}"
            )
    
    def get_dependencies(self, rule_id: str) -> Set[str]:
        """
        Get direct dependencies of rule (O(1)).
        
        Args:
            rule_id: Rule ID
        
        Returns:
            Set of direct dependencies (copied)
        """
        if rule_id not in self._nodes:
            return set()
        return self._nodes[rule_id].dependencies.copy()
    
    def has_cycle(self) -> bool:
        """
        Detect if DAG contains cycles using DFS.
        
        Returns:
            True if cycle detected, False otherwise
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        for node_id in self._nodes:
            if node_id not in visited:
                if self._has_cycle_dfs(node_id, visited, rec_stack):
                    self._logger.error(f"Cycle detected in DAG")
                    return True
        
        return False
    
    def _has_cycle_dfs(
        self,
        node_id: str,
        visited: Set[str],
        rec_stack: Set[str]
    ) -> bool:
        """
        DFS helper for cycle detection.
        
        Uses recursion stack to detect back edges.
        
        Args:
            node_id: Current node in traversal
            visited: Set of visited nodes
            rec_stack: Current recursion stack
        
        Returns:
            True if cycle found
        """
        visited.add(node_id)
        rec_stack.add(node_id)
        
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                if self._has_cycle_dfs(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                # Back edge found (cycle)
                return True
        
        rec_stack.remove(node_id)
        return False
    
    def topological_sort(self) -> List[str]:
        """
        Get topological ordering of all rules (O(V+E)).
        
        Returns rules in dependency order: rules with no dependencies
        come first, followed by rules that depend only on earlier rules.
        
        Returns:
            List of rule IDs in topological order
        
        Raises:
            ValueError: If cycle detected in DAG
        """
        if self.has_cycle():
            raise ValueError("Cannot sort: cycle detected in dependency graph")
        
        visited: Set[str] = set()
        stack: List[str] = []
        
        for node_id in self._nodes:
            if node_id not in visited:
                self._topological_sort_dfs(node_id, visited, stack)
        
        self._logger.info(
            f"Topological sort complete: {len(stack)} rules",
            extra={"rule_count": len(stack)}
        )
        return stack
    
    def _topological_sort_dfs(
        self,
        node_id: str,
        visited: Set[str],
        stack: List[str]
    ) -> None:
        """
        DFS helper for topological sort (post-order).
        
        Args:
            node_id: Current node
            visited: Set of visited nodes
            stack: Output stack (post-order)
        """
        visited.add(node_id)
        
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                self._topological_sort_dfs(neighbor, visited, stack)
        
        stack.append(node_id)
    
    def get_transitive_closure(self, rule_id: str) -> Set[str]:
        """
        Get all transitive dependencies (O(V+E)).
        
        Includes both direct and indirect dependencies.
        
        Args:
            rule_id: Rule ID
        
        Returns:
            Set of all rules this rule depends on (direct and indirect)
        """
        visited: Set[str] = set()
        self._get_transitive_closure_dfs(rule_id, visited)
        
        self._logger.debug(
            f"Transitive closure for {rule_id}: {len(visited)} dependencies",
            extra={"rule_id": rule_id, "dependency_count": len(visited)}
        )
        return visited
    
    def _get_transitive_closure_dfs(
        self,
        node_id: str,
        visited: Set[str]
    ) -> None:
        """
        DFS helper for transitive closure.
        
        Args:
            node_id: Current node
            visited: Set of visited nodes (accumulates)
        """
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                self._get_transitive_closure_dfs(neighbor, visited)
    
    def get_isolation_group(self, rule_ids: Set[str]) -> List[str]:
        """
        Get evaluation order for subset of rules (O(V+E)).
        
        Automatically includes all transitive dependencies of rules in subset.
        Returns topological order of expanded subset.
        
        Args:
            rule_ids: Set of rule IDs to evaluate
        
        Returns:
            Topological order for subset and dependencies
        """
        # Collect all transitive dependencies
        subset_visited: Set[str] = set()
        
        def collect_dependencies(rule_id: str) -> None:
            """Collect this rule and all its dependencies."""
            if rule_id in subset_visited:
                return
            subset_visited.add(rule_id)
            for dep in self._adj_list.get(rule_id, set()):
                collect_dependencies(dep)
        
        for rule_id in rule_ids:
            collect_dependencies(rule_id)
        
        # Topological sort of subset
        visited: Set[str] = set()
        stack: List[str] = []
        
        def subset_topo_dfs(node_id: str) -> None:
            """Sort only rules in subset."""
            if node_id in visited:
                return
            visited.add(node_id)
            for neighbor in self._adj_list.get(node_id, set()):
                if neighbor in subset_visited:
                    subset_topo_dfs(neighbor)
            stack.append(node_id)
        
        for rule_id in subset_visited:
            subset_topo_dfs(rule_id)
        
        self._logger.info(
            f"Isolation group evaluation order: {len(stack)} rules from {len(rule_ids)} requested",
            extra={"requested_count": len(rule_ids), "total_count": len(stack)}
        )
        return stack
    
    def rule_count(self) -> int:
        """
        Get total number of rules in DAG.
        
        Returns:
            Count of rules
        """
        return len(self._nodes)
    
    def edge_count(self) -> int:
        """
        Get total number of dependency edges.
        
        Returns:
            Count of dependencies
        """
        return sum(len(deps) for deps in self._adj_list.values())
    
    def get_all_rules(self) -> Set[str]:
        """
        Get all rule IDs in DAG.
        
        Returns:
            Set of all rule IDs
        """
        return set(self._nodes.keys())
    
    def get_roots(self) -> Set[str]:
        """
        Get rules with no dependencies (can evaluate first).
        
        Returns:
            Set of root rule IDs
        """
        return {
            rule_id for rule_id in self._nodes
            if len(self._nodes[rule_id].dependencies) == 0
        }
    
    def get_leaves(self) -> Set[str]:
        """
        Get rules that nothing else depends on.
        
        Returns:
            Set of leaf rule IDs
        """
        all_dependencies = set()
        for deps in self._adj_list.values():
            all_dependencies.update(deps)
        
        return {
            rule_id for rule_id in self._nodes
            if rule_id not in all_dependencies
        }
    
    def get_graph_stats(self) -> Dict[str, int]:
        """
        Get DAG statistics.
        
        Returns:
            Dictionary with rule_count, edge_count, roots_count, leaves_count
        """
        return {
            "rule_count": self.rule_count(),
            "edge_count": self.edge_count(),
            "roots_count": len(self.get_roots()),
            "leaves_count": len(self.get_leaves())
        }
    
    def clear(self) -> None:
        """Clear entire DAG."""
        self._nodes.clear()
        self._adj_list.clear()
        self._logger.info("DAG cleared")
