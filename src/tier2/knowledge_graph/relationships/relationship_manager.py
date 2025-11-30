"""
Relationship Manager Module

Manages pattern-to-pattern relationships (graph edges).

Relationship Types:
    - extends: Pattern B extends Pattern A
    - relates_to: General relationship
    - contradicts: Patterns conflict
    - supersedes: New pattern replaces old

Responsibilities:
    - Create relationships with validation
    - Query relationships (incoming/outgoing)
    - Update relationship strength
    - Delete relationships
    - Detect circular relationships

Performance Targets:
    - Create relationship: <15ms
    - Query relationships: <30ms
    - Graph traversal (depth=3): <150ms

Example:
    >>> from tier2.knowledge_graph.relationships.relationship_manager import RelationshipManager
    >>> rel_mgr = RelationshipManager(db)
    >>> rel_mgr.create_relationship(
    ...     from_pattern="tdd-basic",
    ...     to_pattern="tdd-advanced",
    ...     relationship_type="extends",
    ...     strength=0.9
    ... )
"""

from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime


class RelationshipType(Enum):
    """Pattern relationship types."""
    EXTENDS = "extends"
    RELATES_TO = "relates_to"
    RELATED_TO = "related_to"  # Alias
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"


class RelationshipManager:
    """
    Manages pattern relationships (graph edges).
    
    Handles creation, retrieval, and validation of relationships
    between patterns in the knowledge graph.
    """
    
    def __init__(self, db):
        """
        Initialize Relationship Manager.
        
        Args:
            db: DatabaseConnection instance
        """
        self.db = db
    
    def create_relationship(
        self,
        from_pattern: str,
        to_pattern: str,
        relationship_type: str,
        strength: float = 1.0
    ) -> Dict[str, Any]:
        """
        Create a relationship between two patterns.
        
        Args:
            from_pattern: Source pattern ID
            to_pattern: Target pattern ID
            relationship_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
        
        Returns:
            Dictionary with relationship data
        
        Raises:
            ValueError: If validation fails
            sqlite3.IntegrityError: If relationship already exists
        
        Validation:
            - Both patterns must exist
            - Cannot relate pattern to itself
            - Strength must be 0.0-1.0
        
        Performance: <15ms
        """
        if from_pattern == to_pattern:
            raise ValueError("Cannot create relationship to itself")
        if not (0.0 <= strength <= 1.0):
            raise ValueError(f"Strength must be 0.0-1.0, got {strength}")

        # Normalize alias
        if relationship_type == RelationshipType.RELATED_TO.value:
            relationship_type = RelationshipType.RELATES_TO.value

        if relationship_type not in {rt.value for rt in RelationshipType}:
            raise ValueError(f"Invalid relationship_type: {relationship_type}")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Validate both patterns exist
        cursor.execute("SELECT 1 FROM patterns WHERE pattern_id = ?", (from_pattern,))
        if cursor.fetchone() is None:
            raise ValueError(f"Source pattern not found: {from_pattern}")
        cursor.execute("SELECT 1 FROM patterns WHERE pattern_id = ?", (to_pattern,))
        if cursor.fetchone() is None:
            raise ValueError(f"Target pattern not found: {to_pattern}")

        created_at = datetime.now().isoformat()
        try:
            cursor.execute(
                """
                INSERT INTO pattern_relationships (
                    from_pattern, to_pattern, relationship_type, strength, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (from_pattern, to_pattern, relationship_type, strength, created_at)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise

        return {
            "from_pattern": from_pattern,
            "to_pattern": to_pattern,
            "relationship_type": relationship_type,
            "strength": strength,
            "created_at": created_at
        }
    
    def get_relationships(
        self,
        pattern_id: str,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for a pattern.
        
        Args:
            pattern_id: Pattern to query
            direction: "outgoing", "incoming", or "both"
        
        Returns:
            List of relationship dictionaries
        
        Performance: <30ms
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        queries = []
        params: List[str] = []

        if direction in ("outgoing", "both"):
            queries.append(
                "SELECT from_pattern, to_pattern, relationship_type, strength, created_at FROM pattern_relationships WHERE from_pattern = ?"
            )
            params.append(pattern_id)
        if direction in ("incoming", "both"):
            queries.append(
                "SELECT from_pattern, to_pattern, relationship_type, strength, created_at FROM pattern_relationships WHERE to_pattern = ?"
            )
            params.append(pattern_id)

        if not queries:
            raise ValueError("direction must be 'incoming', 'outgoing', or 'both'")

        sql = " UNION ALL ".join(queries) + " ORDER BY created_at DESC"
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append({
                "from_pattern": r[0],
                "to_pattern": r[1],
                "relationship_type": r[2],
                "strength": r[3],
                "created_at": r[4]
            })
        return results
    
    def traverse_graph(
        self,
        start_pattern: str,
        max_depth: int = 3,
        relationship_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Traverse the pattern graph from a starting point.
        
        Args:
            start_pattern: Starting pattern ID
            max_depth: Maximum traversal depth
            relationship_types: Filter by relationship types
        
        Returns:
            Dictionary with:
                - nodes: List of pattern IDs reached
                - edges: List of relationships traversed
                - paths: List of paths from start to each node
        
        Performance: <150ms for depth=3
        """
        if max_depth < 1:
            return {"nodes": [start_pattern], "edges": [], "paths": [[start_pattern]]}

        conn = self.db.get_connection()
        cursor = conn.cursor()

        allowed_types: Optional[Set[str]] = None
        if relationship_types:
            # Normalize alias
            normalized = []
            for rt in relationship_types:
                if rt == RelationshipType.RELATED_TO.value:
                    normalized.append(RelationshipType.RELATES_TO.value)
                else:
                    normalized.append(rt)
            allowed_types = set(normalized)

        nodes: Set[str] = {start_pattern}
        edges: List[Dict[str, Any]] = []
        paths: List[List[str]] = []

        # BFS traversal
        frontier: List[tuple[str, List[str]]] = [(start_pattern, [start_pattern])]
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[tuple[str, List[str]]] = []
            for current, path in frontier:
                cursor.execute(
                    "SELECT from_pattern, to_pattern, relationship_type, strength, created_at FROM pattern_relationships WHERE from_pattern = ?",
                    (current,)
                )
                for r in cursor.fetchall():
                    rel_type = r[2]
                    if allowed_types and rel_type not in allowed_types:
                        continue
                    target = r[1]
                    new_path = path + [target]
                    edges.append({
                        "from_pattern": r[0],
                        "to_pattern": target,
                        "relationship_type": rel_type,
                        "strength": r[3],
                        "created_at": r[4]
                    })
                    if target not in nodes:
                        nodes.add(target)
                        paths.append(new_path)
                        next_frontier.append((target, new_path))
            frontier = next_frontier
            depth += 1

        if not paths:
            paths = [[start_pattern]]

        return {
            "nodes": list(nodes),
            "edges": edges,
            "paths": paths
        }
