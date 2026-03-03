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
# CORE-035 — domain-scoped; class name appropriate for this module

from typing import Dict, List
from .base import CleanerInterface


class CleanerRegistry:
    """
    Registry for vacuum cleaner plugins.

    Manages registration, retrieval, and listing of cleaner plugins.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._cleaners: Dict[str, CleanerInterface] = {}

    def register(
        self,
        cleaner: CleanerInterface
    ) -> None:
        """
        Register cleaner plugin instance.

        Args:
            cleaner: Cleaner instance (must be CleanerInterface)

        Raises:
            TypeError: If cleaner doesn't inherit from CleanerInterface
        """
        if not isinstance(cleaner, CleanerInterface):
            raise TypeError(
                f"{type(cleaner).__name__} must be an instance of CleanerInterface"
            )

        domain = cleaner.domain
        self._cleaners[domain] = cleaner

    def get(self, domain: str) -> CleanerInterface:
        """
        Get cleaner instance by domain.

        Args:
            domain: Cleaner domain identifier

        Returns:
            Cleaner instance

        Raises:
            KeyError: If domain not registered
        """
        if domain not in self._cleaners:
            raise KeyError(f"Cleaner '{domain}' not registered")

        return self._cleaners[domain]

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
