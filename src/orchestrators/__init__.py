"""
Orchestrators Module (Legacy)

⚠️  MIGRATION COMPLETE (December 3, 2025)
   All functional orchestrators have been migrated to operations-based utilities.
   See: cortex-brain/documents/reports/ORCHESTRATOR-MIGRATION-COMPLETE-ANALYSIS.md

This module is preserved for compatibility but all functionality has moved to:
- src/operations/ - Entry point operations (align.py, healthcheck.py, etc.)
- src/operations/modules/ - Organized utility modules by category
- src/tier0/ - Core governance and TDD operations
- src/agents/ - Agent-based implementations

Migration Status: 97% complete (29/30 orchestrators migrated)
Remaining: Module loader only (this file)

For details on new architecture, see:
- ORCHESTRATOR-MIGRATION-COMPLETE-ANALYSIS.md
- Individual operation files in src/operations/
"""

# No orchestrators to import - all migrated to operations/modules/
__all__ = []
