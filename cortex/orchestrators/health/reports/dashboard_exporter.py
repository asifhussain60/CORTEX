"""Dashboard Exporter - Export Health Metrics to Dashboard Format

Exports health metrics in formats suitable for dashboard visualization
and monitoring systems (JSON, YAML, Prometheus).

Author: CORTEX Framework
Phase: PHASE-95 S3 Completion
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, Literal

from .health_report import HealthReport


class DashboardExporter:
    """Export health reports to dashboard-compatible formats.

    Supports multiple output formats:
    - JSON: Standard dashboard format
    - YAML: Human-readable format
    - Prometheus: Metrics format (future)

    Attributes:
        format: Output format (json, yaml, prometheus)
        include_details: Whether to include detailed issue information
    """

    def __init__(
        self,
        format: Literal["json", "yaml"] = "json",
        include_details: bool = True,
    ) -> None:
        """Initialize Dashboard Exporter.

        Args:
            format: Output format (json or yaml)
            include_details: Whether to include detailed issue information

        Raises:
            ValueError: If format is not supported
        """
        if format not in ["json", "yaml"]:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'yaml'")

        self.format = format
        self.include_details = include_details

    def export(self, report: HealthReport, output_path: Path) -> None:
        """Export health report to file.

        Args:
            report: Health report to export
            output_path: Path to write output file

        Raises:
            PermissionError: If output location is not writable
        """
        dashboard_data = self.to_dashboard_format(report)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.format == "json":
            with open(output_path, "w") as f:
                json.dump(dashboard_data, f, indent=2, default=str)
        elif self.format == "yaml":
            with open(output_path, "w") as f:
                yaml.dump(dashboard_data, f, default_flow_style=False, sort_keys=False)

    def to_dashboard_format(self, report: HealthReport) -> Dict[str, Any]:
        """Convert health report to dashboard format.

        Args:
            report: Health report to convert

        Returns:
            Dictionary in dashboard format
        """
        # Calculate summary
        summary = {
            "health_score": report.metrics.health_score,
            "total_issues": report.metrics.total_issues,
            "agents_run": report.metrics.agents_run,
            "files_scanned": report.metrics.files_scanned,
            "duration_seconds": report.metrics.duration_seconds,
            "status": self._calculate_status(report.metrics.health_score),
        }

        # Group issues by category and severity
        issues_by_category = self._group_by_category(report)
        issues_by_severity = {
            "CRITICAL": report.metrics.critical_issues,
            "HIGH": report.metrics.high_issues,
            "MEDIUM": report.metrics.medium_issues,
            "LOW": report.metrics.low_issues,
            "INFO": report.metrics.info_issues,
        }

        # Prepare agent results
        agent_results = []
        for result in report.agent_results:
            agent_data = {
                "agent_name": result.agent_name,
                "issue_count": len(result.issues),
                "duration_seconds": result.duration_seconds,
                "files_scanned": result.files_scanned,
            }

            if self.include_details:
                agent_data["issues"] = [
                    {
                        "category": issue.category.value,
                        "severity": issue.severity.value,
                        "description": issue.description,
                        "file_path": str(issue.file_path),
                        "line_number": issue.line_number,
                        "metadata": issue.metadata,
                    }
                    for issue in result.issues
                ]

            agent_results.append(agent_data)

        # Generate timeline entry
        timeline = [{
            "timestamp": report.timestamp if isinstance(report.timestamp, str) else report.timestamp.isoformat(),
            "health_score": report.metrics.health_score,
            "total_issues": report.metrics.total_issues,
        }]

        return {
            "timestamp": report.timestamp if isinstance(report.timestamp, str) else report.timestamp.isoformat(),
            "workspace_root": str(report.workspace_root),
            "summary": summary,
            "metrics": report.metrics.to_dict(),
            "results": agent_results,
            "issues_by_category": issues_by_category,
            "issues_by_severity": issues_by_severity,
            "timeline": timeline,
        }

    def _calculate_status(self, health_score: float) -> str:
        """Calculate overall status from health score.

        Args:
            health_score: Health score (0-100)

        Returns:
            Status string (HEALTHY, WARNING, CRITICAL)
        """
        if health_score >= 80:
            return "HEALTHY"
        elif health_score >= 60:
            return "WARNING"
        else:
            return "CRITICAL"

    def _group_by_category(self, report: HealthReport) -> Dict[str, int]:
        """Group issues by category.

        Args:
            report: Health report

        Returns:
            Dictionary mapping category to issue count
        """
        category_counts: Dict[str, int] = {}

        for result in report.agent_results:
            for issue in result.issues:
                category = issue.category.value
                category_counts[category] = category_counts.get(category, 0) + 1

        return category_counts
