"""
Orchestrator Registry - Central Repository for Orchestrator Metadata

AC-AR-017-01: Registry stores orchestrator metadata
- Metadata storage (ID, name, domain, version, capabilities)
- Registration with validation
- Lookup and listing
- Statistics tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class OrchestratorMetadata:
    """Metadata for a registered orchestrator"""
    id: str
    name: str
    domain: str
    version: str
    capabilities: List[str]
    description: str
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate metadata after initialization"""
        self._validate()
    
    def _validate(self) -> None:
        """Validate metadata fields"""
        # Validate ID format (kebab-case)
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', self.id):
            raise ValueError(
                f"Invalid orchestrator ID: {self.id}. "
                f"Must be kebab-case (lowercase letters, numbers, hyphens)"
            )
        
        # Validate required fields
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Orchestrator name is required")
        
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Orchestrator description is required")
        
        # Domain must be valid
        valid_domains = {"planning", "analysis", "integration", "validation", "execution"}
        if self.domain not in valid_domains:
            raise ValueError(
                f"Invalid domain: {self.domain}. "
                f"Must be one of: {valid_domains}"
            )


class OrchestratorRegistry:
    """
    Central registry for orchestrator metadata.
    
    Singleton pattern - only one instance exists.
    Stores metadata for all registered orchestrators.
    """
    
    _instance: Optional['OrchestratorRegistry'] = None
    _orchestrators: Dict[str, OrchestratorMetadata] = {}
    
    def __new__(cls) -> 'OrchestratorRegistry':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize registry"""
        if self._initialized:
            return
        
        self._orchestrators = {}
        self._initialized = True
    
    def register(self, metadata: OrchestratorMetadata) -> None:
        """
        Register an orchestrator.
        
        Args:
            metadata: OrchestratorMetadata instance
        
        Raises:
            ValueError: If orchestrator already registered or validation fails
        """
        if metadata.id in self._orchestrators:
            raise ValueError(
                f"Orchestrator already registered: {metadata.id}"
            )
        
        self._orchestrators[metadata.id] = metadata
    
    def unregister(self, orchestrator_id: str) -> None:
        """
        Unregister an orchestrator.
        
        Args:
            orchestrator_id: ID of orchestrator to unregister
        """
        if orchestrator_id in self._orchestrators:
            del self._orchestrators[orchestrator_id]
    
    def get(self, orchestrator_id: str) -> Optional[OrchestratorMetadata]:
        """
        Get orchestrator by ID.
        
        Args:
            orchestrator_id: Orchestrator ID
        
        Returns:
            OrchestratorMetadata or None if not found
        """
        return self._orchestrators.get(orchestrator_id)
    
    def list_all(self) -> List[OrchestratorMetadata]:
        """
        List all registered orchestrators.
        
        Returns:
            List of OrchestratorMetadata objects
        """
        return list(self._orchestrators.values())
    
    def list_by_domain(self, domain: str) -> List[OrchestratorMetadata]:
        """
        List orchestrators in a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            List of orchestrators in the domain
        """
        return [
            orch for orch in self._orchestrators.values()
            if orch.domain == domain
        ]
    
    def list_by_capability(self, capability: str) -> List[OrchestratorMetadata]:
        """
        List orchestrators with a capability.
        
        Args:
            capability: Capability name
        
        Returns:
            List of orchestrators with capability
        """
        return [
            orch for orch in self._orchestrators.values()
            if capability in orch.capabilities
        ]
    
    def list_by_version(self, version: str) -> List[OrchestratorMetadata]:
        """
        List orchestrators with a version.
        
        Args:
            version: Version string
        
        Returns:
            List of orchestrators with version
        """
        return [
            orch for orch in self._orchestrators.values()
            if orch.version == version
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict with statistics
        """
        all_orchs = self._orchestrators.values()
        
        # Collect unique domains
        domains = set(orch.domain for orch in all_orchs)
        
        # Collect unique capabilities
        capabilities = set()
        for orch in all_orchs:
            capabilities.update(orch.capabilities)
        
        return {
            "total_orchestrators": len(self._orchestrators),
            "total_domains": len(domains),
            "domains": sorted(list(domains)),
            "total_capabilities": len(capabilities),
            "capabilities": sorted(list(capabilities)),
            "registered_at": datetime.now().isoformat(),
        }
    
    def clear(self) -> None:
        """Clear all orchestrators (for testing)"""
        self._orchestrators = {}
    
    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (for testing)"""
        cls._instance = None
