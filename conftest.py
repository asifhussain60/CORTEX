"""
Pytest fixtures for orchestrator trace logging.

AC-TRACE-003: Automatic test-mode trace enablement

Provides:
- Auto-enable tracing for all tests
- Auto-disable for production
- Trace report generation
- Trace cleanup utilities

Author: Asif Hussain
"""

import os
import pytest
from pathlib import Path
from cortex.infrastructure.trace_integration import enable_trace_for_tests, disable_trace_for_production
from cortex.infrastructure.orchestrator_trace_logger import get_trace_logger, TraceFlushReason


@pytest.fixture(scope="session", autouse=True)
def enable_traces_for_session():
    """Enable tracing for entire test session."""
    enable_trace_for_tests()
    yield
    # Cleanup after session
    disable_trace_for_production()


@pytest.fixture(autouse=True)
def flush_traces_after_test():
    """Flush traces after each test to prevent unbounded growth."""
    yield
    # After test completes, flush if needed
    try:
        trace_logger = get_trace_logger()
        trace_logger.flush_traces(TraceFlushReason.MANUAL)
    except Exception:
        pass  # Ignore flush errors in tests


@pytest.fixture
def trace_logger_instance():
    """Provide trace logger instance for tests."""
    return get_trace_logger()


@pytest.fixture
def trace_statistics(trace_logger_instance):
    """Get trace statistics for assertions."""
    return trace_logger_instance.get_statistics()


@pytest.fixture
def orchestrator_trace_writer():
    """Provide trace writer for orchestrator under test."""
    logger = get_trace_logger()
    writer = logger.get_trace_writer("test-orchestrator", "TestOrchestrator")
    return writer


def pytest_configure(config):
    """Configure pytest with trace settings."""
    # Set default trace settings for tests
    os.environ["CORTEX_TRACE_ENABLED"] = "true"
    os.environ["CORTEX_TRACE_DB"] = ".cortex/traces/test-orchestrator-traces.db"
    os.environ["CORTEX_TRACE_MAX_ROWS"] = "50000"  # Higher limit for tests
    os.environ["CORTEX_TRACE_ASYNC_FLUSH"] = "true"


def pytest_unconfigure(config):
    """Cleanup after pytest."""
    # Disable tracing for production
    disable_trace_for_production()
