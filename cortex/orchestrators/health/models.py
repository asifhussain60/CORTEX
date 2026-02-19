"""Value Objects — Health-Vacuum Pipeline

All dataclasses shared by HealthOrchestrator, VacuumOrchestrator, and
the unified pipeline.  FileContext has its own module (file_context.py).

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Severity
# ─────────────────────────────────────────────────────────────────────────────

class IssueSeverity(Enum):
    """Severity levels for health/vacuum findings."""

    CRITICAL = "critical"   # P0 — blocks production readiness
    HIGH = "high"           # P1 — should fix soon
    MEDIUM = "medium"       # P2 — technical debt
    LOW = "low"             # P3 — nice to have
    INFO = "info"           # Informational only


# ─────────────────────────────────────────────────────────────────────────────
# Health findings
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class IssueFile:
    """A single health finding tied to a file.

    Attributes:
        check_id: Identifier of the check that found this (e.g. H-001).
        path: Relative path to the affected file.
        severity: How urgent this issue is.
        description: Human-readable explanation.
        suggested_fix: Optional actionable fix text.
        category: Optional category tag for grouping.
        metadata: Extra key/value context.
        detected_at: ISO-8601 timestamp.
    """

    check_id: str
    path: Path
    severity: IssueSeverity
    description: str
    suggested_fix: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary."""
        return {
            "check_id": self.check_id,
            "path": str(self.path),
            "severity": self.severity.value,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "category": self.category,
            "metadata": self.metadata,
            "detected_at": self.detected_at,
        }


@dataclass
class IssueDirectory:
    """A health finding tied to a directory.

    Attributes:
        check_id: Identifier of the check.
        path: Relative path to directory.
        severity: Urgency level.
        description: Explanation.
        file_count: Number of files inside (if applicable).
    """

    check_id: str
    path: Path
    severity: IssueSeverity
    description: str
    file_count: int = 0


@dataclass
class NamingViolation:
    """Result of classify_naming_violation().

    Attributes:
        original_name: Current filename.
        suggested_name: Compliant filename.
        violation_type: One of 'non_snake_case', 'non_kebab_case', 'screaming'.
    """

    original_name: str
    suggested_name: str
    violation_type: str


@dataclass
class RootViolation:
    """File sitting in the project root that should be elsewhere.

    Attributes:
        path: Relative path (always depth-1 from root).
        suggested_location: Where VacuumOrchestrator should move it.
        reason: Why the file doesn't belong in root.
    """

    path: Path
    suggested_location: Path
    reason: str


@dataclass
class DuplicateGroup:
    """A set of files with identical content (same MD5).

    Attributes:
        md5: Common hash.
        paths: All paths sharing this hash.
        canonical: The path deemed canonical (shortest, most central).
    """

    md5: str
    paths: List[Path]
    canonical: Optional[Path] = None


@dataclass
class AgentFinding:
    """Wrapper for a health-agent result that preserves the agent name.

    Attributes:
        agent_name: Name of the agent that produced findings.
        issues: The issues it found.
        files_scanned: How many files the agent inspected.
        duration_seconds: Wall-clock time.
    """

    agent_name: str
    issues: List[IssueFile] = field(default_factory=list)
    files_scanned: int = 0
    duration_seconds: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Scan result — output of HealthOrchestrator.scan()
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    """Aggregated output of a full health scan.

    Attributes:
        workspace_root: Absolute path that was scanned.
        issues: Every finding from all checks and agents.
        agent_findings: Per-agent breakdown.
        health_score: 0–100 (higher is healthier).
        total_issues: Count of all issues.
        critical_issues: Count of P0 issues.
        high_issues: Count of P1 issues.
        medium_issues: Count of P2 issues.
        low_issues: Count of P3 issues.
        info_issues: Count of informational issues.
        files_scanned: Total file count inspected.
        timestamp: ISO-8601 scan timestamp.
    """

    workspace_root: Path
    issues: List[IssueFile] = field(default_factory=list)
    agent_findings: List[AgentFinding] = field(default_factory=list)
    health_score: float = 100.0
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    files_scanned: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # ── helpers ──────────────────────────────────────────────────────────

    def recount(self) -> None:
        """Recalculate totals and health_score from ``self.issues``."""
        self.total_issues = len(self.issues)
        self.critical_issues = sum(
            1 for i in self.issues if i.severity == IssueSeverity.CRITICAL
        )
        self.high_issues = sum(
            1 for i in self.issues if i.severity == IssueSeverity.HIGH
        )
        self.medium_issues = sum(
            1 for i in self.issues if i.severity == IssueSeverity.MEDIUM
        )
        self.low_issues = sum(
            1 for i in self.issues if i.severity == IssueSeverity.LOW
        )
        self.info_issues = sum(
            1 for i in self.issues if i.severity == IssueSeverity.INFO
        )
        deductions = (
            self.critical_issues * 20
            + self.high_issues * 10
            + self.medium_issues * 5
            + self.low_issues * 2
        )
        self.health_score = max(0.0, 100.0 - deductions)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the full scan result."""
        return {
            "workspace_root": str(self.workspace_root),
            "health_score": self.health_score,
            "total_issues": self.total_issues,
            "by_severity": {
                "critical": self.critical_issues,
                "high": self.high_issues,
                "medium": self.medium_issues,
                "low": self.low_issues,
                "info": self.info_issues,
            },
            "files_scanned": self.files_scanned,
            "issues": [i.to_dict() for i in self.issues],
            "timestamp": self.timestamp,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Vacuum results — output of VacuumOrchestrator operations
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OperationResult:
    """Single vacuum operation outcome.

    Attributes:
        op_type: Operation kind (rename, delete, relocate, archive, …).
        source: Source path.
        destination: Destination path (if applicable).
        success: Whether the operation succeeded.
        error: Error message on failure.
        dry_run: Whether this was a preview-only run.
        timestamp: ISO-8601 timestamp.
    """

    op_type: str
    source: Path
    success: bool
    destination: Optional[Path] = None
    error: Optional[str] = None
    dry_run: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to plain dictionary."""
        return {
            "op_type": self.op_type,
            "source": str(self.source),
            "destination": str(self.destination) if self.destination else None,
            "success": self.success,
            "error": self.error,
            "dry_run": self.dry_run,
            "timestamp": self.timestamp,
        }


@dataclass
class VacuumReport:
    """Aggregated report from a vacuum run.

    Attributes:
        operations: Every operation attempted.
        total_operations: Count of all operations.
        successful_operations: Count of successes.
        failed_operations: Count of failures.
        dry_run: Whether the entire run was preview-only.
        timestamp: ISO-8601 report timestamp.
    """

    operations: List[OperationResult] = field(default_factory=list)
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    dry_run: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def recount(self) -> None:
        """Recalculate totals from ``self.operations``."""
        self.total_operations = len(self.operations)
        self.successful_operations = sum(1 for o in self.operations if o.success)
        self.failed_operations = self.total_operations - self.successful_operations

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the full vacuum report."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "dry_run": self.dry_run,
            "operations": [o.to_dict() for o in self.operations],
            "timestamp": self.timestamp,
        }


@dataclass
class PipelineReport:
    """End-to-end report from the HealthVacuumPipeline.

    Attributes:
        scan_result: Output of the health scan stage.
        vacuum_report: Output of the vacuum execution stage.
        converged: Whether the pipeline reached convergence.
        cycles: Number of scan→execute cycles run.
        timestamp: ISO-8601 timestamp.
    """

    scan_result: Optional[ScanResult] = None
    vacuum_report: Optional[VacuumReport] = None
    converged: bool = False
    cycles: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


__all__ = [
    "IssueSeverity",
    "IssueFile",
    "IssueDirectory",
    "NamingViolation",
    "RootViolation",
    "DuplicateGroup",
    "AgentFinding",
    "ScanResult",
    "OperationResult",
    "VacuumReport",
    "PipelineReport",
]
