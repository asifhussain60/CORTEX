"""
Phase 66 Stage 2: Knowledge Graph Query MCP Tool

Exposes knowledge graph querying capabilities via MCP for Copilot Chat.

AC_START: AC-PHASE66-S2-MCP-001
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from cortex.mcp.server import Tool
    from cortex_lens.knowledge_graph.graph_query import GraphQuery
    from cortex_lens.knowledge_graph.graph_storage import GraphStorage
    _HAS_CORTEX = True
except ImportError:
    # Graceful fallback for environments without full CORTEX
    Tool = object  # type: ignore
    GraphStorage = object  # type: ignore
    GraphQuery = object  # type: ignore
    _HAS_CORTEX = False

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGraphQueryResult:
    """Result from knowledge graph query."""

    success: bool
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    query_time_ms: float
    error: Optional[str] = None


class KnowledgeGraphQueryTool(Tool):
    """
    MCP tool for querying CORTEX knowledge graph.

    Enables relationship queries like:
    - "Which files call UserRepository.save()?"
    - "What tests cover the authentication module?"
    - "Show me the dependency chain from API to database"

    Example:
        >>> tool = KnowledgeGraphQueryTool()
        >>> result = tool.execute(
        ...     query_type="find_callers",
        ...     target="UserRepository.save",
        ...     depth=2
        ... )
        >>> print(f"Found {len(result.nodes)} callers")
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize knowledge graph query tool.

        Args:
            db_path: Path to knowledge graph database (defaults to .cortex/knowledge_graph.db)
        """
        # Tool is an ABC - no need to call super().__init__()

        if db_path is None:
            db_path = Path(".cortex/knowledge_graph.db")

        self.db_path = db_path
        self.storage: Optional[Any] = None
        self.query_engine: Optional[Any] = None

    @property
    def definition(self) -> "ToolDefinition":  # type: ignore
        """Get tool definition for MCP registration."""
        from cortex.mcp.server import ToolDefinition, ToolParameter

        return ToolDefinition(
            name="cortex_knowledge_graph_query",
            description="Query CORTEX knowledge graph for code relationships and dependencies",
            parameters=[
                ToolParameter(
                    name="query_type",
                    type="string",
                    required=True,
                    description="Query type: find_callers, find_dependencies, find_path, find_related",
                    enum=["find_callers", "find_dependencies", "find_path", "find_related"]
                ),
                ToolParameter(
                    name="target",
                    type="string",
                    required=True,
                    description="Target identifier (file path, class name, function name)"
                ),
                ToolParameter(
                    name="edge_type",
                    type="string",
                    required=False,
                    description="Edge type filter: calls, imports, tests, depends_on, writes_to",
                    default="calls",
                    enum=["calls", "imports", "tests", "depends_on", "writes_to", "reads_from"]
                ),
                ToolParameter(
                    name="depth",
                    type="integer",
                    required=False,
                    description="Maximum traversal depth (default: 2)",
                    default=2,
                    min_value=1,
                    max_value=5
                ),
                ToolParameter(
                    name="destination",
                    type="string",
                    required=False,
                    description="Destination node for find_path queries"
                )
            ],
            metadata={
                "category": "analysis",
                "phase": "phase-66-s2",
                "performance": "<100ms typical"
            }
        )

    def _ensure_initialized(self) -> bool:
        """Ensure storage and query engine are initialized."""
        if not self.db_path.exists():
            logger.warning(f"Knowledge graph database not found: {self.db_path}")
            return False

        if self.storage is None:
            try:
                self.storage = GraphStorage(self.db_path)
                self.query_engine = GraphQuery(self.storage)
                logger.info(f"Knowledge graph loaded from {self.db_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize knowledge graph: {e}")
                return False

        return True

    def execute(self, **kwargs) -> KnowledgeGraphQueryResult:
        """
        Execute knowledge graph query.

        Args:
            query_type: Type of query (find_callers, find_dependencies, find_path, etc.)
            target: Target node identifier (file path, class name, function name)
            edge_type: Edge type filter (calls, imports, tests, depends_on)
            depth: Maximum traversal depth (default: 2)
            repo_path: Repository path for context (optional)

        Returns:
            KnowledgeGraphQueryResult with nodes, edges, and metadata
        """
        import time
        start_time = time.time()

        try:
            if not self._ensure_initialized():
                return KnowledgeGraphQueryResult(
                    success=False,
                    nodes=[],
                    edges=[],
                    query_time_ms=0.0,
                    error="Knowledge graph not initialized. Run LENS analysis first."
                )

            query_type = kwargs.get("query_type", "find_callers")
            target = kwargs.get("target")
            edge_type = kwargs.get("edge_type", "calls")
            depth = kwargs.get("depth", 2)

            if not target:
                return KnowledgeGraphQueryResult(
                    success=False,
                    nodes=[],
                    edges=[],
                    query_time_ms=(time.time() - start_time) * 1000,
                    error="Missing required parameter: target"
                )

            # Execute query based on type
            if query_type == "find_callers":
                result = self._find_callers(target, edge_type, depth)
            elif query_type == "find_dependencies":
                result = self._find_dependencies(target, edge_type, depth)
            elif query_type == "find_path":
                source = target
                dest = kwargs.get("destination")
                if not dest:
                    return KnowledgeGraphQueryResult(
                        success=False,
                        nodes=[],
                        edges=[],
                        query_time_ms=(time.time() - start_time) * 1000,
                        error="find_path requires 'destination' parameter"
                    )
                result = self._find_path(source, dest, edge_type)
            elif query_type == "find_related":
                result = self._find_related(target, depth)
            else:
                return KnowledgeGraphQueryResult(
                    success=False,
                    nodes=[],
                    edges=[],
                    query_time_ms=(time.time() - start_time) * 1000,
                    error=f"Unknown query type: {query_type}"
                )

            query_time_ms = (time.time() - start_time) * 1000

            return KnowledgeGraphQueryResult(
                success=True,
                nodes=result.get("nodes", []),
                edges=result.get("edges", []),
                query_time_ms=query_time_ms
            )

        except Exception as e:
            logger.exception("Knowledge graph query failed")
            return KnowledgeGraphQueryResult(
                success=False,
                nodes=[],
                edges=[],
                query_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )

    def _find_callers(
        self,
        target: str,
        edge_type: str,
        depth: int
    ) -> Dict[str, Any]:
        """Find all nodes that call/reference the target."""
        if not self.query_engine:
            return {"nodes": [], "edges": []}

        # Query graph for reverse edges (who calls target?)
        nodes = self.query_engine.find_callers(target, edge_type, max_depth=depth)
        edges = self.query_engine.get_edges_for_nodes(nodes, edge_type)

        return {
            "nodes": [self._node_to_dict(n) for n in nodes],
            "edges": [self._edge_to_dict(e) for e in edges]
        }

    def _find_dependencies(
        self,
        target: str,
        edge_type: str,
        depth: int
    ) -> Dict[str, Any]:
        """Find all dependencies of the target."""
        if not self.query_engine:
            return {"nodes": [], "edges": []}

        # Query graph for forward edges (what does target depend on?)
        nodes = self.query_engine.find_dependencies(target, edge_type, max_depth=depth)
        edges = self.query_engine.get_edges_for_nodes(nodes, edge_type)

        return {
            "nodes": [self._node_to_dict(n) for n in nodes],
            "edges": [self._edge_to_dict(e) for e in edges]
        }

    def _find_path(
        self,
        source: str,
        dest: str,
        edge_type: str
    ) -> Dict[str, Any]:
        """Find shortest path between source and destination."""
        if not self.query_engine:
            return {"nodes": [], "edges": []}

        path = self.query_engine.find_shortest_path(source, dest, edge_type)

        if not path:
            return {"nodes": [], "edges": []}

        return {
            "nodes": [self._node_to_dict(n) for n in path["nodes"]],
            "edges": [self._edge_to_dict(e) for e in path["edges"]]
        }

    def _find_related(
        self,
        target: str,
        depth: int
    ) -> Dict[str, Any]:
        """Find all related nodes (any edge type)."""
        if not self.query_engine:
            return {"nodes": [], "edges": []}

        nodes = self.query_engine.find_neighborhood(target, max_depth=depth)
        edges = self.query_engine.get_edges_for_nodes(nodes)

        return {
            "nodes": [self._node_to_dict(n) for n in nodes],
            "edges": [self._edge_to_dict(e) for e in edges]
        }

    def _node_to_dict(self, node: Any) -> Dict[str, Any]:
        """Convert node object to dictionary."""
        if hasattr(node, "to_dict"):
            return node.to_dict()
        return {
            "id": getattr(node, "id", None),
            "type": getattr(node, "node_type", "unknown"),
            "name": getattr(node, "name", ""),
            "metadata": getattr(node, "metadata", {})
        }

    def _edge_to_dict(self, edge: Any) -> Dict[str, Any]:
        """Convert edge object to dictionary."""
        if hasattr(edge, "to_dict"):
            return edge.to_dict()
        return {
            "source_id": getattr(edge, "source_id", None),
            "target_id": getattr(edge, "target_id", None),
            "edge_type": getattr(edge, "edge_type", "unknown"),
            "metadata": getattr(edge, "metadata", {})
        }

    def get_schema(self) -> Dict[str, Any]:
        """Get MCP tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["find_callers", "find_dependencies", "find_path", "find_related"],
                        "description": "Type of knowledge graph query"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target node identifier (file, class, or function name)"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination node for find_path queries (optional)"
                    },
                    "edge_type": {
                        "type": "string",
                        "enum": ["calls", "imports", "tests", "depends_on", "writes_to"],
                        "description": "Edge type filter (optional, defaults to 'calls')"
                    },
                    "depth": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 2,
                        "description": "Maximum traversal depth (optional)"
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Repository path for context (optional)"
                    }
                },
                "required": ["query_type", "target"]
            }
        }


def get_knowledge_graph_tool(db_path: Optional[Path] = None) -> KnowledgeGraphQueryTool:
    """
    Factory function to create knowledge graph query tool.

    Args:
        db_path: Optional custom path to knowledge graph database

    Returns:
        Configured KnowledgeGraphQueryTool instance
    """
    return KnowledgeGraphQueryTool(db_path=db_path)


# AC_COMPLETE: AC-PHASE66-S2-MCP-001 ✅ MCP tool complete
