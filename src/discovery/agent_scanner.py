"""
Agent Scanner - Convention-Based Discovery

Discovers all agents using filesystem + AST analysis:
- Walks src/agents/ recursively
- Parses Python files with AST
- Finds classes ending in 'Agent'
- Validates common agent patterns (process method, etc.)
- Extracts metadata (docstring, capabilities, dependencies)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AgentScanner:
    """
    Convention-based agent discovery.
    
    Scans filesystem for agent classes without hardcoded lists.
    Uses AST for safe parsing without executing code.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize agent scanner.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.src_root = self.project_root / "src"
        
        # Scan paths (convention-based)
        self.scan_paths = [
            self.src_root / "agents",
            self.src_root / "cortex_agents"
        ]
        
        # Exclusion patterns
        self.exclude_files = {
            "base_agent.py",
            "__init__.py",
            "abstract_agent.py"
        }
    
    def discover(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all agents in project.
        
        Returns:
            Dict mapping agent name to metadata:
            {
                "ViewDiscoveryAgent": {
                    "path": Path(...),
                    "module_path": "src.agents.view_discovery_agent",
                    "class_name": "ViewDiscoveryAgent",
                    "docstring": "Auto-discovers element IDs...",
                    "methods": ["process", "discover_elements", "cache_results"],
                    "has_docstring": True,
                    "has_process_method": True
                }
            }
        """
        agents = {}
        
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
                
                # Scan file for agents
                found = self._scan_file(py_file)
                agents.update(found)
        
        logger.info(f"Discovered {len(agents)} agents")
        return agents
    
    def _scan_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        Scan single Python file for agent classes.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Dict of discovered agents in this file
        """
        agents = {}
        
        try:
            # Parse file with AST
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Find all classes
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                
                # Check if name ends with 'Agent' or 'AgentImpl' (concrete implementations)
                if not (node.name.endswith("Agent") or node.name.endswith("AgentImpl")):
                    continue
                
                # Skip abstract base classes (classes with ABC base or containing @abstractmethod)
                if self._is_abstract_class(node):
                    logger.debug(f"Skipping abstract class: {node.name}")
                    continue
                
                # Extract metadata (normalize name by removing 'Impl' suffix for display)
                metadata = self._extract_metadata(node, file_path)
                
                # Use normalized name without 'Impl' suffix as the key
                display_name = node.name.replace("AgentImpl", "Agent") if node.name.endswith("AgentImpl") else node.name
                agents[display_name] = metadata
        
        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")
        
        return agents
    
    def _is_abstract_class(self, class_node: ast.ClassDef) -> bool:
        """
        Check if class is abstract (has ABC base or @abstractmethod decorators).
        
        Args:
            class_node: AST ClassDef node
        
        Returns:
            True if class is abstract
        """
        # Check if inherits from ABC
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                if base.id in ("ABC", "ABCMeta"):
                    return True
        
        # Check for @abstractmethod decorators on any method
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "abstractmethod":
                            return True
                    elif isinstance(decorator, ast.Attribute):
                        if decorator.attr == "abstractmethod":
                            return True
        
        return False
    
    def _extract_metadata(
        self,
        class_node: ast.ClassDef,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Extract metadata from agent class AST node.
        
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
        
        # Check for common agent patterns
        has_process_method = "process" in methods
        has_execute_method = "execute" in methods
        
        # Build module path
        relative_path = file_path.relative_to(self.project_root)
        module_path = str(relative_path.with_suffix("")).replace("\\", ".").replace("/", ".")
        
        # Classify feature (production/admin/internal)
        classification = self._classify_agent(class_node.name, docstring)
        
        return {
            "path": file_path,
            "module_path": module_path,
            "class_name": class_node.name,
            "docstring": docstring,
            "methods": methods,
            "has_docstring": docstring is not None,
            "has_process_method": has_process_method,
            "has_execute_method": has_execute_method,
            "classification": classification
        }
    
    def _classify_agent(self, class_name: str, docstring: str = None) -> str:
        """
        Classify agent as production, admin, or internal.
        
        Args:
            class_name: Agent class name
            docstring: Class docstring (may be None)
        
        Returns:
            Classification: 'production', 'admin', or 'internal'
        """
        # Internal utility agents (not user-facing)
        internal_keywords = ["Ingestion", "Adapter", "Base", "Abstract", "Utility"]
        
        if any(keyword in class_name for keyword in internal_keywords):
            return "internal"
        
        # Check docstring for internal/admin indicators
        if docstring:
            docstring_lower = docstring.lower()
            if "internal" in docstring_lower or "utility" in docstring_lower:
                return "internal"
            if "admin-only" in docstring_lower:
                return "admin"
        
        # Default: production (user-facing agents)
        return "production"
