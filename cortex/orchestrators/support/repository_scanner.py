"""
RepositoryScanner — Comprehensive repository scanning for cleanup candidates.

AC-PHASE44-S1: Inventory Python, test, config, and documentation files.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


_LEGACY_TEST_PATTERNS = ("test_", "_test.py")
_LEGACY_SCRIPT_PATTERNS = ("generate_", "run_", "migrate_", "fix_", "cleanup_", "phase_")


# ============================================================================
# Data Classes (WorkflowOrchestrator contract)
# ============================================================================


@dataclass
class ScanContext:
    """Context for repository scanning."""

    workspace_root: Path
    target_paths: List[Path] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_root": str(self.workspace_root),
            "target_paths": [str(p) for p in self.target_paths],
            "exclude_patterns": self.exclude_patterns,
        }


@dataclass
class ScanOutput:
    """Output of repository scan."""

    workspace_root: Path
    files: List[Dict[str, Any]] = field(default_factory=list)
    entities: Optional[Any] = None
    file_count: int = 0
    class_count: int = 0
    function_count: int = 0
    total_lines_of_code: int = 0
    timestamp: Optional[datetime] = None
    scan_duration: float = 0.0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_root": str(self.workspace_root),
            "files": self.files,
            "file_count": self.file_count,
            "class_count": self.class_count,
            "function_count": self.function_count,
            "total_lines_of_code": self.total_lines_of_code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "scan_duration": self.scan_duration,
            "errors": self.errors,
        }


class RepositoryScanner:
    """Scans a repository and categorises files for cleanup."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        max_depth: int = 10,
    ) -> None:
        """Initialize scanner with optional workspace root.

        Args:
            workspace_root: Root directory of workspace. Defaults to cwd.
            max_depth: Maximum directory depth for recursive scanning.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.max_depth = max_depth

    def scan(self, context: ScanContext) -> ScanOutput:
        """Execute a full repository scan using ScanContext.

        Args:
            context: Scan context with workspace root, targets, and excludes.

        Returns:
            ScanOutput with file inventory and metrics.
        """
        import ast as _ast
        import time

        start = time.time()
        root = context.workspace_root
        exclude_patterns = set(context.exclude_patterns)
        files: List[Dict[str, Any]] = []
        class_count = 0
        func_count = 0
        total_loc = 0
        errors: List[str] = []

        targets = context.target_paths or [root]

        def _is_excluded(path_str: str) -> bool:
            return any(pattern in path_str for pattern in exclude_patterns)

        def _within_depth(base: Path, candidate: Path) -> bool:
            try:
                relative = candidate.relative_to(base)
            except ValueError:
                return False
            return len(relative.parts) <= self.max_depth + 1

        for target in targets:
            target_path = Path(target) if not isinstance(target, Path) else target
            if not target_path.exists():
                continue
            for py_file in target_path.rglob("*.py"):
                path_text = str(py_file)
                if _is_excluded(path_text) or not _within_depth(target_path, py_file):
                    continue
                try:
                    src = py_file.read_text(errors="replace")
                    tree = _ast.parse(src)
                    loc = len(src.splitlines())
                    classes = 0
                    funcs = 0
                    for node in _ast.walk(tree):
                        if isinstance(node, _ast.ClassDef):
                            classes += 1
                        elif isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                            funcs += 1
                    files.append({"path": str(py_file), "lines": loc, "classes": classes, "functions": funcs})
                    class_count += classes
                    func_count += funcs
                    total_loc += loc
                except Exception as exc:
                    errors.append(f"{py_file}: {exc}")

        return ScanOutput(
            workspace_root=root,
            files=files,
            file_count=len(files),
            class_count=class_count,
            function_count=func_count,
            total_lines_of_code=total_loc,
            timestamp=datetime.now(),
            scan_duration=time.time() - start,
            errors=errors,
        )

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
        orphaned: List[str] = []

        for py_file in root_path.rglob("*.py"):
            path_text = str(py_file)
            if "_legacy_broken" in path_text or py_file.name.startswith("test_"):
                orphaned.append(path_text)

        return {
            "status": "success",
            "orphaned_tests": orphaned,
            "count": len(orphaned),
            "legacy_tests_count": len(orphaned),
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
            if md_file.name == "README.md":
                continue
            if not any(md_file.is_relative_to(c) for c in canonical):
                sprawl.append(md_file.name)
        return {
            "status": "success",
            "markdown_sprawl": sprawl,
            "candidates": sprawl,
            "count": len(sprawl),
        }

    def detect_duplicates(self, root: Any) -> Dict[str, Any]:
        """Detect duplicate files by content hash."""
        import ast

        if isinstance(root, list):
            files = [Path(path) for path in root]
        else:
            root_path = Path(root)
            files = list(root_path.rglob("*.py")) if root_path.is_dir() else [root_path]

        signatures: Dict[str, List[str]] = {}
        for py_file in files:
            try:
                tree = ast.parse(py_file.read_text())
                signature = "|".join(type(node).__name__ for node in ast.walk(tree))
                signatures.setdefault(signature, []).append(str(py_file))
            except Exception:
                continue

        duplicates = []
        for paths in signatures.values():
            if len(paths) > 1:
                duplicates.append(
                    {
                        "files": paths,
                        "similarity": 1.0,
                    }
                )
        return {
            "status": "success",
            "duplicates": duplicates,
            "count": len(duplicates),
            "duplicates_found": len(duplicates),
        }

    def map_import_references(self, root: Any) -> Dict[str, Any]:
        """Build a map of module → files that import it."""
        import ast

        if isinstance(root, list):
            files = [Path(path) for path in root]
        else:
            root_path = Path(root)
            files = list(root_path.rglob("*.py")) if root_path.is_dir() else [root_path]

        ref_map: Dict[str, List[str]] = {}
        for py_file in files:
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
        impact_scores = {
            module: len(sorted(set(paths)))
            for module, paths in ref_map.items()
        }
        return {
            "status": "success",
            "reference_map": ref_map,
            "import_map": ref_map,
            "impact_scores": impact_scores,
        }
