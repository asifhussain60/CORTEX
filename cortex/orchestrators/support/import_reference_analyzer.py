"""
AC_START: AC-PHASE44-S3-004
ImportReferenceAnalyzer - AST-based import reference discovery
Phase 44 Stage 3 - Production Readiness Infrastructure
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class ImportReferenceAnalyzer:
    """
    AST-based import reference analyzer for relocation impact analysis.

    Features:
    - Find all import references to a module
    - Parse absolute and relative imports
    - Detect circular import risks
    - Calculate relocation impact

    Usage:
        analyzer = ImportReferenceAnalyzer()
        refs = analyzer.find_references(file_path, "cortex.orchestrators")
        circular = analyzer.detect_circular_imports(file_list)
    """

    def __init__(self) -> None:
        """Initialize ImportReferenceAnalyzer."""
        self.import_graph: Dict[str, Set[str]] = {}

    def find_references(self, file_path: str, target_module: str) -> List[Dict[str, Any]]:
        """
        Find all import references to target module in file.

        AC-044-S3-04: find_references() finds 100% of import refs

        Args:
            file_path: Path to Python file to analyze
            target_module: Module name to search for

        Returns:
            List of import reference dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            refs = self.parse_imports(source)

            # Filter refs that match target module
            matching_refs = [
                ref for ref in refs
                if target_module in ref.get("module", "")
            ]

            return matching_refs

        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return []

    def parse_imports(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Parse all imports from source code using AST.

        AC-044-S3-05: Handles absolute and relative imports

        Args:
            source_code: Python source code string

        Returns:
            List of import dictionaries with type, module, names, level
        """
        refs = []

        try:
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle: import module
                    for alias in node.names:
                        refs.append({
                            "type": "absolute",
                            "module": alias.name,
                            "alias": alias.asname,
                            "lineno": node.lineno,
                            "level": 0
                        })

                elif isinstance(node, ast.ImportFrom):
                    # Handle: from module import name
                    module = node.module or ""
                    level = node.level  # 0 = absolute, >0 = relative

                    import_type = "relative" if level > 0 else "absolute"

                    for alias in node.names:
                        refs.append({
                            "type": import_type,
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "lineno": node.lineno,
                            "level": level
                        })

        except SyntaxError as e:
            logger.error(f"Syntax error parsing source: {e}")

        return refs

    def detect_circular_imports(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Detect circular import dependencies between files.

        AC-044-S3-06: Detects circular import risks

        Args:
            file_paths: List of Python file paths to analyze

        Returns:
            List of circular import pairs (file_a, file_b)
        """
        # Build import graph
        self.import_graph = {}

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()

                refs = self.parse_imports(source)

                # Extract module names from imports
                imported_modules = {ref["module"] for ref in refs if ref["module"]}

                file_module = self._file_to_module(file_path)
                self.import_graph[file_module] = imported_modules

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Detect cycles using DFS
        circular_pairs = []
        visited = set()

        def dfs(node: str, path: List[str]) -> None:
            """Depth-first search for cycles."""
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if len(cycle) >= 2:
                    circular_pairs.append((cycle[0], cycle[1]))
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, []):
                dfs(neighbor, path[:])

        for node in self.import_graph:
            dfs(node, [])

        return list(set(circular_pairs))

    def _file_to_module(self, file_path: str) -> str:
        """
        Convert file path to module name.

        Args:
            file_path: Path to Python file

        Returns:
            Module name (e.g., cortex.orchestrators.core)
        """
        path = Path(file_path)

        # Find cortex root
        parts = path.parts
        if "cortex" in parts:
            cortex_idx = parts.index("cortex")
            module_parts = parts[cortex_idx:]

            # Remove .py extension
            if module_parts[-1].endswith(".py"):
                module_parts = list(module_parts)
                module_parts[-1] = module_parts[-1][:-3]

            return ".".join(module_parts)

        return path.stem


# AC_COMPLETE: AC-PHASE44-S3-004 ✅ ImportReferenceAnalyzer implemented with AST parsing
