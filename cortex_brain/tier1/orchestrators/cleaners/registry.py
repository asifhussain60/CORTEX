"""
Cleaner Registry

Purpose:
    Registry for managing vacuum cleaner plugins with dynamic
    registration and retrieval.

Authority:
    - AC-VACUUM-REFACTOR-001: Golden test-driven refactoring
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: CORTEX Architect
Date: 2026-02-15
"""

from typing import Dict, Type, Any, List
from cortex_brain.tier1.orchestrators.cleaners.base import CleanerInterface


class CleanerRegistry:
    """
    Registry for vacuum cleaner plugins.
    
    Manages registration, retrieval, and listing of cleaner plugins.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._cleaners: Dict[str, Type[CleanerInterface]] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        cleaner_class: Type[CleanerInterface],
        config: Dict[str, Any]
    ) -> None:
        """
        Register cleaner plugin.
        
        Args:
            cleaner_class: Cleaner class (must inherit CleanerInterface)
            config: Configuration for cleaner instance
        
        Raises:
            TypeError: If cleaner_class doesn't inherit CleanerInterface
        """
        if not issubclass(cleaner_class, CleanerInterface):
            raise TypeError(
                f"{cleaner_class.__name__} must inherit from CleanerInterface"
            )
        
        # Create temporary instance to get domain
        temp_instance = cleaner_class(config)
        domain = temp_instance.domain
        
        self._cleaners[domain] = cleaner_class
        self._configs[domain] = config

    def get(self, domain: str) -> CleanerInterface:
        """
        Get cleaner instance by domain.
        
        Args:
            domain: Cleaner domain identifier
        
        Returns:
            Instantiated cleaner
        
        Raises:
            KeyError: If domain not registered
        """
        if domain not in self._cleaners:
            raise KeyError(f"Cleaner '{domain}' not registered")
        
        cleaner_class = self._cleaners[domain]
        config = self._configs[domain]
        return cleaner_class(config)

    def has(self, domain: str) -> bool:
        """
        Check if cleaner is registered.
        
        Args:
            domain: Cleaner domain identifier
        
        Returns:
            True if registered, False otherwise
        """
        return domain in self._cleaners

    def list_domains(self) -> List[str]:
        """
        List all registered cleaner domains.
        
        Returns:
            List of domain identifiers
        """
        return list(self._cleaners.keys())

    def clear(self) -> None:
        """Clear all registered cleaners."""
        self._cleaners.clear()
        self._configs.clear()
