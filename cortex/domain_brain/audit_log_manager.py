"""Audit Log Manager

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ArchivalStats:
    """Archival statistics."""
    archived_count: int = 0
    total_size_bytes: int = 0

__all__ = ["ArchivalStats"]
