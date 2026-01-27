"""
Intent Router Factory Stub (Docker-First Architecture)

Provides backward-compatible factory for IntentRouter.
Actual implementation is in intent_router.py.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

_factory_instance = None


def get_intent_router_factory():
    """
    Get intent router factory instance.
    
    Returns factory that creates IntentRouter instances.
    In Docker-first architecture, returns a stub that defers to intent_router.py.
    """
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = IntentRouterFactory()
    
    return _factory_instance


class IntentRouterFactory:
    """Factory for creating IntentRouter instances."""
    
    def __init__(self):
        """Initialize factory."""
        self._router = None
    
    def get_router(self):
        """Get or create IntentRouter instance."""
        if self._router is None:
            try:
                from cortex.orchestrators.core.intent_router import IntentRouter
                self._router = IntentRouter()
            except ImportError:
                logger.warning("IntentRouter not available")
                return None
        return self._router
    
    def create_router(self):
        """Create new IntentRouter instance."""
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter
            return IntentRouter()
        except ImportError:
            logger.warning("IntentRouter not available")
            return None
