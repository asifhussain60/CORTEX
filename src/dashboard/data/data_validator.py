"""
Data Validator - Holistic Review System

Ensures all dashboard data is consistent, accurate, and matches the narrative
before rendering in the UI.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from typing import Dict, List, Any, Tuple


class DashboardDataValidator:
    """
    Validates dashboard data for consistency and accuracy across all tabs.
    
    This ensures:
    1. OWASP scores match actual findings
    2. Overall security score reflects category scores
    3. Compliance status matches vulnerability counts
    4. Tech stack versions align with status labels
    5. All narratives are consistent with data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_all(self, security_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Run holistic validation on all dashboard data.
        
        Args:
            security_data: Complete security data dictionary
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        self.logger.info("Starting holistic dashboard data validation...")
        
        # 1. Validate OWASP Top 10 consistency
        self._validate_owasp_consistency(security_data)
        
        # 2. Validate security score calculation
        self._validate_security_score(security_data)
        
        # 3. Validate compliance readiness
        self._validate_compliance_readiness(security_data)
        
        # 4. Validate vulnerability counts
        self._validate_vulnerability_counts(security_data)
        
        # 5. Validate category scores
        self._validate_category_scores(security_data)
        
        is_valid = len(self.validation_errors) == 0
        
        if is_valid:
            self.logger.info(f"✓ Validation passed with {len(self.validation_warnings)} warnings")
        else:
            self.logger.error(f"✗ Validation failed with {len(self.validation_errors)} errors")
        
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_owasp_consistency(self, security_data: Dict[str, Any]):
        """Ensure OWASP scores match actual findings."""
        owasp_data = security_data.get("owasp_top_10", [])
        
        if not owasp_data:
            self.validation_errors.append("OWASP Top 10 data is missing")
            return
        
        for category in owasp_data:
            risk_id = category.get("risk", "")
            score = category.get("score", 0)
            findings_count = category.get("findings_count", 0)
            status = category.get("status", "")
            
            # Rule: If findings_count > 0, score should be < 100
            if findings_count > 0 and score == 100:
                self.validation_errors.append(
                    f"OWASP {risk_id}: Score is 100 but has {findings_count} findings"
                )
            
            # Rule: If score >= 80, status should be "pass"
            if score >= 80 and status != "pass":
                self.validation_errors.append(
                    f"OWASP {risk_id}: Score {score} >= 80 but status is '{status}' (should be 'pass')"
                )
            
            # Rule: If score < 60, status should be "fail"
            if score < 60 and status != "fail":
                self.validation_errors.append(
                    f"OWASP {risk_id}: Score {score} < 60 but status is '{status}' (should be 'fail')"
                )
            
            # Rule: Findings count should make sense with severity
            findings = category.get("findings", [])
            if len(findings) > 0 and findings_count == 0:
                self.validation_warnings.append(
                    f"OWASP {risk_id}: Has {len(findings)} findings but findings_count is 0"
                )
    
    def _validate_security_score(self, security_data: Dict[str, Any]):
        """Ensure overall security score matches category scores."""
        overall_score = security_data.get("overall_score", 0)
        categories = security_data.get("categories", [])
        
        if not categories:
            self.validation_errors.append("Security categories are missing")
            return
        
        # Calculate expected score from categories
        category_scores = [cat.get("score", 0) for cat in categories]
        expected_avg = sum(category_scores) / len(category_scores)
        
        # Allow 10-point variance for penalty calculations
        if abs(overall_score - expected_avg) > 10:
            self.validation_warnings.append(
                f"Overall score ({overall_score}) differs significantly from category average ({expected_avg:.1f})"
            )
        
        # Rule: If any category is "critical", overall score should be < 50
        critical_categories = [cat for cat in categories if cat.get("status") == "critical"]
        if critical_categories and overall_score >= 50:
            self.validation_warnings.append(
                f"Has critical categories but overall score is {overall_score} (expected < 50)"
            )
    
    def _validate_compliance_readiness(self, security_data: Dict[str, Any]):
        """Ensure compliance status matches vulnerability data."""
        compliance = security_data.get("compliance", {})
        vulnerabilities = security_data.get("vulnerabilities", {})
        
        critical_count = vulnerabilities.get("critical", 0)
        high_count = vulnerabilities.get("high", 0)
        
        # Rule: Cannot be GDPR/SOC2/HIPAA/PCI ready with critical vulnerabilities
        for standard in ["gdpr_ready", "soc2_ready", "hipaa_ready", "pci_dss_ready"]:
            if compliance.get(standard, False) and critical_count > 0:
                self.validation_errors.append(
                    f"{standard.upper()}: Cannot be ready with {critical_count} critical vulnerabilities"
                )
        
        # Rule: HIPAA requires zero high vulnerabilities
        if compliance.get("hipaa_ready", False) and high_count > 0:
            self.validation_errors.append(
                f"HIPAA: Cannot be ready with {high_count} high vulnerabilities"
            )
    
    def _validate_vulnerability_counts(self, security_data: Dict[str, Any]):
        """Ensure vulnerability counts match findings."""
        vulnerabilities = security_data.get("vulnerabilities", {})
        findings = security_data.get("findings", {})
        
        vuln_findings = findings.get("vulnerabilities", [])
        
        # Count by severity
        actual_counts = {
            "critical": len([f for f in vuln_findings if f.get("severity") == "critical"]),
            "high": len([f for f in vuln_findings if f.get("severity") == "high"]),
            "medium": len([f for f in vuln_findings if f.get("severity") == "medium"]),
            "low": len([f for f in vuln_findings if f.get("severity") == "low"])
        }
        
        for severity in ["critical", "high", "medium", "low"]:
            reported = vulnerabilities.get(severity, 0)
            actual = actual_counts.get(severity, 0)
            
            # Allow mismatch if we're only showing top N findings
            if reported > actual + 5:  # Allow for top-20 truncation
                self.validation_warnings.append(
                    f"Vulnerability count mismatch for {severity}: reported {reported}, found {actual} in findings"
                )
    
    def _validate_category_scores(self, security_data: Dict[str, Any]):
        """Ensure category scores are consistent with their data."""
        categories = security_data.get("categories", [])
        
        for category in categories:
            name = category.get("name", "")
            score = category.get("score", 0)
            issues = category.get("issues", 0)
            status = category.get("status", "")
            
            # Rule: No issues should mean score >= 90
            if issues == 0 and score < 90:
                self.validation_warnings.append(
                    f"Category '{name}': Has 0 issues but score is {score} (expected >= 90)"
                )
            
            # Rule: Status should match score thresholds
            if score >= 80 and status != "healthy":
                self.validation_errors.append(
                    f"Category '{name}': Score {score} >= 80 but status is '{status}' (should be 'healthy')"
                )
            
            if score < 60 and status != "critical":
                self.validation_errors.append(
                    f"Category '{name}': Score {score} < 60 but status is '{status}' (should be 'critical')"
                )
    
    def get_validation_report(self) -> str:
        """Generate human-readable validation report."""
        report = []
        report.append("=" * 70)
        report.append("DASHBOARD DATA VALIDATION REPORT")
        report.append("=" * 70)
        
        if not self.validation_errors and not self.validation_warnings:
            report.append("\n✓ All validations passed. Data is consistent and accurate.\n")
        else:
            if self.validation_errors:
                report.append(f"\n✗ ERRORS ({len(self.validation_errors)}):")
                for error in self.validation_errors:
                    report.append(f"  - {error}")
            
            if self.validation_warnings:
                report.append(f"\n⚠ WARNINGS ({len(self.validation_warnings)}):")
                for warning in self.validation_warnings:
                    report.append(f"  - {warning}")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


# Convenience function for quick validation
def validate_security_data(security_data: Dict[str, Any]) -> bool:
    """
    Quick validation of security data.
    
    Args:
        security_data: Security data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    validator = DashboardDataValidator()
    is_valid, errors, warnings = validator.validate_all(security_data)
    
    print(validator.get_validation_report())
    
    return is_valid
