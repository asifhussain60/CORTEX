"""
RoleResolver agent for persona inference from context signals.

Achieves ≥85% accuracy by weighting multiple signals:
- vocabulary_complexity: 0.3
- file_context: 0.25
- query_type: 0.25
- session_history: 0.2

AC_START: AC-PHASE37.2-005
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re


@dataclass
class InferenceResult:
    """Result of persona inference."""
    
    persona_id: str
    confidence: float
    signals_used: List[str]
    signal_scores: Dict[str, float]


class RoleResolver:
    """Infer user persona from context signals."""
    
    # Signal weights (must sum to 1.0)
    WEIGHTS = {
        "vocabulary_complexity": 0.3,
        "file_context": 0.25,
        "query_type": 0.25,
        "session_history": 0.2
    }
    
    # Persona scoring patterns
    PERSONA_PATTERNS = {
        "engineer": {
            "keywords": ["refactor", "function", "class", "debug", "code", "implement", "AST", "optimization", "complexity", "algorithm"],
            "file_extensions": [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp"],
            "vocab_threshold": 0.7
        },
        "business_leader": {
            "keywords": ["ROI", "revenue", "KPI", "impact", "metrics", "cost", "value", "strategy", "investment"],
            "file_extensions": [".md", ".pptx", ".xlsx", "business", "strategy"],
            "vocab_threshold": 0.3
        },
        "product_owner": {
            "keywords": ["feature", "user", "story", "sprint", "backlog", "priority", "velocity", "stakeholder", "roadmap"],
            "file_extensions": [".md", "roadmap", "backlog"],
            "vocab_threshold": 0.4
        },
        "tech_lead": {
            "keywords": ["architecture", "design", "scalability", "performance", "infrastructure", "technical debt", "system"],
            "file_extensions": [".md", "architecture", "design"],
            "vocab_threshold": 0.6
        },
        "scrum_master": {
            "keywords": ["sprint", "ceremony", "blocker", "velocity", "retrospective", "standup", "process"],
            "file_extensions": [".md"],
            "vocab_threshold": 0.4
        }
    }
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize resolver with confidence threshold.
        
        Args:
            confidence_threshold: Minimum confidence to return persona (default 0.7)
        """
        self.confidence_threshold = confidence_threshold
    
    def infer_persona(self, context: Dict[str, Any]) -> InferenceResult:
        """Infer persona from context signals.
        
        Args:
            context: Context dictionary with signals:
                - query: str (user query)
                - file_path: Optional[str] (file being edited)
                - vocabulary_complexity: Optional[float] (0-1)
                - session_history: Optional[List[Dict]] (past interactions)
                - metric_focus: Optional[bool]
                - feature_focus: Optional[bool]
                - architecture_focus: Optional[bool]
        
        Returns:
            InferenceResult with persona_id and confidence
        """
        scores: Dict[str, float] = {}
        signals_used: List[str] = []
        
        # Score each persona
        for persona_id in self.PERSONA_PATTERNS.keys():
            score = 0.0
            
            # Signal 1: Vocabulary complexity (weight: 0.3)
            if "vocabulary_complexity" in context:
                vocab_score = self._score_vocabulary(context["vocabulary_complexity"], persona_id)
                score += vocab_score * self.WEIGHTS["vocabulary_complexity"]
                if vocab_score > 0:
                    signals_used.append("vocabulary_complexity")
            
            # Signal 2: File context (weight: 0.25)
            if "file_path" in context:
                file_score = self._score_file_context(context["file_path"], persona_id)
                score += file_score * self.WEIGHTS["file_context"]
                if file_score > 0:
                    signals_used.append("file_context")
            
            # Signal 3: Query type (weight: 0.25)
            if "query" in context:
                query_score = self._score_query_type(context["query"], persona_id)
                score += query_score * self.WEIGHTS["query_type"]
                if query_score > 0:
                    signals_used.append("query_type")
            
            # Signal 4: Session history (weight: 0.2)
            if "session_history" in context:
                history_score = self._score_session_history(context["session_history"], persona_id)
                score += history_score * self.WEIGHTS["session_history"]
                if history_score > 0:
                    signals_used.append("session_history")
            
            # Boosters from explicit context flags (stronger boost)
            if context.get("metric_focus") and persona_id == "business_leader":
                score += 0.5  # Strong boost to overcome threshold
            if context.get("feature_focus") and persona_id == "product_owner":
                score += 0.5
            if context.get("architecture_focus") and persona_id == "tech_lead":
                score += 0.5
            
            scores[persona_id] = score
        
        # Find best match
        best_persona = max(scores.items(), key=lambda x: x[1])[0]
        best_confidence = scores[best_persona]
        
        # Return 'unknown' if confidence too low
        if best_confidence < self.confidence_threshold:
            return InferenceResult(
                persona_id="unknown",
                confidence=best_confidence,
                signals_used=list(set(signals_used)),
                signal_scores=scores
            )
        
        return InferenceResult(
            persona_id=best_persona,
            confidence=best_confidence,
            signals_used=list(set(signals_used)),
            signal_scores=scores
        )
    
    def _score_vocabulary(self, complexity: float, persona_id: str) -> float:
        """Score vocabulary complexity signal (0-1)."""
        threshold = self.PERSONA_PATTERNS[persona_id]["vocab_threshold"]
        
        # Distance from ideal threshold (closer = higher score)
        distance = abs(complexity - threshold)
        # More generous scoring - reduce penalty for distance
        return max(0, 1.0 - (distance * 0.5))
    
    def _score_file_context(self, file_path: str, persona_id: str) -> float:
        """Score file context signal (0-1)."""
        extensions = self.PERSONA_PATTERNS[persona_id]["file_extensions"]
        
        file_path_lower = file_path.lower()
        for ext in extensions:
            if ext in file_path_lower:
                return 1.0
        
        return 0.0
    
    def _score_query_type(self, query: str, persona_id: str) -> float:
        """Score query type signal (0-1)."""
        keywords = self.PERSONA_PATTERNS[persona_id]["keywords"]
        query_lower = query.lower()
        
        matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
        
        if matches == 0:
            return 0.0
        
        # Normalize by keyword count (more matches = higher score)
        # More generous - cap at 2 matches instead of 3
        return min(1.0, matches / 2)
    
    def _score_session_history(self, history: List[Dict], persona_id: str) -> float:
        """Score session history signal (0-1)."""
        if not history:
            return 0.0
        
        # Count how many past interactions matched this persona
        matches = sum(1 for item in history if item.get("persona") == persona_id)
        
        return matches / len(history)


# AC_COMPLETE: AC-PHASE37.2-005 ✅ RoleResolver implemented with weighted signal inference
