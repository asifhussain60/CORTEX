"""
KnowledgeIndexerDocGenBridge — bridges KnowledgeIndexer to DocGen pipeline.

Authority: GAP-66-005 | Phase 66-A | SWEEP-66-INTELLIGENCE-MATRIX
CORE-011: type hints on all functions
CORE-012: docstrings on all public APIs
CORE-035: single canonical implementation — no duplicates

Syncs YAML-based docgen artifacts into the KnowledgeIndexer SQLite database,
returning the list of YAML paths processed.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from cortex.intelligence.tier3.knowledge.knowledge_indexer import (
    IndexEntry,
    KnowledgeIndexer,
)

# AC_START: AC-66-A-005-KNOWLEDGE-INDEXER-DOCGEN-BRIDGE-20260224T000000Z

# Canonical docgen YAML locations under cortex-registry/
_DOCGEN_SEARCH_ROOTS: List[str] = [
    "cortex-registry/planning/phases",
    "cortex-registry/workflows/templates",
    "cortex-registry/governance",
    "cortex-registry/patterns",
]


class KnowledgeIndexerDocGenBridge:
    """Bridges the KnowledgeIndexer to the DocGen pipeline.

    Scans canonical YAML docgen artifact locations and registers each
    artifact as an :class:`~cortex.intelligence.tier3.knowledge.knowledge_indexer.IndexEntry`
    in the :class:`~cortex.intelligence.tier3.knowledge.knowledge_indexer.KnowledgeIndexer`
    SQLite database.

    Usage::

        from cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge import (
            KnowledgeIndexerDocGenBridge,
        )
        bridge = KnowledgeIndexerDocGenBridge()
        synced_paths = bridge.sync()
        # returns: ['.../phase-66.yaml', '.../audit-fix-pipeline.yaml', ...]

    Authority: GAP-66-005 | Phase 66-A
    """

    def __init__(
        self,
        indexer: Optional[KnowledgeIndexer] = None,
        search_roots: Optional[List[str]] = None,
    ) -> None:
        """Initialise the bridge with an optional custom indexer and search roots.

        Args:
            indexer: Pre-configured :class:`KnowledgeIndexer` instance.
                     If ``None``, a default indexer is created.
            search_roots: List of directory paths to scan for YAML docgen
                          artifacts.  Defaults to :data:`_DOCGEN_SEARCH_ROOTS`.
        """
        self._indexer = indexer if indexer is not None else KnowledgeIndexer()
        self._search_roots = search_roots if search_roots is not None else _DOCGEN_SEARCH_ROOTS

    def sync(self) -> List[str]:
        """Scan docgen YAML locations and register each artifact in the index.

        For every ``.yaml`` file found under the configured search roots the
        method creates an :class:`IndexEntry` and persists it via
        :meth:`KnowledgeIndexer.index_entry`.

        Returns:
            List of YAML file paths (as strings) that were discovered and
            indexed.  Guaranteed to have at least one entry when the project
            has any YAML artifacts under ``cortex-registry/``.
        """
        synced: List[str] = []

        for root_str in self._search_roots:
            root = Path(root_str)
            if not root.exists():
                continue
            for yaml_path in sorted(root.rglob("*.yaml")):
                entry = self._make_entry(yaml_path)
                self._indexer.index_entry(entry)
                synced.append(str(yaml_path))

        return synced

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_entry(self, yaml_path: Path) -> IndexEntry:
        """Convert a YAML file path to a :class:`IndexEntry`.

        Args:
            yaml_path: Absolute or relative path to the YAML file.

        Returns:
            :class:`IndexEntry` ready for :meth:`KnowledgeIndexer.index_entry`.
        """
        # Derive domain from the first component after cortex-registry/
        parts = yaml_path.parts
        domain = "docgen"
        for i, part in enumerate(parts):
            if part == "cortex-registry" and i + 1 < len(parts):
                domain = parts[i + 1]
                break

        entry_id = f"docgen:{yaml_path.stem}"
        return IndexEntry(
            entry_id=entry_id,
            domain=domain,
            title=yaml_path.stem.replace("-", " ").replace("_", " ").title(),
            ac_ids=[],
            created_at=datetime.utcnow(),
            file_path=str(yaml_path),
        )


# AC_COMPLETE: AC-66-A-005-KNOWLEDGE-INDEXER-DOCGEN-BRIDGE-20260224T000000Z ✅
