"""
Phase 52 S4: Documentation Generation System

Auto-generate documentation from PR review findings:
- Finding summaries
- Change reports  
- Recommendation documents
- Migration guides
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class DocumentFormat(Enum):
    """Output document formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PDF = "pdf"


class DocumentType(Enum):
    """Types of documents to generate"""
    FINDINGS_SUMMARY = "findings_summary"
    CHANGE_REPORT = "change_report"
    SECURITY_AUDIT = "security_audit"
    MIGRATION_GUIDE = "migration_guide"
    DEPLOYMENT_PLAN = "deployment_plan"
    ROLLBACK_GUIDE = "rollback_guide"


@dataclass
class ReviewFinding:
    """Individual finding from a review"""
    finding_id: str
    category: str  # "security", "performance", "code_quality", "migration"
    severity: str  # "critical", "high", "medium", "low"
    title: str
    description: str
    recommendation: str
    affected_components: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ReviewReport:
    """Complete review report"""
    pr_id: str
    repository: str
    timestamp: str
    review_type: str  # "standard", "migration", "security", "performance"
    findings: List[ReviewFinding] = field(default_factory=list)
    summary: Optional[str] = None
    recommendation: str = "COMMENT"
    confidence_score: float = 0.5
    reviewer_notes: Optional[str] = None


class DocumentBuilder:
    """Build review documents in various formats"""

    def __init__(self, format: DocumentFormat = DocumentFormat.MARKDOWN):
        self.format = format
        self.content = ""

    def build_findings_summary(self, report: ReviewReport) -> str:
        """Build findings summary document"""
        if self.format == DocumentFormat.MARKDOWN:
            return self._build_markdown_summary(report)
        elif self.format == DocumentFormat.JSON:
            return self._build_json_summary(report)
        elif self.format == DocumentFormat.HTML:
            return self._build_html_summary(report)
        return ""

    def _build_markdown_summary(self, report: ReviewReport) -> str:
        """Build markdown findings summary"""
        lines = [
            "# PR Review Report",
            f"\n## Metadata",
            f"- **PR ID**: {report.pr_id}",
            f"- **Repository**: {report.repository}",
            f"- **Review Type**: {report.review_type}",
            f"- **Timestamp**: {report.timestamp}",
            f"- **Confidence**: {report.confidence_score:.1%}",
            f"\n## Summary",
            f"{report.summary or 'No summary provided'}",
            f"\n## Findings ({len(report.findings)})",
        ]

        # Group findings by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_findings = sorted(
            report.findings,
            key=lambda f: severity_order.get(f.severity, 99)
        )

        for finding in sorted_findings:
            lines.extend([
                f"\n### {finding.severity.upper()}: {finding.title}",
                f"**Category**: {finding.category}",
                f"\n**Description**:\n{finding.description}",
                f"\n**Recommendation**:\n{finding.recommendation}",
            ])
            
            if finding.affected_components:
                lines.append(f"\n**Affected Components**: {', '.join(finding.affected_components)}")
            
            if finding.tags:
                lines.append(f"\n**Tags**: {', '.join(finding.tags)}")

        lines.extend([
            f"\n## Overall Recommendation",
            f"**Action**: {report.recommendation}",
            f"\n## Reviewer Notes",
            report.reviewer_notes or "No additional notes"
        ])

        return "\n".join(lines)

    def _build_json_summary(self, report: ReviewReport) -> str:
        """Build JSON findings summary"""
        data = {
            "pr_id": report.pr_id,
            "repository": report.repository,
            "timestamp": report.timestamp,
            "review_type": report.review_type,
            "summary": report.summary,
            "recommendation": report.recommendation,
            "confidence_score": report.confidence_score,
            "findings_count": len(report.findings),
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "category": f.category,
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "recommendation": f.recommendation,
                    "affected_components": f.affected_components,
                    "tags": f.tags
                }
                for f in report.findings
            ]
        }
        return json.dumps(data, indent=2)

    def _build_html_summary(self, report: ReviewReport) -> str:
        """Build HTML findings summary"""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><title>PR Review Report</title></head>",
            "<body>",
            f"<h1>PR Review Report: {report.pr_id}</h1>",
            f"<p><strong>Repository</strong>: {report.repository}</p>",
            f"<p><strong>Review Type</strong>: {report.review_type}</p>",
            f"<p><strong>Confidence</strong>: {report.confidence_score:.1%}</p>",
            "<h2>Summary</h2>",
            f"<p>{report.summary or 'No summary provided'}</p>",
            f"<h2>Findings ({len(report.findings)})</h2>",
        ]

        for finding in report.findings:
            html.extend([
                f"<h3>{finding.severity.upper()}: {finding.title}</h3>",
                f"<p><strong>Category</strong>: {finding.category}</p>",
                f"<p><strong>Description</strong></p>",
                f"<p>{finding.description}</p>",
                f"<p><strong>Recommendation</strong></p>",
                f"<p>{finding.recommendation}</p>",
            ])

        html.extend([
            "</body>",
            "</html>"
        ])

        return "\n".join(html)

    def build_change_report(self, report: ReviewReport, changes: Dict[str, Any]) -> str:
        """Build change analysis report"""
        if self.format == DocumentFormat.MARKDOWN:
            lines = [
                "# Change Report",
                f"\n## PR: {report.pr_id}",
            ]
            
            if "files_changed" in changes:
                lines.append(f"\n## Files Changed: {changes['files_changed']}")
            
            if "lines_added" in changes:
                lines.append(f"## Lines Added: {changes['lines_added']}")
            
            if "lines_removed" in changes:
                lines.append(f"## Lines Removed: {changes['lines_removed']}")
            
            if "affected_modules" in changes:
                lines.append(f"\n## Affected Modules")
                for module in changes["affected_modules"]:
                    lines.append(f"- {module}")
            
            return "\n".join(lines)
        
        return json.dumps(changes, indent=2)

    def build_migration_guide(self, components: List[str], steps: List[str]) -> str:
        """Build migration guide document"""
        if self.format == DocumentFormat.MARKDOWN:
            lines = [
                "# Migration Guide",
                "\n## Components Being Migrated",
            ]
            
            for component in components:
                lines.append(f"- {component}")
            
            lines.append("\n## Migration Steps")
            for i, step in enumerate(steps, 1):
                lines.append(f"{i}. {step}")
            
            return "\n".join(lines)
        
        return json.dumps({
            "components": components,
            "steps": steps
        }, indent=2)

    def build_deployment_plan(self, plan_data: Dict[str, Any]) -> str:
        """Build deployment plan document"""
        if self.format == DocumentFormat.MARKDOWN:
            lines = [
                "# Deployment Plan",
                f"\n## Pre-Deployment",
            ]
            
            if "pre_checks" in plan_data:
                for check in plan_data["pre_checks"]:
                    lines.append(f"- [ ] {check}")
            
            lines.append(f"\n## Deployment Steps")
            if "steps" in plan_data:
                for i, step in enumerate(plan_data["steps"], 1):
                    lines.append(f"{i}. {step}")
            
            lines.append(f"\n## Post-Deployment")
            if "post_checks" in plan_data:
                for check in plan_data["post_checks"]:
                    lines.append(f"- [ ] {check}")
            
            return "\n".join(lines)
        
        return json.dumps(plan_data, indent=2)


class ReportGenerator:
    """Generate complete review reports"""

    def __init__(self):
        self.generated_reports: Dict[str, ReviewReport] = {}

    def create_report(self, pr_id: str, repository: str, 
                     review_type: str = "standard") -> ReviewReport:
        """Create new review report"""
        report = ReviewReport(
            pr_id=pr_id,
            repository=repository,
            timestamp=datetime.now().isoformat(),
            review_type=review_type
        )
        self.generated_reports[pr_id] = report
        return report

    def add_finding(self, pr_id: str, finding: ReviewFinding) -> bool:
        """Add finding to report"""
        if pr_id not in self.generated_reports:
            return False
        
        self.generated_reports[pr_id].findings.append(finding)
        return True

    def finalize_report(self, pr_id: str, recommendation: str = "COMMENT",
                       confidence: float = 0.5) -> Optional[ReviewReport]:
        """Finalize and return report"""
        if pr_id not in self.generated_reports:
            return None
        
        report = self.generated_reports[pr_id]
        report.recommendation = recommendation
        report.confidence_score = confidence
        
        # Generate summary if not provided
        if not report.summary:
            critical_count = len([f for f in report.findings if f.severity == "critical"])
            high_count = len([f for f in report.findings if f.severity == "high"])
            report.summary = f"Found {len(report.findings)} issues: {critical_count} critical, {high_count} high"
        
        return report

    def export_report(self, pr_id: str, format: DocumentFormat = DocumentFormat.MARKDOWN) -> str:
        """Export report in specified format"""
        if pr_id not in self.generated_reports:
            return ""
        
        report = self.generated_reports[pr_id]
        builder = DocumentBuilder(format)
        return builder.build_findings_summary(report)

    def get_report_stats(self) -> Dict[str, Any]:
        """Get statistics about generated reports"""
        total_findings = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for report in self.generated_reports.values():
            total_findings += len(report.findings)
            for finding in report.findings:
                if finding.severity in severity_counts:
                    severity_counts[finding.severity] += 1
        
        return {
            "total_reports": len(self.generated_reports),
            "total_findings": total_findings,
            "severity_breakdown": severity_counts,
            "average_findings_per_report": total_findings / max(len(self.generated_reports), 1)
        }
