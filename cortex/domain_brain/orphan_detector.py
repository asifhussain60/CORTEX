"""Domain brain module."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class OrphanData:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrphanReport:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


class OrphanDetector:
    """Class OrphanDetector."""
    def __init__(self): pass


__all__ = [
    "OrphanDetector",
    "OrphanData",
    "OrphanReport",
]