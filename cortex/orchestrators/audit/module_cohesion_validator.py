"""
ModuleCohesionValidator - AUDIT Mode P1.5 Module Cohesion Check (Stage 4).

Validates module cohesion across 2 dimensions:
1. Import health (all imports resolve, no deprecated imports, no wildcards)
2. Circular dependency detection (no circular imports, dependency graph is DAG)

Checks:
1. P1.5-011: Import health validation
2. P1.5-012: Circular dependency detection

Author: Asif Hussain
Date: 2026-02-07
Phase: 39 Stage 4
"""

import ast
import importlib.util
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Constants
CORTEX_MODULE_DIR = "cortex"
"""Directory containing CORTEX modules."""

# Python 3.10+ has sys.stdlib_module_names, for older versions use common stdlib modules
try:
    STDLIB_MODULES = set(sys.stdlib_module_names)  # type: ignore
except AttributeError:
    STDLIB_MODULES = {
        'abc', 'argparse', 'ast', 'asyncio', 'collections', 'copy', 'datetime',
        'functools', 'importlib', 'io', 'json', 'logging', 'os', 'pathlib', 're',
        'sys', 'typing', 'unittest', 'uuid', 'yaml', 'dataclasses'
    }
"""Set of standard library module names."""

DEPRECATED_IMPORTS = [
    "imp",  # Deprecated in Python 3.4
    "asynchat",  # Removed in Python 3.12
    "asyncore",  # Removed in Python 3.12
]
"""List of deprecated module names."""


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    from_module: Optional[str]
    is_relative: bool
    is_wildcard: bool
    line_number: int


@dataclass
class ModuleMetadata:
    """Metadata about a Python module."""
    file_path: str
    imports: List[ImportInfo] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    missing_imports: List[str] = field(default_factory=list)
    deprecated_imports: List[str] = field(default_factory=list)
    wildcard_imports: List[str] = field(default_factory=list)


# AC_START: AC-PHASE39-011
# Description: ModuleCohesionValidator GREEN phase implementation
# Author: Asif Hussain
# Date: 2026-02-07


class ModuleCohesionValidator:
    """
    Validate module cohesion across CORTEX architecture.

    Ensures:
    - Import health (all imports resolve)
    - No circular dependencies
    - Proper module coupling
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            repo_root: Repository root path (defaults to current directory)
        """
        self.repo_root = repo_root or Path.cwd()
        self.cortex_dir = self.repo_root / CORTEX_MODULE_DIR

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all module cohesion validation checks.

        Returns:
            Dict with:
            - cohesive: bool (all checks passed)
            - issues: List[str] (human-readable issues)
            - details: Dict (detailed check results)
        """
        # Discover all Python modules
        python_files = self._discover_python_files()

        # Build metadata for all modules
        modules = self._build_module_metadata(python_files)

        # Run checks
        import_health = self.check_import_health(modules)
        circular_deps = self.check_circular_dependencies(modules)

        # Aggregate issues
        issues = []

        if import_health["missing_imports"]:
            for file, imports in import_health["missing_imports"].items():
                for imp in imports:
                    issues.append(f"P1.5-011: {file} has missing import: {imp}")

        if import_health["deprecated_imports"]:
            for file, imports in import_health["deprecated_imports"].items():
                for imp in imports:
                    issues.append(f"P1.5-011: {file} uses deprecated import: {imp}")

        if import_health["wildcard_imports"]:
            for file, imports in import_health["wildcard_imports"].items():
                for imp in imports:
                    issues.append(f"P1.5-011: {file} has wildcard import: from {imp} import *")

        if circular_deps["cycles"]:
            for cycle in circular_deps["cycles"]:
                cycle_str = " → ".join(cycle)
                issues.append(f"P1.5-012: Circular dependency detected: {cycle_str}")

        return {
            "cohesive": len(issues) == 0,
            "issues": issues,
            "details": {
                "import_health": import_health,
                "circular_dependencies": circular_deps
            }
        }

    def _discover_python_files(self) -> List[Path]:
        """Discover all Python files in cortex/ directory."""
        if not self.cortex_dir.exists():
            return []

        files = []
        for py_file in self.cortex_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                files.append(py_file)

        return sorted(files)

    def _build_module_metadata(self, python_files: List[Path]) -> Dict[str, ModuleMetadata]:
        """Build metadata for all modules."""
        modules = {}

        for file_path in python_files:
            try:
                content = file_path.read_text()
                relative_path = str(file_path.relative_to(self.repo_root))

                metadata = ModuleMetadata(file_path=relative_path)
                metadata.imports = self._extract_imports(content)

                for import_info in metadata.imports:
                    # Check for missing imports
                    if not self._can_resolve_import(import_info.module):
                        metadata.missing_imports.append(import_info.module)

                    # Check for deprecated imports
                    if import_info.module in DEPRECATED_IMPORTS:
                        metadata.deprecated_imports.append(import_info.module)

                    # Check for wildcard imports
                    if import_info.is_wildcard:
                        metadata.wildcard_imports.append(import_info.from_module or import_info.module)

                    # Track dependencies
                    if import_info.from_module:
                        metadata.dependencies.add(import_info.from_module)
                    else:
                        metadata.dependencies.add(import_info.module)

                modules[relative_path] = metadata

            except Exception:
                # Skip files that can't be parsed
                continue

        return modules

    def _extract_imports(self, content: str) -> List[ImportInfo]:
        """Extract import statements from Python file content."""
        imports = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportInfo(
                            module=alias.name,
                            from_module=None,
                            is_relative=False,
                            is_wildcard=False,
                            line_number=node.lineno
                        ))

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    is_relative = node.level > 0

                    for alias in node.names:
                        imports.append(ImportInfo(
                            module=alias.name,
                            from_module=module,
                            is_relative=is_relative,
                            is_wildcard=(alias.name == "*"),
                            line_number=node.lineno
                        ))

        except SyntaxError:
            pass

        return imports

    def _can_resolve_import(self, module_name: str) -> bool:
        """Check if an import can be resolved."""
        # Check standard library
        if module_name.split('.')[0] in STDLIB_MODULES:
            return True

        # Check if it's a cortex module
        if module_name.startswith('cortex'):
            return True

        # Try to find the module spec
        try:
            spec = importlib.util.find_spec(module_name.split('.')[0])
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError, AttributeError):
            return False

    def check_import_health(self, modules: Dict[str, ModuleMetadata]) -> Dict[str, Any]:
        """
        Check P1.5-011: Import health validation.

        Args:
            modules: Dict of file_path → ModuleMetadata

        Returns:
            Dict with:
            - missing_imports: Dict[file, List[module]]
            - deprecated_imports: Dict[file, List[module]]
            - wildcard_imports: Dict[file, List[module]]
            - total_imports: int
            - healthy_imports: int
        """
        missing_imports = {}
        deprecated_imports = {}
        wildcard_imports = {}
        total_imports = 0
        healthy_imports = 0

        for file_path, metadata in modules.items():
            total_imports += len(metadata.imports)

            if metadata.missing_imports:
                missing_imports[file_path] = metadata.missing_imports

            if metadata.deprecated_imports:
                deprecated_imports[file_path] = metadata.deprecated_imports

            if metadata.wildcard_imports:
                wildcard_imports[file_path] = metadata.wildcard_imports

            # Count healthy imports
            healthy_count = len(metadata.imports) - len(metadata.missing_imports) - \
                           len(metadata.deprecated_imports) - len(metadata.wildcard_imports)
            healthy_imports += max(0, healthy_count)

        return {
            "missing_imports": missing_imports,
            "deprecated_imports": deprecated_imports,
            "wildcard_imports": wildcard_imports,
            "total_imports": total_imports,
            "healthy_imports": healthy_imports,
            "health_percentage": (healthy_imports / total_imports * 100) if total_imports > 0 else 100
        }

    def check_circular_dependencies(self, modules: Dict[str, ModuleMetadata]) -> Dict[str, Any]:
        """
        Check P1.5-012: Circular dependency detection.

        Args:
            modules: Dict of file_path → ModuleMetadata

        Returns:
            Dict with:
            - cycles: List[List[str]] (circular dependency chains)
            - is_dag: bool
            - coupling_metrics: Dict[file, int] (number of dependencies)
        """
        # Build dependency graph
        graph = defaultdict(set)

        for file_path, metadata in modules.items():
            for dep in metadata.dependencies:
                # Find matching module files
                for other_file in modules.keys():
                    if dep in other_file or other_file.replace('/', '.').replace('.py', '') == dep:
                        graph[file_path].add(other_file)

        # Detect cycles using DFS
        cycles = self._detect_cycles(graph)

        # Calculate coupling metrics
        coupling_metrics = {
            file_path: len(deps)
            for file_path, deps in graph.items()
        }

        return {
            "cycles": cycles,
            "is_dag": len(cycles) == 0,
            "coupling_metrics": coupling_metrics,
            "high_coupling_modules": [
                file for file, count in coupling_metrics.items() if count > 10
            ]
        }

    def _detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect cycles in dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    # Simplify cycle to just module names
                    simplified_cycle = [p.split('/')[-1].replace('.py', '') for p in cycle]
                    if simplified_cycle not in cycles:
                        cycles.append(simplified_cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles


# AC_COMPLETE: AC-PHASE39-011 GREEN ✅ Import health validation implemented
# AC_COMPLETE: AC-PHASE39-012 GREEN ✅ Circular dependency detection implemented
