"""
Canonical Orchestrator Metadata Models

AC-CORE-035-01: Single source of truth for orchestrator metadata structures
Authority: CORE-035 (Single Canonical Implementation)

This module provides the canonical definitions for orchestrator metadata used
across registry, lookup, and runtime systems.
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from cortex.core.interfaces.i_orchestrator import IOrchestrator  # CORE-035  # interface pattern — L0 model references L1 interface type-hint only


@dataclass
class OrchestratorMetadata:  # CORE-035-scoped — domain-specific variant
    """
    Canonical orchestrator metadata for runtime registration.

    Used by MasterOrchestrator for tracking registered orchestrators.

    Attributes:
        domain: Domain/category of orchestrator (core, domain, support)
        orchestrator: The orchestrator instance
        version: Version string (default "1.0")
        capabilities: List of capabilities provided
        registered_at: ISO timestamp of registration
    """
    domain: str
    orchestrator: "IOrchestrator"
    version: str = "1.0"
    capabilities: List[str] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WiringMetadata:
    """
    Canonical orchestrator metadata from wiring registry (YAML-backed).

    Used by OrchestratorLookup for resolving orchestrators from Git-backed YAML.

    Attributes:
        name: Orchestrator alias/name (registry key)
        module: Python module path
        category: core, domain, or support
        capabilities: List of capabilities
        priority: Loading priority (lower = higher priority)
        wired: Whether orchestrator is currently wired
        class_name: Actual Python class name (may differ from name)
            e.g., name="DocumentationOrchestrator", class_name="EnhancedDocumentationOrchestrator"
    """
    name: str
    module: str
    category: str
    capabilities: List[str]
    priority: int = 0
    wired: bool = False
    class_name: Optional[str] = None  # FIX: Add class_name field for name/class mismatch


class DecoratorMetadata:
    """
    Lightweight metadata container for decorator-based registration.

    Used by OrchestratorRegistry for @orchestrator decorator support.

    Attributes:
        name: Orchestrator name
        class_type: The orchestrator class
        **kwargs: Additional metadata fields
    """
    def __init__(self, name: str, class_type: Any = None, **kwargs) -> None:
        """Initialize instance."""
        self.name = name
        self.class_type = class_type
        self.__dict__.update(kwargs)


__all__ = [
    "OrchestratorMetadata",
    "WiringMetadata",
    "DecoratorMetadata",
]
