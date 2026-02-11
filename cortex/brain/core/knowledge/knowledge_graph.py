# AC-ID: IR-004-01 - CORTEX LENS Knowledge Graph Builder
"""
CORTEX LENS Knowledge Graph Module (IR-004-01).

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-004-01 - CORTEX LENS Knowledge Graph Builder

This module implements the unified knowledge graph representation that
aggregates intelligence findings from multiple sources:

1. AST Intelligence (IR-001-01)
   - Function/class definitions, parameters, return types
   - Module structure, import statements

2. Git History Analysis (IR-001-02)
   - Commit history, file change frequency
   - Author context, temporal patterns

3. Code Comments & Documentation (IR-001-03)
   - Docstrings, inline comments
   - README and documentation files

4. Relationship Traversal (IR-001-04)
   - Call graphs, dependency chains
   - Cross-file references, API relationships

5. API Relationship Discovery (IR-004-01)
   - REST endpoints, GraphQL schemas
   - Microservice interactions

6. Database Schema Analysis (IR-004-01)
   - Table definitions, foreign keys
   - ORM model relationships

The knowledge graph serves as the unified queryable structure for the
Intent Reflection Protocol and Comprehension Loop.

Architecture:
- GraphNode: Represents entities (functions, classes, APIs, tables, etc.)
- GraphEdge: Represents relationships (calls, imports, depends_on, etc.)
- KnowledgeGraph: Container for nodes, edges, and metadata
- KnowledgeGraphBuilder: Orchestrates graph construction from sources

Core Responsibilities:
1. Aggregate findings from multiple intelligence sources
2. Build unified knowledge graph with all node and edge types
3. Provide rich query and traversal operations
4. Support incremental updates on workspace changes
5. Serialize/deserialize for persistence and transmission
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# =============================================================================
# ENUMS
# =============================================================================

class NodeType(Enum):
    """Types of nodes in the knowledge graph."""

    # Code Structure
    MODULE = "module"
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    DECORATOR = "decorator"

    # API Layer
    API_ENDPOINT = "api_endpoint"
    API_MODEL = "api_model"

    # Database Layer
    DATABASE_MODEL = "database_model"
    DATABASE_TABLE = "database_table"
    DATABASE_COLUMN = "database_column"
    DATABASE_INDEX = "database_index"

    # Configuration & Infrastructure
    CONFIGURATION = "configuration"
    ENVIRONMENT = "environment"
    SERVICE = "service"

    # Patterns & Metadata
    PATTERN = "pattern"
    DESIGN_PATTERN = "design_pattern"
    ANTIPATTERN = "antipattern"


class EdgeType(Enum):
    """Types of relationships between nodes."""

    # Code Flow
    CALLS = "calls"
    DEFINED_IN = "defined_in"
    IMPORTS = "imports"
    EXPORTED_FROM = "exported_from"

    # Structural
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    CONTAINS = "contains"
    PART_OF = "part_of"

    # Dependencies
    DEPENDS_ON = "depends_on"
    USED_BY = "used_by"
    REQUIRED_BY = "required_by"
    MODIFIES = "modifies"

    # API & Database
    SERVES = "serves"  # API serves model
    PERSISTS = "persists"  # Model persists to table
    QUERIES = "queries"  # Code queries table
    CONSUMES = "consumes"  # Service consumes API

    # Relationships
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"

    # Change & History
    CHANGED_BY = "changed_by"  # File changed by commit
    AUTHORED_BY = "authored_by"  # Authored by person


# =============================================================================
# DATA CLASSES - Graph Structures
# =============================================================================

@dataclass
class GraphNode:
    """
    Represents a single entity in the knowledge graph.

    A node can represent code entities (functions, classes), infrastructure
    components (APIs, databases), or metadata (patterns, configurations).

    Attributes:
        id: Unique identifier (typically kebab-case)
        node_type: NodeType enum indicating entity kind
        name: Human-readable name
        file: Source file path
        properties: Additional metadata (line numbers, parameters, etc.)
        source: Which intelligence source discovered this node
        discovered_at: When this node was discovered
        confidence: Confidence score (0.0-1.0) for discovery
    """

    id: str
    node_type: NodeType
    name: str
    file: str
    properties: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    discovered_at: Optional[str] = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Initialize timestamps if needed."""
        if self.discovered_at is None:
            self.discovered_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "name": self.name,
            "file": self.file,
            "properties": self.properties,
            "source": self.source,
            "discovered_at": self.discovered_at,
            "confidence": round(self.confidence, 3),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GraphNode:
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            node_type=NodeType(data["node_type"]),
            name=data["name"],
            file=data["file"],
            properties=data.get("properties", {}),
            source=data.get("source", "unknown"),
            discovered_at=data.get("discovered_at"),
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class GraphEdge:
    """
    Represents a relationship between two nodes.

    Edges model dependencies, call relationships, API contracts,
    database relationships, and other structural connections.

    Attributes:
        source_id: ID of source node
        target_id: ID of target node
        relationship: EdgeType enum
        weight: Strength of relationship (0.0-1.0, higher = stronger)
        properties: Additional metadata
        discovered_at: When this edge was discovered
    """

    source_id: str
    target_id: str
    relationship: EdgeType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    discovered_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize timestamps if needed."""
        if self.discovered_at is None:
            self.discovered_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary for serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship.value,
            "weight": round(self.weight, 3),
            "properties": self.properties,
            "discovered_at": self.discovered_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GraphEdge:
        """Create edge from dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship=EdgeType(data["relationship"]),
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {}),
            discovered_at=data.get("discovered_at"),
        )


@dataclass
class GraphMetadata:
    """Metadata about the knowledge graph."""

    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    workspace_root: Optional[str] = None
    source_count: int = 0
    last_build_duration_ms: int = 0
    is_stale: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# =============================================================================
# KNOWLEDGE GRAPH
# =============================================================================

class KnowledgeGraph:
    """
    Unified knowledge graph aggregating intelligence from multiple sources.

    The knowledge graph is the central data structure for CORTEX LENS,
    serving as the foundation for holistic intent understanding.

    It maintains:
    - nodes: Dict mapping node ID to GraphNode
    - edges: List of GraphEdge relationships
    - metadata: GraphMetadata tracking

    Query Operations:
    - find_node(id): Find node by ID
    - query_nodes_by_type(type): Find all nodes of given type
    - query_nodes_by_file(file): Find all nodes in file
    - find_edges_from(node_id, relation_type): Outgoing edges
    - find_edges_to(node_id, relation_type): Incoming edges
    - get_neighbors(node_id, relation_type): Adjacent nodes
    - get_all_reachable(node_id): All reachable nodes (transitive)
    - find_path(source_id, target_id): Path between nodes
    """

    def __init__(self) -> None:
        """Initialize empty knowledge graph."""
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.metadata = GraphMetadata()

    # =========================================================================
    # Node Operations
    # =========================================================================

    def add_node(self, node: GraphNode) -> None:
        """Add or update a node in the graph."""
        self.nodes[node.id] = node
        self.metadata.last_updated = datetime.now().isoformat()

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its edges."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove all edges involving this node
            self.edges = [
                e for e in self.edges
                if e.source_id != node_id and e.target_id != node_id
            ]
            self.metadata.last_updated = datetime.now().isoformat()

    def find_node(self, node_id: str) -> Optional[GraphNode]:
        """Find a node by ID."""
        return self.nodes.get(node_id)

    def query_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Find all nodes of a given type."""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def query_nodes_by_file(self, file_path: str) -> List[GraphNode]:
        """Find all nodes defined in a file."""
        return [node for node in self.nodes.values() if node.file == file_path]

    def query_nodes_by_name(self, name: str) -> List[GraphNode]:
        """Find nodes by name (supports partial matching)."""
        return [
            node for node in self.nodes.values()
            if name.lower() in node.name.lower()
        ]

    # =========================================================================
    # Edge Operations
    # =========================================================================

    def add_edge(self, edge: GraphEdge) -> None:
        """Add a relationship edge between two nodes."""
        # Verify both nodes exist
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError(
                f"Edge references non-existent node: {edge.source_id} -> {edge.target_id}"
            )

        self.edges.append(edge)
        self.metadata.last_updated = datetime.now().isoformat()

    def remove_edge(self, edge: GraphEdge) -> None:
        """Remove a specific edge."""
        self.edges = [
            e for e in self.edges
            if not (e.source_id == edge.source_id and
                    e.target_id == edge.target_id and
                    e.relationship == edge.relationship)
        ]
        self.metadata.last_updated = datetime.now().isoformat()

    def find_edges_from(
        self,
        source_id: str,
        relationship: Optional[EdgeType] = None
    ) -> List[GraphEdge]:
        """Find all outgoing edges from a node."""
        edges = [e for e in self.edges if e.source_id == source_id]
        if relationship:
            edges = [e for e in edges if e.relationship == relationship]
        return edges

    def find_edges_to(
        self,
        target_id: str,
        relationship: Optional[EdgeType] = None
    ) -> List[GraphEdge]:
        """Find all incoming edges to a node."""
        edges = [e for e in self.edges if e.target_id == target_id]
        if relationship:
            edges = [e for e in edges if e.relationship == relationship]
        return edges

    # =========================================================================
    # Query Operations
    # =========================================================================

    def get_neighbors(
        self,
        node_id: str,
        relationship: Optional[EdgeType] = None
    ) -> List[GraphNode]:
        """Get all adjacent nodes connected by specific relationship type."""
        edges = self.find_edges_from(node_id, relationship)
        neighbors = []
        for edge in edges:
            neighbor = self.find_node(edge.target_id)
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_reverse_neighbors(
        self,
        node_id: str,
        relationship: Optional[EdgeType] = None
    ) -> List[GraphNode]:
        """Get all nodes pointing to this node (reverse direction)."""
        edges = self.find_edges_to(node_id, relationship)
        neighbors = []
        for edge in edges:
            neighbor = self.find_node(edge.source_id)
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_all_reachable(self, start_id: str) -> Set[str]:
        """
        Get all nodes reachable from a starting node (transitive closure).

        Uses breadth-first search to find all transitively reachable nodes.
        """
        if start_id not in self.nodes:
            return set()

        visited: Set[str] = set()
        queue: List[str] = [start_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor.id not in visited:
                    queue.append(neighbor.id)

        visited.discard(start_id)  # Don't include start node itself
        return visited

    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS.

        Returns list of node IDs forming a path, or None if no path exists.
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        if source_id == target_id:
            return [source_id]

        visited: Set[str] = set()
        queue: List[Tuple[str, List[str]]] = [(source_id, [source_id])]

        while queue:
            current, path = queue.pop(0)

            if current in visited:
                continue
            visited.add(current)

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                new_path = path + [neighbor.id]
                if neighbor.id == target_id:
                    return new_path
                if neighbor.id not in visited:
                    queue.append((neighbor.id, new_path))

        return None

    # =========================================================================
    # Impact Analysis
    # =========================================================================

    def get_change_impact(self, node_id: str) -> Dict[str, Any]:
        """
        Analyze the impact of changing a node.

        Returns downstream dependencies and potentially affected nodes.
        """
        if node_id not in self.nodes:
            return {}

        node = self.nodes[node_id]

        return {
            "node": node.to_dict(),
            "direct_dependents": [
                n.to_dict() for n in self.get_reverse_neighbors(node_id)
            ],
            "all_dependents": list(
                self.nodes[nid].to_dict()
                for nid in self._find_all_dependents(node_id)
            ),
            "direct_dependencies": [
                n.to_dict() for n in self.get_neighbors(node_id)
            ],
            "all_dependencies": list(
                self.nodes[nid].to_dict()
                for nid in self.get_all_reachable(node_id)
            ),
        }

    def _find_all_dependents(self, node_id: str) -> Set[str]:
        """Find all nodes that depend on the given node."""
        dependents: Set[str] = set()
        queue: List[str] = [node_id]
        visited: Set[str] = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            reverse_neighbors = self.get_reverse_neighbors(current)
            for neighbor in reverse_neighbors:
                if neighbor.id not in visited:
                    dependents.add(neighbor.id)
                    queue.append(neighbor.id)

        return dependents

    # =========================================================================
    # Utilities
    # =========================================================================

    def mark_stale(self) -> None:
        """Mark graph as stale due to workspace changes."""
        self.metadata.is_stale = True

    def is_stale(self) -> bool:
        """Check if graph is stale."""
        return self.metadata.is_stale

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the graph."""
        node_types: Dict[str, int] = {}
        for node in self.nodes.values():
            key = node.node_type.value
            node_types[key] = node_types.get(key, 0) + 1

        edge_types: Dict[str, int] = {}
        for edge in self.edges:
            key = edge.relationship.value
            edge_types[key] = edge_types.get(key, 0) + 1

        file_nodes: Dict[str, int] = {}
        for node in self.nodes.values():
            key = node.file
            file_nodes[key] = file_nodes.get(key, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "files": file_nodes,
            "average_edges_per_node": (
                len(self.edges) / len(self.nodes) if self.nodes else 0
            ),
        }

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert entire graph to dictionary."""
        return {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata.to_dict(),
        }

    def to_json(self) -> str:
        """Serialize graph to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeGraph:
        """Reconstruct graph from dictionary."""
        graph = cls()

        # Restore nodes
        for node_data in data.get("nodes", {}).values():
            graph.add_node(GraphNode.from_dict(node_data))

        # Restore edges
        for edge_data in data.get("edges", []):
            graph.add_edge(GraphEdge.from_dict(edge_data))

        # Restore metadata
        metadata_data = data.get("metadata", {})
        graph.metadata.version = metadata_data.get("version", "1.0")
        graph.metadata.created_at = metadata_data.get("created_at", datetime.now().isoformat())
        graph.metadata.last_updated = metadata_data.get("last_updated", datetime.now().isoformat())
        graph.metadata.is_stale = metadata_data.get("is_stale", False)

        return graph

    @classmethod
    def from_json(cls, json_str: str) -> KnowledgeGraph:
        """Deserialize graph from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# =============================================================================
# KNOWLEDGE GRAPH BUILDER
# =============================================================================

class KnowledgeGraphBuilder:
    """
    Orchestrates knowledge graph construction from multiple intelligence sources.

    The builder aggregates findings from:
    1. AST Intelligence (src/core/intelligence/ast_intelligence.py)
    2. Git History Analyzer (src/core/intelligence/git_history_analyzer.py)
    3. Comment Analyzer (src/core/intelligence/comment_analyzer.py)
    4. Relationship Traversal (src/core/intelligence/relationship_traversal.py)

    And integrates additional analysis for:
    5. API Relationships
    6. Database Schema

    Usage:
        builder = KnowledgeGraphBuilder()
        graph = builder.build()

        # Query the graph
        functions = graph.query_nodes_by_type(NodeType.FUNCTION)
        impact = graph.get_change_impact("func_id")
    """

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        """
        Initialize builder.

        Args:
            workspace_root: Root directory of workspace to analyze
        """
        self.workspace_root = workspace_root or str(Path.cwd())
        self.graph: Optional[KnowledgeGraph] = None

    def build(self) -> KnowledgeGraph:
        """
        Build knowledge graph from all sources.

        This is the main orchestration method that:
        1. Initializes empty graph
        2. Scans AST across workspace
        3. Analyzes git history
        4. Extracts comments and documentation
        5. Traverses relationships
        6. Discovers API definitions
        7. Analyzes database schema
        8. Integrates all findings into unified graph

        Returns:
            Fully populated KnowledgeGraph
        """
        graph = KnowledgeGraph()
        graph.metadata.workspace_root = self.workspace_root

        start_time = datetime.now()

        # Stage 1: Load AST findings
        self._integrate_ast_findings(graph)

        # Stage 2: Load git history
        self._integrate_git_findings(graph)

        # Stage 3: Extract comments and docs
        self._integrate_comment_findings(graph)

        # Stage 4: Traverse relationships
        self._integrate_relationship_findings(graph)

        # Stage 5: Discover API relationships
        self._integrate_api_findings(graph)

        # Stage 6: Analyze database schema
        self._integrate_database_findings(graph)

        # Update metadata
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        graph.metadata.last_build_duration_ms = duration_ms
        graph.metadata.is_stale = False

        self.graph = graph
        return graph

    def _integrate_ast_findings(self, graph: KnowledgeGraph) -> None:
        """Integrate AST analysis findings into graph."""
        # Placeholder for AST integration
        # This would use src/core/intelligence/ast_intelligence.py
        # to scan Python files and extract functions, classes, etc.
        pass

    def _integrate_git_findings(self, graph: KnowledgeGraph) -> None:
        """Integrate git history findings into graph."""
        # Placeholder for git history integration
        # This would use src/core/intelligence/git_history_analyzer.py
        # to extract commit history and change patterns
        pass

    def _integrate_comment_findings(self, graph: KnowledgeGraph) -> None:
        """Integrate code comment and documentation findings."""
        # Placeholder for comment analysis
        # This would use src/core/intelligence/comment_analyzer.py
        # to extract docstrings and inline comments
        pass

    def _integrate_relationship_findings(self, graph: KnowledgeGraph) -> None:
        """Integrate relationship traversal findings."""
        # Placeholder for relationship traversal
        # This would use src/core/intelligence/relationship_traversal.py
        # to discover call graphs and dependencies
        pass

    def _integrate_api_findings(self, graph: KnowledgeGraph) -> None:
        """Discover and integrate API relationships."""
        # Placeholder for API discovery
        # Scan for REST endpoints, GraphQL schemas
        # Extract API documentation
        pass

    def _integrate_database_findings(self, graph: KnowledgeGraph) -> None:
        """Analyze and integrate database schema relationships."""
        # Placeholder for database schema analysis
        # Extract table definitions, foreign keys
        # Model ORM relationships
        pass

    def update_incremental(self, changed_files: List[str]) -> KnowledgeGraph:
        """
        Incrementally update graph after workspace changes.

        Args:
            changed_files: List of files that changed

        Returns:
            Updated KnowledgeGraph
        """
        if self.graph is None:
            return self.build()

        # Mark graph as stale to trigger fresh build
        self.graph.mark_stale()

        # In a full implementation, could do incremental updates
        # For now, rebuild from scratch
        return self.build()
