"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class IntentClassifier(Base): pass

class Classification(Base): pass

__all__ = ['IntentClassifier', 'Classification']