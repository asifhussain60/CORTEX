"""
Security-first analysis enhancement for proactive threat detection.
Detects P0-P2 security issues and integrates with challenge engine.

Module: cortex.orchestrators.core.security_first_analyzer
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

# ============================================================================
# ENUMERATIONS
# ============================================================================


class SeverityLevel(str, Enum):
    """Security severity level."""

    P0_BLOCKER = "P0_BLOCKER"
    """Critical vulnerability - hard gate, blocks execution"""

    P1_WARNING = "P1_WARNING"
    """High severity - included in challenge"""

    P2_ADVISORY = "P2_ADVISORY"
    """Medium severity - included in synthesis"""


# ============================================================================
# CWE PATTERNS
# ============================================================================


class CWEPattern:
    """CWE pattern for detection."""

    def __init__(self, cwe_id: str, description: str, patterns: List[str]):
        self.cwe_id = cwe_id
        self.description = description
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    def matches(self, code: str) -> bool:
        """Check if code matches pattern."""
        return any(p.search(code) for p in self.patterns)


# ============================================================================
# SECURITY THREAT DATABASE
# ============================================================================


CWE_DATABASE = {
    # P0: Blockers
    "CWE-94": CWEPattern(
        "CWE-94",
        "Code Injection",
        [
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"__import__",
        ]
    ),
    "CWE-89": CWEPattern(
        "CWE-89",
        "SQL Injection",
        [
            r"query\s*=\s*['\"].*\{.*\}.*['\"]",
            r"sql\s*\+\s*",
            r"\.format\(.*user.*\)",
            r"f['\"].*SELECT.*\{",
        ]
    ),
    "CWE-22": CWEPattern(
        "CWE-22",
        "Path Traversal",
        [
            r"open\s*\(\s*user_path",
            r"os\.path\.join\(.*user",
            r"\.\.",
        ]
    ),
    "CWE-78": CWEPattern(
        "CWE-78",
        "OS Command Injection",
        [
            r"os\.system\s*\(",
            r"subprocess.*shell\s*=\s*True",
            r"popen\s*\(",
        ]
    ),
    # P1: Warnings
    "CWE-327": CWEPattern(
        "CWE-327",
        "Inadequate Encryption",
        [
            r"md5\s*\(",
            r"sha1\s*\(",
            r"DES",
            r"RC4",
        ]
    ),
    "CWE-502": CWEPattern(
        "CWE-502",
        "Deserialization of Untrusted Data",
        [
            r"pickle\.load\s*\(",
            r"yaml\.load\s*\(",
            r"json\.load\s*\(",
        ]
    ),
}


P0_CWES = {"CWE-94", "CWE-89", "CWE-22", "CWE-78"}
P1_CWES = {"CWE-327", "CWE-502"}
P2_CWES = set()  # Additional P2 checks defined dynamically


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class SecurityFinding:
    """A security finding."""

    cwe_id: str
    description: str
    severity: SeverityLevel
    location: str
    remediation: str
    context: str = ""


@dataclass
class SecurityAnalysis:
    """Complete security analysis result."""

    p0_findings: List[SecurityFinding] = field(default_factory=list)
    p1_findings: List[SecurityFinding] = field(default_factory=list)
    p2_findings: List[SecurityFinding] = field(default_factory=list)

    has_blockers: bool = False
    owasp_coverage: float = 0.0

    @property
    def all_findings(self) -> List[SecurityFinding]:
        """Get all findings."""
        return self.p0_findings + self.p1_findings + self.p2_findings

    @property
    def total_findings(self) -> int:
        """Get total finding count."""
        return len(self.all_findings)


# ============================================================================
# SECURITY FIRST ANALYZER
# ============================================================================


class SecurityFirstAnalyzer:
    """Proactive security threat detector."""

    def __init__(self):
        self.cwe_db = CWE_DATABASE

    def analyze(self, code: str, file_path: str = "unknown") -> SecurityAnalysis:
        """
        Analyze code for security threats.

        Args:
            code: Source code to analyze
            file_path: File path for context

        Returns:
            SecurityAnalysis with findings
        """
        analysis = SecurityAnalysis()

        # Check for P0 blockers
        for cwe_id in P0_CWES:
            if cwe_id in self.cwe_db:
                if self.cwe_db[cwe_id].matches(code):
                    analysis.p0_findings.append(SecurityFinding(
                        cwe_id=cwe_id,
                        description=self.cwe_db[cwe_id].description,
                        severity=SeverityLevel.P0_BLOCKER,
                        location=file_path,
                        remediation=self._get_remediation(cwe_id),
                        context=self._extract_context(code, cwe_id)
                    ))
                    analysis.has_blockers = True

        # Check for P1 warnings
        for cwe_id in P1_CWES:
            if cwe_id in self.cwe_db:
                if self.cwe_db[cwe_id].matches(code):
                    analysis.p1_findings.append(SecurityFinding(
                        cwe_id=cwe_id,
                        description=self.cwe_db[cwe_id].description,
                        severity=SeverityLevel.P1_WARNING,
                        location=file_path,
                        remediation=self._get_remediation(cwe_id),
                        context=self._extract_context(code, cwe_id)
                    ))

        # Calculate OWASP coverage
        analysis.owasp_coverage = self._calculate_owasp_coverage(analysis)

        return analysis

    def _get_remediation(self, cwe_id: str) -> str:
        """Get remediation steps for CWE."""
        remediations = {
            "CWE-94": "Avoid eval(), exec(), compile(). Use safer alternatives like ast.literal_eval().",
            "CWE-89": "Use parameterized queries. Never concatenate user input into SQL.",
            "CWE-22": "Validate and sanitize file paths. Use os.path.normpath() + whitelist.",
            "CWE-78": "Avoid os.system(). Use subprocess with shell=False.",
            "CWE-327": "Use bcrypt, scrypt, or PBKDF2 for hashing. AES-256 for encryption.",
            "CWE-502": "Avoid pickle. Use JSON with schema validation instead.",
        }
        return remediations.get(cwe_id, "Review security best practices.")

    def _extract_context(self, code: str, cwe_id: str) -> str:
        """Extract context around vulnerable code."""
        if cwe_id not in self.cwe_db:
            return ""

        for line in code.split('\n'):
            if self.cwe_db[cwe_id].matches(line):
                return line.strip()[:100]

        return ""

    def _calculate_owasp_coverage(self, analysis: SecurityAnalysis) -> float:
        """Calculate OWASP Top 10 coverage percentage."""
        # Simplified: checks 6 key OWASP items
        checks = {
            "Injection": any(f.cwe_id in {"CWE-89", "CWE-78"} for f in analysis.all_findings),
            "Broken Auth": False,
            "Sensitive Data": any(f.cwe_id in {"CWE-327"} for f in analysis.all_findings),
            "XXE": False,
            "Broken Access": False,
            "Security Misconfiguration": any(f.cwe_id in {"CWE-502"} for f in analysis.all_findings),
        }
        return len([v for v in checks.values() if v]) / len(checks) * 100


# ============================================================================
# SURROUNDING CONTEXT ANALYZER
# ============================================================================


class SurroundingContextAnalyzer:
    """Analyzes surrounding context for security issues."""

    def __init__(self, analyzer: SecurityFirstAnalyzer):
        self.analyzer = analyzer

    def find_related_issues(
        self,
        primary_finding: SecurityFinding,
        codebase_files: Dict[str, str]
    ) -> List[SecurityFinding]:
        """
        Find related security issues in other files.

        Args:
            primary_finding: Primary finding to search for related issues
            codebase_files: Dictionary of file_path -> code

        Returns:
            List of related findings
        """
        related = []

        for file_path, code in codebase_files.items():
            if file_path != primary_finding.location:
                analysis = self.analyzer.analyze(code, file_path)
                for finding in analysis.all_findings:
                    if finding.cwe_id == primary_finding.cwe_id:
                        related.append(finding)

        return related


# ============================================================================
# OWASP COVERAGE REPORTER
# ============================================================================


class OWASPCoverageReport:
    """OWASP Top 10 coverage analysis."""

    OWASP_ITEMS = [
        ("A01:2021", "Broken Access Control", ["CWE-22", "CWE-639"]),
        ("A02:2021", "Cryptographic Failures", ["CWE-327", "CWE-521"]),
        ("A03:2021", "Injection", ["CWE-89", "CWE-78", "CWE-94"]),
        ("A04:2021", "Insecure Design", ["CWE-434"]),
        ("A05:2021", "Security Misconfiguration", ["CWE-16"]),
        ("A06:2021", "Vulnerable Components", ["CWE-1035"]),
        ("A07:2021", "Authentication Failures", ["CWE-307", "CWE-384"]),
        ("A08:2021", "Software Data Integrity Failures", ["CWE-502"]),
        ("A09:2021", "Logging Monitoring Failures", ["CWE-778"]),
        ("A10:2021", "SSRF", ["CWE-918"]),
    ]

    @staticmethod
    def generate_report(analysis: SecurityAnalysis) -> Dict[str, object]:
        """Generate OWASP coverage report."""
        findings_cwes = {f.cwe_id for f in analysis.all_findings}

        coverage = {}
        for item_id, item_name, cwes in OWASPCoverageReport.OWASP_ITEMS:
            matched = any(cwe in findings_cwes for cwe in cwes)
            coverage[item_id] = {
                "name": item_name,
                "checked": matched,
                "cwes": cwes,
            }

        covered_items = sum(1 for v in coverage.values() if v["checked"])
        coverage_percent = (covered_items / len(coverage)) * 100

        return {
            "coverage_percent": coverage_percent,
            "covered_items": covered_items,
            "total_items": len(coverage),
            "items": coverage,
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "SeverityLevel",
    "SecurityFinding",
    "SecurityAnalysis",
    "SecurityFirstAnalyzer",
    "SurroundingContextAnalyzer",
    "OWASPCoverageReport",
    "CWE_DATABASE",
]
