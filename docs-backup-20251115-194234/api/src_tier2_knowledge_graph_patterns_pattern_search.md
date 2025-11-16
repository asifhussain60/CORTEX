# src.tier2.knowledge_graph.patterns.pattern_search

Pattern Search Module

Handles semantic search across patterns using SQLite FTS5 (Full-Text Search).

Responsibilities:
    - FTS5 index management
    - BM25-ranked search queries
    - Namespace-aware search (boundary enforcement)
    - Multi-filter search (tags, confidence, scope)
    - Related pattern discovery

Performance Targets:
    - Simple search: <50ms
    - Complex search (multi-filter): <100ms
    - FTS5 ranking: <20ms overhead

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_search import PatternSearch
    >>> search = PatternSearch(db)
    >>> results = search.search("TDD workflow", min_confidence=0.8)
    >>> for result in results:
    ...     print(f"{result['title']}: {result['score']}")
