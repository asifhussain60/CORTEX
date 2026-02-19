"""
AST-based Knowledge Graph Builder — Phase 3 Wave 4.

Authority: Phase 3 Wave 4 | LENS Knowledge Graph
Purpose: Convert code AST into graph database representation
Note: Complements existing GraphBuilder (architecture-level) with AST-level detail
"""
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class ASTGraphNode:
    """Node in AST-based knowledge graph."""
    name: str
    type: str  # function, class, method, variable
    file_path: str
    line_number: int


@dataclass
class ASTGraphRelationship:
    """Relationship between AST nodes."""
    source: str
    relation_type: str  # CONTAINS, IMPORTS, CALLS, INHERITS
    target: str


class ASTKnowledgeGraph:
    """
    In-memory AST-based knowledge graph representation.
    
    Example:
        graph = ASTKnowledgeGraph()
        graph.add_node(ASTGraphNode("Calculator", "class", "app.py", 1))
        graph.add_relationship(ASTGraphRelationship("Calculator", "CONTAINS", "add"))
    """
    
    def __init__(self) -> None:
        """Initialize empty knowledge graph."""
        self.nodes: Dict[str, ASTGraphNode] = {}
        self.relationships: List[ASTGraphRelationship] = []
    
    @property
    def node_count(self) -> int:
        """Get total node count."""
        return len(self.nodes)
    
    def add_node(self, node: ASTGraphNode) -> None:
        """Add node to graph."""
        self.nodes[node.name] = node
    
    def add_relationship(self, relationship: ASTGraphRelationship) -> None:
        """Add relationship to graph."""
        self.relationships.append(relationship)
    
    def has_node(self, name: str) -> bool:
        """Check if node exists."""
        return name in self.nodes
    
    def has_relationship(self, source: str, relation_type: str, target: str) -> bool:
        """Check if relationship exists."""
        return any(
            r.source == source and r.relation_type == relation_type and r.target == target
            for r in self.relationships
        )


class ASTKnowledgeGraphBuilder:
    """
    Builds AST-level knowledge graph from Python code.
    
    Workflow:
    1. Parse Python file to AST
    2. Extract entities (classes, functions, methods)
    3. Extract relationships (inheritance, calls, imports)
    4. Build graph representation
    
    Example:
        builder = ASTKnowledgeGraphBuilder()
        graph = builder.build_from_file(Path("app.py"))
    """
    
    def __init__(self) -> None:
        """Initialize graph builder."""
        self.graph = ASTKnowledgeGraph()
    
    def build_from_file(self, file_path: Path) -> ASTKnowledgeGraph:
        """
        Build graph from single Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ASTKnowledgeGraph with extracted entities
        """
        code = file_path.read_text()
        tree = ast.parse(code)
        
        # Extract top-level functions first
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is at module level
                is_method = False
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        if node in parent.body:
                            is_method = True
                            break
                
                if not is_method:
                    self.graph.add_node(ASTGraphNode(
                        name=node.name,
                        type="function",
                        file_path=str(file_path),
                        line_number=node.lineno
                    ))
        
        # Extract classes and methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.graph.add_node(ASTGraphNode(
                    name=node.name,
                    type="class",
                    file_path=str(file_path),
                    line_number=node.lineno
                ))
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        self.graph.add_node(ASTGraphNode(
                            name=item.name,
                            type="method",
                            file_path=str(file_path),
                            line_number=item.lineno
                        ))
                        self.graph.add_relationship(ASTGraphRelationship(
                            source=node.name,
                            relation_type="CONTAINS",
                            target=item.name
                        ))
        
        return self.graph
    
    def build_from_directory(self, directory: Path) -> ASTKnowledgeGraph:
        """
        Build graph from all Python files in directory.
        
        Args:
            directory: Path to directory
            
        Returns:
            ASTKnowledgeGraph with all files
        """
        for py_file in directory.glob("*.py"):
            self.build_from_file(py_file)
        
        # Detect imports
        self._detect_imports(directory)
        
        return self.graph
    
    def _detect_imports(self, directory: Path) -> None:
        """Detect import relationships between files."""
        for py_file in directory.glob("*.py"):
            code = py_file.read_text()
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.graph.add_relationship(ASTGraphRelationship(
                            source=py_file.name,
                            relation_type="IMPORTS",
                            target=f"{node.module}.py"
                        ))
                
                # Detect function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Find the calling function
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.FunctionDef):
                                for child in ast.walk(parent):
                                    if child is node:
                                        self.graph.add_relationship(ASTGraphRelationship(
                                            source=parent.name,
                                            relation_type="CALLS",
                                            target=node.func.id
                                        ))
                                        break
