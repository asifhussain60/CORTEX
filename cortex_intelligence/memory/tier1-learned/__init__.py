"""CORTEX Tier 1 - Core Logic and Intelligence.

TIER 1 provides core intelligence and orchestration:
- Orchestrators (Master, Planning, ADO, TDD, Interaction, etc.)
- Brain implementations (business domain, AST analysis, semantic)
- Intent routing and comprehension
- Dependency analysis and knowledge graph
- Adapter implementations

TIER 1 builds on TIER 0 governance and compliance.
"""

__version__ = '1.0.0'
__author__ = 'Asif Hussain'
__license__ = 'Proprietary'
__description__ = 'TIER 1 - Core Logic and Intelligence'

# Import orchestrators components for backward compatibility
from .orchestrators import (
    Cleaner,
    DataCleaner,
    FormatCleaner,
    CleaningRule,
    CleanerType,
    VacuumOrchestrator,
    VacuumStats,
    VacuumStrategy,
    cleaners,
)

# Key TIER 1 components
__all__ = [
    '__version__',
    '__author__',
    '__license__',
    '__description__',
    'orchestrators',
    'brains',
    'intelligence',
    'adapters',
    # Backward compatibility exports
    'Cleaner',
    'DataCleaner',
    'FormatCleaner',
    'CleaningRule',
    'CleanerType',
    'VacuumOrchestrator',
    'VacuumStats',
    'VacuumStrategy',
    'cleaners',
]

# Lazy imports for TIER 1 components
def __getattr__(name: str):
    """Lazy load TIER 1 modules."""
    tier1_modules = {
        'orchestrators': 'cortex_brain.tier1.orchestrators',
        'brains': 'cortex_brain.tier1.brains',
        'intelligence': 'cortex_brain.tier1.intelligence',
        'adapters': 'cortex_brain.tier1.adapters',
    }
    
    if name in tier1_modules:
        try:
            import importlib
            return importlib.import_module(tier1_modules[name])
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex_brain.tier1' has no attribute '{name}'")
