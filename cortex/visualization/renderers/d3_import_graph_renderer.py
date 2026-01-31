"""
D3.js Import Graph Renderer - Module Dependency Visualization.

Converts module import graph data into D3.js force-directed graph format:
- Nodes: Modules/packages with coloring by package hierarchy
- Edges: Import relationships
- Circular dependency detection
- External vs internal module differentiation

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-003
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.visualization.renderers.d3_call_graph_renderer import (
    D3Graph,
    D3Node,
    D3Edge,
    D3Configuration,
)


class D3ImportGraphRenderer:
    """
    Renders module import graph as D3.js force-directed graph.
    
    Visualizes module dependencies with:
    - Color coding by package hierarchy
    - External vs internal module differentiation
    - Circular dependency highlighting
    - Size based on import/imported-by count
    
    Example:
        ```python
        renderer = D3ImportGraphRenderer()
        
        graph_data = {
            "nodes": [
                {"id": "cortex.brain.module", "type": "module", "is_external": False},
                {"id": "pandas", "type": "module", "is_external": True},
            ],
            "edges": [
                {"source": "cortex.brain.module", "target": "pandas"},
            ],
        }
        
        d3_graph = renderer.render(graph_data)
        json_output = renderer.to_json(d3_graph)
        ```
    """
    
    # Color palette for package hierarchies
    PACKAGE_COLORS = {
        "cortex.brain": "#9f7aea",      # Purple
        "cortex.orchestrators": "#4299e1",  # Blue
        "cortex.visualization": "#48bb78",  # Green
        "cortex.infrastructure": "#ed8936",  # Orange
        "external": "#a0aec0",          # Gray
        "default": "#718096",           # Dark gray
    }
    
    def render(
        self,
        graph_data: Dict[str, Any],
        config: Optional[D3Configuration] = None,
    ) -> D3Graph:
        """
        Render import graph data as D3.js graph.
        
        Args:
            graph_data: Graph data with "nodes" and "edges"
            config: Optional custom D3 configuration
        
        Returns:
            D3Graph ready for JSON serialization
        """
        if config is None:
            config = D3Configuration()
        
        # Calculate connection counts
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
    
    def detect_circular_dependencies(self, graph_data: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Detect circular dependencies in import graph.
        
        Args:
            graph_data: Graph data with "edges"
        
        Returns:
            List of (module_a, module_b) tuples representing circular imports
        """
        edges = graph_data.get("edges", [])
        
        # Build adjacency list and reverse adjacency list
        graph: Dict[str, Set[str]] = {}
        reverse_graph: Dict[str, Set[str]] = {}
        
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            if source not in graph:
                graph[source] = set()
            graph[source].add(target)
            
            if target not in reverse_graph:
                reverse_graph[target] = set()
            reverse_graph[target].add(source)
        
        # Find direct circular dependencies (A→B and B→A)
        circular_deps: List[Tuple[str, str]] = []
        seen_pairs: Set[Tuple[str, str]] = set()
        
        for source, targets in graph.items():
            for target in targets:
                # Check if there's a reverse edge
                if target in graph and source in graph[target]:
                    # Normalize pair to avoid duplicates
                    pair = tuple(sorted([source, target]))
                    if pair not in seen_pairs:
                        circular_deps.append((source, target))
                        seen_pairs.add(pair)
        
        return circular_deps
    
    def to_json(self, d3_graph: D3Graph) -> Dict[str, Any]:
        """
        Convert D3Graph to JSON with circular dependency info.
        
        Args:
            d3_graph: D3Graph object
        
        Returns:
            Dictionary with "nodes", "links", "config", "circular_dependencies"
        """
        # Build graph_data for circular dependency detection
        graph_data = {
            "nodes": [{"id": node.id} for node in d3_graph.nodes],
            "edges": [{"source": edge.source, "target": edge.target} for edge in d3_graph.edges],
        }
        
        circular_deps = self.detect_circular_dependencies(graph_data)
        
        return {
            "nodes": [self._node_to_dict(node) for node in d3_graph.nodes],
            "links": [self._edge_to_dict(edge) for edge in d3_graph.edges],
            "config": self._config_to_dict(d3_graph.config),
            "circular_dependencies": [{"source": s, "target": t} for s, t in circular_deps],
        }
    
    def _create_d3_node(
        self,
        node: Dict[str, Any],
        connection_counts: Dict[str, int],
        config: D3Configuration,
    ) -> D3Node:
        """Create D3Node from input node data."""
        node_id = node.get("id", "unknown")
        is_external = node.get("is_external", self._is_external_module(node_id))
        
        # Calculate size based on connections
        connections = connection_counts.get(node_id, 0)
        size = self._calculate_node_size(connections, config)
        
        # Get color based on package hierarchy
        color = self._get_module_color(node_id, is_external)
        
        # Group by internal/external
        group = "external" if is_external else "internal"
        
        return D3Node(
            id=node_id,
            label=node.get("label", node_id.split(".")[-1]),  # Short name
            group=group,
            size=size,
            color=color,
        )
    
    def _create_d3_edge(self, edge: Dict[str, Any]) -> D3Edge:
        """Create D3Edge from input edge data."""
        return D3Edge(
            source=edge.get("source", ""),
            target=edge.get("target", ""),
            value=edge.get("value", 1),
            label="imports",
        )
    
    def _get_module_color(self, module_id: str, is_external: bool) -> str:
        """Get color based on package hierarchy."""
        if is_external:
            return self.PACKAGE_COLORS["external"]
        
        # Check package prefixes
        for package, color in self.PACKAGE_COLORS.items():
            if module_id.startswith(package + "."):
                return color
        
        return self.PACKAGE_COLORS["default"]
    
    def _is_external_module(self, module_id: str) -> bool:
        """Determine if module is external (not part of CORTEX)."""
        internal_prefixes = ["cortex", "tests"]
        return not any(module_id.startswith(prefix) for prefix in internal_prefixes)
    
    def _calculate_connection_counts(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate total connections per node."""
        counts: Dict[str, int] = {}
        
        for edge in graph_data.get("edges", []):
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            counts[source] = counts.get(source, 0) + 1
            counts[target] = counts.get(target, 0) + 1
        
        return counts
    
    def _calculate_node_size(self, connections: int, config: D3Configuration) -> int:
        """Calculate node size based on connection count."""
        if connections == 0:
            return config.node_radius_min
        
        max_connections = 10
        ratio = min(connections / max_connections, 1.0)
        
        size_range = config.node_radius_max - config.node_radius_min
        size = config.node_radius_min + int(ratio * size_range)
        
        return size
    
    def _node_to_dict(self, node: D3Node) -> Dict[str, Any]:
        """Convert D3Node to dictionary."""
        return {
            "id": node.id,
            "label": node.label,
            "group": node.group,
            "size": node.size,
            "color": node.color,
        }
    
    def _edge_to_dict(self, edge: D3Edge) -> Dict[str, Any]:
        """Convert D3Edge to dictionary."""
        return {
            "source": edge.source,
            "target": edge.target,
            "value": edge.value,
            "label": edge.label,
        }
    
    def _config_to_dict(self, config: D3Configuration) -> Dict[str, Any]:
        """Convert D3Configuration to dictionary."""
        return {
            "width": config.width,
            "height": config.height,
            "charge_strength": config.charge_strength,
            "link_distance": config.link_distance,
            "node_radius_min": config.node_radius_min,
            "node_radius_max": config.node_radius_max,
        }


def render_import_graph(
    graph_data: Dict[str, Any],
    config: Optional[D3Configuration] = None,
) -> Dict[str, Any]:
    """
    Convenience function to render import graph and convert to JSON.
    
    Args:
        graph_data: Graph data with "nodes" and "edges"
        config: Optional custom D3 configuration
    
    Returns:
        JSON-serializable dictionary with circular dependency info
    """
    renderer = D3ImportGraphRenderer()
    d3_graph = renderer.render(graph_data, config=config)
    return renderer.to_json(d3_graph)
