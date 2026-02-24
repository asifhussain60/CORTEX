"""Domain Adapter Protocol — Pluggable extensions for toolkit components.

Enables domain-specific customization of generic toolkit behaviors without
modifying core components. Adapters provide rules, patterns, and enrichment
sources for specific use cases (media, code, documents).

Authority: phase-toolkit-consolidation.yaml Sub-phase S5
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs

AC_START: AC-TOOLKIT-DOMAIN-ADAPTER-001
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Pattern


@dataclass
class MorphRule:
    """Text transformation rule (e.g., obscenity → euphemism).
    
    Attributes:
        pattern:      Regex pattern to match.
        replacement:  Replacement text.
        priority:     Rule priority (higher = applied first).
    """
    
    pattern: Pattern[str]
    replacement: str
    priority: int = 0


@dataclass
class EnrichmentSource:
    """External enrichment API configuration.
    
    Attributes:
        name:          Source name (e.g., "IAFD", "TMDB", "GitHub").
        base_url:      API base URL.
        rate_limit:    Max requests per second.
        cache_ttl_sec: Cache time-to-live in seconds.
    """
    
    name: str
    base_url: str
    rate_limit: float = 1.0
    cache_ttl_sec: int = 3600


class DomainAdapter(Protocol):
    """Protocol for domain-specific toolkit customization.
    
    Implementations provide rules and configurations for:
      - Organization detection from folder structures
      - Content sanitization (text morphing rules)
      - External enrichment sources
    
    Examples:
        >>> from cortex.toolkit.adapters import MediaAdapter
        >>> adapter = MediaAdapter()
        >>> rules = adapter.get_organization_rules()
        >>> morph_rules = adapter.get_morph_rules()
    """
    
    @abstractmethod
    def get_organization_rules(self) -> Dict[str, Pattern[str]]:
        """Return regex patterns for organization detection.
        
        Maps organization type → regex pattern for folder/file matching.
        
        Returns:
            Dict of organization_type → compiled regex pattern.
        
        Examples:
            >>> adapter.get_organization_rules()
            {
                "studio": re.compile(r"(?i)(SexArt|Bellesa|Wicked)"),
                "artist": re.compile(r"feat\\.\\s+([A-Z][a-z]+\\s+[A-Z][a-z]+)")
            }
        """
        ...
    
    @abstractmethod
    def get_morph_rules(self) -> List[MorphRule]:
        """Return content transformation rules.
        
        Returns:
            List of MorphRule instances (ordered by priority).
        
        Examples:
            >>> adapter.get_morph_rules()
            [
                MorphRule(pattern=re.compile(r"\\bfoo\\b"), replacement="bar", priority=100),
                ...
            ]
        """
        ...
    
    @abstractmethod
    def get_enrichment_sources(self) -> List[EnrichmentSource]:
        """Return external API sources for metadata enrichment.
        
        Returns:
            List of EnrichmentSource configurations.
        
        Examples:
            >>> adapter.get_enrichment_sources()
            [
                EnrichmentSource(name="IAFD", base_url="https://www.iafd.com/api"),
                EnrichmentSource(name="TMDB", base_url="https://api.themoviedb.org/3"),
            ]
        """
        ...
    
    def detect_organization(self, path: Path, folder_name: str) -> Optional[str]:
        """Detect organization from file path using domain rules.
        
        Optional method with default passthrough implementation.
        
        Args:
            path:        File path.
            folder_name: Parent folder name.
        
        Returns:
            Organization name or None if not detected.
        """
        return folder_name if folder_name else None


# AC_COMPLETE: AC-TOOLKIT-DOMAIN-ADAPTER-001 ✅ Protocol defined
