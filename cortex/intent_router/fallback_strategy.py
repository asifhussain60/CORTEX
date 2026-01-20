"""Fallback Strategy - Fallback routing for low-confidence classifications.

Provides fallback chains and strategies for handling uncertain or
ambiguous intent classifications.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import List
from enum import Enum
from cortex.intent_router.classifier import IntentCategory


class FallbackType(Enum):
    """Types of fallback strategies."""
    GENERAL = "general"
    SIMILAR = "similar"
    CONTEXT = "context"
    USER_PROMPT = "user_prompt"


class FallbackStrategy:
    """Fallback routing strategies.
    
    Provides fallback chains for intent categories and confidence-based
    fallback decisions.
    
    Attributes:
        DEFAULT_FALLBACK: Default fallback handler name
        CONFIDENCE_THRESHOLD: Threshold for using fallback
    """
    
    DEFAULT_FALLBACK = "GeneralHandler"
    CONFIDENCE_THRESHOLD = 0.7
    
    @staticmethod
    def get_fallback_chain(intent: IntentCategory) -> List[str]:
        """Get fallback chain for an intent.
        
        Args:
            intent: Primary intent category
            
        Returns:
            List of fallback handler names in order of preference
        """
        chains = {
            IntentCategory.CREATE: ["CreateHandler", "ModifyHandler", "GeneralHandler"],
            IntentCategory.FIX: ["FixHandler", "AnalyzeHandler", "GeneralHandler"],
            IntentCategory.ANALYZE: ["AnalyzeHandler", "QueryHandler", "GeneralHandler"],
            IntentCategory.OPTIMIZE: ["OptimizeHandler", "RefactorHandler", "GeneralHandler"],
            IntentCategory.REFACTOR: ["RefactorHandler", "ModifyHandler", "GeneralHandler"],
            IntentCategory.TEST: ["TestHandler", "AnalyzeHandler", "GeneralHandler"],
            IntentCategory.DOCUMENT: ["DocumentHandler", "QueryHandler", "GeneralHandler"],
            IntentCategory.MODIFY: ["ModifyHandler", "CreateHandler", "GeneralHandler"],
            IntentCategory.QUERY: ["QueryHandler", "GeneralHandler"],
            IntentCategory.COMMAND: ["CommandHandler", "GeneralHandler"],
            IntentCategory.NAVIGATION: ["NavigationHandler", "GeneralHandler"],
            IntentCategory.UNKNOWN: ["GeneralHandler"],
        }
        return chains.get(intent, ["GeneralHandler"])
    
    @staticmethod
    def apply_fallback(confidence: float, primary_handler: str) -> str:
        """Apply fallback strategy based on confidence.
        
        Args:
            confidence: Classification confidence score
            primary_handler: Primary handler name
            
        Returns:
            Handler name to use (primary or fallback)
        """
        if confidence >= FallbackStrategy.CONFIDENCE_THRESHOLD:
            return primary_handler
        return FallbackStrategy.DEFAULT_FALLBACK


__all__ = ["FallbackType", "FallbackStrategy"]
