"""
ImportReferenceAnalyzer — AST-based import reference discovery.

AC-PHASE44-S3: Find all import references to a given module path.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union


class ImportReferenceAnalyzer:
    """Finds import references to a given module inside a Python file."""

    def _load_source(self, source_or_path: str) -> str:
        """Return source text from a path or treat the input as raw Python code."""
        path = Path(source_or_path)
        if path.exists():
            return path.read_text()
        return source_or_path

    def _parse_tree(self, source_or_path: str) -> ast.AST:
        """Parse Python source from raw code or a file path."""
        return ast.parse(self._load_source(source_or_path))

    def _iter_import_nodes(self, tree: ast.AST) -> Iterable[Tuple[Union[ast.Import, ast.ImportFrom], int]]:
        """Yield import nodes in source order."""
        for index, node in enumerate(getattr(tree, "body", [])):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                yield node, index

    def find_references(
        self, file_path: str, module_prefix: str
    ) -> List[Dict[str, Any]]:
        """Return all import statements that reference *module_prefix*."""
        try:
            tree = self._parse_tree(file_path)
        except SyntaxError:
            return []

        refs: List[Dict[str, Any]] = []
        for node, _ in self._iter_import_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(module_prefix):
                        refs.append({
                            "type": "absolute",
                            "module": alias.name,
                            "alias": alias.asname,
                            "lineno": node.lineno,
                        })
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith(module_prefix):
                    for alias in node.names:
                        refs.append({
                            "type": "absolute",
                            "module": mod,
                            "name": alias.name,
                            "alias": alias.asname,
                            "lineno": node.lineno,
                        })
        return refs

    def analyze_absolute_imports(
        self, file_path: str
    ) -> List[Dict[str, Any]]:
        """Return all absolute import statements in the file."""
        try:
            tree = self._parse_tree(file_path)
        except SyntaxError:
            return []

        results: List[Dict[str, Any]] = []
        for node, _ in self._iter_import_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    results.append({"type": "absolute", "module": alias.name, "lineno": node.lineno})
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                results.append({
                    "type": "absolute",
                    "module": node.module or "",
                    "names": [a.name for a in node.names],
                    "lineno": node.lineno,
                })
        return results

    def analyze_relative_imports(
        self, file_path: str
    ) -> List[Dict[str, Any]]:
        """Return all relative import statements in the file."""
        try:
            tree = self._parse_tree(file_path)
        except SyntaxError:
            return []

        results: List[Dict[str, Any]] = []
        for node, _ in self._iter_import_nodes(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                results.append({
                    "type": "relative",
                    "level": node.level,
                    "module": node.module or "",
                    "names": [a.name for a in node.names],
                    "lineno": node.lineno,
                })
        return results

    def scan_directory(
        self, directory: str, module_prefix: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all Python files under *directory* for references to *module_prefix*."""
        results: Dict[str, List[Dict[str, Any]]] = {}
        for py_file in Path(directory).rglob("*.py"):
            refs = self.find_references(str(py_file), module_prefix)
            if refs:
                results[str(py_file)] = refs
        return results

    def parse_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse all imports from a file — alias for analyze_absolute_imports + relative."""
        return self.analyze_absolute_imports(file_path) + self.analyze_relative_imports(file_path)

    def detect_circular_imports(self, codebase_root: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """Detect circular import chains (simple heuristic)."""
        circular: List[Dict[str, Any]] = []
        import_map: Dict[str, List[str]] = {}

        if isinstance(codebase_root, list):
            files = [Path(path) for path in codebase_root]
        else:
            root = Path(codebase_root)
            files = list(root.rglob("*.py")) if root.is_dir() else [root]

        for py_file in files:
            try:
                refs = self.analyze_absolute_imports(str(py_file))
                module = py_file.stem
                import_map[module] = [r.get("module", "").split(".")[-1] for r in refs]
            except Exception:
                pass
        # Simple cycle detection
        for module, imports in import_map.items():
            for imp in imports:
                if imp in import_map and module in import_map.get(imp, []):
                    circular.append({"module_a": module, "module_b": imp})
        return circular
