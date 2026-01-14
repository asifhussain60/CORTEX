"""
Orchestrator Registry - Domain-based Query Interface

AC-AR-006-03: Orchestrator registry queryable by domain

Provides OrchestratorRegistry singleton for querying orchestrators:
- Query by domain (e.g., "governance", "audit", "evidence")
- Pattern matching and wildcards
- Metadata retrieval
- Registry statistics

Usage:
    registry = OrchestratorRegistry.instance()
    
    # Query by exact domain
    orchestrators = registry.get_by_domain("governance")
    
    # Query with pattern
    orchestrators = registry.query(domain_pattern="gov*")
    
    # Get registry stats
    stats = registry.get_stats()

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Pattern
import re
from dataclasses import dataclass, asdict
from datetime import datetime

from src.core.decorators.orchestrator_decorator import (
    get_registered_orchestrators,
    get_orchestrator_by_domain,
    get_orchestrators_by_domain,
)


@dataclass
class RegistryQuery:
    """Query result for registry lookups"""
    domain: Optional[str] = None
    pattern: Optional[str] = None
    results: List[Dict[str, Any]] = None
    total_count: int = 0
    matched_count: int = 0
    query_time: str = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []


class OrchestratorRegistry:
    """
    Singleton registry for querying orchestrators by domain.
    
    Provides:
    - Exact domain queries
    - Pattern/wildcard matching
    - Registry statistics
    - Orchestrator discovery
    """
    
    _instance: Optional['OrchestratorRegistry'] = None
    
    def __init__(self):
        """Initialize registry"""
        self.created_at = datetime.now().isoformat()
    
    @classmethod
    def instance(cls) -> 'OrchestratorRegistry':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)"""
        cls._instance = None
    
    # Query Methods
    
    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all orchestrators for a specific domain.
        
        Args:
            domain: Domain name (exact match)
        
        Returns:
            List of orchestrator metadata dicts
        """
        return get_orchestrators_by_domain(domain)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators."""
        return list(get_registered_orchestrators().values())
    
    def query(
        self,
        domain_pattern: Optional[str] = None,
        capability: Optional[str] = None,
        version: Optional[str] = None
    ) -> RegistryQuery:
        """
        Query orchestrators with pattern matching.
        
        Args:
            domain_pattern: Domain pattern (supports * wildcard)
                           e.g., "gov*", "*audit", "gov*ance"
            capability: Filter by capability (exact match)
            version: Filter by version (exact match)
        
        Returns:
            RegistryQuery with results and statistics
        """
        query_start = datetime.now()
        all_orchestrators = self.get_all()
        results = []
        
        # Filter by domain pattern
        if domain_pattern:
            domain_regex = self._pattern_to_regex(domain_pattern)
            filtered = [
                orch for orch in all_orchestrators
                if domain_regex.match(orch.get("domain", ""))
            ]
        else:
            filtered = all_orchestrators
        
        # Filter by capability
        if capability:
            filtered = [
                orch for orch in filtered
                if capability in orch.get("capabilities", [])
            ]
        
        # Filter by version
        if version:
            filtered = [
                orch for orch in filtered
                if orch.get("version") == version
            ]
        
        query_end = datetime.now()
        duration = (query_end - query_start).total_seconds()
        
        return RegistryQuery(
            domain=domain_pattern,
            pattern=domain_pattern,
            results=filtered,
            total_count=len(all_orchestrators),
            matched_count=len(filtered),
            query_time=f"{duration:.6f}s"
        )
    
    def find_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find all orchestrators with a specific capability.
        
        Args:
            capability: Capability name (exact match)
        
        Returns:
            List of orchestrator metadata dicts
        """
        return [
            orch for orch in self.get_all()
            if capability in orch.get("capabilities", [])
        ]
    
    def find_by_version(self, version: str) -> List[Dict[str, Any]]:
        """
        Find all orchestrators with a specific version.
        
        Args:
            version: Version string (exact match)
        
        Returns:
            List of orchestrator metadata dicts
        """
        return [
            orch for orch in self.get_all()
            if orch.get("version") == version
        ]
    
    # Registry Info Methods
    
    def get_domains(self) -> List[str]:
        """Get list of all registered domains."""
        domains = set()
        for orch in self.get_all():
            domains.add(orch.get("domain", "unknown"))
        return sorted(list(domains))
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """
        Get all capabilities organized by domain.
        
        Returns:
            Dict mapping domain -> list of capabilities
        """
        capabilities = {}
        for orch in self.get_all():
            domain = orch.get("domain", "unknown")
            if domain not in capabilities:
                capabilities[domain] = []
            capabilities[domain].extend(orch.get("capabilities", []))
        
        # Remove duplicates and sort
        for domain in capabilities:
            capabilities[domain] = sorted(list(set(capabilities[domain])))
        
        return capabilities
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict with statistics
        """
        orchestrators = self.get_all()
        domains = self.get_domains()
        capabilities = self.get_capabilities()
        
        # Flatten capabilities
        all_capabilities = set()
        for caps in capabilities.values():
            all_capabilities.update(caps)
        
        versions = set(orch.get("version") for orch in orchestrators)
        
        return {
            "total_orchestrators": len(orchestrators),
            "total_domains": len(domains),
            "domains": domains,
            "total_capabilities": len(all_capabilities),
            "capabilities": sorted(list(all_capabilities)),
            "capabilities_by_domain": capabilities,
            "versions": sorted(list(versions)),
            "created_at": self.created_at,
            "last_query_time": datetime.now().isoformat()
        }
    
    def get_orchestrator_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get orchestrator info for a domain (if unique).
        
        Args:
            domain: Domain name
        
        Returns:
            Orchestrator metadata or None if not found or multiple
        """
        orchestrators = self.get_by_domain(domain)
        if len(orchestrators) == 1:
            return orchestrators[0]
        return None
    
    # Pattern Matching
    
    @staticmethod
    def _pattern_to_regex(pattern: str) -> Pattern:
        """
        Convert wildcard pattern to regex.
        
        Args:
            pattern: Pattern string (e.g., "gov*", "*audit")
        
        Returns:
            Compiled regex pattern
        """
        # Escape special regex chars except *
        escaped = re.escape(pattern)
        # Replace escaped * with .*
        regex_pattern = escaped.replace(r"\*", ".*")
        # Match entire string
        regex_pattern = f"^{regex_pattern}$"
        return re.compile(regex_pattern, re.IGNORECASE)
    
    # Validation Methods
    
    def is_domain_registered(self, domain: str) -> bool:
        """Check if a domain has registered orchestrators."""
        return len(self.get_by_domain(domain)) > 0
    
    def validate_domain(self, domain: str) -> bool:
        """Validate a domain is registered."""
        return self.is_domain_registered(domain)
    
    # Summary/Description Methods
    
    def describe_registry(self) -> str:
        """Get human-readable registry description."""
        stats = self.get_stats()
        lines = [
            f"🎯 Orchestrator Registry",
            f"  Total Orchestrators: {stats['total_orchestrators']}",
            f"  Total Domains: {stats['total_domains']}",
            f"  Domains: {', '.join(stats['domains']) or 'None'}",
            f"  Total Capabilities: {stats['total_capabilities']}",
            f"  Versions: {', '.join(stats['versions']) or 'None'}",
        ]
        return "\n".join(lines)
