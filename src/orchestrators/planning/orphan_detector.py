"""
Planning-Specific Orphan Detector.

Identifies unused functions and classes in codebase.
Uses call graph analysis to detect dead code.

Author: Asif Hussain
Created: 2026-01-04
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

logger = logging.getLogger(__name__)


class PlanningOrphanDetector:
    """
    Detects orphaned (unused) functions and classes.
    
    Algorithm:
    1. Build call graph of all functions/classes
    2. Identify entry points (main, tests, __init__)
    3. Mark reachable functions from entry points
    4. Report unreachable functions as orphans
    
    Usage:
        detector = PlanningOrphanDetector(workspace_root=Path("/project"))
        results = detector.find_orphaned_functions()
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize orphan detector.
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = Path(workspace_root)
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.calls: Dict[str, Set[str]] = {}
        self.entry_points: Set[str] = set()
        
        logger.info(f"Initialized PlanningOrphanDetector for {workspace_root}")
    
    def find_orphaned_functions(self) -> Dict[str, Any]:
        """
        Find orphaned functions in workspace.
        
        Returns:
            Dictionary with orphan analysis results
        """
        logger.info(f"Analyzing workspace for orphaned functions")
        
        # Step 1: Build function registry and call graph
        python_files = list(self.workspace_root.rglob("*.py"))
        self._build_call_graph(python_files)
        
        # Step 2: Identify entry points
        self._identify_entry_points()
        
        # Step 3: Mark reachable functions
        reachable = self._find_reachable_functions()
        
        # Step 4: Find orphans (defined but not reachable)
        orphaned = []
        for func_name, func_info in self.functions.items():
            if func_name not in reachable and not self._is_special_function(func_name):
                orphaned.append({
                    "name": func_name,
                    "file": func_info["file"],
                    "line": func_info["line"],
                    "type": func_info["type"]
                })
        
        total_functions = len(self.functions)
        orphaned_count = len(orphaned)
        orphaned_percentage = (
            (orphaned_count / total_functions * 100)
            if total_functions > 0 else 0
        )
        
        logger.info(f"Found {orphaned_count} orphaned functions out of {total_functions}")
        
        return {
            "orphaned_functions": orphaned,
            "total_functions": total_functions,
            "orphaned_count": orphaned_count,
            "orphaned_percentage": round(orphaned_percentage, 2),
            "reachable_count": len(reachable)
        }
    
    def _build_call_graph(self, file_paths: List[Path]) -> None:
        """Build function registry and call graph."""
        for file_path in file_paths:
            if self._should_skip(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source, filename=str(file_path))
                analyzer = CallGraphAnalyzer(file_path, self.workspace_root)
                analyzer.visit(tree)
                
                # Register functions
                for func_name, func_info in analyzer.functions.items():
                    self.functions[func_name] = func_info
                
                # Register calls
                for caller, callees in analyzer.calls.items():
                    if caller not in self.calls:
                        self.calls[caller] = set()
                    self.calls[caller].update(callees)
            
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
    
    def _identify_entry_points(self) -> None:
        """Identify entry point functions."""
        for func_name in self.functions:
            # Entry points: main, if __name__ == "__main__", test functions, __init__
            if (func_name == "main" or
                func_name.startswith("test_") or
                func_name == "__init__" or
                func_name.startswith("_test")):
                self.entry_points.add(func_name)
        
        logger.debug(f"Identified {len(self.entry_points)} entry points")
    
    def _find_reachable_functions(self) -> Set[str]:
        """Find all functions reachable from entry points."""
        reachable = set()
        to_visit = list(self.entry_points)
        
        while to_visit:
            current = to_visit.pop()
            if current in reachable:
                continue
            
            reachable.add(current)
            
            # Add all functions called by current
            if current in self.calls:
                for callee in self.calls[current]:
                    if callee not in reachable:
                        to_visit.append(callee)
        
        return reachable
    
    def _is_special_function(self, func_name: str) -> bool:
        """Check if function is special (dunder, property, etc.)."""
        special_patterns = [
            "__init__",
            "__str__",
            "__repr__",
            "__eq__",
            "__hash__",
            "__call__",
            "__enter__",
            "__exit__",
            "__new__",
            "__del__"
        ]
        
        return any(func_name.startswith(pattern) for pattern in special_patterns)
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            ".tox",
            ".git",
            "node_modules"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)


class CallGraphAnalyzer(ast.NodeVisitor):
    """AST visitor to build call graph."""
    
    def __init__(self, file_path: Path, workspace_root: Path):
        self.file_path = file_path
        self.workspace_root = workspace_root
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.calls: Dict[str, Set[str]] = {}
        self.current_function: Optional[str] = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        func_name = node.name
        
        # Register function
        self.functions[func_name] = {
            "file": str(self.file_path.relative_to(self.workspace_root)),
            "line": node.lineno,
            "type": "function"
        }
        
        # Visit function body to find calls
        old_function = self.current_function
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.visit_FunctionDef(node)  # Same logic
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        class_name = node.name
        
        # Register class
        self.functions[class_name] = {
            "file": str(self.file_path.relative_to(self.workspace_root)),
            "line": node.lineno,
            "type": "class"
        }
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call."""
        if self.current_function:
            # Extract called function name
            callee_name = self._get_call_name(node.func)
            
            if callee_name:
                if self.current_function not in self.calls:
                    self.calls[self.current_function] = set()
                self.calls[self.current_function].add(callee_name)
        
        self.generic_visit(node)
    
    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        """Extract function name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
