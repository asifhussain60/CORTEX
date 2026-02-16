"""Unit Tests for Phase 97 Integration

Tests integration of LENS, Evolution, and Consolidation components.

Author: CORTEX Framework
Phase: PHASE-97 S6-S9
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.intelligence.phase97_integration import (
    IntelligenceIntegrator,
    IntegratedIntelligenceReport,
)
from cortex.lens.facade import WorkflowType


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create temporary git repository.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        Path to git repository
    """
    import subprocess
    
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    
    # Create initial commit
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
    )
    
    return tmp_path


@pytest.fixture
def integrator(git_repo: Path) -> IntelligenceIntegrator:
    """Create intelligence integrator.
    
    Args:
        git_repo: Git repository path
    
    Returns:
        IntelligenceIntegrator instance
    """
    return IntelligenceIntegrator(repo_path=git_repo)


class TestIntegratedIntelligenceReport:
    """Test suite for IntegratedIntelligenceReport."""
    
    def test_report_creation(self) -> None:
        """Test creating integrated report."""
        report = IntegratedIntelligenceReport(
            lens_analysis={"workflow": "refactor"},
        )
        
        assert report.lens_analysis["workflow"] == "refactor"
        assert report.registry_stats == {}
    
    def test_report_with_all_data(self) -> None:
        """Test report with all analysis data."""
        from cortex.lens.analyzers.evolution_analyzer import EvolutionTimeline
        from cortex.orchestrators.health.agents.consolidation_analyzer import (
            ConsolidationReport,
        )
        from datetime import datetime
        
        now = datetime.now()
        report = IntegratedIntelligenceReport(
            lens_analysis={"workflow": "security"},
            evolution_timeline=EvolutionTimeline(
                start_date=now,
                end_date=now,
            ),
            consolidation_report=ConsolidationReport(
                total_orchestrators=50,
                target_count=28,
            ),
            registry_stats={"total_analyzers": 10},
        )
        
        assert report.evolution_timeline is not None
        assert report.consolidation_report is not None
        assert report.registry_stats["total_analyzers"] == 10


class TestIntelligenceIntegrator:
    """Test suite for IntelligenceIntegrator."""
    
    def test_init(self, integrator: IntelligenceIntegrator) -> None:
        """Test integrator initialization.
        
        Args:
            integrator: Intelligence integrator
        """
        assert integrator.repo_path is not None
        assert integrator.lens_facade is not None
        assert integrator.evolution_analyzer is not None
        assert integrator.consolidation_analyzer is not None
        assert integrator.registry is not None
    
    def test_analyze_comprehensive_minimal(
        self, integrator: IntelligenceIntegrator, git_repo: Path
    ) -> None:
        """Test comprehensive analysis with minimal options.
        
        Args:
            integrator: Intelligence integrator
            git_repo: Git repository path
        """
        target = git_repo / "test.py"
        
        report = integrator.analyze_comprehensive(
            target_path=target,
            workflow=WorkflowType.REFACTOR,
            include_evolution=False,
            include_consolidation=False,
        )
        
        assert isinstance(report, IntegratedIntelligenceReport)
        assert report.lens_analysis is not None
        assert report.evolution_timeline is None
        assert report.consolidation_report is None
    
    def test_analyze_comprehensive_full(
        self, integrator: IntelligenceIntegrator, git_repo: Path
    ) -> None:
        """Test comprehensive analysis with all options.
        
        Args:
            integrator: Intelligence integrator
            git_repo: Git repository path
        """
        target = git_repo / "test.py"
        
        report = integrator.analyze_comprehensive(
            target_path=target,
            workflow=WorkflowType.SECURITY,
            include_evolution=True,
            include_consolidation=True,
        )
        
        assert report.lens_analysis is not None
        assert report.evolution_timeline is not None
        assert report.consolidation_report is not None
        assert report.registry_stats is not None
    
    def test_get_registry_summary(
        self, integrator: IntelligenceIntegrator
    ) -> None:
        """Test registry summary retrieval.
        
        Args:
            integrator: Intelligence integrator
        """
        summary = integrator.get_registry_summary()
        
        assert "total_analyzers" in summary
        assert "capabilities" in summary
        assert "languages" in summary
        assert "analyzer_names" in summary
        assert isinstance(summary["capabilities"], dict)
        assert isinstance(summary["languages"], dict)
    
    def test_get_evolution_summary(
        self, integrator: IntelligenceIntegrator
    ) -> None:
        """Test evolution summary retrieval.
        
        Args:
            integrator: Intelligence integrator
        """
        summary = integrator.get_evolution_summary(days=30)
        
        assert "total_commits" in summary
        assert "total_refactorings" in summary
        assert "tech_debt_trend" in summary
        assert "active_contributors" in summary
        assert isinstance(summary["total_commits"], int)
    
    def test_get_consolidation_summary(
        self, integrator: IntelligenceIntegrator
    ) -> None:
        """Test consolidation summary retrieval.
        
        Args:
            integrator: Intelligence integrator
        """
        summary = integrator.get_consolidation_summary()
        
        assert "total_orchestrators" in summary
        assert "target_count" in summary
        assert "reduction_percentage" in summary
        assert "sprawl_score" in summary
        assert "recommendations_count" in summary
        assert isinstance(summary["sprawl_score"], int)
    
    def test_analyze_different_workflows(
        self, integrator: IntelligenceIntegrator, git_repo: Path
    ) -> None:
        """Test analysis with different workflow types.
        
        Args:
            integrator: Intelligence integrator
            git_repo: Git repository path
        """
        target = git_repo / "test.py"
        
        workflows = [
            WorkflowType.REFACTOR,
            WorkflowType.SECURITY,
            WorkflowType.IMPLEMENTATION,
        ]
        
        for workflow in workflows:
            report = integrator.analyze_comprehensive(
                target_path=target,
                workflow=workflow,
                include_evolution=False,
                include_consolidation=False,
            )
            
            assert report.lens_analysis["workflow"] == workflow.value
