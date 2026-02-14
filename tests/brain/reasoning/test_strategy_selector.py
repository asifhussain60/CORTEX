"""
Tests for Strategy Selector - Phase 12 S3

AC-PHASE71-010: Context-aware strategy selection in reasoning layer

Tests brain reasoning layer strategy selector:
- Context-aware strategy selection
- Risk assessment based on historical outcomes
- Recommendation generation with evidence
- Strategy ranking by suitability

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from cortex_brain.reasoning.strategy_selector import (
    StrategySelector,
    Strategy,
    StrategyRecommendation,
    RiskAssessment,
)


@pytest.fixture
def selector() -> StrategySelector:
    """Create StrategySelector instance."""
    return StrategySelector()


@pytest.fixture
def sample_strategy() -> Strategy:
    """Create sample strategy."""
    return Strategy(
        id="extract_microservices",
        name="Extract Microservices",
        description="Extract bounded contexts into microservices",
        applicable_contexts=["modular_monolith", "segmented_architecture"],
        prerequisites=["clear_boundaries", "domain_knowledge"],
        risk_level="medium",
        success_rate=0.70,
        evidence=["10+ successful extractions"]
    )


class TestStrategySelectorInitialization:
    """Test StrategySelector initialization."""

    def test_initialization(self) -> None:
        """Test selector initialization."""
        selector = StrategySelector()
        assert selector is not None

    def test_starts_with_no_strategies(self, selector: StrategySelector) -> None:
        """Test selector starts with no registered strategies."""
        strategies = selector.get_all_strategies()
        assert len(strategies) == 0


class TestStrategyRegistration:
    """Test strategy registration."""

    def test_register_single_strategy(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test registering a single strategy."""
        selector.register_strategy(sample_strategy)

        strategies = selector.get_all_strategies()
        assert len(strategies) == 1

    def test_register_multiple_strategies(
        self,
        selector: StrategySelector
    ) -> None:
        """Test registering multiple strategies."""
        strategies = [
            Strategy(
                id=f"strategy_{i}",
                name=f"Strategy {i}",
                description="Test strategy",
                applicable_contexts=[f"context_{i}"],
                prerequisites=[],
                risk_level="low",
                success_rate=0.8
            )
            for i in range(5)
        ]

        for strategy in strategies:
            selector.register_strategy(strategy)

        all_strategies = selector.get_all_strategies()
        assert len(all_strategies) == 5


class TestStrategySelection:
    """Test context-aware strategy selection."""

    def test_select_strategy_for_context(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test selecting strategies for specific context."""
        selector.register_strategy(sample_strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "modular_monolith"}
        )

        assert len(recommendations) > 0
        assert recommendations[0].strategy_id == "extract_microservices"

    def test_select_returns_empty_for_no_match(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test selection returns empty when no strategies match."""
        selector.register_strategy(sample_strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "microservices"}  # Doesn't match
        )

        assert len(recommendations) == 0

    def test_select_multiple_applicable_strategies(
        self,
        selector: StrategySelector
    ) -> None:
        """Test selecting multiple applicable strategies."""
        strategies = [
            Strategy(
                id="strategy_a",
                name="Strategy A",
                description="Strategy A",
                applicable_contexts=["monolith"],
                prerequisites=[],
                risk_level="low",
                success_rate=0.9
            ),
            Strategy(
                id="strategy_b",
                name="Strategy B",
                description="Strategy B",
                applicable_contexts=["monolith"],
                prerequisites=[],
                risk_level="medium",
                success_rate=0.7
            )
        ]

        for strategy in strategies:
            selector.register_strategy(strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "monolith"}
        )

        assert len(recommendations) >= 2


class TestStrategyRanking:
    """Test strategy ranking by suitability."""

    def test_strategies_ranked_by_success_rate(
        self,
        selector: StrategySelector
    ) -> None:
        """Test strategies ranked by success rate."""
        strategies = [
            Strategy(
                id="low_success",
                name="Low Success",
                description="Low success strategy",
                applicable_contexts=["test"],
                prerequisites=[],
                risk_level="high",
                success_rate=0.5
            ),
            Strategy(
                id="high_success",
                name="High Success",
                description="High success strategy",
                applicable_contexts=["test"],
                prerequisites=[],
                risk_level="low",
                success_rate=0.9
            )
        ]

        for strategy in strategies:
            selector.register_strategy(strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "test"}
        )

        # Higher success rate should be ranked first
        assert recommendations[0].strategy_id == "high_success"

    def test_ranking_considers_risk_level(
        self,
        selector: StrategySelector
    ) -> None:
        """Test ranking considers risk level."""
        strategies = [
            Strategy(
                id="high_risk",
                name="High Risk",
                description="High risk strategy",
                applicable_contexts=["test"],
                prerequisites=[],
                risk_level="high",
                success_rate=0.8
            ),
            Strategy(
                id="low_risk",
                name="Low Risk",
                description="Low risk strategy",
                applicable_contexts=["test"],
                prerequisites=[],
                risk_level="low",
                success_rate=0.75  # Slightly lower success but lower risk
            )
        ]

        for strategy in strategies:
            selector.register_strategy(strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "test"}
        )

        # Should have both recommendations
        assert len(recommendations) == 2


class TestRiskAssessment:
    """Test risk assessment for strategies."""

    def test_assess_risk_for_strategy(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test assessing risk for a strategy."""
        selector.register_strategy(sample_strategy)

        risk = selector.assess_risk(
            strategy_id="extract_microservices",
            context={"team_size": 5, "complexity": "medium"}
        )

        assert isinstance(risk, RiskAssessment)
        assert risk.strategy_id == "extract_microservices"
        assert 0.0 <= risk.risk_score <= 1.0

    def test_risk_assessment_includes_factors(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test risk assessment includes identified risk factors."""
        selector.register_strategy(sample_strategy)

        risk = selector.assess_risk(
            strategy_id="extract_microservices",
            context={}
        )

        assert isinstance(risk.risk_factors, list)

    def test_risk_assessment_includes_mitigations(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test risk assessment includes mitigation strategies."""
        selector.register_strategy(sample_strategy)

        risk = selector.assess_risk(
            strategy_id="extract_microservices",
            context={}
        )

        assert isinstance(risk.mitigations, list)


class TestRecommendationGeneration:
    """Test recommendation generation with evidence."""

    def test_recommendation_includes_confidence(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test recommendations include confidence scores."""
        selector.register_strategy(sample_strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "modular_monolith"}
        )

        assert len(recommendations) > 0
        assert 0.0 <= recommendations[0].confidence <= 1.0

    def test_recommendation_includes_evidence(
        self,
        selector: StrategySelector,
        sample_strategy: Strategy
    ) -> None:
        """Test recommendations include supporting evidence."""
        selector.register_strategy(sample_strategy)

        recommendations = selector.select_strategies(
            context={"architecture_type": "modular_monolith"}
        )

        assert len(recommendations) > 0
        assert isinstance(recommendations[0].evidence, list)

    def test_recommendation_checks_prerequisites(
        self,
        selector: StrategySelector
    ) -> None:
        """Test recommendations check prerequisite fulfillment."""
        strategy = Strategy(
            id="advanced_strategy",
            name="Advanced Strategy",
            description="Requires prerequisites",
            applicable_contexts=["test"],
            prerequisites=["prerequisite_1", "prerequisite_2"],
            risk_level="medium",
            success_rate=0.8
        )
        selector.register_strategy(strategy)

        # Context without prerequisites
        recommendations = selector.select_strategies(
            context={"architecture_type": "test"}
        )

        # Should still recommend but note missing prerequisites
        assert len(recommendations) > 0
        assert "prerequisites" in recommendations[0].notes


class TestStrategyDataClass:
    """Test Strategy data class."""

    def test_strategy_creation(self) -> None:
        """Test creating Strategy instance."""
        strategy = Strategy(
            id="test_strategy",
            name="Test Strategy",
            description="Test description",
            applicable_contexts=["context1", "context2"],
            prerequisites=["prereq1"],
            risk_level="low",
            success_rate=0.85,
            evidence=["evidence1"]
        )

        assert strategy.id == "test_strategy"
        assert strategy.risk_level == "low"
        assert strategy.success_rate == 0.85

    def test_strategy_to_dict(self, sample_strategy: Strategy) -> None:
        """Test converting strategy to dictionary."""
        data = sample_strategy.to_dict()

        assert data["id"] == "extract_microservices"
        assert data["success_rate"] == 0.70
        assert "prerequisites" in data


class TestStrategyRecommendationDataClass:
    """Test StrategyRecommendation data class."""

    def test_recommendation_creation(self) -> None:
        """Test creating StrategyRecommendation instance."""
        rec = StrategyRecommendation(
            strategy_id="test",
            confidence=0.85,
            evidence=["reason1", "reason2"],
            notes={"key": "value"}
        )

        assert rec.strategy_id == "test"
        assert rec.confidence == 0.85
        assert len(rec.evidence) == 2

    def test_recommendation_to_dict(self) -> None:
        """Test converting recommendation to dictionary."""
        rec = StrategyRecommendation(
            strategy_id="test",
            confidence=0.9,
            evidence=["evidence"],
            notes={}
        )

        data = rec.to_dict()
        assert data["strategy_id"] == "test"
        assert data["confidence"] == 0.9


class TestRiskAssessmentDataClass:
    """Test RiskAssessment data class."""

    def test_risk_assessment_creation(self) -> None:
        """Test creating RiskAssessment instance."""
        risk = RiskAssessment(
            strategy_id="test",
            risk_score=0.65,
            risk_factors=["factor1", "factor2"],
            mitigations=["mitigation1"]
        )

        assert risk.strategy_id == "test"
        assert risk.risk_score == 0.65
        assert len(risk.risk_factors) == 2

    def test_risk_assessment_to_dict(self) -> None:
        """Test converting risk assessment to dictionary."""
        risk = RiskAssessment(
            strategy_id="test",
            risk_score=0.5,
            risk_factors=[],
            mitigations=[]
        )

        data = risk.to_dict()
        assert data["strategy_id"] == "test"
        assert data["risk_score"] == 0.5


class TestContextMatching:
    """Test context matching logic."""

    def test_fuzzy_context_matching(
        self,
        selector: StrategySelector
    ) -> None:
        """Test fuzzy matching for context values."""
        strategy = Strategy(
            id="test",
            name="Test",
            description="Test",
            applicable_contexts=["modular_monolith"],
            prerequisites=[],
            risk_level="low",
            success_rate=0.8
        )
        selector.register_strategy(strategy)

        # Slightly different naming
        recommendations = selector.select_strategies(
            context={"architecture_type": "modular monolith"}  # Space instead of underscore
        )

        assert len(recommendations) > 0

    def test_partial_context_matching(
        self,
        selector: StrategySelector
    ) -> None:
        """Test partial context matching."""
        strategy = Strategy(
            id="test",
            name="Test",
            description="Test",
            applicable_contexts=["monolith"],
            prerequisites=[],
            risk_level="low",
            success_rate=0.8
        )
        selector.register_strategy(strategy)

        # Substring match
        recommendations = selector.select_strategies(
            context={"architecture_type": "modular_monolith"}  # Contains "monolith"
        )

        assert len(recommendations) > 0
