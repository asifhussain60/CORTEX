"""
Dashboard collectors package.
"""

from .universal_collector_base import UniversalCollectorBase
from .architecture_collector import (
    ArchitectureCollector,
    ArchitectureData
)

__all__ = [
    'UniversalCollectorBase',
    'ArchitectureCollector',
    'ArchitectureData'
]
