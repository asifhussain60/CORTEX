"""
Solution Recommendation Engine - Marks best solution option for CORTEX.

AC-RECOMMENDATION-001: Intelligent solution ranking and marking system
Integrates with ConversationProtocol to:
- Evaluate multiple solution options
- Score based on CORTEX governance and best practices
- Mark the best option for recommendation
- Present other options with confidence scores
- Track recommendation acceptance

Author: CORTEX Framework
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RecommendationConfidence(Enum):
    """Confidence levels for recommendations."""
    HIGH = "high"  # 80%+ confidence, strongly recommended
    MEDIUM = "medium"  # 60-80% confidence, recommended
    LOW = "low"  # 40-60% confidence, consider alternatives
    UNCERTAIN = "uncertain"  # <40% confidence, all options viable


@dataclass
class SolutionOption:
    """A single solution option with evaluation metrics."""

    option_id: str
    name: str
    description: str
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    maintenance_cost: str  # "low", "medium", "high"
    cortex_alignment: float  # 0.0-1.0: How well aligned with CORTEX patterns
    governance_compliance: float  # 0.0-1.0: Compliance with CORE rules
    performance_impact: float  # 0.0-1.0: Performance (1.0 = best)
    scalability_score: float  # 0.0-1.0: Scalability potential
    team_familiarity: float  # 0.0-1.0: How familiar team is with tech
    technical_debt: float  # 0.0-1.0: Inverse of technical debt (1.0 = no debt)

    # Metadata
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeline_estimate: Optional[str] = None
    estimated_cost: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class RecommendedSolution:
    """A recommendation with the best option marked."""

    best_option_id: str
    best_option: SolutionOption
    confidence: RecommendationConfidence
    reasoning: str
    all_options: List[SolutionOption]
    option_scores: Dict[str, float] = field(default_factory=dict)
    summary: str = ""
    user_override_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "best_option": {
                "option_id": self.best_option.option_id,
                "name": self.best_option.name,
                "description": self.best_option.description,
                "marked_as": "⭐ RECOMMENDED BY CORTEX",
            },
            "confidence": self.confidence.value,
            "reasoning": self.reasoning,
            "summary": self.summary,
            "alternative_options": [
                {
                    "option_id": opt.option_id,
                    "name": opt.name,
                    "description": opt.description,
                    "score": self.option_scores.get(opt.option_id, 0.0),
                    "why_not_recommended": f"Score: {self.option_scores.get(opt.option_id, 0.0):.2f} vs best: {self.option_scores.get(self.best_option_id, 0.0):.2f}",
                }
                for opt in self.all_options
                if opt.option_id != self.best_option_id
            ],
            "user_can_override": self.user_override_enabled,
        }


class SolutionRecommendationEngine:
    """
    Evaluates multiple solution options and marks the best one.

    Scoring Factors (weighted):
    - CORTEX alignment: 25%
    - Governance compliance: 20%
    - Implementation effort: 15%
    - Risk level: 15%
    - Performance/scalability: 10%
    - Maintenance cost: 10%
    - Team familiarity: 5%
    """

    # Weights for scoring (must sum to 1.0)
    WEIGHTS = {
        "cortex_alignment": 0.25,
        "governance_compliance": 0.20,
        "implementation_effort": 0.15,  # Lower effort = higher score
        "risk_level": 0.15,  # Lower risk = higher score
        "performance_impact": 0.10,
        "scalability_score": 0.05,
        "team_familiarity": 0.05,
        "technical_debt": 0.05,
    }

    def __init__(self):
        """Initialize the recommendation engine."""
        self.evaluated_options: Dict[str, SolutionOption] = {}
        self.recommendations: List[RecommendedSolution] = []

    def score_option(self, option: SolutionOption) -> float:
        """
        Calculate composite score for a solution option.

        Returns:
            Float between 0.0 and 1.0, where 1.0 is best.
        """
        # Convert categorical scores to numeric (0.0-1.0)
        effort_score = self._effort_to_score(option.implementation_effort)
        risk_score = self._risk_to_score(option.risk_level)

        # Calculate weighted score
        score = (
            option.cortex_alignment * self.WEIGHTS["cortex_alignment"] +
            option.governance_compliance * self.WEIGHTS["governance_compliance"] +
            effort_score * self.WEIGHTS["implementation_effort"] +
            risk_score * self.WEIGHTS["risk_level"] +
            option.performance_impact * self.WEIGHTS["performance_impact"] +
            option.scalability_score * self.WEIGHTS["scalability_score"] +
            option.team_familiarity * self.WEIGHTS["team_familiarity"] +
            option.technical_debt * self.WEIGHTS["technical_debt"]
        )

        return round(score, 3)

    def _effort_to_score(self, effort: str) -> float:
        """Convert effort level to score (low effort = high score)."""
        mapping = {
            "low": 1.0,
            "medium": 0.6,
            "high": 0.2,
        }
        return mapping.get(effort.lower(), 0.5)

    def _risk_to_score(self, risk: str) -> float:
        """Convert risk level to score (low risk = high score)."""
        mapping = {
            "low": 1.0,
            "medium": 0.6,
            "high": 0.2,
        }
        return mapping.get(risk.lower(), 0.5)

    def recommend_best_option(
        self,
        options: List[SolutionOption],
        context: Optional[Dict[str, Any]] = None
    ) -> RecommendedSolution:
        """
        Evaluate options and return recommendation with best option marked.

        Args:
            options: List of solution options to evaluate
            context: Optional context for decision-making

        Returns:
            RecommendedSolution with best option marked as ⭐ RECOMMENDED BY CORTEX
        """
        if not options:
            raise ValueError("Must provide at least one option")

        # Score all options
        scores = {}
        for option in options:
            score = self.score_option(option)
            scores[option.option_id] = score
            self.evaluated_options[option.option_id] = option

        # Find best option
        best_option_id = max(scores, key=scores.get)
        best_option = next(opt for opt in options if opt.option_id == best_option_id)
        best_score = scores[best_option_id]

        # Determine confidence level
        confidence = self._determine_confidence(best_score, scores, options)

        # Build reasoning
        reasoning = self._build_reasoning(
            best_option, best_score, scores, options, confidence
        )

        # Create recommendation
        recommendation = RecommendedSolution(
            best_option_id=best_option_id,
            best_option=best_option,
            confidence=confidence,
            reasoning=reasoning,
            all_options=options,
            option_scores=scores,
            summary=self._build_summary(best_option, confidence),
        )

        self.recommendations.append(recommendation)
        logger.info(
            f"Recommendation: {best_option.name} (score: {best_score:.2f}, "
            f"confidence: {confidence.value})"
        )

        return recommendation

    def _determine_confidence(
        self,
        best_score: float,
        scores: Dict[str, float],
        options: List[SolutionOption]
    ) -> RecommendationConfidence:
        """Determine confidence level based on score spread."""
        if not options or len(options) < 2:
            return RecommendationConfidence.HIGH

        other_scores = [s for oid, s in scores.items() if oid != list(scores.keys())[0]]
        if not other_scores:
            return RecommendationConfidence.HIGH

        # Calculate score gap (best - second best)
        second_best = max(other_scores)
        gap = best_score - second_best

        if gap >= 0.3:
            return RecommendationConfidence.HIGH
        elif gap >= 0.15:
            return RecommendationConfidence.MEDIUM
        elif gap >= 0.05:
            return RecommendationConfidence.LOW
        else:
            return RecommendationConfidence.UNCERTAIN

    def _build_reasoning(
        self,
        best_option: SolutionOption,
        best_score: float,
        scores: Dict[str, float],
        options: List[SolutionOption],
        confidence: RecommendationConfidence
    ) -> str:
        """Build detailed reasoning for the recommendation."""
        reasoning_parts = [
            f"✅ CORTEX Recommendation: {best_option.name}",
            "",
            f"Confidence: {confidence.value.upper()}",
            f"Overall Score: {best_score:.2f}/1.0",
            "",
            "Key Strengths:",
        ]

        # Add strengths
        if best_option.pros:
            for pro in best_option.pros[:3]:  # Top 3 pros
                reasoning_parts.append(f"  • {pro}")

        # Add scoring breakdown
        reasoning_parts.extend([
            "",
            "Scoring Breakdown:",
            f"  • CORTEX Alignment: {best_option.cortex_alignment:.0%}",
            f"  • Governance Compliance: {best_option.governance_compliance:.0%}",
            f"  • Implementation Effort: {best_option.implementation_effort}",
            f"  • Risk Level: {best_option.risk_level}",
            f"  • Performance Impact: {best_option.performance_impact:.0%}",
        ])

        # Add comparison if other options exist
        if len(options) > 1:
            reasoning_parts.append("")
            reasoning_parts.append("Why not the alternatives?")
            for opt in options:
                if opt.option_id != best_option.option_id:
                    score = scores.get(opt.option_id, 0.0)
                    gap = best_score - score
                    reasoning_parts.append(
                        f"  • {opt.name}: Score {score:.2f} (-{gap:.2f})"
                    )

        return "\n".join(reasoning_parts)

    def _build_summary(
        self,
        best_option: SolutionOption,
        confidence: RecommendationConfidence
    ) -> str:
        """Build concise summary of recommendation."""
        confidence_emoji = {
            RecommendationConfidence.HIGH: "🟢",
            RecommendationConfidence.MEDIUM: "🟡",
            RecommendationConfidence.LOW: "🟠",
            RecommendationConfidence.UNCERTAIN: "⚪",
        }

        return (
            f"{confidence_emoji[confidence]} CORTEX Recommends: {best_option.name}\n"
            f"Implementation: {best_option.implementation_effort} effort\n"
            f"Risk: {best_option.risk_level} | Timeline: {best_option.timeline_estimate or 'TBD'}"
        )


# Module-level singleton
_engine_instance: Optional[SolutionRecommendationEngine] = None


def get_recommendation_engine() -> SolutionRecommendationEngine:
    """Get or create recommendation engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SolutionRecommendationEngine()
    return _engine_instance


__all__ = [
    "SolutionRecommendationEngine",
    "SolutionOption",
    "RecommendedSolution",
    "RecommendationConfidence",
    "get_recommendation_engine",
]
