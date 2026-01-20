"""Brain Populator - Populates brain with knowledge.

Populates the knowledge base/brain with structured information.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum


class KnowledgeType(Enum):
    """Types of knowledge."""

    FACT = "fact"
    RULE = "rule"
    PATTERN = "pattern"
    HEURISTIC = "heuristic"
    RELATIONSHIP = "relationship"


@dataclass
class KnowledgeEntry:
    """Knowledge entry for brain.

    Attributes:
        entry_id: Unique entry identifier.
        knowledge_type: Type of knowledge.
        content: Knowledge content.
        metadata: Additional metadata.
    """

    entry_id: str
    knowledge_type: KnowledgeType
    content: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}


class BrainPopulator:
    """Populates brain with knowledge."""

    def __init__(self) -> None:
        """Initialize brain populator."""
        self.entries: Dict[str, KnowledgeEntry] = {}

    def add_knowledge(
        self, entry_id: str, knowledge_type: KnowledgeType, content: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeEntry:
        """Add knowledge entry.

        Args:
            entry_id: Entry ID.
            knowledge_type: Type of knowledge.
            content: Knowledge content.
            metadata: Optional metadata.

        Returns:
            KnowledgeEntry.
        """
        entry = KnowledgeEntry(
            entry_id=entry_id, knowledge_type=knowledge_type, content=content, metadata=metadata or {}
        )
        self.entries[entry_id] = entry
        return entry

    def get_knowledge(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get knowledge entry.

        Args:
            entry_id: Entry ID.

        Returns:
            KnowledgeEntry or None.
        """
        return self.entries.get(entry_id)

    def get_by_type(self, knowledge_type: KnowledgeType) -> List[KnowledgeEntry]:
        """Get entries by type.

        Args:
            knowledge_type: Type of knowledge.

        Returns:
            List of KnowledgeEntry.
        """
        return [e for e in self.entries.values() if e.knowledge_type == knowledge_type]

    def populate_brain(self, knowledge_entries: List[KnowledgeEntry]) -> int:
        """Populate brain with multiple entries.

        Args:
            knowledge_entries: List of entries to add.

        Returns:
            Number of entries added.
        """
        count = 0
        for entry in knowledge_entries:
            self.entries[entry.entry_id] = entry
            count += 1
        return count


__all__ = ["BrainPopulator", "KnowledgeEntry", "KnowledgeType"]
