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

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """Initialize scanner with optional workspace root.

        Args:
            workspace_root: Root directory of workspace. Defaults to cwd.
        """
        self.workspace_root = workspace_root or Path.cwd()

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
        exclude = set(context.exclude_patterns)
        files: List[Dict[str, Any]] = []
        class_count = 0
        func_count = 0
        total_loc = 0
        errors: List[str] = []

        targets = context.target_paths or [root]
        for target in targets:
            target_path = Path(target) if not isinstance(target, Path) else target
            if not target_path.exists():
                continue
            for py_file in target_path.rglob("*.py"):
                if any(pat in str(py_file) for pat in exclude):
                    continue
                try:
                    src = py_file.read_text(errors="replace")
                    tree = _ast.parse(src)
                    loc = len(src.splitlines())
                    classes = sum(1 for n in _ast.walk(tree) if isinstance(n, _ast.ClassDef))
                    funcs = sum(1 for n in _ast.walk(tree) if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef)))
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
