"""Intent Lens Context Builder - Constructs contextual information for intent analysis.

Builds comprehensive context from user intent, operation history, and system state
for intelligent intent routing and comprehension.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class LensContext:
    """Context built for intent analysis.

    Attributes:
        intent_id: Unique intent identifier.
        original_input: Original user input.
        parsed_intent: Parsed intent structure.
        history: Previous operations in conversation.
        system_state: Current system state snapshot.
        user_profile: User profile and preferences.
        timestamp: When context was created.
        metadata: Additional context metadata.
    """

    intent_id: str
    original_input: str
    parsed_intent: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    system_state: Dict[str, Any] = field(default_factory=dict)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LensContextBuilder:
    """Builds lens context from intent and system state."""

    def __init__(self) -> None:
        """Initialize context builder."""
        self.contexts: Dict[str, LensContext] = {}

    def build(
        self,
        intent_id: str,
        original_input: str,
        history: Optional[List[Dict[str, Any]]] = None,
        system_state: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> LensContext:
        """Build a lens context.

        Args:
            intent_id: Intent identifier.
            original_input: Original user input.
            history: Previous operations.
            system_state: Current system state.
            user_profile: User profile.

        Returns:
            LensContext with built context.
        """
        context = LensContext(
            intent_id=intent_id,
            original_input=original_input,
            history=history or [],
            system_state=system_state or {},
            user_profile=user_profile or {},
        )

        # Parse intent from input
        context.parsed_intent = self._parse_intent(original_input)

        # Cache context
        self.contexts[intent_id] = context

        return context

    def _parse_intent(self, input_text: str) -> Dict[str, Any]:
        """Parse intent from input text.

        Args:
            input_text: Input text to parse.

        Returns:
            Parsed intent dictionary.
        """
        # Simple intent parsing
        lower_text = input_text.lower()

        intent_type = "general"
        if any(w in lower_text for w in ["create", "make", "new"]):
            intent_type = "create"
        elif any(w in lower_text for w in ["delete", "remove"]):
            intent_type = "delete"
        elif any(w in lower_text for w in ["update", "modify"]):
            intent_type = "update"
        elif any(w in lower_text for w in ["list", "show", "get"]):
            intent_type = "retrieve"
        elif any(w in lower_text for w in ["help", "explain", "how"]):
            intent_type = "help"

        return {
            "type": intent_type,
            "raw_input": input_text,
            "confidence": 0.8,  # Placeholder confidence
            "entities": [],  # Could be extracted here
        }

    def get_context(self, intent_id: str) -> Optional[LensContext]:
        """Get a stored context.

        Args:
            intent_id: Intent identifier.

        Returns:
            LensContext or None if not found.
        """
        return self.contexts.get(intent_id)

    def enrich_context(
        self, intent_id: str, enrichment: Dict[str, Any]
    ) -> Optional[LensContext]:
        """Enrich an existing context.

        Args:
            intent_id: Intent identifier.
            enrichment: Additional context to add.

        Returns:
            Updated LensContext or None if not found.
        """
        context = self.contexts.get(intent_id)
        if context:
            context.metadata.update(enrichment)
        return context


# Alias for backward compatibility
LENSContextBuilder = LensContextBuilder

__all__ = [
    "LensContext",
    "LensContextBuilder",
    "LENSContextBuilder",
]

