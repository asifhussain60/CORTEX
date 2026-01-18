"""Agent Confidence Scoring Module (AC-HP-003-02)"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

@dataclass
class ConfidenceScore:
    """Represents a confidence score for an action."""
    score_id: str
    action_type: str
    score: float
    justification: str
    factors: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: str = 'MEDIUM'
    requires_review: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

class ConfidenceScorer:
    """Scores confidence in agent actions."""
    def __init__(self):
        self.scores: List[ConfidenceScore] = []
    
    def calculate_confidence(self, action_type: str, data: Dict[str, Any]) -> ConfidenceScore:
        """Calculate confidence score for action."""
        base_score = 0.7
        
        # Adjust based on approvals
        if 'approval_count' in data:
            base_score += data['approval_count'] * 0.1
        
        # Adjust based on risk level
        risk = data.get('risk_level', 'MEDIUM')
        if risk == 'LOW':
            base_score += 0.15
        elif risk == 'HIGH':
            base_score -= 0.2
        
        # Adjust based on historical success
        if 'historical_success_rate' in data:
            base_score = (base_score + data['historical_success_rate']) / 2
        
        # Cap score
        score = min(1.0, max(0.0, base_score))
        
        score_id = f'SCORE-{uuid4().hex[:8]}'
        requires_review = score < 0.5 and action_type == 'DELETE'
        
        conf_score = ConfidenceScore(
            score_id=score_id,
            action_type=action_type,
            score=score,
            justification=f'Confidence score for {action_type}',
            factors=data,
            risk_assessment=risk,
            requires_review=requires_review,
        )
        self.scores.append(conf_score)
        return conf_score
    
    def get_score_history(self) -> List[ConfidenceScore]:
        """Get all scores."""
        return self.scores.copy()
    
    def get_scores_by_action(self, action_type: str) -> List[ConfidenceScore]:
        """Get scores for action type."""
        return [s for s in self.scores if s.action_type == action_type]
    
    def get_scoring_model(self) -> Dict[str, Any]:
        """Get scoring model documentation."""
        return {
            'description': 'Agent Confidence Scoring Model',
            'factors': ['approval_count', 'risk_level', 'historical_success_rate'],
            'version': '1.0',
        }
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights."""
        return {
            'approval_weight': 0.1,
            'risk_weight': 0.15,
            'history_weight': 0.5,
        }

__all__ = ['ConfidenceScore', 'ConfidenceScorer']
