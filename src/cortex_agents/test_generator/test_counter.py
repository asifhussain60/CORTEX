"""
Test Counter Module

Counts the number of test functions in generated test code.
Supports pytest, unittest, and other Python test frameworks.
"""

import ast
import re
from typing import Optional


class TestCounter:
    """
    Counts test functions in Python test code.
    
    Supports:
    - pytest test functions (def test_*)
    - unittest test methods (class TestCase, def test_*)
    - pytest test classes (class Test*, def test_*)
    """
    
    def __init__(self):
        """Initialize TestCounter."""
        pass
    
    def count(self, test_code: str) -> int:
        """
        Count the number of test functions/methods in test code.
        
        Args:
            test_code: Python test code as string
        
        Returns:
            Number of test functions found
        
        Example:
            >>> counter = TestCounter()
            >>> code = '''
            ... def test_addition():
            ...     assert 1 + 1 == 2
            ... 
            ... def test_subtraction():
            ...     assert 2 - 1 == 1
            ... '''
            >>> counter.count(code)
            2
        """
        if not test_code or not isinstance(test_code, str):
            return 0
        
        try:
            # Try AST parsing first (most accurate)
            return self._count_via_ast(test_code)
        except SyntaxError:
            # Fall back to regex if AST fails (malformed code)
            return self._count_via_regex(test_code)
    
    def _count_via_ast(self, test_code: str) -> int:
        """
        Count tests using AST parsing (most accurate).
        
        Args:
            test_code: Python test code
        
        Returns:
            Number of test functions
        """
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            raise  # Re-raise to trigger regex fallback
        
        test_count = 0
        
        # Walk the AST tree
        for node in ast.walk(tree):
            # Count standalone test functions (def test_*)
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_count += 1
            
            # Count test methods in test classes
            elif isinstance(node, ast.ClassDef):
                # Check if it's a test class (TestCase, Test*)
                is_test_class = (
                    node.name.startswith('Test') or
                    'TestCase' in [base.id for base in node.bases if isinstance(base, ast.Name)]
                )
                
                if is_test_class:
                    # Count test methods in this class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                            test_count += 1
        
        return test_count
    
    def _count_via_regex(self, test_code: str) -> int:
        """
        Count tests using regex (fallback for malformed code).
        
        Args:
            test_code: Python test code (possibly incomplete)
        
        Returns:
            Number of test functions found
        """
        # Match: def test_something(...):
        pattern = r'^\s*def\s+test_\w+\s*\('
        matches = re.findall(pattern, test_code, re.MULTILINE)
        return len(matches)
    
    def count_by_type(self, test_code: str) -> dict:
        """
        Count tests grouped by type (function, method, async).
        
        Args:
            test_code: Python test code
        
        Returns:
            Dictionary with counts: {
                'functions': int,
                'methods': int,
                'async_functions': int,
                'total': int
            }
        """
        if not test_code or not isinstance(test_code, str):
            return {
                'functions': 0,
                'methods': 0,
                'async_functions': 0,
                'total': 0
            }
        
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            # Fall back to simple count
            total = self._count_via_regex(test_code)
            return {
                'functions': total,
                'methods': 0,
                'async_functions': 0,
                'total': total
            }
        
        function_count = 0
        method_count = 0
        async_count = 0
        
        # Walk the AST tree
        for node in ast.walk(tree):
            # Count standalone test functions
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    function_count += 1
            
            # Count async test functions
            elif isinstance(node, ast.AsyncFunctionDef):
                if node.name.startswith('test_'):
                    async_count += 1
            
            # Count test methods in test classes
            elif isinstance(node, ast.ClassDef):
                is_test_class = (
                    node.name.startswith('Test') or
                    'TestCase' in [base.id for base in node.bases if isinstance(base, ast.Name)]
                )
                
                if is_test_class:
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if item.name.startswith('test_'):
                                if isinstance(item, ast.AsyncFunctionDef):
                                    async_count += 1
                                else:
                                    method_count += 1
        
        total = function_count + method_count + async_count
        
        return {
            'functions': function_count,
            'methods': method_count,
            'async_functions': async_count,
            'total': total
        }
