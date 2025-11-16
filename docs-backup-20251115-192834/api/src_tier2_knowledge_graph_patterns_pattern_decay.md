# src.tier2.knowledge_graph.patterns.pattern_decay

Pattern Decay Module

Implements confidence decay based on access patterns (Governance Rule #12).

Decay Logic:
    - Patterns unused for >60 days start decaying
    - Decay rate: 1% per day
    - Minimum confidence: 0.3 (delete below this)
    - Pinned patterns: immune to decay

Responsibilities:
    - Calculate decay for patterns
    - Apply decay adjustments
    - Delete low-confidence patterns
    - Log decay operations (audit trail)

Performance Targets:
    - Decay calculation: <5ms per pattern
    - Batch decay (1000 patterns): <500ms
    - Cleanup operation: <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_decay import PatternDecay
    >>> decay = PatternDecay(db)
    >>> results = decay.apply_decay()
    >>> print(f"Decayed: {results['decayed']}, Deleted: {results['deleted']}")
