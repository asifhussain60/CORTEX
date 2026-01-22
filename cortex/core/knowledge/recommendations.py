"""Knowledge recommendation engine for personalized content suggestions."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Recommendation:
    """Personalized recommendation for a user.
    
    Attributes:
        doc_id: Document identifier being recommended.
        content: Recommendation content/title.
        confidence: Confidence score between 0 and 1.
        reason: Why this recommendation was generated.
        backend: Source backend.
        relevance_score: Relevance to user context.
    """
    doc_id: str = ""
    content: str = ""
    confidence: float = 0.0
    reason: str = ""
    backend: str = ""
    relevance_score: float = 0.0

    def __post_init__(self) -> None:
        """Validate confidence is in valid range."""
        if not 0 <= self.confidence <= 1:
            self.confidence = min(1.0, max(0.0, self.confidence))

    @property
    def knowledge_id(self) -> str:
        """Alias for doc_id for backwards compatibility."""
        return self.doc_id


@dataclass
class UserInteraction:
    """Records a user interaction with content.
    
    Attributes:
        user_id: User identifier.
        doc_id: Document identifier.
        interaction_type: Type of interaction (view, click, share, etc.).
        engagement_score: Engagement level (0-1).
        timestamp: When interaction occurred.
    """
    user_id: str
    doc_id: str
    interaction_type: str
    engagement_score: float
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class RecommendationEngine:
    """Engine for generating personalized recommendations based on behavior and context.
    
    Learns from user interactions and generates contextual recommendations.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize recommendation engine with configured backends.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        
        Raises:
            TypeError: If backends is not a dict or None.
        """
        if backends is None:
            backends = {}
        if not isinstance(backends, dict):
            raise TypeError(f"backends must be dict, got {type(backends)}")
        
        self.backends = backends
        self.behavior_history: Dict[str, List[UserInteraction]] = defaultdict(list)
        self.interaction_weights = {
            "view": 0.3,
            "click": 0.5,
            "share": 0.9,
            "bookmark": 0.8,
            "comment": 0.7
        }
        self.document_registry: Dict[str, Dict[str, Any]] = {}
        self.user_preferences: Dict[str, Dict[str, float]] = defaultdict(dict)

    def get_recommendations(
        self,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate recommendations based on context and optional user history.
        
        Args:
            context: Context dictionary with topic, interest, skill, etc.
            user_id: Optional user ID for personalized recommendations.
            limit: Maximum number of recommendations to return.
        
        Returns:
            List of Recommendation objects sorted by confidence.
        """
        recommendations: List[Recommendation] = []
        
        # If we have user history, use it to personalize
        if user_id and user_id in self.behavior_history:
            for interaction in self.behavior_history[user_id]:
                confidence = self.interaction_weights.get(
                    interaction.interaction_type, 0.5
                ) * interaction.engagement_score
                
                rec = Recommendation(
                    doc_id=interaction.doc_id,
                    content=f"Previously engaged with {interaction.doc_id}",
                    confidence=confidence,
                    reason=f"Based on your {interaction.interaction_type} history",
                    relevance_score=confidence
                )
                recommendations.append(rec)
        
        # Generate context-based recommendations
        for topic_key, topic_value in context.items():
            if isinstance(topic_value, str):
                confidence = 0.7
                rec = Recommendation(
                    doc_id=f"{topic_key}_{topic_value}",
                    content=f"Content about {topic_value}",
                    confidence=confidence,
                    reason=f"Matches your interest in {topic_key}",
                    relevance_score=confidence
                )
                recommendations.append(rec)
        
        # Sort by confidence descending
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:limit]

    def learn_from_interaction(
        self,
        user_id: str,
        doc_id: str,
        interaction_type: str,
        engagement_score: float
    ) -> None:
        """Record a user interaction for learning.
        
        Args:
            user_id: User identifier.
            doc_id: Document identifier.
            interaction_type: Type of interaction (view, click, share, etc.).
            engagement_score: Engagement level between 0 and 1.
        """
        interaction = UserInteraction(
            user_id=user_id,
            doc_id=doc_id,
            interaction_type=interaction_type,
            engagement_score=engagement_score
        )
        self.behavior_history[user_id].append(interaction)
        
        # Update user preferences
        if interaction_type not in self.user_preferences[user_id]:
            self.user_preferences[user_id][interaction_type] = 0.0
        
        self.user_preferences[user_id][interaction_type] = (
            self.user_preferences[user_id][interaction_type] * 0.7 +
            engagement_score * 0.3
        )

    def get_behavioral_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Recommendation]:
        """Generate recommendations based purely on user behavior history.
        
        Args:
            user_id: User identifier.
            limit: Maximum number of recommendations to return.
        
        Returns:
            List of Recommendation objects from user behavior.
        """
        if user_id not in self.behavior_history:
            return []
        
        recommendations_map: Dict[str, Recommendation] = {}
        interactions = self.behavior_history[user_id]
        
        for interaction in interactions:
            weight = self.interaction_weights.get(interaction.interaction_type, 0.5)
            confidence = weight * interaction.engagement_score
            
            # If doc_id already seen, update with higher confidence
            if interaction.doc_id not in recommendations_map:
                rec = Recommendation(
                    doc_id=interaction.doc_id,
                    content=f"Item: {interaction.doc_id}",
                    confidence=confidence,
                    reason=f"Based on your {interaction.interaction_type} of this item",
                    relevance_score=confidence
                )
                recommendations_map[interaction.doc_id] = rec
            else:
                # Update confidence if this interaction is stronger
                existing = recommendations_map[interaction.doc_id]
                if confidence > existing.confidence:
                    existing.confidence = confidence
                    existing.reason = f"Based on your {interaction.interaction_type} of this item"
        
        recommendations = list(recommendations_map.values())
        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:limit]

    def register_document(
        self,
        doc_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Register a document for recommendations.
        
        Args:
            doc_id: Document identifier.
            metadata: Document metadata (title, tags, category, etc.).
        """
        self.document_registry[doc_id] = metadata

    def get_personalized_recommendations(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Recommendation]:
        """Get fully personalized recommendations combining behavior and context.
        
        Args:
            user_id: User identifier.
            context: Optional context dictionary.
            limit: Maximum number of recommendations.
        
        Returns:
            List of personalized Recommendation objects.
        """
        recommendations: List[Recommendation] = []
        
        # Get behavioral recommendations
        behavioral = self.get_behavioral_recommendations(user_id, limit=limit * 2)
        recommendations.extend(behavioral)
        
        # Get context-based recommendations if provided
        if context:
            context_based = self.get_recommendations(
                context,
                user_id=user_id,
                limit=limit * 2
            )
            recommendations.extend(context_based)
        
        # Deduplicate by doc_id (keep highest confidence)
        seen: Dict[str, Recommendation] = {}
        for rec in recommendations:
            if rec.doc_id not in seen or rec.confidence > seen[rec.doc_id].confidence:
                seen[rec.doc_id] = rec
        
        final_recs = list(seen.values())
        final_recs.sort(key=lambda r: r.confidence, reverse=True)
        return final_recs[:limit]


class KnowledgeRecommender:
    """High-level knowledge recommender with advanced personalization.
    
    Builds on RecommendationEngine to provide domain-specific recommendations.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize knowledge recommender.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        """
        self.engine = RecommendationEngine(backends or {})

    def recommend(
        self,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = "hybrid"
    ) -> List[Recommendation]:
        """Generate recommendations using specified strategy.
        
        Args:
            user_id: Optional user identifier for personalization.
            context: Optional context for content-based recommendations.
            strategy: Strategy type ("behavioral", "contextual", "hybrid").
        
        Returns:
            List of Recommendation objects.
        
        Raises:
            ValueError: If strategy is not recognized.
        """
        if strategy == "behavioral" and user_id:
            return self.engine.get_behavioral_recommendations(user_id)
        elif strategy == "contextual" and context:
            return self.engine.get_recommendations(context)
        elif strategy == "hybrid" and user_id:
            return self.engine.get_personalized_recommendations(
                user_id,
                context=context
            )
        else:
            raise ValueError(f"Cannot apply strategy '{strategy}' with given inputs")


__all__ = [
    "Recommendation",
    "RecommendationEngine",
    "KnowledgeRecommender",
]