"""KnowledgeIndexRegistrar — idempotent INDEX.yaml registration.

Registers newly synthesized knowledge files into the canonical
``cortex-registry/knowledge/INDEX.yaml`` index.  All operations are idempotent
(duplicate paths produce a single entry) and the resulting guide list within
each domain is alphabetically sorted by path.

Phase: 135-b (GAP-135-03)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical — no other module writes INDEX.yaml directly)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# ── Canonical INDEX path ──────────────────────────────────────────────────────
_DEFAULT_INDEX_PATH: Path = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "INDEX.yaml"
)


class KnowledgeIndexRegistrar:
    """Idempotent registrar for cortex-registry/knowledge/INDEX.yaml.

    Ensures newly acquired knowledge files appear in the cross-domain index
    without duplicating existing entries.  Writes are immediately flushed to
    disk so callers see the update after ``register()`` returns.

    Args:
        index_path: Override path to INDEX.yaml (used in tests with ``tmp_path``).

    Usage::

        registrar = KnowledgeIndexRegistrar()
        registrar.register(
            domain="security",
            path="security/new-guide.yaml",
            title="New Security Guide",
            keywords=["security", "owasp"],
        )
    """

    def __init__(self, index_path: Optional[Path] = None) -> None:
        """Initialise with an optional INDEX.yaml path override."""
        self._index_path = index_path or _DEFAULT_INDEX_PATH

    def register(
        self,
        domain: str,
        path: str,
        title: str,
        keywords: Optional[List[str]] = None,
    ) -> None:
        """Register a new knowledge guide in INDEX.yaml.

        If *domain* does not yet exist in the index, a new section is created.
        If *path* is already registered under *domain*, the call is a no-op
        (idempotent).  After any write, guides within the domain are sorted
        alphabetically by ``path``.

        Args:
            domain: Top-level domain key in INDEX.yaml (e.g. ``"security"``).
            path: Relative path to the knowledge file (relative to ``cortex-registry/knowledge/``).
            title: Human-readable title for the guide entry.
            keywords: Optional list of search keywords.
        """
        data = self._load()

        # Ensure domain section exists
        if domain not in data or not isinstance(data.get(domain), dict):
            data[domain] = {"guides": []}
        if "guides" not in data[domain] or not isinstance(data[domain]["guides"], list):
            data[domain]["guides"] = []

        guides: List[Dict[str, Any]] = data[domain]["guides"]

        # Idempotency check: skip if path already registered
        existing_paths = [g.get("path", "") for g in guides]
        if path in existing_paths:
            logger.debug("KnowledgeIndexRegistrar: %r already in domain %r — skipping", path, domain)
            return

        # Add new entry
        new_entry: Dict[str, Any] = {"path": path, "title": title}
        if keywords:
            new_entry["keywords"] = sorted(keywords)
        guides.append(new_entry)

        # Sort alphabetically by path (CORE-012: predictable ordering)
        data[domain]["guides"] = sorted(guides, key=lambda g: g.get("path", ""))

        self._save(data)
        logger.debug("KnowledgeIndexRegistrar: registered %r in domain %r", path, domain)

    def _load(self) -> Dict[str, Any]:
        """Load the current INDEX.yaml content.

        Returns:
            Parsed INDEX.yaml dict, or empty dict on read/parse failure.
        """
        try:
            raw = yaml.safe_load(self._index_path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except Exception as exc:
            logger.warning("KnowledgeIndexRegistrar: failed to load INDEX.yaml — %s", exc)
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        """Write *data* back to INDEX.yaml.

        Args:
            data: Full INDEX.yaml dict to persist.
        """
        try:
            self._index_path.write_text(
                yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=True),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.error("KnowledgeIndexRegistrar: failed to write INDEX.yaml — %s", exc)
            raise
