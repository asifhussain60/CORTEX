"""
Dashboard collectors package.
"""

from .universal_collector_base import UniversalCollectorBase
from .architecture_collector_v2 import (
    ArchitectureCollectorV2,
    ArchitectureData
)

__all__ = [
    'UniversalCollectorBase',
    'ArchitectureCollectorV2',
    'ArchitectureData'
]
