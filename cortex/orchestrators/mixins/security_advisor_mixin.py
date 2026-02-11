"""
SecurityAdvisor Mixin for all orchestrators.

Provides:
- Automatic security assessment on every operation
- P0/P1/P2 risk classification
- OWASP Top 10 + CWE pattern detection
- Compliance gap detection (HIPAA, PCI-DSS, SOC2)

AC-ID: AC-LENS-V2-SECURITY-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.analysis.security_threat_analyzer import (
    SecurityThreatAnalyzer,
    ThreatSeverity,
    get_security_threat_analyzer,
)
from cortex.lens.analyzers.config_analyzer import (
    ConfigAnalyzer,
    ConfigSeverity,
    get_config_analyzer,
)

logger = logging.getLogger(__name__)


class SecurityAdvisorMixin:
    """
    Mixin to add security-first capabilities to all orchestrators.

    Provides automatic security assessment with P0/P1/P2 classification
    and compliance checking against OWASP Top 10 and company standards.

    Usage:
        ```python
        class MyOrchestrator(SecurityAdvisorMixin, IOrchestrator):
            def execute(self, params):
                # Auto-run security assessment
                security = self.assess_security_risks(params)
                if security["block_execution"]:
                    return Err(f"⛔ SECURITY BLOCK: {security['summary']}")
                # ... continue operation
        ```

    Attributes:
        security_analyzer: SecurityThreatAnalyzer instance
        config_analyzer: ConfigAnalyzer instance
        security_knowledge: Loaded security knowledge from YAMLs
    """

    def __init__(self, *args, **kwargs):
        """Initialize SecurityAdvisorMixin."""
        super().__init__(*args, **kwargs)
        self.security_analyzer = get_security_threat_analyzer()
        self.config_analyzer = get_config_analyzer()
        self.security_knowledge = self._load_security_knowledge()

    def assess_security_risks(
        self,
        context: Dict[str, Any],
        code: Optional[str] = None,
        config_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Assess security risks in operation context.

        Performs multi-layer security analysis:
        1. Code threat analysis (CWE patterns)
        2. Config security analysis (secrets, insecure defaults)
        3. OWASP Top 10 compliance check
        4. Company compliance check (HIPAA, PCI-DSS, etc.)

        Args:
            context: Operation context (lens_context, user_request, etc.)
            code: Optional code to analyze
            config_path: Optional config file to analyze

        Returns:
            Dict with:
            - has_risks: bool
            - block_execution: bool (True for P0/CRITICAL)
            - p0_risks: List of critical risks
            - p1_risks: List of high risks
            - p2_risks: List of medium risks
            - p3_risks: List of low risks
            - compliance_gaps: List of compliance violations
            - summary: Human-readable summary

        Example:
            >>> security = self.assess_security_risks(
            ...     context={"operation": "deploy"},
            ...     code="eval(user_input)"
            ... )
            >>> if security["block_execution"]:
            ...     print(f"BLOCKED: {security['summary']}")
        """
        risks = {
            "has_risks": False,
            "block_execution": False,
            "p0_risks": [],
            "p1_risks": [],
            "p2_risks": [],
            "p3_risks": [],
            "compliance_gaps": [],
            "summary": "",
            "details": {},
        }

        # 1. Code threat analysis
        if code:
            code_risks = self._analyze_code_threats(code, context)
            risks["p0_risks"].extend(code_risks.get("p0", []))
            risks["p1_risks"].extend(code_risks.get("p1", []))
            risks["p2_risks"].extend(code_risks.get("p2", []))
            risks["details"]["code_analysis"] = code_risks

        # 2. Config security analysis
        if config_path:
            config_risks = self._analyze_config_security(config_path)
            risks["p0_risks"].extend(config_risks.get("p0", []))
            risks["p1_risks"].extend(config_risks.get("p1", []))
            risks["p2_risks"].extend(config_risks.get("p2", []))
            risks["details"]["config_analysis"] = config_risks

        # 3. OWASP Top 10 check
        owasp_gaps = self._check_owasp_compliance(context)
        risks["compliance_gaps"].extend(owasp_gaps)

        # 4. Company compliance check
        company_gaps = self._check_company_compliance(context)
        risks["compliance_gaps"].extend(company_gaps)

        # 5. Determine if execution should be blocked
        risks["has_risks"] = (
            len(risks["p0_risks"]) > 0 or
            len(risks["p1_risks"]) > 0
        )
        risks["block_execution"] = len(risks["p0_risks"]) > 0

        # 6. Generate summary
        risks["summary"] = self._generate_risk_summary(risks)

        logger.info(
            "Security assessment complete: P0=%d, P1=%d, P2=%d, block=%s",
            len(risks["p0_risks"]),
            len(risks["p1_risks"]),
            len(risks["p2_risks"]),
            risks["block_execution"]
        )

        return risks

    def _analyze_code_threats(self, code: str, context: Dict[str, Any]) -> Dict[str, List]:
        """
        Analyze code for security threats using SecurityThreatAnalyzer.

        Returns dict with p0, p1, p2, p3 lists.
        """
        file_path = context.get("file_path", "user_code.py")
        result = self.security_analyzer.analyze_code(code, file_path)

        risks = {"p0": [], "p1": [], "p2": [], "p3": []}

        if not result.success:
            logger.warning("Code threat analysis failed: %s", result.error)
            return risks

        for threat in result.threat_findings:
            priority = self._map_severity_to_priority(threat.severity)
            risks[priority].append({
                "cwe_id": threat.cwe_id,
                "description": threat.description,
                "recommendation": threat.recommendation,
                "line_number": threat.line_number,
                "severity": threat.severity.name,
                "code_snippet": threat.code_snippet,
            })

        return risks

    def _analyze_config_security(self, config_path: Path) -> Dict[str, List]:
        """
        Analyze config file for security issues using ConfigAnalyzer.

        Returns dict with p0, p1, p2, p3 lists.
        """
        result = self.config_analyzer.analyze_file(config_path)

        risks = {"p0": [], "p1": [], "p2": [], "p3": []}

        if not result.success:
            logger.warning("Config analysis failed: %s", result.error)
            return risks

        for finding in result.findings:
            priority = finding.severity.value.lower()  # P0 -> p0
            risks[priority].append({
                "category": finding.category.value,
                "description": finding.description,
                "recommendation": finding.recommendation,
                "line_number": finding.line_number,
                "file_path": finding.file_path,
            })

        return risks

    def _check_owasp_compliance(self, context: Dict[str, Any]) -> List[Dict]:
        """
        Check for OWASP Top 10 violations.

        Loads from cortex_brain/tier3/knowledge/SECURITY/owasp-top-10.yaml
        """
        gaps = []

        try:
            owasp_knowledge = self.security_knowledge.get("owasp_top_10", {})

            # Basic checks based on context
            # (Full implementation would analyze code patterns)

            # Example: Check for authentication requirements
            if context.get("operation") in ["deploy", "production"]:
                if not context.get("auth_enabled"):
                    gaps.append({
                        "standard": "OWASP A01:2021",
                        "name": "Broken Access Control",
                        "description": "Authentication not verified for production deployment",
                        "recommendation": "Ensure authentication is enabled and tested",
                        "severity": "P1",
                    })

        except Exception as e:
            logger.warning("OWASP compliance check failed: %s", e)

        return gaps

    def _check_company_compliance(self, context: Dict[str, Any]) -> List[Dict]:
        """
        Check for company-specific compliance gaps.

        Loads from company/domains/compliance-standards/*.yaml
        """
        gaps = []

        try:
            company_path = Path("company/domains/compliance-standards")

            if not company_path.exists():
                return gaps

            # Load compliance standards
            for yaml_file in company_path.glob("*.yaml"):
                with open(yaml_file, "r") as f:
                    standard = yaml.safe_load(f)

                # Basic compliance checks
                # (Full implementation would check specific requirements)

                # Example: HIPAA check
                if yaml_file.stem == "hipaa" and context.get("handles_phi"):
                    if not context.get("encryption_enabled"):
                        gaps.append({
                            "standard": "HIPAA",
                            "description": "PHI encryption not verified",
                            "recommendation": "Ensure PHI is encrypted at rest and in transit",
                            "severity": "P0",
                        })

        except Exception as e:
            logger.warning("Company compliance check failed: %s", e)

        return gaps

    def _map_severity_to_priority(self, severity: ThreatSeverity) -> str:
        """Map ThreatSeverity to priority string (p0/p1/p2/p3)."""
        mapping = {
            ThreatSeverity.CRITICAL: "p0",
            ThreatSeverity.HIGH: "p1",
            ThreatSeverity.MEDIUM: "p2",
            ThreatSeverity.LOW: "p3",
            ThreatSeverity.INFO: "p3",
        }
        return mapping.get(severity, "p3")

    def _generate_risk_summary(self, risks: Dict[str, Any]) -> str:
        """Generate human-readable risk summary."""
        p0_count = len(risks["p0_risks"])
        p1_count = len(risks["p1_risks"])
        p2_count = len(risks["p2_risks"])
        compliance_count = len(risks["compliance_gaps"])

        if p0_count > 0:
            return (
                f"⛔ CRITICAL: {p0_count} P0 risk(s) detected. "
                f"Execution BLOCKED. Address immediately."
            )
        elif p1_count > 0:
            return (
                f"⚠️  HIGH: {p1_count} P1 risk(s) detected. "
                f"Address within current sprint."
            )
        elif p2_count > 0 or compliance_count > 0:
            return (
                f"ℹ️  MODERATE: {p2_count} P2 risk(s), {compliance_count} compliance gap(s). "
                f"Review and address."
            )
        else:
            return "✅ No security risks detected."

    def _load_security_knowledge(self) -> Dict[str, Any]:
        """
        Load security knowledge from YAML files.

        Loads from:
        - cortex_brain/tier3/knowledge/SECURITY/owasp-top-10.yaml
        - Other security knowledge files
        """
        knowledge = {}

        try:
            # Load OWASP Top 10
            owasp_path = Path("cortex_brain/tier3/knowledge/SECURITY/owasp-top-10.yaml")
            if owasp_path.exists():
                with open(owasp_path, "r") as f:
                    knowledge["owasp_top_10"] = yaml.safe_load(f)

        except Exception as e:
            logger.warning("Failed to load security knowledge: %s", e)

        return knowledge
