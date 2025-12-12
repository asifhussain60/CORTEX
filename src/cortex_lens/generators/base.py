"""
Base protocol for content generators.

All generator implementations must follow this protocol.
"""

from typing import Protocol, Dict, Any
from pathlib import Path


class BaseGenerator(Protocol):
    """
    Protocol for content generators.
    
    Generators transform collected data into dashboard content
    (HTML, narratives, JSON).
    
    Example:
        >>> generator = NarrativeGenerator()
        >>> narrative = generator.generate(collected_data)
        >>> print(narrative)
    """
    
    @property
    def name(self) -> str:
        """
        Get the generator name.
        
        Returns:
            Generator identifier (e.g., 'narrative', 'dashboard')
        """
        ...
    
    @property
    def description(self) -> str:
        """
        Get a brief description of what this generator creates.
        
        Returns:
            Human-readable description
        """
        ...
    
    def generate(self, data: Dict[str, Any], output_path: Path = None) -> Any:
        """
        Generate content from collected data.
        
        Args:
            data: Dictionary of collected repository data
            output_path: Optional output file path
            
        Returns:
            Generated content (type varies by generator):
                - NarrativeGenerator: str (markdown text)
                - DashboardBuilder: Path (dashboard HTML path)
                - DataInjector: Dict (injected data)
                
        Raises:
            ValueError: If data structure is invalid
            IOError: If output_path write fails
        """
        ...
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data structure.
        
        Args:
            data: Data dictionary to validate
            
        Returns:
            True if data structure is compatible
        """
        ...
