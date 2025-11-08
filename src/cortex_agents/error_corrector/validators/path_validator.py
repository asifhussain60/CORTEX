"""Validate file paths for error correction."""

from pathlib import Path
from typing import List


class PathValidator:
    """Validator for protected paths that should not be auto-fixed."""
    
    def __init__(self, protected_paths: List[str]):
        """
        Initialize path validator.
        
        Args:
            protected_paths: List of protected directory paths
        """
        self.protected_paths = protected_paths or []
    
    def is_protected(self, file_path: str) -> bool:
        """
        Check if file path is in protected directory.
        
        Protected paths:
        - CORTEX/tests/ (system health tests)
        - CORTEX/src/cortex_agents/ (core agents)
        - cortex-brain/ (knowledge base)
        
        Args:
            file_path: Path to check
            
        Returns:
            True if path is protected and should not be auto-fixed
        """
        path = Path(file_path)
        
        for protected in self.protected_paths:
            protected_path = Path(protected)
            try:
                # Check if file_path is relative to protected_path
                path.resolve().relative_to(protected_path.resolve())
                return True
            except ValueError:
                # Not relative, continue checking
                continue
        
        return False
