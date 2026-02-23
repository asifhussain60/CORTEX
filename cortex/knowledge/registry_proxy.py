"""
cortex.knowledge.registry_proxy — KnowledgeRegistryProxy
=========================================================

Loads domain knowledge from YAML files in ``cortex-registry/knowledge/``
and exposes them as a queryable Python interface.

Phase 59-d: Converts cortex/knowledge/ from a ghost directory into
an active module that bridges the registry YAML knowledge base.

CORE Rules: CORE-035, CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-KNOWLEDGE-PROXY-5904
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Registry root — resolve relative to this file: cortex/knowledge/ → cortex-registry/knowledge/
_REGISTRY_ROOT = Path(__file__).parent.parent.parent / "cortex-registry" / "knowledge"

__all__ = ["KnowledgeRegistryProxy"]


class KnowledgeRegistryProxy:
    """Proxy that loads and queries YAML knowledge from ``cortex-registry/knowledge/``.

    This class provides a lazy-loading interface over the knowledge YAML files
    so that orchestrators can retrieve domain best-practices, patterns, and
    standards without directly coupling to the file system.

    Usage::

        proxy = KnowledgeRegistryProxy()
        entries = proxy.query(domain="backend-python")
        all_entries = proxy.all()

    Attributes:
        registry_root: Path to ``cortex-registry/knowledge/``.
    """

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """Initialise the proxy.

        Args:
            registry_root: Override path to the knowledge registry directory.
                           Defaults to ``cortex-registry/knowledge/`` relative
                           to the CORTEX project root.
        """
        self.registry_root: Path = registry_root or _REGISTRY_ROOT
        self._cache: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> Dict[str, Any]:
        """Load all YAML knowledge files from the registry.

        Returns:
            Dictionary keyed by ``domain/filename`` with parsed YAML content.
        """
        if self._cache is not None:
            return self._cache

        try:
            import yaml  # soft — yaml may not be installed in minimal envs
        except ImportError:
            logger.warning(
                "PyYAML not installed — KnowledgeRegistryProxy returning empty store. "
                "Run: pip install pyyaml"
            )
            self._cache = {}
            return self._cache

        store: Dict[str, Any] = {}
        if not self.registry_root.exists():
            logger.warning(
                "Knowledge registry root not found: %s", self.registry_root
            )
            self._cache = {}
            return self._cache

        for yaml_file in sorted(self.registry_root.rglob("*.yaml")):
            relative = yaml_file.relative_to(self.registry_root)
            key = str(relative.with_suffix("")).replace("/", ".")
            try:
                content = yaml_file.read_text(encoding="utf-8")
                parsed = yaml.safe_load(content) or {}
                store[key] = {
                    "key": key,
                    "path": str(yaml_file),
                    "domain": relative.parts[0] if len(relative.parts) > 1 else "root",
                    "content": parsed,
                }
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to parse %s: %s", yaml_file, exc)

        self._cache = store
        return self._cache

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def all(self) -> List[Dict[str, Any]]:
        """Return all knowledge entries.

        Returns:
            List of dictionaries with ``key``, ``path``, ``domain``, and
            ``content`` for each knowledge YAML file.
        """
        return list(self._load().values())

    def query(self, domain: Optional[str] = None, key_contains: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query knowledge entries by domain or key substring.

        Args:
            domain: Filter by domain name (e.g. ``"backend-python"``).
            key_contains: Filter by substring match on the key.

        Returns:
            Filtered list of knowledge entries.
        """
        entries = self.all()
        if domain:
            entries = [e for e in entries if e.get("domain") == domain]
        if key_contains:
            entries = [e for e in entries if key_contains in e.get("key", "")]
        return entries

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single knowledge entry by exact key.

        Args:
            key: Dot-separated key (e.g. ``"backend-python.clean-code"``).

        Returns:
            Knowledge entry dictionary or ``None`` if not found.
        """
        return self._load().get(key)

    def domains(self) -> List[str]:
        """Return all distinct domain names in the registry.

        Returns:
            Sorted list of domain name strings.
        """
        return sorted({e.get("domain", "root") for e in self.all()})

    def invalidate_cache(self) -> None:
        """Clear the in-memory cache so the next call re-reads the registry.

        Useful in tests or when YAML files change at runtime.
        """
        self._cache = None


# AC_COMPLETE: AC-KNOWLEDGE-PROXY-5904 ✅
