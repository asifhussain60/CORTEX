"""
RepositoryScanner — Comprehensive repository scanning for cleanup candidates.

AC-PHASE44-S1: Inventory Python, test, config, and documentation files.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


_LEGACY_TEST_PATTERNS = ("test_", "_test.py")
_LEGACY_SCRIPT_PATTERNS = ("generate_", "run_", "migrate_", "fix_", "cleanup_", "phase_")


class RepositoryScanner:
    """Scans a repository and categorises files for cleanup."""

    def scan_root_directory(self, root: str) -> Dict[str, Any]:
        """Scan the root directory and categorise all files found."""
        root_path = Path(root)
        python_files: List[str] = []
        test_files: List[str] = []
        config_files: List[str] = []
        doc_files: List[str] = []

        for item in root_path.iterdir():
            if not item.is_file():
                continue
            name = item.name
            if item.suffix == ".py":
                python_files.append(str(item))
                if any(p in name for p in _LEGACY_TEST_PATTERNS):
                    test_files.append(str(item))
            elif item.suffix in (".yaml", ".yml", ".toml", ".cfg", ".ini"):
                config_files.append(str(item))
            elif item.suffix == ".md":
                doc_files.append(str(item))

        return {
            "status": "success",
            "python_files": python_files,
            "test_files": test_files,
            "config_files": config_files,
            "doc_files": doc_files,
            "total_files": len(python_files) + len(config_files) + len(doc_files),
        }

    def scan_legacy_tests(self, root: str) -> Dict[str, Any]:
        """Find orphaned / legacy test files outside the canonical tests/ directory."""
        root_path = Path(root)
        tests_dir = root_path / "tests"
        orphaned: List[str] = []

        for py_file in root_path.rglob("*.py"):
            if py_file.is_relative_to(tests_dir):
                continue
            name = py_file.name
            if any(p in name for p in _LEGACY_TEST_PATTERNS):
                orphaned.append(str(py_file))

        return {
            "status": "success",
            "orphaned_tests": orphaned,
            "count": len(orphaned),
        }

    def scan_all(self, root: str) -> Dict[str, Any]:
        """Full repository scan — combines root directory and legacy test scanning."""
        root_scan = self.scan_root_directory(root)
        legacy = self.scan_legacy_tests(root)
        return {
            "status": "success",
            "root_scan": root_scan,
            "legacy_tests": legacy,
            "python_files": root_scan["python_files"],
            "orphaned_tests": legacy["orphaned_tests"],
            "legacy_tests_count": legacy["count"],
        }

    def scan_markdown_sprawl(self, root: str) -> Dict[str, Any]:
        """Find markdown files outside canonical documentation directories."""
        root_path = Path(root)
        canonical = {root_path / "docs", root_path / ".github"}
        sprawl: List[str] = []
        for md_file in root_path.rglob("*.md"):
            if not any(md_file.is_relative_to(c) for c in canonical):
                sprawl.append(str(md_file))
        return {"status": "success", "markdown_sprawl": sprawl, "count": len(sprawl)}

    def detect_duplicates(self, root: str) -> Dict[str, Any]:
        """Detect duplicate files by content hash."""
        import hashlib
        root_path = Path(root)
        hashes: Dict[str, List[str]] = {}
        for py_file in root_path.rglob("*.py"):
            try:
                digest = hashlib.md5(py_file.read_bytes()).hexdigest()
                hashes.setdefault(digest, []).append(str(py_file))
            except Exception:
                pass
        duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
        return {
            "status": "success",
            "duplicates": duplicates,
            "count": len(duplicates),
        }

    def map_import_references(self, root: str) -> Dict[str, Any]:
        """Build a map of module → files that import it."""
        import ast
        root_path = Path(root)
        ref_map: Dict[str, List[str]] = {}
        for py_file in root_path.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        ref_map.setdefault(node.module, []).append(str(py_file))
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            ref_map.setdefault(alias.name, []).append(str(py_file))
            except Exception:
                pass
        return {"status": "success", "reference_map": ref_map}
