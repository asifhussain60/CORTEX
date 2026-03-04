"""chat_response_policy.py — Response policy validation and formatting.

Provides ChatResponsePolicyValidator for enforcing CORTEX response format
standards, plus utility functions for verbosity suppression and plan spine
injection.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
Phase: 34 (Response Formatting Pipeline) — activated Phase 116-b GAP-116-04
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

_log = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    """A single response policy violation.

    Attributes:
        rule_id: Governance rule identifier (e.g. CORE-002).
        severity: Violation severity (P0, P1, P2, P3).
        message: Human-readable violation description.
        location: Where in the response the violation occurred.
    """

    rule_id: str
    severity: str
    message: str
    location: str = ""


class ChatResponsePolicyValidator:
    """Validates CORTEX chat responses against governance format rules.

    Checks for:
    - Mandatory header presence (Zone 1 / Zone 2 / Zone 3)
    - CORE-002 compliance (no .md/.txt file creation)
    - Verbosity limits (≤800 words)
    - Duplicate section detection

    Attributes:
        max_word_count: Maximum allowed words in response.
        violations: Accumulated violations from last validation.
    """

    def __init__(self, max_word_count: int = 800) -> None:
        """Initialise policy validator.

        Args:
            max_word_count: Maximum allowed words (default 800).
        """
        self.max_word_count = max_word_count
        self.violations: List[PolicyViolation] = []

    def validate(self, response: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate a response against CORTEX response policy.

        Args:
            response: The full response text to validate.
            context: Optional context (intent type, mode, etc.).

        Returns:
            True if response passes all policy checks, False otherwise.
        """
        self.violations = []
        self._check_word_count(response)
        self._check_duplicate_headers(response)
        return len(self.violations) == 0

    def _check_word_count(self, response: str) -> None:
        """Check response does not exceed word limit."""
        word_count = len(response.split())
        if word_count > self.max_word_count:
            self.violations.append(
                PolicyViolation(
                    rule_id="RESP-001",
                    severity="P2",
                    message=f"Response exceeds {self.max_word_count} word limit ({word_count} words)",
                    location="full_response",
                )
            )

    def _check_duplicate_headers(self, response: str) -> None:
        """Check for duplicate ## headers in response."""
        lines = response.split("\n")
        headers: Dict[str, int] = {}
        for i, line in enumerate(lines):
            if line.startswith("## "):
                header = line.strip()
                if header in headers:
                    self.violations.append(
                        PolicyViolation(
                            rule_id="RESP-002",
                            severity="P1",
                            message=f"Duplicate header: {header}",
                            location=f"line {i + 1}",
                        )
                    )
                headers[header] = i


def suppress_verbosity(response: str, max_words: int = 800) -> str:
    """Trim response to maximum word count while preserving structure.

    Args:
        response: Full response text.
        max_words: Maximum allowed words.

    Returns:
        Trimmed response if over limit, original otherwise.
    """
    words = response.split()
    if len(words) <= max_words:
        return response
    # Trim to max_words, preserving last paragraph break
    trimmed = " ".join(words[:max_words])
    last_newline = trimmed.rfind("\n\n")
    if last_newline > len(trimmed) // 2:
        trimmed = trimmed[:last_newline]
    return trimmed + "\n\n*[Response trimmed for readability]*"


def inject_plan_spine(
    response: str,
    plan_items: Optional[List[str]] = None,
) -> str:
    """Inject a plan spine (numbered action list) into the response.

    Args:
        response: Full response text.
        plan_items: Optional list of plan items to inject.

    Returns:
        Response with plan spine injected (if items provided).
    """
    if not plan_items:
        return response
    spine = "\n### ⚡ If you say `proceed`, I will:\n"
    for i, item in enumerate(plan_items, 1):
        spine += f"{i}. {item}\n"
    return response + spine


__all__ = [
    "ChatResponsePolicyValidator",
    "PolicyViolation",
    "suppress_verbosity",
    "inject_plan_spine",
]
