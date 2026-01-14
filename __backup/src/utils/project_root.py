"""
Project Root Utility (CORE-005 Compliance)

Provides cross-platform project root resolution.
Ensures path portability across MAC/WIN/LINUX.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Optional


def get_project_root(marker_file: str = ".git") -> Path:
    """
    Get the project root directory in a cross-platform way.
    
    Args:
        marker_file: File/directory that marks the project root (default: .git)
        
    Returns:
        Path: Absolute path to project root
        
    Raises:
        RuntimeError: If project root cannot be determined
        
    Examples:
        >>> root = get_project_root()
        >>> cortex_brain = root / "cortex-brain"
        >>> config = root / "cortex-brain" / "config"
    """
    current = Path(__file__).resolve()
    
    # Walk up the directory tree looking for marker
    for parent in [current, *current.parents]:
        if (parent / marker_file).exists():
            return parent
    
    # Fallback: Use environment variable if set
    import os
    if env_root := os.getenv("CORTEX_PROJECT_ROOT"):
        return Path(env_root)
    
    # Last resort: Assume we're in src/utils and go up 2 levels
    return Path(__file__).resolve().parent.parent.parent


def get_cortex_brain_root() -> Path:
    """Get cortex-brain directory (shortcut)"""
    return get_project_root() / "cortex-brain"


def get_scripts_dir() -> Path:
    """Get scripts directory (shortcut)"""
    return get_project_root() / "scripts"


def get_src_dir() -> Path:
    """Get src directory (shortcut)"""
    return get_project_root() / "src"


def ensure_portable_path(path_str: str) -> Path:
    """
    Convert any path string to portable Path object.
    
    Args:
        path_str: Path string (may be absolute or relative)
        
    Returns:
        Path: Portable Path object
        
    Warning:
        If path_str contains hardcoded absolute paths like /Users/ or C:\\,
        they will be returned as-is but flagged in logs.
    """
    path = Path(path_str)
    
    # Detect hardcoded absolute paths (CORE-005 violation)
    if path.is_absolute():
        import logging
        logging.warning(
            f"CORE-005: Hardcoded absolute path detected: {path_str}. "
            f"Consider using get_project_root() for portability."
        )
    
    return path
