"""Knowledge recommendations and suggestions."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class Recommendation:
    """Recommendation item."""
    knowledge_id: str
    backend: str
    confidence: float
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)

class RecommendationEngine:
    """Generates knowledge recommendations."""

    def __init__(self, backends: Dict[str, Any]):
        """Initialize RecommendationEngine."""
        self.backends = backends
        self.behavior_history: Dict[str, List[Dict[str, Any]]] = {}
        self.recommendations_cache: Dict[str, List[Recommendation]] = {}

    def get_recommendations(self, context: Dict[str, Any], user: str = "anonymous") -> List[Recommendation]:
        """Get context-based recommendations."""
        recommendations = []
        
        for backend, provider in self.backends.items():
            # Generate context-based suggestions
            for key, value in context.items():
                score = self._compute_context_score(key, value)
                if score > 0.6:
                    recommendations.append(Recommendation(
                        knowledge_id=f"{backend}_{key}",
                        backend=backend,
                        confidence=score,
                        reason=f"Matches context: {key}"
                    ))
        
        return sorted(recommendations, key=lambda r: r.confidence, reverse=True)

    def learn_from_interaction(self, user: str, knowledge_id: str, interaction_type: str, score: float) -> None:
        """Learn from user interactions."""
        if user not in self.behavior_history:
            self.behavior_history[user] = []
        
        self.behavior_history[user].append({
            "knowledge_id": knowledge_id,
            "interaction_type": interaction_type,
            "score": score,
            "timestamp": datetime.now()
        })

    def get_behavioral_recommendations(self, user: str, limit: int = 5) -> List[Recommendation]:
        """Get recommendations based on user behavior."""
        recommendations = []
        history = self.behavior_history.get(user, [])
        
        # Find frequently accessed knowledge
        access_counts = {}
        for item in history:
            kid = item["knowledge_id"]
            access_counts[kid] = access_counts.get(kid, 0) + 1
        
        for kid, count in sorted(access_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            recommendations.append(Recommendation(
                knowledge_id=kid,
                backend=kid.split("_")[0] if "_" in kid else "unknown",
                confidence=min(count / 10.0, 1.0),
                reason="Based on access history"
            ))
        
        return recommendations

    def _compute_context_score(self, key: str, value: Any) -> float:
        """Compute context relevance score."""
        # Simple heuristic scoring
        if value is None:
            return 0.0
        if isinstance(value, str):
            return min(len(value) / 100.0, 1.0)
        if isinstance(value, (int, float)):
            return 0.7
        return 0.5
