"""
Discovery Engine - Orchestrator Discovery and Query System

AC-AR-017-01: Discovery API for finding orchestrators

Provides:
- Query by domain, capability, version
- Combined queries with multiple filters
- Discovery results with metadata
- Performance-optimized searches

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
import time

from src.orchestrators.registry.orchestrator_registry import (
    OrchestratorRegistry,
    OrchestratorMetadata,
)


@dataclass
class DiscoveryQuery:
    """Query parameters for discovery search"""
    domain: Optional[str] = None
    capability: Optional[str] = None
    version: Optional[str] = None
    limit: Optional[int] = None
    
    def has_filters(self) -> bool:
        """Check if query has any filters"""
        return any([self.domain, self.capability, self.version])


@dataclass
class DiscoveryResult:
    """Result of discovery search"""
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
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize engine"""
        if self._initialized:
            return
        
        self.registry = OrchestratorRegistry()
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
        all_orchs = self.registry.list_all()
        
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
        orchestrators: List[OrchestratorMetadata],
        query: DiscoveryQuery
    ) -> List[OrchestratorMetadata]:
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
            filtered = [o for o in filtered if o.domain == query.domain]
        
        # Filter by capability
        if query.capability:
            filtered = [
                o for o in filtered
                if query.capability in o.capabilities
            ]
        
        # Filter by version
        if query.version:
            filtered = [o for o in filtered if o.version == query.version]
        
        return filtered
    
    def get_all_domains(self) -> List[str]:
        """
        Get all domains with registered orchestrators.
        
        Returns:
            List of domain names
        """
        stats = self.registry.get_statistics()
        return stats.get("domains", [])
    
    def get_all_capabilities(self) -> List[str]:
        """
        Get all capabilities provided by registered orchestrators.
        
        Returns:
            List of capability names
        """
        stats = self.registry.get_statistics()
        return stats.get("capabilities", [])
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get discovery statistics.
        
        Returns:
            Dict with discovery statistics
        """
        stats = self.registry.get_statistics()
        return {
            "total_orchestrators": stats["total_orchestrators"],
            "total_domains": stats["total_domains"],
            "domains": stats["domains"],
            "total_capabilities": stats["total_capabilities"],
            "capabilities": stats["capabilities"],
        }

