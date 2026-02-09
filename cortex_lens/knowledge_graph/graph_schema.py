"""
Phase 66 Stage 2: Knowledge Graph Schema

Defines the property graph schema for code knowledge storage.

AC_START: AC-PHASE66-S2-002
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the knowledge graph"""
    FILE = "File"
    CLASS = "Class"
    FUNCTION = "Function"
    IMPORT = "Import"
    TEST = "Test"
    MODULE = "Module"


class EdgeType(Enum):
    """Types of edges (relationships) in the knowledge graph"""
    CALLS = "calls"
    IMPORTS = "imports"
    TESTS = "tests"
    DEPENDS_ON = "depends_on"
    WRITES_TO = "writes_to"
    READS_FROM = "reads_from"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"


@dataclass
class Node:
    """
    Node in the knowledge graph.
    
    Represents code elements (files, classes, functions, etc.)
    with properties stored as JSON.
    
    Attributes:
        id: Unique node identifier (auto-generated)
        node_type: Type of node (File, Class, Function, etc.)
        name: Human-readable name
        properties: Additional metadata (JSON-serializable dict)
    
    Example:
        >>> node = Node(
        ...     id=1,
        ...     node_type="File",
        ...     name="user_controller.py",
        ...     properties={"path": "/controllers/user_controller.py", "lines": 50}
        ... )
    """
    
    id: Optional[int]
    node_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "node_type": self.node_type,
            "name": self.name,
            "properties": self.properties,
        }


@dataclass
class Edge:
    """
    Edge (relationship) in the knowledge graph.
    
    Represents relationships between code elements with
    directional semantics and optional properties.
    
    Attributes:
        id: Unique edge identifier (auto-generated)
        source_id: ID of source node
        target_id: ID of target node
        edge_type: Type of relationship (calls, imports, etc.)
        properties: Additional metadata (JSON-serializable dict)
    
    Example:
        >>> edge = Edge(
        ...     id=1,
        ...     source_id=10,
        ...     target_id=20,
        ...     edge_type="imports",
        ...     properties={"line_number": 5}
        ... )
    """
    
    id: Optional[int]
    source_id: int
    target_id: int
    edge_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "properties": self.properties,
        }


@dataclass
class GraphQuery:
    """
    Query specification for graph traversal.
    
    Defines parameters for querying the knowledge graph,
    including starting point, relationship types, and depth.
    
    Attributes:
        start_node_id: Starting node for traversal
        edge_types: List of edge types to follow (empty = all types)
        depth: Maximum traversal depth (1 = direct neighbors)
        limit: Maximum number of results to return
    """
    
    start_node_id: int
    edge_types: List[str] = field(default_factory=list)
    depth: int = 1
    limit: Optional[int] = None


# SQL Schema Definitions

SCHEMA_SQL = """
-- Nodes table: stores all graph nodes
CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_type TEXT NOT NULL,
    name TEXT NOT NULL,
    properties TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Edges table: stores all relationships
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    edge_type TEXT NOT NULL,
    properties TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_node_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_edge_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edge_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edge_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edge_source_type ON edges(source_id, edge_type);
"""


# AC_COMPLETE: AC-PHASE66-S2-002 ✅ Graph schema defined
