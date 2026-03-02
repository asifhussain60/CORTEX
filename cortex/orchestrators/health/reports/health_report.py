"""Health Report - Aggregated Health Metrics

Aggregates results from all health agents into a comprehensive report
with metrics, visualizations, and actionable recommendations.

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path

from ..agents.base_agent import HealthCheckResult, HealthIssueSeverity


@dataclass
class HealthMetrics:
    """Aggregated health metrics across all agents.

    Attributes:
        total_issues: Total number of issues detected
        critical_issues: Number of critical (P0) issues
        high_issues: Number of high (P1) issues
        medium_issues: Number of medium (P2) issues
        low_issues: Number of low (P3) issues
        info_issues: Number of informational issues
        files_scanned: Total files scanned
        agents_run: Number of agents that ran
        duration_seconds: Total time taken
        health_score: Overall health score (0-100)
    """

    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    files_scanned: int = 0
    agents_run: int = 0
    duration_seconds: float = 0.0
    health_score: float = 100.0

    def calculate_health_score(self) -> float:
        """Calculate overall health score based on issue severity.

        Returns:
            Health score (0-100, higher is better)
        """
        # Scoring: Critical=-20, High=-10, Medium=-5, Low=-2, Info=-0
        deductions = (
            (self.critical_issues * 20) +
            (self.high_issues * 10) +
            (self.medium_issues * 5) +
            (self.low_issues * 2)
        )

        self.health_score = max(0.0, 100.0 - deductions)
        return self.health_score

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "total_issues": self.total_issues,
            "by_severity": {
                "critical": self.critical_issues,
                "high": self.high_issues,
                "medium": self.medium_issues,
                "low": self.low_issues,
                "info": self.info_issues,
            },
            "files_scanned": self.files_scanned,
            "agents_run": self.agents_run,
            "duration_seconds": self.duration_seconds,
            "health_score": self.health_score,
        }


@dataclass
class HealthReport:
    """Comprehensive health report.

    Attributes:
        workspace_root: Path to workspace that was checked
        timestamp: When report was generated
        agent_results: Results from each agent
        metrics: Aggregated metrics
        recommendations: List of recommended actions
        metadata: Additional report data
    """

    workspace_root: Path
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_results: List[HealthCheckResult] = field(default_factory=list)
    metrics: HealthMetrics = field(default_factory=HealthMetrics)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_agent_result(self, result: HealthCheckResult) -> None:
        """Add result from an agent.

        Args:
            result: HealthCheckResult from agent
        """
        self.agent_results.append(result)
        self._update_metrics()

    @property
    def all_issues(self) -> List:
        """Get all issues from all agents.

        Returns:
            List of all HealthIssue objects
        """
        issues = []
        for result in self.agent_results:
            issues.extend(result.issues)
        return issues

    @property
    def total_issues(self) -> int:
        """Get total number of issues.

        Returns:
            Total issue count
        """
        return self.metrics.total_issues

    @property
    def health_score(self) -> float:
        """Get overall health score.

        Returns:
            Health score (0-100)
        """
        return self.metrics.health_score

    @property
    def by_severity(self) -> Dict[str, int]:
        """Get issues grouped by severity.

        Returns:
            Dictionary with severity counts
        """
        return {
            "critical": self.metrics.critical_issues,
            "high": self.metrics.high_issues,
            "medium": self.metrics.medium_issues,
            "low": self.metrics.low_issues,
            "info": self.metrics.info_issues,
        }

    def _update_metrics(self) -> None:
        """Update aggregated metrics from agent results."""
        self.metrics.total_issues = sum(r.issue_count for r in self.agent_results)
        self.metrics.files_scanned = sum(r.files_scanned for r in self.agent_results)
        self.metrics.agents_run = len(self.agent_results)
        self.metrics.duration_seconds = sum(r.duration_seconds for r in self.agent_results)

        # Reset severity counts before recalculating
        self.metrics.critical_issues = 0
        self.metrics.high_issues = 0
        self.metrics.medium_issues = 0
        self.metrics.low_issues = 0
        self.metrics.info_issues = 0

        # Count by severity
        for result in self.agent_results:
            for issue in result.issues:
                if issue.severity == HealthIssueSeverity.CRITICAL:
                    self.metrics.critical_issues += 1
                elif issue.severity == HealthIssueSeverity.HIGH:
                    self.metrics.high_issues += 1
                elif issue.severity == HealthIssueSeverity.MEDIUM:
                    self.metrics.medium_issues += 1
                elif issue.severity == HealthIssueSeverity.LOW:
                    self.metrics.low_issues += 1
                elif issue.severity == HealthIssueSeverity.INFO:
                    self.metrics.info_issues += 1

        # Calculate health score
        self.metrics.calculate_health_score()

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on findings.

        Returns:
            List of recommendations
        """
        self.recommendations.clear()

        if self.metrics.critical_issues > 0:
            self.recommendations.append(
                f"🔴 CRITICAL: Fix {self.metrics.critical_issues} P0 issues immediately"
            )

        if self.metrics.high_issues > 0:
            self.recommendations.append(
                f"🟡 HIGH: Address {self.metrics.high_issues} P1 issues this sprint"
            )

        if self.metrics.health_score < 50:
            self.recommendations.append(
                "⚠️ Health score below 50 — repository needs significant cleanup"
            )
        elif self.metrics.health_score < 80:
            self.recommendations.append(
                "ℹ️ Health score below 80 — consider addressing technical debt"
            )

        if self.metrics.health_score >= 95:
            self.recommendations.append(
                "✅ Excellent health! Repository is production-ready"
            )

        return self.recommendations

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "workspace_root": str(self.workspace_root),
            "timestamp": self.timestamp,
            "metrics": self.metrics.to_dict(),
            "agent_results": [r.to_dict() for r in self.agent_results],
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }

    def to_markdown(self) -> str:
        """Generate markdown report.

        Returns:
            Markdown-formatted report
        """
        lines = [
            "# CORTEX Health Report",
            "",
            f"**Workspace:** `{self.workspace_root}`",
            f"**Generated:** {self.timestamp}",
            f"**Health Score:** {self.metrics.health_score:.1f}/100",
            "",
            "## Metrics Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Issues | {self.metrics.total_issues} |",
            f"| Critical (P0) | {self.metrics.critical_issues} |",
            f"| High (P1) | {self.metrics.high_issues} |",
            f"| Medium (P2) | {self.metrics.medium_issues} |",
            f"| Low (P3) | {self.metrics.low_issues} |",
            f"| Files Scanned | {self.metrics.files_scanned} |",
            f"| Agents Run | {self.metrics.agents_run} |",
            f"| Duration | {self.metrics.duration_seconds:.2f}s |",
            "",
        ]

        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        if self.agent_results:
            lines.extend([
                "## Agent Results",
                "",
            ])
            for result in self.agent_results:
                lines.append(f"### {result.agent_name}")
                lines.append(f"- Issues: {result.issue_count}")
                lines.append(f"- Files Scanned: {result.files_scanned}")
                lines.append(f"- Duration: {result.duration_seconds:.2f}s")
                lines.append("")

        return "\n".join(lines)


__all__ = ["HealthMetrics", "HealthReport"]
