"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class MultimodalProcessor(Base): pass

class ProcessedInput(Base): pass

__all__ = ['MultimodalProcessor', 'ProcessedInput']