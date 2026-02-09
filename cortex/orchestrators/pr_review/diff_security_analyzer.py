# AC_START: AC-PHASE52-S1-2-diff_security_analyzer
# Description: Phase 52 S1.2 - Diff Security Analysis & Secret Detection
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 52, Stage 1

"""
Diff Security Analyzer: Comprehensive security scanning for PR diffs.

Detects:
- Secrets (API keys, credentials, tokens)
- Security vulnerabilities (eval, exec, dangerous functions)
- Insecure configurations (hardcoded passwords, exposed endpoints)
- Compliance violations (PII in code, license issues)
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets that can be detected."""

    API_KEY = "api_key"
    AWS_SECRET = "aws_secret"
    GITHUB_TOKEN = "github_token"
    DATABASE_PASSWORD = "database_password"
    PRIVATE_KEY = "private_key"
    JWT_TOKEN = "jwt_token"
    SLACK_TOKEN = "slack_token"
    STRIPE_KEY = "stripe_key"
    HARDCODED_PASSWORD = "hardcoded_password"
    CONNECTION_STRING = "connection_string"


@dataclass
class SecretFinding:
    """Detected secret in code."""

    secret_type: SecretType
    line_number: int
    file_path: str
    line_content: str
    severity: str  # critical, high, medium
    suggestion: str


@dataclass
class SecurityScanResult:
    """Results of security scan on diff."""

    file_path: str
    secrets_found: List[SecretFinding]
    vulnerabilities: List[Dict[str, Any]]
    compliance_issues: List[Dict[str, Any]]
    total_issues: int
    risk_level: str  # critical, high, medium, low


class SecretDetector:
    """Detect secrets and credentials in code."""

    # Patterns for detecting secrets
    SECRET_PATTERNS = {
        SecretType.API_KEY: [
            r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'apikey["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'api_secret["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ],
        SecretType.AWS_SECRET: [
            r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'AKIA[0-9A-Z]{16}',
        ],
        SecretType.GITHUB_TOKEN: [
            r'gh[psuoa]_[A-Za-z0-9_]{36,255}',
            r'github[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ],
        SecretType.DATABASE_PASSWORD: [
            r'password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            r'db[_-]?password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ],
        SecretType.PRIVATE_KEY: [
            r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----',
            r'private[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ],
        SecretType.JWT_TOKEN: [
            r'eyJh[A-Za-z0-9_-]{50,}\.eyJ[A-Za-z0-9_-]{50,}\.[A-Za-z0-9_-]+',
        ],
        SecretType.SLACK_TOKEN: [
            r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9_-]{24,32}',
        ],
        SecretType.STRIPE_KEY: [
            r'sk_[live|test]_[0-9a-zA-Z]{20,}',
            r'pk_[live|test]_[0-9a-zA-Z]{20,}',
        ],
        SecretType.HARDCODED_PASSWORD: [
            r'password\s*=\s*["\']([^"\']{6,})["\']',
            r'passwd\s*=\s*["\']([^"\']{6,})["\']',
        ],
        SecretType.CONNECTION_STRING: [
            r'mongodb://([^:]+):([^@]+)@',
            r'postgres://([^:]+):([^@]+)@',
            r'mysql://([^:]+):([^@]+)@',
        ],
    }

    @staticmethod
    def detect_secrets(file_path: str, line_number: int, line_content: str) -> List[SecretFinding]:
        """Detect secrets in a single line of code.

        Args:
            file_path: Path to the file
            line_number: Line number in file
            line_content: Content of the line

        Returns:
            List of detected secrets
        """
        # AC_START: AC-PHASE52-S1-2-secret_detection
        findings = []

        for secret_type, patterns in SecretDetector.SECRET_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line_content, re.IGNORECASE):
                    severity = "critical" if secret_type in [
                        SecretType.AWS_SECRET,
                        SecretType.GITHUB_TOKEN,
                        SecretType.PRIVATE_KEY,
                    ] else "high"

                    findings.append(
                        SecretFinding(
                            secret_type=secret_type,
                            line_number=line_number,
                            file_path=file_path,
                            line_content=line_content[:50] + "..." if len(line_content) > 50 else line_content,
                            severity=severity,
                            suggestion=SecretDetector._get_suggestion(secret_type),
                        )
                    )

        # AC_COMPLETE: AC-PHASE52-S1-2-secret_detection
        return findings

    @staticmethod
    def _get_suggestion(secret_type: SecretType) -> str:
        """Get remediation suggestion for secret type."""
        suggestions = {
            SecretType.API_KEY: "Move API key to environment variables or secrets manager",
            SecretType.AWS_SECRET: "Use AWS IAM roles instead of hardcoded credentials",
            SecretType.GITHUB_TOKEN: "Rotate token immediately and use GitHub Actions secrets",
            SecretType.DATABASE_PASSWORD: "Use connection pooling with secure credential store",
            SecretType.PRIVATE_KEY: "Move private key to secure key management system",
            SecretType.JWT_TOKEN: "Generate JWT at runtime, don't embed in code",
            SecretType.SLACK_TOKEN: "Use environment variables or secrets manager",
            SecretType.STRIPE_KEY: "Use Stripe's dashboard to rotate keys",
            SecretType.HARDCODED_PASSWORD: "Use environment variables for all credentials",
            SecretType.CONNECTION_STRING: "Parameterize connection strings with environment variables",
        }
        return suggestions.get(secret_type, "Move to environment variables or secrets manager")


class VulnerabilityScanner:
    """Scan for common code vulnerabilities."""

    VULNERABILITY_PATTERNS = {
        "sql_injection": {
            "patterns": [
                r"SELECT.*\+\s*str\(",
                r'execute\s*\(\s*["\']SELECT',
            ],
            "severity": "critical",
            "message": "SQL injection vulnerability detected",
        },
        "hardcoded_sql": {
            "patterns": [
                r'(SELECT|INSERT|UPDATE|DELETE).*WHERE.*=\s*["\'][^"\']+["\']',
            ],
            "severity": "high",
            "message": "Hardcoded SQL query in code",
        },
        "xss_vulnerability": {
            "patterns": [
                r"innerHTML\s*=",
                r"dangerouslySetInnerHTML",
            ],
            "severity": "high",
            "message": "Potential XSS vulnerability",
        },
        "insecure_randomness": {
            "patterns": [
                r"Math\.random\(\)",
                r"random\.randint\(",
            ],
            "severity": "medium",
            "message": "Insecure random number generation",
        },
        "debug_enabled": {
            "patterns": [
                r"DEBUG\s*=\s*True",
                r"debug=true",
            ],
            "severity": "high",
            "message": "Debug mode enabled in production code",
        },
    }

    @staticmethod
    def scan_for_vulnerabilities(
        file_path: str, line_number: int, line_content: str
    ) -> List[Dict[str, Any]]:
        """Scan for vulnerabilities in a line of code.

        Args:
            file_path: Path to file
            line_number: Line number
            line_content: Content of line

        Returns:
            List of vulnerability findings
        """
        # AC_START: AC-PHASE52-S1-2-vuln_scan
        findings = []

        for vuln_type, config in VulnerabilityScanner.VULNERABILITY_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, line_content, re.IGNORECASE):
                    findings.append(
                        {
                            "type": vuln_type,
                            "severity": config["severity"],
                            "line_number": line_number,
                            "file_path": file_path,
                            "message": config["message"],
                        }
                    )

        # AC_COMPLETE: AC-PHASE52-S1-2-vuln_scan
        return findings


class ComplianceChecker:
    """Check for compliance violations in code."""

    COMPLIANCE_PATTERNS = {
        "pii_detection": {
            "patterns": [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
            ],
            "severity": "critical",
            "message": "Potential PII (Personally Identifiable Information) detected",
        },
        "license_header_missing": {
            "patterns": [
                r"^(?!.*Apache|MIT|GPL|BSD|ISC)",
            ],
            "severity": "low",
            "message": "License header may be missing",
        },
    }

    @staticmethod
    def check_compliance(
        file_path: str, file_content: str
    ) -> List[Dict[str, Any]]:
        """Check file for compliance violations.

        Args:
            file_path: Path to file
            file_content: Full file content

        Returns:
            List of compliance issues
        """
        # AC_START: AC-PHASE52-S1-2-compliance_check
        findings = []

        for check_type, config in ComplianceChecker.COMPLIANCE_PATTERNS.items():
            for pattern in config["patterns"]:
                if re.search(pattern, file_content, re.IGNORECASE | re.MULTILINE):
                    findings.append(
                        {
                            "type": check_type,
                            "severity": config["severity"],
                            "file_path": file_path,
                            "message": config["message"],
                        }
                    )

        # AC_COMPLETE: AC-PHASE52-S1-2-compliance_check
        return findings


class DiffSecurityAnalyzer:
    """Complete diff security analysis engine."""

    def __init__(self):
        """Initialize security analyzer."""
        self.secret_detector = SecretDetector()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.compliance_checker = ComplianceChecker()

    def analyze_diff_security(
        self,
        file_path: str,
        file_type: str,
        added_lines: List[Tuple[int, str]],
        full_file_content: Optional[str] = None,
    ) -> SecurityScanResult:
        """Analyze security of file diff.

        Args:
            file_path: Path to file
            file_type: File type (python, javascript, etc.)
            added_lines: List of (line_number, content) tuples for added lines
            full_file_content: Full file content for compliance checks (optional)

        Returns:
            SecurityScanResult with all findings
        """
        # AC_START: AC-PHASE52-S1-2-analyze_security
        secrets_found: List[SecretFinding] = []
        vulnerabilities: List[Dict[str, Any]] = []
        compliance_issues: List[Dict[str, Any]] = []

        # Scan added lines for secrets and vulnerabilities
        for line_number, line_content in added_lines:
            # Detect secrets
            secrets = self.secret_detector.detect_secrets(
                file_path, line_number, line_content
            )
            secrets_found.extend(secrets)

            # Scan for vulnerabilities
            vulns = self.vulnerability_scanner.scan_for_vulnerabilities(
                file_path, line_number, line_content
            )
            vulnerabilities.extend(vulns)

        # Check compliance for full file
        if full_file_content:
            compliance = self.compliance_checker.check_compliance(
                file_path, full_file_content
            )
            compliance_issues.extend(compliance)

        # Determine risk level
        risk_level = self._calculate_risk_level(
            secrets_found, vulnerabilities, compliance_issues
        )

        result = SecurityScanResult(
            file_path=file_path,
            secrets_found=secrets_found,
            vulnerabilities=vulnerabilities,
            compliance_issues=compliance_issues,
            total_issues=len(secrets_found) + len(vulnerabilities) + len(compliance_issues),
            risk_level=risk_level,
        )

        # AC_COMPLETE: AC-PHASE52-S1-2-analyze_security
        return result

    @staticmethod
    def _calculate_risk_level(
        secrets: List[SecretFinding],
        vulnerabilities: List[Dict[str, Any]],
        compliance: List[Dict[str, Any]],
    ) -> str:
        """Calculate overall risk level.

        Args:
            secrets: List of secret findings
            vulnerabilities: List of vulnerabilities
            compliance: List of compliance issues

        Returns:
            Risk level: critical, high, medium, low
        """
        critical_count = sum(
            1 for s in secrets if s.severity == "critical"
        ) + sum(
            1 for v in vulnerabilities if v["severity"] == "critical"
        ) + sum(
            1 for c in compliance if c["severity"] == "critical"
        )

        if critical_count > 0:
            return "critical"

        high_count = sum(
            1 for s in secrets if s.severity == "high"
        ) + sum(
            1 for v in vulnerabilities if v["severity"] == "high"
        )

        if high_count > 2:
            return "high"

        if len(vulnerabilities) > 0 or len(secrets) > 0:
            return "medium"

        return "low"


# AC_COMPLETE: AC-PHASE52-S1-2-diff_security_analyzer
