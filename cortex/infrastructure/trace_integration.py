"""
Orchestrator Trace Integration - Decorator and utility functions

Provides:
- Automatic trace decoration for orchestrator methods
- Context management for trace operations
- Violation tracking and correlation
- Test-mode automatic enablement
- Production mode deactivation

AC-TRACE-002: Integration layer for orchestrator tracing

Author: Asif Hussain
"""

import functools
import os
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional, TypeVar

from cortex.infrastructure.orchestrator_trace_logger import (
    TraceEntry,
    TraceLevel,
    get_trace_logger,
)

F = TypeVar("F", bound=Callable[..., Any])

# Thread-local storage for correlation context
import threading

_context_storage = threading.local()


class TraceContext:
    """Context manager for trace operations."""

    def __init__(
        self,
        orchestrator_id: str,
        orchestrator_class: str,
        action: str,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Initialize trace context."""
        self.orchestrator_id = orchestrator_id
        self.orchestrator_class = orchestrator_class
        self.action = action
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.request_id = request_id or str(uuid.uuid4())
        self.trace_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.context_data: Dict[str, Any] = {}
        self.result = None
        self.violation_type = None

        # Store in thread-local storage
        if not hasattr(_context_storage, "stack"):
            _context_storage.stack = []
        _context_storage.stack.append(self)

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and record trace."""
        if hasattr(_context_storage, "stack") and _context_storage.stack:
            _context_storage.stack.pop()

        # Determine result
        result = "ERR" if exc_type else "OK"

        # Record trace
        duration_ms = (datetime.utcnow() - self.start_time).total_seconds() * 1000

        trace_logger = get_trace_logger()

        entry = TraceEntry(
            trace_id=self.trace_id,
            timestamp=self.start_time,
            orchestrator_id=self.orchestrator_id,
            orchestrator_class=self.orchestrator_class,
            action=self.action,
            level=TraceLevel.VIOLATION if self.violation_type else TraceLevel.ACTION,
            correlation_id=self.correlation_id,
            request_id=self.request_id,
            context=self.context_data,
            result=result,
            violation_type=self.violation_type,
            duration_ms=duration_ms,
        )

        trace_logger.record_trace(entry)

    def set_context(self, key: str, value: Any) -> None:
        """Add context data."""
        self.context_data[key] = value

    def set_violation(self, violation_type: str) -> None:
        """Mark as violation."""
        self.violation_type = violation_type


def trace_orchestrator_action(
    action_name: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator for orchestrator methods to automatically trace actions.

    Usage:
    ```python
    class MyOrchestrator:
        @trace_orchestrator_action("EXECUTE_OPERATION")
        def execute(self, operation: str) -> Result[str]:
            # Method body
    ```
    """

    def decorator(func: F) -> F:
        """Create decorated function wrapper."""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            """Execute wrapped function with applied decoration."""
            # Determine action name
            trace_action = action_name or func.__name__.upper()

            # Get orchestrator identity
            orchestrator_id = getattr(self, "orchestrator_id", self.__class__.__name__)
            orchestrator_class = self.__class__.__name__

            # Get trace context if already set
            correlation_id = None
            request_id = None
            if hasattr(_context_storage, "stack") and _context_storage.stack:
                parent_context = _context_storage.stack[-1]
                correlation_id = parent_context.correlation_id
                request_id = parent_context.request_id

            # Execute with tracing
            with TraceContext(
                orchestrator_id=orchestrator_id,
                orchestrator_class=orchestrator_class,
                action=trace_action,
                correlation_id=correlation_id,
                request_id=request_id,
            ) as ctx:
                try:
                    # Add argument info to context
                    ctx.set_context("args_count", len(args))
                    ctx.set_context("kwargs_keys", list(kwargs.keys()))

                    # Execute function
                    result = func(self, *args, **kwargs)

                    # Capture result
                    if hasattr(result, "is_ok"):
                        ctx.set_context("result_type", "Result")
                        ctx.set_context("is_ok", result.is_ok())
                        if not result.is_ok():
                            ctx.set_context("error", result.error())
                    else:
                        ctx.set_context("result_type", type(result).__name__)

                    return result
                except Exception as e:
                    ctx.set_context("exception_type", type(e).__name__)
                    ctx.set_context("exception_message", str(e))
                    raise

        return wrapper  # type: ignore

    return decorator


def trace_violation(
    orchestrator_id: str,
    violation_type: str,
    context: Dict[str, Any],
) -> None:
    """
    Record a governance violation trace.

    Usage:
    ```python
    trace_violation(
        orchestrator_id="enforcement",
        violation_type="CORE-002",
        context={"file": "file.md", "rule": "no_markdown_generation"}
    )
    ```
    """
    trace_logger = get_trace_logger()

    entry = TraceEntry(
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        orchestrator_id=orchestrator_id,
        orchestrator_class="GovernanceEnforcer",
        action="VIOLATION_DETECTED",
        level=TraceLevel.VIOLATION,
        correlation_id=_get_correlation_id(),
        request_id=_get_request_id(),
        context=context,
        result="BLOCKED",
        violation_type=violation_type,
    )

    trace_logger.record_trace(entry)


def trace_action(
    orchestrator_id: str,
    action: str,
    context: Dict[str, Any],
    result: str = "OK",
    duration_ms: Optional[float] = None,
) -> None:
    """
    Record a generic orchestrator action trace.

    Usage:
    ```python
    trace_action(
        orchestrator_id="master",
        action="EXECUTE_OPERATION",
        context={"operation": "implement", "target": "file.py"},
        result="OK",
        duration_ms=125.5
    )
    ```
    """
    trace_logger = get_trace_logger()

    entry = TraceEntry(
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        orchestrator_id=orchestrator_id,
        orchestrator_class=_get_orchestrator_class(orchestrator_id),
        action=action,
        level=TraceLevel.ACTION,
        correlation_id=_get_correlation_id(),
        request_id=_get_request_id(),
        context=context,
        result=result,
        duration_ms=duration_ms,
    )

    trace_logger.record_trace(entry)


def _get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    if hasattr(_context_storage, "stack") and _context_storage.stack:
        return _context_storage.stack[-1].correlation_id
    return str(uuid.uuid4())


def _get_request_id() -> str:
    """Get current request ID or generate new one."""
    if hasattr(_context_storage, "stack") and _context_storage.stack:
        return _context_storage.stack[-1].request_id
    return str(uuid.uuid4())


def _get_orchestrator_class(orchestrator_id: str) -> str:
    """Map orchestrator ID to class name."""
    # Simple mapping - can be extended
    id_to_class = {
        "master": "MasterOrchestrator",
        "enforcement": "EnforcementOrchestrator",
        "tdd": "TDDOrchestrator",
        "intent": "IntentRouter",
        "lens": "LENSSynthesis",
        "interaction": "InteractionOrchestrator",
    }
    return id_to_class.get(orchestrator_id.lower(), "UnknownOrchestrator")


def enable_trace_for_tests() -> None:
    """Enable tracing for test execution."""
    os.environ["CORTEX_TRACE_ENABLED"] = "true"


def disable_trace_for_production() -> None:
    """Disable tracing for production execution."""
    os.environ["CORTEX_TRACE_ENABLED"] = "false"


def is_trace_enabled() -> bool:
    """Check if tracing is enabled."""
    return os.getenv("CORTEX_TRACE_ENABLED", "false").lower() == "true"
