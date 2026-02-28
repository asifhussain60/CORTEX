"""Phase 89-d: ExecutionTraceRecorder — Unified SQLite Timeline — RED tests.

Tests that ExecutionTraceRecorder populates audit_sessions, workflow_runs,
workflow_cycles tables and provides timeline reconstruction.

GAP-89-10: Zero rows in audit/workflow trace tables
GAP-89-11: No ExecutionTraceRecorder class
GAP-89-12: No tool engagement logging

CORE-008: TDD mandatory — RED phase (all tests must FAIL before implementation)
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.infrastructure.execution_trace_recorder import ExecutionTraceRecorder


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: ExecutionTraceRecorder schema creation (GAP-89-11)
# ══════════════════════════════════════════════════════════════════════════════


class TestExecutionTraceRecorderSchema:
    """ExecutionTraceRecorder must create execution_traces table."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_recorder_creates_execution_traces_table(self, temp_db: Path) -> None:
        """ExecutionTraceRecorder creates execution_traces table on init."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        # Verify table exists
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='execution_traces'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "execution_traces"

    def test_execution_traces_table_has_required_columns(self, temp_db: Path) -> None:
        """execution_traces table has all required columns."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(execution_traces)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        
        required = {
            "id",
            "timestamp",
            "orchestrator",
            "operation",
            "template_id",
            "tool",
            "duration_ms",
            "status",
        }
        assert required.issubset(columns)


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: Orchestrator invocation recording (GAP-89-10)
# ══════════════════════════════════════════════════════════════════════════════


class TestOrchestratorInvocationRecording:
    """ExecutionTraceRecorder must record orchestrator invocations."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_record_orchestrator_invocation_writes_row(self, temp_db: Path) -> None:
        """record_orchestrator_invocation() writes to execution_traces."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        recorder.record_orchestrator_invocation(
            orchestrator="TDDOrchestrator",
            operation="implement",
            status="success",
            duration_ms=123,
        )
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM execution_traces WHERE orchestrator='TDDOrchestrator'")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1

    def test_record_multiple_invocations(self, temp_db: Path) -> None:
        """Multiple invocations create multiple rows."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        recorder.record_orchestrator_invocation("IntentRouter", "route", "success", 10)
        recorder.record_orchestrator_invocation("TDDOrchestrator", "implement", "success", 200)
        recorder.record_orchestrator_invocation("RefactoringOrchestrator", "refactor", "success", 150)
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM execution_traces")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: Template selection recording (GAP-89-10)
# ══════════════════════════════════════════════════════════════════════════════


class TestTemplateSelectionRecording:
    """ExecutionTraceRecorder must record template selections."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_record_template_selection_writes_row(self, temp_db: Path) -> None:
        """record_template_selection() writes to execution_traces with template_id."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        recorder.record_template_selection(
            template_id="frontend/html-refactor-validation",
            orchestrator="WorkflowComplexityRouter",
            rationale="technology=html detected",
        )
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT template_id FROM execution_traces WHERE template_id='frontend/html-refactor-validation'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "frontend/html-refactor-validation"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: Tool engagement recording (GAP-89-12)
# ══════════════════════════════════════════════════════════════════════════════


class TestToolEngagementRecording:
    """ExecutionTraceRecorder must record tool engagements (linters, formatters)."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_record_tool_engagement_writes_row(self, temp_db: Path) -> None:
        """record_tool_engagement() writes to execution_traces with tool field."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        recorder.record_tool_engagement(
            tool="ruff",
            command="ruff check --fix",
            exit_code=0,
            duration_ms=45,
        )
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT tool, duration_ms FROM execution_traces WHERE tool='ruff'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "ruff"
        assert result[1] == 45

    def test_record_lint_result_writes_row(self, temp_db: Path) -> None:
        """record_lint_result() writes to execution_traces with linter metadata."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        recorder.record_lint_result(
            linter="eslint",
            file_path="src/app.ts",
            issues_found=3,
            issues_fixed=2,
            duration_ms=67,
        )
        
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT tool FROM execution_traces WHERE tool='eslint'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "eslint"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 5: Timeline reconstruction (GAP-89-10)
# ══════════════════════════════════════════════════════════════════════════════


class TestTimelineReconstruction:
    """ExecutionTraceRecorder must provide timeline query."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_get_timeline_returns_chronological_events(self, temp_db: Path) -> None:
        """get_timeline() returns events in chronological order."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        # Record events in random order
        recorder.record_orchestrator_invocation("IntentRouter", "route", "success", 10)
        recorder.record_tool_engagement("ruff", "ruff check", 0, 45)
        recorder.record_template_selection("frontend/html-refactor-validation", "WorkflowComplexityRouter", "tech=html")
        
        timeline = recorder.get_timeline()
        
        assert len(timeline) == 3
        assert timeline[0]["orchestrator"] == "IntentRouter"  # First event
        assert timeline[1]["tool"] == "ruff"  # Second event
        assert timeline[2]["template_id"] == "frontend/html-refactor-validation"  # Third event

    def test_get_timeline_with_session_filter(self, temp_db: Path) -> None:
        """get_timeline(session_id) filters by session."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        # Record with session IDs
        recorder.record_orchestrator_invocation("IntentRouter", "route", "success", 10, session_id="session-1")
        recorder.record_orchestrator_invocation("TDDOrchestrator", "implement", "success", 200, session_id="session-2")
        
        timeline_s1 = recorder.get_timeline(session_id="session-1")
        
        assert len(timeline_s1) == 1
        assert timeline_s1[0]["orchestrator"] == "IntentRouter"


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 6: 30-day retention cleanup (GAP-89-10)
# ══════════════════════════════════════════════════════════════════════════════


class TestThirtyDayRetention:
    """ExecutionTraceRecorder must enforce 30-day retention."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create temporary SQLite database for testing."""
        fd, path = tempfile.mkstemp(suffix=".db")
        yield Path(path)
        Path(path).unlink(missing_ok=True)

    def test_cleanup_old_traces_removes_expired_rows(self, temp_db: Path) -> None:
        """cleanup_old_traces() removes rows older than 30 days."""
        recorder = ExecutionTraceRecorder(db_path=str(temp_db))
        
        # Insert old timestamp (40 days ago)
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO execution_traces (timestamp, orchestrator, operation, status, duration_ms) "
            "VALUES (datetime('now', '-40 days'), 'OldOrchestrator', 'test', 'success', 10)"
        )
        conn.commit()
        conn.close()
        
        # Run cleanup
        recorder.cleanup_old_traces(retention_days=30)
        
        # Verify row removed
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM execution_traces WHERE orchestrator='OldOrchestrator'")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 0
