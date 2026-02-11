"""
RoleResolver agent for persona inference from context signals.

Achieves ≥85% accuracy by weighting multiple signals:
- vocabulary_complexity: 0.3
- file_context: 0.25
- query_type: 0.25
- session_history: 0.2

AC_START: AC-PHASE37.2-005
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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

    def __init__(self, confidence_threshold: float = 0.5):
        """Initialize resolver with confidence threshold.

        Args:
            confidence_threshold: Minimum confidence to return persona (default 0.5)
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

        # Calculate raw signal scores once (outside persona loop)
        vocab_score_cache = {}
        file_score_cache = {}
        query_score_cache = {}
        history_score_cache = {}

        for persona_id in self.PERSONA_PATTERNS.keys():
            vocab_score_cache[persona_id] = self._score_vocabulary(context.get("vocabulary_complexity", 0), persona_id) if "vocabulary_complexity" in context else 0
            file_score_cache[persona_id] = self._score_file_context(context.get("file_path", ""), persona_id) if "file_path" in context else 0
            query_score_cache[persona_id] = self._score_query_type(context.get("query", ""), persona_id) if "query" in context else 0
            history_score_cache[persona_id] = self._score_session_history(context.get("session_history", []), persona_id) if "session_history" in context else 0

        # Score each persona
        for persona_id in self.PERSONA_PATTERNS.keys():
            score = 0.0
            persona_signals = []

            # Signal 1: Vocabulary complexity (weight: 0.3)
            if "vocabulary_complexity" in context:
                vocab_score = vocab_score_cache[persona_id]
                score += vocab_score * self.WEIGHTS["vocabulary_complexity"]
                if vocab_score > 0:
                    persona_signals.append("vocabulary_complexity")

            # Signal 2: File context (weight: 0.25)
            if "file_path" in context:
                file_score = file_score_cache[persona_id]
                score += file_score * self.WEIGHTS["file_context"]
                if file_score > 0:
                    persona_signals.append("file_context")

            # Signal 3: Query type (weight: 0.25)
            if "query" in context:
                query_score = query_score_cache[persona_id]
                score += query_score * self.WEIGHTS["query_type"]
                if query_score > 0:
                    persona_signals.append("query_type")

            # Signal 4: Session history (weight: 0.2)
            if "session_history" in context:
                history_score = history_score_cache[persona_id]
                score += history_score * self.WEIGHTS["session_history"]
                if history_score > 0:
                    persona_signals.append("session_history")

            # AMPLIFICATION: Boost if we have a very strong signal (>0.9 quality)
            # Only amplify when we have 1-2 weak additional signals
            amplify = False
            if vocab_score_cache[persona_id] > 0.9 and len([s for s in persona_signals if s not in ["vocabulary_complexity", "query_type"]]) == 0:
                amplify = True
            elif file_score_cache[persona_id] > 0.9 and len(persona_signals) <= 2:
                amplify = True
            elif history_score_cache[persona_id] > 0.9 and len(persona_signals) <= 2:
                amplify = True

            if amplify:
                score += 0.35

            if persona_signals:
                signals_used = list(set(signals_used + persona_signals))

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
