"""
Project Root Detection Utility for CORTEX.

Provides portable path resolution across different installations.
Enforces SKULL rule: PATH_PORTABILITY

Author: Asif Hussain
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Detect CORTEX project root dynamically.
    
    Strategy:
    1. Check for marker files (cortex.config.json, .github/copilot-instructions.md)
    2. Walk up from current file until found
    3. Cache result for performance
    
    Returns:
        Path object pointing to project root
        
    Raises:
        RuntimeError: If project root cannot be detected
    """
    # Start from this file's location
    current = Path(__file__).resolve()
    
    # Marker files that identify CORTEX root
    markers = [
        "cortex.config.json",
        ".github/copilot-instructions.md",
        "cortex-brain",
        "src/main.py"
    ]
    
    # Walk up directory tree
    for parent in [current.parent] + list(current.parents):
        # Check if any marker exists
        if any((parent / marker).exists() for marker in markers):
            return parent
    
    # Fallback: assume we're in src/utils, go up 2 levels
    fallback = current.parent.parent
    if (fallback / "cortex.config.json").exists():
        return fallback
    
    raise RuntimeError(
        "Cannot detect CORTEX project root. "
        "Ensure cortex.config.json exists in project root."
    )


def get_brain_dir() -> Path:
    """Get cortex-brain directory path."""
    return get_project_root() / "cortex-brain"


def get_src_dir() -> Path:
    """Get src directory path."""
    return get_project_root() / "src"


def get_toolkit_dir() -> Path:
    """Get cortex-toolkit directory path."""
    return get_project_root() / "cortex-toolkit"


def get_scripts_dir() -> Path:
    """Get scripts directory path."""
    return get_project_root() / "scripts"


def get_templates_dir() -> Path:
    """Get templates directory path."""
    return get_project_root() / "templates"


def resolve_path(relative_path: str) -> Path:
    """
    Resolve a relative path from project root.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute Path object
    """
    return get_project_root() / relative_path


# Cache for performance
_PROJECT_ROOT: Optional[Path] = None


def cached_project_root() -> Path:
    """Get cached project root (faster for repeated calls)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        _PROJECT_ROOT = get_project_root()
    return _PROJECT_ROOT


if __name__ == "__main__":
    # Test detection
    print(f"Project root: {get_project_root()}")
    print(f"Brain dir: {get_brain_dir()}")
    print(f"Src dir: {get_src_dir()}")
    print(f"Toolkit dir: {get_toolkit_dir()}")
