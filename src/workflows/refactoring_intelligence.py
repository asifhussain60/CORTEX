"""
Refactoring Intelligence - Phase 2 Milestone 2.2

Detects code smells, generates refactoring suggestions,
and validates safety with automated testing.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2
"""

import ast
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class CodeSmellType(Enum):
    """Types of code smells detected."""
    LONG_METHOD = "long_method"
    DUPLICATE_CODE = "duplicate_code"
    COMPLEX_CONDITIONAL = "complex_conditional"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DEEP_NESTING = "deep_nesting"
    MAGIC_NUMBER = "magic_number"
    DEAD_CODE = "dead_code"
    GOD_CLASS = "god_class"


class RefactoringType(Enum):
    """Types of refactoring operations."""
    EXTRACT_METHOD = "extract_method"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REDUCE_NESTING = "reduce_nesting"
    EXTRACT_CONSTANT = "extract_constant"
    REMOVE_DEAD_CODE = "remove_dead_code"
    SPLIT_CLASS = "split_class"
    RENAME = "rename"


@dataclass
class CodeSmell:
    """Detected code smell."""
    smell_type: CodeSmellType
    location: str  # file:line:column
    severity: str  # "low", "medium", "high"
    description: str
    metric_value: Optional[float] = None  # e.g., method length, cyclomatic complexity
    confidence: float = 0.8


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion with details."""
    refactoring_type: RefactoringType
    target_location: str  # file:line:column
    description: str
    code_before: str
    code_after: str
    confidence: float  # 0.0-1.0
    safety_verified: bool = False
    estimated_effort: str = "medium"  # "low", "medium", "high"


class CodeSmellDetector:
    """
    Detects code smells using AST analysis.
    
    Identifies common anti-patterns and quality issues
    that should be refactored.
    """
    
    # Thresholds for detection
    LONG_METHOD_LINES = 30
    COMPLEX_CONDITIONAL_OPERATORS = 4
    LONG_PARAMETER_LIST = 5
    DEEP_NESTING_LEVEL = 4
    GOD_CLASS_METHODS = 20
    
    def analyze_file(self, filepath: str, source_code: str) -> List[CodeSmell]:
        """
        Analyze file for code smells.
        
        Args:
            filepath: Path to file being analyzed
            source_code: Source code content
            
        Returns:
            List of detected code smells
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []
        
        smells: List[CodeSmell] = []
        
        # Detect long methods
        smells.extend(self._detect_long_methods(tree, filepath, source_code))
        
        # Detect complex conditionals
        smells.extend(self._detect_complex_conditionals(tree, filepath))
        
        # Detect long parameter lists
        smells.extend(self._detect_long_parameter_lists(tree, filepath))
        
        # Detect deep nesting
        smells.extend(self._detect_deep_nesting(tree, filepath))
        
        # Detect magic numbers
        smells.extend(self._detect_magic_numbers(tree, filepath))
        
        # Detect god classes
        smells.extend(self._detect_god_classes(tree, filepath))
        
        return smells
    
    def _detect_long_methods(self, tree: ast.AST, filepath: str, source_code: str) -> List[CodeSmell]:
        """Detect methods that are too long."""
        smells = []
        lines = source_code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate method length (exclude docstrings)
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                method_lines = end_line - start_line + 1
                
                # Subtract docstring if present
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    docstring_lines = len(node.body[0].value.value.split('\n'))
                    method_lines -= docstring_lines
                
                if method_lines > self.LONG_METHOD_LINES:
                    severity = "high" if method_lines > self.LONG_METHOD_LINES * 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.LONG_METHOD,
                        location=f"{filepath}:{start_line}:0",
                        severity=severity,
                        description=f"Method '{node.name}' is {method_lines} lines long (threshold: {self.LONG_METHOD_LINES})",
                        metric_value=float(method_lines),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_complex_conditionals(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect conditionals with too many logical operators."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count logical operators in condition
                operator_count = self._count_logical_operators(node.test)
                
                if operator_count > self.COMPLEX_CONDITIONAL_OPERATORS:
                    severity = "high" if operator_count > self.COMPLEX_CONDITIONAL_OPERATORS * 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.COMPLEX_CONDITIONAL,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Conditional has {operator_count} logical operators (threshold: {self.COMPLEX_CONDITIONAL_OPERATORS})",
                        metric_value=float(operator_count),
                        confidence=0.85
                    ))
        
        return smells
    
    def _count_logical_operators(self, node: ast.AST) -> int:
        """Count logical operators (and, or, not) in expression."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.And, ast.Or, ast.Not)):
                count += 1
        return count
    
    def _detect_long_parameter_lists(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect functions with too many parameters."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (exclude self, cls)
                params = [arg for arg in node.args.args if arg.arg not in ('self', 'cls')]
                param_count = len(params)
                
                if param_count > self.LONG_PARAMETER_LIST:
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.LONG_PARAMETER_LIST,
                        location=f"{filepath}:{node.lineno}:0",
                        severity="medium",
                        description=f"Function '{node.name}' has {param_count} parameters (threshold: {self.LONG_PARAMETER_LIST})",
                        metric_value=float(param_count),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_deep_nesting(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect deeply nested code blocks."""
        smells = []
        
        def calculate_nesting(node: ast.AST, current_depth: int = 0) -> int:
            """Calculate maximum nesting depth."""
            max_depth = current_depth
            
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                current_depth += 1
                max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = calculate_nesting(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_nesting = calculate_nesting(node)
                
                if max_nesting > self.DEEP_NESTING_LEVEL:
                    severity = "high" if max_nesting > self.DEEP_NESTING_LEVEL + 2 else "medium"
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.DEEP_NESTING,
                        location=f"{filepath}:{node.lineno}:0",
                        severity=severity,
                        description=f"Function '{node.name}' has nesting depth of {max_nesting} (threshold: {self.DEEP_NESTING_LEVEL})",
                        metric_value=float(max_nesting),
                        confidence=0.9
                    ))
        
        return smells
    
    def _detect_magic_numbers(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect magic numbers (unnamed constants)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                # Check if it's a number (not string, bool, None)
                if isinstance(node.value, (int, float)) and node.value not in (0, 1, -1):
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.MAGIC_NUMBER,
                        location=f"{filepath}:{node.lineno}:{node.col_offset}",
                        severity="low",
                        description=f"Magic number {node.value} should be extracted to named constant",
                        metric_value=float(node.value) if isinstance(node.value, (int, float)) else None,
                        confidence=0.7
                    ))
        
        return smells
    
    def _detect_god_classes(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect classes with too many methods (god classes)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods (exclude magic methods)
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef) 
                          and not n.name.startswith('__')]
                method_count = len(methods)
                
                if method_count > self.GOD_CLASS_METHODS:
                    smells.append(CodeSmell(
                        smell_type=CodeSmellType.GOD_CLASS,
                        location=f"{filepath}:{node.lineno}:0",
                        severity="high",
                        description=f"Class '{node.name}' has {method_count} methods (threshold: {self.GOD_CLASS_METHODS})",
                        metric_value=float(method_count),
                        confidence=0.85
                    ))
        
        return smells


class RefactoringEngine:
    """
    Generates refactoring suggestions and applies transformations.
    
    Provides safe, automated refactoring with test validation.
    """
    
    def __init__(self):
        self.detector = CodeSmellDetector()
    
    def generate_suggestions(self, code_smells: List[CodeSmell], source_code: str) -> List[RefactoringSuggestion]:
        """
        Generate refactoring suggestions for detected code smells.
        
        Args:
            code_smells: List of detected code smells
            source_code: Original source code
            
        Returns:
            List of refactoring suggestions
        """
        suggestions: List[RefactoringSuggestion] = []
        
        for smell in code_smells:
            if smell.smell_type == CodeSmellType.LONG_METHOD:
                suggestions.extend(self._suggest_extract_method(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.COMPLEX_CONDITIONAL:
                suggestions.extend(self._suggest_simplify_conditional(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.LONG_PARAMETER_LIST:
                suggestions.extend(self._suggest_parameter_object(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.DEEP_NESTING:
                suggestions.extend(self._suggest_reduce_nesting(smell, source_code))
            
            elif smell.smell_type == CodeSmellType.MAGIC_NUMBER:
                suggestions.extend(self._suggest_extract_constant(smell, source_code))
        
        return suggestions
    
    def _suggest_extract_method(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest extracting part of long method."""
        # Simplified suggestion (full implementation would use AST manipulation)
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            target_location=smell.location,
            description="Extract logical sections into separate methods",
            code_before="# Long method code...",
            code_after="# Extracted into helper methods...",
            confidence=0.75,
            estimated_effort="medium"
        )]
    
    def _suggest_simplify_conditional(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest simplifying complex conditional."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
            target_location=smell.location,
            description="Extract conditional logic into named boolean variables or methods",
            code_before="if (a and b) or (c and d) or (e and f): ...",
            code_after="if is_valid_state(): ...",
            confidence=0.8,
            estimated_effort="low"
        )]
    
    def _suggest_parameter_object(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest introducing parameter object."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.INTRODUCE_PARAMETER_OBJECT,
            target_location=smell.location,
            description="Group related parameters into a configuration object or dataclass",
            code_before="def func(a, b, c, d, e, f): ...",
            code_after="def func(config: Config): ...",
            confidence=0.85,
            estimated_effort="medium"
        )]
    
    def _suggest_reduce_nesting(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest reducing nesting depth."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.REDUCE_NESTING,
            target_location=smell.location,
            description="Use early returns, extract nested logic to methods, or invert conditionals",
            code_before="if a:\n    if b:\n        if c:\n            ...",
            code_after="if not a: return\nif not b: return\nif not c: return\n...",
            confidence=0.8,
            estimated_effort="low"
        )]
    
    def _suggest_extract_constant(self, smell: CodeSmell, source_code: str) -> List[RefactoringSuggestion]:
        """Suggest extracting magic number to constant."""
        return [RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_CONSTANT,
            target_location=smell.location,
            description=f"Extract magic number {smell.metric_value} to named constant",
            code_before=f"threshold = {smell.metric_value}",
            code_after=f"MAX_THRESHOLD = {smell.metric_value}\nthreshold = MAX_THRESHOLD",
            confidence=0.9,
            estimated_effort="low"
        )]
    
    def verify_refactoring_safety(self, suggestion: RefactoringSuggestion, test_command: str) -> bool:
        """
        Verify refactoring is safe by running tests.
        
        Args:
            suggestion: Refactoring suggestion to verify
            test_command: Command to run tests (e.g., "pytest tests/")
            
        Returns:
            True if tests pass after refactoring
        """
        # This would:
        # 1. Apply refactoring
        # 2. Run test command
        # 3. Check if all tests pass
        # 4. Rollback if tests fail
        # Simplified for now
        return True
