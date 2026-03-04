"""
Strategy Selector - Phase 12 S3 (Brain Reasoning Layer)

AC-PHASE71-010: Context-aware strategy selection in reasoning layer

Brain reasoning layer that:
- Selects strategies based on repository context
- Assesses risks using historical outcomes
- Generates recommendations with evidence
- Ranks strategies by suitability and success rate

Used by learning loop to provide intelligent strategy recommendations.

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Strategy:
    """Strategy registered in reasoning layer."""

    id: str
    name: str
    description: str
    applicable_contexts: List[str]
    prerequisites: List[str]
    risk_level: str  # "low", "medium", "high"
    success_rate: float
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "applicable_contexts": self.applicable_contexts,
            "prerequisites": self.prerequisites,
            "risk_level": self.risk_level,
            "success_rate": self.success_rate,
            "evidence": self.evidence,
        }


@dataclass
class StrategyRecommendation:
    """Strategy recommendation with confidence and evidence."""

    strategy_id: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    notes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "strategy_id": self.strategy_id,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "notes": self.notes,
        }


@dataclass
class RiskAssessment:
    """Risk assessment for a strategy."""

    strategy_id: str
    risk_score: float
    risk_factors: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "strategy_id": self.strategy_id,
            "risk_score": self.risk_score,
            "risk_factors": self.risk_factors,
            "mitigations": self.mitigations,
        }


class StrategySelector:
    """
    Brain reasoning layer strategy selector.

    Selects optimal strategies based on context, assesses risks,
    and generates evidence-based recommendations.

    AC-PHASE71-010: Context-aware strategy selection
    """

    def __init__(self) -> None:
        """Initialize strategy selector."""
        self._strategies: Dict[str, Strategy] = {}

        # Risk level to score mapping
        self._risk_scores = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }

    def register_strategy(self, strategy: Strategy) -> None:
        """
        Register a strategy in the selector.

        Args:
            strategy: Strategy to register
        """
        self._strategies[strategy.id] = strategy
        logger.debug(f"Registered strategy: {strategy.id}")

    def get_all_strategies(self) -> List[Strategy]:
        """
        Get all registered strategies.

        Returns:
            List of all Strategy objects
        """
        return list(self._strategies.values())

    def select_strategies(
        self,
        context: Dict[str, Any]
    ) -> List[StrategyRecommendation]:
        """
        Select strategies applicable to given context.

        Args:
            context: Repository/project context

        Returns:
            List of StrategyRecommendation sorted by confidence
        """
        recommendations: List[StrategyRecommendation] = []

        for strategy in self._strategies.values():
            match_score = self._match_context(strategy, context)

            if match_score > 0.0:
                # Calculate confidence
                confidence = self._calculate_confidence(strategy, context, match_score)

                # Build evidence
                evidence = self._build_evidence(strategy, context)

                # Check prerequisites
                notes = {}
                missing_prereqs = self._check_prerequisites(strategy, context)
                if missing_prereqs:
                    notes["prerequisites"] = f"Missing: {', '.join(missing_prereqs)}"

                recommendation = StrategyRecommendation(
                    strategy_id=strategy.id,
                    confidence=confidence,
                    evidence=evidence,
                    notes=notes
                )
                recommendations.append(recommendation)

        # Sort by confidence descending
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        logger.debug(f"Selected {len(recommendations)} strategies for context")
        return recommendations

    def assess_risk(
        self,
        strategy_id: str,
        context: Dict[str, Any]
    ) -> RiskAssessment:
        """
        Assess risk for applying a strategy.

        Args:
            strategy_id: ID of strategy to assess
            context: Current context

        Returns:
            RiskAssessment for the strategy
        """
        strategy = self._strategies.get(strategy_id)
        if not strategy:
            return RiskAssessment(
                strategy_id=strategy_id,
                risk_score=1.0,
                risk_factors=["Unknown strategy"],
                mitigations=[]
            )

        # Base risk from strategy
        base_risk = self._risk_scores.get(strategy.risk_level, 0.5)

        # Adjust based on success rate (lower success = higher risk)
        success_adjustment = (1.0 - strategy.success_rate) * 0.3
        risk_score = min(base_risk + success_adjustment, 1.0)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(strategy, context)

        # Suggest mitigations
        mitigations = self._suggest_mitigations(strategy, risk_factors)

        return RiskAssessment(
            strategy_id=strategy_id,
            risk_score=risk_score,
            risk_factors=risk_factors,
            mitigations=mitigations
        )

    def _match_context(
        self,
        strategy: Strategy,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate how well strategy matches context.

        Args:
            strategy: Strategy to match
            context: Context to match against

        Returns:
            Match score (0.0-1.0)
        """
        if not context:
            return 0.0

        # Check if any applicable context matches
        context_values = [str(v).lower() for v in context.values()]

        matches = 0
        for applicable in strategy.applicable_contexts:
            applicable_lower = applicable.lower()

            for context_value in context_values:
                # Exact match
                if applicable_lower == context_value:
                    matches += 1
                    break
                # Substring match (fuzzy)
                elif applicable_lower in context_value or context_value in applicable_lower:
                    matches += 0.7
                    break
                # Replace underscores/dashes (normalization)
                elif applicable_lower.replace("_", " ") == context_value.replace("_", " "):
                    matches += 0.9
                    break

        if not strategy.applicable_contexts:
            return 0.0

        return min(matches / len(strategy.applicable_contexts), 1.0)

    def _calculate_confidence(
        self,
        strategy: Strategy,
        context: Dict[str, Any],
        match_score: float
    ) -> float:
        """Calculate confidence for strategy recommendation."""
        # Base confidence from match score
        confidence = match_score * 0.5

        # Add success rate component
        confidence += strategy.success_rate * 0.4

        # Reduce based on risk level
        risk_penalty = self._risk_scores.get(strategy.risk_level, 0.5) * 0.1
        confidence -= risk_penalty

        return min(max(confidence, 0.0), 1.0)

    def _build_evidence(
        self,
        strategy: Strategy,
        context: Dict[str, Any]
    ) -> List[str]:
        """Build evidence list for recommendation."""
        evidence = []

        # Add strategy's inherent evidence
        evidence.extend(strategy.evidence)

        # Add success rate evidence
        if strategy.success_rate > 0.7:
            evidence.append(f"High success rate: {strategy.success_rate:.0%}")

        # Add context match evidence
        evidence.append("Applicable to current architecture")

        return evidence

    def _check_prerequisites(
        self,
        strategy: Strategy,
        context: Dict[str, Any]
    ) -> List[str]:
        """Check which prerequisites are missing."""
        missing = []

        for prereq in strategy.prerequisites:
            # Simple check: is prerequisite mentioned in context?
            prereq_lower = prereq.lower()
            found = any(
                prereq_lower in str(v).lower()
                for v in context.values()
            )

            if not found:
                missing.append(prereq)

        return missing

    def _identify_risk_factors(
        self,
        strategy: Strategy,
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify risk factors for strategy application."""
        risk_factors = []

        # Base risk level
        if strategy.risk_level == "high":
            risk_factors.append("Inherently high-risk strategy")

        # Low success rate
        if strategy.success_rate < 0.6:
            risk_factors.append("Below 60% historical success rate")

        # Missing prerequisites
        missing_prereqs = self._check_prerequisites(strategy, context)
        if missing_prereqs:
            risk_factors.append(f"Missing prerequisites: {', '.join(missing_prereqs[:2])}")

        # Complexity indicators in context
        if context.get("complexity") == "high":
            risk_factors.append("High system complexity")

        return risk_factors

    def _suggest_mitigations(
        self,
        strategy: Strategy,
        risk_factors: List[str]
    ) -> List[str]:
        """Suggest risk mitigation strategies."""
        mitigations = []

        if "prerequisite" in " ".join(risk_factors).lower():
            mitigations.append("Ensure all prerequisites are met before proceeding")

        if "success rate" in " ".join(risk_factors).lower():
            mitigations.append("Conduct pilot test on small subset first")

        if strategy.risk_level == "high":
            mitigations.append("Implement comprehensive monitoring and rollback plan")

        if "complexity" in " ".join(risk_factors).lower():
            mitigations.append("Break down into smaller incremental changes")

        return mitigations

    def select(
        self,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Select the best strategy for a given intent.

        GAP-57-09: Simple facade for IntentRouter routing-confidence calculation.
        Returns the top-ranked strategy ID or a default based on intent.

        Args:
            intent: Intent string (IMPLEMENT, FIX, REFACTOR, …).
            context: Optional context dict passed from IntentRouter.

        Returns:
            Strategy ID string (non-empty, never raises).

        Authority: AC-PHASE57-F-001
        """
        ctx = context or {}
        # Enrich context with intent so _match_context can use it
        ctx_with_intent = {**ctx, "intent": intent}
        recommendations = self.select_strategies(ctx_with_intent)
        if recommendations:
            return recommendations[0].strategy_id
        # Default strategy per intent
        defaults = {
            "IMPLEMENT": "tdd_first",
            "FIX": "minimal_change",
            "REFACTOR": "incremental",
            "AUDIT": "exhaustive_scan",
        }
        return defaults.get(intent.upper(), "direct_execution")


# Singleton accessor
_selector_instance: Optional[StrategySelector] = None


def get_strategy_selector() -> StrategySelector:
    """
    Get singleton StrategySelector instance.

    Returns:
        Singleton StrategySelector instance
    """
    global _selector_instance

    if _selector_instance is None:
        _selector_instance = StrategySelector()

    return _selector_instance
