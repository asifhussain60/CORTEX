"""
content_extractor.py — Documentation Content Extractor Stub

Restored for import compatibility. Extracts structured content
from documentation artefacts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class ContentExtractor:
    """Extracts structured content from documentation files."""

    def extract(self, path: str | Path) -> dict[str, Any]:
        """Extract content from a single documentation file.

        Args:
            path: Path to the documentation file.

        Returns:
            Dict with 'path', 'content', and 'sections' keys.
        """
        p = Path(path)
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        return {
            "path": str(p),
            "content": text,
            "sections": self._split_sections(text),
        }

    def _split_sections(self, text: str) -> list[str]:
        """Split text into heading sections.

        Args:
            text: Raw document text.

        Returns:
            List of section strings.
        """
        return [s.strip() for s in text.split("\n#") if s.strip()]
