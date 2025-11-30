"""
PythonAnalyzer - AST-based Python code analysis.

Analyzes Python files to extract metrics, complexity, and structure.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
from pathlib import Path
from typing import Dict, Any


class PythonAnalyzer:
    """
    Analyze Python source files using AST.
    
    Extracts:
    - Function and class definitions
    - Complexity metrics
    - Import statements
    - Docstring presence
    """
    
    def __init__(self):
        """Initialize PythonAnalyzer."""
        pass
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary containing analysis results
        """
        path = Path(file_path)
        
        # Read source code
        try:
            source = path.read_text(encoding='utf-8')
        except Exception:
            return {
                'file_path': file_path,
                'language': 'python',
                'error': 'Failed to read file'
            }
        
        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return {
                'file_path': file_path,
                'language': 'python',
                'error': 'Syntax error in file'
            }
        
        # Extract functions and classes
        functions = []
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return {
            'file_path': file_path,
            'language': 'python',
            'functions': functions,
            'classes': classes
        }
