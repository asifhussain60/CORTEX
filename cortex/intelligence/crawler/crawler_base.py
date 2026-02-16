# AC_START: AC-PHASE58-S1-002
# Description: AsyncRepositoryCrawler Base Class
# Authority: CORE-008 TDD, CORE-011 type hints, CORE-012 docstrings
# Stage: S1 - GREEN phase implementation

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CrawlerConfig:
    """Configuration for async crawler."""
    max_concurrent_tasks: int = 10
    include_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.ts", "*.cs"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pyc", ".git/*", "__pycache__/*"])
    timeout_seconds: float = 30.0
    enable_gitignore: bool = True


@dataclass
class FileMetadata:
    """Metadata about discovered file."""
    path: str
    size_bytes: int
    relative_path: str
    file_type: str
    discovered_at: float = 0.0


class AsyncRepositoryCrawler(ABC):
    """
    Abstract base class for async repository crawlers.

    Provides foundation for non-blocking file system traversal
    with filtering, progress tracking, and cancellation support.
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        Initialize AsyncRepositoryCrawler.

        Args:
            config: Crawler configuration
        """
        self.config = config or CrawlerConfig()
        self.is_running = False
        self.files_discovered = 0
        self.errors: List[str] = []

    @abstractmethod
    async def crawl(self, path: str, context: Optional[Dict] = None) -> None:
        """
        Main crawl method - traverse repository and discover files.

        Args:
            path: Root path to crawl
            context: Optional analysis context
        """
        pass

    @abstractmethod
    async def on_file_discovered(self, file_path: str, metadata: FileMetadata) -> None:
        """
        Callback when file is discovered.

        Args:
            file_path: Path to discovered file
            metadata: File metadata
        """
        pass

    async def start(self) -> None:
        """Start crawler lifecycle."""
        self.is_running = True
        self.errors.clear()

    async def stop(self) -> None:
        """Stop crawler lifecycle."""
        self.is_running = False

    def get_status(self) -> Dict[str, Any]:
        """Get crawler status."""
        return {
            "is_running": self.is_running,
            "files_discovered": self.files_discovered,
            "errors": len(self.errors),
        }

# AC_COMPLETE: AC-PHASE58-S1-002 ✅
# Implementation: AsyncRepositoryCrawler base class
# Status: READY FOR TESTING
