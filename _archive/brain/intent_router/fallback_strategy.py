"""AC-PHX-007-07: Fallback Strategies"""
from typing import Any, Dict, List

from cortex.brain.intent_router.classifier import IntentCategory


class FallbackStrategy:
    """Fallback strategies for low-confidence intents."""

    DEFAULT_FALLBACK = "GeneralHandler"

    @staticmethod
    def get_fallback_chain(intent: IntentCategory) -> List[str]:
        """Get fallback chain for intent."""
        fallback_map = {
            IntentCategory.CREATE: ["ModifyHandler", "GeneralHandler"],
            IntentCategory.FIX: ["AnalyzeHandler", "GeneralHandler"],
            IntentCategory.REFACTOR: ["OptimizeHandler", "ModifyHandler"],
        }
        return fallback_map.get(intent, ["GeneralHandler"])

    @staticmethod
    def apply_fallback(confidence: float, primary: str) -> str:
        """Apply fallback based on confidence."""
        if confidence > 0.7:
            return primary
        return FallbackStrategy.DEFAULT_FALLBACK
