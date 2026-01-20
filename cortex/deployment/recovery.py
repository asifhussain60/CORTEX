"""Recovery

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class Snapshot:
    """System snapshot."""
    snapshot_id: str
    timestamp: str
    data: dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

__all__ = ["Snapshot"]
