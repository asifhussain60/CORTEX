"""Base Health Agent - Abstract Interface for All Health Agents

Defines the contract that all health agents must implement for detecting
and reporting health issues in the CORTEX repository.

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class HealthIssueSeverity(Enum):
    """Severity levels for health issues."""

    CRITICAL = "critical"  # P0: Blocks production readiness
    HIGH = "high"          # P1: Should fix soon
    MEDIUM = "medium"      # P2: Technical debt
    LOW = "low"            # P3: Nice to have
    INFO = "info"          # Informational only


class HealthIssueCategory(Enum):
    """Categories of health issues."""

    DUPLICATE = "duplicate"              # CORE-035 violations
    STUB = "stub"                        # Weak implementations
    PATH = "path"                        # Path integrity issues
    PATH_DRIFT = "path_drift"            # Import path issues
    VERSION_ARTIFACT = "version_artifact"  # Versioned files
    MISSING_TEST = "missing_test"        # Test coverage gaps
    CONFIGURATION = "configuration"      # MCP/configuration issues
    CONFIG_MISPLACED = "config_misplaced"  # Config outside registry
    WEAK_IMPLEMENTATION = "weak_implementation"  # Low quality code
    MULTIPLE_EXECUTION_PATHS = "multiple_execution_paths"  # Path ambiguity


@dataclass
class HealthIssue:
    """A detected health issue in the repository.

    Attributes:
        category: Issue category (duplicate, stub, etc.)
        severity: Issue severity (critical, high, medium, low, info)
        file_path: Path to affected file
        description: Human-readable description
        line_number: Optional line number in file
        suggested_fix: Optional fix suggestion
        metadata: Additional context data
        detected_at: Timestamp of detection
    """

    category: HealthIssueCategory
    severity: HealthIssueSeverity
    file_path: Path
    description: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary.

        Returns:
            Dictionary representation of issue
        """
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "file_path": str(self.file_path),
            "description": self.description,
            "line_number": self.line_number,
            "suggested_fix": self.suggested_fix,
            "metadata": self.metadata,
            "detected_at": self.detected_at,
        }


@dataclass
class HealthCheckResult:  # noqa: CORE-035-scoped — domain-specific health check result variant
    """Result of a health agent check.

    Attributes:
        agent_name: Name of agent that ran check
        issues: List of detected issues
        files_scanned: Number of files scanned
        duration_seconds: Time taken to run check
        timestamp: When check was performed
        metadata: Additional result data
    """

    agent_name: str
    issues: List[HealthIssue] = field(default_factory=list)
    files_scanned: int = 0
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def issue_count(self) -> int:
        """Get total number of issues detected.

        Returns:
            Number of issues
        """
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        """Get number of critical issues.

        Returns:
            Number of critical issues
        """
        return sum(1 for issue in self.issues if issue.severity == HealthIssueSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Get number of high severity issues.

        Returns:
            Number of high severity issues
        """
        return sum(1 for issue in self.issues if issue.severity == HealthIssueSeverity.HIGH)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of result
        """
        return {
            "agent_name": self.agent_name,
            "issues": [issue.to_dict() for issue in self.issues],
            "files_scanned": self.files_scanned,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "summary": {
                "total_issues": self.issue_count,
                "critical": self.critical_count,
                "high": self.high_count,
            },
        }


class BaseHealthAgent(ABC):
    """Abstract base class for all health agents.

    All health agents must inherit from this class and implement
    the check() method to detect specific types of health issues.

    Attributes:
        name: Agent name
        description: Agent description
        enabled: Whether agent is enabled
        config: Agent-specific configuration
    """

    def __init__(
        self,
        name: str,
        description: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize health agent.

        Args:
            name: Agent name (e.g., "DuplicateDetectionAgent")
            description: Agent description
            config: Optional configuration dictionary
        """
        self.name = name
        self.description = description
        self.enabled = True
        self.config = config or {}

    @abstractmethod
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run health check on workspace.

        Args:
            workspace_root: Root path of workspace to check

        Returns:
            HealthCheckResult with detected issues
        """
        pass

    def enable(self) -> None:
        """Enable this agent."""
        self.enabled = True

    def disable(self) -> None:
        """Disable this agent."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if agent is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.enabled


__all__ = [
    "HealthIssueSeverity",
    "HealthIssueCategory",
    "HealthIssue",
    "HealthCheckResult",
    "BaseHealthAgent",
]
