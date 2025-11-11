"""
CORTEX Source Package

Core CORTEX components:
- router.py: Universal entry point router
- session_manager.py: Conversation session management
- context_injector.py: Tier 1-3 context injection
- workflows/: Workflow orchestrators (TDD, feature creation, bug fix)

Version: 1.0
"""

# Lazy imports to avoid breaking tier1 imports when cortex_agents not installed
__all__ = [
    'CortexRouter',
    'SessionManager',
    'ContextInjector'
]

def __getattr__(name):
    """Lazy import to avoid dependency issues."""
    if name == 'CortexRouter':
        from .router import CortexRouter
        return CortexRouter
    elif name == 'SessionManager':
        from .session_manager import SessionManager
        return SessionManager
    elif name == 'ContextInjector':
        from .context_injector import ContextInjector
        return ContextInjector
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
