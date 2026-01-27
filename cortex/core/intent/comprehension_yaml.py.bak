# © 2025-2026 Asif Hussain. All rights reserved.
"""Comprehension YAML Generation for Intent Router.

This module transforms canonicalized intents, challenges, and recommendations
into structured YAML comprehension documents for user approval before execution.

PHASE-07: Holistic Intent Router Intelligence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class IntentSection:
    """Intent section of comprehension YAML.
    
    Attributes:
        type: Intent type (IMPLEMENT, REFACTOR, etc.)
        scope: Target scope information
        confidence: Confidence score
        keywords: Extracted keywords
        needs_clarification: Whether clarification is needed
    """
    
    type: str
    scope: Dict[str, Any]
    confidence: float
    keywords: List[str] = field(default_factory=list)
    needs_clarification: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "scope": self.scope,
            "confidence": self.confidence,
            "keywords": self.keywords,
            "needs_clarification": self.needs_clarification,
        }


@dataclass
class ChallengeSection:
    """Challenges section of comprehension YAML.
    
    Attributes:
        summary: Summary statistics
        items: List of challenges
    """
    
    summary: Dict[str, Any]
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "items": self.items,
        }


@dataclass
class RecommendationSection:
    """Recommendations section of comprehension YAML.
    
    Attributes:
        summary: Summary statistics
        items: List of recommendations
    """
    
    summary: Dict[str, Any]
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "items": self.items,
        }


@dataclass
class ComprehensionYAML:
    """Complete comprehension YAML document.
    
    Attributes:
        metadata: Document metadata
        intent: Intent section
        challenges: Challenges section
        recommendations: Recommendations section
    """
    
    metadata: Dict[str, Any]
    intent: IntentSection
    challenges: ChallengeSection
    recommendations: RecommendationSection
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation suitable for YAML serialization
        """
        return {
            "metadata": self.metadata,
            "intent": self.intent.to_dict(),
            "challenges": self.challenges.to_dict(),
            "recommendations": self.recommendations.to_dict(),
        }
    
    def to_yaml(self) -> str:
        """Convert to YAML string.
        
        Returns:
            YAML string representation
        """
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComprehensionYAML":
        """Create ComprehensionYAML from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            ComprehensionYAML object
        """
        # Reconstruct intent section
        intent_data = data.get("intent", {})
        intent_section = IntentSection(
            type=intent_data.get("type", "UNKNOWN"),
            scope=intent_data.get("scope", {}),
            confidence=intent_data.get("confidence", 0.0),
            keywords=intent_data.get("keywords", []),
            needs_clarification=intent_data.get("needs_clarification", False),
        )
        
        # Reconstruct challenges section
        challenges_data = data.get("challenges", {})
        challenges_section = ChallengeSection(
            summary=challenges_data.get("summary", {}),
            items=challenges_data.get("items", []),
        )
        
        # Reconstruct recommendations section
        recommendations_data = data.get("recommendations", {})
        recommendations_section = RecommendationSection(
            summary=recommendations_data.get("summary", {}),
            items=recommendations_data.get("items", []),
        )
        
        return cls(
            metadata=data.get("metadata", {}),
            intent=intent_section,
            challenges=challenges_section,
            recommendations=recommendations_section,
        )


class CanonicalIntentComposer:
    """Composes comprehension YAML from intent, challenges, and recommendations.
    
    Methods:
        compose: Create ComprehensionYAML from inputs
        to_yaml_string: Convert ComprehensionYAML to YAML string
    """
    
    def __init__(self) -> None:
        """Initialize composer."""
        pass
    
    def compose(
        self,
        intent: Optional[Dict[str, Any]] = None,
        challenges: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        intent_dict: Optional[Dict[str, Any]] = None,
    ) -> ComprehensionYAML:
        """Compose comprehension YAML from inputs.
        
        Args:
            intent: Canonicalized intent dictionary (deprecated, use intent_dict)
            challenges: List of challenge dictionaries
            recommendations: List of recommendation dictionaries
            intent_dict: Canonicalized intent dictionary
            
        Returns:
            ComprehensionYAML object
        """
        # Support both intent and intent_dict
        intent_data = intent_dict or intent or {}
        challenges = challenges or []
        recommendations = recommendations or []
        
        # Create metadata with intent_id
        metadata = {
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "tool": "CORTEX Intent Router",
            "phase": "Intent Comprehension",
            "intent_id": intent_data.get("intent_id", "unknown"),
        }
        
        # Create intent section
        intent_section = IntentSection(
            type=intent_data.get("intent_type", "UNKNOWN"),
            scope=intent_data.get("scope", {}),
            confidence=intent_data.get("confidence", 0.0),
            keywords=intent_data.get("keywords", []),
            needs_clarification=intent_data.get("needs_clarification", False),
        )
        
        # Create challenges section with summary (lowercase severity keys)
        severity_counts = {}
        for challenge in challenges:
            severity = challenge.get("severity", "UNKNOWN").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Build summary with both flat severity counts and by_severity dict
        challenges_summary = {
            "total": len(challenges),
            "by_severity": severity_counts,
        }
        # Add flat severity counts to summary
        challenges_summary.update(severity_counts)
        
        challenges_section = ChallengeSection(
            summary=challenges_summary,
            items=challenges,
        )
        
        # Create recommendations section with priority sorting
        priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        sorted_recommendations = sorted(
            recommendations,
            key=lambda r: priority_order.get(r.get("priority", "LOW"), 0),
            reverse=True,
        )
        
        priority_counts = {}
        for rec in recommendations:
            priority = rec.get("priority", "UNKNOWN")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        recommendations_section = RecommendationSection(
            summary={
                "total": len(recommendations),
                "by_priority": priority_counts,
            },
            items=sorted_recommendations,
        )
        
        return ComprehensionYAML(
            metadata=metadata,
            intent=intent_section,
            challenges=challenges_section,
            recommendations=recommendations_section,
        )
    
    def to_yaml_string(self, comprehension: ComprehensionYAML) -> str:
        """Convert ComprehensionYAML to YAML string.
        
        Args:
            comprehension: ComprehensionYAML object
            
        Returns:
            YAML string
        """
        return comprehension.to_yaml()


class YAMLComprehensionEngine:
    """Engine for processing comprehension YAML documents.
    
    Provides parsing and validation capabilities.
    """
    
    def __init__(self) -> None:
        """Initialize engine."""
        pass
    
    def parse(self, yaml_string: str) -> ComprehensionYAML:
        """Parse YAML string to ComprehensionYAML object.
        
        Args:
            yaml_string: YAML string to parse
            
        Returns:
            ComprehensionYAML object
        """
        data = yaml.safe_load(yaml_string)
        
        # Reconstruct intent section
        intent_data = data.get("intent", {})
        intent_section = IntentSection(
            type=intent_data.get("type", "UNKNOWN"),
            scope=intent_data.get("scope", {}),
            confidence=intent_data.get("confidence", 0.0),
            keywords=intent_data.get("keywords", []),
            needs_clarification=intent_data.get("needs_clarification", False),
        )
        
        # Reconstruct challenges section
        challenges_data = data.get("challenges", {})
        challenges_section = ChallengeSection(
            summary=challenges_data.get("summary", {}),
            items=challenges_data.get("items", []),
        )
        
        # Reconstruct recommendations section
        recommendations_data = data.get("recommendations", {})
        recommendations_section = RecommendationSection(
            summary=recommendations_data.get("summary", {}),
            items=recommendations_data.get("items", []),
        )
        
        return ComprehensionYAML(
            metadata=data.get("metadata", {}),
            intent=intent_section,
            challenges=challenges_section,
            recommendations=recommendations_section,
        )
    
    def validate(self, comprehension: ComprehensionYAML) -> List[str]:
        """Validate comprehension YAML structure.
        
        Args:
            comprehension: ComprehensionYAML to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check metadata
        if not comprehension.metadata.get("version"):
            errors.append("Missing metadata.version")
        if not comprehension.metadata.get("generated_at"):
            errors.append("Missing metadata.generated_at")
        
        # Check intent
        if not comprehension.intent.type:
            errors.append("Missing intent.type")
        if comprehension.intent.confidence < 0 or comprehension.intent.confidence > 1:
            errors.append("Invalid intent.confidence (must be 0-1)")
        
        return errors


@dataclass
class ParsingResult:
    """Data class for ParsingResult."""
    data: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "ChallengeSection",
    "ComprehensionYAML",
    "CanonicalIntentComposer",
    "YAMLComprehensionEngine",
    "ParsingResult",
    "RecommendationSection",
    "IntentSection",
]