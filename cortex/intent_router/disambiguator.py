"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class IntentDisambiguator(Base): pass

class Disambiguation(Base): pass

__all__ = ['IntentDisambiguator', 'Disambiguation']