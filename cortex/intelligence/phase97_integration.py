"""Phase 97 Integration Module

Integrates LENS Facade, Registry, Evolution Analyzer, and Consolidation Analyzer.

Author: CORTEX Framework
Phase: PHASE-97 S6-S9
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.lens.facade import LENSIntelligenceFacade, WorkflowType
from cortex.lens.lens_registry import (
    AnalyzerCapability,
    LanguageSupport,
    get_analyzer_registry,
)
from cortex.lens.analyzers.evolution_analyzer import (
    EvolutionAnalyzer,
    EvolutionTimeline,
)
from cortex.orchestrators.health.agents.consolidation_analyzer import (
    ConsolidationAnalyzer,
    ConsolidationReport,
)


@dataclass
class IntegratedIntelligenceReport:
    """Comprehensive intelligence report combining all analyzers.

    Attributes:
        lens_analysis: LENS workflow results
        evolution_timeline: Git history evolution
        consolidation_report: Orchestrator sprawl analysis
        registry_stats: Analyzer registry statistics
    """

    lens_analysis: Dict[str, Any]
    evolution_timeline: Optional[EvolutionTimeline] = None
    consolidation_report: Optional[ConsolidationReport] = None
    registry_stats: Dict[str, int] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.registry_stats is None:
            self.registry_stats = {}


class IntelligenceIntegrator:
    """Integration layer for Phase 97 intelligence components.

    Provides unified access to LENS, Evolution, and Consolidation analysis.

    Attributes:
        repo_path: Repository path
        lens_facade: LENS intelligence facade
        evolution_analyzer: Evolution timeline analyzer
        consolidation_analyzer: Consolidation analyzer
        registry: Analyzer registry
    """

    def __init__(self, repo_path: Path) -> None:
        """Initialize intelligence integrator.

        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.lens_facade = LENSIntelligenceFacade(repo_path=repo_path)
        self.evolution_analyzer = EvolutionAnalyzer(repo_path=repo_path)
        self.consolidation_analyzer = ConsolidationAnalyzer(repo_path=repo_path)
        self.registry = get_analyzer_registry()

    def analyze_comprehensive(
        self,
        target_path: Path,
        workflow: WorkflowType = WorkflowType.REFACTOR,
        include_evolution: bool = True,
        include_consolidation: bool = True,
    ) -> IntegratedIntelligenceReport:
        """Perform comprehensive analysis using all components.

        Args:
            target_path: Path to analyze
            workflow: LENS workflow type
            include_evolution: Whether to include evolution analysis
            include_consolidation: Whether to include consolidation analysis

        Returns:
            Integrated intelligence report
        """
        # LENS analysis
        lens_result = self.lens_facade.analyze(
            workflow=workflow,
            target_path=target_path,
        )

        # Evolution analysis (optional)
        evolution_timeline = None
        if include_evolution:
            evolution_timeline = self.evolution_analyzer.analyze(
                target_path=target_path if target_path.is_file() else None,
                days=90,
            )

        # Consolidation analysis (optional)
        consolidation_report = None
        if include_consolidation:
            consolidation_report = self.consolidation_analyzer.analyze()

        # Registry statistics
        all_analyzers = self.registry.get_all()
        registry_stats = {
            "total_analyzers": len(all_analyzers),
            "capabilities_count": len(AnalyzerCapability),
            "languages_count": len(LanguageSupport),
        }

        return IntegratedIntelligenceReport(
            lens_analysis=lens_result,
            evolution_timeline=evolution_timeline,
            consolidation_report=consolidation_report,
            registry_stats=registry_stats,
        )

    def get_registry_summary(self) -> Dict[str, Any]:
        """Get analyzer registry summary.

        Returns:
            Registry summary with counts and capabilities
        """
        all_analyzers = self.registry.get_all()

        capabilities_breakdown = {}
        for capability in AnalyzerCapability:
            analyzers = self.registry.find_by_capability(capability)
            capabilities_breakdown[capability.value] = len(analyzers)

        languages_breakdown = {}
        for language in LanguageSupport:
            analyzers = self.registry.find_by_language(language)
            languages_breakdown[language.value] = len(analyzers)

        return {
            "total_analyzers": len(all_analyzers),
            "capabilities": capabilities_breakdown,
            "languages": languages_breakdown,
            "analyzer_names": [a.name for a in all_analyzers],
        }

    def get_evolution_summary(self, days: int = 90) -> Dict[str, Any]:
        """Get evolution timeline summary.

        Args:
            days: Number of days to analyze

        Returns:
            Evolution summary
        """
        timeline = self.evolution_analyzer.analyze(days=days)

        return {
            "total_commits": timeline.total_commits,
            "total_refactorings": timeline.total_refactorings,
            "average_improvement": timeline.average_complexity_improvement,
            "tech_debt_trend": timeline.tech_debt_trend,
            "active_contributors": len(timeline.active_contributors),
            "milestones": len(timeline.milestones),
        }

    def get_consolidation_summary(self) -> Dict[str, Any]:
        """Get consolidation analysis summary.

        Returns:
            Consolidation summary
        """
        report = self.consolidation_analyzer.analyze()

        return {
            "total_orchestrators": report.total_orchestrators,
            "target_count": report.target_count,
            "reduction_percentage": report.reduction_percentage,
            "sprawl_score": report.sprawl_score,
            "recommendations_count": len(report.recommendations),
            "estimated_effort_hours": report.estimated_effort,
        }
