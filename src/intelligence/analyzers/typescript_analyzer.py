"""
TypeScript Analyzer

AST-based code smell detection for TypeScript code using tree-sitter.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import List, Any
from .base_analyzer import BaseAnalyzer, CodeSmell, SmellType


class TypeScriptAnalyzer(BaseAnalyzer):
    """TypeScript-specific AST analyzer using tree-sitter"""
    
    # Configuration thresholds
    LONG_METHOD_LINES = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MAX_PARAMETERS = 5
    
    def __init__(self):
        super().__init__("typescript")
    
    def _get_base_confidence(self) -> float:
        """TypeScript has good confidence with tree-sitter"""
        return 0.85
    
    def analyze(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """
        Analyze TypeScript AST for all code smells
        
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
        functions = self._find_functions(ast_tree)
        
        for func in functions:
            start_line = func.start_point[0] + 1
            end_line = func.end_point[0] + 1
            length = end_line - start_line + 1
            
            if length > self.LONG_METHOD_LINES:
                func_name = self._get_function_name(func, code)
                smells.append(CodeSmell(
                    smell_type=SmellType.LONG_METHOD,
                    function_name=func_name,
                    line_number=start_line,
                    confidence=self.adjust_confidence(0.85),
                    message=f"Function '{func_name}' is {length} lines long",
                    suggestion=f"Split into smaller functions (target: <{self.LONG_METHOD_LINES} lines)",
                    metadata={'length': length}
                ))
        
        return smells
    
    def detect_complex_methods(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect methods with high cyclomatic complexity"""
        smells = []
        functions = self._find_functions(ast_tree)
        
        for func in functions:
            complexity = self._calculate_complexity(func)
            
            if complexity > self.MAX_COMPLEXITY:
                func_name = self._get_function_name(func, None)
                line_num = func.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.COMPLEX_METHOD,
                    function_name=func_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.80),
                    message=f"Function '{func_name}' has complexity {complexity}",
                    suggestion=f"Reduce complexity (target: <{self.MAX_COMPLEXITY})",
                    metadata={'complexity': complexity}
                ))
        
        return smells
    
    def detect_deep_nesting(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect deeply nested code blocks"""
        smells = []
        functions = self._find_functions(ast_tree)
        
        for func in functions:
            max_depth = self._calculate_nesting_depth(func)
            
            if max_depth > self.MAX_NESTING_DEPTH:
                func_name = self._get_function_name(func, None)
                line_num = func.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.DEEP_NESTING,
                    function_name=func_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.85),
                    message=f"Function '{func_name}' has nesting depth {max_depth}",
                    suggestion=f"Use early returns or extract nested logic (target: <{self.MAX_NESTING_DEPTH})",
                    metadata={'depth': max_depth}
                ))
        
        return smells
    
    def detect_long_parameter_lists(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect functions with too many parameters"""
        smells = []
        functions = self._find_functions(ast_tree)
        
        for func in functions:
            param_count = self._count_parameters(func)
            
            if param_count > self.MAX_PARAMETERS:
                func_name = self._get_function_name(func, None)
                line_num = func.start_point[0] + 1
                
                smells.append(CodeSmell(
                    smell_type=SmellType.LONG_PARAMETER_LIST,
                    function_name=func_name,
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.75),
                    message=f"Function '{func_name}' has {param_count} parameters",
                    suggestion=f"Use options object or builder pattern (target: <{self.MAX_PARAMETERS})",
                    metadata={'param_count': param_count}
                ))
        
        return smells
    
    def detect_magic_numbers(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect unexplained numeric literals"""
        # Simplified implementation for tree-sitter
        return []
    
    # Helper methods
    
    def _find_functions(self, node: Any) -> List[Any]:
        """Find all function nodes"""
        functions = []
        
        if hasattr(node, 'type'):
            if node.type in ('function_declaration', 'method_definition', 
                            'arrow_function', 'function_expression'):
                functions.append(node)
        
        if hasattr(node, 'children'):
            for child in node.children:
                functions.extend(self._find_functions(child))
        
        return functions
    
    def _get_function_name(self, func: Any, code: str = None) -> str:
        """Extract function name"""
        if hasattr(func, 'children'):
            for child in func.children:
                if hasattr(child, 'type') and child.type == 'identifier':
                    if code:
                        return code[child.start_byte:child.end_byte]
                    return '<function>'
        return '<anonymous>'
    
    def _count_parameters(self, func: Any) -> int:
        """Count function parameters"""
        if hasattr(func, 'children'):
            for child in func.children:
                if hasattr(child, 'type') and child.type == 'formal_parameters':
                    # Count identifier children
                    return len([c for c in child.children if hasattr(c, 'type') and c.type == 'identifier'])
        return 0
    
    def _calculate_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        if hasattr(node, 'type'):
            if node.type in ('if_statement', 'while_statement', 'for_statement',
                            'for_in_statement', 'do_statement', 'switch_case',
                            'catch_clause', 'ternary_expression'):
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
                            'for_in_statement', 'do_statement', 'try_statement'):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
        
        if hasattr(node, 'children'):
            for child in node.children:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
