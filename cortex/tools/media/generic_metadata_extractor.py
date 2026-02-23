"""
cortex/tools/media/generic_metadata_extractor.py

Generic metadata extractor for video filenames — no sanitization.
Extracts performer names, titles, studio hints from raw filenames using patterns.

Works with any studio/naming convention:
- "Michael Vegas action Brooklyn Lee" → performers: ["Michael Vegas", "Brooklyn Lee"], action_type: "action"
- "Julia Ann Does Nicole Sheridan - Voodoo" → performers: ["Julia Ann", "Nicole Sheridan"], title: "Voodoo"
- "Wicked_123_Performers.mp4" → raw stem: "Wicked_123_Performers"

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from typing import List, Optional, Pattern

logger = logging.getLogger(__name__)


@dataclass
class ExtractedMetadata:
    """Metadata extracted from a filename."""

    filename: str
    performers: List[str]  # Names extracted as performers
    title: Optional[str] = None  # Scene title if identifiable
    action_type: Optional[str] = None  # "action", "Does", "with", etc.
    studio: Optional[str] = None  # Studio hint if detectable
    confidence: float = 0.0  # Extraction confidence (0.0-1.0)


class GenericMetadataExtractor:
    """Extract metadata from video filenames using pattern matching."""

    def __init__(self) -> None:
        """Initialize extractor with common performer/title patterns."""
        # Action/connector patterns: "Name1 {pattern} Name2"
        # Order matters: try most specific (multi-word performers) first
        self.action_patterns: List[Pattern] = [
            # "Name1 action Name2" with word boundary, non-greedy capture for performers
            re.compile(
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(action|does|with|meets|vs)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                re.IGNORECASE,
            ),
            # "Name1 & Name2" pattern
            re.compile(
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+&\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                re.IGNORECASE,
            ),
        ]

        # Title patterns: "Title:" or "- Title" or in parentheses
        self.title_patterns: List[Pattern] = [
            re.compile(r":\s*([A-Z][^-]*?)(?:\s*-|$)", re.IGNORECASE),
            re.compile(r"-\s*([A-Z][a-z\s0-9]+?)(?:\s*$|\.mp4)", re.IGNORECASE),
            re.compile(r"\(([A-Z][^)]*?)\)", re.IGNORECASE),
        ]

    def extract(self, filename: str) -> ExtractedMetadata:
        """
        Extract metadata from filename.

        Args:
            filename: Raw filename (e.g., "Michael Vegas action Brooklyn Lee.mp4")

        Returns:
            ExtractedMetadata with extracted fields and confidence score.
        """
        # Remove extension
        stem = filename.rsplit(".", 1)[0] if "." in filename else filename

        performers: List[str] = []
        action_type: Optional[str] = None
        title: Optional[str] = None
        confidence: float = 0.0

        # Try action patterns
        for pattern in self.action_patterns:
            match = pattern.search(stem)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    # Extract performers and action type
                    perf1 = groups[0].strip()
                    if len(groups) == 3:
                        action_type = groups[1].lower()
                        perf2 = groups[2].strip()
                    else:
                        perf2 = groups[1].strip()

                    performers = [self._clean_name(perf1), self._clean_name(perf2)]
                    confidence = 0.85
                    break

        # If no action pattern matched, try to extract single title
        if not performers:
            # Try title patterns
            for pattern in self.title_patterns:
                match = pattern.search(stem)
                if match:
                    title = match.group(1).strip()
                    confidence = 0.5
                    break

            # Fallback: use entire stem as potential title
            if not title and stem:
                title = stem
                confidence = 0.3

        return ExtractedMetadata(
            filename=filename,
            performers=performers,
            title=title,
            action_type=action_type,
            confidence=confidence,
        )

    @staticmethod
    def _clean_name(name: str) -> str:
        """Clean a performer name — strip whitespace, fix capitalization."""
        name = name.strip()
        # Remove trailing numbers/symbols
        name = re.sub(r"\s*[\d_-]*$", "", name)
        # Title case
        return name.title()


class FilenameNormalizer:
    """
    Normalize filenames for consistency while preserving meaning.

    Transformations:
    - Replace "action" → "Does"
    - Apply proper case (Title Case for performer names)
    - Remove numeric prefixes/suffixes
    - Standardize spacing
    """

    def __init__(self) -> None:
        """Initialize normalizer patterns."""
        self.action_replacement_pattern = re.compile(
            r"\s+action\s+", re.IGNORECASE
        )
        self.leading_numbers = re.compile(r"^\d+[\s_-]*")
        self.trailing_numbers = re.compile(r"[\s_-]*\d+$")

    def normalize(
        self,
        filename: str,
        replace_action: bool = True,
        proper_case: bool = True,
        remove_numbers: bool = True,
    ) -> str:
        """
        Normalize a filename.

        Args:
            filename: Original filename (with or without extension)
            replace_action: Replace "action" with "Does"
            proper_case: Apply Title Case
            remove_numbers: Remove numeric prefixes/suffixes

        Returns:
            Normalized filename.
        """
        # Split extension
        parts = filename.rsplit(".", 1)
        stem = parts[0]
        ext = f".{parts[1]}" if len(parts) > 1 else ""

        if replace_action:
            stem = self.action_replacement_pattern.sub(" Does ", stem)

        if remove_numbers:
            stem = self.leading_numbers.sub("", stem)
            stem = self.trailing_numbers.sub("", stem)

        if proper_case:
            # Smart title case: capitalize performer names, lowercase connectors
            words = stem.split()
            cased_words = []
            for i, word in enumerate(words):
                if word.lower() in ["does", "and", "with", "vs", "meets"]:
                    cased_words.append(word.lower())
                else:
                    cased_words.append(word.title())
            stem = " ".join(cased_words)

        # Standardize spacing
        stem = re.sub(r"\s+", " ", stem).strip()

        return stem + ext

    def normalize_batch(
        self,
        filenames: List[str],
        replace_action: bool = True,
        proper_case: bool = True,
        remove_numbers: bool = True,
    ) -> dict[str, str]:
        """
        Normalize multiple filenames.

        Args:
            filenames: List of filenames
            replace_action: Replace "action" with "Does"
            proper_case: Apply Title Case
            remove_numbers: Remove numeric prefixes/suffixes

        Returns:
            Dict mapping original → normalized filenames.
        """
        return {
            fname: self.normalize(
                fname,
                replace_action=replace_action,
                proper_case=proper_case,
                remove_numbers=remove_numbers,
            )
            for fname in filenames
        }
