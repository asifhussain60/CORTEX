"""
Knowledge Indexer - Index entities and relationships for fast retrieval.
"""

from typing import Any, Dict, List


class KnowledgeIndexer:
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
