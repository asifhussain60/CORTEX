"""
Dependency Graph Generator - Visualize module dependencies.

Generates dependency graphs in Mermaid and DOT formats using
AST analysis of import relationships.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """Node in dependency graph."""
    name: str
    type: str  # "module", "class", "function"
    file_path: str
    dependencies: List[str]


class DependencyGraphGenerator:
    """Generate visual dependency graphs."""
    
    def __init__(self, ast_engine):
        """
        Initialize dependency graph generator.
        
        Args:
            ast_engine: AST engine for architecture analysis
        """
        self.ast_engine = ast_engine
        
    def generate_module_graph(
        self,
        target_path: Path = None,
        format: str = "mermaid"
    ) -> str:
        """
        Generate module-level dependency graph.
        
        Args:
            target_path: Specific directory or None for full project
            format: Output format ("mermaid", "dot", "json")
            
        Returns:
            Graph representation in specified format
            
        Raises:
            ValueError: If format is not supported
        """
        logger.info(f"Generating module dependency graph (format: {format})")
        
        # Get architecture data from AST engine
        arch = self.ast_engine.get_architecture_insights()
        module_graph = arch.get('dependencies', [])
        
        if format == "mermaid":
            return self._generate_mermaid_graph(module_graph)
        elif format == "dot":
            return self._generate_dot_graph(module_graph)
        elif format == "json":
            return self._generate_json_graph(module_graph)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_mermaid_graph(self, module_graph: List[Dict]) -> str:
        """Generate Mermaid graph syntax."""
        lines = ["graph TD"]
        
        # Add nodes and edges
        edges_added = set()
        for edge in module_graph:
            from_module = edge.get('from', '').replace('/', '_').replace('.', '_').replace('-', '_')
            to_module = edge.get('to', '').replace('/', '_').replace('.', '_').replace('-', '_')
            
            if not from_module or not to_module:
                continue
                
            edge_key = f"{from_module}-->{to_module}"
            if edge_key not in edges_added:
                lines.append(f"    {from_module}[\"{edge.get('from', 'unknown')}\"] --> {to_module}[\"{edge.get('to', 'unknown')}\"]")
                edges_added.add(edge_key)
                
        # Add styling for different module types
        lines.extend([
            "",
            "    classDef orchestrator fill:#e1f5ff,stroke:#01579b",
            "    classDef analyzer fill:#f3e5f5,stroke:#4a148c",
            "    classDef utility fill:#fff9c4,stroke:#f57f17"
        ])
        
        return "\n".join(lines)
        
    def _generate_dot_graph(self, module_graph: List[Dict]) -> str:
        """Generate Graphviz DOT format."""
        lines = ["digraph Dependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box];")
        
        for edge in module_graph:
            from_module = edge.get('from', 'unknown')
            to_module = edge.get('to', 'unknown')
            lines.append(f'    "{from_module}" -> "{to_module}";')
            
        lines.append("}")
        return "\n".join(lines)
        
    def _generate_json_graph(self, module_graph: List[Dict]) -> str:
        """Generate JSON graph representation."""
        return json.dumps(module_graph, indent=2)
        
    def detect_circular_dependencies(self) -> str:
        """
        Generate visualization highlighting circular dependencies.
        
        Returns:
            Mermaid graph with circular deps highlighted in red
        """
        arch = self.ast_engine.get_architecture_insights()
        circular_deps = arch.get('circular_dependencies', [])
        
        if not circular_deps:
            return "graph TD\n    NO_CYCLES[\"✓ No Circular Dependencies Detected\"]"
        
        lines = ["graph TD"]
        
        for cycle in circular_deps:
            # Highlight circular paths in red
            for i in range(len(cycle)):
                from_node = cycle[i].replace('/', '_').replace('.', '_').replace('-', '_')
                to_node = cycle[(i + 1) % len(cycle)].replace('/', '_').replace('.', '_').replace('-', '_')
                lines.append(
                    f"    {from_node}[\"{cycle[i]}\"] -->|CIRCULAR| {to_node}[\"{cycle[(i + 1) % len(cycle)]}\"]"
                )
                
        lines.append("    linkStyle default stroke:red,stroke-width:2px")
        
        return "\n".join(lines)
