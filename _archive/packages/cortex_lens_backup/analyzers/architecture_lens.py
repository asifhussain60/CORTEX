"""
Phase 66 Stage 1: Architecture Lens Analyzer

Detects architectural patterns and layering violations through
import graph analysis and naming conventions.

AC_START: AC-PHASE66-S1-003
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import logging

from cortex_lens.models.architecture_report import ArchitectureReport

logger = logging.getLogger(__name__)


class ArchitectureLens:
    """
    Architectural pattern analyzer for Python codebases.
    
    Analyzes import relationships to detect:
    - Architectural patterns (MVC, Repository, Service layers)
    - Layering violations (upward dependencies)
    - Circular dependencies
    - Component hierarchy
    
    Example:
        >>> lens = ArchitectureLens(Path("/repo"))
        >>> report = lens.analyze()
        >>> print(f"Found {len(report.violations)} violations")
        Found 2 violations
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize Architecture Lens analyzer.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.files: List[Path] = []
        self.imports_by_file: Dict[Path, List[str]] = {}
        self.dependency_graph: Dict[Path, List[Path]] = defaultdict(list)
        
    def analyze(self) -> ArchitectureReport:
        """
        Perform complete architectural analysis.
        
        Returns:
            ArchitectureReport with patterns, violations, hierarchy
        """
        logger.info(f"Starting architectural analysis of {self.repo_path}")
        
        # Step 1: Scan Python files
        self._scan_python_files()
        
        # Step 2: Build dependency graph from imports
        self._build_dependency_graph()
        
        # Step 3: Detect architectural patterns
        patterns = self._detect_patterns()
        
        # Step 4: Detect violations
        violations = self._detect_violations()
        
        # Step 5: Build component hierarchy
        hierarchy = self._build_component_hierarchy()
        
        report = ArchitectureReport(
            repo_path=self.repo_path,
            patterns_detected=patterns,
            violations=violations,
            component_hierarchy=hierarchy,
            dependency_graph={str(k): [str(v) for v in vals] for k, vals in self.dependency_graph.items()},
            total_files_analyzed=len(self.files),
            analysis_timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Analysis complete: {len(patterns)} patterns, {len(violations)} violations")
        return report
    
    def _scan_python_files(self) -> None:
        """Scan repository for Python files."""
        self.files = []
        
        for py_file in self.repo_path.rglob("*.py"):
            # Skip __pycache__, .venv, node_modules
            if any(skip in py_file.parts for skip in ["__pycache__", ".venv", "node_modules", ".git"]):
                continue
            self.files.append(py_file)
        
        logger.debug(f"Scanned {len(self.files)} Python files")
    
    def _parse_imports(self, file_path: Path) -> List[str]:
        """
        Extract import statements from Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of imported module names
        """
        imports = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
        
        return imports
    
    def _build_dependency_graph(self) -> Dict[Path, List[Path]]:
        """
        Build directed graph of file dependencies from imports.
        
        Returns:
            Dictionary mapping each file to its dependencies
        """
        self.dependency_graph.clear()
        self.imports_by_file.clear()
        
        # First pass: extract all imports
        for file_path in self.files:
            imports = self._parse_imports(file_path)
            self.imports_by_file[file_path] = imports
        
        # Second pass: resolve imports to files
        # Convert files list to set for O(1) lookup
        files_set = set(self.files)
        
        for file_path, imports in self.imports_by_file.items():
            for imp in imports:
                # Convert import to potential file paths
                potential_files = self._resolve_import_to_files(imp)
                for dep_file in potential_files:
                    if dep_file in files_set and dep_file != file_path:
                        self.dependency_graph[file_path].append(dep_file)
        
        return self.dependency_graph
    
    def _resolve_import_to_files(self, import_name: str) -> List[Path]:
        """
        Resolve import statement to possible file paths.
        
        Args:
            import_name: Module import name (e.g., 'services.user_service')
            
        Returns:
            List of possible file paths
        """
        # Convert dots to path separators
        parts = import_name.split(".")
        possible_files = []
        
        # Try exact match
        file_path = self.repo_path / "/".join(parts) / "__init__.py"
        if file_path.exists():
            possible_files.append(file_path)
        
        # Try as module file
        file_path = self.repo_path / f"{'/'.join(parts)}.py"
        if file_path.exists():
            possible_files.append(file_path)
        
        # Try subdirectory search
        for py_file in self.files:
            if any(part in py_file.parts for part in parts):
                possible_files.append(py_file)
        
        return list(set(possible_files))
    
    def _detect_patterns(self) -> List[Dict[str, Any]]:
        """
        Detect architectural patterns from file structure and naming.
        
        Returns:
            List of detected patterns with metadata
        """
        patterns = []
        
        # Detect MVC pattern
        has_controllers = any("controller" in str(f).lower() for f in self.files)
        has_services = any("service" in str(f).lower() for f in self.files)
        has_repos = any("repositor" in str(f).lower() for f in self.files)
        
        if has_controllers and (has_services or has_repos):
            patterns.append({
                "pattern_type": "MVC",
                "confidence": 0.9 if (has_controllers and has_services and has_repos) else 0.7,
                "layers": {
                    "controller": has_controllers,
                    "service": has_services,
                    "repository": has_repos,
                },
                "description": "Model-View-Controller pattern detected"
            })
        
        # Detect Repository pattern
        if has_repos:
            repo_files = [f for f in self.files if "repositor" in str(f).lower()]
            patterns.append({
                "pattern_type": "Repository",
                "confidence": 0.85,
                "files": [str(f) for f in repo_files[:5]],  # Sample
                "description": "Repository pattern for data access abstraction"
            })
        
        # Detect Orchestrator pattern (common in CORTEX)
        has_orchestrators = any("orchestrator" in str(f).lower() for f in self.files)
        if has_orchestrators:
            orch_files = [f for f in self.files if "orchestrator" in str(f).lower()]
            patterns.append({
                "pattern_type": "Orchestrator",
                "confidence": 0.9,
                "files": [str(f) for f in orch_files[:5]],
                "description": "Orchestrator pattern for workflow coordination"
            })
        
        return patterns
    
    def _detect_violations(self) -> List[Dict[str, Any]]:
        """
        Detect architectural violations.
        
        Returns:
            List of violations with severity and details
        """
        violations = []
        
        # Detect layering violations
        layering_violations = self._detect_upward_dependencies()
        violations.extend(layering_violations)
        
        # Detect circular dependencies
        circular_violations = self._detect_cycles()
        violations.extend(circular_violations)
        
        return violations
    
    def _detect_upward_dependencies(self) -> List[Dict[str, Any]]:
        """
        Detect upward dependencies (layering violations).
        
        Controller → Repository direct is violation (should go through Service)
        
        Returns:
            List of layering violation dictionaries
        """
        violations = []
        
        for file_path, deps in self.dependency_graph.items():
            file_str = str(file_path).lower()
            
            # Check if controller directly depends on repository
            if "controller" in file_str:
                for dep in deps:
                    dep_str = str(dep).lower()
                    if "repositor" in dep_str and "service" not in file_str:
                        # Check if there's a service layer being bypassed
                        has_service_layer = any("service" in str(f).lower() for f in self.files)
                        
                        if has_service_layer:
                            violations.append({
                                "violation_type": "layering_bypass",
                                "severity": "medium",
                                "file": str(file_path),
                                "target": str(dep),
                                "description": "Controller directly accessing Repository (bypassing Service layer)",
                                "suggestion": "Route data access through Service layer"
                            })
        
        return violations
    
    def _detect_cycles(self) -> List[Dict[str, Any]]:
        """
        Detect circular dependencies using DFS.
        
        Returns:
            List of circular dependency violations
        """
        violations = []
        visited: Set[Path] = set()
        rec_stack: Set[Path] = set()
        
        def dfs(node: Path, path: List[Path]) -> Optional[List[Path]]:
            """DFS helper to find cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path[:])
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        # Find all cycles
        for file_path in self.files:
            if file_path not in visited:
                cycle = dfs(file_path, [])
                if cycle and len(cycle) > 1:
                    violations.append({
                        "violation_type": "circular_dependency",
                        "severity": "high",
                        "cycle_path": [str(f) for f in cycle],
                        "description": f"Circular dependency detected ({len(cycle)} files in cycle)",
                        "suggestion": "Refactor to break circular dependency (extract interface, introduce mediator)"
                    })
                    # Only report first cycle for each component
                    break
        
        return violations
    
    def _build_component_hierarchy(self) -> Dict[str, Any]:
        """
        Build hierarchical structure of components.
        
        Returns:
            Dictionary representing component layers
        """
        hierarchy = {
            "presentation": [],
            "business": [],
            "data": [],
            "other": []
        }
        
        for file_path in self.files:
            file_str = str(file_path).lower()
            
            if "controller" in file_str or "view" in file_str:
                hierarchy["presentation"].append(str(file_path))
            elif "service" in file_str or "orchestrator" in file_str:
                hierarchy["business"].append(str(file_path))
            elif "repositor" in file_str or "dao" in file_str or "database" in file_str:
                hierarchy["data"].append(str(file_path))
            else:
                hierarchy["other"].append(str(file_path))
        
        # Limit samples for large codebases
        for layer in hierarchy:
            if len(hierarchy[layer]) > 10:
                hierarchy[layer] = hierarchy[layer][:10] + [f"... and {len(hierarchy[layer]) - 10} more"]
        
        return hierarchy


# AC_COMPLETE: AC-PHASE66-S1-003 ✅ ArchitectureLens analyzer complete
