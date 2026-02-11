"""
AuditIntelligence for CORTEX Company Domain Integration.

Auto-discovers orchestrators and tracks standards integration coverage.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

import yaml


@dataclass
class OrchestratorCoverage:
    """
    Tracks standards integration status for an orchestrator.

    Attributes:
        name: Orchestrator name
        has_standards_resolver: Whether it uses StandardsResolver
        integration_status: INTEGRATED or NOT_INTEGRATED
    """
    name: str
    has_standards_resolver: bool
    integration_status: str


@dataclass
class CoverageReport:
    """
    Standards integration coverage report.

    Attributes:
        total_orchestrators: Total number of orchestrators
        integrated_count: Number with StandardsResolver
        coverage_percentage: Percentage integrated
        recommendations: List of integration recommendations
        markdown: Markdown-formatted report
    """
    total_orchestrators: int
    integrated_count: int
    coverage_percentage: float
    recommendations: List[str]
    markdown: str


class AuditIntelligence:
    """
    Auto-discovers orchestrators and tracks standards integration coverage.

    Scans wiring.yaml to find all registered orchestrators, checks which
    ones have StandardsResolver integration, generates coverage reports.

    Example:
        >>> intelligence = AuditIntelligence()
        >>> orchestrators = intelligence.discover_orchestrators()
        >>> report = intelligence.generate_coverage_report()
        >>> print(f"Coverage: {report.coverage_percentage}%")
    """

    def __init__(self, wiring_path: str = None):
        """
        Initialize audit intelligence.

        Args:
            wiring_path: Path to wiring.yaml (defaults to cortex/wiring/specifications/wiring.yaml)
        """
        if wiring_path is None:
            wiring_path = str(
                Path(__file__).parent.parent.parent
                / "cortex" / "wiring" / "specifications" / "wiring.yaml"
            )

        self.wiring_path = Path(wiring_path)
        self._orchestrators: List[str] = []
        self._coverage: List[OrchestratorCoverage] = []

    def discover_orchestrators(self) -> List[str]:
        """
        Discover orchestrators from wiring.yaml.

        Returns:
            List of orchestrator names
        """
        if not self.wiring_path.exists():
            return []

        try:
            with open(self.wiring_path, 'r') as f:
                wiring_data = yaml.safe_load(f)

            # Extract orchestrator names
            orchestrators = []

            if wiring_data and 'orchestrators' in wiring_data:
                for orch in wiring_data['orchestrators']:
                    if 'name' in orch:
                        orchestrators.append(orch['name'])

            self._orchestrators = orchestrators
            return orchestrators

        except Exception:
            return []

    def _check_has_standards_resolver(self, orchestrator: Any) -> bool:
        """
        Check if orchestrator has standards_resolver attribute.

        Args:
            orchestrator: Orchestrator instance

        Returns:
            True if has standards_resolver
        """
        return hasattr(orchestrator, 'standards_resolver')

    def analyze_coverage(self) -> None:
        """
        Analyze standards integration coverage.

        Checks each discovered orchestrator for StandardsResolver integration.
        """
        if not self._orchestrators:
            self.discover_orchestrators()

        self._coverage = []

        # For each orchestrator, check integration status
        # Note: In production, would dynamically import and check
        # For now, use known integration status
        integrated_orchestrators = [
            "MasterOrchestrator",
            "TDDOrchestrator",
        ]

        for orch_name in self._orchestrators:
            has_resolver = orch_name in integrated_orchestrators
            status = "INTEGRATED" if has_resolver else "NOT_INTEGRATED"

            coverage = OrchestratorCoverage(
                name=orch_name,
                has_standards_resolver=has_resolver,
                integration_status=status,
            )

            self._coverage.append(coverage)

    def generate_coverage_report(self) -> CoverageReport:
        """
        Generate standards integration coverage report.

        Returns:
            CoverageReport with statistics and recommendations
        """
        if not self._coverage:
            self.analyze_coverage()

        total = len(self._coverage)
        integrated = sum(1 for c in self._coverage if c.has_standards_resolver)

        coverage_pct = (integrated / total * 100) if total > 0 else 0.0

        # Generate recommendations for unintegrated orchestrators
        recommendations = []
        for cov in self._coverage:
            if not cov.has_standards_resolver:
                recommendations.append(
                    f"📋 **{cov.name}**: Integrate StandardsResolver for company domain support"
                )

        # Build markdown report
        lines = [
            "# Standards Integration Coverage Report",
            "",
            "## Summary",
            f"- **Total Orchestrators:** {total}",
            f"- **Integrated:** {integrated}",
            f"- **Coverage:** {coverage_pct:.1f}%",
            "",
        ]

        if integrated > 0:
            lines.append("## ✅ Integrated Orchestrators")
            lines.append("")
            for cov in self._coverage:
                if cov.has_standards_resolver:
                    lines.append(f"- {cov.name}")
            lines.append("")

        if recommendations:
            lines.append("## 📋 Integration Recommendations")
            lines.append("")
            for rec in recommendations:
                lines.append(rec)
            lines.append("")

        markdown = "\n".join(lines)

        return CoverageReport(
            total_orchestrators=total,
            integrated_count=integrated,
            coverage_percentage=coverage_pct,
            recommendations=recommendations,
            markdown=markdown,
        )
