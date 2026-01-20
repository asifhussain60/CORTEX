"""Intent Classifier

Author: CORTEX Framework
"""

from enum import Enum

class IntentCategory(str, Enum):
    """Intent categories."""
    QUERY = "query"
    COMMAND = "command"
    NAVIGATION = "navigation"

__all__ = ["IntentCategory"]
