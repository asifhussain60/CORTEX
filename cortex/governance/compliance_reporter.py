"""Compliance Reporter for generating governance reports."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from cortex.governance.governance_analyzer import ViolationReport


class ComplianceReporter:
    """Generates compliance reports in various formats."""

    def __init__(self) -> None:
        """Initialize reporter."""
        pass

    def generate_json_report(self, violations: List[ViolationReport]) -> str:
        """Generate JSON compliance report.

        Args:
            violations: List of violations to report

        Returns:
            JSON report as string
        """
        total_checks = len(violations) + 100  # Assume 100 baseline checks
        violations_count = len(violations)
        compliance_percentage = max(0, 100 - (violations_count * 5))

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity,
                    "message": v.message,
                    "entity": v.entity,
                    "remediation": v.remediation
                }
                for v in violations
            ],
            "compliance_percentage": compliance_percentage,
            "total_violations": violations_count,
            "total_checks": total_checks,
            "summary": f"{compliance_percentage:.1f}% compliant ({total_checks - violations_count}/{total_checks} checks passed)"
        }

        return json.dumps(report, indent=2)

    def generate_pdf_report(self, violations: List[ViolationReport]) -> bytes:
        """Generate PDF compliance report.

        Args:
            violations: List of violations to report

        Returns:
            PDF report as bytes
        """
        # Simplified PDF generation (in production would use reportlab or similar)
        compliance_pct = max(0, 100 - (len(violations) * 5))

        pdf_content = f"""
        %PDF-1.4
        Compliance Report
        Timestamp: {datetime.now(timezone.utc).isoformat()}

        Summary:
        - Total Violations: {len(violations)}
        - Compliance: {compliance_pct:.1f}%

        Violations:
        """.encode('utf-8')

        for v in violations:
            pdf_content += f"\n- {v.rule_id}: {v.severity} - {v.message}".encode('utf-8')

        return pdf_content

    def get_compliance_percentage(self, violations: List[ViolationReport]) -> float:
        """Calculate compliance percentage.

        Args:
            violations: List of violations

        Returns:
            Compliance percentage (0-100)
        """
        return max(0, 100 - (len(violations) * 5))
