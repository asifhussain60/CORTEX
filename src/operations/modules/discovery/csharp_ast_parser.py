"""
C# AST parser using tree-sitter
"""
import logging
from pathlib import Path
from typing import List, Optional

try:
    from tree_sitter import Language, Parser
    import tree_sitter_c_sharp as tscsharp
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

from .ast_parser import ASTParser
from .models import ASTNode, CodeElement, ComplexityMetrics

logger = logging.getLogger(__name__)


class CSharpASTParser(ASTParser):
    """C# AST parser using tree-sitter-csharp"""
    
    def __init__(self):
        """Initialize C# AST parser"""
        super().__init__()
        self.supported_languages = ['csharp', 'c#']
        if TREE_SITTER_AVAILABLE:
            self.parser = Parser()
            self.parser.language = Language(tscsharp.language())
        else:
            self.parser = None
    
    def parse(self, file_path: Path, content: str) -> Optional[ASTNode]:
        """
        Parse C# file into AST
        
        Args:
            file_path: Path to C# file
            content: C# source code
            
        Returns:
            Root ASTNode or None if parsing fails
        """
        if not TREE_SITTER_AVAILABLE or self.parser is None:
            logger.warning("tree-sitter not available for C# parsing")
            return None
        
        try:
            tree = self.parser.parse(bytes(content, 'utf8'))
            return self._convert_tree_sitter_node(tree.root_node, content)
        except Exception as e:
            logger.error(f"Error parsing C# file {file_path}: {e}")
            return None
    
    def _convert_tree_sitter_node(self, node, source: str) -> ASTNode:
        """Convert tree-sitter node to ASTNode"""
        name = ''
        if node.type in ['class_declaration', 'method_declaration', 'property_declaration']:
            # Try to extract name from child nodes
            for child in node.children:
                if child.type == 'identifier':
                    name = source[child.start_byte:child.end_byte]
                    break
        
        children = []
        for child in node.children:
            if child.type not in ['comment', '{', '}', '(', ')']:
                children.append(self._convert_tree_sitter_node(child, source))
        
        return ASTNode(
            node_type=node.type,
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            children=children,
            attributes={'grammar': 'csharp'}
        )
    
    def extract_elements(self, ast_node: ASTNode, file_path: Path) -> List[CodeElement]:
        """
        Extract C# code elements (classes, methods, properties)
        
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
        """Recursively extract C# code elements"""
        if node.node_type == 'class_declaration':
            elements.append(CodeElement(
                type='class',
                name=node.name,
                file_path=file_path,
                line_start=node.start_line,
                line_end=node.end_line,
                signature=f"class {node.name}",
                complexity=self.calculate_complexity(node)
            ))
        elif node.node_type == 'method_declaration':
            elements.append(CodeElement(
                type='method',
                name=node.name,
                file_path=file_path,
                line_start=node.start_line,
                line_end=node.end_line,
                signature=f"method {node.name}",
                complexity=self.calculate_complexity(node)
            ))
        elif node.node_type == 'property_declaration':
            elements.append(CodeElement(
                type='property',
                name=node.name,
                file_path=file_path,
                line_start=node.start_line,
                line_end=node.end_line,
                signature=f"property {node.name}"
            ))
        
        for child in node.children:
            self._extract_recursive(child, file_path, elements)
    
    def calculate_complexity(self, ast_node: ASTNode) -> ComplexityMetrics:
        """
        Calculate complexity metrics for C# code
        
        Args:
            ast_node: AST node to analyze
            
        Returns:
            ComplexityMetrics
        """
        cyclomatic = 1
        lines = ast_node.end_line - ast_node.start_line + 1
        cyclomatic += self._count_decision_points(ast_node)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cyclomatic,
            lines_of_code=lines,
            nesting_depth=self._calculate_nesting_depth(ast_node),
            maintainability_index=max(0, 100 - (cyclomatic * 5))
        )
    
    def _count_decision_points(self, node: ASTNode) -> int:
        """Count C# decision points"""
        count = 0
        decision_nodes = {'if_statement', 'while_statement', 'for_statement', 
                         'foreach_statement', 'switch_statement', 'catch_clause'}
        
        if node.node_type in decision_nodes:
            count += 1
        
        for child in node.children:
            count += self._count_decision_points(child)
        
        return count
    
    def _calculate_nesting_depth(self, node: ASTNode, current_depth: int = 0) -> int:
        """Calculate C# nesting depth"""
        nesting_nodes = {'if_statement', 'while_statement', 'for_statement', 
                        'foreach_statement', 'try_statement'}
        
        if node.node_type in nesting_nodes:
            current_depth += 1
        
        max_depth = current_depth
        for child in node.children:
            child_depth = self._calculate_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
