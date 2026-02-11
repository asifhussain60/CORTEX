"""Cleaner Registry - Plugin Manager for VacuumOrchestrator

This module implements the registry that manages cleaner plugin registration,
discovery, and lifecycle. Follows SOLID principles for extensibility.

Registry Pattern Features:
- Dynamic registration of cleaner implementations
- Lazy instantiation (instantiate only when needed)
- Configuration resolution (per-cleaner or global)
- Plugin discovery and enumeration

Author: CORTEX Builder
Phase: PHASE-VAC-001-01
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from .interface import CleanerInterface


class CleanerRegistrationError(Exception):
    """Raised when cleaner registration fails."""

    pass


class CleanerNotFoundError(Exception):
    """Raised when requested cleaner is not registered."""

    pass


class CleanerRegistry:
    """Registry for VacuumOrchestrator cleaner plugins.

    SOLID Compliance:
    - Open/Closed: Registry extensible without modification
    - Dependency Inversion: Registry depends on CleanerInterface abstraction
    - Single Responsibility: Registry only manages plugins (not orchestration)

    Features:
    - Register cleaners by domain identifier
    - Retrieve instantiated cleaners with configuration
    - Enumerate all registered cleaners
    - Configuration resolution (per-cleaner or global fallback)

    Usage:
        ```python
        registry = CleanerRegistry()

        # Register cleaners
        registry.register_cleaner(MDOrganizerCleaner)
        registry.register_cleaner(PythonCacheCleaner)

        # Get cleaner list
        domains = registry.list_all()  # ['md_organizer', 'python_cache']

        # Instantiate cleaner
        cleaner = registry.get_cleaner('md_organizer')

        # Or with custom config
        custom_config = {'some_setting': 'value'}
        cleaner = registry.get_cleaner('md_organizer', config=custom_config)
        ```

    Type Hints: All parameters and return types are fully typed (CORE-011)
    Docstrings: All public methods have Google-style docstrings (CORE-012)
    """

    def __init__(self) -> None:
        """Initialize empty registry.

        Sets up internal storage for cleaner class mappings.
        """
        self._cleaners: Dict[str, Type[CleanerInterface]] = {}
        self._instantiated: Dict[str, CleanerInterface] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    def register_cleaner(
        self,
        cleaner_class: Type[CleanerInterface],
        domain: Optional[str] = None,
    ) -> None:
        """Register a cleaner implementation.

        Verifies that the provided class implements CleanerInterface, then
        registers it under its domain identifier. Domain can be specified
        explicitly or extracted from cleaner_class.domain property.

        Args:
            cleaner_class: Class implementing CleanerInterface
            domain: Override domain identifier (uses cleaner.domain if None)

        Raises:
            CleanerRegistrationError: If cleaner_class doesn't implement interface
            CleanerRegistrationError: If domain already has a registered cleaner
            ValueError: If cleaner_class is not a class
        """
        # Verify is a class
        if not isinstance(cleaner_class, type):
            raise CleanerRegistrationError(
                f"cleaner_class must be a class, got {type(cleaner_class)}"
            )

        # Verify implements CleanerInterface
        if not issubclass(cleaner_class, CleanerInterface):
            raise CleanerRegistrationError(
                f"{cleaner_class.__name__} must implement CleanerInterface"
            )

        # Get domain
        if domain is None:
            # Need to instantiate to get domain (property)
            # Create temporary instance just to get domain
            try:
                temp_config: Dict[str, Any] = {}
                temp_instance = cleaner_class(temp_config)
                domain = temp_instance.domain
            except Exception as e:
                raise CleanerRegistrationError(
                    f"Cannot get domain from {cleaner_class.__name__}: {e}"
                )

        # Check duplicate
        if domain in self._cleaners:
            raise CleanerRegistrationError(
                f"Cleaner already registered for domain '{domain}': {self._cleaners[domain].__name__}"
            )

        # Register
        self._cleaners[domain] = cleaner_class
        self.logger.info(f"Registered cleaner '{domain}': {cleaner_class.__name__}")

    def get_cleaner(
        self,
        domain: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> CleanerInterface:
        """Get instantiated cleaner by domain.

        Retrieves the cleaner class for the specified domain, loads
        configuration (if not provided), and returns an instantiated cleaner.

        Configuration Resolution Order:
        1. Provided config parameter (highest priority)
        2. Per-cleaner config: cortex_brain/tier1/orchestrators/cleaners/<domain>/config.yaml
        3. Global config: cortex_brain/vacuum/config.yaml
        4. Empty dict (fallback)

        Args:
            domain: Domain identifier (e.g., 'md_organizer')
            config: Override configuration (uses auto-resolution if None)

        Returns:
            Instantiated cleaner ready to use

        Raises:
            CleanerNotFoundError: If domain not registered
            Exception: Propagated from cleaner initialization
        """
        # Check domain exists
        if domain not in self._cleaners:
            available = ", ".join(self._cleaners.keys()) if self._cleaners else "none"
            raise CleanerNotFoundError(
                f"Cleaner not registered for domain '{domain}'. "
                f"Available domains: {available}"
            )

        # Get cleaner class
        cleaner_class = self._cleaners[domain]

        # Resolve config if not provided
        if config is None:
            config = self._load_config(domain)

        # Instantiate and return
        cleaner = cleaner_class(config)
        self.logger.info(f"Instantiated cleaner for domain '{domain}'")
        return cleaner

    def list_all(self) -> List[str]:
        """List all registered cleaner domains.

        Returns:
            List of domain identifiers (empty if none registered)
        """
        return list(self._cleaners.keys())

    def has_cleaner(self, domain: str) -> bool:
        """Check if cleaner is registered for domain.

        Args:
            domain: Domain identifier

        Returns:
            True if cleaner registered, False otherwise
        """
        return domain in self._cleaners

    def clear(self) -> None:
        """Clear all registered cleaners.

        WARNING: Use only for testing. Clears both the registry and
        instantiated cleaners cache.
        """
        self._cleaners.clear()
        self._instantiated.clear()
        self.logger.warning("Registry cleared - all cleaners removed")

    def _load_config(self, domain: str) -> Dict[str, Any]:
        """Load configuration for cleaner.

        Resolution order:
        1. Per-cleaner config: cortex_brain/tier1/orchestrators/cleaners/<domain>/config.yaml
        2. Global config: cortex_brain/vacuum/config.yaml
        3. Empty dict (fallback)

        Args:
            domain: Domain identifier

        Returns:
            Configuration dictionary
        """
        # Per-cleaner config
        cleaner_config_path = Path(__file__).parent / domain / "config.yaml"
        if cleaner_config_path.exists():
            try:
                with open(cleaner_config_path) as f:
                    config = yaml.safe_load(f)
                    self.logger.debug(f"Loaded per-cleaner config from {cleaner_config_path}")
                    return config or {}
            except Exception as e:
                self.logger.warning(f"Failed to load per-cleaner config: {e}")

        # Global config
        global_config_path = Path(__file__).parent.parent.parent / "vacuum" / "config.yaml"
        if global_config_path.exists():
            try:
                with open(global_config_path) as f:
                    config = yaml.safe_load(f)
                    self.logger.debug(f"Loaded global config from {global_config_path}")
                    return config or {}
            except Exception as e:
                self.logger.warning(f"Failed to load global config: {e}")

        # Fallback
        self.logger.debug(f"No config found for domain '{domain}', using empty config")
        return {}

    def __repr__(self) -> str:
        """String representation of registry.

        Returns:
            String describing registry status
        """
        count = len(self._cleaners)
        domains = ", ".join(self._cleaners.keys()) if self._cleaners else "none"
        return f"CleanerRegistry(cleaners={count}, domains=[{domains}])"
