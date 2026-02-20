"""
ImportReferenceAnalyzer — AST-based import reference discovery.

AC-PHASE44-S3: Find all import references to a given module path.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List


class ImportReferenceAnalyzer:
    """Finds import references to a given module inside a Python file."""

    def find_references(
        self, file_path: str, module_prefix: str
    ) -> List[Dict[str, Any]]:
        """Return all import statements that reference *module_prefix*."""
        src = Path(file_path).read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return []

        refs: List[Dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(module_prefix):
                        refs.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "lineno": node.lineno,
                        })
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith(module_prefix):
                    for alias in node.names:
                        refs.append({
                            "type": "from_import",
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
        src = Path(file_path).read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return []

        results: List[Dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    results.append({"type": "import", "module": alias.name, "lineno": node.lineno})
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                results.append({
                    "type": "from_import",
                    "module": node.module or "",
                    "names": [a.name for a in node.names],
                    "lineno": node.lineno,
                })
        return results

    def analyze_relative_imports(
        self, file_path: str
    ) -> List[Dict[str, Any]]:
        """Return all relative import statements in the file."""
        src = Path(file_path).read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return []

        results: List[Dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                results.append({
                    "type": "relative_import",
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

    def detect_circular_imports(self, codebase_root: str) -> List[Dict[str, Any]]:
        """Detect circular import chains (simple heuristic)."""
        circular: List[Dict[str, Any]] = []
        import_map: Dict[str, List[str]] = {}
        for py_file in Path(codebase_root).rglob("*.py"):
            try:
                refs = self.analyze_absolute_imports(str(py_file))
                module = str(py_file).replace("/", ".").replace(".py", "")
                import_map[module] = [r.get("module", "") for r in refs]
            except Exception:
                pass
        # Simple cycle detection
        for module, imports in import_map.items():
            for imp in imports:
                if imp in import_map and module in import_map.get(imp, []):
                    circular.append({"module_a": module, "module_b": imp})
        return circular
