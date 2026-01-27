"""
Knowledge Querier - Advanced search and discovery over knowledge graph.
"""

from typing import Dict, List, Any, Optional


class KnowledgeQuerier:
    """Queries knowledge entities with filtering and relationship traversal."""

    def __init__(self) -> None:
        """Initialize the querier."""
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []

    def index_entity(self, entity: Dict[str, Any]) -> None:
        """Index an entity."""
        entity_id = str(entity.get("id", ""))
        if entity_id:
            self.entities[entity_id] = entity

    def query_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Query entity by ID."""
        return self.entities.get(entity_id)

    def query_by_filter(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query entities by filters."""
        results: List[Dict[str, Any]] = []
        
        for entity in self.entities.values():
            if all(entity.get(k) == v for k, v in filters.items()):
                results.append(entity)
        
        return results

    def index_relationship(self, relationship: Dict[str, Any]) -> None:
        """Index a relationship."""
        self.relationships.append(relationship)

    def find_relationship_path(self, source: str, target: str) -> List[str]:
        """Find path between entities through relationships."""
        if source == target:
            return [source]
        
        # Simple BFS
        visited: Dict[str, bool] = {source: True}
        queue: List[Any] = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            for rel in self.relationships:
                if rel.get("source_id") == current:
                    next_id = str(rel.get("target_id", ""))
                    if next_id == target:
                        return path + [next_id]
                    if next_id not in visited:
                        visited[next_id] = True
                        queue.append((next_id, path + [next_id]))
        
        return []

    def find_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Find entities related to given entity."""
        related_ids = set()
        
        for rel in self.relationships:
            if rel.get("source_id") == entity_id:
                related_ids.add(rel.get("target_id"))
            elif rel.get("target_id") == entity_id:
                related_ids.add(rel.get("source_id"))
        
        return [self.entities[eid] for eid in related_ids if eid in self.entities]
