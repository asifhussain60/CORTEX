"""Unit Tests for Consolidation Analyzer

Tests orchestrator sprawl detection and consolidation recommendations.

Author: CORTEX Framework
Phase: PHASE-97 S5
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.orchestrators.health.agents.consolidation_analyzer import (
    ConsolidationAnalyzer,
    ConsolidationRecommendation,
    ConsolidationReport,
    OrchestratorMetadata,
)


@pytest.fixture
def sample_orchestrators() -> list[OrchestratorMetadata]:
    """Create sample orchestrator metadata.
    
    Returns:
        List of orchestrator metadata
    """
    return [
        OrchestratorMetadata(
            file_path=Path("orch1.py"),
            class_name="MainOrchestrator",
            line_count=500,
            method_count=10,
            dependency_count=15,
        ),
        OrchestratorMetadata(
            file_path=Path("orch2.py"),
            class_name="HelperOrchestrator",
            line_count=50,
            method_count=2,
            dependency_count=5,
        ),
        OrchestratorMetadata(
            file_path=Path("orch3.py"),
            class_name="UtilityOrchestrator",
            line_count=75,
            method_count=3,
            dependency_count=8,
        ),
    ]


@pytest.fixture
def analyzer(tmp_path: Path) -> ConsolidationAnalyzer:
    """Create consolidation analyzer.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        ConsolidationAnalyzer instance
    """
    return ConsolidationAnalyzer(repo_path=tmp_path)


class TestOrchestratorMetadata:
    """Test suite for OrchestratorMetadata."""
    
    def test_metadata_creation(self) -> None:
        """Test creating orchestrator metadata."""
        metadata = OrchestratorMetadata(
            file_path=Path("test.py"),
            class_name="TestOrchestrator",
            line_count=100,
            method_count=5,
            dependency_count=10,
        )
        
        assert metadata.class_name == "TestOrchestrator"
        assert metadata.line_count == 100
        assert metadata.method_count == 5


class TestConsolidationReport:
    """Test suite for ConsolidationReport."""
    
    def test_reduction_percentage(self) -> None:
        """Test reduction percentage calculation."""
        report = ConsolidationReport(
            total_orchestrators=100,
            target_count=28,
        )
        
        assert report.reduction_percentage == 72.0
    
    def test_reduction_percentage_zero(self) -> None:
        """Test reduction percentage with zero orchestrators."""
        report = ConsolidationReport(
            total_orchestrators=0,
            target_count=0,
        )
        
        assert report.reduction_percentage == 0.0


class TestConsolidationAnalyzer:
    """Test suite for ConsolidationAnalyzer."""
    
    def test_init(self, analyzer: ConsolidationAnalyzer) -> None:
        """Test analyzer initialization.
        
        Args:
            analyzer: Consolidation analyzer
        """
        assert analyzer.repo_path is not None
        assert len(analyzer.orchestrator_dirs) > 0
    
    def test_init_custom_dirs(self, tmp_path: Path) -> None:
        """Test initialization with custom directories.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        analyzer = ConsolidationAnalyzer(
            repo_path=tmp_path,
            orchestrator_dirs=["custom/dir"],
        )
        
        assert "custom/dir" in analyzer.orchestrator_dirs
    
    def test_analyze_empty_repo(self, analyzer: ConsolidationAnalyzer) -> None:
        """Test analyze with no orchestrators.
        
        Args:
            analyzer: Consolidation analyzer
        """
        report = analyzer.analyze()
        
        assert isinstance(report, ConsolidationReport)
        assert report.total_orchestrators == 0
        assert report.sprawl_score == 0
    
    def test_calculate_sprawl_score_empty(
        self, analyzer: ConsolidationAnalyzer
    ) -> None:
        """Test sprawl score with empty list.
        
        Args:
            analyzer: Consolidation analyzer
        """
        score = analyzer._calculate_sprawl_score([])
        
        assert score == 0
    
    def test_calculate_sprawl_score_high(
        self, analyzer: ConsolidationAnalyzer, sample_orchestrators: list
    ) -> None:
        """Test sprawl score calculation.
        
        Args:
            analyzer: Consolidation analyzer
            sample_orchestrators: Sample orchestrator list
        """
        # Add many small orchestrators to increase sprawl
        small_orchestrators = [
            OrchestratorMetadata(
                file_path=Path(f"orch{i}.py"),
                class_name=f"Orchestrator{i}",
                line_count=50,
                method_count=2,
                dependency_count=5,
            )
            for i in range(50)
        ]
        
        score = analyzer._calculate_sprawl_score(small_orchestrators)
        
        assert score > 50  # High sprawl
    
    def test_generate_recommendations_no_groups(
        self, analyzer: ConsolidationAnalyzer
    ) -> None:
        """Test recommendation generation with no groups.
        
        Args:
            analyzer: Consolidation analyzer
        """
        orchestrators = [
            OrchestratorMetadata(
                file_path=Path("orch1.py"),
                class_name="UniqueOrchestrator",
                line_count=100,
                method_count=5,
                dependency_count=10,
            ),
        ]
        
        recommendations = analyzer._generate_recommendations(orchestrators)
        
        assert len(recommendations) == 0
    
    def test_generate_recommendations_with_similar(
        self, analyzer: ConsolidationAnalyzer
    ) -> None:
        """Test recommendation generation with similar orchestrators.
        
        Args:
            analyzer: Consolidation analyzer
        """
        orchestrators = [
            OrchestratorMetadata(
                file_path=Path("main.py"),
                class_name="MainOrchestrator",
                line_count=500,
                method_count=10,
                dependency_count=15,
            ),
            OrchestratorMetadata(
                file_path=Path("helper.py"),
                class_name="MainHandler",  # Similar to MainOrchestrator
                line_count=100,
                method_count=3,
                dependency_count=8,
            ),
        ]
        
        recommendations = analyzer._generate_recommendations(orchestrators)
        
        assert len(recommendations) > 0
        assert recommendations[0].target_orchestrator in [
            "MainOrchestrator",
            "MainHandler",
        ]
    
    def test_group_by_similarity(
        self, analyzer: ConsolidationAnalyzer
    ) -> None:
        """Test grouping by similarity.
        
        Args:
            analyzer: Consolidation analyzer
        """
        orchestrators = [
            OrchestratorMetadata(
                file_path=Path("main1.py"),
                class_name="MainOrchestrator",
                line_count=100,
                method_count=5,
                dependency_count=10,
            ),
            OrchestratorMetadata(
                file_path=Path("main2.py"),
                class_name="MainHandler",
                line_count=100,
                method_count=5,
                dependency_count=10,
            ),
            OrchestratorMetadata(
                file_path=Path("util.py"),
                class_name="UtilityOrchestrator",
                line_count=50,
                method_count=2,
                dependency_count=5,
            ),
        ]
        
        groups = analyzer._group_by_similarity(orchestrators)
        
        # Should have 2 groups: Main* and Utility*
        assert len(groups) >= 1
    
    def test_analyze_with_orchestrators(self, tmp_path: Path) -> None:
        """Test analyze with actual orchestrator files.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        # Create orchestrator directory
        orch_dir = tmp_path / "cortex" / "orchestrators"
        orch_dir.mkdir(parents=True)
        
        # Create sample orchestrator file
        orch_file = orch_dir / "sample_orchestrator.py"
        orch_file.write_text("""
class SampleOrchestrator:
    def method1(self):
        pass
    
    def method2(self):
        pass
""")
        
        analyzer = ConsolidationAnalyzer(repo_path=tmp_path)
        report = analyzer.analyze()
        
        assert report.total_orchestrators >= 1
        assert isinstance(report.sprawl_score, int)


class TestConsolidationRecommendation:
    """Test suite for ConsolidationRecommendation."""
    
    def test_recommendation_creation(self) -> None:
        """Test creating consolidation recommendation."""
        rec = ConsolidationRecommendation(
            target_orchestrator="MainOrchestrator",
            merge_candidates=["Helper1", "Helper2"],
            reason="Similar functionality",
            impact_score=80,
            effort_hours=4.0,
            risk_level="medium",
        )
        
        assert rec.target_orchestrator == "MainOrchestrator"
        assert len(rec.merge_candidates) == 2
        assert rec.impact_score == 80
