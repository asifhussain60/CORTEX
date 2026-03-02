"""
Duplicate Scanner - Find duplicate/similar content.

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Finds duplicate and near-duplicate content:
    - Exact duplicates (100% match)
    - Near-duplicates (configurable similarity threshold)
    - Consolidation suggestions
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple

from cortex.orchestrators.validation.coherence_models import (
    DuplicateMatch,
    Section,
)

logger = logging.getLogger(__name__)

@dataclass
class ConsolidationSuggestion:
    """Suggestion for consolidating duplicate content.

    Attributes:
        duplicates: List of duplicate matches to consolidate
        recommended_location: Where to keep the canonical version
        action: Recommended action (keep_first, merge, create_new)
        rationale: Explanation for the recommendation
    """

    duplicates: List[DuplicateMatch]
    recommended_location: int  # Line number
    action: str
    rationale: str

@dataclass
class ScanResult:
    """Result of a duplicate scan.

    Attributes:
        exact_duplicates: Sections with 100% match
        near_duplicates: Sections with similarity >= threshold
        all_duplicates: Combined list
        consolidation_suggestions: Suggestions for fixing
    """

    exact_duplicates: List[DuplicateMatch] = field(default_factory=list)
    near_duplicates: List[DuplicateMatch] = field(default_factory=list)
    all_duplicates: List[DuplicateMatch] = field(default_factory=list)
    consolidation_suggestions: List[ConsolidationSuggestion] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        """Check if any duplicates were found."""
        return len(self.all_duplicates) > 0

    @property
    def total_count(self) -> int:
        """Total number of duplicates found."""
        return len(self.all_duplicates)

class DuplicateScanner:
    """Scanner for detecting duplicate and similar content.

    Supports multiple detection strategies:
    - Exact name matching (section headers)
    - Content similarity (using SequenceMatcher)
    - Structural similarity (same patterns)

    Example:
        >>> scanner = DuplicateScanner(similarity_threshold=0.8)
        >>> result = scanner.scan_sections(sections)
        >>> if result.has_duplicates:
        ...     for dup in result.all_duplicates:
        ...         print(f"Duplicate: {dup.original_section.name}")
    """

    DEFAULT_SIMILARITY_THRESHOLD = 0.8

    def __init__(
        self,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
        """Initialize the DuplicateScanner.

        Args:
            similarity_threshold: Minimum similarity (0.0-1.0) for near-duplicate
        """
        self._threshold = similarity_threshold
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def scan_sections(self, sections: List[Section]) -> ScanResult:
        """Scan sections for duplicates.

        Args:
            sections: List of sections to scan

        Returns:
            ScanResult with found duplicates and suggestions
        """
        exact: List[DuplicateMatch] = []
        near: List[DuplicateMatch] = []

        # Group sections by name for exact match
        name_groups = self._group_by_name(sections)

        for name, group in name_groups.items():
            if len(group) > 1:
                # First one is "original", rest are duplicates
                original = group[0]
                for dup in group[1:]:
                    exact.append(DuplicateMatch(
                        original_section=original,
                        duplicate_section=dup,
                        similarity=1.0,
                        is_exact=True,
                    ))

        # Check for near-duplicates (similar names)
        near = self._find_near_duplicates(sections)

        # Filter near-duplicates that aren't already in exact
        exact_pairs = {
            (d.original_section.name.lower(), d.duplicate_section.name.lower())
            for d in exact
        }
        near = [
            d for d in near
            if (d.original_section.name.lower(), d.duplicate_section.name.lower())
            not in exact_pairs
        ]

        all_dups = exact + near

        # Generate consolidation suggestions
        suggestions = self._generate_suggestions(all_dups)

        return ScanResult(
            exact_duplicates=exact,
            near_duplicates=near,
            all_duplicates=all_dups,
            consolidation_suggestions=suggestions,
        )

    def scan_for_pattern(
        self,
        content: str,
        pattern: str,
    ) -> List[Tuple[int, str]]:
        """Scan content for occurrences of a pattern.

        Args:
            content: Content to search
            pattern: Regex pattern to find

        Returns:
            List of (line_number, matched_text) tuples
        """
        matches: List[Tuple[int, str]] = []

        for i, line in enumerate(content.splitlines(), start=1):
            if re.search(pattern, line, re.IGNORECASE):
                matches.append((i, line.strip()))

        return matches

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate similarity between two text strings.

        Uses SequenceMatcher for similarity scoring.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Similarity score from 0.0 to 1.0
        """
        if not text_a or not text_b:
            return 0.0

        # Normalize whitespace
        a_normalized = " ".join(text_a.lower().split())
        b_normalized = " ".join(text_b.lower().split())

        return SequenceMatcher(None, a_normalized, b_normalized).ratio()

    def suggest_consolidation(
        self,
        duplicates: List[DuplicateMatch],
    ) -> List[ConsolidationSuggestion]:
        """Generate consolidation suggestions for duplicates.

        Args:
            duplicates: List of duplicate matches

        Returns:
            List of ConsolidationSuggestion objects
        """
        return self._generate_suggestions(duplicates)

    def find_content_duplicates(
        self,
        sections: List[Section],
    ) -> List[DuplicateMatch]:
        """Find duplicates based on content similarity.

        Args:
            sections: List of sections with content

        Returns:
            List of DuplicateMatch objects
        """
        duplicates: List[DuplicateMatch] = []
        checked: Set[Tuple[int, int]] = set()

        for i, section_a in enumerate(sections):
            for j, section_b in enumerate(sections):
                if i >= j:
                    continue
                if (i, j) in checked:
                    continue

                checked.add((i, j))

                # Skip if no content
                if not section_a.content or not section_b.content:
                    continue

                similarity = self.calculate_similarity(
                    section_a.content,
                    section_b.content,
                )

                if similarity >= self._threshold:
                    duplicates.append(DuplicateMatch(
                        original_section=section_a,
                        duplicate_section=section_b,
                        similarity=similarity,
                        is_exact=similarity >= 0.99,
                    ))

        return duplicates

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _group_by_name(self, sections: List[Section]) -> Dict[str, List[Section]]:
        """Group sections by normalized name.

        Args:
            sections: List of sections

        Returns:
            Dict mapping normalized name to list of sections
        """
        groups: Dict[str, List[Section]] = {}

        for section in sections:
            name = section.name.lower().strip()
            if name not in groups:
                groups[name] = []
            groups[name].append(section)

        return groups

    def _find_near_duplicates(self, sections: List[Section]) -> List[DuplicateMatch]:
        """Find sections with similar names.

        Args:
            sections: List of sections

        Returns:
            List of near-duplicate matches
        """
        duplicates: List[DuplicateMatch] = []
        checked: Set[Tuple[int, int]] = set()

        for i, section_a in enumerate(sections):
            for j, section_b in enumerate(sections):
                if i >= j:
                    continue
                if (i, j) in checked:
                    continue

                checked.add((i, j))

                # Check name similarity
                similarity = self.calculate_similarity(
                    section_a.name,
                    section_b.name,
                )

                # Skip exact matches (handled separately)
                if similarity >= 0.99:
                    continue

                if similarity >= self._threshold:
                    duplicates.append(DuplicateMatch(
                        original_section=section_a,
                        duplicate_section=section_b,
                        similarity=similarity,
                        is_exact=False,
                    ))

        return duplicates

    def _generate_suggestions(
        self,
        duplicates: List[DuplicateMatch],
    ) -> List[ConsolidationSuggestion]:
        """Generate consolidation suggestions for duplicates.

        Args:
            duplicates: List of duplicate matches

        Returns:
            List of ConsolidationSuggestion objects
        """
        if not duplicates:
            return []

        suggestions: List[ConsolidationSuggestion] = []

        # Group duplicates by original section
        groups: Dict[str, List[DuplicateMatch]] = {}
        for dup in duplicates:
            name = dup.original_section.name.lower()
            if name not in groups:
                groups[name] = []
            groups[name].append(dup)

        for name, group in groups.items():
            # Find earliest occurrence
            all_sections = [group[0].original_section] + [
                d.duplicate_section for d in group
            ]
            earliest = min(all_sections, key=lambda s: s.start_line)

            # Determine action
            if all(d.is_exact for d in group):
                action = "keep_first"
                rationale = "All duplicates are exact copies - keep the first occurrence"
            else:
                action = "merge"
                rationale = "Near-duplicates detected - merge content into single section"

            suggestions.append(ConsolidationSuggestion(
                duplicates=group,
                recommended_location=earliest.start_line,
                action=action,
                rationale=rationale,
            ))

        return suggestions

# AC_COMPLETE: AC-ENH-101-006 ✅ DuplicateScanner implementation
