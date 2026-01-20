"""CORTEX - AI-Powered Development Orchestration System.

A comprehensive orchestration framework for intelligent development workflows,
combining governance, audit trails, and multi-tier knowledge management.

This is the root package for the CORTEX system. It exports core components
and provides unified access to the orchestration framework.
"""

__version__ = '1.0.0'
__author__ = 'Asif Hussain'
__email__ = 'asif@cortex.dev'
__license__ = 'Proprietary'
__description__ = 'AI-Powered Development Orchestration System'

# Package metadata
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__description__',
]

# Lazy imports - import submodules as needed
def __getattr__(name: str):
    """Lazy load cortex modules."""
    # This allows: from cortex import brain, api, etc. without importing everything
    if name in ('brain', 'api', 'core', 'infrastructure', 'lib', 'mcp', 'orchestrators', 'scripts', 'tools'):
        try:
            import importlib
            return importlib.import_module(f'cortex.{name}')
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex' has no attribute '{name}'")
