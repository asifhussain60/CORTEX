"""Orchestrator Decorator - Auto-registration framework.

This module provides decorator functionality for marking classes as orchestrators
and auto-registering them in a global registry with metadata tracking.

Author: CORTEX Framework
"""

import threading
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


class OrchestratorCapability(Enum):
    """Available orchestrator capabilities."""

    VALIDATE = "validate"
    ENFORCE = "enforce"
    ROUTE = "route"
    EXECUTE = "execute"
    ANALYZE = "analyze"
    RECOVER = "recover"


# Global registry protected by lock
_ORCHESTRATOR_REGISTRY: Dict[str, Dict[str, Any]] = {}
_REGISTRY_LOCK = threading.RLock()


def orchestrator(
    domain: str,
    version: str = "1.0",
    capabilities: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Callable[[Type[T]], Type[T]]:
    """Decorator to mark a class as an orchestrator and register it.

    Args:
        domain: Domain name for the orchestrator (e.g., "governance", "routing").
        version: Version string for the orchestrator. Defaults to "1.0".
        capabilities: List of capability strings the orchestrator provides.
        description: Human-readable description of the orchestrator.

    Returns:
        Decorator function that marks and registers the class.

    Raises:
        ValueError: If domain is empty or invalid.

    Example:
        @orchestrator(domain="governance", version="2.0", capabilities=["validate"])
        class GovernanceOrchestrator:
            pass
    """
    if not domain or not isinstance(domain, str):
        raise ValueError("domain must be a non-empty string")

    def decorator(cls: Type[T]) -> Type[T]:
        """Inner decorator that registers the class."""
        with _REGISTRY_LOCK:
            # Generate metadata
            metadata: Dict[str, Any] = {
                "domain": domain,
                "version": version,
                "capabilities": capabilities or [],
                "description": description or f"{cls.__name__} orchestrator for {domain}",
                "class": cls,
                "module": cls.__module__,
                "class_name": cls.__name__,
                "registered_at": datetime.now().isoformat(),
            }

            # Attach metadata to class
            cls._orchestrator_registered = True  # type: ignore
            cls._orchestrator_metadata = metadata  # type: ignore
            cls._orchestrator_domain = domain  # type: ignore

            # Register in global registry
            registry_key = f"{domain}::{cls.__name__}"
            _ORCHESTRATOR_REGISTRY[registry_key] = metadata

        return cls

    return decorator


def is_orchestrator(cls: Type[Any]) -> bool:
    """Check if a class is registered as an orchestrator.

    Args:
        cls: Class to check.

    Returns:
        True if the class is registered as an orchestrator, False otherwise.
    """
    return getattr(cls, "_orchestrator_registered", False) is True


def get_registered_orchestrators() -> Dict[str, Dict[str, Any]]:
    """Get all registered orchestrators.

    Returns:
        Dictionary mapping orchestrator registry keys to their metadata.
    """
    with _REGISTRY_LOCK:
        return dict(_ORCHESTRATOR_REGISTRY)


def get_orchestrator_by_domain(domain: str) -> Optional[Dict[str, Any]]:
    """Get first orchestrator for a specific domain.

    Args:
        domain: Domain name to search for.

    Returns:
        Metadata dict for the orchestrator, or None if not found.
    """
    with _REGISTRY_LOCK:
        for key, metadata in _ORCHESTRATOR_REGISTRY.items():
            if metadata["domain"] == domain:
                return dict(metadata)
    return None


def get_orchestrators_by_domain(domain: str) -> List[Dict[str, Any]]:
    """Get all orchestrators for a specific domain.

    Args:
        domain: Domain name to search for.

    Returns:
        List of metadata dicts for orchestrators in the domain.
    """
    with _REGISTRY_LOCK:
        return [
            dict(metadata)
            for metadata in _ORCHESTRATOR_REGISTRY.values()
            if metadata["domain"] == domain
        ]


def clear_orchestrator_registry() -> None:
    """Clear the global orchestrator registry.

    Used primarily for testing to reset registry state between tests.
    """
    with _REGISTRY_LOCK:
        _ORCHESTRATOR_REGISTRY.clear()
