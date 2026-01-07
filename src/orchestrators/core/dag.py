# ==============================================================================
# CORTEX 6.0 - Directed Acyclic Graph (DAG) Implementation
# ==============================================================================
# Author: Asif Hussain
# Version: 6.0.0
# Purpose: DAG data structure for task dependency management
# TDD: Tests in tests/unit/test_dag.py
# ==============================================================================

"""
Directed Acyclic Graph (DAG) implementation for CORTEX 6.0.

This module provides a production-grade DAG implementation for managing
task dependencies in the TODO Orchestrator. It supports:

- O(1) node lookup via hash table
- O(V+E) cycle detection via DFS
- O(V+E) topological sorting via Kahn's algorithm
- Thread-safe operations with RLock
- Audit logging integration
- JSON serialization/deserialization

Architecture:
    DAG uses an adjacency list representation with:
    - nodes: Dict[str, DAGNode] for O(1) node access
    - edges: List[DAGEdge] for edge tracking
    - adjacency_list: Dict[str, Set[str]] for O(1) neighbor lookup
    - reverse_adjacency: Dict[str, Set[str]] for dependency queries

Performance Guarantees:
    - add_node: O(1)
    - remove_node: O(degree)
    - add_edge: O(1) amortized
    - remove_edge: O(1)
    - has_cycle: O(V+E)
    - topological_sort: O(V+E)
    - get_ready_tasks: O(V)

Usage:
    >>> from src.orchestrators.core.dag import DAG, DAGNode, NodeStatus
    >>> dag = DAG(name="example")
    >>> dag.add_node("task1", data={"title": "First Task"})
    >>> dag.add_node("task2", data={"title": "Second Task"})
    >>> dag.add_edge("task1", "task2")  # task2 depends on task1
    >>> ready = dag.get_ready_tasks()
    >>> print(ready)  # ['task1'] - no dependencies
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from collections import deque

# ==============================================================================
# ENUMS
# ==============================================================================


class NodeStatus(str, Enum):
    """Status of a DAG node/task."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    
    @property
    def is_terminal(self) -> bool:
        """Check if status is terminal (no further transitions possible)."""
        return self in {NodeStatus.COMPLETED, NodeStatus.FAILED, 
                       NodeStatus.SKIPPED, NodeStatus.CANCELLED}
    
    @property
    def is_active(self) -> bool:
        """Check if status indicates active work."""
        return self == NodeStatus.IN_PROGRESS


class EdgeType(str, Enum):
    """Type of edge/dependency between nodes."""
    DEPENDS_ON = "depends_on"        # Target cannot start until source completes
    BLOCKS = "blocks"                # Source blocks target from starting
    SOFT_DEPENDENCY = "soft"         # Preference but not required
    PARALLEL_WITH = "parallel_with"  # Can run in parallel


class Priority(int, Enum):
    """Task priority levels."""
    P0_CRITICAL = 0
    P1_HIGH = 1
    P2_MEDIUM = 2
    P3_LOW = 3
    P4_OPTIONAL = 4


# ==============================================================================
# EXCEPTIONS
# ==============================================================================


class DAGError(Exception):
    """Base exception for DAG operations."""
    pass


class DAGValidationError(DAGError):
    """Raised when DAG validation fails."""
    pass


class CyclicDependencyError(DAGError):
    """Raised when a cycle is detected in the DAG."""
    def __init__(self, cycle: List[str], message: str = ""):
        self.cycle = cycle
        if not message:
            message = f"Cyclic dependency detected: {' → '.join(cycle)}"
        super().__init__(message)


class NodeNotFoundError(DAGError):
    """Raised when a node is not found in the DAG."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(f"Node not found: {node_id}")


class EdgeNotFoundError(DAGError):
    """Raised when an edge is not found in the DAG."""
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        super().__init__(f"Edge not found: {source} → {target}")


class DuplicateNodeError(DAGError):
    """Raised when trying to add a node that already exists."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(f"Node already exists: {node_id}")


class InvalidTransitionError(DAGError):
    """Raised when an invalid status transition is attempted."""
    def __init__(self, node_id: str, current: NodeStatus, target: NodeStatus):
        self.node_id = node_id
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid status transition for {node_id}: "
            f"{current.value} → {target.value}"
        )


# ==============================================================================
# DATA CLASSES
# ==============================================================================


@dataclass
class DAGNode:
    """
    Node in the Directed Acyclic Graph.
    
    Represents a task or work item with metadata and status.
    
    Attributes:
        id: Unique node identifier
        name: Human-readable node name
        status: Current execution status
        priority: Task priority level
        data: Arbitrary metadata dictionary
        created_at: Node creation timestamp
        updated_at: Last update timestamp
        started_at: When execution started
        completed_at: When execution completed
        error_message: Error details if failed
        retry_count: Number of retry attempts
        max_retries: Maximum allowed retries
        tags: Set of tags for categorization
    """
    id: str
    name: str = ""
    status: NodeStatus = NodeStatus.NOT_STARTED
    priority: Priority = Priority.P2_MEDIUM
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize defaults after creation."""
        if not self.name:
            self.name = self.id
        if isinstance(self.tags, (list, tuple)):
            self.tags = set(self.tags)
    
    def start(self) -> None:
        """Mark node as started."""
        self.status = NodeStatus.IN_PROGRESS
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        """Mark node as completed."""
        self.status = NodeStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def fail(self, error: str) -> None:
        """Mark node as failed with error message."""
        self.status = NodeStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.now()
    
    def can_retry(self) -> bool:
        """Check if node can be retried."""
        return (
            self.status == NodeStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def retry(self) -> None:
        """Reset node for retry."""
        if not self.can_retry():
            raise InvalidTransitionError(
                self.id, self.status, NodeStatus.NOT_STARTED
            )
        self.retry_count += 1
        self.status = NodeStatus.NOT_STARTED
        self.error_message = None
        self.updated_at = datetime.now()
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "tags": list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DAGNode:
        """Create node from dictionary."""
        # Parse datetime fields
        for dt_field in ['created_at', 'updated_at', 'started_at', 'completed_at']:
            if data.get(dt_field) and isinstance(data[dt_field], str):
                data[dt_field] = datetime.fromisoformat(data[dt_field])
        
        # Parse status
        if isinstance(data.get('status'), str):
            data['status'] = NodeStatus(data['status'])
        
        # Parse priority
        if isinstance(data.get('priority'), int):
            data['priority'] = Priority(data['priority'])
        
        # Parse tags
        if isinstance(data.get('tags'), list):
            data['tags'] = set(data['tags'])
        
        return cls(**data)


@dataclass
class DAGEdge:
    """
    Edge in the Directed Acyclic Graph.
    
    Represents a dependency relationship between nodes.
    
    Attributes:
        source: Source node ID (dependency)
        target: Target node ID (dependent)
        edge_type: Type of dependency relationship
        metadata: Additional edge metadata
        created_at: Edge creation timestamp
    """
    source: str
    target: str
    edge_type: EdgeType = EdgeType.DEPENDS_ON
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self) -> int:
        """Make edge hashable by source and target."""
        return hash((self.source, self.target))
    
    def __eq__(self, other: object) -> bool:
        """Compare edges by source and target."""
        if not isinstance(other, DAGEdge):
            return False
        return self.source == other.source and self.target == other.target
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DAGEdge:
        """Create edge from dictionary."""
        if isinstance(data.get('edge_type'), str):
            data['edge_type'] = EdgeType(data['edge_type'])
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class DAGStatistics:
    """Statistics about a DAG."""
    node_count: int
    edge_count: int
    completed_count: int
    failed_count: int
    in_progress_count: int
    blocked_count: int
    not_started_count: int
    depth: int
    width: int  # Maximum parallel tasks at any level
    critical_path_length: int
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.node_count == 0:
            return 100.0
        return (self.completed_count / self.node_count) * 100


# ==============================================================================
# DAG IMPLEMENTATION
# ==============================================================================


class DAG:
    """
    Directed Acyclic Graph implementation for task dependency management.
    
    Thread-safe implementation supporting:
    - O(1) node operations
    - O(V+E) cycle detection
    - O(V+E) topological sorting
    - Parallel task identification
    
    Attributes:
        name: DAG identifier/name
        description: Human-readable description
        
    Usage:
        >>> dag = DAG("my-project")
        >>> dag.add_node("task1")
        >>> dag.add_node("task2")
        >>> dag.add_edge("task1", "task2")
        >>> order = dag.topological_sort()
    """
    
    # Valid status transitions
    VALID_TRANSITIONS: Dict[NodeStatus, Set[NodeStatus]] = {
        NodeStatus.NOT_STARTED: {NodeStatus.IN_PROGRESS, NodeStatus.BLOCKED, 
                                  NodeStatus.SKIPPED, NodeStatus.CANCELLED},
        NodeStatus.IN_PROGRESS: {NodeStatus.COMPLETED, NodeStatus.FAILED,
                                  NodeStatus.CANCELLED},
        NodeStatus.BLOCKED: {NodeStatus.NOT_STARTED, NodeStatus.SKIPPED,
                             NodeStatus.CANCELLED},
        NodeStatus.COMPLETED: set(),  # Terminal state
        NodeStatus.FAILED: {NodeStatus.NOT_STARTED},  # Can retry
        NodeStatus.SKIPPED: set(),  # Terminal state
        NodeStatus.CANCELLED: set(),  # Terminal state
    }
    
    def __init__(
        self,
        name: str = "unnamed",
        description: str = "",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize a new DAG.
        
        Args:
            name: DAG identifier
            description: Human-readable description
            logger: Optional logger for audit logging
        """
        self.name = name
        self.description = description
        self.logger = logger or logging.getLogger(__name__)
        
        # Node storage - O(1) lookup
        self._nodes: Dict[str, DAGNode] = {}
        
        # Edge storage
        self._edges: Set[DAGEdge] = set()
        
        # Adjacency lists - O(1) neighbor lookup
        # adjacency[a] = {b, c} means a → b and a → c
        self._adjacency: Dict[str, Set[str]] = {}
        
        # Reverse adjacency - for finding dependencies
        # reverse[b] = {a} means b depends on a
        self._reverse_adjacency: Dict[str, Set[str]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Metadata
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._version = 1
    
    # =========================================================================
    # PROPERTIES
    # =========================================================================
    
    @property
    def node_count(self) -> int:
        """Get number of nodes in the DAG."""
        with self._lock:
            return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        """Get number of edges in the DAG."""
        with self._lock:
            return len(self._edges)
    
    @property
    def nodes(self) -> List[DAGNode]:
        """Get list of all nodes (copy)."""
        with self._lock:
            return list(self._nodes.values())
    
    @property
    def edges(self) -> List[DAGEdge]:
        """Get list of all edges (copy)."""
        with self._lock:
            return list(self._edges)
    
    @property
    def node_ids(self) -> List[str]:
        """Get list of all node IDs."""
        with self._lock:
            return list(self._nodes.keys())
    
    @property
    def is_empty(self) -> bool:
        """Check if DAG has no nodes."""
        return self.node_count == 0
    
    @property
    def version(self) -> int:
        """Get DAG version (increments on modification)."""
        return self._version
    
    # =========================================================================
    # NODE OPERATIONS
    # =========================================================================
    
    def add_node(
        self,
        node_id: str,
        name: str = "",
        data: Optional[Dict[str, Any]] = None,
        priority: Priority = Priority.P2_MEDIUM,
        tags: Optional[Set[str]] = None
    ) -> DAGNode:
        """
        Add a node to the DAG.
        
        Args:
            node_id: Unique node identifier
            name: Human-readable name (defaults to node_id)
            data: Additional node metadata
            priority: Task priority
            tags: Set of tags for categorization
            
        Returns:
            The created DAGNode
            
        Raises:
            DuplicateNodeError: If node already exists
        """
        with self._lock:
            if node_id in self._nodes:
                raise DuplicateNodeError(node_id)
            
            node = DAGNode(
                id=node_id,
                name=name or node_id,
                data=data or {},
                priority=priority,
                tags=tags or set()
            )
            
            self._nodes[node_id] = node
            self._adjacency[node_id] = set()
            self._reverse_adjacency[node_id] = set()
            
            self._touch()
            self.logger.debug(f"Added node: {node_id}")
            
            return node
    
    def add_node_object(self, node: DAGNode) -> DAGNode:
        """
        Add an existing DAGNode object to the DAG.
        
        Args:
            node: DAGNode to add
            
        Returns:
            The added node
            
        Raises:
            DuplicateNodeError: If node already exists
        """
        with self._lock:
            if node.id in self._nodes:
                raise DuplicateNodeError(node.id)
            
            self._nodes[node.id] = node
            self._adjacency[node.id] = set()
            self._reverse_adjacency[node.id] = set()
            
            self._touch()
            self.logger.debug(f"Added node object: {node.id}")
            
            return node
    
    def get_node(self, node_id: str) -> DAGNode:
        """
        Get a node by ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            The DAGNode
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            return self._nodes[node_id]
    
    def has_node(self, node_id: str) -> bool:
        """Check if node exists in DAG."""
        with self._lock:
            return node_id in self._nodes
    
    def remove_node(self, node_id: str) -> DAGNode:
        """
        Remove a node and all its edges.
        
        Args:
            node_id: Node to remove
            
        Returns:
            The removed node
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            
            # Remove all edges involving this node
            outgoing = self._adjacency.get(node_id, set()).copy()
            incoming = self._reverse_adjacency.get(node_id, set()).copy()
            
            for target in outgoing:
                self._edges.discard(DAGEdge(node_id, target))
                self._reverse_adjacency[target].discard(node_id)
            
            for source in incoming:
                self._edges.discard(DAGEdge(source, node_id))
                self._adjacency[source].discard(node_id)
            
            # Remove node
            node = self._nodes.pop(node_id)
            del self._adjacency[node_id]
            del self._reverse_adjacency[node_id]
            
            self._touch()
            self.logger.debug(f"Removed node: {node_id}")
            
            return node
    
    def update_node(
        self,
        node_id: str,
        name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        priority: Optional[Priority] = None,
        tags: Optional[Set[str]] = None
    ) -> DAGNode:
        """
        Update node properties.
        
        Args:
            node_id: Node to update
            name: New name (if provided)
            data: New/merged data (if provided)
            priority: New priority (if provided)
            tags: New tags (if provided)
            
        Returns:
            The updated node
            
        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            
            node = self._nodes[node_id]
            
            if name is not None:
                node.name = name
            if data is not None:
                node.data.update(data)
            if priority is not None:
                node.priority = priority
            if tags is not None:
                node.tags = tags
            
            node.updated_at = datetime.now()
            self._touch()
            
            return node
    
    def set_node_status(
        self,
        node_id: str,
        status: NodeStatus,
        error_message: Optional[str] = None
    ) -> DAGNode:
        """
        Set node status with validation.
        
        Args:
            node_id: Node to update
            status: New status
            error_message: Error message (if failing)
            
        Returns:
            The updated node
            
        Raises:
            NodeNotFoundError: If node doesn't exist
            InvalidTransitionError: If transition is not valid
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            
            node = self._nodes[node_id]
            current = node.status
            
            # Validate transition
            valid_targets = self.VALID_TRANSITIONS.get(current, set())
            if status not in valid_targets and status != current:
                raise InvalidTransitionError(node_id, current, status)
            
            # Apply transition
            if status == NodeStatus.IN_PROGRESS:
                node.start()
            elif status == NodeStatus.COMPLETED:
                node.complete()
            elif status == NodeStatus.FAILED:
                node.fail(error_message or "Unknown error")
            else:
                node.status = status
                node.updated_at = datetime.now()
            
            self._touch()
            self.logger.info(
                f"Node {node_id} status: {current.value} → {status.value}"
            )
            
            return node
    
    # =========================================================================
    # EDGE OPERATIONS
    # =========================================================================
    
    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType = EdgeType.DEPENDS_ON,
        metadata: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> DAGEdge:
        """
        Add an edge between nodes.
        
        The edge means: target depends on source
        (source must complete before target can start)
        
        Args:
            source: Source node (dependency)
            target: Target node (dependent)
            edge_type: Type of dependency
            metadata: Additional edge metadata
            validate: Check for cycles after adding
            
        Returns:
            The created edge
            
        Raises:
            NodeNotFoundError: If either node doesn't exist
            CyclicDependencyError: If adding creates a cycle
        """
        with self._lock:
            if source not in self._nodes:
                raise NodeNotFoundError(source)
            if target not in self._nodes:
                raise NodeNotFoundError(target)
            
            # Check if edge already exists
            edge = DAGEdge(source, target, edge_type, metadata or {})
            if edge in self._edges:
                return edge  # Idempotent
            
            # Add edge
            self._edges.add(edge)
            self._adjacency[source].add(target)
            self._reverse_adjacency[target].add(source)
            
            # Validate no cycle created
            if validate and self.has_cycle():
                # Find the cycle BEFORE rollback for error message
                cycle = self._find_cycle()
                
                # Rollback
                self._edges.discard(edge)
                self._adjacency[source].discard(target)
                self._reverse_adjacency[target].discard(source)
                
                raise CyclicDependencyError(cycle)
            
            self._touch()
            self.logger.debug(f"Added edge: {source} → {target}")
            
            return edge
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists between nodes."""
        with self._lock:
            return target in self._adjacency.get(source, set())
    
    def get_edge(self, source: str, target: str) -> DAGEdge:
        """
        Get edge between nodes.
        
        Raises:
            EdgeNotFoundError: If edge doesn't exist
        """
        with self._lock:
            if not self.has_edge(source, target):
                raise EdgeNotFoundError(source, target)
            
            for edge in self._edges:
                if edge.source == source and edge.target == target:
                    return edge
            
            raise EdgeNotFoundError(source, target)
    
    def remove_edge(self, source: str, target: str) -> DAGEdge:
        """
        Remove an edge between nodes.
        
        Args:
            source: Source node
            target: Target node
            
        Returns:
            The removed edge
            
        Raises:
            EdgeNotFoundError: If edge doesn't exist
        """
        with self._lock:
            if not self.has_edge(source, target):
                raise EdgeNotFoundError(source, target)
            
            # Find and remove edge
            edge_to_remove = None
            for edge in self._edges:
                if edge.source == source and edge.target == target:
                    edge_to_remove = edge
                    break
            
            if edge_to_remove:
                self._edges.discard(edge_to_remove)
            
            self._adjacency[source].discard(target)
            self._reverse_adjacency[target].discard(source)
            
            self._touch()
            self.logger.debug(f"Removed edge: {source} → {target}")
            
            return edge_to_remove
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """
        Get all dependencies of a node (nodes that must complete first).
        
        Args:
            node_id: Node to query
            
        Returns:
            List of dependency node IDs
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            return list(self._reverse_adjacency.get(node_id, set()))
    
    def get_dependents(self, node_id: str) -> List[str]:
        """
        Get all nodes that depend on this node.
        
        Args:
            node_id: Node to query
            
        Returns:
            List of dependent node IDs
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id)
            return list(self._adjacency.get(node_id, set()))
    
    # =========================================================================
    # GRAPH ALGORITHMS
    # =========================================================================
    
    def has_cycle(self) -> bool:
        """
        Check if DAG contains a cycle using DFS.
        
        Time complexity: O(V + E)
        
        Returns:
            True if cycle exists, False otherwise
        """
        with self._lock:
            if not self._nodes:
                return False
            
            # Track visited state
            WHITE, GRAY, BLACK = 0, 1, 2
            colors = {node_id: WHITE for node_id in self._nodes}
            
            def dfs(node_id: str) -> bool:
                """DFS with color tracking."""
                colors[node_id] = GRAY  # Being processed
                
                for neighbor in self._adjacency.get(node_id, set()):
                    if colors[neighbor] == GRAY:
                        return True  # Back edge = cycle
                    if colors[neighbor] == WHITE:
                        if dfs(neighbor):
                            return True
                
                colors[node_id] = BLACK  # Finished
                return False
            
            # Check all components
            for node_id in self._nodes:
                if colors[node_id] == WHITE:
                    if dfs(node_id):
                        return True
            
            return False
    
    def _find_cycle(self) -> List[str]:
        """Find nodes involved in a cycle."""
        with self._lock:
            WHITE, GRAY, BLACK = 0, 1, 2
            colors = {node_id: WHITE for node_id in self._nodes}
            parent = {}
            
            def dfs(node_id: str, path: List[str]) -> Optional[List[str]]:
                colors[node_id] = GRAY
                path = path + [node_id]
                
                for neighbor in self._adjacency.get(node_id, set()):
                    if colors[neighbor] == GRAY:
                        # Found cycle - extract it
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:] + [neighbor]
                    if colors[neighbor] == WHITE:
                        result = dfs(neighbor, path)
                        if result:
                            return result
                
                colors[node_id] = BLACK
                return None
            
            for node_id in self._nodes:
                if colors[node_id] == WHITE:
                    result = dfs(node_id, [])
                    if result:
                        return result
            
            return []
    
    def topological_sort(self) -> List[str]:
        """
        Get topological ordering of nodes using Kahn's algorithm.
        
        Time complexity: O(V + E)
        
        Returns:
            List of node IDs in topological order
            
        Raises:
            CyclicDependencyError: If DAG contains a cycle
        """
        with self._lock:
            if not self._nodes:
                return []
            
            # Calculate in-degrees
            in_degree = {node_id: 0 for node_id in self._nodes}
            for node_id in self._nodes:
                for neighbor in self._adjacency.get(node_id, set()):
                    in_degree[neighbor] += 1
            
            # Start with zero in-degree nodes (sorted by priority)
            queue = deque(
                sorted(
                    [n for n, d in in_degree.items() if d == 0],
                    key=lambda x: self._nodes[x].priority.value
                )
            )
            
            result = []
            
            while queue:
                node_id = queue.popleft()
                result.append(node_id)
                
                # Process neighbors
                neighbors = sorted(
                    self._adjacency.get(node_id, set()),
                    key=lambda x: self._nodes[x].priority.value
                )
                
                for neighbor in neighbors:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # Check if all nodes were processed
            if len(result) != len(self._nodes):
                cycle = self._find_cycle()
                raise CyclicDependencyError(cycle)
            
            return result
    
    def get_ready_tasks(self) -> List[str]:
        """
        Get nodes that are ready to execute.
        
        A node is ready if:
        - Status is NOT_STARTED
        - All dependencies are COMPLETED
        
        Returns:
            List of ready node IDs sorted by priority
        """
        with self._lock:
            ready = []
            
            for node_id, node in self._nodes.items():
                if node.status != NodeStatus.NOT_STARTED:
                    continue
                
                # Check all dependencies are complete
                dependencies = self._reverse_adjacency.get(node_id, set())
                all_complete = all(
                    self._nodes[dep].status == NodeStatus.COMPLETED
                    for dep in dependencies
                )
                
                if all_complete:
                    ready.append(node_id)
            
            # Sort by priority (lower = higher priority)
            return sorted(ready, key=lambda x: self._nodes[x].priority.value)
    
    def get_blocked_tasks(self) -> List[str]:
        """
        Get nodes that are blocked by incomplete dependencies.
        
        Returns:
            List of blocked node IDs with their blockers
        """
        with self._lock:
            blocked = []
            
            for node_id, node in self._nodes.items():
                if node.status != NodeStatus.NOT_STARTED:
                    continue
                
                dependencies = self._reverse_adjacency.get(node_id, set())
                incomplete_deps = [
                    dep for dep in dependencies
                    if self._nodes[dep].status != NodeStatus.COMPLETED
                ]
                
                if incomplete_deps:
                    blocked.append(node_id)
            
            return blocked
    
    def get_critical_path(self) -> List[str]:
        """
        Find the critical path (longest dependency chain).
        
        Returns:
            List of node IDs forming the critical path
        """
        with self._lock:
            if not self._nodes:
                return []
            
            # Get topological order
            try:
                topo_order = self.topological_sort()
            except CyclicDependencyError:
                return []
            
            # Calculate distances from start
            dist = {node_id: 0 for node_id in self._nodes}
            parent = {node_id: None for node_id in self._nodes}
            
            for node_id in topo_order:
                for neighbor in self._adjacency.get(node_id, set()):
                    if dist[node_id] + 1 > dist[neighbor]:
                        dist[neighbor] = dist[node_id] + 1
                        parent[neighbor] = node_id
            
            # Find node with maximum distance
            end_node = max(dist, key=dist.get)
            
            # Reconstruct path
            path = []
            current = end_node
            while current is not None:
                path.append(current)
                current = parent[current]
            
            return list(reversed(path))
    
    def get_parallel_groups(self) -> List[List[str]]:
        """
        Get groups of tasks that can run in parallel.
        
        Groups are organized by dependency level.
        
        Returns:
            List of groups, each group contains parallelizable tasks
        """
        with self._lock:
            if not self._nodes:
                return []
            
            # Calculate levels using BFS from roots
            levels: Dict[str, int] = {}
            
            # Find roots (no dependencies)
            roots = [
                node_id for node_id in self._nodes
                if not self._reverse_adjacency.get(node_id)
            ]
            
            # BFS to assign levels
            queue = deque((root, 0) for root in roots)
            while queue:
                node_id, level = queue.popleft()
                
                if node_id in levels:
                    levels[node_id] = max(levels[node_id], level)
                else:
                    levels[node_id] = level
                
                for neighbor in self._adjacency.get(node_id, set()):
                    queue.append((neighbor, level + 1))
            
            # Group by level
            groups: Dict[int, List[str]] = {}
            for node_id, level in levels.items():
                if level not in groups:
                    groups[level] = []
                groups[level].append(node_id)
            
            # Sort by level and priority within each group
            return [
                sorted(groups[level], key=lambda x: self._nodes[x].priority.value)
                for level in sorted(groups.keys())
            ]
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_statistics(self) -> DAGStatistics:
        """
        Get comprehensive statistics about the DAG.
        
        Returns:
            DAGStatistics with counts and metrics
        """
        with self._lock:
            status_counts = {status: 0 for status in NodeStatus}
            for node in self._nodes.values():
                status_counts[node.status] += 1
            
            parallel_groups = self.get_parallel_groups()
            width = max(len(g) for g in parallel_groups) if parallel_groups else 0
            
            critical_path = self.get_critical_path()
            
            return DAGStatistics(
                node_count=len(self._nodes),
                edge_count=len(self._edges),
                completed_count=status_counts[NodeStatus.COMPLETED],
                failed_count=status_counts[NodeStatus.FAILED],
                in_progress_count=status_counts[NodeStatus.IN_PROGRESS],
                blocked_count=status_counts[NodeStatus.BLOCKED],
                not_started_count=status_counts[NodeStatus.NOT_STARTED],
                depth=len(critical_path),
                width=width,
                critical_path_length=len(critical_path)
            )
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DAG to dictionary for serialization.
        
        Returns:
            Dictionary representation of DAG
        """
        with self._lock:
            return {
                "name": self.name,
                "description": self.description,
                "version": self._version,
                "created_at": self._created_at.isoformat(),
                "updated_at": self._updated_at.isoformat(),
                "nodes": [node.to_dict() for node in self._nodes.values()],
                "edges": [edge.to_dict() for edge in self._edges],
            }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert DAG to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DAG:
        """
        Create DAG from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Reconstructed DAG
        """
        dag = cls(
            name=data.get("name", "unnamed"),
            description=data.get("description", "")
        )
        
        # Restore nodes
        for node_data in data.get("nodes", []):
            node = DAGNode.from_dict(node_data)
            dag.add_node_object(node)
        
        # Restore edges
        for edge_data in data.get("edges", []):
            edge = DAGEdge.from_dict(edge_data)
            dag.add_edge(
                edge.source, 
                edge.target, 
                edge.edge_type, 
                edge.metadata,
                validate=False  # Skip validation for restoration
            )
        
        # Restore metadata
        dag._version = data.get("version", 1)
        if data.get("created_at"):
            dag._created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            dag._updated_at = datetime.fromisoformat(data["updated_at"])
        
        return dag
    
    @classmethod
    def from_json(cls, json_str: str) -> DAG:
        """Create DAG from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def clear(self) -> None:
        """Remove all nodes and edges."""
        with self._lock:
            self._nodes.clear()
            self._edges.clear()
            self._adjacency.clear()
            self._reverse_adjacency.clear()
            self._touch()
            self.logger.info(f"Cleared DAG: {self.name}")
    
    def _touch(self) -> None:
        """Update modification timestamp and version."""
        self._updated_at = datetime.now()
        self._version += 1
    
    def __len__(self) -> int:
        """Get number of nodes."""
        return self.node_count
    
    def __contains__(self, node_id: str) -> bool:
        """Check if node exists."""
        return self.has_node(node_id)
    
    def __iter__(self) -> Iterator[DAGNode]:
        """Iterate over nodes in topological order."""
        try:
            order = self.topological_sort()
            for node_id in order:
                yield self._nodes[node_id]
        except CyclicDependencyError:
            yield from self._nodes.values()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DAG(name='{self.name}', nodes={self.node_count}, edges={self.edge_count})"


# ==============================================================================
# GLOBAL INSTANCE (Optional)
# ==============================================================================

_global_dag: Optional[DAG] = None


def get_global_dag() -> DAG:
    """Get or create global DAG instance."""
    global _global_dag
    if _global_dag is None:
        _global_dag = DAG(name="global")
    return _global_dag


def set_global_dag(dag: DAG) -> None:
    """Set global DAG instance."""
    global _global_dag
    _global_dag = dag
