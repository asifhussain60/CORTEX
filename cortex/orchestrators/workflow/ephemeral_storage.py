"""
EphemeralStorage — Phase 45 Stage 3.

.temp/ directory management with auto-cleanup.

AC_START: AC-WORKFLOW-EPHEMERAL-20260223T000000Z
Phase: 45 | Stage: 3 | Priority: P0
Description: GREEN phase implementation for ephemeral storage
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import shutil
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


logger = logging.getLogger(__name__)


# =============================================================================
# DIRECTORY MANAGEMENT
# =============================================================================
def ensure_temp_directory(base_path: Path) -> Path:
    """Ensure .temp/ directory exists under base_path.
    
    Args:
        base_path: Base directory path.
    
    Returns:
        Path to .temp/ directory.
    """
    temp_dir = base_path / ".temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured temp directory: {temp_dir}")
    return temp_dir


def cleanup_temp_directory(base_path: Path) -> None:
    """Remove .temp/ directory and all contents.
    
    Args:
        base_path: Base directory path.
    """
    temp_dir = base_path / ".temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        logger.info(f"Cleaned up temp directory: {temp_dir}")
    else:
        logger.debug(f"Temp directory does not exist: {temp_dir}")


# =============================================================================
# EPHEMERAL STORAGE
# =============================================================================
class EphemeralStorage:
    """Manages ephemeral file storage in .temp/ directory.
    
    Provides context manager interface for automatic cleanup.
    
    Example:
        >>> with EphemeralStorage() as storage:
        ...     storage.write_file("data.txt", "content")
        ...     content = storage.read_file("data.txt")
        # .temp/ automatically cleaned up after context
    """
    
    def __init__(self, base_path: Optional[Path] = None) -> None:
        """Initialize ephemeral storage.
        
        Args:
            base_path: Base directory for .temp/. Defaults to current directory.
        """
        self.base_path = base_path or Path.cwd()
        self._temp_dir: Optional[Path] = None
    
    def get_temp_dir(self) -> Path:
        """Get .temp/ directory, creating if necessary.
        
        Returns:
            Path to .temp/ directory.
        """
        if self._temp_dir is None:
            self._temp_dir = ensure_temp_directory(self.base_path)
        return self._temp_dir
    
    def write_file(self, filename: str, content: str) -> Path:
        """Write file to .temp/ directory.
        
        Args:
            filename: Filename (relative to .temp/).
            content: File content.
        
        Returns:
            Path to written file.
        """
        temp_dir = self.get_temp_dir()
        file_path = temp_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        logger.debug(f"Wrote file: {file_path}")
        return file_path
    
    def read_file(self, filename: str) -> str:
        """Read file from .temp/ directory.
        
        Args:
            filename: Filename (relative to .temp/).
        
        Returns:
            File content.
        
        Raises:
            FileNotFoundError: If file does not exist.
        """
        temp_dir = self.get_temp_dir()
        file_path = temp_dir / filename
        content = file_path.read_text()
        logger.debug(f"Read file: {file_path}")
        return content
    
    def cleanup(self) -> None:
        """Remove .temp/ directory and all contents."""
        cleanup_temp_directory(self.base_path)
        self._temp_dir = None
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with automatic cleanup."""
        self.cleanup()
        return False


# =============================================================================
# AC_COMPLETE: AC-WORKFLOW-EPHEMERAL-20260223T000000Z (GREEN phase implementation)
# =============================================================================
