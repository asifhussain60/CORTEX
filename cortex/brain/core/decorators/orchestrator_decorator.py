"""
Orchestrator Decorator - Auto-registration Pattern

AC-AR-006-02: Orchestrators auto-registered via @orchestrator decorator

Provides @orchestrator decorator for automatic registration:
- Marks a class as an orchestrator
- Auto-registers with central registry
- Tracks domain, version, and capabilities
- Enables dynamic discovery and composition

Usage:
    @orchestrator(
        domain="governance",
        version="2.0",
        capabilities=["validate", "enforce"]
    )
    class GovernanceOrchestrator(IOrchestrator):
        ...

Docker-first architecture: Orchestrators are configured via YAML wiring.

Author: Asif Hussain
"""

import functools
from typing import Any, Callable, List, Optional, Type, Dict
from datetime import datetime


# Global registry for orchestrator classes
_REGISTERED_ORCHESTRATORS: Dict[str, Dict[str, Any]] = {}


def orchestrator(
    domain: str,
    version: str = "1.0",
    capabilities: Optional[List[str]] = None,
    description: Optional[str] = None
):
    """
    Decorator to mark a class as an orchestrator and auto-register it.
    
    Args:
        domain: Domain name (e.g., "governance", "audit", "evidence")
        version: Orchestrator version (default: "1.0")
        capabilities: List of capabilities (e.g., ["validate", "enforce"])
        description: Human-readable description
    
    Returns:
        Decorated class with orchestrator metadata
    
    Example:
        @orchestrator(
            domain="governance",
            version="2.0",
            capabilities=["validate", "enforce"]
        )
        class GovernanceOrchestrator(IOrchestrator):
            ...
    """
    def decorator(cls: Type) -> Type:
        # Register the orchestrator
        metadata = {
            "domain": domain,
            "version": version,
            "capabilities": capabilities or [],
            "description": description or f"{cls.__name__} orchestrator",
            "class": cls,
            "registered_at": datetime.now().isoformat(),
            "class_name": cls.__name__
        }
        
        # Store in global registry
        registry_key = f"{domain}:{cls.__name__}"
        _REGISTERED_ORCHESTRATORS[registry_key] = metadata
        
        # Add metadata attribute to class
        cls._orchestrator_metadata = metadata
        cls._orchestrator_domain = domain
        cls._orchestrator_registered = True
        
        @functools.wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)
        
        # Preserve original class attributes
        wrapper._orchestrator_metadata = metadata
        wrapper._orchestrator_domain = domain
        wrapper._orchestrator_registered = True
        wrapper.__bases__ = cls.__bases__
        wrapper.__name__ = cls.__name__
        wrapper.__module__ = cls.__module__
        
        return cls
    
    return decorator


def get_registered_orchestrators() -> Dict[str, Dict[str, Any]]:
    """Get all registered orchestrators."""
    return _REGISTERED_ORCHESTRATORS.copy()


def get_orchestrator_by_domain(domain: str) -> Optional[Dict[str, Any]]:
    """Get orchestrator registration for a domain."""
    for key, metadata in _REGISTERED_ORCHESTRATORS.items():
        if metadata["domain"] == domain:
            return metadata
    return None


def get_orchestrators_by_domain(domain: str) -> List[Dict[str, Any]]:
    """Get all orchestrators for a domain."""
    return [
        metadata
        for metadata in _REGISTERED_ORCHESTRATORS.values()
        if metadata["domain"] == domain
    ]


def is_orchestrator(cls: Type) -> bool:
    """Check if a class is registered as an orchestrator."""
    return hasattr(cls, "_orchestrator_registered") and cls._orchestrator_registered


def clear_orchestrator_registry():
    """Clear all registered orchestrators (useful for testing)."""
    global _REGISTERED_ORCHESTRATORS
    _REGISTERED_ORCHESTRATORS.clear()
