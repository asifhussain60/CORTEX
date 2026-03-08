"""KnowledgeCoverageAssessor — scores domain signal coverage against INDEX.yaml.

Computes a coverage score (0.0–1.0) by matching extracted domain signals against
known domains in cortex-registry/knowledge/INDEX.yaml.  When the score falls below
the configured threshold (default 0.80), sets ``acquisition_needed = True``.

Phase: 135-a (GAP-135-02)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import yaml

logger = logging.getLogger(__name__)

# ── Canonical INDEX path ──────────────────────────────────────────────────────
_INDEX_PATH: Path = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "INDEX.yaml"
)

_DEFAULT_THRESHOLD: float = 0.80

# Module-level cache — populated once per process
_INDEX_DOMAINS_CACHE: Optional[set[str]] = None


@dataclass
class CoverageResult:
    """Result of a knowledge coverage assessment.

    Attributes:
        score: Coverage fraction in [0.0, 1.0].
        covered_domains: Domain strings that were matched in INDEX.yaml.
        missing_domains: Domain strings with no INDEX.yaml match.
        acquisition_needed: True when ``score < threshold``.
        threshold: The threshold used for this assessment.
    """

    score: float
    covered_domains: List[str] = field(default_factory=list)
    missing_domains: List[str] = field(default_factory=list)
    acquisition_needed: bool = False
    threshold: float = _DEFAULT_THRESHOLD


class KnowledgeCoverageAssessor:
    """Scores domain signal coverage against cortex-registry/knowledge/INDEX.yaml.

    Implements a three-level matching strategy:
    1. **Exact** — signal matches an INDEX domain key exactly.
    2. **Prefix** — signal is a prefix of an INDEX domain key.
    3. **Keyword containment** — signal is contained within any INDEX domain key
       or any keyword listed in the INDEX entries.

    Args:
        threshold: Acquisition trigger threshold (default 0.80).
        index_path: Override path to INDEX.yaml (used in tests).

    Usage::

        assessor = KnowledgeCoverageAssessor()
        result = assessor.assess(["testing-validation", "unknown-xyz"])
        if result.acquisition_needed:
            # trigger KnowledgeAcquisitionOrchestrator
            ...
    """

    def __init__(
        self,
        threshold: float = _DEFAULT_THRESHOLD,
        index_path: Optional[Path] = None,
    ) -> None:
        """Initialise the assessor with optional threshold and index path overrides."""
        self.threshold = threshold
        self._index_path = index_path or _INDEX_PATH

    def assess(self, signals: List[str]) -> CoverageResult:
        """Score coverage of *signals* against known INDEX.yaml domains.

        Args:
            signals: Domain signal strings from ``DomainSignalExtractor.extract()``.

        Returns:
            :class:`CoverageResult` with score, covered/missing lists, and acquisition flag.
        """
        if not signals:
            return CoverageResult(
                score=1.0,
                covered_domains=[],
                missing_domains=[],
                acquisition_needed=False,
                threshold=self.threshold,
            )

        known = self._load_index_domains()
        covered: List[str] = []
        missing: List[str] = []

        for signal in signals:
            if self._matches(signal, known):
                covered.append(signal)
            else:
                missing.append(signal)

        score = len(covered) / len(signals)
        acquisition_needed = score < self.threshold

        return CoverageResult(
            score=score,
            covered_domains=covered,
            missing_domains=missing,
            acquisition_needed=acquisition_needed,
            threshold=self.threshold,
        )

    def _matches(self, signal: str, known_domains: set[str]) -> bool:
        """Apply three-level matching: exact → prefix → keyword containment.

        Args:
            signal: Domain signal string to match.
            known_domains: Set of known domain keys from INDEX.yaml.

        Returns:
            True if the signal matches any known domain by any strategy.
        """
        signal_lower = signal.lower()

        # Level 1: exact match
        if signal_lower in known_domains:
            return True

        # Level 2: prefix match (signal is a prefix of a known domain)
        for domain in known_domains:
            if domain.startswith(signal_lower) or signal_lower.startswith(domain):
                return True

        # Level 3: keyword containment (signal appears within any domain key)
        for domain in known_domains:
            if signal_lower in domain or domain in signal_lower:
                return True

        return False

    def _load_index_domains(self) -> set[str]:
        """Load and cache top-level domain keys from INDEX.yaml.

        Returns:
            Set of domain name strings (e.g. ``{"testing-validation", "security", ...}``).
        """
        global _INDEX_DOMAINS_CACHE

        # If a custom index_path was provided, bypass the module-level cache
        if self._index_path != _INDEX_PATH:
            return self._parse_domains(self._index_path)

        if _INDEX_DOMAINS_CACHE is not None:
            return _INDEX_DOMAINS_CACHE

        _INDEX_DOMAINS_CACHE = self._parse_domains(self._index_path)
        return _INDEX_DOMAINS_CACHE

    def _parse_domains(self, index_path: Path) -> set[str]:
        """Parse domain keys from a given INDEX.yaml path.

        Args:
            index_path: Path to the INDEX.yaml file.

        Returns:
            Set of top-level domain key strings, lowercased.
        """
        try:
            raw: Any = yaml.safe_load(index_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return set()
            # Top-level keys that are dict (have 'guides' or similar sub-structure)
            domains = set()
            for key, value in raw.items():
                if isinstance(value, dict):
                    domains.add(key.lower())
            return domains
        except Exception as exc:
            logger.warning("KnowledgeCoverageAssessor: failed to load INDEX.yaml — %s", exc)
            return set()


def invalidate_index_cache() -> None:
    """Clear the module-level INDEX.yaml domain cache.

    Called by ``IntelligenceFacade.invalidate_cache()`` after new knowledge files
    are registered so newly added domains become immediately visible.
    """
    global _INDEX_DOMAINS_CACHE
    _INDEX_DOMAINS_CACHE = None
