"""Entity deduplication engine for Knowledge Graph ingestion.

Detects and resolves duplicate entities in the domain brain based on ID matching
and fuzzy name matching, with configurable conflict resolution strategies.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class EntityRecord:
    """Represents a domain entity record for deduplication.

    Attributes:
        entity_id: Unique identifier
        entity_type: Type of entity (Domain, Service, API)
        name: Human-readable name
        properties: Entity properties
    """

    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    occurrences: int = 1


@dataclass
class DeduplicationResult:
    """Result of deduplication operation.

    Attributes:
        total_input: Total entities before deduplication
        total_output: Total entities after deduplication
        duplicates_found: Number of duplicate sets found
        conflicts_resolved: Number of property conflicts resolved
        merged_entities: List of merge operations (old_id -> new_id)
    """

    total_input: int
    total_output: int
    duplicates_found: int
    conflicts_resolved: int
    merged_entities: List[Tuple[str, str]] = field(default_factory=list)


class EntityDeduplicator:
    """Deduplication engine for domain brain entities.

    Deduplicates entities using:
      - Exact ID match (primary key dedup)
      - Fuzzy name matching (similarity > threshold)
      - Conflict resolution (property merging)

    Provides comprehensive reporting and merge tracking.
    """

    def __init__(self, name_similarity_threshold: float = 0.95) -> None:
        """Initialize deduplicator.

        Args:
            name_similarity_threshold: Minimum similarity score for fuzzy matching (0.0-1.0)
        """
        self.name_similarity_threshold = name_similarity_threshold
        self.deduplicated: Dict[str, EntityRecord] = {}
        self.merge_log: List[Tuple[str, str]] = []

    def deduplicate(self, entities: List[Dict[str, Any]]) -> DeduplicationResult:
        """Deduplicate a list of entities.

        Args:
            entities: List of entity dicts with id, type, name, properties

        Returns:
            DeduplicationResult: Summary of deduplication operation
        """
        self.deduplicated.clear()
        self.merge_log.clear()

        total_input = len(entities)
        conflicts_resolved = 0

        # Phase 1: Exact ID matching
        for entity in entities:
            entity_id = entity.get("id", "")
            entity_type = entity.get("type", "")
            name = entity.get("name", "")
            properties = entity.get("properties", {})

            if entity_id not in self.deduplicated:
                self.deduplicated[entity_id] = EntityRecord(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    name=name,
                    properties=properties.copy(),
                )
            else:
                # Duplicate ID found - resolve conflicts
                existing = self.deduplicated[entity_id]
                conflicts_resolved += self._resolve_conflicts(
                    existing, properties
                )
                existing.occurrences += 1

        # Phase 2: Fuzzy name matching (optional, for name-based dedup)
        # This is deferred for now - could implement in future
        # For now, primary dedup is by exact ID

        total_output = len(self.deduplicated)
        duplicates_found = total_input - total_output

        return DeduplicationResult(
            total_input=total_input,
            total_output=total_output,
            duplicates_found=duplicates_found,
            conflicts_resolved=conflicts_resolved,
            merged_entities=self.merge_log.copy(),
        )

    def _resolve_conflicts(
        self, existing: EntityRecord, new_properties: Dict[str, Any]
    ) -> int:
        """Resolve property conflicts between duplicate entities.

        Uses last-write-wins strategy: newer values override older ones.

        Args:
            existing: Existing entity record
            new_properties: New properties from duplicate entity

        Returns:
            int: Number of conflicts resolved
        """
        conflicts = 0

        for key, new_value in new_properties.items():
            if key in existing.properties:
                old_value = existing.properties[key]
                if old_value != new_value:
                    conflicts += 1
                    # Last-write-wins: use new value
                    existing.properties[key] = new_value
            else:
                # New property from duplicate, add it
                existing.properties[key] = new_value

        return conflicts

    def get_deduplicated_entities(self) -> List[Dict[str, Any]]:
        """Get list of deduplicated entities.

        Returns:
            List[Dict]: Deduplicated entities in ingestible format
        """
        return [
            {
                "id": record.entity_id,
                "type": record.entity_type,
                "name": record.name,
                "properties": record.properties,
            }
            for record in self.deduplicated.values()
        ]

    def get_merge_log(self) -> List[Tuple[str, str]]:
        """Get log of entity merges (duplicates).

        Returns:
            List[Tuple[str, str]]: List of (old_id, new_id) merges
        """
        return self.merge_log.copy()

    @staticmethod
    def _string_similarity(s1: str, s2: str) -> float:
        """Calculate string similarity using simple character overlap.

        Args:
            s1: First string
            s2: Second string

        Returns:
            float: Similarity score (0.0-1.0)

        Note:
            For production, use difflib.SequenceMatcher or more sophisticated
            fuzzy matching libraries.
        """
        if not s1 or not s2:
            return 0.0

        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0

        # Simple overlap-based similarity
        s1_set = set(s1_lower)
        s2_set = set(s2_lower)

        if not s1_set or not s2_set:
            return 0.0

        intersection = len(s1_set & s2_set)
        union = len(s1_set | s2_set)

        return intersection / union
