"""Response Templates

Author: CORTEX Framework
"""

from enum import Enum

class VariableType(str, Enum):
    """Template variable types."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"



from typing import Dict

class ResponseTemplate:
    """Response template."""
    
    def render(self, variables: Dict[str, VariableType]) -> str:
        """Render template."""
        return ""

__all__ = ["VariableType", "ResponseTemplate"]
