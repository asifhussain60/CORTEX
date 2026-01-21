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
        self._cleaners: Dict[str, CleanerInterface] = {}
    
    def register(self, cleaner_id: str, cleaner: CleanerInterface) -> None:
        """Register a cleaner.
        
        Args:
            cleaner_id: Unique cleaner ID
            cleaner: Cleaner instance
            
        Raises:
            ValueError: If cleaner_id already registered
        """
        if cleaner_id in self._cleaners:
            raise ValueError(f"Cleaner {cleaner_id} already registered")
        self._cleaners[cleaner_id] = cleaner
    
    def get(self, cleaner_id: str) -> Optional[CleanerInterface]:
        """Get registered cleaner.
        
        Args:
            cleaner_id: Cleaner ID
            
        Returns:
            Cleaner instance or None
        """
        return self._cleaners.get(cleaner_id)
    
    def list_cleaners(self) -> List[str]:
        """List all registered cleaner IDs.
        
        Returns:
            List of cleaner IDs
        """
        return list(self._cleaners.keys())
    
    def unregister(self, cleaner_id: str) -> None:
        """Unregister a cleaner.
        
        Args:
            cleaner_id: Cleaner ID to remove
        """
        if cleaner_id in self._cleaners:
            del self._cleaners[cleaner_id]


class CleanerRegistrationError(Exception):
    """Cleaner registration error."""
    pass


class CleanerNotFoundError(Exception):
    """Cleaner not found error."""
    pass


__all__ = [
    "CleanerInterface",
    "CleanerRegistry",
    "Analysis",
    "Report",
    "RollbackResult",
    "CleanerRegistrationError",
    "CleanerNotFoundError",
]
