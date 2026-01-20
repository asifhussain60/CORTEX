"""Folder Migration Script

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class FileIntegrityRecord:
    """File integrity record."""
    file_path: str
    checksum: str
    verified: bool = False

__all__ = ["FileIntegrityRecord"]
