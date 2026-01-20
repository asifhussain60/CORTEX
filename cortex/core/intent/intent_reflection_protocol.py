"""Intent Reflection Protocol - Reflective protocol for intent comprehension.

Provides structured protocol for intent reflection, analysis, and comprehension
in conversational contexts.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class ReflectionType(Enum):
    """Types of intent reflection."""

    CLARIFICATION = "clarification"
    DECOMPOSITION = "decomposition"
    VALIDATION = "validation"
    REFINEMENT = "refinement"
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"


@dataclass
class ReflectionQuestion:
    """A clarification question during reflection.

    Attributes:
        question: The question text.
        type: Type of reflection question.
        expected_answers: Possible expected answers.
    """

    question: str
    type: ReflectionType
    expected_answers: List[str] = None

    def __post_init__(self) -> None:
        """Initialize expected answers if not provided."""
        if self.expected_answers is None:
            self.expected_answers = []


@dataclass
class IntentReflection:
    """Result of intent reflection analysis.

    Attributes:
        original_intent: Original intent statement.
        refined_intent: Refined/clarified intent.
        confidence: Confidence in refined intent (0-1).
        clarification_questions: Questions asked during reflection.
        decomposed_goals: Goals decomposed from intent.
        metadata: Additional metadata.
    """

    original_intent: str
    refined_intent: str
    confidence: float
    clarification_questions: List[ReflectionQuestion] = None
    decomposed_goals: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize optional fields."""
        if self.clarification_questions is None:
            self.clarification_questions = []
        if self.decomposed_goals is None:
            self.decomposed_goals = []
        if self.metadata is None:
            self.metadata = {}


class IntentReflectionProtocol:
    """Protocol for intent reflection and comprehension."""

    def __init__(self) -> None:
        """Initialize reflection protocol."""
        self.reflection_history: List[IntentReflection] = []

    def reflect(self, intent: str) -> IntentReflection:
        """Reflect on an intent to clarify and refine it.

        Args:
            intent: Intent to reflect on.

        Returns:
            IntentReflection with refined intent and analysis.
        """
        # Basic reflection logic
        questions = self._generate_clarification_questions(intent)
        goals = self._decompose_intent(intent)

        reflection = IntentReflection(
            original_intent=intent,
            refined_intent=intent,  # Start with original
            confidence=0.85,  # Placeholder
            clarification_questions=questions,
            decomposed_goals=goals,
        )

        # Store in history
        self.reflection_history.append(reflection)

        return reflection

    def _generate_clarification_questions(self, intent: str) -> List[ReflectionQuestion]:
        """Generate clarification questions for intent.

        Args:
            intent: Intent to clarify.

        Returns:
            List of clarification questions.
        """
        questions = []

        # Always ask about scope
        questions.append(
            ReflectionQuestion(
                question="What is the scope of this operation?",
                type=ReflectionType.CLARIFICATION,
                expected_answers=["full", "partial", "specific"],
            )
        )

        # Ask about priority if time-sensitive
        if any(w in intent.lower() for w in ["urgent", "asap", "quickly"]):
            questions.append(
                ReflectionQuestion(
                    question="What is the priority level?",
                    type=ReflectionType.CLARIFICATION,
                    expected_answers=["high", "medium", "low"],
                )
            )

        return questions

    def _decompose_intent(self, intent: str) -> List[str]:
        """Decompose intent into sub-goals.

        Args:
            intent: Intent to decompose.

        Returns:
            List of decomposed goals.
        """
        goals = []

        # Simple decomposition based on keywords
        if "and" in intent.lower():
            parts = intent.split(" and ")
            goals.extend([p.strip() for p in parts])
        elif "," in intent:
            parts = intent.split(",")
            goals.extend([p.strip() for p in parts])
        else:
            goals.append(intent)

        return goals

    def validate_reflection(self, reflection: IntentReflection) -> bool:
        """Validate a reflection result.

        Args:
            reflection: Reflection to validate.

        Returns:
            True if reflection is valid, False otherwise.
        """
        # Basic validation
        return (
            bool(reflection.original_intent)
            and bool(reflection.refined_intent)
            and 0 <= reflection.confidence <= 1
        )

    def get_reflection_history(self) -> List[IntentReflection]:
        """Get reflection history.

        Returns:
            List of reflections performed.
        """
        return self.reflection_history.copy()

    def clear_history(self) -> None:
        """Clear reflection history."""
        self.reflection_history.clear()


# Alias for backward compatibility
IntentReflectionEngine = IntentReflectionProtocol

__all__ = [
    "IntentReflectionProtocol",
    "IntentReflectionEngine",
    "IntentReflection",
    "ReflectionQuestion",
    "ReflectionType",
]

