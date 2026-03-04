"""
Knowledge Indexer - Index entities and relationships for fast retrieval.

Extended in Phase 20 with index_registry_yaml() — loads entities directly from
cortex-registry YAML files (profiles, repositories, domains) into the in-memory
entity index so KGInference can reason over them.

Authority: AC-P20-004, AC-P20-014
Rule: CORE-011 (type hints), CORE-012 (docstrings)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class KnowledgeIndexer:  # CORE-035-scoped — domain-specific variant
    """Indexes entities and relationships with full-text search."""

    def __init__(self) -> None:
        """Initialize the indexer."""
        self.entity_index: Dict[str, Dict[str, Any]] = {}
        self.relationship_index: Dict[str, List[Dict[str, Any]]] = {}
        self.full_text_index: Dict[str, List[str]] = {}

    def add_entity(self, entity: Dict[str, Any]) -> None:
        """
        Add entity to index.

        Args:
            entity: Entity with id, type, and other properties.
        """
        entity_id = str(entity.get("id", ""))
        if not entity_id:
            return

        self.entity_index[entity_id] = entity

        # Build full-text index
        text_fields = [
            str(entity.get("name", "")),
            str(entity.get("description", "")),
        ]
        text = " ".join(text_fields).lower()
        self.full_text_index[entity_id] = text.split()

    def get_entity(self, entity_id: str) -> Any:
        """Get entity by ID."""
        return self.entity_index.get(entity_id)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Full-text search for entities."""
        query_words = query.lower().split()
        results = []

        for entity_id, words in self.full_text_index.items():
            if any(word in words for word in query_words):
                results.append(self.entity_index[entity_id])

        return results

    def add_relationship(self, relationship: Dict[str, Any]) -> None:
        """Add relationship to index."""
        source = str(relationship.get("source_id", ""))
        if not source:
            return

        if source not in self.relationship_index:
            self.relationship_index[source] = []
        self.relationship_index[source].append(relationship)

    def get_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships from entity."""
        return self.relationship_index.get(entity_id, [])

    def batch_add_entities(self, entities: List[Dict[str, Any]]) -> None:
        """Batch add entities."""
        for entity in entities:
            self.add_entity(entity)

    def index_registry_yaml(self, yaml_path: Path, entity_type: str) -> None:
        """
        Load entities from a cortex-registry YAML file into the entity index.

        Reads *yaml_path* and extracts the canonical entity id from the
        ``profile.id`` key (knowledge-base/profiles/) or ``repository.name``
        key (knowledge-base/repositories/).  Entities already present in the
        index are overwritten in-place (idempotent — AC-P20-014).

        Missing or malformed files are logged and silently skipped (graceful
        degradation — AC-P20-004c).

        Args:
            yaml_path: Absolute path to the YAML file to index.
            entity_type: Semantic type label (e.g. ``"profile"``, ``"repo"``,
                         ``"domain"``).  Stored on the entity as ``entity["type"]``.

        Returns:
            None — entities are added to :attr:`entity_index` in place.

        Example::

            indexer = KnowledgeIndexer()
            indexer.index_registry_yaml(
                Path("cortex-registry/knowledge/profiles/finops.yaml"),
                entity_type="profile",
            )
            assert indexer.get_entity("finops-v1.0") is not None
        """
        if not yaml_path.exists():
            logger.debug("index_registry_yaml: file not found — %s", yaml_path)
            return

        try:
            raw: Any = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("index_registry_yaml: failed to parse %s — %s", yaml_path, exc)
            return

        if not isinstance(raw, dict):
            logger.debug("index_registry_yaml: root is not a mapping — %s", yaml_path)
            return

        # ---- Extract entity id using known YAML layouts ----
        entity_id: Optional[str] = None
        entity_data: Dict[str, Any] = dict(raw)

        # Layout 1: profile: {id: "...", ...}
        profile_block = raw.get("profile") or {}
        if isinstance(profile_block, dict) and profile_block.get("id"):
            entity_id = str(profile_block["id"])
            entity_data = {**profile_block, "raw_yaml": raw}

        # Layout 2: repository: {name: "..."}
        elif raw.get("repository", {}).get("name"):
            entity_id = str(raw["repository"]["name"])
            entity_data = {**raw.get("repository", {}), "raw_yaml": raw}

        # Layout 3: fallback — use stem of filename
        else:
            entity_id = yaml_path.stem
            entity_data = {**raw, "id": entity_id}

        entity_data["id"] = entity_id
        entity_data["type"] = entity_type
        entity_data["source_file"] = str(yaml_path)

        # Overwrite existing entry (idempotent — AC-P20-014)
        self.entity_index[entity_id] = entity_data

        # Rebuild full-text index entry for this entity
        text_fields = [
            str(entity_data.get("name", "")),
            str(entity_data.get("description", "")),
            entity_id,
        ]
        self.full_text_index[entity_id] = " ".join(text_fields).lower().split()

        logger.debug(
            "index_registry_yaml: indexed entity '%s' (type=%s) from %s",
            entity_id,
            entity_type,
            yaml_path.name,
        )
