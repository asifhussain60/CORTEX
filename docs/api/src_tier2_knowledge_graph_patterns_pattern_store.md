# src.tier2.knowledge_graph.patterns.pattern_store

Pattern Store Module

Handles all pattern storage operations including:
- Pattern creation and persistence
- Pattern retrieval by ID
- Pattern updates
- Pattern deletion (with cascade)
- Batch operations

Responsibilities (Single Responsibility Principle):
    - CRUD operations for patterns
    - Confidence score management
    - Access tracking (last_accessed, access_count)
    - Pattern validation

Performance Targets:
    - Pattern storage: <20ms
    - Pattern retrieval by ID: <10ms
    - Batch insert (100 patterns): <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_store import PatternStore
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> 
    >>> db = DatabaseConnection()
    >>> store = PatternStore(db)
    >>> 
    >>> pattern = store.store_pattern(
    ...     title="TDD Workflow",
    ...     content="Always write tests first",
    ...     pattern_type="workflow",
    ...     confidence=0.95
    ... )
