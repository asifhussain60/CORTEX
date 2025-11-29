"""
JavaScript Analyzer

AST-based code smell detection for JavaScript code using esprima.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import List, Any, Dict
from .base_analyzer import BaseAnalyzer, CodeSmell, SmellType


class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript-specific AST analyzer"""
    
    # Configuration thresholds
    LONG_METHOD_LINES = 50
    MAX_COMPLEXITY = 10
    MAX_NESTING_DEPTH = 4
    MAX_PARAMETERS = 5
    
    def __init__(self):
        super().__init__("javascript")
    
    def _get_base_confidence(self) -> float:
        """JavaScript has good confidence with esprima"""
        return 0.85
    
    def analyze(self, ast_tree: Any, code: str) -> List[CodeSmell]:
        """
        Analyze JavaScript AST for all code smells
        
        Args:
            ast_tree: Esprima AST tree (dict)
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
            if 'loc' in func and func['loc']:
                start = func['loc']['start']['line']
                end = func['loc']['end']['line']
                length = end - start + 1
                
                if length > self.LONG_METHOD_LINES:
                    func_name = self._get_function_name(func)
                    smells.append(CodeSmell(
                        smell_type=SmellType.LONG_METHOD,
                        function_name=func_name,
                        line_number=start,
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
                func_name = self._get_function_name(func)
                line_num = func.get('loc', {}).get('start', {}).get('line', 0) if 'loc' in func else 0
                
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
                func_name = self._get_function_name(func)
                line_num = func.get('loc', {}).get('start', {}).get('line', 0) if 'loc' in func else 0
                
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
            params = func.get('params', [])
            param_count = len(params)
            
            if param_count > self.MAX_PARAMETERS:
                func_name = self._get_function_name(func)
                line_num = func.get('loc', {}).get('start', {}).get('line', 0) if 'loc' in func else 0
                
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
        smells = []
        ACCEPTABLE_NUMBERS = {0, 1, -1, 2, 10, 100, 1000}
        
        literals = self._find_numeric_literals(ast_tree)
        
        for literal in literals:
            value = literal.get('value')
            if value and value not in ACCEPTABLE_NUMBERS:
                line_num = literal.get('loc', {}).get('start', {}).get('line', 0) if 'loc' in literal else 0
                
                smells.append(CodeSmell(
                    smell_type=SmellType.MAGIC_NUMBER,
                    function_name="<function>",
                    line_number=line_num,
                    confidence=self.adjust_confidence(0.70),
                    message=f"Magic number {value}",
                    suggestion="Extract to named constant",
                    metadata={'value': value}
                ))
        
        return smells
    
    # Helper methods
    
    def _find_functions(self, node: Any, functions: List = None) -> List[Dict]:
        """Recursively find all function declarations"""
        if functions is None:
            functions = []
        
        if isinstance(node, dict):
            node_type = node.get('type')
            if node_type in ('FunctionDeclaration', 'FunctionExpression', 
                            'ArrowFunctionExpression', 'MethodDefinition'):
                functions.append(node)
            
            for value in node.values():
                self._find_functions(value, functions)
        elif isinstance(node, list):
            for item in node:
                self._find_functions(item, functions)
        
        return functions
    
    def _find_numeric_literals(self, node: Any, literals: List = None) -> List[Dict]:
        """Recursively find all numeric literals"""
        if literals is None:
            literals = []
        
        if isinstance(node, dict):
            if node.get('type') == 'Literal' and isinstance(node.get('value'), (int, float)):
                literals.append(node)
            
            for value in node.values():
                self._find_numeric_literals(value, literals)
        elif isinstance(node, list):
            for item in node:
                self._find_numeric_literals(item, literals)
        
        return literals
    
    def _get_function_name(self, func: Dict) -> str:
        """Extract function name from node"""
        if func.get('type') == 'MethodDefinition':
            key = func.get('key', {})
            return key.get('name', '<anonymous>')
        
        id_node = func.get('id')
        if id_node and isinstance(id_node, dict):
            return id_node.get('name', '<anonymous>')
        
        return '<anonymous>'
    
    def _calculate_complexity(self, node: Any, complexity: int = 1) -> int:
        """Calculate cyclomatic complexity"""
        if isinstance(node, dict):
            node_type = node.get('type')
            if node_type in ('IfStatement', 'WhileStatement', 'ForStatement',
                            'ForInStatement', 'ForOfStatement', 'DoWhileStatement',
                            'SwitchCase', 'CatchClause', 'ConditionalExpression'):
                complexity += 1
            elif node_type == 'LogicalExpression':
                complexity += 1
            
            for value in node.values():
                complexity = self._calculate_complexity(value, complexity)
        elif isinstance(node, list):
            for item in node:
                complexity = self._calculate_complexity(item, complexity)
        
        return complexity
    
    def _calculate_nesting_depth(self, node: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        if isinstance(node, dict):
            node_type = node.get('type')
            if node_type in ('IfStatement', 'WhileStatement', 'ForStatement',
                            'ForInStatement', 'ForOfStatement', 'DoWhileStatement',
                            'TryStatement', 'WithStatement'):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            for value in node.values():
                child_depth = self._calculate_nesting_depth(value, current_depth)
                max_depth = max(max_depth, child_depth)
        elif isinstance(node, list):
            for item in node:
                child_depth = self._calculate_nesting_depth(item, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
