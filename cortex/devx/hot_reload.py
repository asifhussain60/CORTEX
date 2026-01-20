"""Hot Reload

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import List

@dataclass
class FileWatcher:
    """File system watcher."""
    paths: List[str] = None
    
    def __post_init__(self):
        if self.paths is None:
            self.paths = []
    
    def watch(self) -> None:
        """Start watching."""
        pass

__all__ = ["FileWatcher"]
