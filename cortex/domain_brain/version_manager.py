"""Domain brain module."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class VersionConflict:
    """Data class."""
    data: Dict[str, Any] = field(default_factory=dict)


class VersionManager:
    """Class VersionManager."""
    def __init__(self): pass


class Version:
    """Class Version."""
    def __init__(self): pass


__all__ = [
    "VersionManager",
    "Version",
    "VersionConflict",
]