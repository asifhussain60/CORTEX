# src.tier2.knowledge_graph.knowledge_graph

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
