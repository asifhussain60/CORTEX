"""LENS Integration

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class LENSIntegrationLayer:
    """LENS integration layer."""
    enabled: bool = True

__all__ = ["LENSIntegrationLayer"]
