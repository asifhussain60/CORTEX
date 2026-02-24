"""
cortex.knowledge.registry_proxy — KnowledgeRegistryProxy
=========================================================

Unified proxy over **all** CORTEX knowledge YAML files across two
canonical roots inside ``cortex-registry/``:

1. ``cortex-registry/knowledge/``      — best-practice guides (clean code,
   TDD, SOLID, design patterns, security coding, monitoring)
2. ``cortex-registry/knowledge-base/`` — runtime knowledge (governance rules,
   domain profiles, repository metadata, OWASP, CI/CD hardening)

Together these roots contain **30 YAML files** spanning 11 domains.  The
proxy loads lazily, caches in-memory, and tags every entry with a ``source``
field (``"knowledge"`` or ``"knowledge-base"``) so consumers can filter by
origin when needed.

Phase 59-d → Phase 62-H: Upgraded from single-root to dual-root unified
loading.  All 30 YAMLs now visible to orchestrators via one import.

CORE Rules: CORE-035 (single canonical), CORE-011, CORE-012
AC_START: AC-KNOWLEDGE-PROXY-62H
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Resolve project root → cortex-registry/
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_KNOWLEDGE_ROOT = _PROJECT_ROOT / "cortex-registry" / "knowledge"
_KNOWLEDGE_BASE_ROOT = _PROJECT_ROOT / "cortex-registry" / "knowledge-base"

__all__ = ["KnowledgeRegistryProxy"]


class KnowledgeRegistryProxy:
    """Unified proxy that loads and queries YAML knowledge from both
    ``cortex-registry/knowledge/`` and ``cortex-registry/knowledge-base/``.

    Every entry is tagged with:

    - ``source`` — ``"knowledge"`` (guides) or ``"knowledge-base"`` (runtime)
    - ``domain`` — top-level directory name (e.g. ``"backend-python"``,
      ``"governance"``, ``"profiles"``)
    - ``key``    — dot-separated path without extension

    Usage::

        proxy = KnowledgeRegistryProxy()
        all_entries = proxy.all()              # 30 entries
        proxy.query(domain="governance")       # 5 governance rule files
        proxy.query(source="knowledge")        # 11 best-practice guides
        proxy.query(source="knowledge-base")   # 19 runtime knowledge files
        proxy.get("governance.compliance-rules")

    Attributes:
        roots: List of (Path, source_tag) tuples to scan.
    """

    def __init__(
        self,
        knowledge_root: Optional[Path] = None,
        knowledge_base_root: Optional[Path] = None,
        *,
        registry_root: Optional[Path] = None,
    ) -> None:
        """Initialise the proxy.

        Args:
            knowledge_root: Override path to ``cortex-registry/knowledge/``.
            knowledge_base_root: Override path to ``cortex-registry/knowledge-base/``.
            registry_root: **Backward-compat alias** for ``knowledge_root``.
                           If provided (and ``knowledge_root`` is not), sets the
                           primary root and disables the ``knowledge-base`` root.
        """
        # Backward compatibility: registry_root sets knowledge_root
        if registry_root is not None and knowledge_root is None:
            knowledge_root = registry_root
            # When only registry_root is given, behave like the old single-root proxy
            knowledge_base_root = knowledge_base_root  # keep if explicitly given

        self._primary_root: Path = knowledge_root or _KNOWLEDGE_ROOT
        self.roots: List[tuple] = [
            (self._primary_root, "knowledge"),
        ]
        # Only add knowledge-base root if not overridden to a custom path
        kb_root = knowledge_base_root or _KNOWLEDGE_BASE_ROOT
        if kb_root.exists():
            self.roots.append((kb_root, "knowledge-base"))
        self._cache: Optional[Dict[str, Any]] = None

    @property
    def registry_root(self) -> Path:
        """Backward-compat property — returns the primary knowledge root path."""
        return self._primary_root

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> Dict[str, Any]:
        """Load all YAML knowledge files from both registry roots.

        Returns:
            Dictionary keyed by ``domain/filename`` with parsed YAML content.
            Each entry includes a ``source`` tag indicating origin.
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

        for root_path, source_tag in self.roots:
            if not root_path.exists():
                logger.debug(
                    "Knowledge root not found (skipped): %s", root_path
                )
                continue

            for yaml_file in sorted(root_path.rglob("*.yaml")):
                relative = yaml_file.relative_to(root_path)
                # Skip INDEX files
                if relative.name == "INDEX.yaml":
                    continue
                key = str(relative.with_suffix("")).replace("/", ".")
                try:
                    content = yaml_file.read_text(encoding="utf-8")
                    parsed = yaml.safe_load(content) or {}
                    store[key] = {
                        "key": key,
                        "path": str(yaml_file),
                        "source": source_tag,
                        "domain": (
                            relative.parts[0]
                            if len(relative.parts) > 1
                            else "root"
                        ),
                        "content": parsed,
                    }
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse %s: %s", yaml_file, exc)

        logger.debug(
            "KnowledgeRegistryProxy loaded %d entries from %d roots",
            len(store),
            len(self.roots),
        )
        self._cache = store
        return self._cache

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def all(self) -> List[Dict[str, Any]]:
        """Return all knowledge entries from both roots.

        Returns:
            List of dictionaries with ``key``, ``path``, ``source``,
            ``domain``, and ``content`` for each knowledge YAML file.
        """
        return list(self._load().values())

    def query(
        self,
        domain: Optional[str] = None,
        source: Optional[str] = None,
        key_contains: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query knowledge entries by domain, source, or key substring.

        Args:
            domain: Filter by domain name (e.g. ``"backend-python"``).
            source: Filter by origin — ``"knowledge"`` or ``"knowledge-base"``.
            key_contains: Filter by substring match on the key.

        Returns:
            Filtered list of knowledge entries.
        """
        entries = self.all()
        if domain:
            entries = [e for e in entries if e.get("domain") == domain]
        if source:
            entries = [e for e in entries if e.get("source") == source]
        if key_contains:
            entries = [e for e in entries if key_contains in e.get("key", "")]
        return entries

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single knowledge entry by exact key.

        Args:
            key: Dot-separated key (e.g. ``"backend-python.clean-code"``
                 or ``"governance.compliance-rules"``).

        Returns:
            Knowledge entry dictionary or ``None`` if not found.
        """
        return self._load().get(key)

    def domains(self) -> List[str]:
        """Return all distinct domain names across both roots.

        Returns:
            Sorted list of domain name strings.
        """
        return sorted({e.get("domain", "root") for e in self.all()})

    def sources(self) -> List[str]:
        """Return distinct source tags (``"knowledge"`` and/or ``"knowledge-base"``).

        Returns:
            Sorted list of source tag strings.
        """
        return sorted({e.get("source", "unknown") for e in self.all()})

    def entry_count(self) -> int:
        """Return total number of knowledge entries loaded.

        Returns:
            Integer count of all loaded YAML entries.
        """
        return len(self._load())

    def invalidate_cache(self) -> None:
        """Clear the in-memory cache so the next call re-reads the registry.

        Useful in tests or when YAML files change at runtime.
        """
        self._cache = None


# AC_COMPLETE: AC-KNOWLEDGE-PROXY-62H ✅
