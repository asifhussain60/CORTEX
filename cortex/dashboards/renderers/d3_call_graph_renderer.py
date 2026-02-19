"""
D3.js Call Graph Renderer - Force-Directed Function Call Visualization.

Converts function call graph data into D3.js force-directed graph format:
- Nodes: Functions/methods with size based on connections
- Edges: Call relationships between functions
- Force simulation configuration for interactive layout
- JSON output for frontend D3.js consumption

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-003
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class D3Node:
    """
    D3.js node representation.

    Attributes:
        id: Unique identifier (function/class name)
        label: Display label
        group: Node type (function, class, method)
        size: Node radius (based on connections)
        color: Node color (based on type)
    """
    id: str
    label: str
    group: str
    size: int
    color: str


@dataclass
class D3Edge:
    """
    D3.js edge representation (called "link" in D3.js).

    Attributes:
        source: Source node ID (caller)
        target: Target node ID (callee)
        value: Edge weight (call frequency, default 1)
        label: Edge label (default "calls")
    """
    source: str
    target: str
    value: int = 1
    label: str = "calls"


@dataclass
class D3Configuration:
    """
    D3.js force simulation configuration.

    Attributes:
        width: Canvas width (pixels)
        height: Canvas height (pixels)
        charge_strength: Repulsion force (-300 = strong repulsion)
        link_distance: Target distance between connected nodes
        node_radius_min: Minimum node radius
        node_radius_max: Maximum node radius
    """
    width: int = 1200
    height: int = 800
    charge_strength: int = -300
    link_distance: int = 100
    node_radius_min: int = 5
    node_radius_max: int = 20


@dataclass
class D3Graph:
    """
    Complete D3.js graph data structure.

    Attributes:
        nodes: List of D3Node objects
        edges: List of D3Edge objects (converted to "links" in JSON)
        config: D3Configuration for force simulation
    """
    nodes: List[D3Node]
    edges: List[D3Edge]
    config: D3Configuration


class D3CallGraphRenderer:
    """
    Renders function call graph data as D3.js force-directed graph.

    Converts LENS analysis call graph data into D3.js-compatible JSON format
    for interactive frontend visualization.

    Example:
        ```python
        renderer = D3CallGraphRenderer()

        # Input from LENS analysis
        graph_data = {
            "nodes": [
                {"id": "main", "type": "function"},
                {"id": "process_data", "type": "function"},
            ],
            "edges": [
                {"source": "main", "target": "process_data"},
            ],
        }

        # Render to D3.js format
        d3_graph = renderer.render(graph_data)

        # Convert to JSON for frontend
        json_output = renderer.to_json(d3_graph)
        # {
        #   "nodes": [...],
        #   "links": [...],  # D3.js uses "links" not "edges"
        #   "config": {...}
        # }
        ```
    """

    # Color palette for node types
    NODE_COLORS = {
        "function": "#4299e1",  # Blue
        "class": "#48bb78",     # Green
        "method": "#ed8936",    # Orange
        "default": "#a0aec0",   # Gray
    }

    def render(
        self,
        graph_data: Dict[str, Any],
        config: Optional[D3Configuration] = None,
    ) -> D3Graph:
        """
        Render call graph data as D3.js graph.

        Args:
            graph_data: Graph data with "nodes" and "edges" keys
            config: Optional custom D3 configuration

        Returns:
            D3Graph ready for JSON serialization
        """
        if config is None:
            config = D3Configuration()

        # Calculate connection counts for node sizing
        connection_counts = self._calculate_connection_counts(graph_data)

        # Convert nodes
        d3_nodes = []
        for node in graph_data.get("nodes", []):
            d3_node = self._create_d3_node(node, connection_counts, config)
            d3_nodes.append(d3_node)

        # Convert edges
        d3_edges = []
        for edge in graph_data.get("edges", []):
            d3_edge = self._create_d3_edge(edge)
            d3_edges.append(d3_edge)

        return D3Graph(
            nodes=d3_nodes,
            edges=d3_edges,
            config=config,
        )

    def to_json(self, d3_graph: D3Graph) -> Dict[str, Any]:
        """
        Convert D3Graph to JSON-serializable dictionary.

        Args:
            d3_graph: D3Graph object

        Returns:
            Dictionary with "nodes", "links", "config" keys (D3.js format)
        """
        return {
            "nodes": [asdict(node) for node in d3_graph.nodes],
            "links": [asdict(edge) for edge in d3_graph.edges],  # D3.js uses "links"
            "config": asdict(d3_graph.config),
        }

    def _create_d3_node(
        self,
        node: Dict[str, Any],
        connection_counts: Dict[str, int],
        config: D3Configuration,
    ) -> D3Node:
        """Create D3Node from input node data."""
        node_id = node.get("id", "unknown")
        node_type = node.get("type", "default")

        # Calculate size based on connections
        connections = connection_counts.get(node_id, 0)
        size = self._calculate_node_size(connections, config)

        # Get color based on type
        color = self.NODE_COLORS.get(node_type, self.NODE_COLORS["default"])

        return D3Node(
            id=node_id,
            label=node.get("label", node_id),
            group=node_type,
            size=size,
            color=color,
        )

    def _create_d3_edge(self, edge: Dict[str, Any]) -> D3Edge:
        """Create D3Edge from input edge data."""
        return D3Edge(
            source=edge.get("source", ""),
            target=edge.get("target", ""),
            value=edge.get("value", 1),
            label=edge.get("label", "calls"),
        )

    def _calculate_connection_counts(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate total connections per node (in + out).

        Args:
            graph_data: Graph data with edges

        Returns:
            Dictionary mapping node_id → connection_count
        """
        counts: Dict[str, int] = {}

        for edge in graph_data.get("edges", []):
            source = edge.get("source", "")
            target = edge.get("target", "")

            counts[source] = counts.get(source, 0) + 1
            counts[target] = counts.get(target, 0) + 1

        return counts

    def _calculate_node_size(self, connections: int, config: D3Configuration) -> int:
        """
        Calculate node size based on connection count.

        Args:
            connections: Total number of connections (in + out)
            config: D3Configuration with min/max radius

        Returns:
            Node radius (pixels)
        """
        if connections == 0:
            return config.node_radius_min

        # Linear scaling based on connections
        # 0 connections → min radius
        # 10+ connections → max radius
        max_connections = 10
        ratio = min(connections / max_connections, 1.0)

        size_range = config.node_radius_max - config.node_radius_min
        size = config.node_radius_min + int(ratio * size_range)

        return size


def render_call_graph(
    graph_data: Dict[str, Any],
    config: Optional[D3Configuration] = None,
) -> Dict[str, Any]:
    """
    Convenience function to render call graph and convert to JSON.

    Args:
        graph_data: Graph data with "nodes" and "edges"
        config: Optional custom D3 configuration

    Returns:
        JSON-serializable dictionary (D3.js format)
    """
    renderer = D3CallGraphRenderer()
    d3_graph = renderer.render(graph_data, config=config)
    return renderer.to_json(d3_graph)
