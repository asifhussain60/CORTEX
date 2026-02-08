"""Tests for cortex_brain integration orchestrator.

Phase 48 S4: CORTEX self-analysis via cortex_brain.
"""

import pytest
from cortex.orchestrators.holistic.cortex_brain_integration import (
    CortexBrainIntegrationOrchestrator,
    CortexSelfAnalysis,
    ArchitectureDriftDetection,
    InternalPackageRecommendation,
    SecurityGateAnalysis,
)


class TestCortexSelfAnalysis:
    """Tests for CortexSelfAnalysis dataclass."""

    def test_create_analysis(self):
        """Test creating a CORTEX self-analysis."""
        analysis = CortexSelfAnalysis(
            repository="CORTEX",
            analysis_type="architecture",
            findings=[{"type": "drift", "severity": "medium"}],
            recommendations=["Fix recommendation"],
            risk_areas=["orchestrators"],
            improvement_opportunities=["Add validation"],
            confidence_score=0.85,
        )

        assert analysis.repository == "CORTEX"
        assert analysis.analysis_type == "architecture"
        assert len(analysis.findings) == 1
        assert analysis.confidence_score == 0.85

    def test_analysis_confidence_bounds(self):
        """Test confidence score is in valid bounds."""
        analysis = CortexSelfAnalysis(
            repository="CORTEX",
            analysis_type="quality",
            findings=[],
            recommendations=[],
            risk_areas=[],
            improvement_opportunities=[],
            confidence_score=0.95,
        )

        assert 0.0 <= analysis.confidence_score <= 1.0


class TestArchitectureDriftDetection:
    """Tests for ArchitectureDriftDetection dataclass."""

    def test_create_drift_detection(self):
        """Test creating drift detection result."""
        drift = ArchitectureDriftDetection(
            drift_detected=True,
            drift_score=0.35,
            violations=["circular dependency"],
            affected_components=["orchestrators"],
            patterns_violated=["MCP-FIRST"],
            recommendations=["Fix issue"],
        )

        assert drift.drift_detected is True
        assert drift.drift_score == 0.35
        assert len(drift.violations) == 1

    def test_drift_score_bounds(self):
        """Test drift score is in valid bounds."""
        drift = ArchitectureDriftDetection(
            drift_detected=False,
            drift_score=0.0,
            violations=[],
            affected_components=[],
            patterns_violated=[],
            recommendations=[],
        )

        assert 0.0 <= drift.drift_score <= 1.0

    def test_drift_with_multiple_violations(self):
        """Test drift detection with multiple violations."""
        drift = ArchitectureDriftDetection(
            drift_detected=True,
            drift_score=0.45,
            violations=["violation1", "violation2", "violation3"],
            affected_components=["comp1", "comp2"],
            patterns_violated=["pattern1", "pattern2"],
            recommendations=["rec1", "rec2"],
        )

        assert len(drift.violations) == 3
        assert len(drift.affected_components) == 2
        assert len(drift.recommendations) == 2


class TestInternalPackageRecommendation:
    """Tests for InternalPackageRecommendation dataclass."""

    def test_create_recommendation(self):
        """Test creating package recommendation."""
        rec = InternalPackageRecommendation(
            package_name="logging → cortex.observability.logging",
            current_approach="Using standard Python logging",
            recommended_approach="Use cortex.observability.logging",
            benefits=["Consistency", "Integration"],
            migration_effort="low",
            security_benefit=False,
        )

        assert rec.package_name is not None
        assert rec.migration_effort == "low"
        assert rec.security_benefit is False

    def test_migration_effort_levels(self):
        """Test different migration effort levels."""
        for effort in ["low", "medium", "high"]:
            rec = InternalPackageRecommendation(
                package_name="test",
                current_approach="current",
                recommended_approach="recommended",
                benefits=[],
                migration_effort=effort,
                security_benefit=False,
            )
            assert rec.migration_effort == effort

    def test_security_benefit_flag(self):
        """Test security benefit flag."""
        rec_with_security = InternalPackageRecommendation(
            package_name="config management",
            current_approach="current",
            recommended_approach="recommended",
            benefits=["Secrets management"],
            migration_effort="medium",
            security_benefit=True,
        )

        assert rec_with_security.security_benefit is True

    def test_multiple_benefits(self):
        """Test package with multiple benefits."""
        rec = InternalPackageRecommendation(
            package_name="test",
            current_approach="current",
            recommended_approach="recommended",
            benefits=[
                "Consistency",
                "Security",
                "Performance",
                "Integration",
            ],
            migration_effort="low",
            security_benefit=True,
        )

        assert len(rec.benefits) == 4


class TestSecurityGateAnalysis:
    """Tests for SecurityGateAnalysis dataclass."""

    def test_create_security_analysis(self):
        """Test creating security analysis."""
        analysis = SecurityGateAnalysis(
            vulnerabilities_found=2,
            severity_levels={"critical": 1, "high": 1, "medium": 0, "low": 0},
            blocked_packages=["package1"],
            recommendations=["Fix critical"],
            compliance_status="critical",
        )

        assert analysis.vulnerabilities_found == 2
        assert analysis.compliance_status == "critical"
        assert len(analysis.blocked_packages) == 1

    def test_compliance_status_levels(self):
        """Test different compliance status levels."""
        for status in ["compliant", "warning", "critical"]:
            analysis = SecurityGateAnalysis(
                vulnerabilities_found=0,
                severity_levels={"critical": 0, "high": 0, "medium": 0, "low": 0},
                blocked_packages=[],
                recommendations=[],
                compliance_status=status,
            )
            assert analysis.compliance_status == status

    def test_severity_distribution(self):
        """Test severity level distribution."""
        analysis = SecurityGateAnalysis(
            vulnerabilities_found=4,
            severity_levels={"critical": 1, "high": 2, "medium": 1, "low": 0},
            blocked_packages=[],
            recommendations=[],
            compliance_status="warning",
        )

        total = sum(analysis.severity_levels.values())
        assert total == 4


class TestCortexBrainIntegrationOrchestrator:
    """Tests for CortexBrainIntegrationOrchestrator."""

    def test_initialize(self):
        """Test initializing orchestrator."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        assert orchestrator is not None
        assert orchestrator.cortex_repo_path is not None
        assert len(orchestrator.analysis_cache) == 0

    def test_analyze_cortex_architecture(self):
        """Test architecture analysis."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_cortex_architecture()

        assert isinstance(result, ArchitectureDriftDetection)
        assert isinstance(result.drift_detected, bool)
        assert 0.0 <= result.drift_score <= 1.0

    def test_analyze_cortex_architecture_returns_violations(self):
        """Test architecture analysis includes violations."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_cortex_architecture()

        # Should have violations list (may be empty)
        assert isinstance(result.violations, list)
        assert isinstance(result.affected_components, list)
        assert isinstance(result.patterns_violated, list)

    def test_analyze_internal_packages(self):
        """Test internal package analysis."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_internal_packages()

        assert isinstance(result, list)
        # Each result should be a recommendation
        for rec in result:
            assert isinstance(rec, InternalPackageRecommendation)

    def test_analyze_internal_packages_has_benefits(self):
        """Test package recommendations include benefits."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_internal_packages()

        for rec in result:
            assert len(rec.benefits) > 0
            assert rec.migration_effort in ["low", "medium", "high"]

    def test_analyze_security(self):
        """Test security analysis."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_security()

        assert isinstance(result, SecurityGateAnalysis)
        assert isinstance(result.vulnerabilities_found, int)
        assert isinstance(result.severity_levels, dict)
        assert result.compliance_status in ["compliant", "warning", "critical"]

    def test_analyze_security_severity_distribution(self):
        """Test security analysis severity distribution."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        result = orchestrator.analyze_security()

        # Should have all severity levels
        assert "critical" in result.severity_levels
        assert "high" in result.severity_levels
        assert "medium" in result.severity_levels
        assert "low" in result.severity_levels

        # Total should match vulnerabilities_found
        total = sum(result.severity_levels.values())
        assert total == result.vulnerabilities_found

    def test_generate_cortex_analysis_report(self):
        """Test comprehensive analysis report generation."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        report = orchestrator.generate_cortex_analysis_report()

        assert isinstance(report, dict)
        assert "timestamp" in report
        assert "repository" in report
        assert report["repository"] == "CORTEX"
        assert "analysis" in report
        assert "recommendations" in report

    def test_analysis_report_structure(self):
        """Test analysis report has correct structure."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        report = orchestrator.generate_cortex_analysis_report()

        analysis = report["analysis"]
        assert "architecture_drift" in analysis
        assert "internal_packages" in analysis
        assert "security" in analysis

        # Architecture section
        arch = analysis["architecture_drift"]
        assert "detected" in arch
        assert "score" in arch
        assert "violations_count" in arch
        assert "recommendations" in arch

        # Internal packages section
        packages = analysis["internal_packages"]
        assert "opportunities" in packages
        assert "high_value" in packages
        assert "security_related" in packages

        # Security section
        security = analysis["security"]
        assert "vulnerabilities" in security
        assert "severity_distribution" in security
        assert "compliance_status" in security
        assert "recommendations" in security

    def test_analysis_report_recommendations(self):
        """Test analysis report includes synthesized recommendations."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        report = orchestrator.generate_cortex_analysis_report()

        recommendations = report["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_orchestrator_api_completeness(self):
        """Test orchestrator has all required methods."""
        orchestrator = CortexBrainIntegrationOrchestrator()

        # Check public API
        assert hasattr(orchestrator, "analyze_cortex_architecture")
        assert callable(orchestrator.analyze_cortex_architecture)
        assert hasattr(orchestrator, "analyze_internal_packages")
        assert callable(orchestrator.analyze_internal_packages)
        assert hasattr(orchestrator, "analyze_security")
        assert callable(orchestrator.analyze_security)
        assert hasattr(orchestrator, "generate_cortex_analysis_report")
        assert callable(orchestrator.generate_cortex_analysis_report)

    def test_analysis_consistency_across_calls(self):
        """Test analysis is consistent across multiple calls."""
        orchestrator = CortexBrainIntegrationOrchestrator()

        report1 = orchestrator.generate_cortex_analysis_report()
        report2 = orchestrator.generate_cortex_analysis_report()

        # Results should be consistent
        assert report1["repository"] == report2["repository"]
        assert (
            report1["analysis"]["architecture_drift"]["detected"]
            == report2["analysis"]["architecture_drift"]["detected"]
        )

    def test_no_analysis_cache_pollution(self):
        """Test that analysis cache doesn't pollute results."""
        orchestrator = CortexBrainIntegrationOrchestrator()

        # Run multiple analyses
        orchestrator.analyze_cortex_architecture()
        orchestrator.analyze_internal_packages()
        orchestrator.analyze_security()

        # Cache should exist but not affect new analyses
        assert len(orchestrator.analysis_cache) == 0  # No caching by default

    def test_architecture_drift_recommendations_context_aware(self):
        """Test drift recommendations are context-aware."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        drift = orchestrator.analyze_cortex_architecture()

        # If violations exist, recommendations should address them
        if drift.violations:
            assert len(drift.recommendations) > 0

    def test_security_analysis_completeness(self):
        """Test security analysis provides complete view."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        security = orchestrator.analyze_security()

        # Should have recommendations even if no vulnerabilities
        assert isinstance(security.recommendations, list)
        if security.vulnerabilities_found == 0:
            assert any(
                "maintain" in rec.lower() or "no" in rec.lower()
                for rec in security.recommendations
            )

    def test_package_recommendations_quality(self):
        """Test package recommendations are high quality."""
        orchestrator = CortexBrainIntegrationOrchestrator()
        recommendations = orchestrator.analyze_internal_packages()

        for rec in recommendations:
            # Each recommendation should be complete
            assert rec.package_name
            assert rec.current_approach
            assert rec.recommended_approach
            assert len(rec.benefits) > 0
            assert rec.migration_effort in ["low", "medium", "high"]
