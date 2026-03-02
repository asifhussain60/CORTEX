"""Media Adapter — Domain-specific rules for video library organization.

Provides organization detection, sanitization rules, and enrichment sources
specific to media libraries (studios, performers, content ratings).

Authority: phase-toolkit-consolidation.yaml Sub-phase S5
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs

AC_START: AC-TOOLKIT-MEDIA-ADAPTER-001
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Pattern

from cortex.toolkit.adapters.domain_adapter import (
    DomainAdapter,
    EnrichmentSource,
    MorphRule,
)


class MediaAdapter(DomainAdapter):
    """Domain adapter for video library organization.

    Specializes toolkit components for media-specific workflows:
      - Studio detection from folder structure
      - Content sanitization (obscenity morphing)
      - External metadata enrichment (IAFD, TMDB)

    Examples:
        >>> from cortex.toolkit.filesystem import HierarchicalScanner
        >>> from cortex.toolkit.adapters import MediaAdapter
        >>>
        >>> adapter = MediaAdapter()
        >>> scanner = HierarchicalScanner(Path("/media"), adapter=adapter)
        >>> files = scanner.scan()
    """

    # Studio patterns (priority-sorted)
    STUDIO_PATTERNS: Dict[str, Pattern[str]] = {
        "SexArt": re.compile(r"(?i)(?:^|\s)SexArt(?:\s|-|_|$)"),
        "Bellesa": re.compile(r"(?i)Bellesa(?:\s+Plus)?"),
        "Blacked": re.compile(r"(?i)(?:^|\s)Blacked(?:\s|$)"),
        "EroticaX": re.compile(r"(?i)(?:^|\s)EroticaX(?:\s|$)"),
        "Pure Taboo": re.compile(r"(?i)(?:^|\s)Pure\s+Taboo(?:\s|$)"),
        "Wicked": re.compile(r"(?i)(?:^|\s)Wicked(?:\s|$)"),
        "Sweet Sinner": re.compile(r"(?i)(?:^|\s)Sweet\s+Sinner(?:\s|$)"),
    }

    def __init__(self) -> None:
        """Initialize media adapter with default configurations."""
        self._morph_rules: List[MorphRule] = self._build_morph_rules()
        self._enrichment_sources: List[EnrichmentSource] = self._build_enrichment_sources()

    def get_organization_rules(self) -> Dict[str, Pattern[str]]:
        """Return studio detection patterns.

        Returns:
            Dict of studio_name → compiled regex pattern.
        """
        return self.STUDIO_PATTERNS

    def get_morph_rules(self) -> List[MorphRule]:
        """Return content sanitization rules.

        Transforms obscene/explicit language → euphemisms for filename safety.

        Returns:
            List of MorphRule instances (priority-sorted).
        """
        return self._morph_rules

    def get_enrichment_sources(self) -> List[EnrichmentSource]:
        """Return external metadata sources.

        Returns:
            List of EnrichmentSource configurations (IAFD, TMDB).
        """
        return self._enrichment_sources

    def detect_organization(self, path: Path, folder_name: str) -> Optional[str]:
        """Detect studio from file path and folder context.

        Args:
            path:        File path.
            folder_name: Parent folder name.

        Returns:
            Studio name if detected, folder_name otherwise.
        """
        # Try filename first
        filename = path.stem
        for studio, pattern in self.STUDIO_PATTERNS.items():
            if pattern.search(filename):
                return studio

        # Fallback to folder name
        for studio, pattern in self.STUDIO_PATTERNS.items():
            if pattern.search(folder_name):
                return studio

        # Default passthrough
        return folder_name if folder_name else None

    def _build_morph_rules(self) -> List[MorphRule]:
        """Build sanitization morph rules.

        Returns:
            List of MorphRule instances.
        """
        # Example morph rules (extensible via YAML config in production)
        rules = [
            MorphRule(
                pattern=re.compile(r"\b(explicit_term_1)\b", re.IGNORECASE),
                replacement="intimate",
                priority=100
            ),
            MorphRule(
                pattern=re.compile(r"\b(explicit_term_2)\b", re.IGNORECASE),
                replacement="adult",
                priority=90
            ),
            # Add more rules as needed
        ]
        return sorted(rules, key=lambda r: r.priority, reverse=True)

    def _build_enrichment_sources(self) -> List[EnrichmentSource]:
        """Build external enrichment source configurations.

        Returns:
            List of EnrichmentSource instances.
        """
        return [
            EnrichmentSource(
                name="IAFD",
                base_url="https://www.iafd.com",
                rate_limit=1.0,  # 1 req/sec
                cache_ttl_sec=86400  # 24 hours
            ),
            EnrichmentSource(
                name="TMDB",
                base_url="https://api.themoviedb.org/3",
                rate_limit=4.0,  # 4 req/sec
                cache_ttl_sec=3600  # 1 hour
            ),
        ]


# AC_COMPLETE: AC-TOOLKIT-MEDIA-ADAPTER-001 ✅ Concrete adapter implemented
