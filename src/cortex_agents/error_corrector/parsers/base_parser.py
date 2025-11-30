"""Base error parser interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseErrorParser(ABC):
    """Abstract base class for error parsers."""
    
    @abstractmethod
    def can_parse(self, output: str) -> bool:
        """
        Check if this parser can handle the error output.
        
        Args:
            output: Error output string
            
        Returns:
            True if this parser can handle the output
        """
        pass
    
    @abstractmethod
    def parse(self, output: str) -> Dict[str, Any]:
        """
        Parse error output to extract structured information.
        
        Args:
            output: Error output string
            
        Returns:
            Parsed error dict with keys:
            - file: str (file path)
            - line: int (line number)
            - category: str (error category)
            - message: str (error message)
            - traceback: List[str] (traceback lines)
            - code_snippet: str (problematic code)
            - Additional parser-specific fields
        """
        pass
