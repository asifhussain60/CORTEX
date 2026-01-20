"""
Tests for AC-GC-004-01: Dependency Resolution via DAG Builder

AC-GC-004-01: Dependency Resolution
- Build directed acyclic graph (DAG) from rule dependencies
- Topological sort: evaluable rule ordering
- Detect cycles: prevent invalid dependency graphs
- Transitive closure: compute all indirect dependencies
- Isolation levels: evaluate subsets in topological order
- Performance: O(V+E) for DAG construction, O(V+E) for sort

CORE Governance Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class RuleNode:
    """Represents a rule in dependency graph."""
    rule_id: str
    dependencies: Set[str] = field(default_factory=set)
    
    def add_dependency(self, dep_id: str) -> None:
        """Add dependency."""
        self.dependencies.add(dep_id)


class DAGBuilder:
    """
    Builds directed acyclic graph from rule dependencies.
    
    Detects cycles, computes topological order, and transitive closure.
    """
    
    def __init__(self) -> None:
        """Initialize DAG builder."""
        self._nodes: Dict[str, RuleNode] = {}
        self._adj_list: Dict[str, Set[str]] = {}
    
    def add_rule(self, rule_id: str) -> None:
        """
        Add rule to graph.
        
        Args:
            rule_id: Unique rule identifier
        """
        if rule_id not in self._nodes:
            self._nodes[rule_id] = RuleNode(rule_id)
            self._adj_list[rule_id] = set()
    
    def add_dependency(self, rule_id: str, depends_on: str) -> None:
        """
        Add dependency edge.
        
        Args:
            rule_id: Rule that has dependency
            depends_on: Rule it depends on
        """
        self.add_rule(rule_id)
        self.add_rule(depends_on)
        
        self._nodes[rule_id].add_dependency(depends_on)
        self._adj_list[rule_id].add(depends_on)
    
    def get_dependencies(self, rule_id: str) -> Set[str]:
        """
        Get direct dependencies.
        
        Args:
            rule_id: Rule ID
        
        Returns:
            Set of direct dependencies
        """
        if rule_id not in self._nodes:
            return set()
        return self._nodes[rule_id].dependencies.copy()
    
    def has_cycle(self) -> bool:
        """
        Detect if DAG has cycles.
        
        Returns:
            True if cycle detected
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        for node_id in self._nodes:
            if node_id not in visited:
                if self._has_cycle_dfs(node_id, visited, rec_stack):
                    return True
        
        return False
    
    def _has_cycle_dfs(
        self,
        node_id: str,
        visited: Set[str],
        rec_stack: Set[str]
    ) -> bool:
        """DFS for cycle detection."""
        visited.add(node_id)
        rec_stack.add(node_id)
        
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                if self._has_cycle_dfs(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node_id)
        return False
    
    def topological_sort(self) -> List[str]:
        """
        Get topological ordering of rules.
        
        Returns:
            List of rule IDs in evaluation order
        
        Raises:
            ValueError: If cycle detected
        """
        if self.has_cycle():
            raise ValueError("Cycle detected in dependency graph")
        
        visited: Set[str] = set()
        stack: List[str] = []
        
        for node_id in self._nodes:
            if node_id not in visited:
                self._topological_sort_dfs(node_id, visited, stack)
        
        return stack
    
    def _topological_sort_dfs(
        self,
        node_id: str,
        visited: Set[str],
        stack: List[str]
    ) -> None:
        """DFS for topological sort."""
        visited.add(node_id)
        
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                self._topological_sort_dfs(neighbor, visited, stack)
        
        stack.append(node_id)
    
    def get_transitive_closure(self, rule_id: str) -> Set[str]:
        """
        Get all transitive dependencies.
        
        Args:
            rule_id: Rule ID
        
        Returns:
            Set of all direct and indirect dependencies
        """
        visited: Set[str] = set()
        self._get_transitive_closure_dfs(rule_id, visited)
        return visited
    
    def _get_transitive_closure_dfs(
        self,
        node_id: str,
        visited: Set[str]
    ) -> None:
        """DFS for transitive closure."""
        for neighbor in self._adj_list.get(node_id, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                self._get_transitive_closure_dfs(neighbor, visited)
    
    def get_isolation_group(self, rule_ids: Set[str]) -> List[str]:
        """
        Get evaluation order for subset of rules.
        
        Args:
            rule_ids: Set of rule IDs to evaluate
        
        Returns:
            Topological order for subset
        """
        # Filter graph to subset
        subset_visited: Set[str] = set()
        
        def filter_dfs(rule_id: str) -> None:
            subset_visited.add(rule_id)
            for dep in self._adj_list.get(rule_id, set()):
                if dep not in subset_visited:
                    filter_dfs(dep)
        
        for rule_id in rule_ids:
            if rule_id not in subset_visited:
                filter_dfs(rule_id)
        
        # Topological sort of subset
        visited: Set[str] = set()
        stack: List[str] = []
        
        def subset_sort_dfs(node_id: str) -> None:
            visited.add(node_id)
            for neighbor in self._adj_list.get(node_id, set()):
                if neighbor in subset_visited and neighbor not in visited:
                    subset_sort_dfs(neighbor)
            stack.append(node_id)
        
        for rule_id in subset_visited:
            if rule_id not in visited:
                subset_sort_dfs(rule_id)
        
        return stack
    
    def rule_count(self) -> int:
        """Get number of rules in DAG."""
        return len(self._nodes)
    
    def edge_count(self) -> int:
        """Get number of dependency edges."""
        return sum(len(deps) for deps in self._adj_list.values())


class TestRuleNode:
    """Tests for RuleNode dataclass."""
    
    def test_node_creation(self) -> None:
        """Test creating rule node."""
        node = RuleNode("CORE-008")
        assert node.rule_id == "CORE-008"
        assert len(node.dependencies) == 0
    
    def test_add_dependency(self) -> None:
        """Test adding dependency."""
        node = RuleNode("CORE-008")
        node.add_dependency("CORE-011")
        assert "CORE-011" in node.dependencies


class TestDAGBuilderBasic:
    """Tests for basic DAGBuilder functionality."""
    
    @pytest.fixture
    def builder(self) -> DAGBuilder:
        """Create builder fixture."""
        return DAGBuilder()
    
    def test_builder_initialization(self, builder: DAGBuilder) -> None:
        """Test builder initializes empty."""
        assert builder.rule_count() == 0
        assert builder.edge_count() == 0
    
    def test_add_single_rule(self, builder: DAGBuilder) -> None:
        """Test adding single rule."""
        builder.add_rule("CORE-008")
        assert builder.rule_count() == 1
    
    def test_add_dependency(self, builder: DAGBuilder) -> None:
        """Test adding dependency edge."""
        builder.add_dependency("CORE-008", "CORE-011")
        assert builder.rule_count() == 2
        assert builder.edge_count() == 1
    
    def test_get_dependencies(self, builder: DAGBuilder) -> None:
        """Test retrieving dependencies."""
        builder.add_dependency("CORE-008", "CORE-011")
        builder.add_dependency("CORE-008", "CORE-012")
        deps = builder.get_dependencies("CORE-008")
        assert len(deps) == 2
        assert "CORE-011" in deps
        assert "CORE-012" in deps


class TestCycleDetection:
    """Tests for cycle detection."""
    
    @pytest.fixture
    def builder(self) -> DAGBuilder:
        """Create builder fixture."""
        return DAGBuilder()
    
    def test_no_cycle_linear(self, builder: DAGBuilder) -> None:
        """Test linear dependency chain has no cycle."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "C")
        builder.add_dependency("C", "D")
        assert builder.has_cycle() is False
    
    def test_no_cycle_tree(self, builder: DAGBuilder) -> None:
        """Test tree structure has no cycle."""
        builder.add_dependency("A", "B")
        builder.add_dependency("A", "C")
        builder.add_dependency("B", "D")
        builder.add_dependency("C", "D")
        assert builder.has_cycle() is False
    
    def test_direct_cycle(self, builder: DAGBuilder) -> None:
        """Test direct cycle detected."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "A")
        assert builder.has_cycle() is True
    
    def test_self_loop(self, builder: DAGBuilder) -> None:
        """Test self-loop detected."""
        builder.add_dependency("A", "A")
        assert builder.has_cycle() is True
    
    def test_indirect_cycle(self, builder: DAGBuilder) -> None:
        """Test indirect cycle detected."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "C")
        builder.add_dependency("C", "A")
        assert builder.has_cycle() is True
    
    def test_complex_cycle(self, builder: DAGBuilder) -> None:
        """Test complex cycle in DAG."""
        builder.add_dependency("A", "B")
        builder.add_dependency("A", "C")
        builder.add_dependency("B", "D")
        builder.add_dependency("C", "D")
        builder.add_dependency("D", "B")  # Creates cycle
        assert builder.has_cycle() is True


class TestTopologicalSort:
    """Tests for topological sorting."""
    
    @pytest.fixture
    def builder(self) -> DAGBuilder:
        """Create builder fixture."""
        return DAGBuilder()
    
    def test_sort_empty_graph(self, builder: DAGBuilder) -> None:
        """Test sorting empty graph."""
        order = builder.topological_sort()
        assert len(order) == 0
    
    def test_sort_single_node(self, builder: DAGBuilder) -> None:
        """Test sorting single node."""
        builder.add_rule("A")
        order = builder.topological_sort()
        assert order == ["A"]
    
    def test_sort_linear_chain(self, builder: DAGBuilder) -> None:
        """Test sorting linear dependency chain."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "C")
        order = builder.topological_sort()
        
        # C should come before B, B before A
        assert order.index("C") < order.index("B")
        assert order.index("B") < order.index("A")
    
    def test_sort_tree(self, builder: DAGBuilder) -> None:
        """Test sorting tree structure."""
        builder.add_dependency("A", "B")
        builder.add_dependency("A", "C")
        builder.add_dependency("B", "D")
        order = builder.topological_sort()
        
        # D before B, B before A, C before A
        assert order.index("D") < order.index("B")
        assert order.index("B") < order.index("A")
        assert order.index("C") < order.index("A")
    
    def test_sort_with_cycle_raises(self, builder: DAGBuilder) -> None:
        """Test sort raises error on cycle."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "A")
        
        with pytest.raises(ValueError):
            builder.topological_sort()


class TestTransitiveClosure:
    """Tests for transitive closure computation."""
    
    @pytest.fixture
    def builder(self) -> DAGBuilder:
        """Create builder fixture."""
        return DAGBuilder()
    
    def test_direct_dependency_only(self, builder: DAGBuilder) -> None:
        """Test rule with direct dependency only."""
        builder.add_dependency("A", "B")
        closure = builder.get_transitive_closure("A")
        assert closure == {"B"}
    
    def test_transitive_chain(self, builder: DAGBuilder) -> None:
        """Test transitive closure in chain."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "C")
        builder.add_dependency("C", "D")
        closure = builder.get_transitive_closure("A")
        assert closure == {"B", "C", "D"}
    
    def test_multiple_paths(self, builder: DAGBuilder) -> None:
        """Test transitive closure with multiple paths."""
        builder.add_dependency("A", "B")
        builder.add_dependency("A", "C")
        builder.add_dependency("B", "D")
        builder.add_dependency("C", "D")
        closure = builder.get_transitive_closure("A")
        assert closure == {"B", "C", "D"}
    
    def test_no_dependencies(self, builder: DAGBuilder) -> None:
        """Test rule with no dependencies."""
        builder.add_rule("A")
        closure = builder.get_transitive_closure("A")
        assert closure == set()


class TestIsolationGroups:
    """Tests for isolation group evaluation."""
    
    @pytest.fixture
    def builder(self) -> DAGBuilder:
        """Create builder fixture."""
        return DAGBuilder()
    
    def test_isolation_single_rule(self, builder: DAGBuilder) -> None:
        """Test isolation group with single rule."""
        builder.add_rule("A")
        order = builder.get_isolation_group({"A"})
        assert order == ["A"]
    
    def test_isolation_subset_with_deps(self, builder: DAGBuilder) -> None:
        """Test isolation group includes dependencies."""
        builder.add_dependency("A", "B")
        builder.add_dependency("B", "C")
        builder.add_dependency("C", "D")
        builder.add_dependency("D", "E")
        
        # Requesting A should include all its dependencies
        order = builder.get_isolation_group({"A"})
        assert set(order) == {"A", "B", "C", "D", "E"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
