"""
Cache Cleaner - Group 1 cleanup (cache directories).

Handles:
- Python cache (__pycache__/, *.pyc, .pytest_cache/, .mypy_cache/)
- Generic cache directories
- Sweeper/distributed caching artifacts
- Temporary directories
- Empty directories after cleanup

Priority: HIGH (safe, fast, high impact)
Expected: ~10s execution, 1GB+ freed

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from src.orchestrators.cleanup.cleanup_engine import CleanupEngine


logger = logging.getLogger(__name__)


class CacheCleaner:
    """
    Cache cleanup (Group 1) - Python cache, generic cache, temp dirs.
    
    Categories:
    - python_cache: __pycache__/, *.pyc, .pytest_cache/, .mypy_cache/
    - cache: Generic cache directories
    - sweeper: Distributed caching artifacts
    - temp_directories: Temporary build artifacts
    - empty_directories: Empty folders after cleanup
    """
    
    CATEGORIES = [
        "python_cache",
        "cache",
        "sweeper",
        "temp_directories",
        "empty_directories"
    ]
    
    def __init__(
        self,
        workspace_root: Path,
        rules_path: Path,
        config: Dict[str, Any]
    ):
        """
        Initialize cache cleaner.
        
        Args:
            workspace_root: Workspace root directory
            rules_path: Path to cleanup-rules.yaml
            config: Orchestrator configuration
        """
        self.workspace_root = workspace_root
        self.rules_path = rules_path
        self.config = config
        
        # Initialize cleanup engine
        self.cleanup_engine = CleanupEngine(workspace_root, rules_path)
        
        logger.info("CacheCleaner initialized")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute cache cleanup.
        
        Returns:
            Cleanup result dictionary
        """
        logger.info("Starting cache cleanup (Group 1)")
        
        # Use cleanup engine to process cache categories
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        
        logger.info(
            f"Cache cleanup complete: {result['statistics']['files_deleted']} files, "
            f"{result['statistics']['space_freed_mb']:.2f} MB freed"
        )
        
        return result
