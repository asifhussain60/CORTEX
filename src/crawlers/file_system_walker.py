"""
FileSystemWalker component for traversing directory structures.

Provides file system traversal with filtering and exclusion patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import List, Set, Dict


class FileSystemWalker:
    """
    Walk directory trees and collect file paths with filtering.
    
    Supports:
    - Extension-based filtering
    - Directory exclusion patterns
    - Recursive traversal
    """
    
    def __init__(self):
        """Initialize FileSystemWalker."""
        self.extensions: Set[str] = set()
        self.exclusions: Set[str] = set()
    
    def set_extensions(self, extensions: List[str]) -> None:
        """
        Set file extensions to filter.
        
        Args:
            extensions: List of extensions to include (e.g., ['.py', '.js'])
        """
        self.extensions = set(extensions)
    
    def set_exclusions(self, exclusions: List[str]) -> None:
        """
        Set directory names to exclude from traversal.
        
        Args:
            exclusions: List of directory names to exclude (e.g., ['.git', 'node_modules'])
        """
        self.exclusions = set(exclusions)
    
    def walk(self, root_path: str) -> List[Path]:
        """
        Walk directory tree and collect file paths.
        
        Args:
            root_path: Root directory to start traversal
            
        Returns:
            List of file paths found
        """
        root = Path(root_path)
        if not root.exists():
            return []
        
        files = []
        if root.is_file():
            if self._should_include(root):
                files.append(root)
        else:
            for item in root.rglob('*'):
                if item.is_file() and self._should_include(item) and not self._is_excluded(item):
                    files.append(item)
        
        return files
    
    def _should_include(self, path: Path) -> bool:
        """Check if file should be included based on extension filter."""
        if not self.extensions:
            return True
        return path.suffix in self.extensions
    
    def _is_excluded(self, path: Path) -> bool:
        """
        Check if file is in an excluded directory.
        
        Args:
            path: File path to check
            
        Returns:
            True if file is in an excluded directory
        """
        if not self.exclusions:
            return False
        return any(part in self.exclusions for part in path.parts)
