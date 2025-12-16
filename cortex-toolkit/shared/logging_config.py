"""
CORTEX Toolkit - Logging Configuration

Standardized logging setup for all toolkit tools.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    tool_name: str,
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup standardized logging for toolkit tool.
    
    Args:
        tool_name: Name of the tool (used in log messages).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to log file. Auto-generates if None.
        console: Enable console logging.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(tool_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Format: [TIMESTAMP] [LEVEL] [TOOL] Message
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Auto-generate log file in logs/toolkit/
        toolkit_root = Path(__file__).parent.parent
        log_dir = toolkit_root.parent / "logs" / "toolkit"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"{tool_name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_audit_logger(tool_name: str) -> logging.Logger:
    """
    Get audit logger for tool invocation tracking.
    
    Args:
        tool_name: Name of the tool.
        
    Returns:
        Audit logger instance.
    """
    audit_logger = logging.getLogger(f"{tool_name}.audit")
    audit_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    audit_logger.handlers.clear()
    
    # Audit log format
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Audit log file
    toolkit_root = Path(__file__).parent.parent
    audit_file = toolkit_root.parent / "logs" / "toolkit-audit.log"
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(audit_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    audit_logger.addHandler(file_handler)
    
    return audit_logger


def log_tool_invocation(
    tool_name: str,
    args: list,
    user: Optional[str] = None,
    working_dir: Optional[Path] = None
):
    """
    Log tool invocation to audit trail.
    
    Args:
        tool_name: Name of the tool.
        args: Command-line arguments.
        user: Username (auto-detects if None).
        working_dir: Working directory (auto-detects if None).
    """
    import getpass
    
    audit_logger = get_audit_logger(tool_name)
    
    user = user or getpass.getuser()
    working_dir = working_dir or Path.cwd()
    
    audit_logger.info(
        f"INVOCATION | tool={tool_name} | user={user} | "
        f"cwd={working_dir} | args={' '.join(args)}"
    )
