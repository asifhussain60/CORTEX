"""
CORTEX 4.0 Configuration Package

Provides centralized configuration management for all CORTEX components.
"""

from .config_manager import (
    ConfigManager,
    CortexConfig,
    PathConfig,
    BrainConfig,
    IDEConfig,
    LoggingConfig,
    IDEType,
    Environment,
    get_config_manager,
    get_config
)

# Singleton config instance for backward compatibility
# Many legacy modules import: from src.config import config
config = get_config()

__all__ = [
    "ConfigManager",
    "CortexConfig",
    "PathConfig",
    "BrainConfig",
    "IDEConfig",
    "LoggingConfig",
    "IDEType",
    "Environment",
    "get_config_manager",
    "get_config",
    "config"  # Singleton instance
]
