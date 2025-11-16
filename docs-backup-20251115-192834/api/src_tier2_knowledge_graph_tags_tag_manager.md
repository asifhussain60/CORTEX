# src.tier2.knowledge_graph.tags.tag_manager

Tag Manager Module

Manages pattern tags for organization and filtering.

Tag Features:
    - Many-to-many pattern-tag associations
    - Tag-based filtering and search
    - Tag popularity tracking
    - Namespace-aware tag queries

Responsibilities:
    - Add/remove tags from patterns
    - Query patterns by tags
    - List all tags with counts
    - Tag validation and normalization

Performance Targets:
    - Add tag: <10ms
    - Query by tag: <40ms
    - List all tags: <30ms

Example:
    >>> from tier2.knowledge_graph.tags.tag_manager import TagManager
    >>> tag_mgr = TagManager(db)
    >>> tag_mgr.add_tag("tdd-pattern-001", "testing")
    >>> tag_mgr.add_tag("tdd-pattern-001", "best-practice")
    >>> patterns = tag_mgr.get_patterns_by_tag("testing")
