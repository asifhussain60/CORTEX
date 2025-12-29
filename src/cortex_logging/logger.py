"""
CORTEX 4.0 Logging System

Provides standardized logging for all CORTEX components with:
- Console and file output
- Orchestrator-specific log files
- Configurable log levels
- Rotation and archival
- Structured logging support

Design Principles:
1. Single logger setup function for consistency
2. Automatic log directory creation
3. Separate log files per orchestrator
4. Console output for development, file for production
5. Integration with ConfigManager for settings
"""

import logging as stdlib_logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    log_dir: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> stdlib_logging.Logger:
    """
    Set up standardized logger for CORTEX components.
    
    Args:
        name: Logger name (usually orchestrator/module name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: logs/)
        console_output: Enable console output
        file_output: Enable file output
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = setup_logger("planning_orchestrator")
        >>> logger.info("Phase 1 started")
        >>> logger.error("Validation failed", exc_info=True)
    """
    # Get or create logger
    logger = stdlib_logging.getLogger(name)
    logger.setLevel(getattr(stdlib_logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Formatter
    formatter = stdlib_logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = stdlib_logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(stdlib_logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler (with rotation)
    if file_output:
        # Default log directory
        if log_dir is None:
            log_dir = Path("logs")
        
        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file path
        log_file = log_dir / f"{name}.log"
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(stdlib_logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> stdlib_logging.Logger:
    """
    Get existing logger or create new one with default settings.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = stdlib_logging.getLogger(name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


def set_global_log_level(level: str) -> None:
    """
    Set log level for all CORTEX loggers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(stdlib_logging, level.upper())
    
    # Update all existing loggers
    for logger_name in stdlib_logging.Logger.manager.loggerDict:
        if logger_name.startswith("cortex") or logger_name.startswith("src"):
            logger = stdlib_logging.getLogger(logger_name)
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)


def configure_logging_from_config():
    """
    Configure logging using settings from ConfigManager.
    
    This should be called during CORTEX initialization to apply
    configuration file settings to the logging system.
    """
    try:
        from src.config import get_config_manager
        
        config_manager = get_config_manager()
        logging_config = config_manager.config.logging
        
        # Set global log level
        set_global_log_level(logging_config.level)
        
        # Configure root logger
        root_logger = stdlib_logging.getLogger()
        root_logger.setLevel(getattr(stdlib_logging, logging_config.level.upper()))
        
    except Exception as e:
        # Fallback to default if config loading fails
        stdlib_logging.warning(f"Failed to load logging configuration: {e}. Using defaults.")
