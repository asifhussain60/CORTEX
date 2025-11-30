"""
Python Analyzer

AST-based code smell detection for Python code.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
from typing import List, Any
from .base_analyzer import BaseAnalyzer, CodeSmell, SmellType


class PythonAnalyzer(BaseAnalyzer):
    """Python-specific AST analyzer"""
    
    # Configuration thresholds
    LONG_METHOD_LINES = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MAX_PARAMETERS = 5
    
    def __init__(self):
        super().__init__("python")
    
    def _get_base_confidence(self) -> float:
        """Python has highest confidence (most mature AST)"""
        return 0.90
    
    def analyze(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """
        Analyze Python AST for all code smells
        
        Args:
            ast_tree: Python ast.AST tree
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
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate method length
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    length = node.end_lineno - node.lineno + 1
                    
                    if length > self.LONG_METHOD_LINES:
                        smells.append(CodeSmell(
                            smell_type=SmellType.LONG_METHOD,
                            function_name=node.name,
                            line_number=node.lineno,
                            confidence=self.adjust_confidence(0.85),
                            message=f"Method '{node.name}' is {length} lines long",
                            suggestion=f"Split into smaller functions (target: <{self.LONG_METHOD_LINES} lines)",
                            metadata={'length': length}
                        ))
        
        return smells
    
    def detect_complex_methods(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect methods with high cyclomatic complexity"""
        smells = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                
                if complexity > self.MAX_COMPLEXITY:
                    smells.append(CodeSmell(
                        smell_type=SmellType.COMPLEX_METHOD,
                        function_name=node.name,
                        line_number=node.lineno,
                        confidence=self.adjust_confidence(0.80),
                        message=f"Method '{node.name}' has complexity {complexity}",
                        suggestion=f"Reduce complexity (target: <{self.MAX_COMPLEXITY})",
                        metadata={'complexity': complexity}
                    ))
        
        return smells
    
    def detect_deep_nesting(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect deeply nested code blocks"""
        smells = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                max_depth = self._calculate_nesting_depth(node)
                
                if max_depth > self.MAX_NESTING_DEPTH:
                    smells.append(CodeSmell(
                        smell_type=SmellType.DEEP_NESTING,
                        function_name=node.name,
                        line_number=node.lineno,
                        confidence=self.adjust_confidence(0.85),
                        message=f"Method '{node.name}' has nesting depth {max_depth}",
                        suggestion=f"Use early returns or extract nested logic (target: <{self.MAX_NESTING_DEPTH})",
                        metadata={'depth': max_depth}
                    ))
        
        return smells
    
    def detect_long_parameter_lists(self, ast_tree: Any) -> List[CodeSmell]:
        """Detect functions with too many parameters"""
        smells = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                param_count = len(node.args.args)
                
                # Exclude 'self' and 'cls' from count
                if param_count > 0 and node.args.args[0].arg in ('self', 'cls'):
                    param_count -= 1
                
                if param_count > self.MAX_PARAMETERS:
                    smells.append(CodeSmell(
                        smell_type=SmellType.LONG_PARAMETER_LIST,
                        function_name=node.name,
                        line_number=node.lineno,
                        confidence=self.adjust_confidence(0.75),
                        message=f"Method '{node.name}' has {param_count} parameters",
                        suggestion=f"Use parameter object or builder pattern (target: <{self.MAX_PARAMETERS})",
                        metadata={'param_count': param_count}
                    ))
        
        return smells
    
    def detect_magic_numbers(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """Detect unexplained numeric literals"""
        smells = []
        
        # Common acceptable numbers
        ACCEPTABLE_NUMBERS = {0, 1, -1, 2, 10, 100, 1000}
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in ACCEPTABLE_NUMBERS:
                    # Find containing function
                    parent_func = self._find_parent_function(ast_tree, node)
                    func_name = parent_func.name if parent_func else "<module>"
                    
                    smells.append(CodeSmell(
                        smell_type=SmellType.MAGIC_NUMBER,
                        function_name=func_name,
                        line_number=node.lineno if hasattr(node, 'lineno') else 0,
                        confidence=self.adjust_confidence(0.70),
                        message=f"Magic number {node.value} in '{func_name}'",
                        suggestion="Extract to named constant",
                        metadata={'value': node.value}
                    ))
        
        return smells
    
    # Helper methods
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                 ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                 ast.With, ast.AsyncWith, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _find_parent_function(self, tree: ast.AST, target: ast.AST) -> ast.FunctionDef:
        """Find the function containing target node"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for child in ast.walk(node):
                    if child is target:
                        return node
        return None
