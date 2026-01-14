"""
Path Resolver - Cross-Platform Path Resolution

Provides portable path resolution without hardcoded paths.
All path operations should go through this module.

NEVER use hardcoded paths like:
- /Users/asifhussain/PROJECTS/CORTEX
- C:\\Users\\...

ALWAYS use:
- get_project_root()
- resolve_path("cortex-brain/tier0")

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import Optional


_PROJECT_ROOT: Optional[Path] = None


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Resolution order:
    1. CORTEX_ROOT environment variable
    2. Git root (if in git repo)
    3. Current working directory
    
    Returns:
        Path to project root
    """
    global _PROJECT_ROOT
    
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT
    
    # Check environment variable first
    env_root = os.environ.get("CORTEX_ROOT")
    if env_root:
        _PROJECT_ROOT = Path(env_root)
        return _PROJECT_ROOT
    
    # Try to find git root
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            _PROJECT_ROOT = parent
            return _PROJECT_ROOT
    
    # Fall back to current directory
    _PROJECT_ROOT = Path.cwd()
    return _PROJECT_ROOT


def resolve_path(*parts: str) -> Path:
    """
    Resolve a path relative to project root.
    
    Args:
        *parts: Path components (e.g., "cortex-brain", "tier0")
    
    Returns:
        Absolute Path object
    
    Example:
        >>> resolve_path("cortex-brain", "tier0", "governance")
        Path("/path/to/project/cortex-brain/tier0/governance")
    """
    return get_project_root().joinpath(*parts)


def cortex_brain_path() -> Path:
    """Get path to cortex-brain directory."""
    return resolve_path("cortex-brain")


def tier_path(tier: int) -> Path:
    """Get path to a specific tier directory."""
    if tier not in (0, 1, 2, 3):
        raise ValueError(f"Invalid tier: {tier}. Must be 0, 1, 2, or 3.")
    return resolve_path("cortex-brain", f"tier{tier}")


def audit_logs_path() -> Path:
    """Get path to audit logs directory."""
    return resolve_path("cortex-brain", "audit-logs")


def config_path() -> Path:
    """Get path to config directory."""
    return resolve_path("cortex-brain", "config")


def reset_project_root():
    """Reset cached project root (for testing)."""
    global _PROJECT_ROOT
    _PROJECT_ROOT = None
