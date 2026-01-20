"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class FolderMigrationScript(Base): pass

class MigrationPlan(Base): pass

__all__ = ['FolderMigrationScript', 'MigrationPlan']