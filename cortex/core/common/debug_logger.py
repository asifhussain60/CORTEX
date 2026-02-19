"""
Debug Logging Utility for Dashboard Development.

Provides easy-to-remove debug logging with clear markers.
All debug logs can be removed by:
1. Deleting this file
2. Removing imports of dashboard_debug
3. Removing @dashboard_debug decorators

AC-ID: AC-DEBUG-DASHBOARD-001
Authority: CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import functools
import logging
from datetime import datetime
from typing import Any, Callable, Optional

# Dedicated logger for dashboard debugging
# Can be disabled by setting level to CRITICAL or removing handlers
_dashboard_logger = logging.getLogger("cortex.debug.dashboard")
_dashboard_logger.setLevel(logging.DEBUG)

# Console handler with distinct format
if not _dashboard_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "[DEBUG:DASHBOARD] %(asctime)s - %(funcName)s - %(message)s",
            datefmt="%H:%M:%S"
        )
    )
    _dashboard_logger.addHandler(_handler)


def dashboard_debug(func: Callable) -> Callable:
    """
    Decorator for functions that need debug logging.

    Can be easily removed along with this module.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with entry/exit logging

    Example:
        >>> @dashboard_debug
        ... def generate_dashboard(repo_path: str) -> dict:
        ...     return {"status": "ok"}
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        _dashboard_logger.debug(f"→ ENTER {func_name}")
        _dashboard_logger.debug(f"  args: {_safe_repr(args)}")
        _dashboard_logger.debug(f"  kwargs: {_safe_repr(kwargs)}")

        try:
            result = func(*args, **kwargs)
            _dashboard_logger.debug(f"← EXIT {func_name} (success)")
            _dashboard_logger.debug(f"  result type: {type(result).__name__}")
            return result
        except Exception as e:
            _dashboard_logger.debug(f"← EXIT {func_name} (error: {e})")
            raise

    return wrapper


def log_dashboard_debug(message: str, **context: Any) -> None:
    """
    Log debug message with context.

    Args:
        message: Debug message
        **context: Additional context key-value pairs

    Example:
        >>> log_dashboard_debug("Processing repo", repo_name="cortex", file_count=850)
    """
    if context:
        context_str = ", ".join(f"{k}={_safe_repr(v)}" for k, v in context.items())
        _dashboard_logger.debug(f"{message} | {context_str}")
    else:
        _dashboard_logger.debug(message)


def log_dashboard_schema_validation(
    schema_name: str,
    data: dict,
    is_valid: bool,
    errors: Optional[list] = None
) -> None:
    """
    Log schema validation results.

    Args:
        schema_name: Name of schema being validated
        data: Data being validated
        is_valid: Whether validation passed
        errors: List of validation errors (if any)

    Example:
        >>> log_dashboard_schema_validation(
        ...     "RepoDashboardModel",
        ...     {"repo": {...}},
        ...     is_valid=True
        ... )
    """
    status = "✅ VALID" if is_valid else "❌ INVALID"
    _dashboard_logger.debug(f"Schema validation: {schema_name} - {status}")

    if not is_valid and errors:
        for error in errors[:5]:  # Limit to first 5 errors
            _dashboard_logger.debug(f"  - {error}")
        if len(errors) > 5:
            _dashboard_logger.debug(f"  ... and {len(errors) - 5} more errors")

    # Log data structure summary
    if isinstance(data, dict):
        keys = list(data.keys())
        _dashboard_logger.debug(f"  data keys: {keys}")


def log_dashboard_generation(
    stage: str,
    repo_name: str,
    **metrics: Any
) -> None:
    """
    Log dashboard generation progress.

    Args:
        stage: Generation stage (e.g., "schema_created", "template_rendered")
        repo_name: Repository name
        **metrics: Stage-specific metrics

    Example:
        >>> log_dashboard_generation(
        ...     "template_rendered",
        ...     "cortex",
        ...     file_size=125000,
        ...     charts=8
        ... )
    """
    _dashboard_logger.debug(f"[{stage}] repo={repo_name}")
    for key, value in metrics.items():
        _dashboard_logger.debug(f"  {key}: {_safe_repr(value)}")


def _safe_repr(obj: Any, max_length: int = 100) -> str:
    """
    Safe string representation of object.

    Args:
        obj: Object to represent
        max_length: Maximum string length

    Returns:
        Safe string representation
    """
    try:
        if obj is None:
            return "None"

        if isinstance(obj, (str, int, float, bool)):
            repr_str = repr(obj)
        elif isinstance(obj, (list, tuple)):
            repr_str = f"{type(obj).__name__}[{len(obj)}]"
        elif isinstance(obj, dict):
            repr_str = f"dict[{len(obj)} keys]"
        else:
            repr_str = f"{type(obj).__name__}(...)"

        if len(repr_str) > max_length:
            return repr_str[:max_length] + "..."
        return repr_str
    except Exception:
        return f"<{type(obj).__name__}>"


def disable_dashboard_debug() -> None:
    """
    Disable dashboard debug logging.

    Call this to silence debug logs without removing code.
    """
    _dashboard_logger.setLevel(logging.CRITICAL)


def enable_dashboard_debug() -> None:
    """
    Enable dashboard debug logging.

    Call this to re-enable debug logs.
    """
    _dashboard_logger.setLevel(logging.DEBUG)


# Export public API
__all__ = [
    "dashboard_debug",
    "log_dashboard_debug",
    "log_dashboard_schema_validation",
    "log_dashboard_generation",
    "disable_dashboard_debug",
    "enable_dashboard_debug",
]
