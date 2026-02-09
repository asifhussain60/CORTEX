"""
AC-054A-S1-07,08,09: GenerateBusinessNarrativeUseCase Tests

TDD Test Suite (6+ tests):
- AC-054A-S1-07: Use case generates business narratives
- AC-054A-S1-08: Delegates to BusinessLanguageOrchestrator
- AC-054A-S1-09: 6+ unit tests with confidence scores

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from dataclasses import dataclass
from typing import Optional


@dataclass
class BusinessNarrative:
    """Business narrative model."""
    title: str
    summary: str
    key_insights: list
    target_audience: str
    confidence_score: float  # 0.0-1.0


class TestGenerateBusinessNarrativeUseCase:
    """Test business narrative generation from repository analysis."""

    @pytest.fixture
    def use_case(self):
        """Initialize GenerateBusinessNarrativeUseCase."""
        from cortex.orchestrators.support.onboarding_use_cases import GenerateBusinessNarrativeUseCase
        return GenerateBusinessNarrativeUseCase()

    @pytest.fixture
    def repo_analysis(self) -> dict:
        """Fixture: Repository analysis data."""
        return {
            "name": "ml-framework",
            "description": "Machine learning framework for data science",
            "language": "Python",
            "stars": 5000,
            "forks": 800,
            "contributors": 250,
            "key_files": ["core/model.py", "core/training.py", "utils/preprocessing.py"],
            "dependencies": ["numpy", "pandas", "scikit-learn"],
            "metrics": {
                "test_coverage": 0.87,
                "readme_quality": 0.92,
                "documentation_completeness": 0.80,
            },
        }

    def test_generates_narrative(self, use_case, repo_analysis):
        """AC-054A-S1-07a: Generates business narrative."""
        narrative = use_case.execute(repo_analysis)
        
        assert isinstance(narrative, BusinessNarrative)
        assert len(narrative.title) > 0
        assert len(narrative.summary) > 0

    def test_includes_key_insights(self, use_case, repo_analysis):
        """AC-054A-S1-07b: Includes key business insights."""
        narrative = use_case.execute(repo_analysis)
        
        assert len(narrative.key_insights) > 0
        assert all(isinstance(i, str) for i in narrative.key_insights)

    def test_identifies_target_audience(self, use_case, repo_analysis):
        """AC-054A-S1-07c: Identifies target audience."""
        narrative = use_case.execute(repo_analysis)
        
        assert narrative.target_audience in [
            "Data Scientists",
            "Backend Engineers",
            "DevOps",
            "Frontend Developers",
            "General Audience",
        ]

    def test_delegates_to_business_language_orchestrator(self):
        """AC-054A-S1-08: Delegates to BusinessLanguageOrchestrator."""
        from cortex.orchestrators.support.onboarding_use_cases import GenerateBusinessNarrativeUseCase
        
        use_case = GenerateBusinessNarrativeUseCase()
        assert hasattr(use_case, 'business_language_orchestrator')

    def test_confidence_score_ranges_0_to_1(self, use_case, repo_analysis):
        """AC-054A-S1-09a: Confidence score between 0-1."""
        narrative = use_case.execute(repo_analysis)
        
        assert 0.0 <= narrative.confidence_score <= 1.0

    def test_high_confidence_for_well_documented_repo(self, use_case):
        """AC-054A-S1-09b: High confidence for well-documented repos."""
        well_documented = {
            "name": "documented-repo",
            "description": "Clear description here",
            "readme_quality": 0.95,
            "documentation_completeness": 0.90,
            "stars": 1000,
            "contributors": 50,
        }
        narrative = use_case.execute(well_documented)
        
        assert narrative.confidence_score > 0.75

    def test_lower_confidence_for_poorly_documented_repo(self, use_case):
        """AC-054A-S1-09c: Lower confidence for poorly-documented repos."""
        poorly_documented = {
            "name": "undocumented-repo",
            "description": "",
            "readme_quality": 0.30,
            "documentation_completeness": 0.20,
            "stars": 10,
            "contributors": 2,
        }
        narrative = use_case.execute(poorly_documented)
        
        assert narrative.confidence_score < 0.60
