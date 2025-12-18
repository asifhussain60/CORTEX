"""
CORTEX 4.0 Logging Package

Provides standardized logging for all CORTEX components.
"""

from .logger import (
    setup_logger,
    get_logger,
    set_global_log_level,
    configure_logging_from_config
)

__all__ = [
    "setup_logger",
    "get_logger",
    "set_global_log_level",
    "configure_logging_from_config"
]
