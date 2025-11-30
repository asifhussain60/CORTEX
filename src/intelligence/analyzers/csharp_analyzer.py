"""
C# Analyzer

AST-based code smell detection for C# code using tree-sitter.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import List, Any
from .base_analyzer import BaseAnalyzer, CodeSmell, SmellType


class CSharpAnalyzer(BaseAnalyzer):
    """C#-specific AST analyzer using tree-sitter"""
    
    # Configuration thresholds
    LONG_METHOD_LINES = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MAX_PARAMETERS = 5
    
    def __init__(self):
        super().__init__("csharp")
    
    def _get_base_confidence(self) -> float:
        """C# has moderate confidence with tree-sitter"""
        return 0.80
    
    def analyze(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """
        Analyze C# AST for all code smells
        
        Args:
            ast_tree: Tree-sitter node
            code: Original source code
            
        Returns:
            List of detected code smells
        """
        smells = []
        smells.extend(self.detect_long_methods(ast_tree, code))
        smells.extend(self.detect_complex_methods(ast_tree))
        smells.extend(self.detect_deep_nesting(ast_tree))
        smells.extend(self.detect_long_parameter_lists(ast_tree))
        smells.extend(self.detect_magic_numbers(ast_tree, code))
        return smells
    
    def detect_long_methods(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect methods exceeding line count threshold"""
        smells = []
        methods = self._find_methods(ast_tree)
        
        for method in methods:
            start_line = method.start_point[0] + 1
            end_line = method.end_point[0] + 1
            length = end_line - start_line + 1
            
            if length > self.LONG_METHOD_LINES:
                method_name = self._get_method_name(method, code)
                smells.append(CodeSmell(
                    smell_type=SmellType.LONG_METHOD,
                    function_name=method_name,
                    line_number=start_line,
                    confidence=self.adjust_confidence(0.85),
                    message=f"Method '{method_name}' is {length} lines long",
                    suggestion=f"Split into smaller methods (target: <{self.LONG_METHOD_LINES} lines)",
                    metadata={'length': length}
                ))
        
        return smells
    
    def detect_complex_methods(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect methods with high cyclomatic complexity"""
        smells = []
        methods = self._find_methods(ast_tree)
        
        for method in methods:
            complexity = self._calculate_complexity(method)
            
            if complexity > self.MAX_COMPLEXITY:
                method_name = self._get_method_name(method, None)
                line_num = method.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.COMPLEX_METHOD,
                    function_name=method_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.80),
                    message=f"Method '{method_name}' has complexity {complexity}",
                    suggestion=f"Reduce complexity (target: <{self.MAX_COMPLEXITY})",
                    metadata={'complexity': complexity}
                ))
        
        return smells
    
    def detect_deep_nesting(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect deeply nested code blocks"""
        smells = []
        methods = self._find_methods(ast_tree)
        
        for method in methods:
            max_depth = self._calculate_nesting_depth(method)
            
            if max_depth > self.MAX_NESTING_DEPTH:
                method_name = self._get_method_name(method, None)
                line_num = method.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.DEEP_NESTING,
                    function_name=method_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.85),
                    message=f"Method '{method_name}' has nesting depth {max_depth}",
                    suggestion=f"Use early returns or extract nested logic (target: <{self.MAX_NESTING_DEPTH})",
                    metadata={'depth': max_depth}
                ))
        
        return smells
    
    def detect_long_parameter_lists(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect methods with too many parameters"""
        smells = []
        methods = self._find_methods(ast_tree)
        
        for method in methods:
            param_count = self._count_parameters(method)
            
            if param_count > self.MAX_PARAMETERS:
                method_name = self._get_method_name(method, None)
                line_num = method.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.LONG_PARAMETER_LIST,
                    function_name=method_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.75),
                    message=f"Method '{method_name}' has {param_count} parameters",
                    suggestion=f"Use parameter object or builder pattern (target: <{self.MAX_PARAMETERS})",
                    metadata={'param_count': param_count}
                ))
        
        return smells
    
    def detect_magic_numbers(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect unexplained numeric literals"""
        # Simplified implementation for tree-sitter
        return []
    
    # Helper methods
    
    def _find_methods(self, node: Any) -> List[Any]:
        """Find all method declaration nodes"""
        methods = []
        
        if hasattr(node, 'type'):
            if node.type in ('method_declaration', 'constructor_declaration', 
                            'local_function_statement'):
                methods.append(node)
        
        if hasattr(node, 'children'):
            for child in node.children:
                methods.extend(self._find_methods(child))
        
        return methods
    
    def _get_method_name(self, method: Any, code: str = None) -> str:
        """Extract method name"""
        if hasattr(method, 'children'):
            for child in method.children:
                if hasattr(child, 'type') and child.type == 'identifier':
                    if code:
                        return code[child.start_byte:child.end_byte]
                    return '<method>'
        return '<anonymous>'
    
    def _count_parameters(self, method: Any) -> int:
        """Count method parameters"""
        if hasattr(method, 'children'):
            for child in method.children:
                if hasattr(child, 'type') and child.type == 'parameter_list':
                    # Count parameter children
                    return len([c for c in child.children if hasattr(c, 'type') and c.type == 'parameter'])
        return 0
    
    def _calculate_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        if hasattr(node, 'type'):
            if node.type in ('if_statement', 'while_statement', 'for_statement',
                            'foreach_statement', 'do_statement', 'switch_section',
                            'catch_clause', 'conditional_expression'):
                complexity += 1
        
        if hasattr(node, 'children'):
            for child in node.children:
                complexity += self._calculate_complexity(child) - 1
        
        return max(1, complexity)
    
    def _calculate_nesting_depth(self, node: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        if hasattr(node, 'type'):
            if node.type in ('if_statement', 'while_statement', 'for_statement',
                            'foreach_statement', 'do_statement', 'try_statement',
                            'using_statement', 'lock_statement'):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
        
        if hasattr(node, 'children'):
            for child in node.children:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
