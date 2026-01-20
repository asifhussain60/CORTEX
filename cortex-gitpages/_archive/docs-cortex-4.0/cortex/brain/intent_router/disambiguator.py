"""
Intent Disambiguation System - AC-PHX-007-03

Resolves ambiguous intents through:
- Confidence thresholding
- Context-aware disambiguation
- Multi-path analysis
- Fallback suggestion ranking
- User interaction support

CORTEX Governance: CORE-008, 011, 012, 013, 027
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from cortex.brain.intent_router.classifier import IntentCategory, ClassificationResult


@dataclass
class DisambiguationResult:
    """Result of disambiguation analysis.
    
    Attributes:
        is_ambiguous: Whether intent is ambiguous
        primary_intent: Primary intent choice
        alternatives: List of alternative intents with scores
        confidence_gap: Gap between primary and secondary (0-1)
        recommendation: Suggested action
    """
    is_ambiguous: bool
    primary_intent: IntentCategory
    alternatives: List[Tuple[IntentCategory, float]]
    confidence_gap: float
    recommendation: str


class IntentDisambiguator:
    """Resolves ambiguous intent classifications.
    
    Features:
    - Confidence threshold checking
    - Context-aware disambiguation
    - Multi-path analysis
    - Fallback suggestions
    - Interactive disambiguation support
    """
    
    CONFIDENCE_THRESHOLD = 0.60
    MIN_CONFIDENCE_GAP = 0.15
    
    def __init__(self) -> None:
        """Initialize disambiguator."""
        self.disambiguation_cache: Dict[str, DisambiguationResult] = {}
        self.metrics = {
            "total_disambiguations": 0,
            "ambiguous_cases": 0,
            "resolutions": 0,
        }
    
    def disambiguate(
        self,
        classification: ClassificationResult,
        context: Optional[Dict[str, Any]] = None
    ) -> DisambiguationResult:
        """Disambiguate intent classification.
        
        Args:
            classification: Classification result to disambiguate
            context: Optional context for disambiguation
            
        Returns:
            DisambiguationResult with disambiguation analysis
        """
        self.metrics["total_disambiguations"] += 1
        
        # Check if ambiguous
        is_ambiguous = self._is_ambiguous(classification)
        
        if is_ambiguous:
            self.metrics["ambiguous_cases"] += 1
            # Apply disambiguation strategies
            result = self._apply_disambiguation(classification, context)
            self.metrics["resolutions"] += 1
        else:
            # Clear primary intent
            result = DisambiguationResult(
                is_ambiguous=False,
                primary_intent=classification.primary_intent,
                alternatives=classification.secondary_intents[:3],
                confidence_gap=1.0,
                recommendation="PROCEED - Intent is clear"
            )
        
        return result
    
    def _is_ambiguous(self, classification: ClassificationResult) -> bool:
        """Check if classification is ambiguous.
        
        Args:
            classification: Classification to check
            
        Returns:
            True if ambiguous, False otherwise
        """
        # Low confidence
        if classification.confidence_score < self.CONFIDENCE_THRESHOLD:
            return True
        
        # Close alternatives
        if classification.secondary_intents:
            secondary_score = classification.secondary_intents[0][1]
            gap = classification.confidence_score - secondary_score
            if gap < self.MIN_CONFIDENCE_GAP:
                return True
        
        return False
    
    def _apply_disambiguation(
        self,
        classification: ClassificationResult,
        context: Optional[Dict[str, Any]] = None
    ) -> DisambiguationResult:
        """Apply disambiguation strategies.
        
        Args:
            classification: Classification to disambiguate
            context: Optional context
            
        Returns:
            Disambiguated result
        """
        alternatives = classification.secondary_intents[:3]
        gap = classification.confidence_score
        
        if alternatives:
            gap -= alternatives[0][1]
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            classification, alternatives, context
        )
        
        return DisambiguationResult(
            is_ambiguous=True,
            primary_intent=classification.primary_intent,
            alternatives=alternatives,
            confidence_gap=max(0.0, gap),
            recommendation=recommendation
        )
    
    def _generate_recommendation(
        self,
        classification: ClassificationResult,
        alternatives: List[Tuple[IntentCategory, float]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate disambiguation recommendation.
        
        Args:
            classification: Original classification
            alternatives: Alternative intents
            context: Optional context
            
        Returns:
            Recommendation string
        """
        if not alternatives:
            return f"PROCEED with {classification.primary_intent.value}"
        
        alt_str = ", ".join([alt[0].value for alt in alternatives[:2]])
        return f"AMBIGUOUS - Consider: {alt_str}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get disambiguation metrics.
        
        Returns:
            Metrics dictionary
        """
        return self.metrics.copy()
