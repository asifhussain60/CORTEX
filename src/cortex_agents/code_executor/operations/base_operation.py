"""Base operation interface for file operations."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseOperation(ABC):
    """Abstract base class for file operations."""
    
    def __init__(self, backup_manager=None, validator=None):
        """
        Initialize operation.
        
        Args:
            backup_manager: BackupManager instance for file backups
            validator: SyntaxValidator instance for validation
        """
        self.backup_manager = backup_manager
        self.validator = validator
    
    @abstractmethod
    def execute(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the operation.
        
        Args:
            file_path: Path to operate on
            context: Operation context (content, options, etc.)
        
        Returns:
            Operation result dictionary with keys:
            - success: bool
            - message: str
            - file_path: str (optional)
            - operation: str (optional)
            - error: str (optional)
        """
        pass
    
    @abstractmethod
    def get_operation_type(self) -> str:
        """
        Get the operation type name.
        
        Returns:
            Operation type (e.g., "create", "edit", "delete")
        """
        pass
