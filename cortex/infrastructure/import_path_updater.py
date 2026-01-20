"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class ImportPathUpdater(Base): pass

class PathUpdate(Base): pass

__all__ = ['ImportPathUpdater', 'PathUpdate']