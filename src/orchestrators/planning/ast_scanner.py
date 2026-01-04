"""
AST Scanner for Planning v5 Phase 0.

Scans Python codebase to extract architectural metrics:
- Function counts
- Class counts  
- Import counts
- File structure

Integrates with duplicate and orphan detectors for comprehensive analysis.

Author: Asif Hussain
Created: 2026-01-04
"""

import ast
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ASTScanner:
    """
    Scans Python workspace for architectural analysis.
    
    Extracts:
    - Functions (with signatures)
    - Classes (with methods)
    - Imports (modules used)
    - Overall code structure metrics
    
    Usage:
        scanner = ASTScanner(workspace_root=Path("/project"))
        scanner.scan_workspace()
        scanner.save_results(Path("ast-analysis.json"))
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize AST scanner.
        
        Args:
            workspace_root: Root directory of workspace to scan
        """
        self.workspace_root = Path(workspace_root)
        self.results: Dict[str, Any] = {
            "scan_date": None,
            "workspace_root": str(self.workspace_root),
            "files_scanned": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_imports": 0,
            "files": {},
            "errors": []
        }
        logger.info(f"Initialized ASTScanner for {self.workspace_root}")
    
    def scan_workspace(self) -> Dict[str, Any]:
        """
        Scan entire workspace for Python files.
        
        Returns:
            Dictionary with scan results
        """
        logger.info(f"Starting workspace scan: {self.workspace_root}")
        self.results["scan_date"] = datetime.now().isoformat()
        
        # Find all Python files
        python_files = list(self.workspace_root.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            file_result = self.scan_file(file_path)
            if "error" not in file_result:
                rel_path = str(file_path.relative_to(self.workspace_root))
                self.results["files"][rel_path] = file_result
                
                # Update totals
                self.results["total_functions"] += file_result.get("function_count", 0)
                self.results["total_classes"] += file_result.get("class_count", 0)
                self.results["total_imports"] += file_result.get("import_count", 0)
                self.results["files_scanned"] += 1
        
        logger.info(f"Scan complete: {self.results['files_scanned']} files, "
                   f"{self.results['total_functions']} functions, "
                   f"{self.results['total_classes']} classes")
        
        return self.results
    
    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Scan a single Python file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Dictionary with file analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            analyzer = FileAnalyzer()
            analyzer.visit(tree)
            
            return {
                "function_count": len(analyzer.functions),
                "class_count": len(analyzer.classes),
                "import_count": len(analyzer.imports),
                "functions": analyzer.functions,
                "classes": analyzer.classes,
                "imports": analyzer.imports
            }
        
        except SyntaxError as e:
            error_msg = f"Syntax error in {file_path}: {e}"
            logger.warning(error_msg)
            self.results["errors"].append(error_msg)
            return {
                "error": str(e),
                "function_count": 0,
                "class_count": 0,
                "import_count": 0
            }
        
        except Exception as e:
            error_msg = f"Error scanning {file_path}: {e}"
            logger.error(error_msg)
            self.results["errors"].append(error_msg)
            return {
                "error": str(e),
                "function_count": 0,
                "class_count": 0,
                "import_count": 0
            }
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped during scan."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            ".tox",
            ".git",
            "node_modules",
            ".pytest_cache"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def add_duplicate_analysis(self, duplicate_results: Dict[str, Any]) -> None:
        """
        Add duplicate code analysis to results.
        
        Args:
            duplicate_results: Results from PlanningDuplicateDetector
        """
        self.results["duplicate_analysis"] = duplicate_results
        logger.info("Added duplicate analysis to results")
    
    def add_orphan_analysis(self, orphan_results: Dict[str, Any]) -> None:
        """
        Add orphaned function analysis to results.
        
        Args:
            orphan_results: Results from PlanningOrphanDetector
        """
        self.results["orphan_analysis"] = orphan_results
        logger.info("Added orphan analysis to results")
    
    def save_results(self, output_file: Path) -> None:
        """
        Save scan results to JSON file.
        
        Args:
            output_file: Path to output JSON file
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Saved AST analysis to {output_file}")


class FileAnalyzer(ast.NodeVisitor):
    """AST visitor to extract functions, classes, and imports from a file."""
    
    def __init__(self):
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.imports: List[str] = []
        self.current_class: Optional[str] = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        if self.current_class:
            # Method inside class
            self.functions.append(f"{self.current_class}.{node.name}")
        else:
            # Module-level function
            self.functions.append(node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        if self.current_class:
            self.functions.append(f"{self.current_class}.{node.name}")
        else:
            self.functions.append(node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.classes.append(node.name)
        
        # Track class context for methods
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statement."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)
