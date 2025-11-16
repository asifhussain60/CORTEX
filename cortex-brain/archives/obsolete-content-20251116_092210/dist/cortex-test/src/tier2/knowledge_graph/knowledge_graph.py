"""
KnowledgeGraph Facade (Coordinator)

Provides a backward-compatible, high-level API aggregating modular components:
    - PatternStore (CRUD + confidence/access tracking)
    - PatternSearch (FTS5 BM25 ranked search + namespace boosting)
    - PatternDecay (scheduled confidence decay + audit trail)
    - RelationshipManager (graph edges CRUD + traversal)
    - TagManager (tag CRUD + queries)

Design Goals:
    - Keep each module <500 LOC (SOLID single responsibility)
    - Orchestrate operations without duplicating logic
    - Provide stable API while legacy code migrates off monolith
    - Allow eventual consolidation of database abstraction

NOTE:
    Two database abstractions currently exist (DatabaseConnection & ConnectionManager).
    This facade uses ConnectionManager for slimmer transactional helpers. A future
    consolidation can rename it to KGDatabase and remove DatabaseConnection.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from .database.connection import ConnectionManager
from .patterns.pattern_store import PatternStore
from .patterns.pattern_search import PatternSearch
from .patterns.pattern_decay import PatternDecay
from .relationships.relationship_manager import RelationshipManager
from .tags.tag_manager import TagManager


class KnowledgeGraph:
    """High-level orchestration for Knowledge Graph operations."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default consistent with existing database modules
            root = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier2"
            root.mkdir(parents=True, exist_ok=True)
            db_path = root / "knowledge_graph.db"
        self.connection_manager = ConnectionManager(db_path=db_path)

        # Component instances
        self.pattern_store = PatternStore(self.connection_manager)
        self.pattern_search = PatternSearch(self.connection_manager)
        self.pattern_decay = PatternDecay(self.connection_manager)
        self.relationships = RelationshipManager(self.connection_manager)
        self.tags = TagManager(self.connection_manager)

    # ---------------------- Pattern CRUD ----------------------
    def store_pattern(self, **kwargs) -> Dict[str, Any]:
        return self.pattern_store.store_pattern(**kwargs)

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        return self.pattern_store.get_pattern(pattern_id)

    def update_pattern(self, pattern_id: str, updates: Dict[str, Any]) -> bool:
        return self.pattern_store.update_pattern(pattern_id, updates)

    def delete_pattern(self, pattern_id: str) -> bool:
        return self.pattern_store.delete_pattern(pattern_id)

    def list_patterns(self, **filters) -> List[Dict[str, Any]]:
        return self.pattern_store.list_patterns(**filters)

    # ---------------------- Search ----------------------
    def search_patterns(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search(query=query, **kwargs)

    def search_patterns_with_namespace_priority(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.search_with_namespace_priority(query=query, **kwargs)

    def get_cortex_patterns(self, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.get_cortex_patterns(**kwargs)

    def get_application_patterns(self, namespace: str, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_search.get_application_patterns(namespace=namespace, **kwargs)

    # ---------------------- Decay ----------------------
    def apply_decay(self) -> Dict[str, Any]:
        return self.pattern_decay.apply_decay()

    def get_decay_candidates(self) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_candidates()

    def pin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.pin_pattern(pattern_id)

    def unpin_pattern(self, pattern_id: str) -> bool:
        return self.pattern_decay.unpin_pattern(pattern_id)

    def get_decay_log(self, **kwargs) -> List[Dict[str, Any]]:
        return self.pattern_decay.get_decay_log(**kwargs)

    # ---------------------- Relationships ----------------------
    def create_relationship(self, **kwargs) -> Dict[str, Any]:
        return self.relationships.create_relationship(**kwargs)

    def get_relationships(self, pattern_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        return self.relationships.get_relationships(pattern_id=pattern_id, direction=direction)

    def traverse_graph(self, start_pattern: str, **kwargs) -> Dict[str, Any]:
        return self.relationships.traverse_graph(start_pattern=start_pattern, **kwargs)

    # ---------------------- Tags ----------------------
    def add_tag(self, pattern_id: str, tag: str) -> bool:
        return self.tags.add_tag(pattern_id, tag)

    def remove_tag(self, pattern_id: str, tag: str) -> bool:
        return self.tags.remove_tag(pattern_id, tag)

    def get_tags(self, pattern_id: str) -> List[str]:
        return self.tags.get_tags(pattern_id)

    def get_patterns_by_tag(self, tag: str, **kwargs) -> List[Dict[str, Any]]:
        return self.tags.get_patterns_by_tag(tag=tag, **kwargs)

    def list_all_tags(self) -> List[Dict[str, int]]:
        return self.tags.list_all_tags()

    # ---------------------- Maintenance ----------------------
    def health_check(self) -> Dict[str, Any]:
        return self.connection_manager.health_check()

    def migrate(self, target_version: Optional[int] = None):
        return self.connection_manager.migrate(target_version)

    def close(self):
        self.connection_manager.close()

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


__all__ = ["KnowledgeGraph"]
