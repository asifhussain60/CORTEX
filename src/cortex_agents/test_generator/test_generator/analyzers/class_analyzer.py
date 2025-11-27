"""Class analysis for test generation."""

import ast
from typing import Dict, Any
from .function_analyzer import FunctionAnalyzer


class ClassAnalyzer:
    """Analyzes class definitions for test generation."""
    
    def __init__(self):
        """Initialize with function analyzer."""
        self.function_analyzer = FunctionAnalyzer()
    
    def analyze(self, node: ast.ClassDef) -> Dict[str, Any]:
        """
        Analyze a class definition.
        
        Args:
            node: AST ClassDef node
        
        Returns:
            Class analysis info
        """
        methods = []
        scenarios = ["basic"]
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.function_analyzer.analyze(item)
                methods.append(method_info)
                scenarios.extend(method_info["scenarios"])
        
        # Check for __init__ method
        has_init = any(m["name"] == "__init__" for m in methods)
        
        if has_init:
            scenarios.append("initialization")
        
        return {
            "name": node.name,
            "methods": methods,
            "method_count": len(methods),
            "scenarios": list(set(scenarios)),
            "has_init": has_init
        }
