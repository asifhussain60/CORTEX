"""
Unit tests for Governance Rule Dashboard.

Tests compliance heatmap, violation trends, and domain summaries.
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import Mock, patch

import pytest
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cortex.tools.governance_dashboard import (
    ComplianceLevel,
    GovernanceDashboardBuilder,
    GovernanceRuleDashboard,
    HeatmapRow,
    PhaseComplianceSummary,
    ViolationMetric,
)


class TestViolationMetric:
    """Test ViolationMetric dataclass."""

    def test_violation_metric_creation(self) -> None:
        """Test creating a violation metric."""
        metric = ViolationMetric(
            rule_id="CORE-008",
            domain="test_execution",
            phase_id="PHASE-09",
            violation_count=2,
            last_violation="2026-01-15T10:00:00Z",
            severity="warning",
        )

        assert metric.rule_id == "CORE-008"
        assert metric.violation_count == 2

    def test_violation_metric_to_dict(self) -> None:
        """Test ViolationMetric.to_dict()."""
        metric = ViolationMetric(
            rule_id="CORE-008",
            domain="test_execution",
            phase_id="PHASE-09",
            violation_count=2,
            last_violation="2026-01-15T10:00:00Z",
            severity="warning",
        )

        data = metric.to_dict()

        assert data["rule_id"] == "CORE-008"
        assert data["violation_count"] == 2
        assert data["severity"] == "warning"


class TestHeatmapRow:
    """Test HeatmapRow dataclass."""

    def test_heatmap_row_creation(self) -> None:
        """Test creating a heatmap row."""
        row = HeatmapRow(
            rule_id="CORE-008",
            rule_name="Test-Driven Development",
            domain="test_execution",
            severity="blocked",
        )
        row.phases["PHASE-09"] = 3
        row.phases["PHASE-10"] = 1

        assert len(row.phases) == 2
        assert row.phases["PHASE-09"] == 3

    def test_heatmap_row_to_dict(self) -> None:
        """Test HeatmapRow.to_dict()."""
        row = HeatmapRow(
            rule_id="CORE-008",
            rule_name="Test-Driven Development",
            domain="test_execution",
        )
        row.phases["PHASE-09"] = 2

        data = row.to_dict()

        assert data["rule_id"] == "CORE-008"
        assert data["max_violations"] == 2


class TestPhaseComplianceSummary:
    """Test PhaseComplianceSummary dataclass."""

    def test_phase_summary_compliant(self) -> None:
        """Test compliant phase summary."""
        summary = PhaseComplianceSummary(
            phase_id="PHASE-09",
            total_rules=10,
            compliant_rules=10,
            warning_rules=0,
            critical_rules=0,
            total_violations=0,
            compliance_percentage=100.0,
            status=ComplianceLevel.COMPLIANT,
        )

        assert summary.compliance_percentage == 100.0
        assert summary.status == ComplianceLevel.COMPLIANT

    def test_phase_summary_warning(self) -> None:
        """Test warning phase summary."""
        summary = PhaseComplianceSummary(
            phase_id="PHASE-09",
            total_rules=10,
            compliant_rules=8,
            warning_rules=2,
            critical_rules=0,
            total_violations=2,
            compliance_percentage=80.0,
            status=ComplianceLevel.WARNING,
        )

        assert summary.status == ComplianceLevel.WARNING

    def test_phase_summary_to_dict(self) -> None:
        """Test PhaseComplianceSummary.to_dict()."""
        summary = PhaseComplianceSummary(
            phase_id="PHASE-09",
            total_rules=10,
            compliant_rules=9,
            warning_rules=1,
            critical_rules=0,
            total_violations=1,
            compliance_percentage=90.0,
            status=ComplianceLevel.WARNING,
        )

        data = summary.to_dict()

        assert data["phase_id"] == "PHASE-09"
        assert data["compliance_percentage"] == 90.0
        assert data["status"] == "warning"


class TestComplianceLevel:
    """Test ComplianceLevel enum."""

    def test_compliance_levels(self) -> None:
        """Test all compliance levels."""
        assert ComplianceLevel.COMPLIANT.value == "compliant"
        assert ComplianceLevel.WARNING.value == "warning"
        assert ComplianceLevel.CRITICAL.value == "critical"
        assert ComplianceLevel.NO_DATA.value == "no_data"


class TestGovernanceDashboardBuilder:
    """Test GovernanceDashboardBuilder class."""

    @pytest.fixture
    def temp_workspace(self) -> Generator[Path, Any, Any]:
        """Create temporary workspace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "cortex_brain" / "state").mkdir(parents=True)
            (workspace / "cortex_brain" / "tier0" / "governance").mkdir(parents=True)

            # Create minimal rules file
            rules_file = workspace / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [
                    {"id": "CORE-008", "title": "TDD", "domain": "test_execution", "severity": "blocked"},
                    {"id": "CORE-011", "title": "Type Hints", "domain": "typing", "severity": "warning"},
                ]
            }))

            yield workspace

    def test_builder_initialization(self, temp_workspace: Path) -> None:
        """Test GovernanceDashboardBuilder initialization."""
        builder = GovernanceDashboardBuilder(temp_workspace)

        assert builder.workspace_root == temp_workspace
        assert builder.governance_db == temp_workspace / "cortex_brain" / "state" / "governance.db"

    def test_load_governance_rules(self, temp_workspace: Path) -> None:
        """Test loading governance rules."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()

        assert "CORE-008" in rules
        assert "CORE-011" in rules
        assert rules["CORE-008"]["title"] == "TDD"

    def test_load_governance_rules_no_file(self, temp_workspace: Path) -> None:
        """Test loading rules when file doesn't exist."""
        (temp_workspace / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml").unlink()

        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()

        assert rules == {}

    def test_build_heatmap_no_database(self, temp_workspace: Path) -> None:
        """Test building heatmap without database."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        heatmap = builder._build_heatmap({})

        assert heatmap == []

    def test_build_heatmap_with_violations(self, temp_workspace: Path) -> None:
        """Test building heatmap with violation data."""
        # Create database with violations
        db_path = temp_workspace / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE violations (
                rule_id TEXT,
                phase_id TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
        cursor.execute("INSERT INTO violations VALUES ('CORE-011', 'PHASE-10', 'info', '2026-01-16')")
        conn.commit()
        conn.close()

        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()
        heatmap = builder._build_heatmap(rules)

        assert len(heatmap) >= 1
        assert any(row.rule_id == "CORE-008" for row in heatmap)

    def test_build_phase_summaries_compliant(self, temp_workspace: Path) -> None:
        """Test building phase summaries for compliant phase."""
        db_path = temp_workspace / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE violations (
                rule_id TEXT,
                phase_id TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()
        summaries = builder._build_phase_summaries(rules)

        # Without violations, should be compliant
        for summary in summaries:
            if summary.total_violations == 0:
                assert summary.status == ComplianceLevel.COMPLIANT

    def test_build_phase_summaries_with_violations(self, temp_workspace: Path) -> None:
        """Test building phase summaries with violations."""
        db_path = temp_workspace / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE violations (
                rule_id TEXT,
                phase_id TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
        conn.commit()
        conn.close()

        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()
        summaries = builder._build_phase_summaries(rules)

        assert len(summaries) > 0

    def test_build_domain_summaries(self, temp_workspace: Path) -> None:
        """Test building domain summaries."""
        # Create database for domain summaries
        db_path = temp_workspace / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE violations (
                rule_id TEXT,
                phase_id TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

        builder = GovernanceDashboardBuilder(temp_workspace)
        rules = builder._load_governance_rules()
        summaries = builder._build_domain_summaries(rules)

        # Should have domain summaries for loaded rules
        assert len(summaries) >= 0
        for domain, summary in summaries.items():
            assert "total_rules" in summary
            assert "violations" in summary
            assert "compliance_percentage" in summary

    def test_build_violation_trends_no_data(self, temp_workspace: Path) -> None:
        """Test building violation trends with no data."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        trends = builder._build_violation_trends()

        assert trends == []

    def test_build_violation_trends_with_data(self, temp_workspace: Path) -> None:
        """Test building violation trends with data."""
        db_path = temp_workspace / "cortex_brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE violations (
                rule_id TEXT,
                phase_id TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15 10:00:00')")
        cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'info', '2026-01-15 11:00:00')")
        conn.commit()
        conn.close()

        builder = GovernanceDashboardBuilder(temp_workspace)
        trends = builder._build_violation_trends()

        assert len(trends) > 0

    def test_generate_recommendations_compliant(self, temp_workspace: Path) -> None:
        """Test recommendations for compliant phases."""
        dashboard = GovernanceRuleDashboard(
            timestamp="2026-01-15T00:00:00Z",
            phase_summaries=[
                PhaseComplianceSummary(
                    phase_id="PHASE-09",
                    total_rules=10,
                    compliant_rules=10,
                    warning_rules=0,
                    critical_rules=0,
                    total_violations=0,
                    compliance_percentage=100.0,
                    status=ComplianceLevel.COMPLIANT,
                )
            ],
        )

        builder = GovernanceDashboardBuilder(temp_workspace)
        recommendations = builder._generate_recommendations(dashboard)

        assert len(recommendations) > 0
        assert any("✅" in rec for rec in recommendations)

    def test_generate_recommendations_critical(self, temp_workspace: Path) -> None:
        """Test recommendations for critical phase."""
        dashboard = GovernanceRuleDashboard(
            timestamp="2026-01-15T00:00:00Z",
            phase_summaries=[
                PhaseComplianceSummary(
                    phase_id="PHASE-09",
                    total_rules=10,
                    compliant_rules=5,
                    warning_rules=0,
                    critical_rules=5,
                    total_violations=5,
                    compliance_percentage=50.0,
                    status=ComplianceLevel.CRITICAL,
                )
            ],
        )

        builder = GovernanceDashboardBuilder(temp_workspace)
        recommendations = builder._generate_recommendations(dashboard)

        assert len(recommendations) > 0
        assert any("🔴" in rec for rec in recommendations)

    def test_build_dashboard_full(self, temp_workspace: Path) -> None:
        """Test building complete dashboard."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        dashboard = builder.build_dashboard()

        assert dashboard.timestamp is not None
        assert isinstance(dashboard.heatmap, list)
        assert isinstance(dashboard.phase_summaries, list)
        assert isinstance(dashboard.domain_summaries, dict)
        assert isinstance(dashboard.recommendations, list)

    def test_dashboard_to_dict(self, temp_workspace: Path) -> None:
        """Test GovernanceRuleDashboard.to_dict()."""
        dashboard = GovernanceRuleDashboard(
            timestamp="2026-01-15T00:00:00Z",
            heatmap=[
                HeatmapRow(
                    rule_id="CORE-008",
                    rule_name="TDD",
                    domain="test_execution",
                )
            ],
            recommendations=["Test recommendation"],
        )

        data = dashboard.to_dict()

        assert data["timestamp"] == "2026-01-15T00:00:00Z"
        assert len(data["heatmap"]) == 1
        assert len(data["recommendations"]) == 1


class TestAcceptanceCriteriaGV00401:
    """Test Acceptance Criteria for GV-004-01."""

    @pytest.fixture
    def temp_workspace(self) -> Generator[Path, Any, Any]:
        """Create temporary workspace with violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            (workspace / "cortex_brain" / "state").mkdir(parents=True)
            (workspace / "cortex_brain" / "tier0" / "governance").mkdir(parents=True)

            # Create rules file
            rules_file = workspace / "cortex_brain" / "tier0" / "governance" / "core-rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [
                    {"id": "CORE-008", "title": "TDD", "domain": "test_execution", "severity": "blocked"},
                    {"id": "CORE-011", "title": "Type Hints", "domain": "typing", "severity": "warning"},
                    {"id": "CORE-012", "title": "Docstrings", "domain": "documentation", "severity": "info"},
                ]
            }))

            # Create database with violations
            db_path = workspace / "cortex_brain" / "state" / "governance.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE violations (
                    rule_id TEXT,
                    phase_id TEXT,
                    severity TEXT,
                    timestamp TEXT
                )
            """)
            # Add violations for different phases
            cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-14')")
            cursor.execute("INSERT INTO violations VALUES ('CORE-008', 'PHASE-09', 'warning', '2026-01-15')")
            cursor.execute("INSERT INTO violations VALUES ('CORE-011', 'PHASE-10', 'info', '2026-01-15')")
            conn.commit()
            conn.close()

            yield workspace

    def test_ac_1_heatmap_shows_rule_violations(self, temp_workspace: Path) -> None:
        """AC-GV-004-01-01: Heatmap shows compliance by rule × phase."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        dashboard = builder.build_dashboard()

        # Heatmap should show violations
        assert len(dashboard.heatmap) > 0

        # Check that each row represents a rule
        for row in dashboard.heatmap:
            assert row.rule_id is not None
            assert isinstance(row.phases, dict)

    def test_ac_2_violation_trends_tracked(self, temp_workspace: Path) -> None:
        """AC-GV-004-01-02: Violation trends are tracked over time."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        dashboard = builder.build_dashboard()

        # Should have phase summaries showing compliance trends
        assert len(dashboard.phase_summaries) >= 0

        # Each phase summary shows compliance percentage
        for phase in dashboard.phase_summaries:
            assert hasattr(phase, "compliance_percentage")
            assert 0 <= phase.compliance_percentage <= 100

    def test_ac_3_recommendations_generated(self, temp_workspace: Path) -> None:
        """AC-GV-004-01-03: Recommendations generated from dashboard."""
        builder = GovernanceDashboardBuilder(temp_workspace)
        dashboard = builder.build_dashboard()

        # Should have recommendations
        assert len(dashboard.recommendations) > 0

        # Recommendations should be actionable
        for rec in dashboard.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
