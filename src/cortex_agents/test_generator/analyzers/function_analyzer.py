"""Function analysis for test generation."""

import ast
from typing import Dict, Any


class FunctionAnalyzer:
    """Analyzes function definitions for test generation."""
    
    def analyze(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Analyze a function definition.
        
        Args:
            node: AST FunctionDef node
        
        Returns:
            Function analysis info
        """
        # Get function signature
        args = [arg.arg for arg in node.args.args]
        
        # Detect scenarios based on function characteristics
        scenarios = ["basic"]
        
        # Check for error handling
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                scenarios.append("error_handling")
                break
        
        # Check for conditionals (edge cases)
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                scenarios.append("edge_cases")
                break
        
        return {
            "name": node.name,
            "args": args,
            "arg_count": len(args),
            "scenarios": scenarios,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node))
        }
