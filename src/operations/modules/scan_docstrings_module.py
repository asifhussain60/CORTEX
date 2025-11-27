"""
Scan Python docstrings module for documentation generation.

Part of the Documentation Update operation - extracts docstrings from Python source files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


@dataclass
class DocstringInfo:
    """Information about a docstring."""
    module_path: str
    object_name: str
    object_type: str  # "module", "class", "function", "method"
    docstring: Optional[str]
    line_number: int
    signature: Optional[str] = None
    parent_class: Optional[str] = None


class ScanDocstringsModule(BaseOperationModule):
    """
    Scan Python source files and extract docstrings.
    
    Extracts docstrings from:
    - Modules (file-level docstrings)
    - Classes
    - Functions
    - Methods
    
    Builds a structured index of all documentation strings in the codebase.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="scan_docstrings",
            name="Scan Docstrings",
            description="Extract docstrings from Python files",
            phase=OperationPhase.PREPARATION,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute docstring scanning.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with docstring index
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            src_dir = project_root / "src"
            
            self.log_info(f"Scanning Python files in {src_dir}")
            
            if not src_dir.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Source directory not found",
                    errors=["src/ directory does not exist"]
                )
            
            # Find all Python files
            python_files = self._find_python_files(src_dir)
            self.log_info(f"Found {len(python_files)} Python files")
            
            # Extract docstrings
            docstrings = []
            for py_file in python_files:
                file_docstrings = self._extract_docstrings(py_file, project_root)
                docstrings.extend(file_docstrings)
            
            # Organize by type
            docstring_index = self._organize_docstrings(docstrings)
            
            self.log_info(
                f"Extracted {len(docstrings)} docstrings "
                f"({docstring_index['stats']['modules']} modules, "
                f"{docstring_index['stats']['classes']} classes, "
                f"{docstring_index['stats']['functions']} functions)"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Scanned {len(python_files)} files, extracted {len(docstrings)} docstrings",
                data={
                    "docstring_index": docstring_index,
                    "total_docstrings": len(docstrings),
                    "files_scanned": len(python_files)
                }
            )
            
        except Exception as e:
            self.log_error(f"Failed to scan docstrings: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Docstring scanning failed",
                errors=[str(e)]
            )
    
    def _find_python_files(self, directory: Path) -> List[Path]:
        """
        Find all Python files in directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of Python file paths
        """
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('_'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _extract_docstrings(self, file_path: Path, project_root: Path) -> List[DocstringInfo]:
        """
        Extract docstrings from a Python file.
        
        Args:
            file_path: Path to Python file
            project_root: Project root directory
            
        Returns:
            List of DocstringInfo objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Get relative module path
            relative_path = file_path.relative_to(project_root)
            module_path = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            docstrings = []
            
            # Module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                docstrings.append(DocstringInfo(
                    module_path=module_path,
                    object_name=module_path.split('.')[-1],
                    object_type="module",
                    docstring=module_docstring,
                    line_number=1
                ))
            
            # Extract from classes and functions  
            # Use simpler iteration to avoid complex AST walking issues
            for node in tree.body:  # Only top-level nodes
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(DocstringInfo(
                            module_path=module_path,
                            object_name=node.name,
                            object_type="class",
                            docstring=docstring,
                            line_number=node.lineno
                        ))
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_docstring = ast.get_docstring(item)
                            if method_docstring:
                                docstrings.append(DocstringInfo(
                                    module_path=module_path,
                                    object_name=item.name,
                                    object_type="method",
                                    docstring=method_docstring,
                                    line_number=item.lineno,
                                    parent_class=node.name,
                                    signature=self._get_signature(item)
                                ))
                
                elif isinstance(node, ast.FunctionDef):
                    # Top-level functions
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(DocstringInfo(
                            module_path=module_path,
                            object_name=node.name,
                            object_type="function",
                            docstring=docstring,
                            line_number=node.lineno,
                            signature=self._get_signature(node)
                        ))
            
            return docstrings
            
        except Exception as e:
            self.log_warning(f"Failed to parse {file_path}: {e}")
            return []
    
    def _get_signature(self, node: ast.FunctionDef) -> str:
        """
        Get function/method signature.
        
        Args:
            node: AST function definition node
            
        Returns:
            Function signature string
        """
        args = []
        
        for arg in node.args.args:
            args.append(arg.arg)
        
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        return f"{node.name}({', '.join(args)})"
    
    def _organize_docstrings(self, docstrings: List[DocstringInfo]) -> Dict[str, Any]:
        """
        Organize docstrings into structured index.
        
        Args:
            docstrings: List of docstring info
            
        Returns:
            Structured docstring index
        """
        index = {
            "modules": [],
            "classes": [],
            "functions": [],
            "methods": [],
            "stats": {
                "modules": 0,
                "classes": 0,
                "functions": 0,
                "methods": 0
            }
        }
        
        for ds in docstrings:
            entry = {
                "module_path": ds.module_path,
                "name": ds.object_name,
                "docstring": ds.docstring,
                "line_number": ds.line_number
            }
            
            if ds.signature:
                entry["signature"] = ds.signature
            if ds.parent_class:
                entry["parent_class"] = ds.parent_class
            
            # Correct pluralization: class -> classes, not classs
            plural_type = f"{ds.object_type}es" if ds.object_type == "class" else f"{ds.object_type}s"
            index[plural_type].append(entry)
            index["stats"][plural_type] += 1
        
        return index


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return ScanDocstringsModule()
