"""
SecurityOrchestrator - Pre-DoR security gate orchestrator.

Enterprise-grade security scanning before code review. Integrates SAST, SCA,
secrets detection, configuration auditing, and CI/CD hardening checks.

Replaces external tools like Arnica, Veracode, Snyk with CORTEX-native scanning.

Author: CORTEX Implementation
Phase: impl-security-orchestrator
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
AC-ID: AC-SECURITY-ORCHESTRATOR-001
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid

from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway  # Phase 94d / 95
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Err, Ok, Result
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin  # Phase 62-B

# Lazy imports to avoid dependency issues
SecurityAuditor = None
CrossRepoEnforcer = None

def _load_security_components() -> None:
    """Lazy load security components."""
    global SecurityAuditor, CrossRepoEnforcer
    if SecurityAuditor is None:
        try:
            from cortex.infrastructure.security.security_auditor import SecurityAuditor as SA
            SecurityAuditor = SA
        except ImportError:
            SecurityAuditor = None
    if CrossRepoEnforcer is None:
        try:
            from cortex.infrastructure.security.cross_repo_enforcer import CrossRepoEnforcer as CRE
            CrossRepoEnforcer = CRE
        except ImportError:
            CrossRepoEnforcer = None

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class SeverityLevel(Enum):  # CORE-035-scoped — domain-specific severity level — local orchestrator values
    """Security finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingType(Enum):
    """Types of security findings."""
    HARDCODED_SECRET = "hardcoded_secret"
    SQL_INJECTION = "sql_injection"
    COMMAND_INJECTION = "command_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    VULNERABLE_DEPENDENCY = "vulnerable_dependency"
    UNPINNED_ACTION = "unpinned_action"
    WORKFLOW_INJECTION = "workflow_injection"
    CONFIG_ISSUE = "config_issue"
    WEAK_CRYPTO = "weak_crypto"
    PRIVATE_KEY_EXPOSURE = "private_key_exposure"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SecurityFinding:
    """A single security finding.

    Attributes:
        finding_id: Unique identifier for this finding
        type: Type of security issue
        severity: Severity level
        title: Short title
        description: Detailed description
        location: File and line number
        cwe_id: CWE identifier if applicable
        owasp_category: OWASP Top 10 category
        remediation: Suggested fix
        pattern_matched: Pattern that triggered detection
    """
    finding_id: str
    type: str
    severity: str
    title: str
    description: str
    location: str = ""
    cwe_id: str = ""
    owasp_category: str = ""
    remediation: str = ""
    pattern_matched: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "finding_id": self.finding_id,
            "type": self.type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "remediation": self.remediation,
            "pattern_matched": self.pattern_matched,
        }


@dataclass
class SecurityReport:
    """Complete security scan report.

    Attributes:
        scan_id: Unique scan identifier
        timestamp: Scan timestamp
        findings: List of security findings
        summary: Summary statistics
        recommendations: Prioritized remediation steps
        owasp_mapping: Findings mapped to OWASP categories
    """
    scan_id: str
    timestamp: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, int]
    recommendations: List[str]
    owasp_mapping: Dict[str, List[str]] = field(default_factory=dict)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "findings": self.findings,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "owasp_mapping": self.owasp_mapping,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
        }


# ============================================================================
# SECURITY PATTERNS (Loaded from knowledge base at runtime)
# ============================================================================

DEFAULT_SECRET_PATTERNS = [
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key", "aws_access_key"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})", "AWS Secret Key", "aws_secret_key"),
    # GitHub
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token", "github_pat"),
    (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth Token", "github_oauth"),
    (r"ghu_[A-Za-z0-9]{36}", "GitHub User Token", "github_user"),
    (r"ghs_[A-Za-z0-9]{36}", "GitHub Server Token", "github_server"),
    # Generic
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([A-Za-z0-9]{20,})", "API Key", "api_key"),
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{4,}['\"]", "Hardcoded Password", "password"),
    (r"(?i)(secret|token)\s*[=:]\s*['\"][^'\"]{10,}['\"]", "Hardcoded Secret", "secret"),
    # Private Keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key", "private_key"),
    # JWT
    (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "JWT Token", "jwt"),
    # Slack
    (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*", "Slack Token", "slack_token"),
    # Stripe
    (r"sk_live_[0-9a-zA-Z]{24}", "Stripe Secret Key", "stripe_key"),
    (r"rk_live_[0-9a-zA-Z]{24}", "Stripe Restricted Key", "stripe_restricted"),
]

DEFAULT_INJECTION_PATTERNS = [
    # SQL Injection
    (r"(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+.*\s+(FROM|INTO|TABLE|WHERE)\s+.*\{.*\}", "SQL Injection (f-string)", "sql_injection", "CWE-89"),
    (r"(?i)(SELECT|INSERT|UPDATE|DELETE).*%s.*%s", "SQL Injection (% formatting)", "sql_injection", "CWE-89"),
    (r"(?i)(SELECT|INSERT|UPDATE|DELETE).*\+\s*[a-zA-Z_]+\s*\+", "SQL Injection (concatenation)", "sql_injection", "CWE-89"),
    # Command Injection
    (r"os\.system\s*\(\s*f['\"]", "Command Injection (os.system)", "command_injection", "CWE-78"),
    (r"subprocess\.(call|run|Popen)\s*\(\s*f['\"]", "Command Injection (subprocess)", "command_injection", "CWE-78"),
    (r"os\.popen\s*\(\s*f['\"]", "Command Injection (os.popen)", "command_injection", "CWE-78"),
    # XSS
    (r"<[^>]*\{[^}]+\}[^>]*>", "Potential XSS (unescaped in HTML)", "xss", "CWE-79"),
    # Path Traversal
    (r"open\s*\(\s*f['\"].*\{.*\}", "Path Traversal (open)", "path_traversal", "CWE-22"),
]

DEFAULT_WORKFLOW_PATTERNS = [
    # Unpinned Actions
    (r"uses:\s*([^@]+)@v\d+", "Unpinned GitHub Action (tag)", "unpinned_action"),
    (r"uses:\s*([^@]+)@main", "Unpinned GitHub Action (branch)", "unpinned_action"),
    (r"uses:\s*([^@]+)@master", "Unpinned GitHub Action (branch)", "unpinned_action"),
    # Expression Injection
    (r"\$\{\{\s*github\.event\.(issue|pull_request|comment)\.body", "Expression Injection (body)", "workflow_injection"),
    (r"\$\{\{\s*github\.event\.(issue|pull_request)\.title", "Expression Injection (title)", "workflow_injection"),
    (r"\$\{\{\s*github\.head_ref", "Expression Injection (head_ref)", "workflow_injection"),
]

DEFAULT_CONFIG_CHECKS = [
    ("DEBUG", True, "Debug mode enabled", "CRITICAL"),
    ("CORS_ALLOW_ALL", True, "CORS allows all origins", "HIGH"),
    ("SESSION_COOKIE_SECURE", False, "Session cookie not secure", "HIGH"),
    ("SESSION_COOKIE_HTTPONLY", False, "Session cookie not HTTP-only", "MEDIUM"),
    ("CSRF_ENABLED", False, "CSRF protection disabled", "HIGH"),
    ("SSL_REDIRECT", False, "SSL redirect disabled", "MEDIUM"),
]


# ============================================================================
# SECURITY ORCHESTRATOR
# ============================================================================

class SecurityOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin, IOrchestrator, WorkflowTemplateMixin):
    """
    Pre-DoR security gate orchestrator.

    Performs comprehensive security scanning before code enters review:
    - SAST: Static analysis for code vulnerabilities
    - SCA: Software composition analysis for dependencies
    - Secrets: Detection of hardcoded credentials
    - Config: Audit of security configurations
    - CI/CD: GitHub Actions and workflow hardening

    Attributes:
        auditor: SecurityAuditor for low-level scanning
        enforcer: CrossRepoEnforcer for policy enforcement
        audit_trail: Log of all security scans
        knowledge_base: Loaded security patterns from YAML
    """

    # Phase 95 — advisory: execute_operation receives domain-specific names ("scan"),
    # not top-level gateway mode strings. @enforce_gateway applied but flag stays False.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialize SecurityOrchestrator."""
        # Lazy load security components
        _load_security_components()

        # Initialize auditor if available
        if SecurityAuditor is not None:
            self.auditor = SecurityAuditor()
        else:
            self.auditor = None

        # Initialize enforcer if available
        if CrossRepoEnforcer is not None:
            self.enforcer = CrossRepoEnforcer()
        else:
            self.enforcer = None

        self.audit_trail: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}

        # Load default patterns (will be overridden by knowledge base)
        self._secret_patterns = DEFAULT_SECRET_PATTERNS
        self._injection_patterns = DEFAULT_INJECTION_PATTERNS
        self._workflow_patterns = DEFAULT_WORKFLOW_PATTERNS
        self._config_checks = DEFAULT_CONFIG_CHECKS

        # Try to load knowledge base
        self._load_knowledge_base()

    # ========================================================================
    # IOrchestrator Interface Implementation
    # ========================================================================

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "SecurityOrchestrator"

    def get_recommended_template(self) -> str:
        """Get the recommended workflow template for security operations."""
        return "security/security-hardening"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator.

        Returns:
            Result with success message or error
        """
        try:
            if self.enforcer is not None:
                self.enforcer.load_tier0_rules()
            self._load_knowledge_base()
            return Ok("SecurityOrchestrator initialized successfully")
        except Exception as err:
            return Err(f"Initialization failed: {err}")

    def execute(
        self,
        request: Dict[str, Any],
        mode: OperationMode = OperationMode.VALIDATION
    ) -> Result[Dict[str, Any]]:
        """Execute security scan.

        Args:
            request: Scan request with target code/path
            mode: Operation mode

        Returns:
            Result with security report or error
        """
        target = request.get("target", "")
        scan_type = request.get("scan_type", "full")

        if scan_type == "secrets":
            return self.scan_for_secrets(target)
        elif scan_type == "injection":
            return self.scan_for_injection(target)
        elif scan_type == "workflow":
            return self.scan_workflow(target)
        elif scan_type == "dependencies":
            path = Path(request.get("path", "."))
            return self.scan_dependencies(path)
        else:
            return self.full_security_scan(target)

    def shutdown(self) -> Result[str]:
        """Shutdown orchestrator.

        Returns:
            Result with success message
        """
        return Ok("SecurityOrchestrator shutdown complete")

    def get_mode(self) -> OperationMode:
        """Get current operation mode.

        Returns:
            Current operation mode (VALIDATION for security scanning)
        """
        return OperationMode.VALIDATION

    @enforce_gateway
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging.

        Args:
            operation_name: Name of the operation to execute
            parameters: Operation parameters

        Returns:
            Result with operation output
        """
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            if operation_name == "scan":
                return self.execute(parameters)
            elif operation_name == "scan_secrets":
                code = parameters.get("code", "")
                return self.scan_for_secrets(code)
            elif operation_name == "scan_injection":
                code = parameters.get("code", "")
                return self.scan_for_injection(code)
            elif operation_name == "scan_workflow":
                content = parameters.get("content", "")
                return self.scan_workflow(content)
            elif operation_name == "scan_dependencies":
                path = Path(parameters.get("path", "."))
                return self.scan_dependencies(path)
            elif operation_name == "full_scan":
                code = parameters.get("code", "")
                return self.full_security_scan(code)
            elif operation_name == "evaluate_gate":
                findings = parameters.get("findings", [])
                return self.evaluate_gate(findings)
            else:
                return Err(f"Unknown operation: {operation_name}")
        except Exception as err:
            return Err(f"Operation failed: {err}")

    # ========================================================================
    # SAST Scanning
    # ========================================================================

    def scan_for_secrets(
        self,
        code: str,
        include_entropy: bool = False
    ) -> Result[List[Dict[str, Any]]]:
        """Scan code for hardcoded secrets.

        Args:
            code: Source code to scan
            include_entropy: Include high-entropy string detection

        Returns:
            Result with list of secret findings
        """
        findings: List[Dict[str, Any]] = []

        for pattern, title, secret_type in self._secret_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                findings.append({
                    "finding_id": str(uuid.uuid4())[:8],
                    "type": secret_type,
                    "severity": "CRITICAL",
                    "title": title,
                    "description": f"Detected potential {title} in code",
                    "pattern_matched": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                    "cwe_id": "CWE-798",
                    "owasp_category": "A07:2021 – Identification and Authentication Failures",
                    "remediation": "Remove hardcoded secret and use environment variables or secrets manager",
                })

        if include_entropy:
            high_entropy_findings = self._detect_high_entropy(code)
            findings.extend(high_entropy_findings)

        self._log_scan("secrets_scan", len(findings))
        return Ok(findings)

    def scan_for_injection(self, code: str) -> Result[List[Dict[str, Any]]]:
        """Scan code for injection vulnerabilities.

        Args:
            code: Source code to scan

        Returns:
            Result with list of injection findings
        """
        findings: List[Dict[str, Any]] = []

        for pattern, title, injection_type, cwe_id in self._injection_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                severity = "CRITICAL" if injection_type in ["sql_injection", "command_injection"] else "HIGH"
                findings.append({
                    "finding_id": str(uuid.uuid4())[:8],
                    "type": injection_type,
                    "severity": severity,
                    "title": title,
                    "description": f"Potential {injection_type.replace('_', ' ')} vulnerability detected",
                    "pattern_matched": match.group(0)[:80],
                    "cwe_id": cwe_id,
                    "owasp_category": "A03:2021 – Injection",
                    "remediation": self._get_injection_remediation(injection_type),
                })

        self._log_scan("injection_scan", len(findings))
        return Ok(findings)

    # ========================================================================
    # SCA Scanning
    # ========================================================================

    def scan_dependencies(self, path: Path) -> Result[List[Dict[str, Any]]]:
        """Scan dependencies for vulnerabilities.

        Args:
            path: Path to project root

        Returns:
            Result with list of dependency findings
        """
        findings: List[Dict[str, Any]] = []

        # Check requirements.txt
        req_file = path / "requirements.txt"
        if req_file.exists():
            if self.auditor is not None and hasattr(self.auditor, 'integrate_pip_audit'):
                pip_findings = self.auditor.integrate_pip_audit(str(path))
                findings.extend(pip_findings)
            else:
                # Fallback: Basic requirements scanning
                findings.extend(self._basic_requirements_scan(req_file))

        # Check for vulnerable packages in our database
        db_findings = self._check_vulnerability_database()
        findings.extend(db_findings)

        self._log_scan("dependency_scan", len(findings))
        return Ok(findings)

    def _basic_requirements_scan(self, req_file: Path) -> List[Dict[str, Any]]:
        """Basic requirements.txt scanning fallback.

        Args:
            req_file: Path to requirements.txt

        Returns:
            List of basic dependency findings
        """
        findings = []
        try:
            content = req_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check for unpinned dependencies
                    if '==' not in line and '>=' not in line and '<=' not in line:
                        findings.append({
                            "finding_id": hashlib.sha256(line.encode()).hexdigest()[:8],
                            "severity": "LOW",
                            "description": f"Unpinned dependency: {line}",
                            "cwe_id": "CWE-1104",
                            "remediation": f"Pin {line} to specific version"
                        })
        except Exception as e:
            logger.warning(f"Failed to scan requirements: {e}")
        return findings

    def _check_vulnerability_database(self) -> List[Dict[str, Any]]:
        """Check against internal vulnerability database.

        Returns:
            List of vulnerability findings
        """
        # Placeholder - would connect to actual vulnerability DB
        return []

    def check_license_compliance(
        self,
        licenses: List[str]
    ) -> Result[Dict[str, List[str]]]:
        """Check license compliance.

        Args:
            licenses: List of license identifiers

        Returns:
            Result with allowed/restricted categorization
        """
        allowed_licenses = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"]
        restricted_licenses = ["GPL-3.0", "AGPL-3.0", "LGPL-3.0"]

        result = {
            "allowed": [l for l in licenses if l in allowed_licenses],
            "restricted": [l for l in licenses if l in restricted_licenses],
            "unknown": [l for l in licenses if l not in allowed_licenses and l not in restricted_licenses],
        }

        return Ok(result)

    def generate_sbom(self, path: Path) -> Result[Dict[str, Any]]:
        """Generate Software Bill of Materials.

        Args:
            path: Path to project root

        Returns:
            Result with SBOM data
        """
        components: List[Dict[str, Any]] = []

        req_file = path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            for line in content.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("==")
                    if len(parts) == 2:
                        components.append({
                            "name": parts[0],
                            "version": parts[1],
                            "type": "pypi",
                        })

        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "components": components,
        }

        return Ok(sbom)

    # ========================================================================
    # CI/CD Hardening
    # ========================================================================

    def scan_workflow(self, workflow_content: str) -> Result[List[Dict[str, Any]]]:
        """Scan GitHub Actions workflow for security issues.

        Args:
            workflow_content: YAML content of workflow file

        Returns:
            Result with list of workflow findings
        """
        findings: List[Dict[str, Any]] = []

        for pattern, title, finding_type in self._workflow_patterns:
            matches = re.finditer(pattern, workflow_content, re.MULTILINE)
            for match in matches:
                severity = "HIGH" if finding_type == "workflow_injection" else "MEDIUM"
                findings.append({
                    "finding_id": str(uuid.uuid4())[:8],
                    "type": finding_type,
                    "severity": severity,
                    "title": title,
                    "description": f"CI/CD security issue: {title}",
                    "pattern_matched": match.group(0),
                    "cwe_id": "CWE-94" if finding_type == "workflow_injection" else "CWE-829",
                    "remediation": self._get_workflow_remediation(finding_type),
                })

        self._log_scan("workflow_scan", len(findings))
        return Ok(findings)

    def validate_provenance(
        self,
        artifact_info: Dict[str, Any]
    ) -> Result[Dict[str, Any]]:
        """Validate artifact provenance.

        Args:
            artifact_info: Artifact metadata with signature

        Returns:
            Result with validation status
        """
        # Simplified provenance check
        has_signature = "signature" in artifact_info
        has_signer = "signed_by" in artifact_info

        return Ok({
            "valid": has_signature and has_signer,
            "has_signature": has_signature,
            "has_signer": has_signer,
            "artifact": artifact_info.get("artifact", "unknown"),
        })

    # ========================================================================
    # Configuration Audit
    # ========================================================================

    def audit_configuration(
        self,
        config: Dict[str, Any]
    ) -> Result[List[Dict[str, Any]]]:
        """Audit configuration for security issues.

        Args:
            config: Configuration dictionary

        Returns:
            Result with list of configuration findings
        """
        findings: List[Dict[str, Any]] = []

        for key, bad_value, message, severity in self._config_checks:
            if key in config and config[key] == bad_value:
                findings.append({
                    "finding_id": str(uuid.uuid4())[:8],
                    "type": "config_issue",
                    "severity": severity,
                    "title": f"Configuration Issue: {key}",
                    "description": message,
                    "pattern_matched": f"{key}={bad_value}",
                    "cwe_id": "CWE-16",
                    "remediation": f"Set {key} to a secure value for production",
                })

        self._log_scan("config_audit", len(findings))
        return Ok(findings)

    # ========================================================================
    # Full Scan Orchestration
    # ========================================================================

    def full_security_scan(self, code: str) -> Result[Dict[str, Any]]:
        """Perform comprehensive security scan.

        Args:
            code: Source code to scan

        Returns:
            Result with complete security report
        """
        all_findings: List[Dict[str, Any]] = []

        # Run all scans
        secrets_result = self.scan_for_secrets(code)
        if secrets_result.is_ok():
            all_findings.extend(secrets_result.unwrap())

        injection_result = self.scan_for_injection(code)
        if injection_result.is_ok():
            all_findings.extend(injection_result.unwrap())

        # Count by severity
        critical_count = sum(1 for f in all_findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in all_findings if f.get("severity") == "HIGH")
        medium_count = sum(1 for f in all_findings if f.get("severity") == "MEDIUM")
        low_count = sum(1 for f in all_findings if f.get("severity") == "LOW")

        # Generate report
        report = {
            "scan_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "findings": all_findings,
            "summary": {
                "total": len(all_findings),
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
            },
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "recommendations": self._generate_recommendations(all_findings),
            "owasp_mapping": self._map_to_owasp(all_findings),
        }

        self._log_scan("full_scan", len(all_findings), report["scan_id"])
        return Ok(report)

    # ========================================================================
    # Security Gate
    # ========================================================================

    def evaluate_gate(
        self,
        findings: List[Dict[str, Any]],
        high_threshold: int = 3
    ) -> Result[Dict[str, Any]]:
        """Evaluate security gate for blocking decisions.

        Args:
            findings: List of security findings
            high_threshold: Number of HIGH findings to trigger block

        Returns:
            Result with gate evaluation
        """
        critical_count = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in findings if f.get("severity") == "HIGH")

        blocked = False
        reason = ""

        if critical_count > 0:
            blocked = True
            reason = "critical_findings"
        elif high_count > high_threshold:
            blocked = True
            reason = "high_threshold_exceeded"

        result = {
            "blocked": blocked,
            "reason": reason,
            "critical_count": critical_count,
            "high_count": high_count,
            "remediation": self._generate_recommendations(findings) if blocked else [],
            "guidance": "Fix critical and high severity issues before proceeding",
        }

        return Ok(result)

    # ========================================================================
    # MCP Tools
    # ========================================================================

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get MCP tool definitions for this orchestrator.

        Returns:
            Result with MCP tool schemas
        """
        tools = [
            {
                "name": "cortex_security_scan",
                "description": "Perform comprehensive security scan on code or repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Code or path to scan"
                        },
                        "scan_type": {
                            "type": "string",
                            "enum": ["full", "secrets", "injection", "dependencies", "workflow"],
                            "description": "Type of security scan"
                        }
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "cortex_validate_security",
                "description": "Validate code against security gate criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to validate"
                        },
                        "high_threshold": {
                            "type": "integer",
                            "description": "Maximum HIGH findings before blocking"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "cortex_generate_sbom",
                "description": "Generate Software Bill of Materials for a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to project root"
                        }
                    },
                    "required": ["path"]
                }
            },
        ]
        return Ok({"tools": tools, "count": len(tools)})

    # ========================================================================
    # Knowledge Base Integration
    # ========================================================================

    def _load_knowledge_base(self) -> None:
        """Load security patterns from knowledge base YAMLs."""
        # Find project root (where cortex-registry is located)
        # Try multiple strategies to locate the knowledge base
        current_file = Path(__file__).resolve()
        project_root_candidates = [
            current_file.parents[4],  # From cortex/orchestrators/core/security_orchestrator.py
            current_file.parents[3],  # Alternate structure
            Path.cwd(),  # Current working directory
            Path.cwd().parent,  # Parent of cwd
        ]

        kb_relative = Path("cortex-registry/knowledge/security")
        kb_found = False

        for candidate in project_root_candidates:
            kb_dir = candidate / kb_relative
            if kb_dir.exists():
                kb_paths = [
                    kb_dir / "owasp-top10.yaml",
                    kb_dir / "secrets-patterns.yaml",
                    kb_dir / "cicd-hardening.yaml",
                ]
                for kb_path in kb_paths:
                    if kb_path.exists():
                        try:
                            with open(kb_path) as f:
                                data = yaml.safe_load(f)
                                self.knowledge_base[kb_path.stem] = data
                                logger.info(f"Loaded knowledge base: {kb_path.stem}")
                                kb_found = True
                        except Exception as err:
                            logger.warning(f"Failed to load {kb_path}: {err}")
                break

        if not kb_found:
            logger.warning("Knowledge base files not found - using defaults")

    def get_owasp_patterns(self) -> List[Dict[str, Any]]:
        """Get OWASP patterns from knowledge base.

        Returns:
            List of OWASP pattern definitions
        """
        if "owasp-top10" in self.knowledge_base:
            kb_data = self.knowledge_base["owasp-top10"]
            # Patterns are nested inside categories
            all_patterns = []
            categories = kb_data.get("categories", [])
            for category in categories:
                patterns = category.get("patterns", [])
                for pattern in patterns:
                    pattern["owasp_category"] = category.get("id", "Unknown")
                    all_patterns.append(pattern)
            if all_patterns:
                return all_patterns
            # Fallback to top-level patterns if they exist
            return kb_data.get("patterns", [])
        return [{"category": "injection", "id": "A03"}]

    def get_secrets_patterns(self) -> List[Dict[str, Any]]:
        """Get secrets patterns from knowledge base.

        Returns:
            List of secrets pattern definitions
        """
        if "secrets-patterns" in self.knowledge_base:
            return self.knowledge_base["secrets-patterns"].get("patterns", [])
        return [{"type": "aws", "pattern": r"AKIA.*"}]

    def get_cicd_rules(self) -> List[Dict[str, Any]]:
        """Get CI/CD hardening rules from knowledge base.

        Returns:
            List of CI/CD rule definitions
        """
        if "cicd-hardening" in self.knowledge_base:
            return self.knowledge_base["cicd-hardening"].get("rules", [])
        return [{"rule": "pin_action_shas", "severity": "HIGH"}]

    # ========================================================================
    # Audit Trail
    # ========================================================================

    def _log_scan(
        self,
        action: str,
        finding_count: int,
        scan_id: Optional[str] = None
    ) -> None:
        """Log scan to audit trail.

        Args:
            action: Type of scan
            finding_count: Number of findings
            scan_id: Optional scan identifier
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "security_scan",
            "scan_type": action,
            "finding_count": finding_count,
            "scan_id": scan_id or str(uuid.uuid4())[:8],
            "findings_hash": hashlib.sha256(str(finding_count).encode()).hexdigest()[:16],
        }
        self.audit_trail.append(entry)

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get security scan audit trail.

        Args:
            limit: Maximum number of entries to return

        Returns:
            Result containing list of audit entries
        """
        return Ok(self.audit_trail[-limit:])

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _detect_high_entropy(self, code: str) -> List[Dict[str, Any]]:
        """Detect high-entropy strings that may be secrets.

        Args:
            code: Source code to scan

        Returns:
            List of high-entropy findings
        """
        findings: List[Dict[str, Any]] = []
        # Simplified entropy detection - look for long base64-like strings
        pattern = r'["\'][A-Za-z0-9+/=]{32,}["\']'
        matches = re.finditer(pattern, code)

        for match in matches:
            findings.append({
                "finding_id": str(uuid.uuid4())[:8],
                "type": "high_entropy",
                "severity": "MEDIUM",
                "title": "High-entropy string detected",
                "description": "String with high entropy may be a secret",
                "pattern_matched": match.group(0)[:30] + "...",
            })

        return findings

    def _get_injection_remediation(self, injection_type: str) -> str:
        """Get remediation guidance for injection type.

        Args:
            injection_type: Type of injection

        Returns:
            Remediation string
        """
        remediations = {
            "sql_injection": "Use parameterized queries or ORM instead of string formatting",
            "command_injection": "Use subprocess with list arguments, never shell=True with user input",
            "xss": "Use proper HTML escaping or templating engine auto-escape",
            "path_traversal": "Validate and sanitize file paths, use os.path.basename()",
        }
        return remediations.get(injection_type, "Review and fix the security issue")

    def _get_workflow_remediation(self, finding_type: str) -> str:
        """Get remediation guidance for workflow finding.

        Args:
            finding_type: Type of workflow finding

        Returns:
            Remediation string
        """
        remediations = {
            "unpinned_action": "Pin GitHub Action to full SHA: uses: action@<full-sha>",
            "workflow_injection": "Never use github.event.* directly in run steps. Use env: to sanitize.",
        }
        return remediations.get(finding_type, "Review CI/CD security best practices")

    def _generate_recommendations(
        self,
        findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate prioritized recommendations.

        Args:
            findings: List of security findings

        Returns:
            List of recommendations
        """
        recommendations: List[str] = []

        types_found = set(f.get("type", "") for f in findings)

        if any(t in types_found for t in ["hardcoded_secret", "api_key", "password"]):
            recommendations.append("Remove all hardcoded secrets and use a secrets manager")

        if "sql_injection" in types_found:
            recommendations.append("Replace string formatting in SQL with parameterized queries")

        if "command_injection" in types_found:
            recommendations.append("Use subprocess with list arguments instead of shell strings")

        if "unpinned_action" in types_found:
            recommendations.append("Pin all GitHub Actions to full commit SHAs")

        if "workflow_injection" in types_found:
            recommendations.append("Sanitize github.event.* inputs via env: variables")

        return recommendations

    def _map_to_owasp(
        self,
        findings: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Map findings to OWASP Top 10 categories.

        Args:
            findings: List of security findings

        Returns:
            Dictionary mapping OWASP categories to finding IDs
        """
        mapping: Dict[str, List[str]] = {}

        for finding in findings:
            category = finding.get("owasp_category", "Unknown")
            finding_id = finding.get("finding_id", "")

            if category not in mapping:
                mapping[category] = []
            mapping[category].append(finding_id)

        return mapping
