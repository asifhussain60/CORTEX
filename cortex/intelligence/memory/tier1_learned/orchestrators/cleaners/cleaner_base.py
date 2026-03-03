"""
Base Cleaner Interface

Purpose:
    Abstract base class defining the contract for all vacuum cleaner plugins.
    Ensures consistent API for analysis, execution, and rollback operations.

Authority:
    - AC-VACUUM-REFACTOR-001: Golden test-driven refactoring
    - CORE-008: TDD
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: CORTEX Architect
Date: 2026-02-15
"""
# noqa: CORE-035 — domain-scoped class names, not CORE-035 violations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class Analysis:
    """
    Analysis result from cleaner scan.

    Attributes:
        cleaner_id: Unique identifier for cleaner
        timestamp: ISO timestamp of analysis
        files_scanned: Number of files scanned
        issues_found: Number of issues detected
        plan: Execution plan (cleaner-specific structure)
        logs: Log messages from analysis
    """
    cleaner_id: str
    timestamp: str
    files_scanned: int
    issues_found: int
    plan: Dict[str, Any]
    logs: List[str] = field(default_factory=list)


@dataclass
class Report:
    """
    Execution report from cleaner.

    Attributes:
        cleaner_id: Unique identifier for cleaner
        timestamp: ISO timestamp of execution
        status: Execution status (SUCCESS, FAILED, PARTIAL)
        actions_taken: Total number of actions performed
        changes: Breakdown of changes by type
        errors: List of error messages
        logs: Log messages from execution
    """
    cleaner_id: str
    timestamp: str
    status: str  # SUCCESS, FAILED, PARTIAL
    actions_taken: int
    changes: Dict[str, int]  # e.g., {"deleted": 4, "relocated": 3}
    errors: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)


@dataclass
class RollbackResult:
    """
    Rollback operation result.

    Attributes:
        cleaner_id: Unique identifier for cleaner
        timestamp: ISO timestamp of rollback
        status: Rollback status (SUCCESS, FAILED, PARTIAL)
        files_restored: Number of files restored
        errors: List of error messages
    """
    cleaner_id: str
    timestamp: str
    status: str  # SUCCESS, FAILED, PARTIAL
    files_restored: int
    errors: List[str] = field(default_factory=list)


# =============================================================================
# CLEANER INTERFACE
# =============================================================================


class CleanerInterface(ABC):
    """
    Abstract base class for all vacuum cleaner plugins.

    Subclasses must implement:
        - name: Cleaner name
        - version: Cleaner version
        - domain: Domain identifier
        - analyze(): Scan and generate plan
        - execute(): Execute plan
        - rollback(): Rollback changes
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize cleaner with configuration.

        Args:
            config: Cleaner configuration dictionary
        """
        self.config = config
        self.repo_root = Path(config.get("repo_root", "."))
        self.dry_run = config.get("dry_run", False)
        self.verbose = config.get("verbose", False)
        self._backup_paths: List[Path] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return cleaner name.

        Returns:
            Human-readable cleaner name
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Return cleaner version.

        Returns:
            Semantic version string (e.g., "1.0.0")
        """
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """
        Return cleaner domain identifier.

        Returns:
            Domain identifier (e.g., "database_migration")
        """
        pass

    @abstractmethod
    def analyze(self) -> Analysis:
        """
        Scan repository and generate execution plan.

        Returns:
            Analysis object with scan results and execution plan
        """
        pass

    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Report:
        """
        Execute cleanup plan.

        Args:
            plan: Execution plan from analyze()

        Returns:
            Report object with execution results
        """
        pass

    @abstractmethod
    def rollback(self) -> RollbackResult:
        """
        Rollback changes made by execute().

        Returns:
            RollbackResult with restoration status
        """
        pass

    def _log(self, message: str) -> None:
        """
        Log message if verbose mode enabled.

        Args:
            message: Log message
        """
        if self.verbose:
            print(f"[{self.name}] {message}")

    def _timestamp(self) -> str:
        """
        Generate ISO timestamp.

        Returns:
            ISO 8601 timestamp string
        """
        return datetime.now().isoformat()
