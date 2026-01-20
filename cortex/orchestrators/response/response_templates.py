"""Response Templates

Author: CORTEX Framework
"""

from enum import Enum

class VariableType(str, Enum):
    """Template variable types."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"

__all__ = ["VariableType"]
