# src.tier2.oracle_crawler

Oracle Database Schema Crawler for CORTEX Knowledge Extraction

This crawler connects to Oracle databases, extracts schema metadata (tables, columns,
relationships, indexes), and stores them as knowledge patterns in Tier 2 knowledge graph.

CORTEX Tier 2 Integration:
- Scope: 'application' (database schemas are application-specific)
- Namespace: Database name (e.g., ['KSESSIONS_DB'])
- Pattern Title: "Oracle: {table_name} schema"
- Confidence: 0.95 (high confidence from direct schema introspection)

Usage:
    crawler = OracleCrawler(connection_string="user/pass@host:port/service")
    patterns = crawler.extract_schema()
    crawler.store_patterns(patterns, knowledge_graph)
