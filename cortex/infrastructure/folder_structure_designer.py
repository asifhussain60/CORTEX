"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class FolderStructureDesigner(Base): pass

class Structure(Base): pass

__all__ = ['FolderStructureDesigner', 'Structure']