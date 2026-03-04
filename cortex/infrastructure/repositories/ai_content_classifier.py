"""
AIContentClassifier — extract structured data from AI instruction markdown.

Phase 121 Sub-phase B | GAP-121-02.
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
           CORE-028 (snake_case), CORE-035 (single canonical implementation).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
from pathlib import Path
import re
from typing import List

logger = logging.getLogger(__name__)

# ── Signal keywords (minimal — sufficiency-driven, not exhaustive) ──────────

_CODING_SIGNALS = frozenset({
    "naming convention", "snake_case", "camelcase", "error handling",
    "logging", "type hints", "type hint", "docstring", "import order",
    "file structure", "code style", "line length", "indentation",
    "prefer", "always use", "never use", "must include", "always include",
})

_SECURITY_SIGNALS = frozenset({
    "authentication", "authorization", "secret", "password",
    "token", "encryption", "owasp", "sanitize", "validate input",
    "sql injection", "xss", "bcrypt", "jwt",
})

_ARCHITECTURE_SIGNALS = frozenset({
    "pattern", "architecture", "microservice", "monolith",
    "layer", "module", "dependency injection", "solid", "clean architecture",
    "domain-driven", "bounded context", "value object",
})

_TESTING_SIGNALS = frozenset({
    "test", "tdd", "coverage", "mock", "fixture",
    "assertion", "integration test", "unit test", "failing test",
})


@dataclass
class ClassifiedContent:
    """Structured content extracted from AI instruction files."""

    coding_conventions: List[str] = field(default_factory=list)
    security_rules: List[str] = field(default_factory=list)
    architecture_patterns: List[str] = field(default_factory=list)
    testing_standards: List[str] = field(default_factory=list)


class AIContentClassifier:
    """
    Extract and classify structured standards from AI instruction markdown.

    Reads markdown content and categorises bullet points / list items into
    four buckets: coding conventions, security rules, architecture patterns,
    and testing standards.

    Example::

        classifier = AIContentClassifier()
        result = classifier.classify(Path("instructions.md"), markdown_text)
        print(result.coding_conventions)
    """

    def classify(self, file_path: Path, content: str) -> ClassifiedContent:
        """
        Classify *content* into structured categories.

        Args:
            file_path: Source file path (used for extension check).
            content: Raw text content to classify.

        Returns:
            :class:`ClassifiedContent` with populated category lists.
        """
        result = ClassifiedContent()
        if not content or not content.strip():
            return result

        lines = self._extract_items(content)
        for item in lines:
            lower = item.lower()
            if self._matches(lower, _CODING_SIGNALS):
                result.coding_conventions.append(item)
            if self._matches(lower, _SECURITY_SIGNALS):
                result.security_rules.append(item)
            if self._matches(lower, _ARCHITECTURE_SIGNALS):
                result.architecture_patterns.append(item)
            if self._matches(lower, _TESTING_SIGNALS):
                result.testing_standards.append(item)

        return result

    # ── Private helpers ───────────────────────────────────────────────────────

    def _extract_items(self, content: str) -> List[str]:
        """
        Extract meaningful lines (bullets, numbered list items, plain sentences).

        Strips markdown headings and fenced code blocks.

        Args:
            content: Raw markdown content.

        Returns:
            List of stripped, non-empty text items.
        """
        items: List[str] = []
        in_code_block = False

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            # Skip headings
            if re.match(r"^#{1,6}\s", stripped):
                continue
            # Extract bullet items
            bullet = re.match(r"^[-*+]\s+(.*)", stripped)
            if bullet:
                items.append(bullet.group(1).strip())
                continue
            # Numbered list items
            numbered = re.match(r"^\d+\.\s+(.*)", stripped)
            if numbered:
                items.append(numbered.group(1).strip())
                continue
            # Plain non-empty lines (potential inline rules)
            if stripped and len(stripped) > 10:
                items.append(stripped)

        return [i for i in items if i]

    def _matches(self, text_lower: str, signals: frozenset) -> bool:
        """Return True if any signal keyword appears in *text_lower*."""
        return any(sig in text_lower for sig in signals)


__all__ = ["AIContentClassifier", "ClassifiedContent"]
