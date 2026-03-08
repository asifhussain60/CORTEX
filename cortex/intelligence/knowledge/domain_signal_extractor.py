"""DomainSignalExtractor — converts LENS output to domain signal strings.

Reads regex patterns from cortex-registry/config/domain-signal-map.yaml and
applies them to a flattened string representation of LENS analysis output,
returning a sorted, deduplicated list of matched domain signal strings.

Phase: 135-a (GAP-135-01)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# ── Canonical signal map path ─────────────────────────────────────────────────
_SIGNAL_MAP_PATH: Path = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "config"
    / "domain-signal-map.yaml"
)

# Module-level cache — populated once per process (invalidated via invalidate_cache())
_SIGNAL_MAP_CACHE: Optional[List[Dict[str, Any]]] = None


class DomainSignalExtractor:
    """Converts LENS output to domain signal strings via regex patterns.

    Reads ``cortex-registry/config/domain-signal-map.yaml`` once and caches
    the pattern list for the lifetime of the process.  Applies each pattern
    against a flattened text representation of the LENS output dict, collecting
    matched domain names and deduplicating them.

    Usage::

        extractor = DomainSignalExtractor()
        signals = extractor.extract(lens_output)
        # ["backend-python", "security", "testing-validation"]
    """

    def extract(self, lens_output: Dict[str, Any]) -> List[str]:
        """Extract sorted, deduplicated domain signal strings from a LENS output dict.

        Args:
            lens_output: Dict produced by LENS analysis (language, imports, files, etc.)

        Returns:
            Sorted, deduplicated list of matched domain signal strings.
        """
        if not lens_output:
            return []

        flat_text = self._flatten(lens_output)
        patterns = self._load_signal_map()

        matched: set[str] = set()
        for entry in patterns:
            pattern_str = entry.get("pattern", "")
            domain = entry.get("domain", "")
            if not pattern_str or not domain:
                continue
            try:
                if re.search(pattern_str, flat_text, re.IGNORECASE):
                    matched.add(domain)
            except re.error as exc:
                logger.debug("DomainSignalExtractor: invalid pattern %r — %s", pattern_str, exc)

        return sorted(matched)

    def _flatten(self, obj: Any) -> str:
        """Recursively flatten a nested dict/list into a single searchable string.

        Args:
            obj: Arbitrary nested object.

        Returns:
            Single space-separated string of all scalar values.
        """
        if isinstance(obj, dict):
            parts = []
            for v in obj.values():
                parts.append(self._flatten(v))
            return " ".join(parts)
        elif isinstance(obj, (list, tuple)):
            return " ".join(self._flatten(item) for item in obj)
        else:
            return str(obj)

    def _load_signal_map(self) -> List[Dict[str, Any]]:
        """Load and cache the domain-signal-map.yaml patterns.

        Returns the same list object on every call after the first (module-level
        cache ensures YAML is parsed only once per process).

        Returns:
            List of pattern dicts with ``pattern``, ``domain``, and optionally
            ``knowledge_file`` keys.
        """
        global _SIGNAL_MAP_CACHE
        if _SIGNAL_MAP_CACHE is not None:
            return _SIGNAL_MAP_CACHE

        try:
            raw = yaml.safe_load(_SIGNAL_MAP_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                patterns = raw.get("patterns", [])
            elif isinstance(raw, list):
                patterns = raw
            else:
                patterns = []
            _SIGNAL_MAP_CACHE = [p for p in patterns if isinstance(p, dict)]
        except Exception as exc:
            logger.warning("DomainSignalExtractor: failed to load signal map — %s", exc)
            _SIGNAL_MAP_CACHE = []

        return _SIGNAL_MAP_CACHE


def invalidate_signal_map_cache() -> None:
    """Clear the module-level signal map cache.

    Called by ``IntelligenceFacade.invalidate_cache()`` after knowledge acquisition
    so newly registered domains are immediately visible to the extractor.
    """
    global _SIGNAL_MAP_CACHE
    _SIGNAL_MAP_CACHE = None
