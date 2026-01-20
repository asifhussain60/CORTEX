"""Path Resolver - Utilities for resolving project and module paths.

Provides functions to resolve paths within the CORTEX project structure
and locate modules, configurations, and resources.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get the CORTEX project root directory.

    Returns:
        Path to project root.
    """
    # Look for cortex-config.yaml or setup.py to identify root
    current = Path(__file__).parent
    
    while current != current.parent:
        if (current / "cortex-config.yaml").exists() or (current / "setup.py").exists():
            return current
        current = current.parent
    
    # Fallback to current file's parent directory's parent (cortex/core -> project root)
    return Path(__file__).parent.parent.parent


def resolve_path(path_str: str, relative_to: Optional[Path] = None) -> Path:
    """Resolve a path string to an absolute Path.

    Args:
        path_str: Path string (can be absolute or relative).
        relative_to: Base path for relative resolution (defaults to project root).

    Returns:
        Resolved absolute Path.
    """
    if relative_to is None:
        relative_to = get_project_root()
    
    path = Path(path_str)
    
    if path.is_absolute():
        return path
    else:
        return relative_to / path


def get_cortex_module_path() -> Path:
    """Get path to cortex module.

    Returns:
        Path to cortex package.
    """
    return get_project_root() / "cortex"


def get_cortex_brain_path() -> Path:
    """Get path to cortex_brain module.

    Returns:
        Path to cortex_brain package.
    """
    return get_project_root() / "cortex_brain"


def get_config_path() -> Path:
    """Get path to configuration directory.

    Returns:
        Path to config directory.
    """
    return get_project_root() / "config"


def get_data_path() -> Path:
    """Get path to data directory.

    Returns:
        Path to data directory.
    """
    return get_project_root() / "data"


def get_tests_path() -> Path:
    """Get path to tests directory.

    Returns:
        Path to tests directory.
    """
    return get_project_root() / "tests"


def get_docs_path() -> Path:
    """Get path to docs directory.

    Returns:
        Path to docs directory.
    """
    return get_project_root() / "docs"


__all__ = [
    "get_project_root",
    "resolve_path",
    "get_cortex_module_path",
    "get_cortex_brain_path",
    "get_config_path",
    "get_data_path",
    "get_tests_path",
    "get_docs_path",
]
