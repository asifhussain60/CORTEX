"""Module stub."""
from typing import Dict, Any; from dataclasses import dataclass, field

@dataclass
class Base:
    data: Dict[str, Any] = field(default_factory=dict)

class ScenarioLibrary(Base): pass

class Scenario(Base): pass


class ScenarioInput:
    """Class ScenarioInput."""
    def __init__(self): pass

__all__ = ['ScenarioLibrary', 'Scenario'    "ScenarioInput",
]