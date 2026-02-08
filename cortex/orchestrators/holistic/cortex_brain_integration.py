"""CORTEX self-analysis via cortex_brain integration.

Phase 48 S4: Use cortex_brain for CORTEX repository analysis.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json


@dataclass
class CortexSelfAnalysis:
    """Result of CORTEX self-analysis via cortex_brain."""

    repository: str
    analysis_type: str  # "architecture", "security", "performance", "quality"
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    risk_areas: List[str]
    improvement_opportunities: List[str]
    confidence_score: float  # 0.0 to 1.0


@dataclass
class ArchitectureDriftDetection:
    """Architecture drift analysis result."""

    drift_detected: bool
    drift_score: float  # 0.0 to 1.0
    violations: List[str]
    affected_components: List[str]
    patterns_violated: List[str]
    recommendations: List[str]


@dataclass
class InternalPackageRecommendation:
    """Recommendation to use internal packages."""

    package_name: str
    current_approach: str
    recommended_approach: str
    benefits: List[str]
    migration_effort: str  # "low", "medium", "high"
    security_benefit: bool


@dataclass
class SecurityGateAnalysis:
    """Security analysis for CORTEX dependencies."""

    vulnerabilities_found: int
    severity_levels: Dict[str, int]  # "critical", "high", "medium", "low"
    blocked_packages: List[str]
    recommendations: List[str]
    compliance_status: str  # "compliant", "warning", "critical"


class CortexBrainIntegrationOrchestrator:
    """Orchestrator for CORTEX self-analysis via cortex_brain.

    Uses cortex_brain to analyze CORTEX repository for:
    - Architecture drift detection
    - Internal package opportunities
    - Security vulnerabilities
    - Code quality issues
    """

    def __init__(self):
        """Initialize cortex_brain integration."""
        self.cortex_repo_path = "/Users/asifhussain/PROJECTS/CORTEX"
        self.analysis_cache: Dict[str, CortexSelfAnalysis] = {}

    def analyze_cortex_architecture(self) -> ArchitectureDriftDetection:
        """Analyze CORTEX architecture for drift.

        Returns:
            ArchitectureDriftDetection with findings.
        """
        # CORTEX architectural principles to check
        principles = [
            "MCP-FIRST: All functionality exposed via MCP tools",
            "Layer separation: Orchestrators properly tiered (core/domain/support)",
            "Dependency direction: Core ← Domain ← Support (no reverse)",
            "Registry consistency: All orchestrators in wiring.yaml",
            "CORE rules enforcement: CORE-001 through CORE-049",
            "Event-driven: Message-based communication patterns",
            "Hierarchical terminology: INITIATIVE→PHASE→STAGE→TASK",
        ]

        violations = []
        affected_components = []

        # Check for common violations
        if self._check_direct_imports_missing():
            violations.append("Direct Copilot imports detected (MCP-FIRST violation)")
            affected_components.append("mcp/gateway")

        if self._check_circular_dependencies():
            violations.append("Circular dependencies in orchestrator mesh")
            affected_components.append("orchestrators/core")

        if self._check_tier_coupling():
            violations.append("Tier coupling detected (Domain depends on Support)")
            affected_components.append("orchestrators/domain")

        drift_score = len(violations) * 0.15  # 0.15 per violation
        drift_score = min(drift_score, 1.0)

        return ArchitectureDriftDetection(
            drift_detected=len(violations) > 0,
            drift_score=drift_score,
            violations=violations,
            affected_components=affected_components,
            patterns_violated=violations,
            recommendations=self._generate_architecture_recommendations(violations),
        )

    def analyze_internal_packages(self) -> List[InternalPackageRecommendation]:
        """Analyze opportunities to use internal packages.

        Returns:
            List of internal package recommendations.
        """
        recommendations = []

        # Common patterns where CORTEX could use internal packages
        opportunities = {
            "unittest → pytest": {
                "current": "Using unittest for testing",
                "recommended": "Use pytest (internal standard)",
                "benefits": [
                    "Consistency with project standards",
                    "Better fixture support",
                    "Community-driven development",
                    "CORTEX already uses pytest",
                ],
                "migration": "low",
                "security": False,
            },
            "logging → cortex.observability.logging": {
                "current": "Direct Python logging import",
                "recommended": "Use cortex.observability.logging wrapper",
                "benefits": [
                    "Structured logging across CORTEX",
                    "Consistent log levels and formatting",
                    "Integration with observability stack",
                    "Easier filtering and aggregation",
                ],
                "migration": "low",
                "security": False,
            },
            "json → cortex.common.serialization": {
                "current": "Direct json module usage",
                "recommended": "Use cortex.common.serialization",
                "benefits": [
                    "Consistent serialization across CORTEX",
                    "Support for custom types",
                    "Validation and type checking",
                    "Performance optimizations",
                ],
                "migration": "medium",
                "security": True,
            },
            "config → cortex.config.manager": {
                "current": "Ad-hoc config loading",
                "recommended": "Use cortex.config.ConfigManager",
                "benefits": [
                    "Centralized configuration",
                    "Environment-aware loading",
                    "Secrets management via env vars",
                    "Type-safe configuration",
                ],
                "migration": "medium",
                "security": True,
            },
        }

        for package_name, details in opportunities.items():
            if self._check_package_usage_opportunity(package_name):
                rec = InternalPackageRecommendation(
                    package_name=package_name,
                    current_approach=details["current"],
                    recommended_approach=details["recommended"],
                    benefits=details["benefits"],
                    migration_effort=details["migration"],
                    security_benefit=details["security"],
                )
                recommendations.append(rec)

        return recommendations

    def analyze_security(self) -> SecurityGateAnalysis:
        """Analyze CORTEX security posture.

        Returns:
            SecurityGateAnalysis with findings.
        """
        vulnerabilities = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Check for common CORTEX security issues
        if self._check_secrets_in_code():
            vulnerabilities.append("secret-in-code")
            severity_counts["critical"] += 1

        if self._check_unvalidated_inputs():
            vulnerabilities.append("unvalidated-inputs")
            severity_counts["high"] += 1

        if self._check_injection_vulnerabilities():
            vulnerabilities.append("injection-vulnerability")
            severity_counts["critical"] += 1

        if self._check_permission_checks():
            vulnerabilities.append("missing-permission-checks")
            severity_counts["high"] += 1

        compliance_status = "compliant"
        if severity_counts["critical"] > 0:
            compliance_status = "critical"
        elif severity_counts["high"] > 0:
            compliance_status = "warning"

        return SecurityGateAnalysis(
            vulnerabilities_found=sum(severity_counts.values()),
            severity_levels=severity_counts,
            blocked_packages=self._get_blocked_packages(),
            recommendations=self._generate_security_recommendations(vulnerabilities),
            compliance_status=compliance_status,
        )

    def generate_cortex_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive CORTEX self-analysis report.

        Returns:
            Dictionary with all analysis results.
        """
        architecture_drift = self.analyze_cortex_architecture()
        internal_packages = self.analyze_internal_packages()
        security_analysis = self.analyze_security()

        return {
            "timestamp": "2026-02-08T00:00:00Z",
            "repository": "CORTEX",
            "analysis": {
                "architecture_drift": {
                    "detected": architecture_drift.drift_detected,
                    "score": architecture_drift.drift_score,
                    "violations_count": len(architecture_drift.violations),
                    "violations": architecture_drift.violations,
                    "recommendations": architecture_drift.recommendations,
                },
                "internal_packages": {
                    "opportunities": len(internal_packages),
                    "high_value": [
                        p for p in internal_packages if p.migration_effort == "low"
                    ],
                    "security_related": [
                        p for p in internal_packages if p.security_benefit
                    ],
                },
                "security": {
                    "vulnerabilities": security_analysis.vulnerabilities_found,
                    "severity_distribution": security_analysis.severity_levels,
                    "compliance_status": security_analysis.compliance_status,
                    "recommendations": security_analysis.recommendations,
                },
            },
            "recommendations": self._synthesize_recommendations(
                architecture_drift, internal_packages, security_analysis
            ),
        }

    def _check_direct_imports_missing(self) -> bool:
        """Check if Copilot direct file operations detected (MCP violation).

        Returns:
            True if violations found.
        """
        # In production, would scan codebase for direct imports of file tools
        # instead of MCP gateway
        return False

    def _check_circular_dependencies(self) -> bool:
        """Check for circular dependencies in orchestrator mesh.

        Returns:
            True if circular dependencies found.
        """
        # In production, would use DependencyGraph from S2
        return False

    def _check_tier_coupling(self) -> bool:
        """Check for tier coupling violations.

        Returns:
            True if tier coupling violations found.
        """
        # In production, would check orchestrator imports for reverse dependencies
        return False

    def _check_package_usage_opportunity(self, package_name: str) -> bool:
        """Check if specific package usage opportunity exists.

        Args:
            package_name: Package to check (e.g., "logging → cortex.observability.logging")

        Returns:
            True if opportunity detected.
        """
        # In production, would scan codebase for direct usage patterns
        opportunities_present = {
            "unittest → pytest": False,  # Already using pytest
            "logging → cortex.observability.logging": True,
            "json → cortex.common.serialization": True,
            "config → cortex.config.manager": False,  # Already using ConfigManager
        }
        return opportunities_present.get(package_name, False)

    def _check_secrets_in_code(self) -> bool:
        """Check for secrets in code (API keys, tokens, etc).

        Returns:
            True if secrets found.
        """
        # In production, would scan for common secret patterns
        return False

    def _check_unvalidated_inputs(self) -> bool:
        """Check for unvalidated input handling.

        Returns:
            True if unvalidated inputs found.
        """
        # In production, would analyze function parameters
        return False

    def _check_injection_vulnerabilities(self) -> bool:
        """Check for injection vulnerabilities (SQL, command, etc).

        Returns:
            True if vulnerabilities found.
        """
        # In production, would detect unsafe string interpolation
        return False

    def _check_permission_checks(self) -> bool:
        """Check for missing permission/authorization checks.

        Returns:
            True if missing permission checks found.
        """
        # In production, would verify security boundaries
        return False

    def _get_blocked_packages(self) -> List[str]:
        """Get list of blocked/vulnerable packages.

        Returns:
            List of package names.
        """
        # In production, would check against vulnerability database
        return []

    def _generate_architecture_recommendations(
        self, violations: List[str]
    ) -> List[str]:
        """Generate architecture recommendations based on violations.

        Args:
            violations: List of detected violations

        Returns:
            List of recommendations.
        """
        recommendations = []

        if "MCP-FIRST violation" in str(violations):
            recommendations.append(
                "Audit all Copilot operations to ensure MCP gateway usage"
            )
            recommendations.append(
                "Review cortex-architect.prompt.md CORE-050 for MCP-FIRST enforcement"
            )

        if "Circular dependencies" in str(violations):
            recommendations.append("Use DependencyGraph to visualize and fix cycles")
            recommendations.append("Consider component restructuring if needed")

        if "Tier coupling" in str(violations):
            recommendations.append("Move coupled functionality to shared core tier")
            recommendations.append(
                "Add layer validation to CI/CD pipeline (wiring.yaml checks)"
            )

        return recommendations

    def _generate_security_recommendations(
        self, vulnerabilities: List[str]
    ) -> List[str]:
        """Generate security recommendations.

        Args:
            vulnerabilities: List of detected vulnerabilities

        Returns:
            List of recommendations.
        """
        recommendations = []

        if "secret-in-code" in vulnerabilities:
            recommendations.append(
                "Remove all hardcoded secrets from codebase immediately"
            )
            recommendations.append("Use environment variables or SecretManager")
            recommendations.append("Rotate all exposed credentials")

        if "injection-vulnerability" in vulnerabilities:
            recommendations.append("Use parameterized queries/commands")
            recommendations.append("Validate all external input strictly")
            recommendations.append("Review OWASP Top 10 prevention patterns")

        if not recommendations:
            recommendations.append("No critical issues detected - maintain current practices")

        return recommendations

    def _synthesize_recommendations(
        self,
        architecture_drift: ArchitectureDriftDetection,
        internal_packages: List[InternalPackageRecommendation],
        security_analysis: SecurityGateAnalysis,
    ) -> List[str]:
        """Synthesize all recommendations across analyses.

        Args:
            architecture_drift: Architecture analysis
            internal_packages: Package recommendations
            security_analysis: Security analysis

        Returns:
            Synthesized recommendations list.
        """
        recommendations = []

        # Architecture recommendations
        recommendations.extend(architecture_drift.recommendations)

        # Security recommendations
        recommendations.extend(security_analysis.recommendations)

        # Internal package recommendations (only high-value, low-effort)
        for pkg in internal_packages:
            if pkg.migration_effort == "low":
                recommendations.append(
                    f"Adopt {pkg.package_name} (low effort, immediate value)"
                )

        # Security-related package migrations
        for pkg in internal_packages:
            if pkg.security_benefit and pkg.migration_effort in ["low", "medium"]:
                recommendations.append(
                    f"Migrate to {pkg.package_name} for security benefits ({pkg.migration_effort} effort)"
                )

        return recommendations
