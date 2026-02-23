"""CORTEX tier1_learned — Cleaners + Cognitive Memory (Dual Purpose).

**Vacuum Cleaners (primary historical use):**
- orchestrators/cleaners/ — markdown_sprawl, root_artifacts, database_bloat, etc.
- Supports VacuumOrchestrator via Cleaner/DataCleaner/FormatCleaner protocols
- governance/confirmation_gate_rules — cleaner safety rules

**Session Memory (Phase 59-h addition, GAP-59-11):**
- KnowledgeRetentionStore — in-session key/value memory for orchestrators
- Enables learned facts (TDD cycle counts, LENS scores, audit outcomes) to
  persist across method calls within a single CORTEX session

CORE-035: Single canonical implementations — no duplicate retention stores.
CORE-012: All public APIs are typed and docstring-covered.
"""

__license__ = 'Proprietary'
__description__ = 'tier1_learned — Cleaners + Cognitive Memory'

# Import orchestrators components for backward compatibility
from .orchestrators import (
    Cleaner,
    DataCleaner,
    FormatCleaner,
    CleaningRule,
    CleanerType,
    cleaners,
)

# Phase 59-h: Cognitive memory — makes 'tier1_learned' name accurate
from .knowledge_retention_store import KnowledgeRetentionStore

# Key TIER 1 components
__all__ = [
    '__license__',
    '__description__',
    # Vacuum cleaner exports (backward compat)
    'Cleaner',
    'DataCleaner',
    'FormatCleaner',
    'CleaningRule',
    'CleanerType',
    'cleaners',
    # Session memory
    'KnowledgeRetentionStore',
]

# Lazy imports for remaining TIER 1 modules
def __getattr__(name: str):
    """Lazy load TIER 1 sub-modules."""
    tier1_modules = {
        'orchestrators': 'cortex.intelligence.memory.tier1_learned.orchestrators',
        'brains': 'cortex.intelligence.memory.tier1_learned.brains',
        'intelligence': 'cortex.intelligence.memory.tier1_learned.intelligence',
        'adapters': 'cortex.intelligence.memory.tier1_learned.adapters',
    }

    if name in tier1_modules:
        try:
            import importlib
            return importlib.import_module(tier1_modules[name])
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.intelligence.memory.tier1_learned' has no attribute '{name}'")
