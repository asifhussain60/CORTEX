"""Domain Brain Adapters

Real implementations replacing empty stubs (Phase 84-e, GAP-84-21).
ASTAdapter parses Python files with ast module; GitAdapter queries git log.

Author: CORTEX Framework
Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""

import ast
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.intelligence.domain_brain.domain_brain_models import Entity, EntityType

logger = logging.getLogger(__name__)


class ASTAdapter:
    """Abstract syntax tree adapter — parses Python source files via ast module.

    Replaces the empty stub that always returned [] from query_source().
    """

    def __init__(self) -> None:
        """Initialize AST adapter."""
        self.source_name = "AST"
        self.entities_cache: Dict[str, Entity] = {}
        self._loaded_file: Optional[Path] = None
        self._ast_data: List[Dict[str, Any]] = []

    def load_file(self, file_path: Any) -> None:
        """Parse a Python source file and populate the AST data cache.

        Args:
            file_path: Path to the Python file to parse.
        """
        p = Path(file_path)
        if not p.exists() or not p.suffix == ".py":
            return
        try:
            source = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(p))
            self._ast_data = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._ast_data.append({
                        "type": "function",
                        "name": node.name,
                        "lineno": node.lineno,
                        "file": str(p),
                    })
                elif isinstance(node, ast.AsyncFunctionDef):
                    self._ast_data.append({
                        "type": "function",
                        "name": node.name,
                        "lineno": node.lineno,
                        "file": str(p),
                        "async": True,
                    })
                elif isinstance(node, ast.ClassDef):
                    self._ast_data.append({
                        "type": "class",
                        "name": node.name,
                        "lineno": node.lineno,
                        "file": str(p),
                    })
            self._loaded_file = p
        except Exception as exc:
            logger.debug("ASTAdapter.load_file: failed to parse %s — %s", p, exc)

    def extract_entities(self) -> List[Entity]:
        """Extract entities from AST."""
        return list(self.entities_cache.values())

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query AST source with pattern matching.

        Supported patterns:
        - function:* — All functions
        - class:* — All classes
        - function:<name> — Specific function by name
        - class:<name> — Specific class by name

        Args:
            query: Pattern string to query against the parsed AST.

        Returns:
            List of matching AST node dicts.
        """
        if not query or ":" not in query:
            parts = ["", ""]
        else:
            parts = query.split(":", 1)
        query_type = parts[0].lower()
        pattern = parts[1] if len(parts) > 1 else ""
        if not query_type:
            return self._ast_data[:]
        results = []
        for item in self._ast_data:
            if item.get("type") != query_type:
                continue
            if pattern == "*" or pattern.lower() in item.get("name", "").lower():
                results.append(item)
        return results


class GitAdapter:
    """Git repository adapter — queries git log for real commit history.

    Replaces the empty stub that always returned [] from query_source().
    """

    def __init__(self, repo_path: Optional[Any] = None) -> None:
        """Initialize Git adapter.

        Args:
            repo_path: Path to the git repository root. Defaults to CWD.
        """
        self.source_name = "GIT"
        self.entities_cache: Dict[str, Entity] = {}
        self._repo_path: Path = Path(repo_path) if repo_path else Path.cwd()

    def extract_entities(self) -> List[Entity]:
        """Extract entities from Git history."""
        return list(self.entities_cache.values())

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query Git source using git log commands.

        Supported patterns:
        - recent:<n> — N most recent commits
        - history:<file> — Commit history for a specific file

        Args:
            query: Pattern string to query.

        Returns:
            List of commit dicts with hash, author, date, and message.
        """
        if not query or ":" not in query:
            parts = ["", ""]
        else:
            parts = query.split(":", 1)
        query_type = parts[0].lower()
        param = parts[1] if len(parts) > 1 else ""

        if query_type == "recent":
            try:
                count = int(param) if param.isdigit() else 10
            except ValueError:
                count = 10
            return self._git_log(n=count)
        elif query_type == "history" and param:
            return self._git_log(n=20, file_path=param)
        return self._git_log(n=10)

    def _git_log(self, n: int = 10, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Run git log and return structured commit list."""
        cmd = ["git", "-C", str(self._repo_path), "log",
               f"--max-count={n}", "--format=%H|%an|%ai|%s"]
        if file_path:
            cmd += ["--", file_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return []
            commits: List[Dict[str, Any]] = []
            for line in result.stdout.strip().splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })
            return commits
        except Exception as exc:
            logger.debug("GitAdapter._git_log: failed — %s", exc)
            return []


class CommentsAdapter:
    """Adapter for comments and documentation — extracts docstrings and TODO comments."""

    def __init__(self) -> None:
        """Initialize Comments adapter."""
        self.source_name = "COMMENTS"
        self.entities_cache: Dict[str, Entity] = {}
        self._loaded_file: Optional[Path] = None
        self._comments_data: List[Dict[str, Any]] = []

    def load_file(self, file_path: Any) -> None:
        """Parse a Python file and extract docstrings and TODO comments.

        Args:
            file_path: Path to the Python file to parse.
        """
        import ast as _ast
        import re as _re
        p = Path(file_path)
        if not p.exists() or not p.suffix == ".py":
            return
        try:
            source = p.read_text(encoding="utf-8", errors="replace")
            tree = _ast.parse(source, filename=str(p))
            self._comments_data = []
            for node in _ast.walk(tree):
                if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef, _ast.Module)):
                    ds = _ast.get_docstring(node)
                    if ds:
                        self._comments_data.append({
                            "type": "docstring",
                            "name": getattr(node, "name", "__module__"),
                            "content": ds,
                            "lineno": getattr(node, "lineno", 0),
                            "file": str(p),
                        })
            for lineno, line in enumerate(source.splitlines(), 1):
                if "TODO" in line or "FIXME" in line or "HACK" in line:
                    self._comments_data.append({
                        "type": "todo",
                        "name": f"line_{lineno}",
                        "content": line.strip(),
                        "lineno": lineno,
                        "file": str(p),
                    })
            self._loaded_file = p
        except Exception as exc:
            logger.debug("CommentsAdapter.load_file: failed — %s", exc)

    def extract_entities(self) -> List[Entity]:
        """Extract entities from comments and docstrings."""
        return list(self.entities_cache.values())

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query comments and documentation.

        Supported patterns:
        - docstring:* — All docstrings
        - docstring:<name> — Specific docstring by name
        - todo:* — All TODO/FIXME comments

        Args:
            query: Pattern string to query.

        Returns:
            List of matching comment/docstring dicts.
        """
        if not query or ":" not in query:
            return list(self._comments_data)
        parts = query.split(":", 1)
        query_type, pattern = parts[0].lower(), parts[1]
        return [
            item for item in self._comments_data
            if item.get("type") == query_type
            and (pattern == "*" or pattern.lower() in item.get("name", "").lower())
        ]


class RelationshipsAdapter:
    """Adapter for relationships between entities — scans import graphs."""

    def __init__(self) -> None:
        """Initialize Relationships adapter."""
        self.source_name = "RELATIONSHIPS"
        self.entities_cache: Dict[str, Entity] = {}
        self._relationships: List[Dict[str, Any]] = []

    def load_directory(self, dir_path: Any) -> None:
        """Scan a directory for Python import relationships.

        Args:
            dir_path: Path to the directory to scan.
        """
        import ast as _ast
        p = Path(dir_path)
        if not p.exists():
            return
        for py_file in p.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                tree = _ast.parse(source)
                for node in _ast.walk(tree):
                    if isinstance(node, _ast.Import):
                        for alias in node.names:
                            self._relationships.append({
                                "source": str(py_file.stem),
                                "target": alias.name,
                                "type": "import",
                                "file": str(py_file),
                            })
                    elif isinstance(node, _ast.ImportFrom) and node.module:
                        self._relationships.append({
                            "source": str(py_file.stem),
                            "target": node.module,
                            "type": "from_import",
                            "file": str(py_file),
                        })
            except Exception:
                pass

    def extract_entities(self) -> List[Entity]:
        """Extract service and relationship entities."""
        return list(self.entities_cache.values())

    def query_source(self, query: str) -> List[Dict[str, Any]]:
        """Query service relationships from the import graph.

        Supported patterns:
        - service:* — All discovered service relationships
        - depends:<module> — Imports of a specific module

        Args:
            query: Pattern string to query.

        Returns:
            List of relationship dicts.
        """
        if not query or ":" not in query:
            return list(self._relationships)
        parts = query.split(":", 1)
        query_type, pattern = parts[0].lower(), parts[1]
        if query_type in ("service", "depends"):
            if pattern == "*":
                return list(self._relationships)
            return [r for r in self._relationships if pattern.lower() in r.get("target", "").lower()]
        return list(self._relationships)


__all__ = ["ASTAdapter", "GitAdapter", "CommentsAdapter", "RelationshipsAdapter"]
