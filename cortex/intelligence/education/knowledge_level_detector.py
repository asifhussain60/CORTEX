"""
Knowledge Level Detector for CORTEX ASK Mode.

Intelligently classifies user knowledge level based on:
- Query complexity and technical depth
- Terminology usage
- Conversation history
- Question types (what/how/why/troubleshooting)

Levels:
- BEGINNER: General questions, "what is" queries, no technical terms
- INTERMEDIATE: Implementation details, integration questions, component-specific
- ADVANCED: Architecture, design patterns, optimization, extension, best practices

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Set


class KnowledgeLevel(Enum):
    """User knowledge level classification."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class DetectionSignals:
    """Signals used for knowledge level detection."""
    query_complexity: float  # 0.0-1.0
    technical_depth: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    detected_level: KnowledgeLevel
    reasoning: str  # Explanation of detection


class KnowledgeLevelDetector:
    """
    Detects user knowledge level from queries and conversation history.

    Strategy:
    1. Analyze query for technical terminology
    2. Classify question type (what/how/why/troubleshooting)
    3. Consider conversation history depth
    4. Compute confidence score

    Signals:
    - BEGINNER: "what is", "explain", general questions, no technical terms
    - INTERMEDIATE: "how does", "integrate", specific components, some technical terms
    - ADVANCED: "why", "optimize", "extend", "pattern", heavy technical terminology
    """

    def __init__(self):
        """Initialize detector with keyword mappings."""
        # Beginner signal keywords
        self._beginner_keywords: Set[str] = {
            "what is", "what are", "explain", "introduction", "overview",
            "basics", "getting started", "new to", "beginner", "simple",
            "tell me about", "help me understand"
        }

        # Intermediate signal keywords
        self._intermediate_keywords: Set[str] = {
            "how does", "how do i", "how can i", "implement", "integrate",
            "configure", "setup", "use", "work with", "connect",
            "troubleshoot", "debug", "fix", "error", "issue"
        }

        # Advanced signal keywords
        self._advanced_keywords: Set[str] = {
            "why does", "why is", "design pattern", "architecture",
            "optimize", "performance", "extend", "customize", "enhance",
            "best practices", "alternative", "trade-off", "scale",
            "internal", "low-level", "algorithm"
        }

        # Technical terminology (indicates higher knowledge)
        self._technical_terms: Set[str] = {
            "ast", "parser", "interface", "inheritance", "polymorphism",
            "decorator", "factory", "singleton", "dependency injection",
            "asynchronous", "concurrency", "thread", "process",
            "algorithm", "complexity", "refactor", "schema",
            "visitor pattern", "strategy pattern", "observer pattern"
        }

        # CORTEX-specific technical terms
        self._cortex_technical: Set[str] = {
            "orchestrator", "iorchestrator", "wiring", "mcp server",
            "lens protocol", "intent router", "enforcement", "governance",
            "ast analyzer", "truth verification", "progressive disclosure"
        }

    def detect_level(
        self,
        query: str,
        conversation_history: List[str]
    ) -> KnowledgeLevel:
        """
        Detect user knowledge level from query and history.

        Args:
            query: Current user query
            conversation_history: Previous queries in conversation

        Returns:
            Detected KnowledgeLevel
        """
        signals = self.get_detection_signals(query, conversation_history)
        return signals.detected_level

    def get_detection_signals(
        self,
        query: str,
        conversation_history: List[str]
    ) -> DetectionSignals:
        """
        Get detailed detection signals for knowledge level.

        Args:
            query: Current user query
            conversation_history: Previous queries in conversation

        Returns:
            DetectionSignals with scores and reasoning
        """
        query_lower = query.lower()

        # Calculate signal scores
        beginner_score = self._calculate_beginner_score(query_lower)
        intermediate_score = self._calculate_intermediate_score(query_lower)
        advanced_score = self._calculate_advanced_score(query_lower)

        # Adjust for conversation history
        history_depth = len(conversation_history)
        if history_depth > 5:
            # Long conversation suggests higher knowledge
            intermediate_score += 0.2
            advanced_score += 0.1
        elif history_depth > 10:
            advanced_score += 0.3

        # Determine level from scores
        max_score = max(beginner_score, intermediate_score, advanced_score)

        # Advanced pattern keywords take priority
        if "design pattern" in query_lower or "architecture" in query_lower:
            if advanced_score >= 0.4:
                level = KnowledgeLevel.ADVANCED
                reasoning = "Question about architecture, optimization, or extension with technical depth"
            else:
                level = KnowledgeLevel.INTERMEDIATE
                reasoning = "Question about implementation, integration, or troubleshooting"
        elif max_score == beginner_score and beginner_score > 0.5:
            level = KnowledgeLevel.BEGINNER
            reasoning = "General or 'what is' question with minimal technical terminology"
        elif max_score == advanced_score and advanced_score > 0.4:
            level = KnowledgeLevel.ADVANCED
            reasoning = "Question about architecture, optimization, or extension with technical depth"
        else:
            level = KnowledgeLevel.INTERMEDIATE
            reasoning = "Question about implementation, integration, or troubleshooting"

        # Calculate query complexity and technical depth
        query_complexity = self._calculate_query_complexity(query_lower)
        technical_depth = self._calculate_technical_depth(query_lower)

        # Confidence is based on signal strength
        confidence = max_score

        return DetectionSignals(
            query_complexity=query_complexity,
            technical_depth=technical_depth,
            confidence=confidence,
            detected_level=level,
            reasoning=reasoning
        )

    def _calculate_beginner_score(self, query: str) -> float:
        """Calculate beginner signal score (0.0-1.0)."""
        score = 0.0

        # Check for beginner keywords (strong signal)
        for keyword in self._beginner_keywords:
            if keyword in query:
                score += 0.5

        # Penalize for technical terms
        tech_count = sum(1 for term in self._technical_terms if term in query)
        score -= tech_count * 0.2

        # Penalize for CORTEX-specific technical terms
        cortex_count = sum(1 for term in self._cortex_technical if term in query)
        score -= cortex_count * 0.15

        # Short, simple questions suggest beginner
        word_count = len(query.split())
        if word_count < 8:
            score += 0.3

        return max(0.0, min(1.0, score))

    def _calculate_intermediate_score(self, query: str) -> float:
        """Calculate intermediate signal score (0.0-1.0)."""
        score = 0.0

        # Check for intermediate keywords
        for keyword in self._intermediate_keywords:
            if keyword in query:
                score += 0.4

        # Check for CORTEX-specific terms (indicates familiarity)
        cortex_count = sum(1 for term in self._cortex_technical if term in query)
        score += cortex_count * 0.25

        # Specific component names suggest intermediate
        if "orchestrator" in query and any(
            prefix in query for prefix in ["master", "intent", "tdd", "lens", "enforcement"]
        ):
            score += 0.3

        # Troubleshooting questions are intermediate
        if "why is my" in query or (" not " in query and any(kw in query for kw in ["register", "work", "error"])):
            score += 0.5

        # "Design pattern" without "used" keyword is advanced, not intermediate
        # So we don't boost intermediate score for it

        return max(0.0, min(1.0, score))

    def _calculate_advanced_score(self, query: str) -> float:
        """Calculate advanced signal score (0.0-1.0)."""
        score = 0.0

        # Check for advanced keywords (strong signal)
        for keyword in self._advanced_keywords:
            if keyword in query:
                score += 0.6  # Increased from 0.5

        # Check for technical terminology
        tech_count = sum(1 for term in self._technical_terms if term in query)
        score += tech_count * 0.3

        # Questions about alternatives or trade-offs suggest advanced
        if any(word in query for word in ["alternative", "instead", "versus", "compared to"]):
            score += 0.4

        # Asking "why" suggests deeper understanding
        if query.startswith("why "):
            score += 0.4

        # Questions about "not" or troubleshooting can be intermediate
        if " not " in query or "why is my" in query:
            score -= 0.3  # Increased penalty

        return max(0.0, min(1.0, score))

    def _calculate_query_complexity(self, query: str) -> float:
        """Calculate query complexity score (0.0-1.0)."""
        # Longer queries are more complex
        word_count = len(query.split())
        length_score = min(word_count / 30.0, 1.0)

        # Multiple clauses increase complexity
        clause_count = query.count(',') + query.count('and') + query.count('or')
        clause_score = min(clause_count / 5.0, 1.0)

        # Technical terms increase complexity
        tech_count = sum(1 for term in self._technical_terms if term in query)
        tech_score = min(tech_count / 3.0, 1.0)

        return (length_score + clause_score + tech_score) / 3.0

    def _calculate_technical_depth(self, query: str) -> float:
        """Calculate technical depth score (0.0-1.0)."""
        # Count technical and CORTEX-specific terms
        tech_count = sum(1 for term in self._technical_terms if term in query)
        cortex_count = sum(1 for term in self._cortex_technical if term in query)

        total_tech = tech_count + cortex_count

        # Normalize to 0-1 range (assume 5+ terms is very technical)
        return min(total_tech / 5.0, 1.0)


# Example usage for testing
if __name__ == "__main__":
    detector = KnowledgeLevelDetector()

    test_queries = [
        "What is CORTEX?",
        "How does the IntentRouter classify intents?",
        "What design patterns are used in the EnforcementOrchestrator?",
    ]

    for query in test_queries:
        signals = detector.get_detection_signals(query, [])
        print(f"\nQuery: {query}")
        print(f"Level: {signals.detected_level.value}")
        print(f"Confidence: {signals.confidence:.2f}")
        print(f"Reasoning: {signals.reasoning}")
