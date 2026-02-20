"""
Pytest fixtures for orchestrator trace logging.

AC-TRACE-003: Automatic test-mode trace enablement

Provides:
- Auto-enable tracing for all tests
- Auto-disable for production
- Trace report generation
- Trace cleanup utilities
- Batched flush (every 100 tests) to avoid per-test SQLite overhead
- Real-time progress feedback (prevents "hanging" perception)

Author: Asif Hussain
"""

import os
import pytest
from pathlib import Path
from cortex.infrastructure.trace_integration import enable_trace_for_tests, disable_trace_for_production
from cortex.infrastructure.orchestrator_trace_logger import get_trace_logger, TraceFlushReason

# Register CORTEX testing plugins — order matters:
# 1. cortex_xdist_plugin: batch-aware parallel progress (supersedes legacy plugin)
# 2. pytest_progress_plugin: retained for slow-test detection (complementary)
pytest_plugins = [
    "cortex.testing.plugins.cortex_xdist_plugin",
    "cortex.testing.pytest_progress_plugin",
]

# Counter for batched flushing — avoids 16K+ SQLite connections per full test run
_test_counter = 0
_FLUSH_INTERVAL = 100  # Flush traces every N tests instead of every single test


@pytest.fixture(scope="session", autouse=True)
def enable_traces_for_session():
    """Enable tracing for entire test session."""
    enable_trace_for_tests()
    yield
    # Final flush + cleanup after session
    try:
        trace_logger = get_trace_logger()
        trace_logger.flush_traces(TraceFlushReason.MANUAL)
    except Exception:
        pass
    disable_trace_for_production()


@pytest.fixture(autouse=True)
def flush_traces_after_test():
    """Batch-flush traces to prevent per-test SQLite overhead.

    Previously flushed after EVERY test (16K+ SQLite round-trips).
    Now flushes every 100 tests — same data integrity, 100x fewer DB calls.
    """
    global _test_counter
    yield
    _test_counter += 1
    if _test_counter % _FLUSH_INTERVAL == 0:
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
    os.environ["CORTEX_TRACE_DB"] = ".cortex-runtime/traces/test-orchestrator-traces.db"
    os.environ["CORTEX_TRACE_MAX_ROWS"] = "50000"  # Higher limit for tests
    os.environ["CORTEX_TRACE_ASYNC_FLUSH"] = "true"


def pytest_unconfigure(config):
    """Cleanup after pytest."""
    # Disable tracing for production
    disable_trace_for_production()
