"""Code analysis for test generation."""

import ast
from typing import Dict, Any, Optional
from .function_analyzer import FunctionAnalyzer
from .class_analyzer import ClassAnalyzer


class CodeAnalyzer:
    """Analyzes source code to identify testable components."""
    
    def __init__(self):
        """Initialize analyzers."""
        self.function_analyzer = FunctionAnalyzer()
        self.class_analyzer = ClassAnalyzer()
    
    def analyze(self, source_code: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze source code to identify testable components.
        
        Args:
            source_code: Python source code to analyze
            target: Optional specific class/function to target
        
        Returns:
            Analysis results with functions, classes, and scenarios
        """
        try:
            tree = ast.parse(source_code)
            
            functions = []
            classes = []
            scenarios = []
            
            for node in ast.walk(tree):
                # Find function definitions (both sync and async)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions unless specifically targeted
                    if target or not node.name.startswith('_'):
                        func_info = self.function_analyzer.analyze(node)
                        
                        # Check if this matches target
                        if not target or node.name == target:
                            functions.append(func_info)
                            scenarios.extend(func_info["scenarios"])
                
                # Find class definitions
                elif isinstance(node, ast.ClassDef):
                    if not target or node.name == target:
                        class_info = self.class_analyzer.analyze(node)
                        classes.append(class_info)
                        scenarios.extend(class_info["scenarios"])
            
            # Deduplicate scenarios
            scenarios = list(set(scenarios))
            
            return {
                "success": True,
                "functions": functions,
                "classes": classes,
                "scenarios": scenarios,
                "has_async": any(f.get("is_async") for f in functions)
            }
            
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error in source code: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
