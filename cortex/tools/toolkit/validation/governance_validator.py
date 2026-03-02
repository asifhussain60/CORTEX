"""
Governance Validator.

Consolidates production readiness validation and governance alignment checking.
Extracted from scripts/validate-production.py and scripts/validate_governance_alignment.py.

Author: CORTEX Framework
Phase: 90 (Toolkit Centralization)
"""

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ValidationCheck:
    """Individual validation check result."""
    name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None


@dataclass
class ProductionReadinessReport:
    """Complete production readiness assessment."""
    overall_status: str
    readiness_score: float
    critical_issues: List[ValidationCheck]
    high_issues: List[ValidationCheck]
    medium_issues: List[ValidationCheck]
    low_issues: List[ValidationCheck]
    passed_checks: List[ValidationCheck]
    summary: Dict[str, Any]
    timestamp: str


class GovernanceValidator:
    """
    Validates CORTEX governance alignment and production readiness.
    
    Consolidates functionality from:
    - scripts/validate-production.py (production readiness)
    - scripts/validate_governance_alignment.py (CORE rules alignment)
    """
    
    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """
        Initialize governance validator.
        
        Args:
            workspace_root: Root of CORTEX workspace (defaults to current directory)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.checks: List[ValidationCheck] = []
    
    def validate_production_readiness(self, dry_run: bool = False) -> ProductionReadinessReport:
        """
        Run complete production readiness assessment.
        
        Args:
            dry_run: If True, perform validation without side effects
        
        Returns:
            ProductionReadinessReport with all findings
        """
        logger.info("🔍 Running CORTEX Production Readiness Assessment...")
        
        if dry_run:
            logger.info("   (dry-run mode - no side effects)")
        
        # Reset checks
        self.checks = []
        
        # Run all validation categories
        self._validate_infrastructure()
        self._validate_dependencies()
        self._validate_mcp_server()
        self._validate_mcp_configuration()
        self._validate_security_configuration()
        self._validate_monitoring()
        self._validate_tests()
        self._validate_governance_files()
        
        # Generate report
        return self._generate_report()
    
    def check_governance_alignment(self) -> bool:
        """
        Validate governance alignment across layers.
        
        Checks:
        - .github/prompts/ directory exists with prompt files
        - .github/agents/ directory exists with agent specifications
        - CORE rules compliance
        - Registry structure
        
        Returns:
            True if validation passes, False otherwise
        """
        logger.info("🔍 Validating Governance Alignment...")
        
        # Check prompts directory
        prompts_dir = self.workspace_root / ".github" / "prompts"
        if not prompts_dir.exists():
            logger.error(f"❌ Missing: {prompts_dir}")
            return False
        
        prompt_files = list(prompts_dir.glob("*.md"))
        logger.info(f"✅ {prompts_dir}: {len(prompt_files)} prompt files")
        
        # Check agents directory
        agents_dir = self.workspace_root / ".github" / "agents"
        if not agents_dir.exists():
            logger.error(f"❌ Missing: {agents_dir}")
            return False
        
        agent_files = list(agents_dir.glob("**/*.md"))
        logger.info(f"✅ {agents_dir}: {len(agent_files)} agent files")
        
        # Check registry structure
        registry_dir = self.workspace_root / "cortex-registry"
        if not registry_dir.exists():
            logger.warning(f"⚠️  Missing registry: {registry_dir}")
            return False
        
        logger.info(f"✅ {registry_dir}: Registry structure exists")
        
        return True
    
    def assess_security_posture(self) -> Dict[str, Any]:
        """
        Assess security posture with OWASP compliance checks.
        
        Returns:
            Dict with security score and findings
        """
        logger.info("🔒 Assessing Security Posture...")
        
        findings = []
        score = 100.0
        
        # Check OWASP knowledge files
        owasp_file = self.workspace_root / "cortex" / "knowledge" / "best-practices" / "security" / "owasp-top-10.yaml"
        if owasp_file.exists():
            findings.append({"check": "OWASP Knowledge", "status": "PASS", "detail": "OWASP-Top-10 knowledge file exists"})
        else:
            findings.append({"check": "OWASP Knowledge", "status": "FAIL", "detail": "Missing OWASP knowledge"})
            score -= 15.0
        
        # Check secrets management
        secrets_dir = self.workspace_root / "cortex" / "secrets"
        if secrets_dir.exists():
            findings.append({"check": "Secrets Management", "status": "PASS", "detail": "Secrets module exists"})
        else:
            findings.append({"check": "Secrets Management", "status": "WARN", "detail": "No secrets module"})
            score -= 10.0
        
        # Check .env in .gitignore
        gitignore = self.workspace_root / ".gitignore"
        if gitignore.exists() and ".env" in gitignore.read_text():
            findings.append({"check": ".env Protection", "status": "PASS", "detail": ".env in .gitignore"})
        else:
            findings.append({"check": ".env Protection", "status": "FAIL", "detail": ".env not protected"})
            score -= 20.0
        
        return {
            "score": max(0.0, score),
            "findings": findings,
            "owasp": {
                "checked": True,
                "file_exists": owasp_file.exists()
            }
        }
    
    def generate_readiness_report(self, report: ProductionReadinessReport) -> str:
        """
        Generate formatted readiness report.
        
        Args:
            report: ProductionReadinessReport to format
        
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX PRODUCTION READINESS REPORT")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Overall Status: {report.overall_status}")
        lines.append(f"Readiness Score: {report.readiness_score:.1f}%")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        for category, result in report.summary.items():
            lines.append(f"  {category}: {result}")
        lines.append("")
        
        # Issues by severity
        if report.critical_issues:
            lines.append(f"CRITICAL ISSUES ({len(report.critical_issues)})")
            lines.append("-" * 80)
            for check in report.critical_issues:
                lines.append(f"  ❌ {check.name}: {check.message}")
                if check.remediation:
                    lines.append(f"     → {check.remediation}")
            lines.append("")
        
        if report.high_issues:
            lines.append(f"HIGH PRIORITY ISSUES ({len(report.high_issues)})")
            lines.append("-" * 80)
            for check in report.high_issues:
                lines.append(f"  ⚠️  {check.name}: {check.message}")
                if check.remediation:
                    lines.append(f"     → {check.remediation}")
            lines.append("")
        
        if report.medium_issues:
            lines.append(f"MEDIUM PRIORITY ISSUES ({len(report.medium_issues)})")
            lines.append("-" * 80)
            for check in report.medium_issues[:5]:  # Limit to first 5
                lines.append(f"  ⚠️  {check.name}: {check.message}")
            if len(report.medium_issues) > 5:
                lines.append(f"  ... and {len(report.medium_issues) - 5} more")
            lines.append("")
        
        # Passed checks summary
        lines.append(f"PASSED CHECKS: {len(report.passed_checks)}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    # Private helper methods
    
    def _add_check(self, name: str, passed: bool, severity: Severity, message: str, 
                   details: Optional[Dict[str, Any]] = None, remediation: Optional[str] = None) -> None:
        """Add validation check result."""
        self.checks.append(ValidationCheck(
            name=name,
            passed=passed,
            severity=severity,
            message=message,
            details=details or {},
            remediation=remediation
        ))
    
    def _validate_infrastructure(self) -> None:
        """Validate core infrastructure components."""
        logger.info("📋 Validating Infrastructure...")
        
        # Python version
        if sys.version_info >= (3, 9):
            self._add_check(
                "Python Version",
                True,
                Severity.INFO,
                f"Python {sys.version_info.major}.{sys.version_info.minor} (>= 3.9 required)"
            )
        else:
            self._add_check(
                "Python Version",
                False,
                Severity.CRITICAL,
                f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.9 required",
                remediation="Upgrade Python to 3.9+ for production deployment"
            )
        
        # Core directories
        required_dirs = ["cortex", "tests", "deployment"]
        for dir_name in required_dirs:
            dir_path = self.workspace_root / dir_name
            self._add_check(
                f"Directory: {dir_name}",
                dir_path.exists(),
                Severity.CRITICAL if not dir_path.exists() else Severity.INFO,
                f"Required directory {'exists' if dir_path.exists() else 'missing'}: {dir_path}",
                remediation=f"Create {dir_name}/ directory" if not dir_path.exists() else None
            )
    
    def _validate_dependencies(self) -> None:
        """Validate Python dependencies."""
        logger.info("📦 Validating Dependencies...")
        
        req_path = self.workspace_root / "requirements.txt"
        self._add_check(
            "requirements.txt",
            req_path.exists(),
            Severity.HIGH if not req_path.exists() else Severity.INFO,
            f"Requirements file {'exists' if req_path.exists() else 'missing'}: {req_path}"
        )
    
    def _validate_mcp_server(self) -> None:
        """Validate MCP server configuration."""
        logger.info("🔧 Validating MCP Server...")
        
        server_path = self.workspace_root / "cortex" / "mcp" / "server.py"
        self._add_check(
            "MCP Server Module",
            server_path.exists(),
            Severity.CRITICAL if not server_path.exists() else Severity.INFO,
            f"MCP server {'exists' if server_path.exists() else 'missing'}: {server_path}"
        )
    
    def _validate_mcp_configuration(self) -> None:
        """Validate MCP deployment configuration.

        CORTEX is delivered via MCP (stdio transport, Pylance-style) or SaaS.
        No Docker runtime is required. Validates MCP server module and
        VS Code settings configuration instead.
        """
        logger.info("� Validating MCP Configuration...")

        mcp_server = self.workspace_root / "cortex" / "mcp" / "server.py"
        self._add_check(
            "MCP Server",
            mcp_server.exists(),
            Severity.CRITICAL if not mcp_server.exists() else Severity.INFO,
            f"MCP server {'exists' if mcp_server.exists() else 'missing'}: {mcp_server}",
            remediation="Ensure cortex/mcp/server.py exists for MCP deployment" if not mcp_server.exists() else None
        )

        vscode_settings = self.workspace_root / ".vscode" / "settings.json"
        self._add_check(
            "MCP VS Code Config",
            vscode_settings.exists(),
            Severity.HIGH if not vscode_settings.exists() else Severity.INFO,
            f"VS Code MCP config {'exists' if vscode_settings.exists() else 'missing'}: {vscode_settings}",
            remediation="Run python3 scripts/setup-mcp.py to configure VS Code MCP settings" if not vscode_settings.exists() else None
        )
    
    def _validate_security_configuration(self) -> None:
        """Validate security configurations."""
        logger.info("🔒 Validating Security Configuration...")
        
        owasp_file = self.workspace_root / "cortex" / "knowledge" / "best-practices" / "security" / "owasp-top-10.yaml"
        self._add_check(
            "OWASP Knowledge",
            owasp_file.exists(),
            Severity.MEDIUM if not owasp_file.exists() else Severity.INFO,
            f"OWASP knowledge {'exists' if owasp_file.exists() else 'missing'}: {owasp_file}"
        )
    
    def _validate_monitoring(self) -> None:
        """Validate monitoring configuration."""
        logger.info("📊 Validating Monitoring...")
        
        prometheus = self.workspace_root / "deployment" / "prometheus.yml"
        self._add_check(
            "Prometheus Config",
            prometheus.exists(),
            Severity.MEDIUM if not prometheus.exists() else Severity.INFO,
            f"Prometheus config {'exists' if prometheus.exists() else 'missing'}: {prometheus}"
        )
    
    def _validate_tests(self) -> None:
        """Validate test suite."""
        logger.info("🧪 Validating Tests...")
        
        tests_dir = self.workspace_root / "tests"
        test_count = len(list(tests_dir.glob("**/test_*.py"))) if tests_dir.exists() else 0
        
        self._add_check(
            "Test Suite",
            test_count > 0,
            Severity.HIGH if test_count == 0 else Severity.INFO,
            f"Found {test_count} test files in {tests_dir}"
        )
    
    def _validate_governance_files(self) -> None:
        """Validate governance file structure."""
        logger.info("📜 Validating Governance Files...")
        
        # CORE-002 compliance
        prompts_dir = self.workspace_root / ".github" / "prompts"
        agents_dir = self.workspace_root / ".github" / "agents"
        
        self._add_check(
            "Prompts Directory",
            prompts_dir.exists(),
            Severity.HIGH if not prompts_dir.exists() else Severity.INFO,
            f"Prompts directory {'exists' if prompts_dir.exists() else 'missing'}: {prompts_dir}"
        )
        
        self._add_check(
            "Agents Directory",
            agents_dir.exists(),
            Severity.HIGH if not agents_dir.exists() else Severity.INFO,
            f"Agents directory {'exists' if agents_dir.exists() else 'missing'}: {agents_dir}"
        )
    
    def _generate_report(self) -> ProductionReadinessReport:
        """Generate production readiness report from checks."""
        # Categorize issues
        critical = [c for c in self.checks if not c.passed and c.severity == Severity.CRITICAL]
        high = [c for c in self.checks if not c.passed and c.severity == Severity.HIGH]
        medium = [c for c in self.checks if not c.passed and c.severity == Severity.MEDIUM]
        low = [c for c in self.checks if not c.passed and c.severity == Severity.LOW]
        passed = [c for c in self.checks if c.passed]
        
        # Calculate score
        total = len(self.checks)
        score = (len(passed) / total * 100) if total > 0 else 0.0
        
        # Determine overall status
        if critical:
            status = "BLOCKED"
        elif high:
            status = "NOT READY"
        elif medium:
            status = "READY WITH WARNINGS"
        else:
            status = "PRODUCTION READY"
        
        # Build summary
        summary = {
            "infrastructure": f"{sum(1 for c in passed if 'infrastructure' in c.name.lower())} checks passed",
            "dependencies": f"{sum(1 for c in passed if 'depend' in c.name.lower() or 'package' in c.name.lower())} checks passed",
            "mcp_server": f"{sum(1 for c in passed if 'mcp' in c.name.lower())} checks passed",
            "security": f"{sum(1 for c in passed if 'secur' in c.name.lower() or 'owasp' in c.name.lower())} checks passed",
            "tests": f"{sum(1 for c in passed if 'test' in c.name.lower())} checks passed",
        }
        
        return ProductionReadinessReport(
            overall_status=status,
            readiness_score=score,
            critical_issues=critical,
            high_issues=high,
            medium_issues=medium,
            low_issues=low,
            passed_checks=passed,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
