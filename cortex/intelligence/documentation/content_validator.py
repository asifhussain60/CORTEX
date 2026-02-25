"""
content_validator.py — Documentation Content Validator Stub

Restored for import compatibility. Validates extracted documentation
content against quality standards.
"""
from __future__ import annotations

from typing import Any


class ContentValidator:
    """Validates documentation content quality."""

    def validate(self, content: dict[str, Any]) -> dict[str, Any]:
        """Validate a content dict returned by ContentExtractor.

        Args:
            content: Extracted content dict with 'content' and 'sections'.

        Returns:
            Validation result with 'valid', 'score', and 'issues' keys.
        """
        issues: list[str] = []
        text = content.get("content", "")

        if len(text) < 50:
            issues.append("Content too short (< 50 chars)")
        if not content.get("sections"):
            issues.append("No sections detected")

        score = max(0.0, 1.0 - len(issues) * 0.25)
        return {
            "valid": len(issues) == 0,
            "score": round(score, 2),
            "issues": issues,
        }
