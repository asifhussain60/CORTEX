"""Import Path Updater

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ImportMapping:
    """Import path mapping."""
    old_path: str
    new_path: str

__all__ = ["ImportMapping"]
