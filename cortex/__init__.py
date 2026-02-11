"""CORTEX - AI-Powered Development Orchestration System.

A comprehensive orchestration framework for intelligent development workflows,
combining governance, audit trails, and multi-tier knowledge management.

This is the root package for the CORTEX system. It exports core components
and provides unified access to the orchestration framework.

**Phase 3 Migration:** Now uses Git-backed YAML wiring system.
All orchestrator wiring comes from cortex/wiring/specifications/wiring.yaml.
"""

__version__ = '2.0.0'  # Updated for Phase 3 Git-backed wiring
__author__ = 'Asif Hussain'
__email__ = 'asif@cortex.dev'
__license__ = 'Proprietary'
__description__ = 'AI-Powered Development Orchestration System'

# Phase 3: Git-backed wiring system
# Import new wiring API for orchestrator access
from cortex.wiring import (
    bootstrap_cortex,
    get_cortex,
    get_wiring_hash,
    is_wired,
)

# AC-PERMANENT-FIX-015: Run mandatory startup validation on import
# This ensures all critical issues are detected and auto-remediated
# before any orchestrator code executes
try:
    from cortex.bootstrap import _bootstrap_success
except ImportError:
    pass

# Package metadata + wiring API
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__description__',
    # Phase 3 wiring API
    'bootstrap_cortex',
    'get_cortex',
    'is_wired',
    'get_wiring_hash',
]

# Lazy imports - import submodules as needed
def __getattr__(name: str):
    """Lazy load cortex modules."""
    # This allows: from cortex import brain, api, etc. without importing everything
    if name in ('brain', 'api', 'core', 'infrastructure', 'lib', 'mcp', 'orchestrators', 'scripts', 'tools', 'wiring'):
        try:
            import importlib
            return importlib.import_module(f'cortex.{name}')
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex' has no attribute '{name}'")
