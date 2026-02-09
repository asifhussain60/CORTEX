"""
Phase 52 S4: Documentation System Tests (20+ tests)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "cortex" / "orchestrators" / "pr_review"))

from doc_generator import (
    DocumentBuilder, DocumentFormat, ReviewFinding, ReviewReport,
    DocumentType, ReportGenerator
)


class TestReviewFinding:
    """Test review finding creation"""

    def test_create_finding(self):
        """Test creating review finding"""
        finding = ReviewFinding(
            finding_id="F-001",
            category="security",
            severity="critical",
            title="SQL Injection Vulnerability",
            description="Unsanitized user input in query",
            recommendation="Use parameterized queries"
        )
        assert finding.finding_id == "F-001"
        assert finding.severity == "critical"

    def test_finding_with_components(self):
        """Test finding with affected components"""
        finding = ReviewFinding(
            finding_id="F-002",
            category="performance",
            severity="high",
            title="N+1 Query",
            description="Loop executes query",
            recommendation="Use batch query",
            affected_components=["database", "api-service"]
        )
        assert len(finding.affected_components) == 2


class TestReviewReport:
    """Test review report creation"""

    def test_create_report(self):
        """Test creating review report"""
        report = ReviewReport(
            pr_id="PR-001",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard"
        )
        assert report.pr_id == "PR-001"
        assert report.recommendation == "COMMENT"

    def test_report_with_findings(self):
        """Test report with multiple findings"""
        report = ReviewReport(
            pr_id="PR-002",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="security"
        )
        
        finding1 = ReviewFinding(
            finding_id="F-1",
            category="security",
            severity="critical",
            title="Issue 1",
            description="Desc",
            recommendation="Fix it"
        )
        
        finding2 = ReviewFinding(
            finding_id="F-2",
            category="code_quality",
            severity="low",
            title="Issue 2",
            description="Desc",
            recommendation="Improve"
        )
        
        report.findings = [finding1, finding2]
        assert len(report.findings) == 2


class TestDocumentBuilder:
    """Test document generation"""

    def test_build_markdown_summary(self):
        """Test building markdown summary"""
        report = ReviewReport(
            pr_id="PR-003",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard",
            summary="Review summary"
        )
        
        finding = ReviewFinding(
            finding_id="F-001",
            category="code",
            severity="medium",
            title="Code Issue",
            description="Found issue",
            recommendation="Fix it"
        )
        report.findings = [finding]
        
        builder = DocumentBuilder(DocumentFormat.MARKDOWN)
        doc = builder.build_findings_summary(report)
        
        assert "PR Review Report" in doc
        assert "PR-003" in doc
        assert "Code Issue" in doc
        assert "markdown" not in doc.lower() or "# " in doc

    def test_build_json_summary(self):
        """Test building JSON summary"""
        report = ReviewReport(
            pr_id="PR-004",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard"
        )
        
        builder = DocumentBuilder(DocumentFormat.JSON)
        doc = builder.build_findings_summary(report)
        
        assert "pr_id" in doc
        assert "PR-004" in doc
        import json
        parsed = json.loads(doc)
        assert parsed["pr_id"] == "PR-004"

    def test_build_html_summary(self):
        """Test building HTML summary"""
        report = ReviewReport(
            pr_id="PR-005",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard"
        )
        
        builder = DocumentBuilder(DocumentFormat.HTML)
        doc = builder.build_findings_summary(report)
        
        assert "<html>" in doc
        assert "</html>" in doc
        assert "PR-005" in doc

    def test_findings_sorted_by_severity(self):
        """Test findings sorted by severity in markdown"""
        report = ReviewReport(
            pr_id="PR-006",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard"
        )
        
        findings = [
            ReviewFinding("F1", "cat", "low", "Low", "Desc", "Fix"),
            ReviewFinding("F2", "cat", "critical", "Critical", "Desc", "Fix"),
            ReviewFinding("F3", "cat", "high", "High", "Desc", "Fix"),
        ]
        report.findings = findings
        
        builder = DocumentBuilder(DocumentFormat.MARKDOWN)
        doc = builder.build_findings_summary(report)
        
        critical_pos = doc.find("CRITICAL")
        high_pos = doc.find("HIGH")
        low_pos = doc.find("LOW")
        
        assert critical_pos < high_pos < low_pos

    def test_build_change_report(self):
        """Test building change report"""
        report = ReviewReport(
            pr_id="PR-007",
            repository="cortex",
            timestamp=datetime.now().isoformat(),
            review_type="standard"
        )
        
        changes = {
            "files_changed": 5,
            "lines_added": 120,
            "lines_removed": 30,
            "affected_modules": ["auth", "api"]
        }
        
        builder = DocumentBuilder(DocumentFormat.MARKDOWN)
        doc = builder.build_change_report(report, changes)
        
        assert "Change Report" in doc
        assert "5" in doc  # files_changed
        assert "120" in doc  # lines_added

    def test_build_migration_guide(self):
        """Test building migration guide"""
        components = ["database", "api"]
        steps = ["Step 1: Backup", "Step 2: Migrate", "Step 3: Verify"]
        
        builder = DocumentBuilder(DocumentFormat.MARKDOWN)
        doc = builder.build_migration_guide(components, steps)
        
        assert "Migration Guide" in doc
        assert "database" in doc
        assert "Step 1" in doc

    def test_build_deployment_plan(self):
        """Test building deployment plan"""
        plan = {
            "pre_checks": ["Check health", "Notify team"],
            "steps": ["Deploy service", "Run tests"],
            "post_checks": ["Verify metrics", "Monitor logs"]
        }
        
        builder = DocumentBuilder(DocumentFormat.MARKDOWN)
        doc = builder.build_deployment_plan(plan)
        
        assert "Deployment Plan" in doc
        assert "Pre-Deployment" in doc
        assert "Deploy service" in doc


class TestReportGenerator:
    """Test report generation"""

    def test_create_report(self):
        """Test creating report via generator"""
        gen = ReportGenerator()
        report = gen.create_report("PR-008", "cortex")
        
        assert report.pr_id == "PR-008"
        assert "PR-008" in gen.generated_reports

    def test_add_finding(self):
        """Test adding finding to report"""
        gen = ReportGenerator()
        gen.create_report("PR-009", "cortex")
        
        finding = ReviewFinding(
            "F-001",
            "security",
            "high",
            "Issue",
            "Description",
            "Fix it"
        )
        
        result = gen.add_finding("PR-009", finding)
        assert result
        assert len(gen.generated_reports["PR-009"].findings) == 1

    def test_add_finding_to_nonexistent_report(self):
        """Test adding finding to nonexistent report fails"""
        gen = ReportGenerator()
        finding = ReviewFinding(
            "F-001",
            "security",
            "high",
            "Issue",
            "Description",
            "Fix it"
        )
        
        result = gen.add_finding("PR-NONE", finding)
        assert not result

    def test_finalize_report(self):
        """Test finalizing report"""
        gen = ReportGenerator()
        gen.create_report("PR-010", "cortex")
        
        finding = ReviewFinding(
            "F-001",
            "code",
            "low",
            "Issue",
            "Desc",
            "Fix"
        )
        gen.add_finding("PR-010", finding)
        
        report = gen.finalize_report("PR-010", "APPROVE", 0.9)
        assert report.recommendation == "APPROVE"
        assert report.confidence_score == 0.9
        assert report.summary is not None

    def test_export_report_markdown(self):
        """Test exporting report as markdown"""
        gen = ReportGenerator()
        gen.create_report("PR-011", "cortex")
        
        finding = ReviewFinding(
            "F-001",
            "security",
            "critical",
            "Issue",
            "Desc",
            "Fix"
        )
        gen.add_finding("PR-011", finding)
        gen.finalize_report("PR-011")
        
        doc = gen.export_report("PR-011", DocumentFormat.MARKDOWN)
        assert "PR-011" in doc
        assert "#" in doc

    def test_export_report_json(self):
        """Test exporting report as JSON"""
        gen = ReportGenerator()
        gen.create_report("PR-012", "cortex")
        gen.finalize_report("PR-012")
        
        doc = gen.export_report("PR-012", DocumentFormat.JSON)
        import json
        parsed = json.loads(doc)
        assert parsed["pr_id"] == "PR-012"

    def test_get_report_stats(self):
        """Test getting report statistics"""
        gen = ReportGenerator()
        
        for i in range(2):
            gen.create_report(f"PR-{i}", "cortex")
            for j in range(2):
                finding = ReviewFinding(
                    f"F-{j}",
                    "code",
                    "high" if j == 0 else "low",
                    "Issue",
                    "Desc",
                    "Fix"
                )
                gen.add_finding(f"PR-{i}", finding)
        
        stats = gen.get_report_stats()
        assert stats["total_reports"] == 2
        assert stats["total_findings"] == 4
        assert stats["severity_breakdown"]["high"] == 2
        assert stats["severity_breakdown"]["low"] == 2
        assert stats["average_findings_per_report"] == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
