"""
Orchestrators Registry - Registration and Discovery System

Docker-First Architecture: YAML-backed wiring replaces database registries.

Provides:
- OrchestratorRegistry: Singleton registry for orchestrator registration
- @orchestrator decorator: Automatic registration and metadata tracking
- get_orchestrator_registry(): Access to singleton instance

Exports:
- OrchestratorMetadata: Metadata container for orchestrators
- OrchestratorRegistry: Main registry class
- orchestrator: Decorator for registering orchestrators
"""

from typing import Any, Callable, Dict, List, Optional, Set, Type
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global in-memory registry for decorated orchestrators
_ORCHESTRATOR_REGISTRY: Dict[str, Dict[str, Any]] = {}


class OrchestratorMetadata:
    """Metadata container for orchestrators."""
    def __init__(self, name: str, class_type: Any = None, **kwargs):
        self.name = name
        self.class_type = class_type
        self.__dict__.update(kwargs)


class OrchestratorRegistry:
    """
    Singleton orchestrator registry for runtime registration.
    
    Docker-first architecture: Actual wiring is via YAML configuration.
    This provides a runtime registry for decorator-based registration and
    runtime discovery of orchestrators.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._orchestrators: Dict[str, Dict[str, Any]] = {}
            self._name_to_id: Dict[str, str] = {}
            self._initialized = True
    
    @classmethod
    def instance(cls) -> 'OrchestratorRegistry':
        """Get singleton instance (backward compat)."""
        return cls()
    
    def register(
        self,
        orchestrator_id: str,
        name: str,
        cls: Type,
        module_path: str,
        tier_dependencies: Optional[Set[str]] = None,
        expose_mcp: bool = True,
        description: str = "",
    ) -> None:
        """Register an orchestrator."""
        entry = {
            "id": orchestrator_id,
            "name": name,
            "class": cls,
            "module_path": module_path,
            "tier_dependencies": tier_dependencies or set(),
            "expose_mcp": expose_mcp,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "wired": True,
        }
        self._orchestrators[orchestrator_id] = entry
        self._name_to_id[name] = orchestrator_id
        _ORCHESTRATOR_REGISTRY[orchestrator_id] = entry
        logger.debug(f"Registered orchestrator: {name} ({orchestrator_id})")
    
    def get_by_id(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator by ID."""
        return self._orchestrators.get(orchestrator_id)
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator by name."""
        orch_id = self._name_to_id.get(name)
        if orch_id:
            return self._orchestrators.get(orch_id)
        return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators."""
        return list(self._orchestrators.values())
    
    def count(self) -> int:
        """Count registered orchestrators."""
        return len(self._orchestrators)
    
    def clear(self) -> None:
        """Clear registry (for testing)."""
        self._orchestrators.clear()
        self._name_to_id.clear()
        _ORCHESTRATOR_REGISTRY.clear()
    
    def get(self, name: str) -> Optional[Any]:
        """Backward compatibility: get by name."""
        return self.get_by_name(name)
    
    def list_all(self) -> list:
        """Backward compatibility: list all."""
        return self.get_all()


def get_orchestrator_registry() -> OrchestratorRegistry:
    """Get the singleton orchestrator registry instance."""
    return OrchestratorRegistry()


# Discovery Engine Components (from deprecated discovery_engine.py)

from dataclasses import dataclass, field
from typing import List
import time


@dataclass
class DiscoveryQuery:
    """Query parameters for discovery search."""
    domain: Optional[str] = None
    capability: Optional[str] = None
    version: Optional[str] = None
    limit: Optional[int] = None
    
    def has_filters(self) -> bool:
        """Check if query has any filters."""
        return any([self.domain, self.capability, self.version])


@dataclass
class DiscoveryResult:
    """Result of discovery search."""
    orchestrators: List[OrchestratorMetadata] = field(default_factory=list)
    total_found: int = 0
    query_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    search_duration_ms: float = 0.0
    query_applied: Optional[DiscoveryQuery] = None


class DiscoveryEngine:
    """
    Discovery engine for finding orchestrators.
    
    Singleton pattern - only one instance exists.
    Provides query interface for orchestrator discovery.
    """
    
    _instance: Optional['DiscoveryEngine'] = None
    
    def __new__(cls) -> 'DiscoveryEngine':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize engine."""
        if self._initialized:
            return
        
        self.registry = get_orchestrator_registry()
        self._initialized = True
    
    def search(self, query: DiscoveryQuery) -> DiscoveryResult:
        """
        Search for orchestrators.
        
        Args:
            query: DiscoveryQuery with search parameters
        
        Returns:
            DiscoveryResult with matching orchestrators
        """
        start_time = time.time()
        
        # Get all orchestrators
        all_orchs = self.registry.get_all() or []
        
        # Apply filters
        filtered = self._apply_filters(all_orchs, query)
        
        # Apply limit
        if query.limit and len(filtered) > query.limit:
            filtered = filtered[:query.limit]
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        return DiscoveryResult(
            orchestrators=filtered,
            total_found=len(filtered),
            query_timestamp=datetime.now().isoformat(),
            search_duration_ms=duration_ms,
            query_applied=query,
        )
    
    def search_by_domain(self, domain: str) -> DiscoveryResult:
        """
        Search orchestrators by domain.
        
        Args:
            domain: Domain name
        
        Returns:
            DiscoveryResult with orchestrators in domain
        """
        query = DiscoveryQuery(domain=domain)
        return self.search(query)
    
    def search_by_capability(self, capability: str) -> DiscoveryResult:
        """
        Search orchestrators by capability.
        
        Args:
            capability: Capability name
        
        Returns:
            DiscoveryResult with orchestrators having capability
        """
        query = DiscoveryQuery(capability=capability)
        return self.search(query)
    
    def search_by_version(self, version: str) -> DiscoveryResult:
        """
        Search orchestrators by version.
        
        Args:
            version: Version string
        
        Returns:
            DiscoveryResult with orchestrators of version
        """
        query = DiscoveryQuery(version=version)
        return self.search(query)
    
    def search_by_domain_and_capability(
        self,
        domain: str,
        capability: str
    ) -> DiscoveryResult:
        """
        Search orchestrators by domain and capability.
        
        Args:
            domain: Domain name
            capability: Capability name
        
        Returns:
            DiscoveryResult with matching orchestrators
        """
        query = DiscoveryQuery(domain=domain, capability=capability)
        return self.search(query)
    
    def _apply_filters(
        self,
        orchestrators: List[Dict[str, Any]],
        query: DiscoveryQuery
    ) -> List[Dict[str, Any]]:
        """
        Apply query filters to orchestrator list.
        
        Args:
            orchestrators: List of orchestrators to filter
            query: Query with filters
        
        Returns:
            Filtered list
        """
        filtered = orchestrators
        
        # Filter by domain
        if query.domain:
            filtered = [o for o in filtered if o.get("domain") == query.domain]
        
        # Filter by capability
        if query.capability:
            filtered = [
                o for o in filtered
                if query.capability in o.get("capabilities", [])
            ]
        
        # Filter by version
        if query.version:
            filtered = [o for o in filtered if o.get("version") == query.version]
        
        return filtered
    
    def get_all_domains(self) -> List[str]:
        """
        Get all domains with registered orchestrators.
        
        Returns:
            List of domain names
        """
        domains = set()
        for orch in self.registry.get_all():
            if domain := orch.get("domain"):
                domains.add(domain)
        return sorted(list(domains))
    
    def get_all_capabilities(self) -> List[str]:
        """
        Get all capabilities provided by registered orchestrators.
        
        Returns:
            List of capability names
        """
        capabilities = set()
        for orch in self.registry.get_all():
            for cap in orch.get("capabilities", []):
                capabilities.add(cap)
        return sorted(list(capabilities))
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get discovery statistics.
        
        Returns:
            Dict with discovery statistics
        """
        all_orchs = self.registry.get_all()
        domains = self.get_all_domains()
        capabilities = self.get_all_capabilities()
        
        return {
            "total_orchestrators": len(all_orchs),
            "total_domains": len(domains),
            "domains": domains,
            "total_capabilities": len(capabilities),
            "capabilities": capabilities,
        }


# AC-PHASE-8.2-01: DiscoveryEngine replaced by OrchestratorLookup
# from cortex.orchestrators.registry.discovery_engine import (
#     DiscoveryEngine,
#     DiscoveryQuery,
#     DiscoveryResult,
# )

__all__ = [
    "OrchestratorRegistry",
    "OrchestratorMetadata",
    # "DiscoveryEngine",  # AC-PHASE-8.2-01: Deprecated
    # "DiscoveryQuery",   # AC-PHASE-8.2-01: Deprecated
    # "DiscoveryResult",  # AC-PHASE-8.2-01: Deprecated
]
