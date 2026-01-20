"""Domain brain module."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class AdapterConfig:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


class DomainAdapter:
    """Class DomainAdapter."""
    def __init__(self): pass



class ASTAdapter:
    """Class ASTAdapter."""
    def __init__(self): pass

__all__ = [
    "DomainAdapter",
    "AdapterConfig",
    "AdapterResult",
    "ASTAdapter",
]