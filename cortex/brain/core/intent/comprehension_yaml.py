"""
Comprehension YAML Generation Module.

Transforms canonicalized intents, challenges, and recommendations into
structured YAML comprehension documents for user approval before execution.

The CanonicalIntentComposer orchestrates creation of ComprehensionYAML objects
that can be presented to users for confirmation. The YAML structure includes:

- Metadata: Generation timestamp, tool version, phase information
- Intent: Canonicalized user intent with confidence score and scope
- Challenges: Identified risks/governance issues with remediation guidance
- Recommendations: Best practice suggestions prioritized by impact

This enables the CORTEX LENS protocol to present holistic context before
executing user requests.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class IntentSection:
    """Structured intent information for comprehension YAML."""

    type: str  # IMPLEMENT, FIX, REFACTOR, QUERY, ANALYZE, VALIDATE, MIGRATE
    scope: Dict[str, Any]  # target_type, target_name, file_path, ac_ids
    confidence: float  # 0.0-1.0
    keywords: List[str]
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        data = {
            "type": self.type,
            "scope": self.scope,
            "confidence": round(self.confidence, 3),
            "keywords": self.keywords,
            "needs_clarification": self.needs_clarification,
        }
        if self.clarification_prompt:
            data["clarification_prompt"] = self.clarification_prompt
        return data


@dataclass
class ChallengeItem:
    """Individual challenge in comprehension YAML."""

    id: str
    category: str  # BREAKING_CHANGE, TEST_GAP, GOVERNANCE_RISK, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    affected_code: str
    remediation: str
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "id": self.id,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "affected_code": self.affected_code,
            "remediation": self.remediation,
            "confidence": round(self.confidence, 3),
        }


@dataclass
class ChallengeSection:
    """Structured challenges section for comprehension YAML."""

    items: List[ChallengeItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with summary statistics."""
        severity_counts = {
            "critical": sum(1 for item in self.items if item.severity == "CRITICAL"),
            "high": sum(1 for item in self.items if item.severity == "HIGH"),
            "medium": sum(1 for item in self.items if item.severity == "MEDIUM"),
            "low": sum(1 for item in self.items if item.severity == "LOW"),
        }

        category_counts = {}
        for item in self.items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1

        return {
            "summary": {
                "total": len(self.items),
                "critical": severity_counts["critical"],
                "high": severity_counts["high"],
                "medium": severity_counts["medium"],
                "low": severity_counts["low"],
                "by_severity": severity_counts,
                "by_category": category_counts,
            },
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class RecommendationItem:
    """Individual recommendation in comprehension YAML."""

    id: str
    category: str  # BEST_PRACTICE, ALTERNATIVE_APPROACH, TEST_STRATEGY, etc.
    priority: str  # LOW, MEDIUM, HIGH
    title: str
    description: str
    code_context: Optional[str] = None
    alternative: Optional[str] = None
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        data = {
            "id": self.id,
            "category": self.category,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
        }
        if self.code_context:
            data["code_context"] = self.code_context
        if self.alternative:
            data["alternative"] = self.alternative
        if self.rationale:
            data["rationale"] = self.rationale
        return data


@dataclass
class RecommendationSection:
    """Structured recommendations section for comprehension YAML."""

    items: List[RecommendationItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with summary statistics."""
        priority_counts = {
            "high": sum(1 for item in self.items if item.priority == "HIGH"),
            "medium": sum(1 for item in self.items if item.priority == "MEDIUM"),
            "low": sum(1 for item in self.items if item.priority == "LOW"),
        }

        category_counts = {}
        for item in self.items:
            category_counts[item.category] = category_counts.get(item.category, 0) + 1

        return {
            "summary": {
                "total": len(self.items),
                "high_priority": priority_counts["high"],
                "medium_priority": priority_counts["medium"],
                "low_priority": priority_counts["low"],
                "by_priority": priority_counts,
                "by_category": category_counts,
            },
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class ComprehensionYAML:
    """Complete comprehension YAML document."""

    metadata: Dict[str, Any]
    intent: IntentSection
    challenges: ChallengeSection
    recommendations: RecommendationSection

    def to_dict(self) -> Dict[str, Any]:
        """Convert entire document to dictionary."""
        return {
            "metadata": self.metadata,
            "intent": self.intent.to_dict(),
            "challenges": self.challenges.to_dict(),
            "recommendations": self.recommendations.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ComprehensionYAML":
        """Reconstruct ComprehensionYAML from dictionary."""
        metadata = data.get("metadata", {})

        intent_data = data.get("intent", {})
        intent = IntentSection(
            type=intent_data.get("type"),
            scope=intent_data.get("scope", {}),
            confidence=intent_data.get("confidence", 0.0),
            keywords=intent_data.get("keywords", []),
            needs_clarification=intent_data.get("needs_clarification", False),
            clarification_prompt=intent_data.get("clarification_prompt"),
        )

        challenges_data = data.get("challenges", {})
        challenge_items = []
        for item_data in challenges_data.get("items", []):
            challenge_items.append(ChallengeItem(
                id=item_data.get("id"),
                category=item_data.get("category"),
                severity=item_data.get("severity"),
                description=item_data.get("description"),
                affected_code=item_data.get("affected_code"),
                remediation=item_data.get("remediation"),
                confidence=item_data.get("confidence", 0.8),
            ))
        challenges = ChallengeSection(items=challenge_items)

        recommendations_data = data.get("recommendations", {})
        recommendation_items = []
        for item_data in recommendations_data.get("items", []):
            recommendation_items.append(RecommendationItem(
                id=item_data.get("id"),
                category=item_data.get("category"),
                priority=item_data.get("priority"),
                title=item_data.get("title"),
                description=item_data.get("description"),
                code_context=item_data.get("code_context"),
                alternative=item_data.get("alternative"),
                rationale=item_data.get("rationale"),
            ))
        recommendations = RecommendationSection(items=recommendation_items)

        return ComprehensionYAML(
            metadata=metadata,
            intent=intent,
            challenges=challenges,
            recommendations=recommendations,
        )


# ============================================================================
# COMPOSER CLASS
# ============================================================================

class CanonicalIntentComposer:
    """
    Orchestrates transformation of intent/challenges/recommendations
    into structured comprehension YAML documents.

    Usage:
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(intent_dict, challenges_list, recommendations_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
    """

    # CORTEX LENS Protocol version
    COMPREHENSION_VERSION = "1.0"
    CORTEX_PHASE = "PHASE-07-Intent-Router"

    def compose(
        self,
        intent_dict: Dict[str, Any],
        challenges: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
    ) -> ComprehensionYAML:
        """
        Compose comprehensive YAML from intent, challenges, and recommendations.

        Args:
            intent_dict: Canonicalized intent with type, scope, confidence
            challenges: List of challenge dicts with id, category, severity, etc.
            recommendations: List of recommendation dicts with id, category, priority

        Returns:
            ComprehensionYAML: Structured document ready for YAML export
        """
        # Build metadata
        metadata = self._build_metadata(intent_dict)

        # Build intent section
        intent_section = self._build_intent_section(intent_dict)

        # Build challenges section (sort by severity: CRITICAL → HIGH → MEDIUM → LOW)
        challenge_items = [
            ChallengeItem(
                id=c.get("id"),
                category=c.get("category"),
                severity=c.get("severity"),
                description=c.get("description"),
                affected_code=c.get("affected_code"),
                remediation=c.get("remediation"),
                confidence=c.get("confidence", 0.8),
            )
            for c in challenges
        ]
        challenge_items.sort(
            key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x.severity, 4)
        )
        challenges_section = ChallengeSection(items=challenge_items)

        # Build recommendations section (sort by priority: HIGH → MEDIUM → LOW)
        recommendation_items = [
            RecommendationItem(
                id=r.get("id"),
                category=r.get("category"),
                priority=r.get("priority"),
                title=r.get("title"),
                description=r.get("description"),
                code_context=r.get("code_context"),
                alternative=r.get("alternative"),
                rationale=r.get("rationale"),
            )
            for r in recommendations
        ]
        recommendation_items.sort(
            key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x.priority, 3)
        )
        recommendations_section = RecommendationSection(items=recommendation_items)

        return ComprehensionYAML(
            metadata=metadata,
            intent=intent_section,
            challenges=challenges_section,
            recommendations=recommendations_section,
        )

    def _build_metadata(self, intent_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata section with timestamp, version, tool info."""
        return {
            "version": self.COMPREHENSION_VERSION,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "tool": "CORTEX-LENS",
            "phase": self.CORTEX_PHASE,
            "intent_id": str(uuid.uuid4()),
            "schema": "cortex-comprehension-v1",
        }

    def _build_intent_section(self, intent_dict: Dict[str, Any]) -> IntentSection:
        """Build intent section from canonicalized intent."""
        return IntentSection(
            type=intent_dict.get("intent_type"),
            scope=intent_dict.get("scope", {}),
            confidence=intent_dict.get("confidence", 0.5),
            keywords=intent_dict.get("keywords", []),
            needs_clarification=intent_dict.get("needs_clarification", False),
            clarification_prompt=intent_dict.get("clarification_prompt"),
        )

    def to_yaml_string(self, yaml_obj: ComprehensionYAML) -> str:
        """
        Convert ComprehensionYAML to formatted YAML string.

        Args:
            yaml_obj: ComprehensionYAML object to serialize

        Returns:
            str: YAML-formatted string ready for output/storage
        """
        data_dict = yaml_obj.to_dict()

        # Use safe_dump for secure YAML generation
        yaml_string = yaml.safe_dump(
            data_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100,
            default_style=None,
        )

        return yaml_string

    def to_file(self, yaml_obj: ComprehensionYAML, filepath: str) -> None:
        """
        Write ComprehensionYAML to file.

        Args:
            yaml_obj: ComprehensionYAML object to write
            filepath: Path where YAML should be written
        """
        yaml_string = self.to_yaml_string(yaml_obj)
        with open(filepath, "w") as f:
            f.write(yaml_string)

    @staticmethod
    def from_file(filepath: str) -> ComprehensionYAML:
        """
        Read ComprehensionYAML from file.

        Args:
            filepath: Path to YAML file

        Returns:
            ComprehensionYAML: Reconstructed object
        """
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        return ComprehensionYAML.from_dict(data)
