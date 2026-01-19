"""CORTEX Tier 0 - Governance, Audit, and Infrastructure.

TIER 0 provides the foundational governance layer:
- Core governance rules (28 CORE-* rules)
- Audit trail logging and verification
- Path abstraction for cross-platform compatibility
- Import resolution and module loading
- Registry and enforcement mechanisms

This tier is the foundation for all higher tiers.
"""

__version__ = '1.0.0'
__author__ = 'Asif Hussain'
__license__ = 'Proprietary'
__description__ = 'TIER 0 - Governance, Audit, and Infrastructure'

# Key TIER 0 components
__all__ = [
    '__version__',
    '__author__',
    '__license__',
    '__description__',
    'governance',
    'path_abstraction',
    'import_resolver',
    'linux_path_compat',
    'macos_path_compat',
    'windows_path_compat',
]

# Lazy imports for TIER 0 components
def __getattr__(name: str):
    """Lazy load TIER 0 modules."""
    tier0_modules = {
        'governance': 'cortex_brain.tier0.governance',
        'path_abstraction': 'cortex_brain.tier0.path_abstraction',
        'import_resolver': 'cortex_brain.tier0.import_resolver',
        'linux_path_compat': 'cortex_brain.tier0.linux_path_compat',
        'macos_path_compat': 'cortex_brain.tier0.macos_path_compat',
        'windows_path_compat': 'cortex_brain.tier0.windows_path_compat',
    }
    
    if name in tier0_modules:
        try:
            import importlib
            return importlib.import_module(tier0_modules[name])
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex_brain.tier0' has no attribute '{name}'")
