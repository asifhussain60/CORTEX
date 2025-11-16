# src.tier2.knowledge_graph.relationships.relationship_manager

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
