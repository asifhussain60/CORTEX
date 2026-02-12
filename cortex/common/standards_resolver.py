"""
StandardsResolver for CORTEX Company Domain Integration.

Priority-based standards loading: company → cortex → defaults.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification
"""

import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class StandardsSource(Enum):
    """Standards source priority levels."""
    COMPANY = "company"  # Highest priority
    CORTEX = "cortex"    # Fallback
    DEFAULTS = "defaults"  # Last resort


@dataclass
class StandardsResult:
    """
    Result from standards resolution.

    Attributes:
        content: Standards content (parsed YAML)
        source: Which source provided the standards
        gaps: List of missing standards (gap detection)
    """
    content: Dict[str, Any]
    source: StandardsSource
    gaps: List[str]


class StandardsResolver:
    """
    Priority-based standards resolver for company domain integration.

    Loading order:
    1. company/domains/{domain}/{subdomain}/
    2. cortex/knowledge/best-practices/{domain}/
    3. cortex/defaults/{domain}/

    Features:
    - LRU caching for performance
    - Gap detection and logging
    - Phase 28 profile integration

    Example:
        >>> resolver = StandardsResolver()
        >>> result = resolver.load_standards("security", "authentication")
        >>> print(f"Source: {result.source}, Gaps: {result.gaps}")
    """

    def __init__(
        self,
        company_root: str = "company/domains",
        cortex_root: str = "cortex/knowledge/best-practices",
        defaults_root: str = "cortex/defaults",
        cache_size: int = 100,
        cache_ttl: int = 3600,
    ):
        """
        Initialize standards resolver.

        Args:
            company_root: Root path for company standards
            cortex_root: Root path for CORTEX standards
            defaults_root: Root path for default standards
            cache_size: LRU cache size
            cache_ttl: Cache TTL in seconds
        """
        self.company_root = Path(company_root)
        self.cortex_root = Path(cortex_root)
        self.defaults_root = Path(defaults_root)
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl

        # Cache for standards (path -> (content, timestamp))
        self._cache: Dict[str, tuple[Dict, float]] = {}

        # Repository profile (from Phase 28)
        self._profile = None

    def load_profile(self, profile: Any):
        """
        Load repository profile from Phase 28.

        Args:
            profile: Repository profile with structure metadata
        """
        self._profile = profile

        # Update company root if profile specifies custom path
        if (hasattr(profile, 'structure') and
            hasattr(profile.structure, 'has_company_domains') and
            profile.structure.has_company_domains):
            self.company_root = Path(profile.structure.company_domains_path)

    def load_standards(
        self,
        domain: str,
        subdomain: str,
    ) -> StandardsResult:
        """
        Load standards with priority-based resolution.

        Priority order:
        1. company/domains/{domain}/{subdomain}.yaml
        2. cortex/knowledge/best-practices/{domain}/{subdomain}.yaml
        3. cortex/defaults/{domain}/{subdomain}.yaml

        Args:
            domain: Domain (e.g., "security", "testing")
            subdomain: Subdomain (e.g., "authentication", "patterns")

        Returns:
            StandardsResult with content, source, and gaps
        """
        gaps = []

        # Try company standards first
        company_path = self.company_root / domain / f"{subdomain}.yaml"
        content = self._load_from_path(company_path)
        if content is not None:
            return StandardsResult(
                content=content,
                source=StandardsSource.COMPANY,
                gaps=[],
            )

        # Log gap
        gaps.append(f"company/domains/{domain}/{subdomain}.yaml")

        # Try cortex standards
        cortex_path = self.cortex_root / domain / f"{subdomain}.yaml"
        content = self._load_from_path(cortex_path)
        if content is not None:
            return StandardsResult(
                content=content,
                source=StandardsSource.CORTEX,
                gaps=gaps,
            )

        # Log gap
        gaps.append(f"cortex/knowledge/{domain}/{subdomain}.yaml")

        # Try defaults
        defaults_path = self.defaults_root / domain / f"{subdomain}.yaml"
        content = self._load_from_path(defaults_path)
        if content is not None:
            return StandardsResult(
                content=content,
                source=StandardsSource.DEFAULTS,
                gaps=gaps,
            )

        # No standards found anywhere
        return StandardsResult(
            content={},
            source=StandardsSource.DEFAULTS,
            gaps=gaps + [f"defaults/{domain}/{subdomain}.yaml"],
        )

    def _load_from_path(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load YAML from path with caching.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML content or None if not found
        """
        # Check cache
        path_str = str(path)
        if path_str in self._cache:
            content, timestamp = self._cache[path_str]

            # Check TTL
            if time.time() - timestamp < self.cache_ttl:
                return content

            # Expired, remove from cache
            del self._cache[path_str]

        # Try to load file
        if not path.exists():
            return None

        try:
            with open(path, 'r') as f:
                content = yaml.safe_load(f)

            # Add to cache
            self._add_to_cache(path_str, content)

            return content

        except Exception:
            return None

    def _add_to_cache(self, path: str, content: Dict[str, Any]):
        """
        Add to cache with LRU eviction.

        Args:
            path: File path (cache key)
            content: Parsed YAML content
        """
        # Evict oldest if cache full
        if len(self._cache) >= self.cache_size:
            # Remove oldest entry (simplistic LRU)
            oldest_path = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_path]

        # Add to cache
        self._cache[path] = (content, time.time())

    def clear_cache(self):
        """Clear all cached standards."""
        self._cache.clear()
