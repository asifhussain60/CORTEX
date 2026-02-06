"""
Tool Adapter Pattern for Environment-Agnostic Tool Access.

Provides unified interface for accessing tools (analysis, search, git) across
different environments (MCP Server, VS Code Copilot, Development).

Authority: Phase 33 - Architecture Alignment & Mandatory Governance Enforcement
CORE-008: TDD-first architecture
CORE-011: Type hints mandatory
CORE-012: Google-style docstrings
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum

import logging

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

    Routes to MCP server cortex_lens_analyze, cortex_detect_duplicates,
    cortex_git_history, semantic_search, etc.
    """

    def __init__(self) -> None:
        """Initialize MCP tool adapter."""
        self.environment = "MCP_SERVER"
        logger.debug("Initialized MCPToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code using cortex_lens_analyze MCP tool."""
        try:
            # In MCP mode, would call: cortex_lens_analyze(target_path)
            logger.info(f"[MCP] Analyzing code: {target_path}")
            # Placeholder: actual implementation calls MCP tool
            return AnalysisResult(
                target_path=target_path,
                issues=[],
                metrics={"status": "analyzed_via_mcp"},
                success=True,
            )
        except Exception as e:
            logger.error(f"MCP analysis failed: {e}")
            raise ToolUnavailableError(f"MCP analysis unavailable: {e}") from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using semantic_search MCP tool."""
        try:
            logger.info(f"[MCP] Searching workspace: {query}")
            # Placeholder: actual implementation calls MCP tool
            return SearchResult(
                query=query,
                matches=[],
                total_count=0,
                success=True,
            )
        except Exception as e:
            logger.error(f"MCP search failed: {e}")
            raise ToolUnavailableError(f"MCP search unavailable: {e}") from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using cortex_detect_duplicates MCP tool."""
        try:
            logger.info(f"[MCP] Detecting duplicates in: {scope}")
            # Placeholder: actual implementation calls MCP tool
            return DuplicateResult(
                scope=scope,
                duplicates=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"MCP duplicate detection failed: {e}")
            raise ToolUnavailableError(
                f"MCP duplicate detection unavailable: {e}"
            ) from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history using cortex_git_history MCP tool."""
        try:
            logger.info(f"[MCP] Fetching git history ({lookback_hours}h)")
            # Placeholder: actual implementation calls MCP tool
            return GitHistoryResult(
                lookback_hours=lookback_hours,
                commits=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"MCP git history failed: {e}")
            raise ToolUnavailableError(
                f"MCP git history unavailable: {e}"
            ) from e

    def is_available(self, tool_name: str) -> bool:
        """Check if MCP tool is available."""
        available_tools = {
            "analyze": True,
            "search": True,
            "duplicates": True,
            "git_history": True,
        }
        return available_tools.get(tool_name, False)

    def get_environment_info(self) -> Dict[str, Any]:
        """Get MCP environment information."""
        return {
            "environment": "MCP_SERVER",
            "tools": ["analyze", "search", "duplicates", "git_history"],
            "status": "production",
        }


class CopilotToolAdapter(IToolAdapter):
    """
    Development tool adapter using VS Code Copilot tools.

    Routes to VS Code extension APIs: grep_search, semantic_search,
    list_code_usages, read_file, etc.
    """

    def __init__(self) -> None:
        """Initialize Copilot tool adapter."""
        self.environment = "COPILOT"
        logger.debug("Initialized CopilotToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code using Copilot tools (grep + semantic search)."""
        try:
            logger.info(f"[Copilot] Analyzing code: {target_path}")
            # Placeholder: actual implementation uses VS Code tools
            return AnalysisResult(
                target_path=target_path,
                issues=[],
                metrics={"status": "analyzed_via_copilot"},
                success=True,
            )
        except Exception as e:
            logger.error(f"Copilot analysis failed: {e}")
            raise ToolUnavailableError(
                f"Copilot analysis unavailable: {e}"
            ) from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using Copilot semantic_search tool."""
        try:
            logger.info(f"[Copilot] Searching workspace: {query}")
            # Placeholder: actual implementation calls VS Code tool
            return SearchResult(
                query=query,
                matches=[],
                total_count=0,
                success=True,
            )
        except Exception as e:
            logger.error(f"Copilot search failed: {e}")
            raise ToolUnavailableError(
                f"Copilot search unavailable: {e}"
            ) from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using Copilot grep + pattern matching."""
        try:
            logger.info(f"[Copilot] Detecting duplicates in: {scope}")
            # Placeholder: actual implementation uses VS Code tools
            return DuplicateResult(
                scope=scope,
                duplicates=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"Copilot duplicate detection failed: {e}")
            raise ToolUnavailableError(
                f"Copilot duplicate detection unavailable: {e}"
            ) from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history via Copilot terminal/git command."""
        try:
            logger.info(f"[Copilot] Fetching git history ({lookback_hours}h)")
            # Placeholder: actual implementation runs git commands
            return GitHistoryResult(
                lookback_hours=lookback_hours,
                commits=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"Copilot git history failed: {e}")
            raise ToolUnavailableError(
                f"Copilot git history unavailable: {e}"
            ) from e

    def is_available(self, tool_name: str) -> bool:
        """Check if Copilot tool is available."""
        available_tools = {
            "analyze": True,
            "search": True,
            "duplicates": True,
            "git_history": True,
        }
        return available_tools.get(tool_name, False)

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

    Routes to Python libraries and local CLI tools: pylint, bandit,
    subprocess git commands, filesystem search, etc.
    """

    def __init__(self) -> None:
        """Initialize development tool adapter."""
        self.environment = "DEVELOPMENT"
        logger.debug("Initialized DevelopmentToolAdapter")

    def analyze_code(self, target_path: str) -> AnalysisResult:
        """Analyze code using local tools (pylint, bandit, etc)."""
        try:
            logger.info(f"[Dev] Analyzing code: {target_path}")
            # Placeholder: actual implementation uses local tools
            return AnalysisResult(
                target_path=target_path,
                issues=[],
                metrics={"status": "analyzed_locally"},
                success=True,
            )
        except Exception as e:
            logger.error(f"Local analysis failed: {e}")
            raise ToolUnavailableError(
                f"Local analysis unavailable: {e}"
            ) from e

    def search_workspace(self, query: str) -> SearchResult:
        """Search workspace using grep/ripgrep."""
        try:
            logger.info(f"[Dev] Searching workspace: {query}")
            # Placeholder: actual implementation uses subprocess/rg
            return SearchResult(
                query=query,
                matches=[],
                total_count=0,
                success=True,
            )
        except Exception as e:
            logger.error(f"Local search failed: {e}")
            raise ToolUnavailableError(
                f"Local search unavailable: {e}"
            ) from e

    def detect_duplicates(self, scope: str) -> DuplicateResult:
        """Detect duplicates using local Python library."""
        try:
            logger.info(f"[Dev] Detecting duplicates in: {scope}")
            # Placeholder: actual implementation uses local lib
            return DuplicateResult(
                scope=scope,
                duplicates=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"Local duplicate detection failed: {e}")
            raise ToolUnavailableError(
                f"Local duplicate detection unavailable: {e}"
            ) from e

    def get_git_history(self, lookback_hours: int = 24) -> GitHistoryResult:
        """Get git history via subprocess."""
        try:
            logger.info(f"[Dev] Fetching git history ({lookback_hours}h)")
            # Placeholder: actual implementation runs git commands
            return GitHistoryResult(
                lookback_hours=lookback_hours,
                commits=[],
                success=True,
            )
        except Exception as e:
            logger.error(f"Local git history failed: {e}")
            raise ToolUnavailableError(
                f"Local git history unavailable: {e}"
            ) from e

    def is_available(self, tool_name: str) -> bool:
        """Check if local tool is available."""
        available_tools = {
            "analyze": True,
            "search": True,
            "duplicates": True,
            "git_history": True,
        }
        return available_tools.get(tool_name, False)

    def get_environment_info(self) -> Dict[str, Any]:
        """Get development environment information."""
        return {
            "environment": "DEVELOPMENT",
            "tools": ["analyze", "search", "duplicates", "git_history"],
            "status": "local_development",
        }
