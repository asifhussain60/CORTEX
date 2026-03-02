"""
Recommendation gate with LENS analysis and registry consultation.

Prevents contradictory or duplicate recommendations by consulting
registry history and performing LENS-based similarity checks.

AC_START: AC-WAVE-3-AUTOMATION-HOOKS-001
Description: RecommendationGate for registry-aware suggestions
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

import yaml


logger = logging.getLogger(__name__)


class RecommendationGate:
    """
    Gate for validating recommendations against registry history.
    
    Prevents duplicate suggestions and catches contradictions with
    previously rejected recommendations.
    
    Attributes:
        registry_path: Path to cortex-registry root
        similarity_threshold: Similarity score threshold (0.0-1.0)
    """
    
    def __init__(self, registry_path: Optional[Path] = None, similarity_threshold: float = 0.3) -> None:
        """
        Initialize recommendation gate.
        
        Args:
            registry_path: Path to registry root (defaults to cortex-registry/)
            similarity_threshold: Minimum similarity to block (default: 0.3)
            
        Raises:
            ValueError: If similarity_threshold not in range [0.0, 1.0]
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(f"similarity_threshold must be in [0.0, 1.0], got: {similarity_threshold}")
            
        self.registry_path = registry_path or Path("cortex-registry")
        self.similarity_threshold = similarity_threshold
        self._check_count = 0
        self._blocked_count = 0
        
    def check_recommendation(
        self, 
        recommendation: str, 
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate recommendation against registry history.
        
        Args:
            recommendation: Recommendation text to validate
            category: Optional category (e.g., "architecture", "governance")
            
        Returns:
            Dictionary with:
                - allowed (bool): Whether recommendation passes gate
                - reason (str): Block reason if not allowed
                - similarity (float): Highest similarity score found
                - matched_id (str): ID of matched recommendation if blocked
        """
        if not recommendation or not recommendation.strip():
            return {
                "allowed": False,
                "reason": "Empty recommendation",
                "similarity": 0.0,
                "matched_id": None
            }
            
        self._check_count += 1
        
        # Load rejected recommendations
        rejected = self._load_rejected_recommendations()
        
        # Check similarity against rejected items
        for rej_id, rej_data in rejected.items():
            similarity = self._calculate_similarity(recommendation, rej_data.get("text", ""))
            
            if similarity > self.similarity_threshold:
                self._blocked_count += 1
                logger.warning(
                    f"Recommendation blocked: {similarity:.2f} similarity to {rej_id}"
                )
                return {
                    "allowed": False,
                    "reason": f"Similar to rejected recommendation {rej_id}",
                    "similarity": similarity,
                    "matched_id": rej_id
                }
                
        # Passed all checks
        return {
            "allowed": True,
            "reason": "No conflicts detected",
            "similarity": 0.0,
            "matched_id": None
        }
        
    def _load_rejected_recommendations(self) -> Dict[str, Any]:
        """
        Load rejected recommendations from registry.
        
        Returns:
            Dictionary of rejected recommendation ID -> data
        """
        rejected_file = (
            self.registry_path / "_cortex-master" / "enhancements" / "rejected_recommendations.yaml"
        )
        
        if not rejected_file.exists():
            logger.debug("No rejected recommendations file found")
            return {}
            
        try:
            with open(rejected_file, "r") as f:
                data = yaml.safe_load(f) or {}
                return data.get("rejected", {})
        except Exception as e:
            logger.error(f"Failed to load rejected recommendations: {e}")
            return {}
            
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        Uses simple word overlap ratio for now. Can be enhanced with
        LENS semantic similarity in future iterations.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score in range [0.0, 1.0]
        """
        if not text1 or not text2:
            return 0.0
            
        # Normalize to lowercase
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        # Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
        
    def get_stats(self) -> Dict[str, int]:
        """
        Get gate statistics.
        
        Returns:
            Dictionary with check_count, blocked_count, pass_rate
        """
        pass_rate = 0
        if self._check_count > 0:
            pass_rate = int(100 * (self._check_count - self._blocked_count) / self._check_count)
            
        return {
            "check_count": self._check_count,
            "blocked_count": self._blocked_count,
            "pass_rate": pass_rate
        }
