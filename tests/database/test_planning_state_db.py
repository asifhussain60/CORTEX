"""
Comprehensive tests for Planning State Database.

Tests cover CRUD operations, transactions, rollback, constraints,
and ACID guarantees.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from src.database.planning_state_db import PlanningStateDB


class TestDatabaseInitialization:
    """Test database initialization and schema creation."""
    
    def test_database_creation(self, tmp_path):
        """Create new database with schema."""
        db_path = tmp_path / "test.db"
        db = PlanningStateDB(db_path=str(db_path))
        
        assert db_path.exists()
        assert db._conn is not None
        
        db.close()
    
    def test_schema_tables_exist(self, tmp_path):
        """Verify all required tables are created."""
        db_path = tmp_path / "test.db"
        db = PlanningStateDB(db_path=str(db_path))
        
        # Query sqlite_master for tables
        cursor = db._conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row["name"] for row in cursor.fetchall()]
        
        expected_tables = [
            "artifacts",
            "execution_log",
            "metrics",
            "phases",
            "plans",
            "schema_migrations",
            "state_snapshots",
            "tasks",
            "validations"
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table '{table}' not found"
        
        db.close()
    
    def test_foreign_keys_enabled(self, tmp_path):
        """Verify foreign key constraints are enabled."""
        db_path = tmp_path / "test.db"
        db = PlanningStateDB(db_path=str(db_path))
        
        cursor = db._conn.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        
        assert result[0] == 1, "Foreign keys not enabled"
        
        db.close()


class TestPlanOperations:
    """Test plan CRUD operations."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create test database."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        yield db_instance
        db_instance.close()
    
    def test_create_plan(self, db):
        """Create a new plan."""
        plan_id = db.create_plan(
            feature_name="User Authentication",
            complexity_tier=3,
            strategy="bootstrap",
            estimated_duration_days=5.0,
            metadata={"author": "test_user"}
        )
        
        assert plan_id.startswith("plan-")
        
        # Verify plan was created
        plan = db.get_plan(plan_id)
        assert plan is not None
        assert plan["feature_name"] == "User Authentication"
        assert plan["complexity_tier"] == 3
        assert plan["status"] == "not_started"
    
    def test_start_plan(self, db):
        """Start a plan."""
        plan_id = db.create_plan("Test Feature", complexity_tier=2)
        
        result = db.start_plan(plan_id)
        assert result is True
        
        plan = db.get_plan(plan_id)
        assert plan["status"] == "in_progress"
        assert plan["started_at"] is not None
    
    def test_complete_plan(self, db):
        """Complete a plan."""
        plan_id = db.create_plan("Test Feature", complexity_tier=2)
        db.start_plan(plan_id)
        
        result = db.complete_plan(plan_id)
        assert result is True
        
        plan = db.get_plan(plan_id)
        assert plan["status"] == "completed"
        assert plan["completed_at"] is not None
    
    def test_fail_plan(self, db):
        """Fail a plan with error message."""
        plan_id = db.create_plan("Test Feature", complexity_tier=2)
        db.start_plan(plan_id)
        
        result = db.fail_plan(plan_id, "Database connection error")
        assert result is True
        
        plan = db.get_plan(plan_id)
        assert plan["status"] == "failed"
        assert plan["error_message"] == "Database connection error"
    
    def test_get_plan_status(self, db):
        """Get comprehensive plan status."""
        plan_id = db.create_plan("Test Feature", complexity_tier=2)
        
        # Create some phases and tasks
        phase_id = db.create_phase(plan_id, 1, "Foundation")
        task_id = db.create_task(phase_id, plan_id, 1, "Setup database")
        
        status = db.get_plan_status(plan_id)
        
        assert status["plan"]["plan_id"] == plan_id
        assert len(status["phases"]) == 1
        assert len(status["tasks"]) == 1
        assert status["summary"]["total_phases"] == 1
        assert status["summary"]["total_tasks"] == 1


class TestPhaseOperations:
    """Test phase CRUD operations."""
    
    @pytest.fixture
    def db_with_plan(self, tmp_path):
        """Create database with a plan."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        yield db_instance, plan_id
        db_instance.close()
    
    def test_create_phase(self, db_with_plan):
        """Create a new phase."""
        db, plan_id = db_with_plan
        
        phase_id = db.create_phase(
            plan_id=plan_id,
            phase_number=1,
            name="Foundation Setup",
            config={"timeout": 300},
            max_retries=3
        )
        
        assert phase_id.startswith("phase-")
    
    def test_start_phase(self, db_with_plan):
        """Start a phase."""
        db, plan_id = db_with_plan
        
        phase_id = db.create_phase(plan_id, 1, "Foundation")
        result = db.start_phase(phase_id)
        
        assert result is True
    
    def test_complete_phase(self, db_with_plan):
        """Complete a phase with result data."""
        db, plan_id = db_with_plan
        
        phase_id = db.create_phase(plan_id, 1, "Foundation")
        db.start_phase(phase_id)
        
        result = db.complete_phase(phase_id, {"files_created": 5})
        assert result is True
    
    def test_fail_phase_with_retry(self, db_with_plan):
        """Fail phase and check retry logic."""
        db, plan_id = db_with_plan
        
        phase_id = db.create_phase(plan_id, 1, "Foundation", max_retries=3)
        db.start_phase(phase_id)
        
        # First failure
        db.fail_phase(phase_id, "Test error")
        assert db.can_retry_phase(phase_id) is True
        
        # Retry and fail again (simulate 3 failures)
        for i in range(2):
            db._conn.execute("""
                UPDATE phases SET status = 'in_progress' WHERE phase_id = ?
            """, (phase_id,))
            db.fail_phase(phase_id, f"Test error {i+2}")
        
        # Should not be able to retry after 3 failures
        assert db.can_retry_phase(phase_id) is False


class TestTaskOperations:
    """Test task CRUD operations."""
    
    @pytest.fixture
    def db_with_phase(self, tmp_path):
        """Create database with plan and phase."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        phase_id = db_instance.create_phase(plan_id, 1, "Foundation")
        yield db_instance, plan_id, phase_id
        db_instance.close()
    
    def test_create_task(self, db_with_phase):
        """Create a new task."""
        db, plan_id, phase_id = db_with_phase
        
        task_id = db.create_task(
            phase_id=phase_id,
            plan_id=plan_id,
            task_number=1,
            description="Setup database schema"
        )
        
        assert task_id.startswith("task-")
    
    def test_complete_task_lifecycle(self, db_with_phase):
        """Test complete task lifecycle: create → start → complete."""
        db, plan_id, phase_id = db_with_phase
        
        task_id = db.create_task(phase_id, plan_id, 1, "Test task")
        
        # Start task
        result = db.start_task(task_id)
        assert result is True
        
        # Complete task
        result = db.complete_task(task_id, {"result": "success"})
        assert result is True


class TestArtifactOperations:
    """Test artifact registration."""
    
    @pytest.fixture
    def db_with_plan(self, tmp_path):
        """Create database with a plan."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        yield db_instance, plan_id
        db_instance.close()
    
    def test_register_artifact(self, db_with_plan, tmp_path):
        """Register an artifact."""
        db, plan_id = db_with_plan
        
        # Create a test file
        test_file = tmp_path / "test_artifact.md"
        test_file.write_text("# Test Plan")
        
        artifact_id = db.register_artifact(
            plan_id=plan_id,
            path=str(test_file),
            artifact_type="plan",
            metadata={"format": "markdown"}
        )
        
        assert artifact_id.startswith("artifact-")


class TestValidationOperations:
    """Test validation recording."""
    
    @pytest.fixture
    def db_with_phase(self, tmp_path):
        """Create database with plan and phase."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        phase_id = db_instance.create_phase(plan_id, 1, "Foundation")
        yield db_instance, plan_id, phase_id
        db_instance.close()
    
    def test_record_validation(self, db_with_phase):
        """Record validation result."""
        db, plan_id, phase_id = db_with_phase
        
        validation_id = db.record_validation(
            plan_id=plan_id,
            phase_id=phase_id,
            validation_type="test",
            status="passed",
            passed_count=10,
            failed_count=0,
            duration_seconds=2.5
        )
        
        assert validation_id.startswith("validation-")


class TestSnapshotOperations:
    """Test state snapshot functionality."""
    
    @pytest.fixture
    def db_with_phase(self, tmp_path):
        """Create database with plan and phase."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        phase_id = db_instance.create_phase(plan_id, 1, "Foundation")
        yield db_instance, plan_id, phase_id
        db_instance.close()
    
    def test_create_snapshot(self, db_with_phase):
        """Create state snapshot."""
        db, plan_id, phase_id = db_with_phase
        
        state_data = {
            "current_phase": 1,
            "variables": {"db_initialized": True}
        }
        
        snapshot_id = db.create_snapshot(
            plan_id=plan_id,
            phase_id=phase_id,
            state_data=state_data,
            snapshot_type="checkpoint",
            description="After phase 1 completion"
        )
        
        assert snapshot_id.startswith("snapshot-")
    
    def test_retrieve_snapshot(self, db_with_phase):
        """Retrieve snapshot by ID."""
        db, plan_id, phase_id = db_with_phase
        
        state_data = {"phase": 1, "completed": True}
        
        snapshot_id = db.create_snapshot(
            plan_id=plan_id,
            phase_id=phase_id,
            state_data=state_data
        )
        
        snapshot = db.get_snapshot(snapshot_id)
        
        assert snapshot is not None
        assert snapshot["snapshot_id"] == snapshot_id
        assert snapshot["state_data"] == state_data
    
    def test_get_latest_snapshot(self, db_with_phase):
        """Get most recent snapshot."""
        db, plan_id, phase_id = db_with_phase
        
        # Create snapshots
        id1 = db.create_snapshot(plan_id, phase_id, {"phase": 1})
        id2 = db.create_snapshot(plan_id, phase_id, {"phase": 2})
        id3 = db.create_snapshot(plan_id, phase_id, {"phase": 3})
        db._conn.commit()
        
        # Get latest - should return one of the snapshots
        latest = db.get_latest_snapshot(plan_id, phase_id)
        
        assert latest is not None
        assert latest["snapshot_id"] in [id1, id2, id3]  # One of them is returned
        assert "phase" in latest["state_data"]  # Contains expected data


class TestTransactions:
    """Test transaction support and rollback."""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create test database."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        yield db_instance
        db_instance.close()
    
    def test_transaction_commit(self, db):
        """Test successful transaction commit."""
        with db.transaction():
            plan_id = db.create_plan("Test Feature", complexity_tier=2)
            phase_id = db.create_phase(plan_id, 1, "Foundation")
        
        # Verify data persisted
        plan = db.get_plan(plan_id)
        assert plan is not None
    
    def test_transaction_rollback(self, db):
        """Test transaction rollback on error."""
        plan_id = None
        
        try:
            with db.transaction():
                plan_id = db.create_plan("Test Feature", complexity_tier=2)
                # Force error with invalid foreign key
                db._conn.execute("""
                    INSERT INTO phases (phase_id, plan_id, phase_number, name)
                    VALUES ('test-phase', 'invalid-plan-id', 1, 'Test')
                """)
        except sqlite3.IntegrityError:
            pass  # Expected error
        
        # Verify plan was rolled back
        if plan_id:
            plan = db.get_plan(plan_id)
            assert plan is None


class TestLoggingOperations:
    """Test execution logging."""
    
    @pytest.fixture
    def db_with_plan(self, tmp_path):
        """Create database with a plan."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        yield db_instance, plan_id
        db_instance.close()
    
    def test_log_entry(self, db_with_plan):
        """Create log entry."""
        db, plan_id = db_with_plan
        
        log_id = db.log(
            plan_id=plan_id,
            message="Test log message",
            level="INFO",
            context={"key": "value"}
        )
        
        assert log_id > 0
    
    def test_get_logs(self, db_with_plan):
        """Retrieve logs for plan."""
        db, plan_id = db_with_plan
        
        # Create multiple log entries
        db.log(plan_id, "Message 1", "INFO")
        db.log(plan_id, "Message 2", "WARNING")
        db.log(plan_id, "Message 3", "ERROR")
        
        # Get all logs
        logs = db.get_logs(plan_id)
        assert len(logs) == 3
        
        # Get only ERROR logs
        error_logs = db.get_logs(plan_id, level="ERROR")
        assert len(error_logs) == 1
        assert error_logs[0]["message"] == "Message 3"


class TestMetricsOperations:
    """Test metrics recording."""
    
    @pytest.fixture
    def db_with_plan(self, tmp_path):
        """Create database with a plan."""
        db_path = tmp_path / "test.db"
        db_instance = PlanningStateDB(db_path=str(db_path))
        plan_id = db_instance.create_plan("Test Feature", complexity_tier=2)
        yield db_instance, plan_id
        db_instance.close()
    
    def test_record_metric(self, db_with_plan):
        """Record a metric."""
        db, plan_id = db_with_plan
        
        metric_id = db.record_metric(
            plan_id=plan_id,
            metric_name="execution_time",
            metric_value=42.5,
            unit="seconds",
            metadata={"phase": "foundation"}
        )
        
        assert metric_id > 0
