# AC_START: AC-PHASE58-S1-003
# Description: RepositoryWalker Concrete Implementation
# Authority: CORE-008 TDD, CORE-011 type hints
# Stage: S1 - GREEN phase implementation

import asyncio
from pathlib import Path
from typing import Dict, Optional, Callable
import fnmatch
import time

from cortex.intelligence.crawler.base import AsyncRepositoryCrawler, CrawlerConfig, FileMetadata


class RepositoryWalker(AsyncRepositoryCrawler):
    """
    Concrete implementation of AsyncRepositoryCrawler.
    
    Traverses repository directory structure asynchronously with:
    - File filtering (include/exclude patterns)
    - Gitignore respect
    - Concurrent task management
    - Error resilience
    """

    def __init__(
        self,
        config: Optional[CrawlerConfig] = None,
        include_patterns: Optional[list] = None,
        exclude_patterns: Optional[list] = None,
    ):
        """
        Initialize RepositoryWalker.
        
        Args:
            config: Crawler configuration
            include_patterns: Override include patterns
            exclude_patterns: Override exclude patterns
        """
        super().__init__(config)
        
        if include_patterns:
            self.config.include_patterns = include_patterns
        if exclude_patterns:
            self.config.exclude_patterns = exclude_patterns
        
        self.gitignore_patterns = []
        self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load .gitignore patterns if file exists."""
        try:
            gitignore_path = Path(".gitignore")
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    self.gitignore_patterns = [
                        line.strip() for line in f if line.strip() and not line.startswith("#")
                    ]
        except Exception:
            pass  # Silently continue if gitignore cannot be read

    def _should_include_file(self, file_path: str) -> bool:
        """
        Determine if file should be included based on patterns.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file should be included
        """
        path_obj = Path(file_path)
        
        # Check gitignore
        if self.config.enable_gitignore:
            for pattern in self.gitignore_patterns:
                if fnmatch.fnmatch(str(file_path), pattern):
                    return False
        
        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(path_obj.name, pattern):
                return False
        
        # Check include patterns
        if self.config.include_patterns:
            matches = any(
                fnmatch.fnmatch(path_obj.name, pattern)
                for pattern in self.config.include_patterns
            )
            return matches
        
        return True

    async def crawl(self, path: str, context: Optional[Dict] = None) -> None:
        """
        Crawl repository and discover files.
        
        Args:
            path: Root path to crawl
            context: Optional analysis context
        """
        await self.start()
        
        try:
            root_path = Path(path)
            
            # Handle non-existent path gracefully
            if not root_path.exists():
                self.errors.append(f"Path does not exist: {path}")
                return
            
            # Traverse directory tree
            await self._traverse_directory(root_path)
        
        except Exception as e:
            self.errors.append(f"Crawl error: {str(e)}")
        
        finally:
            await self.stop()

    async def _traverse_directory(self, root_path: Path, max_depth: int = 50) -> None:
        """
        Recursively traverse directory structure.
        
        Args:
            root_path: Path to traverse
            max_depth: Maximum recursion depth
        """
        if max_depth <= 0:
            return
        
        try:
            entries = list(root_path.iterdir())
        except (PermissionError, OSError):
            return  # Skip inaccessible directories
        
        for entry in entries:
            if not self.is_running:
                break
            
            try:
                if entry.is_file():
                    if self._should_include_file(str(entry)):
                        metadata = FileMetadata(
                            path=str(entry),
                            size_bytes=entry.stat().st_size,
                            relative_path=str(entry.relative_to(root_path)),
                            file_type=entry.suffix,
                            discovered_at=time.time(),
                        )
                        
                        await self.on_file_discovered(str(entry), metadata)
                        self.files_discovered += 1
                
                elif entry.is_dir():
                    await self._traverse_directory(entry, max_depth - 1)
            
            except (PermissionError, OSError):
                continue  # Skip problematic entries

    async def on_file_discovered(self, file_path: str, metadata: FileMetadata) -> None:
        """
        Handle discovered file (override in subclasses).
        
        Args:
            file_path: Path to discovered file
            metadata: File metadata
        """
        pass  # Minimal implementation - subclasses override

# AC_COMPLETE: AC-PHASE58-S1-003 ✅
# Implementation: RepositoryWalker with filtering
# Status: READY FOR TESTING
