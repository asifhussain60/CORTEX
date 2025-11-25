"""
Orchestrator Scanner - Convention-Based Discovery

Discovers all orchestrators using filesystem + AST analysis:
- Walks src/operations/modules/, src/workflows/ recursively
- Parses Python files with AST
- Finds classes ending in 'Orchestrator'
- Validates inheritance from BaseOperationModule
- Extracts metadata (docstring, methods, dependencies)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class OrchestratorScanner:
    """
    Convention-based orchestrator discovery.
    
    Scans filesystem for orchestrator classes without hardcoded lists.
    Uses AST for safe parsing without executing code.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize orchestrator scanner.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.src_root = self.project_root / "src"
        
        # Scan paths (convention-based)
        self.scan_paths = [
            self.src_root / "operations" / "modules",
            self.src_root / "workflows"
        ]
        
        # Exclusion patterns
        self.exclude_files = {
            "base_operation_module.py",
            "__init__.py",
            "abstract_orchestrator.py"
        }
    
    def discover(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all orchestrators in project.
        
        Returns:
            Dict mapping orchestrator name to metadata:
            {
                "TDDWorkflowOrchestrator": {
                    "path": Path(...),
                    "module_path": "src.workflows.tdd_workflow_orchestrator",
                    "class_name": "TDDWorkflowOrchestrator",
                    "docstring": "Complete TDD workflow...",
                    "methods": ["execute", "start_session", "run_tests"],
                    "dependencies": ["ViewDiscoveryAgent", "DebugAgent"],
                    "has_docstring": True,
                    "inherits_base": True
                }
            }
        """
        orchestrators = {}
        
        for scan_path in self.scan_paths:
            if not scan_path.exists():
                logger.warning(f"Scan path not found: {scan_path}")
                continue
            
            # Walk directory recursively
            for py_file in scan_path.rglob("*.py"):
                # Skip excluded files
                if py_file.name in self.exclude_files:
                    continue
                
                # Skip __pycache__
                if "__pycache__" in py_file.parts:
                    continue
                
                # Scan file for orchestrators
                found = self._scan_file(py_file)
                orchestrators.update(found)
        
        logger.info(f"Discovered {len(orchestrators)} orchestrators")
        return orchestrators
    
    def _scan_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Scan single Python file for orchestrator classes.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Dict of discovered orchestrators in this file
        """
        orchestrators = {}
        
        try:
            # Parse file with AST
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Find all classes
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                
                # Check if name ends with 'Orchestrator'
                if not node.name.endswith("Orchestrator"):
                    continue
                
                # Extract metadata
                metadata = self._extract_metadata(node, file_path)
                orchestrators[node.name] = metadata
        
        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")
        
        return orchestrators
    
    def _extract_metadata(
        self,
        class_node: ast.ClassDef,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Extract metadata from orchestrator class AST node.
        
        Args:
            class_node: AST ClassDef node
            file_path: Path to source file
        
        Returns:
            Metadata dictionary
        """
        # Extract docstring
        docstring = ast.get_docstring(class_node)
        
        # Extract methods
        methods = [
            node.name
            for node in ast.walk(class_node)
            if isinstance(node, ast.FunctionDef)
        ]
        
        # Check inheritance
        inherits_base = any(
            self._is_base_class(base)
            for base in class_node.bases
        )
        
        # Extract dependencies (imports at top of file)
        dependencies = self._extract_dependencies(file_path)
        
        # Build module path
        relative_path = file_path.relative_to(self.project_root)
        module_path = str(relative_path.with_suffix("")).replace("\\", ".").replace("/", ".")
        
        return {
            "path": file_path,
            "module_path": module_path,
            "class_name": class_node.name,
            "docstring": docstring,
            "methods": methods,
            "dependencies": dependencies,
            "has_docstring": docstring is not None,
            "inherits_base": inherits_base
        }
    
    def _is_base_class(self, base_node: ast.expr) -> bool:
        """
        Check if base class is BaseOperationModule.
        
        Args:
            base_node: AST base class node
        
        Returns:
            True if base is BaseOperationModule
        """
        if isinstance(base_node, ast.Name):
            return base_node.id == "BaseOperationModule"
        
        if isinstance(base_node, ast.Attribute):
            return base_node.attr == "BaseOperationModule"
        
        return False
    
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """
        Extract dependencies from file imports.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of imported class names
        """
        dependencies = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # Find all imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        # Look for Agent/Orchestrator classes
                        if "Agent" in alias.name or "Orchestrator" in alias.name:
                            dependencies.append(alias.name)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "Agent" in alias.name or "Orchestrator" in alias.name:
                            dependencies.append(alias.name)
        
        except Exception as e:
            logger.warning(f"Failed to extract dependencies from {file_path}: {e}")
        
        return dependencies
