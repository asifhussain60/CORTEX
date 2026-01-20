"""Module: intent_canonicalization.py."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ActionType(str, Enum):
    """Action types."""
    UNKNOWN = "unknown"


@dataclass
class CanonicalIntent:
    """Data class for CanonicalIntent."""
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtendedCanonicalIntent:
    """Data class for ExtendedCanonicalIntent."""
    data: Dict[str, Any] = field(default_factory=dict)


class IntentCanonicalizer:
    """Implementation of IntentCanonicalizer."""

    def __init__(self):
        """Initialize."""
        pass


class ExtendedIntentCanonicalizer:
    """Implementation of ExtendedIntentCanonicalizer."""

    def __init__(self):
        """Initialize."""
        pass


__all__ = [
    "IntentCanonicalizer",
    "ExtendedIntentCanonicalizer",
    "CanonicalIntent",
    "ExtendedCanonicalIntent",
    "ActionType",
]