# ==============================================================================
# CORTEX 6.0 - DAG Unit Tests
# ==============================================================================
# Author: Asif Hussain
# Version: 6.0.0
# TDD Phase: RED → GREEN
# ==============================================================================

"""
Comprehensive unit tests for DAG (Directed Acyclic Graph) implementation.

Test Categories:
1. Node Operations - add, remove, update, get
2. Edge Operations - add, remove, dependencies
3. Cycle Detection - DFS-based validation
4. Topological Sort - Kahn's algorithm
5. Ready Tasks - Execution scheduling
6. Statistics - DAG metrics
7. Serialization - JSON import/export
8. Edge Cases - Empty DAG, single node, etc.
9. Thread Safety - Concurrent operations
10. Performance - O(1) guarantees
"""

import pytest
import json
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from src.orchestrators.core.dag import (
    DAG,
    DAGNode,
    DAGEdge,
    DAGStatistics,
    NodeStatus,
    EdgeType,
    Priority,
    DAGError,
    DAGValidationError,
    CyclicDependencyError,
    NodeNotFoundError,
    EdgeNotFoundError,
    DuplicateNodeError,
    InvalidTransitionError,
)


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def empty_dag():
    """Create an empty DAG."""
    return DAG(name="test-dag")


@pytest.fixture
def simple_dag():
    """Create a simple DAG with 3 nodes in sequence: A → B → C."""
    dag = DAG(name="simple")
    dag.add_node("A", name="Task A")
    dag.add_node("B", name="Task B")
    dag.add_node("C", name="Task C")
    dag.add_edge("A", "B")
    dag.add_edge("B", "C")
    return dag


@pytest.fixture
def diamond_dag():
    """
    Create a diamond DAG:
        A
       / \
      B   C
       \ /
        D
    """
    dag = DAG(name="diamond")
    dag.add_node("A")
    dag.add_node("B")
    dag.add_node("C")
    dag.add_node("D")
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("C", "D")
    return dag


@pytest.fixture
def complex_dag():
    """
    Create a more complex DAG with multiple paths:
        A → B → D
        ↓   ↓
        C → E → F
    """
    dag = DAG(name="complex")
    for node_id in ["A", "B", "C", "D", "E", "F"]:
        dag.add_node(node_id)
    
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("B", "E")
    dag.add_edge("C", "E")
    dag.add_edge("E", "F")
    
    return dag


# ==============================================================================
# TEST CLASS: Node Operations
# ==============================================================================


class TestNodeOperations:
    """Tests for DAG node operations."""
    
    def test_add_node_basic(self, empty_dag):
        """Test adding a basic node."""
        node = empty_dag.add_node("task1", name="First Task")
        
        assert node.id == "task1"
        assert node.name == "First Task"
        assert node.status == NodeStatus.NOT_STARTED
        assert empty_dag.node_count == 1
    
    def test_add_node_with_data(self, empty_dag):
        """Test adding a node with custom data."""
        data = {"description": "Test task", "estimate": 60}
        node = empty_dag.add_node("task1", data=data)
        
        assert node.data == data
        assert node.data["description"] == "Test task"
    
    def test_add_node_with_priority(self, empty_dag):
        """Test adding a node with priority."""
        node = empty_dag.add_node("task1", priority=Priority.P0_CRITICAL)
        
        assert node.priority == Priority.P0_CRITICAL
    
    def test_add_node_with_tags(self, empty_dag):
        """Test adding a node with tags."""
        tags = {"backend", "database"}
        node = empty_dag.add_node("task1", tags=tags)
        
        assert node.tags == tags
        assert "backend" in node.tags
    
    def test_add_duplicate_node_raises(self, empty_dag):
        """Test that adding duplicate node raises error."""
        empty_dag.add_node("task1")
        
        with pytest.raises(DuplicateNodeError) as exc:
            empty_dag.add_node("task1")
        
        assert "task1" in str(exc.value)
    
    def test_get_node(self, simple_dag):
        """Test getting a node by ID."""
        node = simple_dag.get_node("A")
        
        assert node.id == "A"
        assert node.name == "Task A"
    
    def test_get_nonexistent_node_raises(self, empty_dag):
        """Test getting nonexistent node raises error."""
        with pytest.raises(NodeNotFoundError) as exc:
            empty_dag.get_node("nonexistent")
        
        assert "nonexistent" in str(exc.value)
    
    def test_has_node(self, simple_dag):
        """Test checking node existence."""
        assert simple_dag.has_node("A")
        assert not simple_dag.has_node("Z")
    
    def test_remove_node(self, simple_dag):
        """Test removing a node."""
        initial_count = simple_dag.node_count
        removed = simple_dag.remove_node("B")
        
        assert removed.id == "B"
        assert simple_dag.node_count == initial_count - 1
        assert not simple_dag.has_node("B")
        # Edges should also be removed
        assert not simple_dag.has_edge("A", "B")
        assert not simple_dag.has_edge("B", "C")
    
    def test_remove_nonexistent_node_raises(self, empty_dag):
        """Test removing nonexistent node raises error."""
        with pytest.raises(NodeNotFoundError):
            empty_dag.remove_node("nonexistent")
    
    def test_update_node(self, simple_dag):
        """Test updating node properties."""
        updated = simple_dag.update_node(
            "A",
            name="Updated Task A",
            data={"new_key": "value"},
            priority=Priority.P1_HIGH
        )
        
        assert updated.name == "Updated Task A"
        assert updated.data.get("new_key") == "value"
        assert updated.priority == Priority.P1_HIGH
    
    def test_update_node_merges_data(self, empty_dag):
        """Test that update merges data instead of replacing."""
        empty_dag.add_node("task1", data={"key1": "value1"})
        empty_dag.update_node("task1", data={"key2": "value2"})
        
        node = empty_dag.get_node("task1")
        assert node.data == {"key1": "value1", "key2": "value2"}
    
    def test_node_status_transitions(self, simple_dag):
        """Test valid node status transitions."""
        # NOT_STARTED → IN_PROGRESS
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        assert simple_dag.get_node("A").status == NodeStatus.IN_PROGRESS
        
        # IN_PROGRESS → COMPLETED
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        assert simple_dag.get_node("A").status == NodeStatus.COMPLETED
    
    def test_invalid_status_transition_raises(self, simple_dag):
        """Test that invalid status transition raises error."""
        # NOT_STARTED → COMPLETED is invalid (must go through IN_PROGRESS)
        with pytest.raises(InvalidTransitionError):
            simple_dag.set_node_status("A", NodeStatus.COMPLETED)
    
    def test_node_start_sets_timestamp(self, simple_dag):
        """Test that starting a node sets started_at timestamp."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        node = simple_dag.get_node("A")
        
        assert node.started_at is not None
        assert isinstance(node.started_at, datetime)
    
    def test_node_complete_sets_timestamp(self, simple_dag):
        """Test that completing a node sets completed_at timestamp."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        node = simple_dag.get_node("A")
        
        assert node.completed_at is not None
        assert node.completed_at >= node.started_at


# ==============================================================================
# TEST CLASS: Edge Operations
# ==============================================================================


class TestEdgeOperations:
    """Tests for DAG edge operations."""
    
    def test_add_edge_basic(self, empty_dag):
        """Test adding a basic edge."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        edge = empty_dag.add_edge("A", "B")
        
        assert edge.source == "A"
        assert edge.target == "B"
        assert empty_dag.edge_count == 1
    
    def test_add_edge_with_type(self, empty_dag):
        """Test adding edge with specific type."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        edge = empty_dag.add_edge("A", "B", edge_type=EdgeType.SOFT_DEPENDENCY)
        
        assert edge.edge_type == EdgeType.SOFT_DEPENDENCY
    
    def test_add_edge_with_metadata(self, empty_dag):
        """Test adding edge with metadata."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        metadata = {"reason": "data dependency"}
        edge = empty_dag.add_edge("A", "B", metadata=metadata)
        
        assert edge.metadata == metadata
    
    def test_add_edge_nonexistent_source_raises(self, empty_dag):
        """Test adding edge with nonexistent source raises."""
        empty_dag.add_node("B")
        
        with pytest.raises(NodeNotFoundError):
            empty_dag.add_edge("A", "B")
    
    def test_add_edge_nonexistent_target_raises(self, empty_dag):
        """Test adding edge with nonexistent target raises."""
        empty_dag.add_node("A")
        
        with pytest.raises(NodeNotFoundError):
            empty_dag.add_edge("A", "B")
    
    def test_has_edge(self, simple_dag):
        """Test checking edge existence."""
        assert simple_dag.has_edge("A", "B")
        assert not simple_dag.has_edge("B", "A")  # Direction matters
        assert not simple_dag.has_edge("A", "C")  # No direct edge
    
    def test_get_edge(self, simple_dag):
        """Test getting edge details."""
        edge = simple_dag.get_edge("A", "B")
        
        assert edge.source == "A"
        assert edge.target == "B"
    
    def test_get_nonexistent_edge_raises(self, simple_dag):
        """Test getting nonexistent edge raises."""
        with pytest.raises(EdgeNotFoundError):
            simple_dag.get_edge("A", "C")
    
    def test_remove_edge(self, simple_dag):
        """Test removing an edge."""
        initial_count = simple_dag.edge_count
        removed = simple_dag.remove_edge("A", "B")
        
        assert removed.source == "A"
        assert simple_dag.edge_count == initial_count - 1
        assert not simple_dag.has_edge("A", "B")
    
    def test_remove_nonexistent_edge_raises(self, simple_dag):
        """Test removing nonexistent edge raises."""
        with pytest.raises(EdgeNotFoundError):
            simple_dag.remove_edge("A", "C")
    
    def test_get_dependencies(self, diamond_dag):
        """Test getting node dependencies."""
        deps = diamond_dag.get_dependencies("D")
        
        assert set(deps) == {"B", "C"}
    
    def test_get_dependencies_root_node(self, diamond_dag):
        """Test getting dependencies of root node (should be empty)."""
        deps = diamond_dag.get_dependencies("A")
        
        assert deps == []
    
    def test_get_dependents(self, diamond_dag):
        """Test getting nodes that depend on a node."""
        dependents = diamond_dag.get_dependents("A")
        
        assert set(dependents) == {"B", "C"}
    
    def test_get_dependents_leaf_node(self, diamond_dag):
        """Test getting dependents of leaf node (should be empty)."""
        dependents = diamond_dag.get_dependents("D")
        
        assert dependents == []
    
    def test_add_duplicate_edge_is_idempotent(self, simple_dag):
        """Test that adding duplicate edge is idempotent."""
        initial_count = simple_dag.edge_count
        simple_dag.add_edge("A", "B")  # Already exists
        
        assert simple_dag.edge_count == initial_count


# ==============================================================================
# TEST CLASS: Cycle Detection
# ==============================================================================


class TestCycleDetection:
    """Tests for cycle detection in DAG."""
    
    def test_valid_dag_has_no_cycle(self, simple_dag):
        """Test that valid DAG reports no cycle."""
        assert not simple_dag.has_cycle()
    
    def test_detect_simple_cycle(self, empty_dag):
        """Test detection of simple A → B → A cycle."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        empty_dag.add_edge("A", "B", validate=False)
        
        # Adding B → A should fail with cycle
        with pytest.raises(CyclicDependencyError) as exc:
            empty_dag.add_edge("B", "A")
        
        assert "A" in exc.value.cycle
        assert "B" in exc.value.cycle
    
    def test_detect_self_loop(self, empty_dag):
        """Test detection of self-loop cycle."""
        empty_dag.add_node("A")
        
        with pytest.raises(CyclicDependencyError):
            empty_dag.add_edge("A", "A")
    
    def test_detect_longer_cycle(self, empty_dag):
        """Test detection of longer A → B → C → A cycle."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        empty_dag.add_node("C")
        empty_dag.add_edge("A", "B", validate=False)
        empty_dag.add_edge("B", "C", validate=False)
        
        with pytest.raises(CyclicDependencyError) as exc:
            empty_dag.add_edge("C", "A")
        
        assert len(exc.value.cycle) >= 3
    
    def test_diamond_dag_no_cycle(self, diamond_dag):
        """Test that diamond DAG has no cycle."""
        assert not diamond_dag.has_cycle()
    
    def test_adding_edge_preserves_acyclic(self, diamond_dag):
        """Test that valid edge addition keeps DAG acyclic."""
        diamond_dag.add_node("E")
        diamond_dag.add_edge("D", "E")
        
        assert not diamond_dag.has_cycle()
    
    def test_complex_dag_no_cycle(self, complex_dag):
        """Test that complex DAG has no cycle."""
        assert not complex_dag.has_cycle()


# ==============================================================================
# TEST CLASS: Topological Sort
# ==============================================================================


class TestTopologicalSort:
    """Tests for topological sorting."""
    
    def test_simple_topological_sort(self, simple_dag):
        """Test topological sort of simple DAG."""
        order = simple_dag.topological_sort()
        
        assert order.index("A") < order.index("B")
        assert order.index("B") < order.index("C")
    
    def test_diamond_topological_sort(self, diamond_dag):
        """Test topological sort of diamond DAG."""
        order = diamond_dag.topological_sort()
        
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("D")
        assert order.index("C") < order.index("D")
    
    def test_empty_dag_topological_sort(self, empty_dag):
        """Test topological sort of empty DAG."""
        order = empty_dag.topological_sort()
        
        assert order == []
    
    def test_single_node_topological_sort(self, empty_dag):
        """Test topological sort with single node."""
        empty_dag.add_node("A")
        order = empty_dag.topological_sort()
        
        assert order == ["A"]
    
    def test_topological_sort_respects_priority(self, empty_dag):
        """Test that topological sort respects priority."""
        empty_dag.add_node("A", priority=Priority.P3_LOW)
        empty_dag.add_node("B", priority=Priority.P0_CRITICAL)
        empty_dag.add_node("C", priority=Priority.P1_HIGH)
        # No edges - all can be first
        
        order = empty_dag.topological_sort()
        
        # B (P0) should come before C (P1) which should come before A (P3)
        assert order.index("B") < order.index("C")
        assert order.index("C") < order.index("A")
    
    def test_topological_sort_detects_cycle(self, empty_dag):
        """Test that topological sort raises on cyclic graph."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        empty_dag.add_edge("A", "B", validate=False)
        empty_dag.add_edge("B", "A", validate=False)
        
        with pytest.raises(CyclicDependencyError):
            empty_dag.topological_sort()


# ==============================================================================
# TEST CLASS: Ready Tasks
# ==============================================================================


class TestReadyTasks:
    """Tests for ready task identification."""
    
    def test_get_ready_tasks_simple(self, simple_dag):
        """Test getting ready tasks in simple DAG."""
        ready = simple_dag.get_ready_tasks()
        
        assert ready == ["A"]  # Only A has no dependencies
    
    def test_get_ready_tasks_after_completion(self, simple_dag):
        """Test getting ready tasks after completing dependencies."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        ready = simple_dag.get_ready_tasks()
        
        assert ready == ["B"]
    
    def test_get_ready_tasks_diamond(self, diamond_dag):
        """Test getting ready tasks in diamond DAG."""
        diamond_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        diamond_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        ready = diamond_dag.get_ready_tasks()
        
        assert set(ready) == {"B", "C"}  # Both can run in parallel
    
    def test_get_ready_tasks_empty_dag(self, empty_dag):
        """Test getting ready tasks from empty DAG."""
        ready = empty_dag.get_ready_tasks()
        
        assert ready == []
    
    def test_get_ready_tasks_all_completed(self, simple_dag):
        """Test getting ready tasks when all are completed."""
        for node_id in ["A", "B", "C"]:
            simple_dag.set_node_status(node_id, NodeStatus.IN_PROGRESS)
            simple_dag.set_node_status(node_id, NodeStatus.COMPLETED)
        
        ready = simple_dag.get_ready_tasks()
        
        assert ready == []
    
    def test_get_blocked_tasks(self, simple_dag):
        """Test getting blocked tasks."""
        blocked = simple_dag.get_blocked_tasks()
        
        assert set(blocked) == {"B", "C"}  # B and C are blocked by dependencies
    
    def test_ready_tasks_respects_priority(self, diamond_dag):
        """Test that ready tasks are sorted by priority."""
        diamond_dag.update_node("B", priority=Priority.P3_LOW)
        diamond_dag.update_node("C", priority=Priority.P0_CRITICAL)
        
        diamond_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        diamond_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        ready = diamond_dag.get_ready_tasks()
        
        # C (P0) should come before B (P3)
        assert ready.index("C") < ready.index("B")


# ==============================================================================
# TEST CLASS: Critical Path
# ==============================================================================


class TestCriticalPath:
    """Tests for critical path calculation."""
    
    def test_critical_path_simple(self, simple_dag):
        """Test critical path in simple linear DAG."""
        path = simple_dag.get_critical_path()
        
        assert path == ["A", "B", "C"]
    
    def test_critical_path_diamond(self, diamond_dag):
        """Test critical path in diamond DAG."""
        path = diamond_dag.get_critical_path()
        
        assert len(path) == 3
        assert path[0] == "A"
        assert path[-1] == "D"
    
    def test_critical_path_empty_dag(self, empty_dag):
        """Test critical path in empty DAG."""
        path = empty_dag.get_critical_path()
        
        assert path == []
    
    def test_critical_path_single_node(self, empty_dag):
        """Test critical path with single node."""
        empty_dag.add_node("A")
        path = empty_dag.get_critical_path()
        
        assert path == ["A"]


# ==============================================================================
# TEST CLASS: Parallel Groups
# ==============================================================================


class TestParallelGroups:
    """Tests for parallel task grouping."""
    
    def test_parallel_groups_simple(self, simple_dag):
        """Test parallel groups in linear DAG."""
        groups = simple_dag.get_parallel_groups()
        
        assert len(groups) == 3
        assert groups[0] == ["A"]
        assert groups[1] == ["B"]
        assert groups[2] == ["C"]
    
    def test_parallel_groups_diamond(self, diamond_dag):
        """Test parallel groups in diamond DAG."""
        groups = diamond_dag.get_parallel_groups()
        
        assert len(groups) == 3
        assert groups[0] == ["A"]
        assert set(groups[1]) == {"B", "C"}
        assert groups[2] == ["D"]
    
    def test_parallel_groups_empty_dag(self, empty_dag):
        """Test parallel groups in empty DAG."""
        groups = empty_dag.get_parallel_groups()
        
        assert groups == []
    
    def test_parallel_groups_no_edges(self, empty_dag):
        """Test parallel groups when no edges exist."""
        empty_dag.add_node("A")
        empty_dag.add_node("B")
        empty_dag.add_node("C")
        
        groups = empty_dag.get_parallel_groups()
        
        # All nodes can run in parallel (single group)
        assert len(groups) == 1
        assert set(groups[0]) == {"A", "B", "C"}


# ==============================================================================
# TEST CLASS: Statistics
# ==============================================================================


class TestStatistics:
    """Tests for DAG statistics."""
    
    def test_basic_statistics(self, simple_dag):
        """Test basic DAG statistics."""
        stats = simple_dag.get_statistics()
        
        assert stats.node_count == 3
        assert stats.edge_count == 2
        assert stats.not_started_count == 3
        assert stats.completed_count == 0
    
    def test_statistics_after_completion(self, simple_dag):
        """Test statistics after completing some tasks."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        stats = simple_dag.get_statistics()
        
        assert stats.completed_count == 1
        assert stats.in_progress_count == 0
        assert stats.not_started_count == 2
    
    def test_statistics_progress_percentage(self, simple_dag):
        """Test progress percentage calculation."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        stats = simple_dag.get_statistics()
        
        assert stats.progress_percentage == pytest.approx(33.33, rel=0.01)
    
    def test_statistics_empty_dag(self, empty_dag):
        """Test statistics on empty DAG."""
        stats = empty_dag.get_statistics()
        
        assert stats.node_count == 0
        assert stats.edge_count == 0
        assert stats.progress_percentage == 100.0


# ==============================================================================
# TEST CLASS: Serialization
# ==============================================================================


class TestSerialization:
    """Tests for DAG serialization/deserialization."""
    
    def test_to_dict(self, simple_dag):
        """Test converting DAG to dictionary."""
        data = simple_dag.to_dict()
        
        assert data["name"] == "simple"
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2
    
    def test_to_json(self, simple_dag):
        """Test converting DAG to JSON."""
        json_str = simple_dag.to_json()
        
        data = json.loads(json_str)
        assert data["name"] == "simple"
    
    def test_from_dict(self, simple_dag):
        """Test creating DAG from dictionary."""
        data = simple_dag.to_dict()
        restored = DAG.from_dict(data)
        
        assert restored.name == simple_dag.name
        assert restored.node_count == simple_dag.node_count
        assert restored.edge_count == simple_dag.edge_count
    
    def test_from_json(self, simple_dag):
        """Test creating DAG from JSON."""
        json_str = simple_dag.to_json()
        restored = DAG.from_json(json_str)
        
        assert restored.name == simple_dag.name
        assert restored.node_count == simple_dag.node_count
    
    def test_serialization_preserves_status(self, simple_dag):
        """Test that serialization preserves node status."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        simple_dag.set_node_status("A", NodeStatus.COMPLETED)
        
        restored = DAG.from_dict(simple_dag.to_dict())
        
        assert restored.get_node("A").status == NodeStatus.COMPLETED
    
    def test_serialization_preserves_timestamps(self, simple_dag):
        """Test that serialization preserves timestamps."""
        simple_dag.set_node_status("A", NodeStatus.IN_PROGRESS)
        original_started = simple_dag.get_node("A").started_at
        
        restored = DAG.from_dict(simple_dag.to_dict())
        
        assert restored.get_node("A").started_at == original_started


# ==============================================================================
# TEST CLASS: Edge Cases
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_dag_properties(self, empty_dag):
        """Test properties of empty DAG."""
        assert empty_dag.is_empty
        assert empty_dag.node_count == 0
        assert empty_dag.edge_count == 0
        assert empty_dag.nodes == []
        assert empty_dag.edges == []
    
    def test_single_node_dag(self, empty_dag):
        """Test DAG with single node."""
        empty_dag.add_node("A")
        
        assert empty_dag.node_count == 1
        assert empty_dag.topological_sort() == ["A"]
        assert empty_dag.get_ready_tasks() == ["A"]
        assert not empty_dag.has_cycle()
    
    def test_node_name_defaults_to_id(self, empty_dag):
        """Test that node name defaults to ID."""
        node = empty_dag.add_node("task-123")
        
        assert node.name == "task-123"
    
    def test_clear_dag(self, simple_dag):
        """Test clearing all nodes and edges."""
        simple_dag.clear()
        
        assert simple_dag.is_empty
        assert simple_dag.node_count == 0
        assert simple_dag.edge_count == 0
    
    def test_version_increments_on_changes(self, empty_dag):
        """Test that version increments on changes."""
        v1 = empty_dag.version
        empty_dag.add_node("A")
        v2 = empty_dag.version
        empty_dag.add_node("B")
        v3 = empty_dag.version
        
        assert v2 > v1
        assert v3 > v2
    
    def test_dag_contains_operator(self, simple_dag):
        """Test __contains__ operator."""
        assert "A" in simple_dag
        assert "Z" not in simple_dag
    
    def test_dag_len_operator(self, simple_dag):
        """Test __len__ operator."""
        assert len(simple_dag) == 3
    
    def test_dag_iter(self, simple_dag):
        """Test iterating over DAG."""
        node_ids = [node.id for node in simple_dag]
        
        # Should be in topological order
        assert node_ids.index("A") < node_ids.index("B")
        assert node_ids.index("B") < node_ids.index("C")
    
    def test_dag_repr(self, simple_dag):
        """Test DAG string representation."""
        repr_str = repr(simple_dag)
        
        assert "simple" in repr_str
        assert "3" in repr_str  # node count
        assert "2" in repr_str  # edge count


# ==============================================================================
# TEST CLASS: Thread Safety
# ==============================================================================


class TestThreadSafety:
    """Tests for thread-safe operations."""
    
    def test_concurrent_reads(self, simple_dag):
        """Test concurrent read operations."""
        results = []
        
        def read_nodes():
            for _ in range(100):
                count = simple_dag.node_count
                results.append(count)
        
        threads = [threading.Thread(target=read_nodes) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert all(r == 3 for r in results)
    
    def test_concurrent_writes(self, empty_dag):
        """Test concurrent write operations."""
        def add_nodes(prefix: str):
            for i in range(10):
                try:
                    empty_dag.add_node(f"{prefix}-{i}")
                except DuplicateNodeError:
                    pass  # Expected with concurrent writes
        
        threads = [
            threading.Thread(target=add_nodes, args=(f"t{i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have 50 nodes (5 threads × 10 nodes each)
        assert empty_dag.node_count == 50
    
    def test_concurrent_read_write(self, empty_dag):
        """Test concurrent read and write operations."""
        stop_event = threading.Event()
        read_results = []
        
        def writer():
            for i in range(100):
                empty_dag.add_node(f"node-{i}")
        
        def reader():
            while not stop_event.is_set():
                read_results.append(empty_dag.node_count)
        
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        reader_thread.start()
        writer_thread.start()
        
        writer_thread.join()
        stop_event.set()
        reader_thread.join()
        
        # All reads should be valid (0-100)
        assert all(0 <= r <= 100 for r in read_results)


# ==============================================================================
# TEST CLASS: Performance
# ==============================================================================


class TestPerformance:
    """Tests for performance guarantees."""
    
    def test_node_lookup_time(self, empty_dag):
        """Test that node lookup is O(1)."""
        # Add many nodes
        for i in range(1000):
            empty_dag.add_node(f"node-{i}")
        
        # Measure lookup time
        start = time.perf_counter()
        for _ in range(1000):
            _ = empty_dag.get_node("node-500")
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        # Should be very fast (< 10ms for 1000 lookups)
        assert elapsed < 10
    
    def test_add_node_time(self, empty_dag):
        """Test that adding nodes is O(1)."""
        start = time.perf_counter()
        for i in range(1000):
            empty_dag.add_node(f"node-{i}")
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        # Should complete in < 100ms
        assert elapsed < 100
    
    def test_topological_sort_performance(self, empty_dag):
        """Test topological sort performance."""
        # Create a chain of 100 nodes
        for i in range(100):
            empty_dag.add_node(f"node-{i}")
        for i in range(99):
            empty_dag.add_edge(f"node-{i}", f"node-{i+1}")
        
        start = time.perf_counter()
        for _ in range(100):
            empty_dag.topological_sort()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        # Should complete in reasonable time (< 500ms for 100 sorts)
        assert elapsed < 500
    
    def test_cycle_detection_performance(self, empty_dag):
        """Test cycle detection performance."""
        # Create a wide DAG
        for i in range(100):
            empty_dag.add_node(f"node-{i}")
        for i in range(50):
            empty_dag.add_edge(f"node-{i}", f"node-{i+50}")
        
        start = time.perf_counter()
        for _ in range(100):
            empty_dag.has_cycle()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        # Should complete in reasonable time
        assert elapsed < 500


# ==============================================================================
# TEST CLASS: DAGNode Unit Tests
# ==============================================================================


class TestDAGNode:
    """Tests for DAGNode dataclass."""
    
    def test_node_creation(self):
        """Test creating a DAGNode."""
        node = DAGNode(id="task1", name="Test Task")
        
        assert node.id == "task1"
        assert node.name == "Test Task"
        assert node.status == NodeStatus.NOT_STARTED
    
    def test_node_start(self):
        """Test starting a node."""
        node = DAGNode(id="task1")
        node.start()
        
        assert node.status == NodeStatus.IN_PROGRESS
        assert node.started_at is not None
    
    def test_node_complete(self):
        """Test completing a node."""
        node = DAGNode(id="task1")
        node.start()
        node.complete()
        
        assert node.status == NodeStatus.COMPLETED
        assert node.completed_at is not None
    
    def test_node_fail(self):
        """Test failing a node."""
        node = DAGNode(id="task1")
        node.fail("Something went wrong")
        
        assert node.status == NodeStatus.FAILED
        assert node.error_message == "Something went wrong"
    
    def test_node_retry(self):
        """Test retrying a failed node."""
        node = DAGNode(id="task1")
        node.fail("First failure")
        node.retry()
        
        assert node.status == NodeStatus.NOT_STARTED
        assert node.retry_count == 1
        assert node.error_message is None
    
    def test_node_max_retries(self):
        """Test that max retries is enforced."""
        node = DAGNode(id="task1", max_retries=2)
        
        node.fail("Failure 1")
        node.retry()
        node.fail("Failure 2")
        node.retry()
        node.fail("Failure 3")
        
        assert not node.can_retry()
        with pytest.raises(InvalidTransitionError):
            node.retry()
    
    def test_node_duration(self):
        """Test calculating node duration."""
        node = DAGNode(id="task1")
        node.start()
        time.sleep(0.1)
        node.complete()
        
        assert node.duration_seconds >= 0.1
    
    def test_node_terminal_status(self):
        """Test terminal status property."""
        completed = DAGNode(id="1", status=NodeStatus.COMPLETED)
        failed = DAGNode(id="2", status=NodeStatus.FAILED)
        in_progress = DAGNode(id="3", status=NodeStatus.IN_PROGRESS)
        
        assert completed.status.is_terminal
        assert failed.status.is_terminal
        assert not in_progress.status.is_terminal
    
    def test_node_to_dict(self):
        """Test node serialization to dict."""
        node = DAGNode(
            id="task1",
            name="Test",
            data={"key": "value"},
            tags={"tag1"}
        )
        
        data = node.to_dict()
        
        assert data["id"] == "task1"
        assert data["name"] == "Test"
        assert data["data"] == {"key": "value"}
        assert "tag1" in data["tags"]
    
    def test_node_from_dict(self):
        """Test node deserialization from dict."""
        data = {
            "id": "task1",
            "name": "Test",
            "status": "completed",
            "priority": 1,
            "data": {"key": "value"},
            "tags": ["tag1"],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T01:00:00",
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "retry_count": 0,
            "max_retries": 3,
        }
        
        node = DAGNode.from_dict(data)
        
        assert node.id == "task1"
        assert node.status == NodeStatus.COMPLETED
        assert node.priority == Priority.P1_HIGH
