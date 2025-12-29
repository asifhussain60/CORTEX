#!/usr/bin/env python3
"""
Architecture Graph Builder

Analyzes codebase structure and generates D3.js force-directed graph data.
Detects modules, classes, functions, and their relationships (imports, calls, inheritance).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureNode:
    """Represents a node in the architecture graph"""
    id: str
    name: str
    type: str  # 'module', 'class', 'function', 'package'
    file_path: str
    layer: Optional[str] = None  # 'presentation', 'application', 'domain', 'infrastructure'
    size: int = 1  # Lines of code or complexity
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureEdge:
    """Represents an edge (relationship) in the architecture graph"""
    source: str
    target: str
    type: str  # 'imports', 'calls', 'inherits', 'uses'
    weight: int = 1


class ArchitectureGraphBuilder:
    """Builds architecture graph from codebase analysis"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.nodes: Dict[str, ArchitectureNode] = {}
        self.edges: List[ArchitectureEdge] = []
        
    def build_graph(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        Build architecture graph from Python files
        Returns D3.js compatible force-directed graph data
        """
        logger.info(f"Building architecture graph from {len(file_paths)} files...")
        
        # Phase 1: Parse all files and extract nodes
        for file_path in file_paths:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
                continue
        
        # Phase 2: Detect architectural layers
        self._detect_layers()
        
        # Phase 3: Convert to D3.js format
        graph_data = self._to_d3_format()
        
        logger.info(f"Graph built: {len(self.nodes)} nodes, {len(self.edges)} edges")
        return graph_data
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content, filename=str(file_path))
            
            # Create module node
            rel_path = file_path.relative_to(self.project_path)
            module_id = str(rel_path).replace('\\', '/').replace('.py', '')
            
            module_node = ArchitectureNode(
                id=module_id,
                name=file_path.stem,
                type='module',
                file_path=str(file_path),
                size=len(content.splitlines())
            )
            self.nodes[module_id] = module_node
            
            # Extract imports
            imports = self._extract_imports(tree)
            for imported_module in imports:
                edge = ArchitectureEdge(
                    source=module_id,
                    target=imported_module,
                    type='imports'
                )
                self.edges.append(edge)
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node, module_id, file_path)
                elif isinstance(node, ast.FunctionDef):
                    if not self._is_method(node, tree):
                        self._process_function(node, module_id, file_path)
                        
        except Exception as e:
            logger.debug(f"Error analyzing {file_path}: {e}")
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
        return imports
    
    def _process_class(self, node: ast.ClassDef, module_id: str, file_path: Path):
        """Process a class definition"""
        class_id = f"{module_id}.{node.name}"
        
        class_node = ArchitectureNode(
            id=class_id,
            name=node.name,
            type='class',
            file_path=str(file_path),
            size=self._count_lines(node),
            metadata={
                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                'bases': [self._get_base_name(base) for base in node.bases]
            }
        )
        self.nodes[class_id] = class_node
        
        # Add edge from module to class
        edge = ArchitectureEdge(
            source=module_id,
            target=class_id,
            type='contains'
        )
        self.edges.append(edge)
        
        # Add inheritance edges
        for base in node.bases:
            base_name = self._get_base_name(base)
            if base_name:
                edge = ArchitectureEdge(
                    source=class_id,
                    target=base_name,
                    type='inherits'
                )
                self.edges.append(edge)
    
    def _process_function(self, node: ast.FunctionDef, module_id: str, file_path: Path):
        """Process a function definition"""
        func_id = f"{module_id}.{node.name}"
        
        func_node = ArchitectureNode(
            id=func_id,
            name=node.name,
            type='function',
            file_path=str(file_path),
            size=self._count_lines(node),
            metadata={
                'args': [arg.arg for arg in node.args.args]
            }
        )
        self.nodes[func_id] = func_node
        
        # Add edge from module to function
        edge = ArchitectureEdge(
            source=module_id,
            target=func_id,
            type='contains'
        )
        self.edges.append(edge)
    
    def _detect_layers(self):
        """Detect architectural layers based on naming patterns"""
        layer_patterns = {
            'presentation': ['ui', 'views', 'templates', 'controllers', 'api', 'routes'],
            'application': ['services', 'handlers', 'use_cases', 'operations', 'orchestrators'],
            'domain': ['models', 'entities', 'domain', 'core'],
            'infrastructure': ['database', 'repositories', 'adapters', 'plugins', 'external']
        }
        
        for node_id, node in self.nodes.items():
            path_lower = node.file_path.lower()
            
            for layer, patterns in layer_patterns.items():
                if any(pattern in path_lower for pattern in patterns):
                    node.layer = layer
                    break
            
            if not node.layer:
                node.layer = 'unknown'
    
    def _to_d3_format(self) -> Dict[str, Any]:
        """Convert to D3.js force-directed graph format"""
        nodes_list = []
        for node_id, node in self.nodes.items():
            nodes_list.append({
                'id': node.id,
                'name': node.name,
                'type': node.type,
                'layer': node.layer,
                'size': node.size,
                'file_path': node.file_path,
                'metadata': node.metadata
            })
        
        edges_list = []
        for edge in self.edges:
            # Only include edges where both nodes exist
            if edge.source in self.nodes and edge.target in self.nodes:
                edges_list.append({
                    'source': edge.source,
                    'target': edge.target,
                    'type': edge.type,
                    'weight': edge.weight
                })
        
        # Create both formats - detailed and D3 simplified
        result = {
            'nodes': nodes_list,
            'relationships': edges_list,  # Keep for compatibility
            'links': edges_list,  # D3 expects 'links'
            'd3_data': {
                'nodes': nodes_list,
                'links': edges_list
            },
            'metadata': {
                'total_nodes': len(nodes_list),
                'total_edges': len(edges_list),
                'layers': self._count_layers(),
                'node_types': self._count_node_types()
            }
        }
        
        return result
    
    def _count_layers(self) -> Dict[str, int]:
        """Count nodes per layer"""
        layers = {}
        for node in self.nodes.values():
            layer = node.layer or 'unknown'
            layers[layer] = layers.get(layer, 0) + 1
        return layers
    
    def _count_node_types(self) -> Dict[str, int]:
        """Count nodes per type"""
        types = {}
        for node in self.nodes.values():
            types[node.type] = types.get(node.type, 0) + 1
        return types
    
    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if function is a method (inside a class)"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def _get_base_name(self, base: ast.expr) -> Optional[str]:
        """Extract base class name from AST node"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        return None
    
    def _count_lines(self, node: ast.AST) -> int:
        """Count lines of code for an AST node"""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return 1


def generate_architecture_json(project_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Generate architecture.json for a project
    
    Args:
        project_path: Path to project to analyze
        output_path: Path to save architecture.json
        
    Returns:
        Architecture graph data
    """
    builder = ArchitectureGraphBuilder(project_path)
    
    # Find all Python files
    python_files = list(project_path.rglob('*.py'))
    
    # Build graph
    graph_data = builder.build_graph(python_files)
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2)
    
    logger.info(f"Architecture graph saved to {output_path}")
    return graph_data
