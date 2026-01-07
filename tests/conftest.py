# ==============================================================================
# CORTEX 6.0 Shared Test Fixtures
# ==============================================================================
# Centralized pytest fixtures for all CORTEX tests.
# Provides common utilities, mock objects, and test data.
#
# Author: Asif Hussain
# Copyright © 2025-2026 Asif Hussain. All rights reserved.
# ==============================================================================
"""Shared pytest fixtures for CORTEX test suite."""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ==============================================================================
# PATH FIXTURES
# ==============================================================================

@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def src_path(project_root: Path) -> Path:
    """Get the src directory path."""
    return project_root / "src"


@pytest.fixture
def cortex_brain_path(project_root: Path) -> Path:
    """Get the cortex-brain directory path."""
    return project_root / "cortex-brain"


# ==============================================================================
# TEMPORARY DIRECTORY FIXTURES
# ==============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory(prefix="cortex_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_db(temp_dir: Path) -> Path:
    """Create a temporary database file path."""
    return temp_dir / "test_cortex.db"


@pytest.fixture
def temp_log_dir(temp_dir: Path) -> Path:
    """Create a temporary log directory."""
    log_dir = temp_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


# ==============================================================================
# AUDIT LOGGER FIXTURES
# ==============================================================================

@pytest.fixture
def audit_logger(temp_log_dir: Path):
    """Create an audit logger instance for testing."""
    from src.orchestrators.audit_logger import EnterpriseAuditLogger
    
    logger = EnterpriseAuditLogger(
        log_dir=str(temp_log_dir),
        enable_console=False,  # Disable console output in tests
        enable_file=True
    )
    return logger


@pytest.fixture
def mock_audit_logger() -> MagicMock:
    """Create a mock audit logger for unit tests."""
    mock = MagicMock()
    mock.log = MagicMock()
    mock.log_info = MagicMock()
    mock.log_error = MagicMock()
    mock.log_warning = MagicMock()
    mock.get_session_id = MagicMock(return_value="test-session-001")
    return mock


# ==============================================================================
# STATE MANAGER FIXTURES
# ==============================================================================

@pytest.fixture
def state_manager(temp_dir: Path):
    """Create a StateManager instance for testing."""
    from src.orchestrators.state_manager import StateManager
    
    state_file = temp_dir / "test_state.json"
    manager = StateManager(state_file=str(state_file))
    return manager


@pytest.fixture
def mock_state_manager() -> MagicMock:
    """Create a mock state manager for unit tests."""
    mock = MagicMock()
    mock.get_state = MagicMock(return_value=None)
    mock.set_state = MagicMock(return_value=True)
    mock.delete_state = MagicMock(return_value=True)
    mock.get_transitions = MagicMock(return_value=[])
    return mock


# ==============================================================================
# DATABASE FIXTURES
# ==============================================================================

@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    import sqlite3
    
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def test_db(temp_db: Path):
    """Create a test SQLite database file."""
    import sqlite3
    
    conn = sqlite3.connect(str(temp_db))
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for testing
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    
    yield conn
    conn.close()


# ==============================================================================
# SAMPLE DATA FIXTURES
# ==============================================================================

@pytest.fixture
def sample_plan_data() -> Dict[str, Any]:
    """Sample plan data for testing."""
    return {
        "plan_id": "test-plan-001",
        "name": "Test Plan",
        "status": "IN_PROGRESS",
        "phases": [
            {
                "id": 1,
                "name": "Phase 1",
                "status": "COMPLETED",
                "tasks": [
                    {"id": "1.1", "name": "Task 1.1", "status": "COMPLETED"},
                    {"id": "1.2", "name": "Task 1.2", "status": "COMPLETED"}
                ]
            },
            {
                "id": 2,
                "name": "Phase 2",
                "status": "IN_PROGRESS",
                "tasks": [
                    {"id": "2.1", "name": "Task 2.1", "status": "IN_PROGRESS"},
                    {"id": "2.2", "name": "Task 2.2", "status": "NOT_STARTED"}
                ]
            }
        ],
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "author": "test",
            "priority": "P1"
        }
    }


@pytest.fixture
def sample_governance_rules() -> Dict[str, Any]:
    """Sample governance rules for testing."""
    return {
        "rules": [
            {
                "id": "TDD_ENFORCEMENT",
                "name": "TDD Enforcement",
                "description": "Tests must fail before implementation",
                "severity": "CRITICAL",
                "enabled": True
            },
            {
                "id": "HOLISTIC_DISCOVERY",
                "name": "Holistic Discovery",
                "description": "Search before create",
                "severity": "HIGH",
                "enabled": True
            }
        ],
        "version": "1.0.0"
    }


@pytest.fixture
def sample_dag_data() -> Dict[str, Any]:
    """Sample DAG data for testing dependency resolution."""
    return {
        "nodes": {
            "A": {"dependencies": []},
            "B": {"dependencies": ["A"]},
            "C": {"dependencies": ["A"]},
            "D": {"dependencies": ["B", "C"]},
            "E": {"dependencies": ["D"]}
        },
        "metadata": {
            "name": "Test DAG",
            "version": "1.0"
        }
    }


# ==============================================================================
# CORRELATION ID FIXTURES
# ==============================================================================

@pytest.fixture
def correlation_id() -> str:
    """Generate a test correlation ID."""
    return f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"


@pytest.fixture
def trace_context(correlation_id: str) -> Dict[str, str]:
    """Create a trace context for testing."""
    return {
        "correlation_id": correlation_id,
        "span_id": "test-span-001",
        "trace_id": "test-trace-001",
        "parent_span_id": None
    }


# ==============================================================================
# MOCK FIXTURES FOR EXTERNAL DEPENDENCIES
# ==============================================================================

@pytest.fixture
def mock_file_system(temp_dir: Path) -> Generator[MagicMock, None, None]:
    """Mock file system operations."""
    with patch("pathlib.Path.exists") as mock_exists:
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("pathlib.Path.write_text") as mock_write:
                mock_exists.return_value = True
                yield MagicMock(
                    exists=mock_exists,
                    mkdir=mock_mkdir,
                    write_text=mock_write,
                    temp_dir=temp_dir
                )


@pytest.fixture
def mock_datetime():
    """Mock datetime for deterministic tests."""
    fixed_time = datetime(2026, 1, 7, 12, 0, 0)
    with patch("datetime.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt


# ==============================================================================
# PERFORMANCE TEST FIXTURES
# ==============================================================================

@pytest.fixture
def performance_timer():
    """Timer fixture for performance tests."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.perf_counter()
            
        def stop(self):
            self.end_time = time.perf_counter()
            
        @property
        def elapsed_ms(self) -> float:
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return 0.0
    
    return Timer()


@pytest.fixture
def benchmark_config() -> Dict[str, Any]:
    """Configuration for benchmark tests."""
    return {
        "routing_sla_ms": 5.0,  # <5ms for routing
        "state_sla_ms": 10.0,  # <10ms for state operations
        "iterations": 100,
        "warmup_iterations": 10
    }


# ==============================================================================
# CLEANUP FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def cleanup_environment():
    """Auto-cleanup environment after each test."""
    # Setup
    original_env = os.environ.copy()
    
    yield
    
    # Teardown - restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ==============================================================================
# SESSION-SCOPED FIXTURES
# ==============================================================================

@pytest.fixture(scope="session")
def session_temp_dir() -> Generator[Path, None, None]:
    """Session-scoped temporary directory for shared resources."""
    with tempfile.TemporaryDirectory(prefix="cortex_session_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def fixtures_path() -> Path:
    """Path to test fixtures data directory."""
    return Path(__file__).parent / "fixtures"
