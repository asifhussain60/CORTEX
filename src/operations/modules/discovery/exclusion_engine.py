"""
Exclusion Engine - Pattern-Based File Filtering

Applies exclusion patterns from .gitignore, .cortexignore, and custom rules
to filter discovered files.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)


class ExclusionEngine:
    """
    Applies exclusion patterns to file paths.
    
    Supports:
    - .gitignore syntax
    - .cortexignore custom patterns
    - Glob patterns
    - Directory exclusions
    """
    
    # Default exclusion patterns
    DEFAULT_EXCLUDES = [
        ".git/",
        ".svn/",
        "__pycache__/",
        "node_modules/",
        ".venv/",
        "venv/",
        ".env/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        "dist/",
        "build/",
        "*.egg-info/",
    ]
    
    def __init__(self, project_root: Path):
        """
        Initialize exclusion engine.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.patterns: Set[str] = set(self.DEFAULT_EXCLUDES)
        self._load_gitignore()
        self._load_cortexignore()
        
        logger.debug(f"ExclusionEngine initialized with {len(self.patterns)} patterns")
    
    def _load_gitignore(self) -> None:
        """Load patterns from .gitignore file."""
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            self.patterns.add(line)
                logger.debug(f"Loaded {len(self.patterns)} patterns from .gitignore")
            except Exception as e:
                logger.warning(f"Failed to load .gitignore: {e}")
    
    def _load_cortexignore(self) -> None:
        """Load patterns from .cortexignore file."""
        cortexignore_path = self.project_root / ".cortexignore"
        if cortexignore_path.exists():
            try:
                with open(cortexignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            self.patterns.add(line)
                logger.debug(f"Loaded patterns from .cortexignore")
            except Exception as e:
                logger.warning(f"Failed to load .cortexignore: {e}")
    
    def should_exclude(self, path: Path, relative_path: Path) -> bool:
        """
        Check if path should be excluded.
        
        Args:
            path: Absolute path to check
            relative_path: Path relative to project root
        
        Returns:
            True if path should be excluded
        """
        import fnmatch
        
        # Convert to string for matching
        rel_str = str(relative_path).replace('\\', '/')
        path_parts = rel_str.split('/')
        
        for pattern in self.patterns:
            # Directory pattern (ends with /)
            if pattern.endswith('/'):
                dir_pattern = pattern.rstrip('/')
                # Check if any part of path matches directory pattern
                if dir_pattern in path_parts:
                    return True
            else:
                # File pattern - check against filename
                filename = path.name
                if fnmatch.fnmatch(filename, pattern):
                    return True
                # Also check against relative path
                if fnmatch.fnmatch(rel_str, pattern):
                    return True
        
        return False
    
    def add_pattern(self, pattern: str) -> None:
        """
        Add custom exclusion pattern.
        
        Args:
            pattern: Glob pattern or directory name
        """
        self.patterns.add(pattern)
        logger.debug(f"Added exclusion pattern: {pattern}")
    
    def add_patterns(self, patterns: List[str]) -> None:
        """
        Add multiple exclusion patterns.
        
        Args:
            patterns: List of patterns to add
        """
        for pattern in patterns:
            self.add_pattern(pattern)
    
    def get_patterns(self) -> List[str]:
        """
        Get all current exclusion patterns.
        
        Returns:
            List of exclusion patterns
        """
        return sorted(self.patterns)
