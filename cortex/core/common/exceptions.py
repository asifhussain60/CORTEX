"""
cortex/common/exceptions.py

Common exception types with diagnostics for production use.
Includes decorator-based exception handlers for DRY code patterns.

AC-REM-002-01: Consolidates exception handlers across codebase.
"""

import functools
import logging
import sqlite3
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

# Type variable for generic decorator return types
T = TypeVar('T')


class DatabaseOperationError(Exception):
    """Database operation failure with context.

    Wraps SQLite errors with operation context for debugging.
    """

    def __init__(
        self,
        message: str,
        original_exception: Optional[Exception] = None,
        operation: Optional[str] = None,
        table: Optional[str] = None,
    ) -> None:
        """Initialize database operation error.

        Args:
            message: Error description
            original_exception: Original SQLite exception
            operation: Operation that failed (e.g., 'insert', 'update')
            table: Table name involved
        """
        self.message = message
        self.operation = operation
        self.table = table

        parts = [message]
        if operation:
            parts.append(f"operation: {operation}")
        if table:
            parts.append(f"table: {table}")
        if original_exception:
            parts.append(f"cause: {original_exception}")

        super().__init__(" | ".join(parts))

        if original_exception:
            self.__cause__ = original_exception


class RetryExhaustedError(Exception):
    """Raised when retry attempts are exhausted."""

    def __init__(
        self,
        message: str,
        attempts: int,
        last_exception: Optional[Exception] = None,
    ) -> None:
        """Initialize retry exhausted error.

        Args:
            message: Error description
            attempts: Number of attempts made
            last_exception: Last exception encountered
        """
        self.attempts = attempts
        self.last_exception = last_exception

        super().__init__(f"{message} (attempts: {attempts})")

        if last_exception:
            self.__cause__ = last_exception


def handle_database_error(
    func: Optional[Callable[..., T]] = None,
    *,
    fallback: Optional[T] = None,
    reraise: bool = False,
    log_level: int = logging.ERROR,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """Decorator to handle database errors consistently.

    Catches sqlite3 errors and either returns fallback, logs, or reraises
    as DatabaseOperationError.

    Args:
        func: Function to wrap (when used without parentheses)
        fallback: Value to return on error (default: None)
        reraise: If True, reraise as DatabaseOperationError
        log_level: Logging level for errors

    Returns:
        Decorated function or decorator

    Example:
        @handle_database_error
        def query_data():
            # May raise sqlite3.Error
            pass

        @handle_database_error(fallback=[], reraise=False)
        def get_records():
            # Returns [] on error
            pass
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return fn(*args, **kwargs)
            except sqlite3.Error as e:
                logging.log(
                    log_level,
                    f"Database error in {fn.__name__}: {type(e).__name__}: {e}"
                )
                if reraise:
                    raise DatabaseOperationError(
                        f"Database operation failed in {fn.__name__}",
                        original_exception=e,
                        operation=fn.__name__,
                    ) from e
                return fallback
        return wrapper

    if func is not None:
        # Called without parentheses: @handle_database_error
        return decorator(func)
    # Called with parentheses: @handle_database_error(fallback=...)
    return decorator


def handle_validation_error(
    func: Optional[Callable[..., T]] = None,
    *,
    fallback: T = False,  # type: ignore
    log_level: int = logging.WARNING,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """Decorator to handle validation errors consistently.

    Catches ValueError and TypeError, returns fallback (default: False).

    Args:
        func: Function to wrap
        fallback: Value to return on error (default: False)
        log_level: Logging level for errors

    Returns:
        Decorated function or decorator
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return fn(*args, **kwargs)
            except (ValueError, TypeError) as e:
                logging.log(
                    log_level,
                    f"Validation error in {fn.__name__}: {type(e).__name__}: {e}"
                )
                return fallback  # type: ignore
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def handle_io_error(
    func: Optional[Callable[..., T]] = None,
    *,
    fallback: Optional[T] = None,
    log_level: int = logging.ERROR,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """Decorator to handle I/O errors consistently.

    Catches FileNotFoundError, PermissionError, IOError.

    Args:
        func: Function to wrap
        fallback: Value to return on error
        log_level: Logging level for errors

    Returns:
        Decorated function or decorator
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return fn(*args, **kwargs)
            except (FileNotFoundError, PermissionError, IOError) as e:
                logging.log(
                    log_level,
                    f"I/O error in {fn.__name__}: {type(e).__name__}: {e}"
                )
                return fallback
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry function on specified exceptions.

    Implements exponential backoff with configurable retry count.

    Args:
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        backoff_multiplier: Multiply delay by this factor each retry
        retry_on: Tuple of exception types to retry on

    Returns:
        Decorated function

    Raises:
        RetryExhaustedError: When all retries are exhausted
    """
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            delay = delay_seconds

            for attempt in range(max_retries):
                try:
                    return fn(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logging.warning(
                            f"Retry {attempt + 1}/{max_retries} for {fn.__name__}: {e}"
                        )
                        time.sleep(delay)
                        delay *= backoff_multiplier
                except Exception:
                    # Non-retryable exception, reraise immediately
                    raise

            raise RetryExhaustedError(
                f"All {max_retries} retries exhausted for {fn.__name__}",
                attempts=max_retries,
                last_exception=last_exception,
            )
        return wrapper
    return decorator


class ValidationError(Exception):
    """Validation error with diagnostic context.

    Provides structured error information for debugging and monitoring.
    """

    def __init__(self, message: str, file_path: str = None, line_info: str = None,
                 context: dict = None):
        """Initialize validation error.

        Args:
            message: Error message
            file_path: Path to file that caused error (optional)
            line_info: Line number or error details (optional)
            context: Additional context dict (optional)
        """
        self.message = message
        self.file_path = file_path
        self.line_info = line_info
        self.context = context or {}

        # Build detailed message
        parts = [message]
        if file_path:
            parts.append(f"file: {file_path}")
        if line_info:
            parts.append(f"line: {line_info}")

        super().__init__(" | ".join(parts))


class RecoverableError(Exception):
    """Error that can be recovered from via retry or fallback.

    Used to distinguish transient errors from permanent failures.
    """

    def __init__(self, message: str, retry_count: int = 0,
                 retry_delay_ms: float = 100):
        """Initialize recoverable error.

        Args:
            message: Error message
            retry_count: Number of retries attempted
            retry_delay_ms: Delay between retries in milliseconds
        """
        self.message = message
        self.retry_count = retry_count
        self.retry_delay_ms = retry_delay_ms

        super().__init__(
            f"{message} (retries: {retry_count}, delay: {retry_delay_ms}ms)"
        )


class ConfigurationError(Exception):
    """Configuration validation error.

    Indicates invalid or missing configuration values.
    """

    def __init__(self, message: str, config_key: str = None,
                 expected: str = None, received: str = None):
        """Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that failed validation
            expected: Expected value or type
            received: Actual value received
        """
        self.message = message
        self.config_key = config_key
        self.expected = expected
        self.received = received

        parts = [message]
        if config_key:
            parts.append(f"key: {config_key}")
        if expected and received:
            parts.append(f"expected: {expected}, got: {received}")

        super().__init__(" | ".join(parts))


class HealthCheckError(Exception):
    """Health check failure.

    Indicates a component failed its health verification.
    """

    def __init__(self, component: str, message: str,
                 recovery_action: str = None):
        """Initialize health check error.

        Args:
            component: Component that failed (e.g., "database", "audit_logger")
            message: Failure reason
            recovery_action: Suggested recovery action
        """
        self.component = component
        self.message = message
        self.recovery_action = recovery_action

        parts = [f"{component} health check failed: {message}"]
        if recovery_action:
            parts.append(f"recovery: {recovery_action}")

        super().__init__(" | ".join(parts))
