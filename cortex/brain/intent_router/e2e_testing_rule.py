"""
E2E Testing Rule for Intent Classification.

Authority: AC-GOLDEN-E2E-006
Adds deterministic classification for golden test scenarios.
"""

import re
from typing import List

from cortex.brain.intent_router.classifier import (
    ClassificationRule,
    IntentCategory,
    IntentSignal,
)


class E2ETestingRule(ClassificationRule):
    """
    Detect E2E testing intent for golden test harness.
    
    Matches utterances like:
    - "golden tests"
    - "run e2e tests"
    - "end-to-end test"
    
    High confidence (0.95) for deterministic routing.
    """
    
    def __init__(self) -> None:
        """Initialize E2E testing rule."""
        self._patterns = [
            r'\bgolden\s+tests?\b',
            r'\be2e\s+tests?\b',
            r'\bend[- ]to[- ]end\s+tests?\b',
            r'\bgolden\s+test\s+harness\b',
            r'\be2e\s+harness\b',
        ]
    
    def matches(self, text: str) -> bool:
        """
        Check if text matches E2E testing pattern.
        
        Args:
            text: Input text to analyze
        
        Returns:
            True if matches E2E testing pattern
        """
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in self._patterns)
    
    def get_intent(self) -> IntentCategory:
        """
        Get intent category for this rule.
        
        Returns:
            IntentCategory.TEST
        """
        return IntentCategory.TEST
    
    def get_signal_strength(self) -> float:
        """
        Get signal strength (confidence multiplier).
        
        Returns:
            0.95 (high confidence for deterministic routing)
        """
        return 0.95
    
    def get_signals(self) -> List[IntentSignal]:
        """
        Get intent signals detected by this rule.
        
        Returns:
            [IntentSignal.IMPERATIVE] - direct action request
        """
        return [IntentSignal.IMPERATIVE]
    
    def get_keywords(self) -> List[str]:
        """
        Get keywords associated with this rule.
        
        Returns:
            List of E2E testing keywords
        """
        return ["golden", "e2e", "end-to-end", "test", "harness"]
