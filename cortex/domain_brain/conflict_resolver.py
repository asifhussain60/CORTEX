"""Domain brain module."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Conflict:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


class ConflictResolver:
    """Class ConflictResolver."""
    def __init__(self): pass


__all__ = [
    "ConflictResolver",
    "Conflict",
    "Resolution",
]