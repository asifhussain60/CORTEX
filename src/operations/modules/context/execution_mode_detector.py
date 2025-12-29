"""Execution Mode Detector

Detects whether user request is for autonomous, interactive, or continuation execution.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import re
from typing import Literal

ExecutionMode = Literal["autonomous", "interactive", "continuation"]


class ExecutionModeDetector:
    """Detects if user request is for autonomous execution."""

    # Keywords that signal autonomous execution
    AUTONOMOUS_KEYWORDS = [
        "autonomously",
        "execute all",
        "run all phases",
        "complete all",
        "continue automatically",
        "proceed without stopping",
        "no confirmation",
        "automatic execution",
        "run autonomously",
        "autonomous mode",
        "execute all phases",
        "complete all phases",
        "proceed automatically",
    ]

    # Patterns that signal continuation of existing work
    CONTINUATION_PATTERNS = [
        r"continue with phase \d+",
        r"proceed to next phase",
        r"continue to phase \d+",
        r"keep going",
        r"continue execution",
        r"resume execution",
        r"next phase",
        r"proceed",
        r"continue",
    ]

    def detect(self, user_message: str) -> ExecutionMode:
        """
        Detects execution mode from user message.

        Args:
            user_message: The user's request text

        Returns:
            ExecutionMode: 'autonomous', 'interactive', or 'continuation'
        """
        if not user_message:
            return "interactive"

        message_lower = user_message.lower().strip()

        # Check for autonomous keywords
        if self._is_autonomous(message_lower):
            return "autonomous"

        # Check for continuation patterns
        if self._is_continuation(message_lower):
            return "continuation"

        # Default to interactive
        return "interactive"

    def _is_autonomous(self, message: str) -> bool:
        """Check if message contains autonomous execution keywords."""
        return any(keyword in message for keyword in self.AUTONOMOUS_KEYWORDS)

    def _is_continuation(self, message: str) -> bool:
        """Check if message matches continuation patterns."""
        return any(
            re.search(pattern, message, re.IGNORECASE)
            for pattern in self.CONTINUATION_PATTERNS
        )

    def is_autonomous_mode(self, user_message: str) -> bool:
        """
        Convenience method to check if mode is autonomous.

        Args:
            user_message: The user's request text

        Returns:
            bool: True if autonomous mode detected
        """
        return self.detect(user_message) == "autonomous"

    def is_continuation_mode(self, user_message: str) -> bool:
        """
        Convenience method to check if mode is continuation.

        Args:
            user_message: The user's request text

        Returns:
            bool: True if continuation mode detected
        """
        return self.detect(user_message) == "continuation"

    def should_auto_progress(self, user_message: str) -> bool:
        """
        Determines if execution should auto-progress without user confirmation.

        Args:
            user_message: The user's request text

        Returns:
            bool: True if autonomous or continuation mode detected
        """
        mode = self.detect(user_message)
        return mode in ("autonomous", "continuation")
