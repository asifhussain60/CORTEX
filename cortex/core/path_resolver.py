"""
Path Resolver - Cross-Platform Path Resolution

Provides portable path resolution without hardcoded paths.
All path operations should go through this module.

NEVER use hardcoded paths like:
- /Users/<username>/Projects/...
- /home/<username>/...
- C:\\Users\\<username>\\...

ALWAYS use:
- get_project_root()
- resolve_path("cortex", "intelligence")
- cortex.intelligence_path()  ← canonical: cortex/intelligence/

Note: cortex/intelligence/ was dissolved into cortex/intelligence/ (Phase 03).
All tier-based paths now map to cortex-registry/ (governance) or cortex/intelligence/ (code).

Author: Asif Hussain
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
        *parts: Path components (e.g., "cortex", "intelligence")

    Returns:
        Absolute Path object

    Example:
        >>> resolve_path("cortex", "intelligence")
        Path("/path/to/project/cortex/intelligence")
    """
    return get_project_root().joinpath(*parts)


def intelligence_path() -> Path:
    """Get path to cortex/intelligence directory (canonical since Phase 03)."""
    return resolve_path("cortex", "intelligence")


# Backward-compat alias (Phase 105)
cortex_intelligence_path = intelligence_path


def tier_path(tier: int) -> Path:
    """Get path to cortex-registry governance tier directory.

    Tier mapping (post Phase 03 migration):
      0 → cortex-registry/core/tier0-skull/
      1 → cortex-registry/core/tier1-project/
      2 → cortex-registry/core/tier2-conventions/
      3 → cortex-registry/knowledge-base/
    """
    tier_map = {
        0: resolve_path("cortex-registry", "core", "tier0-skull"),
        1: resolve_path("cortex-registry", "core", "tier1-project"),
        2: resolve_path("cortex-registry", "core"),
        3: resolve_path("cortex-registry", "knowledge-base"),
    }
    if tier not in tier_map:
        raise ValueError(f"Invalid tier: {tier}. Must be 0, 1, 2, or 3.")
    return tier_map[tier]


def audit_logs_path() -> Path:
    """Get path to audit logs directory."""
    return resolve_path(".cortex-runtime", "logs")


def config_path() -> Path:
    """Get path to config directory."""
    return resolve_path("cortex-registry", "config")


def reset_project_root() -> None:
    """Reset cached project root (for testing)."""
    global _PROJECT_ROOT
    _PROJECT_ROOT = None
