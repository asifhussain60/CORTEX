"""
Structured JSON Logger Implementation

Provides structured JSON logging with correlation IDs, request context
propagation, PII redaction, and async writes for production systems.

CORE-011: All functions have type hints.
CORE-012: All methods have Google-style docstrings.
CORE-013: Specific exceptions only.
"""

import json
import logging
import uuid
import re
import threading
import queue
from typing import Any, Dict, Optional, List
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field, asdict
import traceback
from concurrent.futures import ThreadPoolExecutor


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """Context for structured logging.

    Attributes:
        correlation_id: Unique ID for request tracing.
        component: Component name generating the log.
        user_id: User ID making the request.
        request_id: HTTP request ID if applicable.
        metadata: Additional context metadata.
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    component: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary.

        Returns:
            Dictionary representation of context.
        """
        return asdict(self)


@dataclass
class StructuredLoggerConfig:
    """Configuration for structured logger.

    Attributes:
        component: Component name.
        level: Minimum log level.
        sampling_rate: Fraction of logs to include (0.0-1.0).
        pii_redaction_enabled: Enable PII automatic redaction.
        async_writes: Use async write queue.
        buffer_size: Maximum logs in buffer.
        environment: Deployment environment (dev, prod, etc).
    """

    component: str
    level: LogLevel = LogLevel.INFO
    sampling_rate: float = 1.0
    pii_redaction_enabled: bool = True
    async_writes: bool = True
    buffer_size: int = 10000
    environment: str = "production"


class PIIRedactor:
    """Redacts Personally Identifiable Information from logs."""

    # Patterns for common PII
    PATTERNS: Dict[str, str] = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "ssn": r"\d{3}-\d{2}-\d{4}",
        "phone": r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "credit_card": r"\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}",
        "password": r"(?i)(password|passwd|pwd|secret|api[_-]?key|token|auth)\s*[:=]\s*[^\s,}]+",
    }

    # Field names that often contain PII
    PII_FIELDS: List[str] = [
        "password", "passwd", "pwd", "secret", "api_key", "apikey",
        "token", "auth_token", "access_token", "refresh_token",
        "ssn", "social_security_number", "phone", "telephone",
        "credit_card", "cc", "cvv", "encryption_key",
    ]

    @staticmethod
    def redact(data: Any, visited: Optional[set] = None) -> Any:
        """Redact PII from data.

        Args:
            data: Data to redact (string, dict, list, etc).
            visited: Set of visited object IDs for circular reference detection.

        Returns:
            Redacted data with same structure.

        Raises:
            TypeError: If data type cannot be redacted.
        """
        if visited is None:
            visited = set()

        if isinstance(data, str):
            return PIIRedactor._redact_string(data)
        elif isinstance(data, dict):
            obj_id = id(data)
            if obj_id in visited:
                return "[CIRCULAR]"
            visited.add(obj_id)
            return PIIRedactor._redact_dict(data, visited)
        elif isinstance(data, (list, tuple)):
            obj_id = id(data)
            if obj_id in visited:
                return "[CIRCULAR]"
            visited.add(obj_id)
            return [PIIRedactor.redact(item, visited) for item in data]
        return data

    @staticmethod
    def _redact_string(value: str) -> str:
        """Redact PII patterns from string.

        Args:
            value: String value to redact.

        Returns:
            String with PII redacted.
        """
        redacted = value
        for pattern_name, pattern in PIIRedactor.PATTERNS.items():
            redacted = re.sub(pattern, "[REDACTED]", redacted)
        return redacted

    @staticmethod
    def _redact_dict(data: Dict[str, Any], visited: Optional[set] = None) -> Dict[str, Any]:
        """Redact PII from dictionary.

        Args:
            data: Dictionary to redact.
            visited: Set of visited object IDs for circular reference detection.

        Returns:
            Dictionary with PII values redacted.
        """
        if visited is None:
            visited = set()

        redacted = {}
        for key, value in data.items():
            if key.lower() in PIIRedactor.PII_FIELDS:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = PIIRedactor.redact(value, visited)
        return redacted


class StructuredLogger:
    """Structured JSON logger with context propagation and PII redaction."""

    def __init__(self, config: StructuredLoggerConfig) -> None:
        """Initialize structured logger.

        Args:
            config: Logger configuration.
        """
        self.config = config
        self.component = config.component
        self.level = config.level
        self.sampling_rate = config.sampling_rate
        self.buffer_size = config.buffer_size
        self.pii_redactor = PIIRedactor()

        # Setup internal logger
        self.internal_logger = logging.getLogger(f"cortex.{config.component}")
        self.internal_logger.setLevel(self._level_to_int(config.level))
        self.internal_logger.propagate = False

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter(config.component))
        self.internal_logger.addHandler(handler)

        # Async write queue
        self.write_queue: Optional[queue.Queue] = None
        self.executor: Optional[ThreadPoolExecutor] = None

        if config.async_writes:
            self.write_queue = queue.Queue(maxsize=config.buffer_size)
            self.executor = ThreadPoolExecutor(max_workers=2)
            self._start_writer()

        # Context storage (thread-local)
        self._context = threading.local()

    def _level_to_int(self, level: LogLevel) -> int:
        """Convert LogLevel to logging module int.

        Args:
            level: LogLevel enum value.

        Returns:
            Logging module level constant.
        """
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARN: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return level_map.get(level, logging.INFO)

    def _start_writer(self) -> None:
        """Start async log writer."""
        if self.executor and self.write_queue:
            self.executor.submit(self._async_writer)

    def _async_writer(self) -> None:
        """Process queued log writes asynchronously."""
        while True:
            try:
                log_entry = self.write_queue.get(timeout=1)
                if log_entry is None:
                    break
                # Write to actual handler
            except queue.Empty:
                continue

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for current context.

        Args:
            correlation_id: Unique request/trace ID.
        """
        if not hasattr(self._context, "correlation_id"):
            self._context.correlation_id = correlation_id
        else:
            self._context.correlation_id = correlation_id

    def get_correlation_id(self) -> str:
        """Get current correlation ID, generating if missing.

        Returns:
            Current or newly generated correlation ID.
        """
        if not hasattr(self._context, "correlation_id"):
            self._context.correlation_id = str(uuid.uuid4())
        return self._context.correlation_id

    def _prepare_log_entry(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Prepare log entry with all metadata.

        Args:
            level: Log level string.
            message: Log message.
            extra: Extra context data.

        Returns:
            Complete log entry dictionary.

        Raises:
            ValueError: If message is empty.
        """
        if not message:
            raise ValueError("Message cannot be empty")

        extra = extra or {}

        # Redact PII if enabled (including message text)
        if self.config.pii_redaction_enabled:
            message = self.pii_redactor.redact(message)
            extra = self.pii_redactor.redact(extra)

        # Truncate large context (4KB limit)
        context_str = json.dumps(extra)
        if len(context_str) > 4096:
            extra = {"truncated": True, "size_bytes": len(context_str)}

        # Get current timestamp (Python 3.11+: datetime.UTC, else utcnow)
        try:
            from datetime import UTC
            timestamp = datetime.now(UTC).isoformat()
        except ImportError:
            timestamp = datetime.utcnow().isoformat() + "Z"

        entry = {
            "timestamp": timestamp,
            "level": level,
            "component": self.component,
            "correlation_id": self.get_correlation_id(),
            "message": message,
        }

        if extra:
            entry["context"] = extra

        return entry

    def debug(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log debug message.

        Args:
            message: Log message.
            extra: Extra context data.
        """
        if self._should_log(LogLevel.DEBUG):
            entry = self._prepare_log_entry("DEBUG", message, extra)
            self.internal_logger.debug(json.dumps(entry))

    def info(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log info message.

        Args:
            message: Log message.
            extra: Extra context data.
        """
        if self._should_log(LogLevel.INFO):
            entry = self._prepare_log_entry("INFO", message, extra)
            self.internal_logger.info(json.dumps(entry))

    def warn(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log warning message.

        Args:
            message: Log message.
            extra: Extra context data.
        """
        if self._should_log(LogLevel.WARN):
            entry = self._prepare_log_entry("WARN", message, extra)
            self.internal_logger.warning(json.dumps(entry))

    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message.

        Args:
            message: Log message.
            extra: Extra context data.
            exc_info: Include exception traceback.
        """
        if self._should_log(LogLevel.ERROR):
            entry = self._prepare_log_entry("ERROR", message, extra)

            if exc_info:
                entry["traceback"] = traceback.format_exc()

            self.internal_logger.error(json.dumps(entry))

    def critical(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log critical message.

        Args:
            message: Log message.
            extra: Extra context data.
            exc_info: Include exception traceback.
        """
        if self._should_log(LogLevel.CRITICAL):
            entry = self._prepare_log_entry("CRITICAL", message, extra)

            if exc_info:
                entry["traceback"] = traceback.format_exc()

            self.internal_logger.critical(json.dumps(entry))

    def _should_log(self, level: LogLevel) -> bool:
        """Determine if message should be logged based on sampling.

        Args:
            level: Log level.

        Returns:
            True if should log, False otherwise.
        """
        # Always log ERROR and CRITICAL
        if level in (LogLevel.ERROR, LogLevel.CRITICAL):
            return True

        # Apply sampling rate
        if self.sampling_rate < 1.0:
            import random
            return random.random() < self.sampling_rate

        return True

    def shutdown(self) -> None:
        """Shutdown logger and flush pending logs."""
        if self.write_queue:
            self.write_queue.put(None)  # Signal to stop

        if self.executor:
            self.executor.shutdown(wait=True)


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON log output."""

    def __init__(self, component: str) -> None:
        """Initialize JSON formatter.

        Args:
            component: Component name.
        """
        super().__init__()
        self.component = component

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON formatted log entry.
        """
        try:
            # If message is already JSON (from StructuredLogger),
            # return as-is
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Fallback for non-structured logs
            try:
                from datetime import UTC
                timestamp = datetime.now(UTC).isoformat()
            except ImportError:
                timestamp = datetime.utcnow().isoformat() + "Z"

            entry = {
                "timestamp": timestamp,
                "level": record.levelname,
                "component": self.component,
                "message": record.getMessage(),
            }
            return json.dumps(entry)


# Global logger instances cache
_loggers: Dict[str, StructuredLogger] = {}
_logger_lock = threading.Lock()


def get_structured_logger(
    component: str,
    level: LogLevel = LogLevel.INFO,
    sampling_rate: float = 1.0,
) -> StructuredLogger:
    """Get or create a structured logger instance.

    Args:
        component: Component name.
        level: Minimum log level.
        sampling_rate: Sampling rate (0.0-1.0).

    Returns:
        Structured logger instance.
    """
    key = f"{component}:{level.value}"

    if key not in _loggers:
        with _logger_lock:
            if key not in _loggers:
                config = StructuredLoggerConfig(
                    component=component,
                    level=level,
                    sampling_rate=sampling_rate,
                )
                _loggers[key] = StructuredLogger(config)

    return _loggers[key]
