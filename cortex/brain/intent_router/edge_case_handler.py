"""AC-PHX-007-14: Edge Case Handling"""
from typing import Any, Optional

from cortex.brain.intent_router.classifier import IntentCategory


class EdgeCaseHandler:
    """Handles edge cases in intent classification."""

    EMPTY_TEXT_FALLBACK = IntentCategory.UNKNOWN
    SPECIAL_CHARS_THRESHOLD = 0.5

    @staticmethod
    def handle_empty_input(text: Optional[str]) -> bool:
        """Check if input is empty."""
        return not text or len(text.strip()) == 0

    @staticmethod
    def handle_special_characters(text: str) -> bool:
        """Check if text has excessive special characters."""
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        return special_chars / len(text) > EdgeCaseHandler.SPECIAL_CHARS_THRESHOLD if text else False

    @staticmethod
    def handle_very_long_input(text: str, max_length: int = 10000) -> str:
        """Truncate very long input."""
        return text[:max_length] if len(text) > max_length else text

    @staticmethod
    def handle_unicode_text(text: str) -> str:
        """Normalize unicode text."""
        return text.encode("utf-8", errors="ignore").decode("utf-8")
