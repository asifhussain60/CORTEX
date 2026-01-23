"""Intent Disambiguator - Disambiguation for ambiguous classifications.

Provides disambiguation logic including confidence thresholding,
context-aware disambiguation, and fallback suggestions.

Author: CORTEX Framework
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from cortex.intent_router.classifier import ClassificationResult, IntentCategory


@dataclass
class Disambiguation:
    """Disambiguation result.
    
    Attributes:
        is_ambiguous: Whether input is ambiguous
        recommendation: Action recommendation (PROCEED or AMBIGUOUS)
        alternatives: Alternative interpretations if ambiguous
        confidence: Overall confidence in disambiguation
    """
    is_ambiguous: bool
    recommendation: str
    alternatives: List[IntentCategory]
    confidence: float


class IntentDisambiguator:
    """Disambiguate ambiguous intent classifications.
    
    Detects ambiguous classifications based on confidence thresholds
    and provides recommendations for handling them.
    
    Attributes:
        CONFIDENCE_THRESHOLD: Minimum confidence for clear intent (0.7)
        MIN_CONFIDENCE_GAP: Minimum gap between primary and secondary (0.2)
        total_disambiguations: Count of total disambiguations
        ambiguous_cases: Count of ambiguous cases detected
    """
    
    CONFIDENCE_THRESHOLD = 0.7
    MIN_CONFIDENCE_GAP = 0.2
    
    def __init__(self):
        """Initialize disambiguator."""
        self.total_disambiguations: int = 0
        self.ambiguous_cases: int = 0
    
    def _is_ambiguous(self, result: ClassificationResult) -> bool:
        """Check if classification is ambiguous.
        
        Args:
            result: Classification result to check
            
        Returns:
            True if ambiguous, False otherwise
        """
        # Low confidence case
        if result.confidence_score < self.CONFIDENCE_THRESHOLD:
            return True
        
        # Close alternatives case
        if result.secondary_intents:
            top_secondary = result.secondary_intents[0][1]
            gap = result.confidence_score - top_secondary
            if gap < self.MIN_CONFIDENCE_GAP:
                return True
        
        return False
    
    def disambiguate(self, result: ClassificationResult) -> Disambiguation:
        """Disambiguate a classification result.
        
        Args:
            result: Classification result to disambiguate
            
        Returns:
            Disambiguation with recommendation and alternatives
        """
        self.total_disambiguations += 1
        
        is_ambig = self._is_ambiguous(result)
        
        if is_ambig:
            self.ambiguous_cases += 1
            # Extract alternative intents
            alternatives = [intent for intent, _ in result.secondary_intents[:3]]
            
            return Disambiguation(
                is_ambiguous=True,
                recommendation="AMBIGUOUS: Multiple interpretations possible",
                alternatives=alternatives,
                confidence=result.confidence_score
            )
        else:
            return Disambiguation(
                is_ambiguous=False,
                recommendation="PROCEED: Clear intent detected",
                alternatives=[],
                confidence=result.confidence_score
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get disambiguation metrics.
        
        Returns:
            Dictionary with total_disambiguations and ambiguous_cases counts
        """
        return {
            "total_disambiguations": self.total_disambiguations,
            "ambiguous_cases": self.ambiguous_cases,
        }


__all__ = ["Disambiguation", "IntentDisambiguator"]
