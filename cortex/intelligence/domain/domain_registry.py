"""
Domain Registry - Discovery and registration of domain types.
"""

from typing import Dict, List, Any, Optional


class DomainRegistry:
    """Registry for domain types and discovery."""

    def __init__(self) -> None:
        """Initialize domain registry."""
        self.domains: Dict[str, Dict[str, Any]] = {}

    def register(self, domain_id: str, metadata: Dict[str, Any]) -> None:
        """
        Register a domain type.
        
        Args:
            domain_id: Domain identifier.
            metadata: Domain metadata.
        """
        self.domains[domain_id] = metadata

    def unregister(self, domain_id: str) -> bool:
        """
        Unregister a domain type.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            True if unregistered.
        """
        if domain_id in self.domains:
            del self.domains[domain_id]
            return True
        return False

    def is_registered(self, domain_id: str) -> bool:
        """
        Check if domain is registered.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            True if registered.
        """
        return domain_id in self.domains

    def get_domain(self, domain_id: str) -> Optional[Dict[str, Any]]:
        """
        Get domain metadata.
        
        Args:
            domain_id: Domain identifier.
            
        Returns:
            Domain metadata or None.
        """
        return self.domains.get(domain_id)

    def list_domains(self) -> List[str]:
        """
        List all registered domains.
        
        Returns:
            List of domain IDs.
        """
        return list(self.domains.keys())

    def list_all_available_domains(self) -> List[str]:
        """
        List all available domains (including built-ins).
        
        Returns:
            List of available domain IDs.
        """
        # Return all registered + built-in domains
        builtin = ["sales", "support", "finance", "operations", "hr"]
        all_domains = set(self.domains.keys())
        all_domains.update(builtin)
        return list(all_domains)

    def clear(self) -> None:
        """Clear all registered domains."""
        self.domains.clear()
