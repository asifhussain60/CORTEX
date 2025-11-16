"""Base fix strategy interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseFixStrategy(ABC):
    """Abstract base class for fix strategies."""
    
    @abstractmethod
    def can_fix(self, parsed_error: Dict[str, Any], fix_pattern: Dict[str, Any]) -> bool:
        """
        Check if this strategy can fix the error.
        
        Args:
            parsed_error: Parsed error information
            fix_pattern: Fix pattern from pattern store
            
        Returns:
            True if this strategy can apply the fix
        """
        pass
    
    @abstractmethod
    def apply_fix(
        self, 
        parsed_error: Dict[str, Any], 
        fix_pattern: Dict[str, Any],
        file_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Apply the fix to the code.
        
        Args:
            parsed_error: Parsed error information
            fix_pattern: Fix pattern to apply
            file_path: Optional file path to fix
            
        Returns:
            Fix result dict with keys:
            - success: bool
            - message: str
            - changes: List[str] (description of changes)
            - fixed_content: Optional[str] (new file content)
        """
        pass
