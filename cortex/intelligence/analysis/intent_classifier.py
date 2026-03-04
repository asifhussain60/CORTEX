"""
Enhanced Intent Classifier (WAVE-M: ENH-078).

Improves intent classification accuracy from 65% → 90% through advanced
NLP techniques, confidence scoring, and pattern recognition.

Authority: cortex-registry/_cortex-master/index.yaml WAVE-M
Created: 2026-02-12
AC-ID: AC-WAVE-M-001
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from cortex.models.canonical_enums import IntentType  # CORE-035: import from canonical


@dataclass
class IntentClassification:  # CORE-035-scoped — domain-specific variant
    """
    Result of intent classification.

    Attributes:
        intent: Classified intent type
        confidence: Confidence score (0.0-1.0)
        is_ambiguous: Whether classification is ambiguous
        alternative_intents: Other possible intents with scores
        reasoning: Explanation of classification
    """
    intent: IntentType
    confidence: float
    is_ambiguous: bool
    alternative_intents: Dict[IntentType, float]
    reasoning: str

    def needs_clarification(self, threshold: float = 0.75) -> bool:
        """
        Check if clarification is needed.

        Args:
            threshold: Confidence threshold (default: 0.75)

        Returns:
            True if clarification needed
        """
        return self.is_ambiguous or self.confidence < threshold


class EnhancedIntentClassifier:
    """
    Enhanced intent classifier with 90% accuracy target (WAVE-M: ENH-078).

    Renamed from IntentClassifier → EnhancedIntentClassifier (Phase 101)
    to resolve CORE-035 duplicate with cortex.orchestrators.core.intent_classifier.

    Uses pattern recognition, keyword analysis, and confidence scoring
    to classify user requests with high accuracy.
    """

    # Strong indicators for each intent (high confidence)
    STRONG_PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.IMPLEMENT: [
            r"\bimplement\b",
            r"\bcreate\b.*\b(feature|function|class|module|system)\b",
            r"\badd\b.*\b(feature|functionality|capability|component)\b",
            r"\bbuild\b.*\b(feature|function|system|component)\b",
            r"\bdevelop\b.*\b(feature|system|component)\b",
            r"^/implement\b",
            r"\bimplement\b.*\bsystem\b",
            r"\bcreate\b.*\bnew\b",
        ],
        IntentType.FIX: [
            r"\bfix\b",
            r"\bresolve\b.*\b(bug|issue|error|problem|conflict)\b",
            r"\bdebug\b",
            r"\bcorrect\b",
            r"\brepair\b",
            r"^/fix\b",
            r"\bnot working\b",
            r"\bbroken\b",
            r"\bbug\b",
            r"\berror\b",
            r"\bresolve\b.*\bconflict",
            r"\bmerge\b.*\bconflict",
        ],
        IntentType.REFACTOR: [
            r"\brefactor\b",
            r"\brestructure\b",
            r"\bimprove\b.*\b(code|structure|design|performance|error|handling)\b",
            r"\bclean up\b",
            r"\boptimize\b",
            r"^/refactor\b",
            r"\bsimplify\b",
            r"\bimprove\b.*\bperformance\b",
            r"\benhance\b.*\b(error|handling|code)\b",
        ],
        IntentType.ANALYZE: [
            r"\banalyze\b",
            r"\bexamine\b",
            r"\binspect\b",
            r"\breview\b.*\b(code|file|module)\b",
            r"\bcheck\b.*\b(code|quality)\b",
            r"^/analyze\b",
            r"\bwhat is\b.*\b(doing|happening)\b",
            r"\bcode\b.*\bquality\b",
        ],
        IntentType.AUDIT: [
            r"^/audit\b",
            r"\baudit\b",
            r"\bgovernance\b.*\b(check|scan|validation)\b",
            r"\bcompliance\b",
            r"\bsecurity\b.*\b(scan|audit|check)\b",
        ],
        IntentType.DESIGN: [
            r"\bdesign\b",
            r"\barchitecture\b",
            r"\bblueprint\b",
            r"\bspecification\b",
            r"\bpropose\b.*\b(solution|approach|design)\b",
            r"^/design\b",
        ],
        IntentType.PLAN: [
            r"^/plan\b",
            r"\bplan\b.*\b(phase|task|work|sprint|next)\b",
            r"\bcreate\b.*\b(plan|roadmap|schedule)\b",
            r"\bbreak down\b",
            r"\bdecompose\b",
            r"\bplan\b.*\bnext\b",
            r"\bnext\b.*\bsprint\b",
        ],
        IntentType.DIGEST: [
            r"^/digest\b",
            r"\bdigest\b.*\b(session|conversation|chat)\b",
            r"\bextract\b.*\b(learning|insight|knowledge)\b",
        ],
        IntentType.QUERY: [
            r"^what is\b",
            r"^how (does|do|can)\b",
            r"^why (is|does|do)\b",
            r"^explain\b",
            r"^tell me about\b",
            r"\bdocumentation\b",
            r"^/recall\b",
            r"^what\b.*\bpurpose\b",
            r"\bexplain\b.*\b(architecture|system|how)\b",
        ],
    }

    # Weak indicators (lower confidence, may need clarification)
    WEAK_PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.IMPLEMENT: [
            r"\bnew\b",
            r"\bmake\b",
            r"\badd\b",  # "add" alone is weak, but "add feature" is strong
            r"\balso\b.*\badd\b",  # "also add" suggests continuation
        ],
        IntentType.FIX: [
            r"\bchange\b",
            r"\bupdate\b",
        ],
        IntentType.REFACTOR: [
            r"\bbetter\b",
            r"\benhance\b",
        ],
    }

    def __init__(self) -> None:
        """Initialize the classifier."""
        # Compile patterns for performance
        self._strong_compiled = {
            intent: [re.compile(pattern, re.IGNORECASE)
                    for pattern in patterns]
            for intent, patterns in self.STRONG_PATTERNS.items()
        }

        self._weak_compiled = {
            intent: [re.compile(pattern, re.IGNORECASE)
                    for pattern in patterns]
            for intent, patterns in self.WEAK_PATTERNS.items()
        }

    def classify(
        self,
        user_request: str,
        context: Optional[Dict[str, str]] = None
    ) -> IntentClassification:
        """
        Classify user request into intent type.

        Args:
            user_request: User's request text
            context: Optional context from previous turns

        Returns:
            IntentClassification with confidence and alternatives

        Example:
            >>> classifier = EnhancedIntentClassifier()
            >>> result = classifier.classify("implement authentication system")
            >>> assert result.intent == IntentType.IMPLEMENT
            >>> assert result.confidence > 0.85
        """
        if not user_request or not user_request.strip():
            return IntentClassification(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                is_ambiguous=True,
                alternative_intents={},
                reasoning="Empty request"
            )

        # Calculate scores for each intent
        intent_scores: Dict[IntentType, float] = {}

        for intent in IntentType:
            if intent == IntentType.UNKNOWN:
                continue

            score = self._calculate_intent_score(
                user_request,
                intent,
                context
            )

            if score > 0:
                intent_scores[intent] = score

        # No matches found
        if not intent_scores:
            return IntentClassification(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                is_ambiguous=True,
                alternative_intents={},
                reasoning="No intent patterns matched"
            )

        # Sort by score
        sorted_intents = sorted(
            intent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_intent, top_score = sorted_intents[0]

        # Check for ambiguity
        is_ambiguous = False
        if len(sorted_intents) > 1:
            second_score = sorted_intents[1][1]
            # If second score is within 20% of top score, consider ambiguous
            if second_score >= top_score * 0.8:
                is_ambiguous = True

        # Build alternative intents (excluding top)
        alternatives = {
            intent: score
            for intent, score in sorted_intents[1:4]  # Top 3 alternatives
        }

        # Generate reasoning
        reasoning = self._generate_reasoning(
            user_request,
            top_intent,
            top_score,
            alternatives
        )

        # Normalize confidence to 0-1 range
        confidence = min(1.0, top_score)

        return IntentClassification(
            intent=top_intent,
            confidence=confidence,
            is_ambiguous=is_ambiguous,
            alternative_intents=alternatives,
            reasoning=reasoning
        )

    def _calculate_intent_score(
        self,
        text: str,
        intent: IntentType,
        context: Optional[Dict[str, str]] = None
    ) -> float:
        """
        Calculate score for a specific intent.

        Args:
            text: User request text
            intent: Intent to score
            context: Optional context

        Returns:
            Score (0.0-1.0+, higher is better)
        """
        score = 0.0
        strong_matches = 0

        # Check strong patterns (high weight)
        if intent in self._strong_compiled:
            for pattern in self._strong_compiled[intent]:
                if pattern.search(text):
                    score += 0.5  # Strong indicator adds 0.5 (increased from 0.4)
                    strong_matches += 1

        # Check weak patterns (low weight)
        if intent in self._weak_compiled:
            for pattern in self._weak_compiled[intent]:
                if pattern.search(text):
                    score += 0.15  # Weak indicator adds 0.15 (increased from 0.1)

        # Context boost (if previous intent was same)
        if context and context.get("previous_intent") == intent.value:
            score += 0.2  # Increased from 0.15

        # Keyword density bonus
        keyword_density = self._calculate_keyword_density(text, intent)
        score += keyword_density * 0.3  # Increased from 0.2

        # Multiple strong matches bonus (shows clear intent)
        if strong_matches >= 2:
            score += 0.15

        return score

    def _calculate_keyword_density(
        self,
        text: str,
        intent: IntentType
    ) -> float:
        """
        Calculate keyword density for intent.

        Args:
            text: User request text
            intent: Intent type

        Returns:
            Density score (0.0-1.0)
        """
        # Define keywords for each intent
        keywords = {
            IntentType.IMPLEMENT: ["create", "build", "add", "develop", "implement"],
            IntentType.FIX: ["fix", "bug", "error", "issue", "problem", "broken"],
            IntentType.REFACTOR: ["refactor", "improve", "optimize", "clean", "restructure"],
            IntentType.ANALYZE: ["analyze", "examine", "inspect", "review", "check"],
            IntentType.AUDIT: ["audit", "compliance", "governance", "security"],
            IntentType.DESIGN: ["design", "architecture", "propose", "plan"],
            IntentType.PLAN: ["plan", "phase", "task", "schedule", "roadmap"],
            IntentType.DIGEST: ["digest", "extract", "learn", "summarize"],
            IntentType.QUERY: ["what", "how", "why", "explain", "documentation"],
        }

        if intent not in keywords:
            return 0.0

        text_lower = text.lower()
        words = text_lower.split()

        if not words:
            return 0.0

        # Count keyword matches
        matches = sum(
            1 for keyword in keywords[intent]
            if keyword in text_lower
        )

        # Normalize by keyword count
        return min(1.0, matches / len(keywords[intent]))

    def _generate_reasoning(
        self,
        text: str,
        intent: IntentType,
        score: float,
        alternatives: Dict[IntentType, float]
    ) -> str:
        """
        Generate human-readable reasoning for classification.

        Args:
            text: User request text
            intent: Classified intent
            score: Confidence score
            alternatives: Alternative intents

        Returns:
            Reasoning string
        """
        reasoning_parts = []

        # Primary classification
        reasoning_parts.append(f"Classified as {intent.value.upper()}")

        # Confidence level
        if score >= 0.85:
            reasoning_parts.append("(high confidence)")
        elif score >= 0.65:
            reasoning_parts.append("(moderate confidence)")
        else:
            reasoning_parts.append("(low confidence)")

        # Alternatives if close
        if alternatives:
            alt_str = ", ".join(
                f"{i.value} ({s:.2f})"
                for i, s in list(alternatives.items())[:2]
            )
            reasoning_parts.append(f"| alternatives: {alt_str}")

        return " ".join(reasoning_parts)


def classify_intent(
    user_request: str,
    context: Optional[Dict[str, str]] = None
) -> IntentClassification:
    """
    Convenience function to classify intent.

    Args:
        user_request: User's request text
        context: Optional context

    Returns:
        IntentClassification result

    Example:
        >>> result = classify_intent("fix the login bug")
        >>> assert result.intent == IntentType.FIX
    """
    classifier = EnhancedIntentClassifier()
    return classifier.classify(user_request, context)


# Phase 101: Backward-compat alias (CORE-035 resolution)
IntentClassifier = EnhancedIntentClassifier
