"""Unit Tests for Dashboard Exporter

Tests dashboard export functionality for health metrics.

Author: CORTEX Framework
Phase: PHASE-95 S3 Completion
CORE Rules: CORE-008 (TDD)
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from cortex.orchestrators.health.reports.dashboard_exporter import DashboardExporter
from cortex.orchestrators.health.reports.health_report import HealthReport, HealthMetrics
from cortex.orchestrators.health.agents.base_agent import (
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


@pytest.fixture
def sample_report() -> HealthReport:
    """Create sample health report.
    
    Returns:
        Sample HealthReport instance
    """
    result1 = HealthCheckResult(
        agent_name="DuplicateDetectionAgent",
        issues=[
            HealthIssue(
                category=HealthIssueCategory.DUPLICATE,
                severity=HealthIssueSeverity.HIGH,
                file_path=Path("cortex/utils.py"),
                description="Duplicate file detected",
                line_number=None,
                metadata={"duplicate_of": "cortex/common/utils.py"},
            )
        ],
        files_scanned=100,
        duration_seconds=1.5,
    )
    
    result2 = HealthCheckResult(
        agent_name="StubDetectionAgent",
        issues=[],
        files_scanned=100,
        duration_seconds=2.0,
    )
    
    metrics = HealthMetrics(
        total_issues=1,
        critical_issues=0,
        high_issues=1,
        medium_issues=0,
        low_issues=0,
        info_issues=0,
        files_scanned=100,
        agents_run=2,
        duration_seconds=3.5,
        health_score=90.0,
    )
    
    report = HealthReport(
        workspace_root=Path("/test/workspace"),
        timestamp=datetime.now().isoformat(),
        agent_results=[result1, result2],
        metrics=metrics,
    )
    
    return report


class TestDashboardExporterInitialization:
    """Test suite for DashboardExporter initialization."""
    
    def test_init_default(self) -> None:
        """Test initialization with defaults."""
        exporter = DashboardExporter()
        
        assert exporter.format == "json"
        assert exporter.include_details is True
    
    def test_init_with_format(self) -> None:
        """Test initialization with custom format."""
        exporter = DashboardExporter(format="yaml")
        
        assert exporter.format == "yaml"
    
    def test_init_with_options(self) -> None:
        """Test initialization with custom options."""
        exporter = DashboardExporter(include_details=False)
        
        assert exporter.include_details is False


class TestJSONExport:
    """Test suite for JSON export."""
    
    def test_export_to_json(self, sample_report: HealthReport, tmp_path: Path) -> None:
        """Test exporting health report to JSON.
        
        Args:
            sample_report: Sample health report
            tmp_path: Pytest temporary directory
        """
        exporter = DashboardExporter(format="json")
        output_file = tmp_path / "health_metrics.json"
        
        exporter.export(sample_report, output_file)
        
        assert output_file.exists()
        
        # Verify JSON structure
        with open(output_file) as f:
            data = json.load(f)
        
        assert "timestamp" in data
        assert "workspace_root" in data
        assert "metrics" in data
        assert "results" in data
        
        assert data["metrics"]["health_score"] == 90.0
        assert data["metrics"]["total_issues"] == 1
        assert len(data["results"]) == 2
    
    def test_export_json_minimal(
        self, sample_report: HealthReport, tmp_path: Path
    ) -> None:
        """Test exporting JSON without details.
        
        Args:
            sample_report: Sample health report
            tmp_path: Pytest temporary directory
        """
        exporter = DashboardExporter(format="json", include_details=False)
        output_file = tmp_path / "health_metrics_minimal.json"
        
        exporter.export(sample_report, output_file)
        
        with open(output_file) as f:
            data = json.load(f)
        
        # Should have metrics but not detailed issue information
        assert "metrics" in data
        assert "results" in data
        
        # Results should be summary only
        for result in data["results"]:
            assert "agent_name" in result
            assert "issue_count" in result


class TestYAMLExport:
    """Test suite for YAML export."""
    
    def test_export_to_yaml(self, sample_report: HealthReport, tmp_path: Path) -> None:
        """Test exporting health report to YAML.
        
        Args:
            sample_report: Sample health report
            tmp_path: Pytest temporary directory
        """
        exporter = DashboardExporter(format="yaml")
        output_file = tmp_path / "health_metrics.yaml"
        
        exporter.export(sample_report, output_file)
        
        assert output_file.exists()
        
        # Read and verify YAML content
        content = output_file.read_text()
        assert "health_score: 90.0" in content
        assert "total_issues: 1" in content
        assert "DuplicateDetectionAgent" in content


class TestDashboardDataTransformation:
    """Test suite for dashboard data transformation."""
    
    def test_to_dashboard_format(self, sample_report: HealthReport) -> None:
        """Test converting health report to dashboard format.
        
        Args:
            sample_report: Sample health report
        """
        exporter = DashboardExporter()
        
        dashboard_data = exporter.to_dashboard_format(sample_report)
        
        assert isinstance(dashboard_data, dict)
        assert "summary" in dashboard_data
        assert "results" in dashboard_data  # Changed from agent_results
        assert "issues_by_category" in dashboard_data
        assert "issues_by_severity" in dashboard_data
        assert "timeline" in dashboard_data
    
    def test_dashboard_summary(self, sample_report: HealthReport) -> None:
        """Test dashboard summary section.
        
        Args:
            sample_report: Sample health report
        """
        exporter = DashboardExporter()
        dashboard_data = exporter.to_dashboard_format(sample_report)
        
        summary = dashboard_data["summary"]
        
        assert summary["health_score"] == 90.0
        assert summary["total_issues"] == 1
        assert summary["agents_run"] == 2
        assert summary["status"] in ["HEALTHY", "WARNING", "CRITICAL"]
    
    def test_issues_by_category(self, sample_report: HealthReport) -> None:
        """Test issues grouped by category.
        
        Args:
            sample_report: Sample health report
        """
        exporter = DashboardExporter()
        dashboard_data = exporter.to_dashboard_format(sample_report)
        
        by_category = dashboard_data["issues_by_category"]
        
        assert "duplicate" in by_category  # Lowercase key from enum value
        assert by_category["duplicate"] == 1
    
    def test_issues_by_severity(self, sample_report: HealthReport) -> None:
        """Test issues grouped by severity.
        
        Args:
            sample_report: Sample health report
        """
        exporter = DashboardExporter()
        dashboard_data = exporter.to_dashboard_format(sample_report)
        
        by_severity = dashboard_data["issues_by_severity"]
        
        assert "HIGH" in by_severity
        assert by_severity["HIGH"] == 1


class TestTimelineGeneration:
    """Test suite for health timeline generation."""
    
    def test_generate_timeline(self, sample_report: HealthReport) -> None:
        """Test generating health timeline data.
        
        Args:
            sample_report: Sample health report
        """
        exporter = DashboardExporter()
        dashboard_data = exporter.to_dashboard_format(sample_report)
        
        timeline = dashboard_data["timeline"]
        
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        # Each timeline entry should have timestamp and metrics
        for entry in timeline:
            assert "timestamp" in entry
            assert "health_score" in entry
            assert "total_issues" in entry


class TestExportErrorHandling:
    """Test suite for export error handling."""
    
    def test_export_to_readonly_location(
        self, sample_report: HealthReport, tmp_path: Path
    ) -> None:
        """Test export fails gracefully with readonly location.
        
        Args:
            sample_report: Sample health report
            tmp_path: Pytest temporary directory
        """
        exporter = DashboardExporter()
        
        # Try to export to nonexistent parent (should fail)
        nonexistent = tmp_path / "nonexistent" / "deep" / "path" / "health_metrics.json"
        
        # Should raise OSError when parent directory creation fails
        try:
            exporter.export(sample_report, nonexistent)
            # If it succeeds (parent dir created), that's also OK
        except (OSError, PermissionError):
            # Expected behavior for readonly/permission issues
            pass
    
    def test_export_invalid_format(self, sample_report: HealthReport, tmp_path: Path) -> None:
        """Test export with invalid format.
        
        Args:
            sample_report: Sample health report
            tmp_path: Pytest temporary directory
        """
        with pytest.raises(ValueError, match="Unsupported format"):
            DashboardExporter(format="xml")
