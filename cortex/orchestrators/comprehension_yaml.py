"""
ComprehensionYAML - YAML-serializable representation of comprehension output.

AC-ID: AC-INTENT-005-01
Phase: REMEDIATION-INTENT-005-COMPREHENSION-YAML
Purpose: Structured data model for intent comprehension output

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class IntentSection:
    """
    Intent understanding from comprehension.

    Attributes:
        type: Intent type (IMPLEMENT, FIX, REFACTOR, etc.)
        scope: Target scope (file, module, system)
        confidence: Confidence score (0-1)
        keywords: Keywords extracted from input
    """
    type: str
    scope: Dict[str, Any]
    confidence: float
    keywords: List[str] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate intent section."""
        if not self.type:
            return False
        if not 0 <= self.confidence <= 1:
            return False
        if not self.scope:
            return False
        return True


@dataclass
class ChallengeItem:
    """
    Single challenge/risk identified during analysis.

    Attributes:
        category: Challenge category
        severity: Challenge severity (CRITICAL, HIGH, MEDIUM, LOW)
        description: Description of challenge
        affected_scope: List of affected scopes
        evidence: List of evidence items
        mitigation: Mitigation strategy
        confidence: Confidence in challenge detection
    """
    category: str
    severity: str
    description: str
    affected_scope: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    mitigation: str = ""
    confidence: float = 1.0


@dataclass
class ChallengeSection:
    """
    Container for challenges identified during comprehension.

    Attributes:
        challenges: List of ChallengeItem objects
        summary: Summary of challenges
    """
    challenges: List[ChallengeItem] = field(default_factory=list)
    summary: str = ""

    def add_challenge(self, challenge: ChallengeItem) -> None:
        """Add a challenge to the section."""
        self.challenges.append(challenge)

    def get_by_severity(self, severity: str) -> List[ChallengeItem]:
        """Get challenges by severity level."""
        return [c for c in self.challenges if c.severity == severity]


@dataclass
class RecommendationItem:
    """
    Single recommendation for addressing identified issues.

    Attributes:
        title: Recommendation title
        description: Detailed description
        priority: Priority level (HIGH, MEDIUM, LOW)
        evidence: Supporting evidence
        confidence: Confidence score
    """
    title: str
    description: str
    priority: str = "MEDIUM"
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class RecommendationSection:
    """
    Container for recommendations.

    Attributes:
        recommendations: List of RecommendationItem objects
        confidence: Overall confidence in recommendations
    """
    recommendations: List[RecommendationItem] = field(default_factory=list)
    confidence: float = 1.0

    def add_recommendation(self, rec: RecommendationItem) -> None:
        """Add a recommendation to the section."""
        self.recommendations.append(rec)


@dataclass
class ComprehensionYAML:
    """
    YAML-serializable comprehension output.

    Contains structured representation of intent comprehension with
    metadata, intent analysis, challenges, and recommendations.

    Attributes:
        metadata: Metadata about comprehension
        intent: IntentSection with intent analysis
        challenges: ChallengeSection with identified risks
        recommendations: RecommendationSection with recommendations
    """
    metadata: Dict[str, Any]
    intent: IntentSection
    challenges: ChallengeSection = field(default_factory=ChallengeSection)
    recommendations: RecommendationSection = field(default_factory=RecommendationSection)

    def validate(self) -> bool:
        """
        Validate comprehension structure.

        Returns:
            True if valid, False otherwise
        """
        if not self.metadata:
            return False
        if not self.intent.validate():
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "metadata": self.metadata,
            "intent": asdict(self.intent),
            "challenges": {
                "challenges": [asdict(c) for c in self.challenges.challenges],
                "summary": self.challenges.summary,
            },
            "recommendations": {
                "recommendations": [asdict(r) for r in self.recommendations.recommendations],
                "confidence": self.recommendations.confidence,
            },
        }

    def to_yaml(self) -> str:
        """
        Convert to YAML string.

        Returns:
            YAML representation
        """
        data = self.to_dict()
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComprehensionYAML:
        """
        Create ComprehensionYAML from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ComprehensionYAML instance

        Raises:
            ValueError: If data is invalid
        """
        if not data or not isinstance(data, dict):
            raise ValueError("Data must be a non-empty dictionary")

        metadata = data.get("metadata", {})
        intent_data = data.get("intent", {})

        intent = IntentSection(
            type=intent_data.get("type", "UNKNOWN"),
            scope=intent_data.get("scope", {}),
            confidence=intent_data.get("confidence", 0.0),
            keywords=intent_data.get("keywords", []),
        )

        challenges_data = data.get("challenges", {})
        challenges = ChallengeSection(
            summary=challenges_data.get("summary", ""),
        )
        for c in challenges_data.get("challenges", []):
            challenges.add_challenge(ChallengeItem(
                category=c.get("category", ""),
                severity=c.get("severity", ""),
                description=c.get("description", ""),
                affected_scope=c.get("affected_scope", []),
                evidence=c.get("evidence", []),
                mitigation=c.get("mitigation", ""),
                confidence=c.get("confidence", 1.0),
            ))

        recommendations_data = data.get("recommendations", {})
        recommendations = RecommendationSection(
            confidence=recommendations_data.get("confidence", 1.0),
        )
        for r in recommendations_data.get("recommendations", []):
            recommendations.add_recommendation(RecommendationItem(
                title=r.get("title", ""),
                description=r.get("description", ""),
                priority=r.get("priority", "MEDIUM"),
                evidence=r.get("evidence", []),
                confidence=r.get("confidence", 1.0),
            ))

        return cls(
            metadata=metadata,
            intent=intent,
            challenges=challenges,
            recommendations=recommendations,
        )
