"""Version Manager

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class VersionedDomainManager:
    """Manage versioned domains."""
    current_version: str = "1.0.0"

__all__ = ["VersionedDomainManager"]
