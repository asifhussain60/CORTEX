"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class ConfidenceScorer(Base): pass

class Score(Base): pass

__all__ = ['ConfidenceScorer', 'Score']