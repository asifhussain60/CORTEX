"""Knowledge Graph - Query and inference engine.

Provides graph-based knowledge storage and retrieval with support for
relationships, inference rules, and semantic queries.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum


class NodeType(Enum):
    """Types of nodes in knowledge graph."""

    ENTITY = "entity"
    CONCEPT = "concept"
    OPERATION = "operation"
    RULE = "rule"
    FACT = "fact"
    GENERIC = "generic"


class RelationType(Enum):
    """Types of relationships in knowledge graph."""

    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    IS_A = "is_a"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    IMPLEMENTS = "implements"


class EdgeType(Enum):
    """Types of edges in knowledge graph (alias for RelationType)."""

    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    IS_A = "is_a"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    IMPLEMENTS = "implements"


@dataclass
class Node:
    """Knowledge graph node.

    Attributes:
        id: Unique node identifier.
        label: Human-readable label.
        properties: Node properties dictionary.
        type: Node type category.
    """

    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    type: str = "generic"


@dataclass
class Edge:
    """Knowledge graph edge (relationship).

    Attributes:
        source_id: Source node ID.
        target_id: Target node ID.
        relation: Relationship type.
        properties: Edge properties.
    """

    source_id: str
    target_id: str
    relation: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """Graph-based knowledge store with inference.

    Attributes:
        nodes: Dictionary of nodes by ID.
        edges: List of edges (relationships).
        _index: Quick lookup index for nodes by type.
    """

    def __init__(self) -> None:
        """Initialize knowledge graph."""
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._index: Dict[str, Set[str]] = {}

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str = "generic",
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a node to the graph.

        Args:
            node_id: Unique node identifier.
            label: Human-readable label.
            node_type: Type category (default: "generic").
            properties: Optional node properties.
        """
        node = Node(
            id=node_id, label=label, type=node_type, properties=properties or {}
        )
        self.nodes[node_id] = node

        # Update index
        if node_type not in self._index:
            self._index[node_type] = set()
        self._index[node_type].add(node_id)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: RelationType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an edge (relationship) to the graph.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            relation: Relationship type.
            properties: Optional edge properties.

        Raises:
            ValueError: If nodes don't exist.
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"One or both nodes not found in graph")

        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            properties=properties or {},
        )
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID.

        Args:
            node_id: Node identifier.

        Returns:
            Node object or None if not found.
        """
        return self.nodes.get(node_id)

    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type.

        Args:
            node_type: Type category.

        Returns:
            List of matching nodes.
        """
        node_ids = self._index.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]

    def get_outgoing_edges(self, source_id: str) -> List[Edge]:
        """Get all outgoing edges from a node.

        Args:
            source_id: Source node ID.

        Returns:
            List of outgoing edges.
        """
        return [e for e in self.edges if e.source_id == source_id]

    def get_incoming_edges(self, target_id: str) -> List[Edge]:
        """Get all incoming edges to a node.

        Args:
            target_id: Target node ID.

        Returns:
            List of incoming edges.
        """
        return [e for e in self.edges if e.target_id == target_id]

    def query(self, query_type: str, **kwargs: Any) -> List[Any]:
        """Execute a query on the knowledge graph.

        Args:
            query_type: Type of query (e.g., "by_type", "related_to").
            **kwargs: Query parameters.

        Returns:
            List of matching results.
        """
        if query_type == "by_type":
            node_type = kwargs.get("type")
            return self.get_nodes_by_type(node_type)
        elif query_type == "neighbors":
            node_id = kwargs.get("node_id")
            return self._get_neighbors(node_id)
        elif query_type == "path":
            source = kwargs.get("source")
            target = kwargs.get("target")
            return self._find_paths(source, target)
        return []

    def _get_neighbors(self, node_id: str) -> List[Node]:
        """Get all neighbors of a node.

        Args:
            node_id: Node identifier.

        Returns:
            List of neighboring nodes.
        """
        neighbors = []
        for edge in self.edges:
            if edge.source_id == node_id:
                neighbor = self.get_node(edge.target_id)
                if neighbor:
                    neighbors.append(neighbor)
            elif edge.target_id == node_id:
                neighbor = self.get_node(edge.source_id)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def _find_paths(
        self, source: str, target: str, max_depth: int = 5
    ) -> List[List[str]]:
        """Find all paths between two nodes.

        Args:
            source: Source node ID.
            target: Target node ID.
            max_depth: Maximum path depth (default: 5).

        Returns:
            List of paths (each path is a list of node IDs).
        """
        paths = []
        visited: Set[str] = set()

        def dfs(current: str, path: List[str]) -> None:
            if len(path) > max_depth:
                return
            if current == target:
                paths.append(path)
                return

            for edge in self.edges:
                if edge.source_id == current and edge.target_id not in visited:
                    visited.add(edge.target_id)
                    dfs(edge.target_id, path + [edge.target_id])
                    visited.remove(edge.target_id)

        dfs(source, [source])
        return paths

    def __len__(self) -> int:
        """Get total number of nodes.

        Returns:
            Node count.
        """
        return len(self.nodes)


# Aliases for backward compatibility
GraphNode = Node
GraphEdge = Edge


class KnowledgeGraphBuilder:
    """Builder for constructing knowledge graphs fluently.

    Provides a fluent interface for building and modifying knowledge graphs.
    """

    def __init__(self) -> None:
        """Initialize the knowledge graph builder."""
        self.graph = KnowledgeGraph()

    def add_node(
        self, node_id: str, label: str, node_type: str = "generic", **properties
    ) -> "KnowledgeGraphBuilder":
        """Add a node to the graph.

        Args:
            node_id: Node identifier.
            label: Human-readable label.
            node_type: Node type category.
            **properties: Additional node properties.

        Returns:
            Self for chaining.
        """
        self.graph.add_node(node_id, label, node_type, properties)
        return self

    def add_edge(
        self, source_id: str, target_id: str, relation: RelationType, **properties
    ) -> "KnowledgeGraphBuilder":
        """Add an edge (relationship) to the graph.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            relation: Relationship type.
            **properties: Additional edge properties.

        Returns:
            Self for chaining.
        """
        self.graph.add_edge(source_id, target_id, relation, properties)
        return self

    def build(self) -> KnowledgeGraph:
        """Build and return the knowledge graph.

        Returns:
            Constructed KnowledgeGraph.
        """
        return self.graph

    def get_graph(self) -> KnowledgeGraph:
        """Get the current graph instance.

        Returns:
            Current KnowledgeGraph.
        """
        return self.graph


__all__ = [
    "KnowledgeGraph",
    "KnowledgeGraphBuilder",
    "Node",
    "Edge",
    "NodeType",
    "RelationType",
    "EdgeType",
    "GraphNode",
    "GraphEdge",
]


