# src.tier2.knowledge_graph.database

Knowledge Graph Database Module

This module handles all database operations for the Knowledge Graph including:
- Database connection management
- Schema creation and migrations
- Transaction handling
- Connection pooling (future enhancement)

Responsibilities (Single Responsibility Principle):
    - Database schema initialization
    - Connection lifecycle management
    - Schema migrations and upgrades
    - Database health checks

Performance Target:
    - Connection establishment: <10ms
    - Schema creation: <50ms
    - Migration execution: <100ms

Example:
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> db = DatabaseConnection(db_path="cortex-brain/tier2/kg.db")
    >>> conn = db.get_connection()
    >>> cursor = conn.cursor()
    >>> # ... execute queries ...
    >>> db.close()
