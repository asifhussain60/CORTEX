"""CORTEX Brain - Tier-based Knowledge and Governance System.

The brain tier system provides hierarchical knowledge management:
- TIER 0: Governance, audit trails, compliance rules, path abstraction
- TIER 1: Core logic, orchestrators, domain brains, intelligence
- TIER 2: Advanced knowledge, curation, semantic search, integration

This is the root package for the multi-tier brain architecture.
"""

__version__ = '1.0.0'
__author__ = 'Asif Hussain'
__license__ = 'Proprietary'
__description__ = 'CORTEX Brain - Tier-based Knowledge and Governance'

# Package metadata
__all__ = [
    '__version__',
    '__author__',
    '__license__',
    '__description__',
    'tier0',
    'tier1',
    'tier2',
]

# Lazy imports for tier subpackages
def __getattr__(name: str):
    """Lazy load cortex_brain tier modules."""
    if name in ('tier0', 'tier1', 'tier2', 'state', 'releases'):
        try:
            import importlib
            return importlib.import_module(f'cortex_brain.{name}')
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex_brain' has no attribute '{name}'")
