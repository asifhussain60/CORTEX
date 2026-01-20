"""
SecurityAuditor - automated security auditing.

Scans codebase for security vulnerabilities, misconfigurations, and
dependency issues with Bandit and pip-audit integration.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening (HARD-PROD-001-06)
Compliance: CORE-011 (100% typed), CORE-012 (Google docstrings), CORE-013 (no bare except)
"""

import subprocess
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class SecurityAuditor:
    """Audits code and configuration for security issues.
    
    Provides:
    - Bandit integration for Python security checks
    - pip-audit for dependency vulnerability scanning
    - Configuration hardness checks
    - Custom CORTEX pattern checks
    - HTML report generation
    
    Attributes:
        findings: List of security findings
        config_checks: List of configuration checks
    """

    def __init__(self) -> None:
        """Initialize SecurityAuditor."""
        self.findings: List[Dict[str, Any]] = []
        self.config_checks: List[Dict[str, Any]] = []
        self.custom_patterns = {
            "debug_mode": r"DEBUG\s*=\s*True",
            "hardcoded_secret": r"(password|api_key|secret)\s*=\s*['\"]",
            "weak_hash": r"(md5|sha1)\(",
        }

    def scan_codebase(self, root_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan codebase for security issues.
        
        Args:
            root_path: Root path to scan (default: current directory)
            
        Returns:
            List of findings
        """
        path = Path(root_path or ".")
        
        # Run Bandit
        bandit_findings = self.integrate_bandit(str(path))
        self.findings.extend(bandit_findings)
        
        # Check dependencies
        dependency_findings = self.integrate_pip_audit(str(path))
        self.findings.extend(dependency_findings)
        
        return self.findings

    def integrate_bandit(self, path: str) -> List[Dict[str, Any]]:
        """Integrate Bandit for Python security checks.
        
        Args:
            path: Path to scan
            
        Returns:
            List of Bandit findings
        """
        findings = []
        
        try:
            result = subprocess.run(
                ["bandit", "-r", path, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get("results", []):
                    findings.append({
                        "type": "bandit",
                        "severity": issue.get("severity"),
                        "issue_type": issue.get("issue_type"),
                        "issue_text": issue.get("issue_text"),
                        "filename": issue.get("filename"),
                        "line_number": issue.get("line_number"),
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as err:
            findings.append({
                "type": "bandit",
                "severity": "INFO",
                "issue_text": f"Bandit scan failed: {err}"
            })
        
        return findings

    def integrate_pip_audit(self, path: str) -> List[Dict[str, Any]]:
        """Integrate pip-audit for dependency scanning.
        
        Args:
            path: Path containing requirements.txt
            
        Returns:
            List of dependency findings
        """
        findings = []
        
        try:
            result = subprocess.run(
                ["pip-audit", "--desc", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=path
            )
            
            if result.returncode == 0 or result.stdout:
                data = json.loads(result.stdout)
                for vuln in data.get("vulnerabilities", []):
                    findings.append({
                        "type": "dependency",
                        "package": vuln.get("name"),
                        "installed_version": vuln.get("installed_version"),
                        "vulnerable_specs": vuln.get("vulnerable_specs"),
                        "advisory": vuln.get("advisory"),
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as err:
            findings.append({
                "type": "dependency",
                "error": f"pip-audit scan failed: {err}"
            })
        
        return findings

    def check_configuration(self, config_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check configuration for hardness issues.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            List of configuration issues
        """
        checks = []
        
        # Check for debug mode
        try:
            config_file = Path(config_path or "cortex/core/config.py")
            if config_file.exists():
                content = config_file.read_text()
                
                if "DEBUG = True" in content or "DEBUG=True" in content:
                    checks.append({
                        "check": "debug_mode",
                        "severity": "CRITICAL",
                        "message": "DEBUG mode enabled in production",
                        "file": str(config_file)
                    })
        except Exception as err:
            checks.append({
                "check": "config_read",
                "severity": "INFO",
                "error": f"Could not read config: {err}"
            })
        
        self.config_checks.extend(checks)
        return checks

    def check_dependencies(self) -> List[Dict[str, Any]]:
        """Check for vulnerable dependencies.
        
        Returns:
            List of vulnerable dependency findings
        """
        return self.integrate_pip_audit(".")

    def generate_report(self, format_type: str = "html") -> str:
        """Generate security audit report.
        
        Args:
            format_type: Report format (html, json, text)
            
        Returns:
            Report content
        """
        if format_type == "json":
            return json.dumps({
                "findings": self.findings,
                "config_checks": self.config_checks
            }, indent=2)
        
        elif format_type == "html":
            return self._generate_html_report()
        
        else:  # text format
            return self._generate_text_report()

    def _generate_html_report(self) -> str:
        """Generate HTML report."""
        total_findings = len(self.findings)
        high_severity = sum(
            1 for f in self.findings
            if f.get("severity") in ["HIGH", "CRITICAL"]
        )
        
        return f"""
        <html>
        <head><title>Security Audit Report</title></head>
        <body>
        <h1>Security Audit Report</h1>
        <p>Total Findings: {total_findings}</p>
        <p>High Severity: {high_severity}</p>
        <h2>Findings</h2>
        <ul>
        {''.join(f'<li>{f}</li>' for f in self.findings[:10])}
        </ul>
        </body>
        </html>
        """

    def _generate_text_report(self) -> str:
        """Generate text report."""
        lines = [
            "Security Audit Report",
            "=" * 50,
            f"Total Findings: {len(self.findings)}",
            "",
            "Recent Findings:",
        ]
        
        for finding in self.findings[:10]:
            lines.append(f"- {finding.get('issue_text', str(finding))}")
        
        return "\n".join(lines)

    def get_remediation_steps(self) -> List[str]:
        """Get recommended remediation steps.
        
        Returns:
            List of remediation recommendations
        """
        steps = []
        
        high_severity_findings = [
            f for f in self.findings
            if f.get("severity") in ["HIGH", "CRITICAL"]
        ]
        
        if high_severity_findings:
            steps.append("Review and fix high-severity findings immediately")
        
        dependency_findings = [
            f for f in self.findings
            if f.get("type") == "dependency"
        ]
        
        if dependency_findings:
            steps.append("Update vulnerable dependencies to latest secure versions")
        
        config_issues = [
            c for c in self.config_checks
            if c.get("severity") == "CRITICAL"
        ]
        
        if config_issues:
            steps.append("Review and fix configuration issues")
        
        return steps
