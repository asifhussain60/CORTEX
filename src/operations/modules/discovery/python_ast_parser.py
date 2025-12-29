"""
Python AST parser using built-in ast module
"""
import ast
import logging
from pathlib import Path
from typing import List, Optional

from .ast_parser import ASTParser
from .models import ASTNode, CodeElement, ComplexityMetrics

logger = logging.getLogger(__name__)


class PythonASTParser(ASTParser):
    """Python AST parser using Python's ast module"""
    
    def __init__(self):
        """Initialize Python AST parser"""
        super().__init__()
        self.supported_languages = ['python']
    
    def parse(self, file_path: Path, content: str) -> Optional[ASTNode]:
        """
        Parse Python file into AST
        
        Args:
            file_path: Path to Python file
            content: Python source code
            
        Returns:
            Root ASTNode or None if parsing fails
        """
        try:
            tree = ast.parse(content, filename=str(file_path))
            return self._convert_to_ast_node(tree)
        except SyntaxError as e:
            logger.error(f"Syntax error parsing {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _convert_to_ast_node(self, node: ast.AST) -> ASTNode:
        """Convert Python ast.AST to our ASTNode model"""
        node_type = node.__class__.__name__
        name = getattr(node, 'name', '')
        start_line = getattr(node, 'lineno', 0)
        end_line = getattr(node, 'end_lineno', start_line)
        
        children = []
        for child in ast.iter_child_nodes(node):
            children.append(self._convert_to_ast_node(child))
        
        attributes = {}
        for attr in node._attributes:
            if hasattr(node, attr):
                attributes[attr] = getattr(node, attr)
        
        return ASTNode(
            node_type=node_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            children=children,
            attributes=attributes
        )
    
    def extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]:
        """
        Extract Python code elements (classes, functions, methods)
        
        Args:
            ast_node: Root AST node
            file_path: Path to source file
            
        Returns:
            List of CodeElements
        """
        elements = []
        self._extract_recursive(ast_node, file_path, elements)
        return elements
    
    def _extract_recursive(self, node: ASTNode, file_path: Path, elements: List[CodeElement]):
        """Recursively extract code elements from AST"""
        if node.node_type == 'ClassDef':
            elements.append(CodeElement(
                type='class',
                name=node.name,
                file_path=file_path,
                line_start=node.start_line,
                line_end=node.end_line,
                signature=f"class {node.name}",
                complexity=self.calculate_complexity(node)
            ))
        elif node.node_type == 'FunctionDef':
            # Check if it's a method (inside a class) or standalone function
            element_type = 'function'
            elements.append(CodeElement(
                type=element_type,
                name=node.name,
                file_path=file_path,
                line_start=node.start_line,
                line_end=node.end_line,
                signature=f"def {node.name}",
                complexity=self.calculate_complexity(node)
            ))
        
        # Recurse into children
        for child in node.children:
            self._extract_recursive(child, file_path, elements)
    
    def calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics:
        """
        Calculate complexity metrics for Python code
        
        Args:
            ast_node: AST node to analyze
            
        Returns:
            ComplexityMetrics
        """
        # Simple cyclomatic complexity calculation
        cyclomatic = 1  # Base complexity
        lines = ast_node.end_line - ast_node.start_line + 1
        
        # Count decision points
        cyclomatic += self._count_decision_points(ast_node)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cyclomatic,  # Simplified for now
            lines_of_code=lines,
            number_of_parameters=0,
            nesting_depth=self._calculate_nesting_depth(ast_node),
            maintainability_index=max(0, 100 - (cyclomatic * 5))
        )
    
    def _count_decision_points(self, node: ASTNode) -> int:
        """Count decision points for cyclomatic complexity"""
        count = 0
        decision_nodes = {'If', 'While', 'For', 'ExceptHandler', 'With', 'Assert'}
        
        if node.node_type in decision_nodes:
            count += 1
        
        for child in node.children:
            count += self._count_decision_points(child)
        
        return count
    
    def _calculate_nesting_depth(self, node: ASTNode, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        nesting_nodes = {'If', 'While', 'For', 'With', 'Try'}
        
        if node.node_type in nesting_nodes:
            current_depth += 1
        
        max_depth = current_depth
        for child in node.children:
            child_depth = self._calculate_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
