"""
Planning-Specific Duplicate Detector.

Detects duplicate code patterns at function/class level (not just file level).
Uses AST-based comparison for semantic duplicate detection.

Author: Asif Hussain
Created: 2026-01-04
"""

import ast
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class PlanningDuplicateDetector:
    """
    Detects duplicate code at semantic level using AST.
    
    Unlike file-level duplicate detection (vacuum), this detector:
    - Compares function/class bodies
    - Ignores variable names (semantic equivalence)
    - Reports code-level duplicates
    
    Usage:
        detector = PlanningDuplicateDetector()
        results = detector.find_code_duplicates(python_files)
    """
    
    def __init__(self, min_lines: int = 3):
        """
        Initialize duplicate detector.
        
        Args:
            min_lines: Minimum lines for a function to be checked
        """
        self.min_lines = min_lines
        self.stats = {
            'files_analyzed': 0,
            'functions_analyzed': 0,
            'duplicates_found': 0
        }
        logger.info(f"Initialized PlanningDuplicateDetector (min_lines={min_lines})")
    
    def find_code_duplicates(self, file_paths: List[Path]) -> Dict[str, Any]:
        """
        Find duplicate code patterns in Python files.
        
        Args:
            file_paths: List of Python file paths to analyze
        
        Returns:
            Dictionary with duplicate analysis results
        """
        logger.info(f"Analyzing {len(file_paths)} files for duplicates")
        
        # Extract functions from all files
        function_hashes: Dict[str, List[Tuple[str, str, int]]] = defaultdict(list)
        
        for file_path in file_paths:
            functions = self._extract_functions(file_path)
            self.stats['files_analyzed'] += 1
            
            for func_name, func_ast, line_no in functions:
                # Generate semantic hash
                func_hash = self._semantic_hash(func_ast)
                function_hashes[func_hash].append((str(file_path), func_name, line_no))
                self.stats['functions_analyzed'] += 1
        
        # Find duplicates (hash appears more than once)
        duplicate_groups = []
        for func_hash, occurrences in function_hashes.items():
            if len(occurrences) > 1:
                duplicate_groups.append({
                    "hash": func_hash,
                    "occurrences": [
                        {
                            "file": file,
                            "function": func,
                            "line": line
                        }
                        for file, func, line in occurrences
                    ]
                })
                self.stats['duplicates_found'] += 1
        
        total_functions = self.stats['functions_analyzed']
        duplicate_percentage = (
            (self.stats['duplicates_found'] / total_functions * 100)
            if total_functions > 0 else 0
        )
        
        logger.info(f"Found {len(duplicate_groups)} duplicate patterns")
        
        return {
            "duplicate_groups": duplicate_groups,
            "duplicates_found": len(duplicate_groups),
            "total_functions": total_functions,
            "duplicate_percentage": round(duplicate_percentage, 2),
            "stats": self.stats.copy()
        }
    
    def _extract_functions(self, file_path: Path) -> List[Tuple[str, ast.FunctionDef, int]]:
        """
        Extract function definitions from a Python file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of (function_name, function_ast, line_number) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if function meets minimum length
                    if self._get_function_lines(node) >= self.min_lines:
                        functions.append((node.name, node, node.lineno))
            
            return functions
        
        except Exception as e:
            logger.warning(f"Error extracting functions from {file_path}: {e}")
            return []
    
    def _get_function_lines(self, func_node: ast.FunctionDef) -> int:
        """Count lines in function body."""
        if not func_node.body:
            return 0
        
        first_line = func_node.body[0].lineno
        last_line = func_node.body[-1].lineno
        
        # For multi-line statements, use end_lineno if available
        if hasattr(func_node.body[-1], 'end_lineno') and func_node.body[-1].end_lineno:
            last_line = func_node.body[-1].end_lineno
        
        return last_line - first_line + 1
    
    def _semantic_hash(self, func_node: ast.FunctionDef) -> str:
        """
        Generate semantic hash of function.
        
        Normalizes:
        - Variable names
        - Argument names
        - Whitespace
        
        Preserves:
        - Structure
        - Operations
        - Constants
        
        Args:
            func_node: AST node for function
        
        Returns:
            SHA256 hash of normalized function
        """
        # Normalize the AST
        normalized = self._normalize_ast(func_node)
        
        # Convert to string and hash
        ast_str = ast.dump(normalized, annotate_fields=False)
        return hashlib.sha256(ast_str.encode()).hexdigest()[:16]
    
    def _normalize_ast(self, node: ast.AST) -> ast.AST:
        """
        Normalize AST for semantic comparison.
        
        Renames all variables to generic names (var_1, var_2, etc.)
        to detect structurally identical code.
        """
        # Create a copy to avoid modifying original
        node_copy = ast.parse(ast.unparse(node)).body[0]
        
        # Variable renaming map
        var_map: Dict[str, str] = {}
        var_counter = [0]  # Use list for closure
        
        class Normalizer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id not in var_map:
                    var_map[node.id] = f"var_{var_counter[0]}"
                    var_counter[0] += 1
                node.id = var_map[node.id]
                return node
            
            def visit_arg(self, node):
                if node.arg not in var_map:
                    var_map[node.arg] = f"var_{var_counter[0]}"
                    var_counter[0] += 1
                node.arg = var_map[node.arg]
                return node
        
        normalizer = Normalizer()
        return normalizer.visit(node_copy)
