"""Multimodal Processor

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class MultiModalIntentProcessor:
    """Process multimodal intents."""
    enabled: bool = True

__all__ = ["MultiModalIntentProcessor"]
