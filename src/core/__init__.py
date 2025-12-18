"""
CORTEX 4.0 Core Module

Provides core infrastructure for CORTEX 4.0:
- IDE detection and configuration management
- Environment context handling
- Cross-IDE compatibility layer

Version: 4.0
"""

from .ide_detector import IDEDetector, IDEType
from .config_manager import ConfigManager, CortexConfig

__all__ = [
    "IDEDetector",
    "IDEType",
    "ConfigManager",
    "CortexConfig",
]
