"""
Intelligence Documentation Generator

Purpose: Auto-generates intelligence reports for test coverage, TDD compliance,
validation results, and manifest compliance.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 4)

Responsibilities:
- Generate test coverage reports (Markdown)
- Generate TDD compliance reports
- Generate validation result reports
- Generate manifest compliance reports
- Generate aggregated intelligence reports
- Support multiple output formats (Markdown, HTML, JSON)

Integration Points:
- Intelligence Orchestrator: Consumes intelligence reports
- Planning System: Documentation for plan reviews
- cortex-brain/documents/reports/: Report storage

Week 9 Target: 300 LOC
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .intelligence_orchestrator import IntelligenceReport, IntelligenceMode

logger = logging.getLogger(__name__)


class DocumentFormat(str):
    """Documentation output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class IntelligenceDocumentationGenerator:
    """
    Generates documentation from intelligence reports.
    
    Creates human-readable reports for test coverage, TDD compliance,
    validation results, and manifest compliance.
    
    Usage:
        generator = IntelligenceDocumentationGenerator(
            output_dir=Path("cortex-brain/documents/reports/intelligence")
        )
        
        # Generate full report
        report_path = generator.generate_full_report(
            intelligence_report,
            plan_name="feature-authentication"
        )
    """
    
    def __init__(
        self,
        output_dir: Path,
        format: str = DocumentFormat.MARKDOWN
    ):
        """
        Initialize documentation generator.
        
        Args:
            output_dir: Directory for generated reports
            format: Output format (markdown, html, json)
        """
        self.output_dir = Path(output_dir)
        self.format = format
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    # ========== Full Report Generation ==========
    
    def generate_full_report(
        self,
        intelligence_report: IntelligenceReport,
        plan_name: str,
        include_recommendations: bool = True
    ) -> Path:
        """
        Generate comprehensive intelligence report.
        
        Args:
            intelligence_report: Intelligence analysis results
            plan_name: Plan name for report filename
            include_recommendations: Include recommendations section
            
        Returns:
            Path to generated report
        """
        self.logger.info(f"Generating intelligence report for: {plan_name}")
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"intelligence-report-{plan_name}-{timestamp}.md"
        output_path = self.output_dir / filename
        
        # Generate report content
        content = self._generate_markdown_report(
            intelligence_report,
            plan_name,
            include_recommendations
        )
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(content)
        
        self.logger.info(f"Report generated: {output_path}")
        return output_path
    
    def _generate_markdown_report(
        self,
        report: IntelligenceReport,
        plan_name: str,
        include_recommendations: bool
    ) -> str:
        """Generate Markdown report content."""
        lines = []
        
        # Header
        lines.append(f"# Intelligence Report: {plan_name}")
        lines.append("")
        lines.append(f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Mode:** {report.mode.value}")
        lines.append(f"**Overall Score:** {report.overall_score:.1f}%")
        lines.append(f"**Status:** {report.get_summary()}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## 📊 Executive Summary")
        lines.append("")
        if report.is_ready_for_execution():
            lines.append("✅ **Plan is ready for execution**")
        else:
            lines.append("❌ **Plan has blocking issues**")
        lines.append("")
        
        if report.blocking_issues:
            lines.append(f"- **Blocking Issues:** {len(report.blocking_issues)}")
        if report.warnings:
            lines.append(f"- **Warnings:** {len(report.warnings)}")
        if include_recommendations and report.recommendations:
            lines.append(f"- **Recommendations:** {len(report.recommendations)}")
        lines.append("")
        
        # Blocking Issues
        if report.blocking_issues:
            lines.append("### 🚫 Blocking Issues")
            lines.append("")
            for issue in report.blocking_issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Test Intelligence Section
        if report.test_coverage_analysis:
            lines.extend(self._generate_test_intelligence_section(report))
        
        # TDD Intelligence Section
        if report.tdd_workflow_status:
            lines.extend(self._generate_tdd_intelligence_section(report))
        
        # Validation Section
        if report.validation_report:
            lines.extend(self._generate_validation_section(report))
        
        # Manifest Compliance Section
        if report.compliance_report:
            lines.extend(self._generate_compliance_section(report))
        
        # Recommendations
        if include_recommendations and report.recommendations:
            lines.append("## 💡 Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        # Warnings
        if report.warnings:
            lines.append("## ⚠️ Warnings")
            lines.append("")
            for warning in report.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        return "\n".join(lines)
    
    # ========== Section Generators ==========
    
    def _generate_test_intelligence_section(self, report: IntelligenceReport) -> List[str]:
        """Generate test intelligence section."""
        lines = []
        coverage = report.test_coverage_analysis
        
        lines.append("## 🧪 Test Intelligence")
        lines.append("")
        lines.append(f"**Overall Coverage:** {coverage.overall_coverage:.1f}%")
        lines.append(f"**Total Files:** {coverage.total_files}")
        lines.append(f"**Test Files:** {coverage.test_files}")
        lines.append("")
        
        # Coverage by type
        lines.append("### Coverage by Type")
        lines.append("")
        lines.append(f"- **Unit Tests:** {coverage.unit_test_coverage:.1f}%")
        lines.append(f"- **Integration Tests:** {coverage.integration_test_coverage:.1f}%")
        lines.append(f"- **E2E Tests:** {coverage.e2e_test_coverage:.1f}%")
        lines.append("")
        
        # Test distribution
        if coverage.test_distribution:
            lines.append("### Test Distribution")
            lines.append("")
            dist = coverage.test_distribution
            lines.append(f"- Unit: {dist.get('unit', 0)} tests")
            lines.append(f"- Integration: {dist.get('integration', 0)} tests")
            lines.append(f"- E2E: {dist.get('e2e', 0)} tests")
            lines.append("")
        
        # Critical gaps
        if report.test_gaps:
            lines.append("### Critical Test Gaps")
            lines.append("")
            for gap in report.test_gaps[:5]:  # Top 5
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(gap.severity, "⚪")
                lines.append(f"- {severity_emoji} **{gap.module_name}** ({gap.severity})")
                lines.append(f"  - {gap.reason}")
            lines.append("")
        
        # Test strategy
        if report.test_strategy:
            lines.append("### Recommended Test Strategy")
            lines.append("")
            strategy = report.test_strategy
            if "approach" in strategy:
                lines.append(f"**Approach:** {strategy['approach']}")
                lines.append("")
            if "priorities" in strategy:
                lines.append("**Priorities:**")
                for priority in strategy["priorities"]:
                    lines.append(f"- {priority}")
                lines.append("")
        
        return lines
    
    def _generate_tdd_intelligence_section(self, report: IntelligenceReport) -> List[str]:
        """Generate TDD intelligence section."""
        lines = []
        
        lines.append("## 🔴🟢♻️ TDD Intelligence")
        lines.append("")
        
        status = report.tdd_workflow_status
        if status["valid"]:
            lines.append("✅ **TDD Workflow Valid**")
        else:
            lines.append("❌ **TDD Workflow Issues**")
        
        lines.append(f"**Quality Score:** {report.tdd_quality_score:.1f}/10")
        lines.append("")
        
        # Errors
        if status.get("errors"):
            lines.append("### Issues")
            lines.append("")
            for error in status["errors"]:
                lines.append(f"- {error}")
            lines.append("")
        
        # Recommendations
        if report.tdd_recommendations:
            lines.append("### TDD Recommendations")
            lines.append("")
            for rec in report.tdd_recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return lines
    
    def _generate_validation_section(self, report: IntelligenceReport) -> List[str]:
        """Generate validation section."""
        lines = []
        
        lines.append("## ✅ Validation Results")
        lines.append("")
        
        validation = report.validation_report
        lines.append(validation.get_summary())
        lines.append("")
        
        if validation.errors > 0:
            lines.append(f"**Errors:** {validation.errors}")
        if validation.warnings > 0:
            lines.append(f"**Warnings:** {validation.warnings}")
        if validation.infos > 0:
            lines.append(f"**Infos:** {validation.infos}")
        lines.append("")
        
        # Blocking errors detail
        blocking = validation.get_blocking_errors()
        if blocking:
            lines.append("### Blocking Errors")
            lines.append("")
            for error in blocking:
                lines.append(f"- **{error.field_path}:** {error.message}")
                if error.suggestion:
                    lines.append(f"  - Suggestion: {error.suggestion}")
            lines.append("")
        
        return lines
    
    def _generate_compliance_section(self, report: IntelligenceReport) -> List[str]:
        """Generate manifest compliance section."""
        lines = []
        
        lines.append("## 📋 Manifest Compliance")
        lines.append("")
        
        compliance = report.compliance_report
        lines.append(compliance.get_summary())
        lines.append("")
        
        lines.append(f"**DoR Compliance:** {compliance.dor_compliance:.0f}%")
        lines.append(f"**DoD Compliance:** {compliance.dod_compliance:.0f}%")
        lines.append(f"**Overall Score:** {compliance.overall_score:.0f}%")
        lines.append("")
        
        # Violations by severity
        if compliance.critical_violations > 0:
            lines.append(f"- **Critical Violations:** {compliance.critical_violations}")
        if compliance.major_violations > 0:
            lines.append(f"- **Major Violations:** {compliance.major_violations}")
        if compliance.minor_violations > 0:
            lines.append(f"- **Minor Violations:** {compliance.minor_violations}")
        lines.append("")
        
        # Critical violations detail
        critical = compliance.get_critical_violations()
        if critical:
            lines.append("### Critical Violations")
            lines.append("")
            for violation in critical:
                lines.append(f"- **{violation.requirement}:** {violation.message}")
                if violation.suggestion:
                    lines.append(f"  - Suggestion: {violation.suggestion}")
            lines.append("")
        
        return lines
    
    # ========== Quick Reports ==========
    
    def generate_coverage_report(
        self,
        intelligence_report: IntelligenceReport,
        filename: str = "coverage-report.md"
    ) -> Path:
        """Generate test coverage report only."""
        output_path = self.output_dir / filename
        
        lines = []
        lines.append("# Test Coverage Report")
        lines.append("")
        lines.extend(self._generate_test_intelligence_section(intelligence_report))
        
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
        
        return output_path
    
    def generate_tdd_report(
        self,
        intelligence_report: IntelligenceReport,
        filename: str = "tdd-compliance-report.md"
    ) -> Path:
        """Generate TDD compliance report only."""
        output_path = self.output_dir / filename
        
        lines = []
        lines.append("# TDD Compliance Report")
        lines.append("")
        lines.extend(self._generate_tdd_intelligence_section(intelligence_report))
        
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
        
        return output_path
    
    def generate_json_export(
        self,
        intelligence_report: IntelligenceReport,
        filename: str = "intelligence-report.json"
    ) -> Path:
        """Export intelligence report as JSON."""
        output_path = self.output_dir / filename
        
        # Convert report to dict (excluding non-serializable objects)
        report_dict = {
            "timestamp": intelligence_report.timestamp.isoformat(),
            "mode": intelligence_report.mode.value,
            "overall_score": intelligence_report.overall_score,
            "execution_approved": intelligence_report.execution_approved,
            "blocking_issues": intelligence_report.blocking_issues,
            "warnings": intelligence_report.warnings,
            "recommendations": intelligence_report.recommendations,
            "tdd_quality_score": intelligence_report.tdd_quality_score,
            "validation_passed": intelligence_report.validation_passed,
            "compliance_level": intelligence_report.compliance_level.value if intelligence_report.compliance_level else None
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        return output_path
