"""
Relationship Traversal Intelligence Engine.

Migrated from cortex/brain/core/intelligence/relationship_traversal.py
Detects and traverses code relationships using BaseIntelligenceEngine pattern.

Authority: Phase 56 - LENS/Intelligence Hybrid Architecture
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

from cortex.intelligence.base_engine import BaseIntelligenceEngine
from cortex.brain.core.result import Ok, Err

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES (from original engine)
# =============================================================================


@dataclass
class APIEndpoint:
    """An API endpoint definition."""
    path: str
    methods: List[str]
    function_name: str
    line_number: int
    framework: str = "unknown"
    prefix: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "methods": self.methods,
            "function_name": self.function_name,
            "line_number": self.line_number,
            "framework": self.framework,
            "prefix": self.prefix,
        }


@dataclass
class DatabaseModel:
    """A database model definition."""
    name: str
    table_name: str
    columns: List[str]
    foreign_keys: List[Dict[str, str]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "table_name": self.table_name,
            "columns": self.columns,
            "foreign_keys": self.foreign_keys,
            "relationships": self.relationships,
            "line_number": self.line_number,
        }


@dataclass
class FileDependency:
    """A file dependency."""
    source_file: str
    source_module: str
    imports: List[str]
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_file": self.source_file,
            "source_module": self.source_module,
            "imports": self.imports,
            "line_number": self.line_number,
        }


@dataclass
class DependencyGraph:
    """A graph of file dependencies."""
    nodes: Set[str] = field(default_factory=set)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node)
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add an edge to the graph."""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges.append((from_node, to_node))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": list(self.nodes),
            "edges": self.edges,
        }


@dataclass
class RelationshipAnalysisResult:
    """Result of relationship analysis."""
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    database_models: List[DatabaseModel] = field(default_factory=list)
    file_dependencies: List[FileDependency] = field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "api_endpoints": [e.to_dict() for e in self.api_endpoints],
            "database_models": [m.to_dict() for m in self.database_models],
            "file_dependencies": [d.to_dict() for d in self.file_dependencies],
            "dependency_graph": self.dependency_graph.to_dict() if self.dependency_graph else None,
        }


# =============================================================================
# INTELLIGENCE ENGINE
# =============================================================================


class RelationshipTraversalEngine(BaseIntelligenceEngine):
    """
    Intelligence engine for detecting code relationships.
    
    Analyzes:
    - API endpoints (Flask, FastAPI, Django)
    - Database models and ORM relationships
    - File dependencies and import structure
    - Dependency graphs
    """
    
    # Flask route decorator pattern
    FLASK_ROUTE_PATTERN = re.compile(
        r"@\w+\.route\s*\(\s*['\"]([^'\"]+)['\"]"
        r"(?:.*?methods\s*=\s*\[([^\]]+)\])?"
    )
    
    # FastAPI route decorator patterns
    FASTAPI_PATTERNS = {
        "get": re.compile(r"@\w+\.get\s*\(\s*['\"]([^'\"]+)['\"]"),
        "post": re.compile(r"@\w+\.post\s*\(\s*['\"]([^'\"]+)['\"]"),
        "put": re.compile(r"@\w+\.put\s*\(\s*['\"]([^'\"]+)['\"]"),
        "delete": re.compile(r"@\w+\.delete\s*\(\s*['\"]([^'\"]+)['\"]"),
        "patch": re.compile(r"@\w+\.patch\s*\(\s*['\"]([^'\"]+)['\"]"),
    }
    
    def __init__(self):
        """Initialize RelationshipTraversal engine."""
        super().__init__(
            name="RelationshipTraversal",
            version="2.0.0",
            description="Analyzes code relationships and builds dependency graphs",
            cache_ttl=600
        )
    
    def _execute(self, context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Execute relationship analysis on code context
        
        Args:
            context: Code structure with optional 'source' code to analyze
        
        Returns:
            Analysis results or error
        """
        try:
            # If source code provided, analyze it
            if "source" in context:
                source = context["source"]
                relationships = self._analyze_source(source)
                return Ok(relationships.to_dict())
            
            # If nodes/edges provided, analyze graph structure
            if "nodes" in context or "edges" in context:
                nodes = context.get("nodes", [])
                edges = context.get("edges", [])
                
                return Ok({
                    "relationships": [],
                    "traversal": [],
                    "graph": {"nodes": nodes, "edges": edges}
                })
            
            return Ok({
                "relationships": [],
                "traversal": [],
                "graph": {"nodes": [], "edges": []}
            })
        
        except Exception as e:
            return Err(f"Relationship analysis failed: {str(e)}")
    
    def _analyze_source(self, source: str) -> RelationshipAnalysisResult:
        """
        Analyze relationships in source code.
        
        Args:
            source: Python source code
            
        Returns:
            RelationshipAnalysisResult
        """
        result = RelationshipAnalysisResult()
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            self.logger.warning(f"Syntax error parsing source: {e}")
            return result
        
        # Extract API endpoints
        result.api_endpoints = self._extract_api_endpoints(source)
        
        # Extract database models
        result.database_models = self._extract_database_models(tree)
        
        # Extract file dependencies
        result.file_dependencies = self._extract_file_dependencies(tree)
        
        # Build dependency graph
        result.dependency_graph = self._build_dependency_graph(result.file_dependencies)
        
        return result
    
    def _extract_api_endpoints(self, source: str) -> List[APIEndpoint]:
        """Extract API endpoints from source code."""
        endpoints = []
        
        for i, line in enumerate(source.split("\n"), 1):
            # Flask patterns
            flask_match = self.FLASK_ROUTE_PATTERN.search(line)
            if flask_match:
                path = flask_match.group(1)
                methods_str = flask_match.group(2) or "GET"
                methods = [m.strip().strip("\"'") for m in methods_str.split(",")]
                
                endpoints.append(APIEndpoint(
                    path=path,
                    methods=methods,
                    function_name=f"flask_route_{i}",
                    line_number=i,
                    framework="flask",
                ))
            
            # FastAPI patterns
            for method, pattern in self.FASTAPI_PATTERNS.items():
                if pattern.search(line):
                    match = pattern.search(line)
                    if match:
                        endpoints.append(APIEndpoint(
                            path=match.group(1),
                            methods=[method.upper()],
                            function_name=f"fastapi_{method}_{i}",
                            line_number=i,
                            framework="fastapi",
                        ))
        
        return endpoints
    
    def _extract_database_models(self, tree: ast.AST) -> List[DatabaseModel]:
        """Extract database models from AST."""
        models = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from common ORMs
                if self._is_orm_model(node):
                    model = DatabaseModel(
                        name=node.name,
                        table_name=self._extract_table_name(node),
                        columns=self._extract_columns(node),
                        line_number=node.lineno,
                    )
                    models.append(model)
        
        return models
    
    def _extract_file_dependencies(self, tree: ast.AST) -> List[FileDependency]:
        """Extract file dependencies from AST."""
        deps = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.append(FileDependency(
                        source_file="<module>",
                        source_module=alias.name,
                        imports=[alias.name],
                        line_number=node.lineno,
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports = [alias.name for alias in node.names]
                deps.append(FileDependency(
                    source_file="<module>",
                    source_module=module,
                    imports=imports,
                    line_number=node.lineno,
                ))
        
        return deps
    
    def _build_dependency_graph(self, deps: List[FileDependency]) -> DependencyGraph:
        """Build dependency graph from file dependencies."""
        graph = DependencyGraph()
        
        for dep in deps:
            graph.add_node(str(dep.source_file))
            for imp in dep.imports:
                graph.add_node(imp)
                graph.add_edge(str(dep.source_file), imp)
        
        return graph
    
    def _is_orm_model(self, node: ast.ClassDef) -> bool:
        """Check if class is an ORM model."""
        # Simple heuristic: class name ends with Model or Table
        return node.name.endswith("Model") or node.name.endswith("Table")
    
    def _extract_table_name(self, node: ast.ClassDef) -> str:
        """Extract table name from model class."""
        # Default to lowercased class name
        return node.name.lower()
    
    def _extract_columns(self, node: ast.ClassDef) -> List[str]:
        """Extract column names from model class."""
        columns = []
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    columns.append(item.target.id)
        
        return columns
    def build_graph(self, dependencies: Dict[str, List[str]]) -> Union[Ok, Err]:
        """
        Build a relationship graph from dependency map
        
        Args:
            dependencies: Dict of node -> [dependency nodes]
        
        Returns:
            Graph structure with nodes and edges
        """
        try:
            nodes = [{"id": node} for node in dependencies.keys()]
            edges = []
            
            for source, targets in dependencies.items():
                for target in targets:
                    edges.append({"from": source, "to": target})
            
            return Ok({
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges)
            })
        
        except Exception as e:
            return Err(f"Graph building failed: {str(e)}")
    
    def transitive_closure(self, dependencies: Dict[str, List[str]]) -> Union[Ok, Err]:
        """
        Compute transitive closure of dependencies
        
        Args:
            dependencies: Dict of node -> [direct dependencies]
        
        Returns:
            Closure with all direct and indirect relationships
        """
        try:
            closure = {}
            
            for source in dependencies:
                closure[source] = self._compute_reachable(source, dependencies)
            
            return Ok(closure)
        
        except Exception as e:
            return Err(f"Closure computation failed: {str(e)}")
    
    def _compute_reachable(self, node: str, adj_map: Dict[str, List[str]]) -> Set[str]:
        """Compute all nodes reachable from a given node"""
        visited = set()
        stack = [node]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            for neighbor in adj_map.get(current, []):
                if neighbor not in visited:
                    stack.append(neighbor)
        
        return visited