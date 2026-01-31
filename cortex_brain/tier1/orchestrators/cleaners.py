"""Cleaners Module - Cleaner Interface and Registry

Author: CORTEX Framework
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Analysis:
    """Analysis result from a cleaner."""
    cleaner_id: str
    timestamp: str
    files_scanned: int
    issues_found: int
    plan: Dict[str, Any]
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        from dataclasses import asdict
        return asdict(self)


@dataclass
class Report:
    """Execution report from a cleaner."""
    cleaner_id: str
    timestamp: str
    status: str
    actions_taken: int
    changes: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        from dataclasses import asdict
        return asdict(self)
    
    @property
    def is_success(self) -> bool:
        """Check if execution was successful.
        
        Returns:
            True if status is SUCCESS and no errors, False otherwise
        """
        return self.status == "SUCCESS" and len(self.errors) == 0
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed.
        
        Returns:
            True if status is FAILED or status is not SUCCESS, False otherwise
        """
        return self.status == "FAILED" or self.status != "SUCCESS"


@dataclass
class RollbackResult:
    """Rollback operation result."""
    cleaner_id: str
    timestamp: str
    status: str
    files_restored: int
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        from dataclasses import asdict
        return asdict(self)
    
    @property
    def is_success(self) -> bool:
        """Check if rollback was successful.
        
        Returns:
            True if status is SUCCESS and no errors, False otherwise
        """
        return self.status == "SUCCESS" and len(self.errors) == 0


class CleanerInterface(ABC):
    """Base interface for cleaner plugins."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize cleaner.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.dry_run = config.get("dry_run", False)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get cleaner name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get cleaner version."""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Get cleaner domain."""
        pass
    
    @property
    def cleaner_id(self) -> str:
        """Get cleaner ID (alias for domain).
        
        Returns:
            Cleaner ID
        """
        return self.domain
    
    @abstractmethod
    def analyze(self) -> Analysis:
        """Analyze repository for cleaning opportunities.
        
        Returns:
            Analysis result
        """
        pass
    
    @abstractmethod
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute cleaning plan.
        
        Args:
            plan: Cleaning plan from analyze
            
        Returns:
            Execution report
        """
        pass
    
    @abstractmethod
    def rollback(self) -> RollbackResult:
        """Rollback recent changes.
        
        Returns:
            Rollback result
        """
        pass


class CleanerRegistry:
    """Registry for cleaner plugins."""
    
    def __init__(self) -> None:
        """Initialize registry."""
        self._cleaners: Dict[str, type] = {}
    
    def register_cleaner(self, cleaner_class: type) -> None:
        """Register a cleaner class.
        
        Args:
            cleaner_class: Cleaner class to register
            
        Raises:
            CleanerRegistrationError: If class is invalid or domain already registered
        """
        # Validate it's a class
        if not isinstance(cleaner_class, type):
            raise CleanerRegistrationError(
                f"Expected a class, got {type(cleaner_class).__name__}"
            )
        
        # Validate it implements CleanerInterface
        if not issubclass(cleaner_class, CleanerInterface):
            raise CleanerRegistrationError(
                f"Class {cleaner_class.__name__} does not implement CleanerInterface"
            )
        
        # Create temporary instance to get domain
        try:
            temp_instance = cleaner_class(config={})
            domain = temp_instance.domain
        except Exception as e:
            raise CleanerRegistrationError(
                f"Failed to instantiate {cleaner_class.__name__}: {str(e)}"
            )
        
        # Check for duplicate domain
        if domain in self._cleaners:
            raise CleanerRegistrationError(
                f"Cleaner with domain '{domain}' already registered"
            )
        
        self._cleaners[domain] = cleaner_class
    
    def get_cleaner(
        self, domain: str, config: Optional[Dict[str, Any]] = None
    ) -> CleanerInterface:
        """Get instantiated cleaner.
        
        Args:
            domain: Cleaner domain
            config: Configuration dictionary
            
        Returns:
            Instantiated cleaner
            
        Raises:
            CleanerNotFoundError: If domain not registered
        """
        if domain not in self._cleaners:
            available = ", ".join(sorted(self._cleaners.keys()))
            raise CleanerNotFoundError(
                f"Cleaner domain '{domain}' not found. Available domains: {available}"
            )
        
        cleaner_class = self._cleaners[domain]
        config = config or {}
        return cleaner_class(config=config)
    
    def has_cleaner(self, domain: str) -> bool:
        """Check if cleaner is registered.
        
        Args:
            domain: Cleaner domain
            
        Returns:
            True if registered, False otherwise
        """
        return domain in self._cleaners
    
    def list_all(self) -> List[str]:
        """List all registered cleaner domains.
        
        Returns:
            List of domains
        """
        return list(self._cleaners.keys())
    
    def unregister(self, domain: str) -> None:
        """Unregister a cleaner.
        
        Args:
            domain: Cleaner domain to remove
        """
        if domain in self._cleaners:
            del self._cleaners[domain]
    
    def __repr__(self) -> str:
        """Get string representation.
        
        Returns:
            String representation showing registered domains
        """
        domains = ", ".join(sorted(self._cleaners.keys()))
        return f"CleanerRegistry(domains=[{domains}])"


from cortex.brain.tier1.orchestrators.cleaners.registry import (
    CleanerRegistrationError,
    CleanerNotFoundError,
)


__all__ = [
    "CleanerInterface",
    "CleanerRegistry",
    "Analysis",
    "Report",
    "RollbackResult",
    "CleanerRegistrationError",
    "CleanerNotFoundError",
]
