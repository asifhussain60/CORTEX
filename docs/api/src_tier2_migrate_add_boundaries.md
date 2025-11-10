# src.tier2.migrate_add_boundaries

CORTEX Tier 2: Schema Migration - Add Namespace/Scope Boundaries

This migration adds the knowledge boundary system to enforce impenetrable
separation between CORTEX core intelligence (generic) and application-specific
knowledge (KSESSIONS, NOOR, etc.).

Changes:
1. Add `scope` column: 'generic' (CORTEX) vs 'application' (apps)
2. Add `namespaces` column: JSON array supporting multi-app patterns
3. Create indexes for performance
4. Classify existing patterns based on content/source
5. Create rollback backup before migration

Usage:
    python CORTEX/src/tier2/migrate_add_boundaries.py [--dry-run] [--db-path PATH]

Args:
    --dry-run: Show what would be done without making changes
    --db-path: Path to database (default: cortex-brain/tier2/knowledge_graph.db)

## Functions

### `main()`

Main migration entry point.
