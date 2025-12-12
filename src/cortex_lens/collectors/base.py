"""
Base protocol for data collectors.

All collector implementations must follow this protocol.
"""

from typing import Protocol, Dict, Any
from pathlib import Path


class BaseCollector(Protocol):
    """
    Protocol for data collectors.
    
    Collectors extract high-level repository information using
    analyzers and file scanning.
    
    Example:
        >>> collector = HealthCollector()
        >>> result = collector.collect(Path('/path/to/repo'))
        >>> print(result['total_files'])
    """
    
    @property
    def name(self) -> str:
        """
        Get the collector name.
        
        Returns:
            Collector identifier (e.g., 'health', 'architecture')
        """
        ...
    
    @property
    def description(self) -> str:
        """
        Get a brief description of what this collector extracts.
        
        Returns:
            Human-readable description
        """
        ...
    
    @property
    def required_for(self) -> list:
        """
        Get list of repo types that require this collector.
        
        Returns:
            List of repo type identifiers (e.g., ['fullstack_web', 'api_service'])
            Empty list means optional for all types.
        """
        ...
    
    def collect(self, repo_path: Path, analyzers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data from repository.
        
        Args:
            repo_path: Path to repository root
            analyzers: Dictionary of available analyzers by language
                      e.g., {'python': PythonAnalyzer(), 'csharp': CSharpAnalyzer()}
            
        Returns:
            Dictionary containing collected data.
            Schema varies by collector type.
            
        Raises:
            ValueError: If repo_path is invalid
            Exception: Collector-specific errors
        """
        ...
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate collected data structure.
        
        Args:
            data: Data dictionary from collect()
            
        Returns:
            True if data structure is valid
        """
        ...
