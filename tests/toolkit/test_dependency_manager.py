"""
Tests for DependencyManager - Tool Dependency Graph Management.

Phase 4 of Toolkit Manager Implementation
TDD: RED Phase - Tests written before implementation

Test Categories:
1. Graph building tests
2. Circular dependency detection tests
3. Topological sort tests
4. Dependency validation tests
5. Execution order tests
6. Edge cases and error handling
"""

import pytest
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

# Import classes under test
from core.dependency_manager import (
    DependencyManager,
    DependencyCheck,
    DependencyGraph,
    CircularDependencyError,
    UnmetDependencyError,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_registry():
    """Create a mock registry with tools and dependencies."""
    registry = Mock()
    registry.toolkit_root = Path("/mock/toolkit")
    
    # Define tools with dependencies
    tools = [
        {"name": "core", "description": "Core tool", "depends_on": []},
        {"name": "utils", "description": "Utility functions", "depends_on": ["core"]},
        {"name": "analyzer", "description": "Code analyzer", "depends_on": ["core", "utils"]},
        {"name": "reporter", "description": "Report generator", "depends_on": ["analyzer"]},
        {"name": "standalone", "description": "No dependencies", "depends_on": []},
    ]
    
    registry.list_tools.return_value = tools
    registry.get_tool.side_effect = lambda name: next(
        (t for t in tools if t["name"] == name), None
    )
    
    return registry


@pytest.fixture
def mock_registry_with_circular():
    """Create a mock registry with circular dependencies."""
    registry = Mock()
    registry.toolkit_root = Path("/mock/toolkit")
    
    # A -> B -> C -> A (circular)
    tools = [
        {"name": "tool_a", "description": "Tool A", "depends_on": ["tool_b"]},
        {"name": "tool_b", "description": "Tool B", "depends_on": ["tool_c"]},
        {"name": "tool_c", "description": "Tool C", "depends_on": ["tool_a"]},
    ]
    
    registry.list_tools.return_value = tools
    registry.get_tool.side_effect = lambda name: next(
        (t for t in tools if t["name"] == name), None
    )
    
    return registry


@pytest.fixture
def mock_registry_with_missing():
    """Create a mock registry with missing dependencies."""
    registry = Mock()
    registry.toolkit_root = Path("/mock/toolkit")
    
    tools = [
        {"name": "dependent", "description": "Depends on missing", "depends_on": ["nonexistent"]},
        {"name": "existing", "description": "Existing tool", "depends_on": []},
    ]
    
    registry.list_tools.return_value = tools
    registry.get_tool.side_effect = lambda name: next(
        (t for t in tools if t["name"] == name), None
    )
    
    return registry


@pytest.fixture
def dependency_manager(mock_registry):
    """Create a DependencyManager with mocked registry."""
    return DependencyManager(mock_registry)


# =============================================================================
# 1. DependencyManager Initialization Tests
# =============================================================================

class TestDependencyManagerInit:
    """Tests for DependencyManager initialization."""
    
    def test_manager_initializes_with_registry(self, mock_registry):
        """DependencyManager initializes with ToolkitRegistry."""
        manager = DependencyManager(mock_registry)
        
        assert manager.registry is mock_registry
    
    def test_manager_builds_graph_on_init(self, mock_registry):
        """DependencyManager builds dependency graph on initialization."""
        manager = DependencyManager(mock_registry)
        
        assert manager.graph is not None
        assert isinstance(manager.graph, DependencyGraph)
    
    def test_graph_contains_all_tools(self, mock_registry):
        """Built graph contains all tools from registry."""
        manager = DependencyManager(mock_registry)
        
        tools = manager.graph.get_all_tools()
        assert "core" in tools
        assert "utils" in tools
        assert "analyzer" in tools
        assert "reporter" in tools
        assert "standalone" in tools
    
    def test_graph_captures_dependencies(self, mock_registry):
        """Graph correctly captures tool dependencies."""
        manager = DependencyManager(mock_registry)
        
        deps = manager.graph.get_dependencies("analyzer")
        assert "core" in deps
        assert "utils" in deps
    
    def test_graph_handles_no_dependencies(self, mock_registry):
        """Graph handles tools with no dependencies."""
        manager = DependencyManager(mock_registry)
        
        deps = manager.graph.get_dependencies("standalone")
        assert deps == []


# =============================================================================
# 2. Circular Dependency Detection Tests
# =============================================================================

class TestCircularDependencyDetection:
    """Tests for detecting circular dependencies."""
    
    def test_detects_circular_dependency(self, mock_registry_with_circular):
        """Detects circular dependency chain."""
        manager = DependencyManager(mock_registry_with_circular)
        
        cycles = manager.detect_circular()
        
        assert len(cycles) > 0
    
    def test_returns_cycle_chain(self, mock_registry_with_circular):
        """Returns the actual cycle chain."""
        manager = DependencyManager(mock_registry_with_circular)
        
        cycles = manager.detect_circular()
        
        # Should contain tools in the cycle
        cycle = cycles[0]
        assert "tool_a" in cycle or "tool_b" in cycle or "tool_c" in cycle
    
    def test_no_circular_returns_empty(self, dependency_manager):
        """Returns empty list when no circular dependencies."""
        cycles = dependency_manager.detect_circular()
        
        assert cycles == []
    
    def test_detects_self_reference(self):
        """Detects self-referencing tool (A -> A)."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        registry.list_tools.return_value = [
            {"name": "self_ref", "description": "Self reference", "depends_on": ["self_ref"]},
        ]
        registry.get_tool.return_value = {"name": "self_ref"}
        
        manager = DependencyManager(registry)
        cycles = manager.detect_circular()
        
        assert len(cycles) > 0
        assert "self_ref" in cycles[0]
    
    def test_detects_complex_cycle(self):
        """Detects cycle in larger graph with non-cyclic parts."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        # A -> B -> C -> D -> B (cycle: B-C-D)
        # E -> A (not in cycle)
        registry.list_tools.return_value = [
            {"name": "A", "depends_on": ["B"]},
            {"name": "B", "depends_on": ["C"]},
            {"name": "C", "depends_on": ["D"]},
            {"name": "D", "depends_on": ["B"]},  # Creates cycle
            {"name": "E", "depends_on": ["A"]},  # Not in cycle
        ]
        registry.get_tool.side_effect = lambda n: {"name": n}
        
        manager = DependencyManager(registry)
        cycles = manager.detect_circular()
        
        assert len(cycles) > 0


# =============================================================================
# 3. Dependency Validation Tests
# =============================================================================

class TestDependencyValidation:
    """Tests for validating tool dependencies."""
    
    def test_validate_satisfied_dependencies(self, dependency_manager):
        """Validates when all dependencies are satisfied."""
        check = dependency_manager.validate_dependencies("analyzer")
        
        assert check.satisfied is True
        assert check.missing == []
    
    def test_validate_missing_dependencies(self, mock_registry_with_missing):
        """Detects missing dependencies."""
        manager = DependencyManager(mock_registry_with_missing)
        
        check = manager.validate_dependencies("dependent")
        
        assert check.satisfied is False
        assert "nonexistent" in check.missing
    
    def test_validate_returns_dependency_check(self, dependency_manager):
        """validate_dependencies returns DependencyCheck object."""
        check = dependency_manager.validate_dependencies("utils")
        
        assert isinstance(check, DependencyCheck)
        assert hasattr(check, 'satisfied')
        assert hasattr(check, 'missing')
    
    def test_validate_tool_without_dependencies(self, dependency_manager):
        """Validates tool with no dependencies."""
        check = dependency_manager.validate_dependencies("standalone")
        
        assert check.satisfied is True
        assert check.missing == []
    
    def test_validate_nonexistent_tool(self, dependency_manager):
        """Validates nonexistent tool gracefully."""
        check = dependency_manager.validate_dependencies("nonexistent")
        
        # Should return satisfied=True with empty deps, or handle gracefully
        assert isinstance(check, DependencyCheck)


# =============================================================================
# 4. Execution Order Tests (Topological Sort)
# =============================================================================

class TestExecutionOrder:
    """Tests for computing execution order."""
    
    def test_returns_list(self, dependency_manager):
        """get_execution_order returns a list."""
        order = dependency_manager.get_execution_order(["analyzer"])
        
        assert isinstance(order, list)
    
    def test_dependencies_before_dependents(self, dependency_manager):
        """Dependencies come before tools that depend on them."""
        order = dependency_manager.get_execution_order(["analyzer"])
        
        # core and utils must come before analyzer
        core_idx = order.index("core")
        utils_idx = order.index("utils")
        analyzer_idx = order.index("analyzer")
        
        assert core_idx < analyzer_idx
        assert utils_idx < analyzer_idx
    
    def test_chain_order(self, dependency_manager):
        """Full chain respects transitive dependencies."""
        order = dependency_manager.get_execution_order(["reporter"])
        
        # Order should be: core, utils, analyzer, reporter
        assert order.index("core") < order.index("utils")
        assert order.index("utils") < order.index("analyzer")
        assert order.index("analyzer") < order.index("reporter")
    
    def test_multiple_tools_order(self, dependency_manager):
        """Orders multiple tools correctly."""
        order = dependency_manager.get_execution_order(["reporter", "standalone"])
        
        # Both should be in order, dependencies first
        assert "core" in order
        assert "reporter" in order
        assert "standalone" in order
    
    def test_no_duplicates_in_order(self, dependency_manager):
        """Execution order has no duplicate entries."""
        order = dependency_manager.get_execution_order(["analyzer", "reporter"])
        
        # Both depend on core, should appear only once
        assert order.count("core") == 1
    
    def test_circular_raises_error(self, mock_registry_with_circular):
        """Circular dependency raises error during ordering."""
        manager = DependencyManager(mock_registry_with_circular)
        
        with pytest.raises(CircularDependencyError):
            manager.get_execution_order(["tool_a"])
    
    def test_empty_input_returns_empty(self, dependency_manager):
        """Empty input returns empty order."""
        order = dependency_manager.get_execution_order([])
        
        assert order == []
    
    def test_standalone_tool_returns_self(self, dependency_manager):
        """Tool with no deps returns just itself."""
        order = dependency_manager.get_execution_order(["standalone"])
        
        assert order == ["standalone"]


# =============================================================================
# 5. DependencyGraph Class Tests
# =============================================================================

class TestDependencyGraph:
    """Tests for the DependencyGraph data structure."""
    
    def test_graph_creation(self):
        """DependencyGraph can be created."""
        graph = DependencyGraph()
        
        assert graph is not None
    
    def test_add_tool(self):
        """Can add tool to graph."""
        graph = DependencyGraph()
        graph.add_tool("test_tool", ["dep1", "dep2"])
        
        assert "test_tool" in graph.get_all_tools()
    
    def test_get_dependencies(self):
        """Can retrieve tool dependencies."""
        graph = DependencyGraph()
        graph.add_tool("child", ["parent1", "parent2"])
        
        deps = graph.get_dependencies("child")
        
        assert "parent1" in deps
        assert "parent2" in deps
    
    def test_get_dependents(self):
        """Can retrieve tools that depend on a tool."""
        graph = DependencyGraph()
        graph.add_tool("parent", [])
        graph.add_tool("child1", ["parent"])
        graph.add_tool("child2", ["parent"])
        
        dependents = graph.get_dependents("parent")
        
        assert "child1" in dependents
        assert "child2" in dependents
    
    def test_has_dependencies(self):
        """Check if tool has dependencies."""
        graph = DependencyGraph()
        graph.add_tool("with_deps", ["dep"])
        graph.add_tool("no_deps", [])
        
        assert graph.has_dependencies("with_deps") is True
        assert graph.has_dependencies("no_deps") is False
    
    def test_get_all_tools(self):
        """Get all tools in graph."""
        graph = DependencyGraph()
        graph.add_tool("a", [])
        graph.add_tool("b", ["a"])
        
        tools = graph.get_all_tools()
        
        assert len(tools) == 2
        assert "a" in tools
        assert "b" in tools


# =============================================================================
# 6. DependencyCheck Dataclass Tests
# =============================================================================

class TestDependencyCheck:
    """Tests for DependencyCheck result object."""
    
    def test_check_creation(self):
        """DependencyCheck can be created."""
        check = DependencyCheck(satisfied=True, missing=[])
        
        assert check.satisfied is True
        assert check.missing == []
    
    def test_check_with_missing(self):
        """DependencyCheck with missing dependencies."""
        check = DependencyCheck(
            satisfied=False,
            missing=["missing_a", "missing_b"]
        )
        
        assert check.satisfied is False
        assert len(check.missing) == 2
    
    def test_check_has_required_fields(self):
        """DependencyCheck has required fields."""
        check = DependencyCheck(satisfied=True, missing=[])
        
        assert hasattr(check, 'satisfied')
        assert hasattr(check, 'missing')
    
    def test_check_optional_fields(self):
        """DependencyCheck can have optional fields."""
        check = DependencyCheck(
            satisfied=True,
            missing=[],
            tool="test_tool",
            dependencies=["dep1", "dep2"]
        )
        
        assert check.tool == "test_tool"
        assert check.dependencies == ["dep1", "dep2"]


# =============================================================================
# 7. Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_registry(self):
        """Handles empty registry."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        registry.list_tools.return_value = []
        
        manager = DependencyManager(registry)
        
        assert manager.graph.get_all_tools() == []
    
    def test_tool_without_depends_on_field(self):
        """Handles tools without depends_on field."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        registry.list_tools.return_value = [
            {"name": "no_deps_field", "description": "Missing depends_on"},
        ]
        registry.get_tool.return_value = {"name": "no_deps_field"}
        
        manager = DependencyManager(registry)
        
        deps = manager.graph.get_dependencies("no_deps_field")
        assert deps == []
    
    def test_rebuild_graph(self, dependency_manager):
        """Can rebuild graph after changes."""
        dependency_manager.rebuild_graph()
        
        # Should still work
        assert dependency_manager.graph is not None
    
    def test_diamond_dependency(self):
        """Handles diamond dependency pattern."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        #       A
        #      / \
        #     B   C
        #      \ /
        #       D
        registry.list_tools.return_value = [
            {"name": "A", "depends_on": []},
            {"name": "B", "depends_on": ["A"]},
            {"name": "C", "depends_on": ["A"]},
            {"name": "D", "depends_on": ["B", "C"]},
        ]
        registry.get_tool.side_effect = lambda n: {"name": n}
        
        manager = DependencyManager(registry)
        order = manager.get_execution_order(["D"])
        
        # A must come before B and C, which must come before D
        a_idx = order.index("A")
        b_idx = order.index("B")
        c_idx = order.index("C")
        d_idx = order.index("D")
        
        assert a_idx < b_idx
        assert a_idx < c_idx
        assert b_idx < d_idx
        assert c_idx < d_idx
    
    def test_deep_dependency_chain(self):
        """Handles deep dependency chains."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        # Chain: t0 -> t1 -> t2 -> t3 -> t4 -> t5
        tools = []
        for i in range(6):
            deps = [f"t{i-1}"] if i > 0 else []
            tools.append({"name": f"t{i}", "depends_on": deps})
        
        registry.list_tools.return_value = tools
        registry.get_tool.side_effect = lambda n: {"name": n}
        
        manager = DependencyManager(registry)
        order = manager.get_execution_order(["t5"])
        
        # All should be in order
        for i in range(5):
            assert order.index(f"t{i}") < order.index(f"t{i+1}")
    
    def test_unmet_dependency_error(self, mock_registry_with_missing):
        """Can raise UnmetDependencyError when appropriate."""
        manager = DependencyManager(mock_registry_with_missing)
        
        with pytest.raises(UnmetDependencyError):
            manager.get_execution_order(["dependent"], strict=True)
    
    def test_isolated_components(self):
        """Handles multiple isolated dependency components."""
        registry = Mock()
        registry.toolkit_root = Path("/mock/toolkit")
        # Two separate components:
        # A -> B
        # C -> D
        registry.list_tools.return_value = [
            {"name": "A", "depends_on": []},
            {"name": "B", "depends_on": ["A"]},
            {"name": "C", "depends_on": []},
            {"name": "D", "depends_on": ["C"]},
        ]
        registry.get_tool.side_effect = lambda n: {"name": n}
        
        manager = DependencyManager(registry)
        
        # Order B and D together
        order = manager.get_execution_order(["B", "D"])
        
        # A before B, C before D
        assert order.index("A") < order.index("B")
        assert order.index("C") < order.index("D")


# =============================================================================
# 8. Integration with ToolkitManager Tests
# =============================================================================

class TestIntegrationWithManager:
    """Tests for integration with ToolkitManager."""
    
    def test_manager_can_check_dependencies(self, dependency_manager):
        """Manager provides dependency check method."""
        check = dependency_manager.can_execute("reporter")
        
        assert isinstance(check, DependencyCheck)
    
    def test_get_all_dependencies_transitive(self, dependency_manager):
        """Gets all transitive dependencies."""
        all_deps = dependency_manager.get_all_dependencies("reporter")
        
        # reporter -> analyzer -> [core, utils] -> core
        assert "analyzer" in all_deps
        assert "core" in all_deps
        assert "utils" in all_deps
    
    def test_dependency_depth(self, dependency_manager):
        """Can calculate dependency depth."""
        depth = dependency_manager.get_dependency_depth("reporter")
        
        # reporter(3) -> analyzer(2) -> utils(1) -> core(0)
        assert depth >= 3
    
    def test_get_dependency_tree(self, dependency_manager):
        """Can get tree representation of dependencies."""
        tree = dependency_manager.get_dependency_tree("reporter")
        
        assert tree is not None
        assert isinstance(tree, dict)
        assert "reporter" in tree
