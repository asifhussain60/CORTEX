"""Domain brain module."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class LockViolation:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


class OptimisticLocker:
    """Class OptimisticLocker."""
    def __init__(self): pass


class Lock:
    """Class Lock."""
    def __init__(self): pass


__all__ = [
    "OptimisticLocker",
    "Lock",
    "LockViolation",
]