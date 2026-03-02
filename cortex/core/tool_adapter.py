"""
Tool Adapter Pattern for Environment-Agnostic Tool Access.

Provides unified interface for accessing tools (analysis, search, git) across
different environments (MCP Server, VS Code Copilot, Development).

Authority: Phase 33 - Architecture Alignment & Mandatory Governance Enforcement
CORE-008: TDD-first architecture
CORE-011: Type hints mandatory
CORE-012: Google-style docstrings
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Base exception for tool adapter errors."""

    pass


class ToolUnavailableError(ToolError):
    """Raised when requested tool is unavailable in current environment."""

    pass


@dataclass
class AnalysisResult:
    """Result from code analysis tool."""

    target_path: str
    issues: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    success: bool
    error: Optional[str] = None


@dataclass
class SearchResult:
    """Result from workspace search tool."""

    query: str
    matches: List[Dict[str, Any]]
    total_count: int
    success: bool
    error: Optional[str] = None


@dataclass
class DuplicateResult:
    """Result from duplicate detection tool."""

    scope: str
    duplicates: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None


@dataclass
class GitHistoryResult:
    """Result from git history tool."""

    lookback_hours: int
    commits: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None


class IToolAdapter(ABC):
    """
    Abstract interface for tool adapters.

    Provides unified access to CORTEX tools regardless of execution environment.
    """

    @abstractmethod
    def analyze_code(self, target_path: str) -> AnalysisResult:
        """
        Analyze code in workspace.

        Args:
            target_path: Path to analyze (file, directory, or ".")

        Returns:
            AnalysisResult with findings

        Raises:
            ToolUnavailableError: If analysis tool not available
        """
        pass

    @abstractmethod
    def search_workspace(self, query: str) -> SearchResult:
        """
        Search workspace for pattern.

        Args:
            query: Search query or regex pattern

        Returns:
            SearchResult with matches

        Raises:
            ToolUnavailableError: If search tool not available
        """
        pass

    @abstractmethod
    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """
        Detect code duplicates in scope.

        Args:
            scope: Path scope for duplication detection

        Returns:
            DuplicateResult with duplicate groups

        Raises:
            ToolUnavailableError: If duplication tool not available
        """
        pass

    @abstractmethod
    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """
        Get git commit history.

        Args:
            lookback_hours: How many hours back to retrieve

        Returns:
            GitHistoryResult with commits

        Raises:
            ToolUnavailableError: If git tool not available
        """
        pass

    @abstractmethod
    def is_available(self, tool_name: str) -> bool:
        """
        Check if specific tool is available.

        Args:
            tool_name: Tool identifier (analyze, search, duplicates, git_history)

        Returns:
            True if tool available, False otherwise
        """
        pass

    @abstractmethod
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get information about execution environment.

        Returns:
            Dict with environment details
        """
        pass


class MCPToolAdapter(IToolAdapter):
    """
    Production tool adapter using MCP server tools.

    Routes to LENS analyzers, subprocess git, AST-based duplicate detection.
    In MCP server context, these tools are invoked directly (not via RPC).
    """

    def __init__(self) -> None:
        """Initialize MCP tool adapter."""
        self.environment = "MCP_SERVER"
        logger.debug("Initialized MCPToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code using LENS analyzers directly."""
        try:
            from pathlib import Path
            from cortex.lens.lens_orchestrator import LENSOrchestrator
            target = Path(target_path)
            orchestrator = LENSOrchestrator(repo_path=str(target.parent if target.is_file() else target))

            if target.is_file():
                result = orchestrator.analyze_file(target)
                issues = result.get("issues", []) if isinstance(result, dict) else []
                metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
            elif target.is_dir():
                batch = orchestrator.analyze_batch(list(target.rglob("*.py"))[:50])
                issues = []
                metrics = {"files_analyzed": len(batch)}
                for file_result in batch.values():
                    if isinstance(file_result, dict):
                        issues.extend(file_result.get("issues", []))
            else:
                issues = []
                metrics = {"error": f"Path not found: {target_path}"}

            return AnalysisResult(
                target_path=target_path, issues=issues, metrics=metrics, success=True,
            )
        except ImportError:
            logger.warning("[MCP] LENS orchestrator not available")
            return AnalysisResult(
                target_path=target_path, issues=[], metrics={"status": "lens_unavailable"},
                success=False, error="LENS orchestrator not importable in current environment",
            )
        except Exception as e:
            logger.error(f"MCP analysis failed: {e}")
            raise ToolUnavailableError(f"MCP analysis unavailable: {e}") from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using grep-based search."""
        import subprocess
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", query, "."],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            matches = []
            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "content": parts[2].strip(),
                        })
            return SearchResult(
                query=query, matches=matches, total_count=len(matches), success=True,
            )
        except Exception as e:
            logger.error(f"MCP search failed: {e}")
            raise ToolUnavailableError(f"MCP search unavailable: {e}") from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using AST-based hash comparison."""
        import ast
        import hashlib
        from pathlib import Path
        try:
            function_hashes: Dict[str, List[Dict[str, Any]]] = {}
            scope_path = Path(scope)
            if scope_path.is_file():
                files = [scope_path]
            elif scope_path.is_dir():
                files = list(scope_path.rglob("*.py"))
            else:
                files = list(Path(".").rglob("*.py"))

            for py_file in files[:100]:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            body = ast.dump(node)
                            h = hashlib.md5(body.encode()).hexdigest()
                            entry = {"file": str(py_file), "name": node.name, "line": node.lineno}
                            function_hashes.setdefault(h, []).append(entry)
                except Exception:
                    continue

            duplicates = [
                {"hash": h, "count": len(locs), "locations": locs}
                for h, locs in function_hashes.items() if len(locs) > 1
            ]
            return DuplicateResult(scope=scope, duplicates=duplicates, success=True)
        except Exception as e:
            logger.error(f"MCP duplicate detection failed: {e}")
            raise ToolUnavailableError(f"MCP duplicate detection unavailable: {e}") from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history using subprocess git commands."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", f"--since={lookback_hours} hours ago",
                 "--pretty=format:%H|%an|%ae|%s|%aI", "--no-merges"],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 4)
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0], "author": parts[1],
                            "email": parts[2], "message": parts[3], "date": parts[4],
                        })
            return GitHistoryResult(
                lookback_hours=lookback_hours, commits=commits, success=True,
            )
        except Exception as e:
            logger.error(f"MCP git history failed: {e}")
            raise ToolUnavailableError(f"MCP git history unavailable: {e}") from e

    def is_available(self, tool_name: str) -> bool:
        """Check if tool is available by testing imports/commands."""
        checkers = {
            "analyze": self._check_lens_available,
            "search": lambda: True,
            "duplicates": lambda: True,
            "git_history": self._check_git_available,
        }
        checker = checkers.get(tool_name)
        return checker() if checker else False

    @staticmethod
    def _check_lens_available() -> bool:
        """Check if LENS orchestrator is importable."""
        try:
            from cortex.lens.lens_orchestrator import LENSOrchestrator  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _check_git_available() -> bool:
        """Check if git is available."""
        import subprocess
        try:
            subprocess.run(["git", "--version"], capture_output=True, timeout=5)
            return True
        except Exception:
            return False

    def get_environment_info(self) -> Dict[str, Any]:
        """Get MCP environment information."""
        return {
            "environment": "MCP_SERVER",
            "tools": {
                name: self.is_available(name)
                for name in ["analyze", "search", "duplicates", "git_history"]
            },
            "status": "production",
        }


class CopilotToolAdapter(IToolAdapter):
    """
    Tool adapter for VS Code Copilot environment.

    In Copilot context, tools are invoked by the AI agent through VS Code
    extension APIs (grep_search, semantic_search, etc.) — not callable
    from Python directly. This adapter delegates to subprocess where possible.
    """

    def __init__(self) -> None:
        """Initialize Copilot tool adapter."""
        self.environment = "COPILOT"
        logger.debug("Initialized CopilotToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code — delegates to LENS if available, else basic lint."""
        try:
            from pathlib import Path
            from cortex.lens.lens_orchestrator import LENSOrchestrator
            target = Path(target_path)
            orchestrator = LENSOrchestrator(repo_path=str(target.parent if target.is_file() else target))

            if target.is_file():
                result = orchestrator.analyze_file(target)
                issues = result.get("issues", []) if isinstance(result, dict) else []
                metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
            else:
                batch = orchestrator.analyze_batch(list(target.rglob("*.py"))[:50])
                issues = []
                metrics = {"files_analyzed": len(batch)}
                for file_result in batch.values():
                    if isinstance(file_result, dict):
                        issues.extend(file_result.get("issues", []))

            return AnalysisResult(
                target_path=target_path, issues=issues, metrics=metrics, success=True,
            )
        except ImportError:
            return AnalysisResult(
                target_path=target_path, issues=[], metrics={},
                success=False, error="LENS not available in Copilot context",
            )
        except Exception as e:
            logger.error(f"Copilot analysis failed: {e}")
            raise ToolUnavailableError(f"Copilot analysis unavailable: {e}") from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using grep subprocess."""
        import subprocess
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", query, "."],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            matches = []
            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "content": parts[2].strip(),
                        })
            return SearchResult(
                query=query, matches=matches, total_count=len(matches), success=True,
            )
        except Exception as e:
            logger.error(f"Copilot search failed: {e}")
            raise ToolUnavailableError(f"Copilot search unavailable: {e}") from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using AST hash comparison."""
        import ast
        import hashlib
        from pathlib import Path
        try:
            function_hashes: Dict[str, List[Dict[str, Any]]] = {}
            scope_path = Path(scope)
            files = (
                [scope_path] if scope_path.is_file()
                else list(scope_path.rglob("*.py")) if scope_path.is_dir()
                else list(Path(".").rglob("*.py"))
            )
            for py_file in files[:100]:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            body = ast.dump(node)
                            h = hashlib.md5(body.encode()).hexdigest()
                            entry = {"file": str(py_file), "name": node.name, "line": node.lineno}
                            function_hashes.setdefault(h, []).append(entry)
                except Exception:
                    continue
            duplicates = [
                {"hash": h, "count": len(locs), "locations": locs}
                for h, locs in function_hashes.items() if len(locs) > 1
            ]
            return DuplicateResult(scope=scope, duplicates=duplicates, success=True)
        except Exception as e:
            logger.error(f"Copilot duplicate detection failed: {e}")
            raise ToolUnavailableError(f"Copilot duplicate detection unavailable: {e}") from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history via subprocess git command."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", f"--since={lookback_hours} hours ago",
                 "--pretty=format:%H|%an|%ae|%s|%aI", "--no-merges"],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 4)
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0], "author": parts[1],
                            "email": parts[2], "message": parts[3], "date": parts[4],
                        })
            return GitHistoryResult(
                lookback_hours=lookback_hours, commits=commits, success=True,
            )
        except Exception as e:
            logger.error(f"Copilot git history failed: {e}")
            raise ToolUnavailableError(f"Copilot git history unavailable: {e}") from e

    def is_available(self, tool_name: str) -> bool:
        """Check if tool is available in Copilot context."""
        return tool_name in {"analyze", "search", "duplicates", "git_history"}

    def get_environment_info(self) -> Dict[str, Any]:
        """Get Copilot environment information."""
        return {
            "environment": "COPILOT",
            "tools": ["analyze", "search", "duplicates", "git_history"],
            "status": "development",
        }


class DevelopmentToolAdapter(IToolAdapter):
    """
    Local development tool adapter.

    Routes to local CLI tools: subprocess grep, git commands,
    AST-based analysis, and filesystem operations.
    """

    def __init__(self) -> None:
        """Initialize development tool adapter."""
        self.environment = "DEVELOPMENT"
        logger.debug("Initialized DevelopmentToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code using py_compile for syntax + basic checks."""
        import py_compile
        from pathlib import Path
        try:
            issues = []
            target = Path(target_path)
            files = [target] if target.is_file() else list(target.rglob("*.py"))
            for py_file in files[:50]:
                try:
                    py_compile.compile(str(py_file), doraise=True)
                except py_compile.PyCompileError as e:
                    issues.append({
                        "file": str(py_file),
                        "type": "syntax_error",
                        "message": str(e),
                    })
            return AnalysisResult(
                target_path=target_path,
                issues=issues,
                metrics={"files_checked": len(files), "syntax_errors": len(issues)},
                success=True,
            )
        except Exception as e:
            logger.error(f"Local analysis failed: {e}")
            raise ToolUnavailableError(f"Local analysis unavailable: {e}") from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using grep subprocess."""
        import subprocess
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", query, "."],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            matches = []
            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "content": parts[2].strip(),
                        })
            return SearchResult(
                query=query, matches=matches, total_count=len(matches), success=True,
            )
        except Exception as e:
            logger.error(f"Local search failed: {e}")
            raise ToolUnavailableError(f"Local search unavailable: {e}") from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using AST hash comparison."""
        import ast
        import hashlib
        from pathlib import Path
        try:
            function_hashes: Dict[str, List[Dict[str, Any]]] = {}
            scope_path = Path(scope)
            files = (
                [scope_path] if scope_path.is_file()
                else list(scope_path.rglob("*.py")) if scope_path.is_dir()
                else list(Path(".").rglob("*.py"))
            )
            for py_file in files[:100]:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            body = ast.dump(node)
                            h = hashlib.md5(body.encode()).hexdigest()
                            entry = {"file": str(py_file), "name": node.name, "line": node.lineno}
                            function_hashes.setdefault(h, []).append(entry)
                except Exception:
                    continue
            duplicates = [
                {"hash": h, "count": len(locs), "locations": locs}
                for h, locs in function_hashes.items() if len(locs) > 1
            ]
            return DuplicateResult(scope=scope, duplicates=duplicates, success=True)
        except Exception as e:
            logger.error(f"Local duplicate detection failed: {e}")
            raise ToolUnavailableError(f"Local duplicate detection unavailable: {e}") from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history via subprocess."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", f"--since={lookback_hours} hours ago",
                 "--pretty=format:%H|%an|%ae|%s|%aI", "--no-merges"],
                capture_output=True, text=True, timeout=30, cwd="."
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 4)
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0], "author": parts[1],
                            "email": parts[2], "message": parts[3], "date": parts[4],
                        })
            return GitHistoryResult(
                lookback_hours=lookback_hours, commits=commits, success=True,
            )
        except Exception as e:
            logger.error(f"Local git history failed: {e}")
            raise ToolUnavailableError(f"Local git history unavailable: {e}") from e

    def is_available(self, tool_name: str) -> bool:
        """Check if local tool is available."""
        return tool_name in {"analyze", "search", "duplicates", "git_history"}

    def get_environment_info(self) -> Dict[str, Any]:
        """Get development environment information."""
        return {
            "environment": "DEVELOPMENT",
            "tools": ["analyze", "search", "duplicates", "git_history"],
            "status": "local_development",
        }
