"""
Tests for audit database schema migrations.

Authority: AC-GOLDEN-E2E-003
TDD Phase: RED → GREEN
"""

import sqlite3
from pathlib import Path
import pytest


class TestAuditSchemaMigrations:
    """Test audit database schema and migrations."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Path:
        """Create temporary database for testing."""
        db_path = tmp_path / "test_audit.db"
        return db_path

    @pytest.fixture
    def db_connection(self, temp_db: Path) -> sqlite3.Connection:
        """Create database connection."""
        conn = sqlite3.connect(str(temp_db))
        conn.row_factory = sqlite3.Row
        return conn

    def test_schema_file_exists(self):
        """Schema file should exist in cortex_intelligence/audit/."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        assert schema_path.exists(), f"Schema file not found at {schema_path}"

    def test_migration_001_file_exists(self):
        """Migration 001 file should exist."""
        migration_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "migrations" / "001_orchestrator_events.sql"
        assert migration_path.exists(), f"Migration 001 not found at {migration_path}"

    def test_schema_creates_audit_log_table(self, db_connection: sqlite3.Connection):
        """Schema should create audit_log table."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Verify table exists
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
        )
        result = cursor.fetchone()
        assert result is not None, "audit_log table not created"

    def test_schema_creates_orchestrator_audit_events_table(self, db_connection: sqlite3.Connection):
        """Schema should create orchestrator_audit_events table."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Verify table exists
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orchestrator_audit_events'"
        )
        result = cursor.fetchone()
        assert result is not None, "orchestrator_audit_events table not created"

    def test_orchestrator_events_table_has_required_columns(self, db_connection: sqlite3.Connection):
        """Orchestrator events table should have all required columns."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Get table info
        cursor = db_connection.execute("PRAGMA table_info(orchestrator_audit_events)")
        columns = {row['name'] for row in cursor.fetchall()}
        
        required_columns = {
            'id', 'timestamp', 'orchestrator_name', 'workflow_stage',
            'activity', 'correlation_id', 'status', 'input_parameters',
            'output_results', 'duration_ms', 'ac_id'
        }
        
        missing = required_columns - columns
        assert not missing, f"Missing required columns: {missing}"

    def test_orchestrator_events_indexes_created(self, db_connection: sqlite3.Connection):
        """Required indexes should be created."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Get indexes
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='orchestrator_audit_events'"
        )
        indexes = {row['name'] for row in cursor.fetchall()}
        
        required_indexes = {
            'idx_orch_events_correlation',
            'idx_orch_events_orchestrator',
            'idx_orch_events_workflow_stage',
            'idx_orch_events_timestamp',
            'idx_orch_events_session'
        }
        
        missing = required_indexes - indexes
        assert not missing, f"Missing required indexes: {missing}"

    def test_golden_test_audit_trail_view_created(self, db_connection: sqlite3.Connection):
        """View for golden test queries should be created."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Verify view exists
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='v_golden_test_audit_trail'"
        )
        result = cursor.fetchone()
        assert result is not None, "v_golden_test_audit_trail view not created"

    def test_migration_001_is_idempotent(self, db_connection: sqlite3.Connection):
        """Migration 001 should be idempotent (safe to run multiple times)."""
        migration_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "migrations" / "001_orchestrator_events.sql"
        
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Run migration twice
        db_connection.executescript(migration_sql)
        db_connection.executescript(migration_sql)
        
        # Should not raise error
        cursor = db_connection.execute("SELECT version FROM schema_migrations WHERE version = 2")
        result = cursor.fetchone()
        assert result is not None, "Migration not recorded in schema_migrations"

    def test_insert_orchestrator_audit_event(self, db_connection: sqlite3.Connection):
        """Should be able to insert orchestrator audit event."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Insert test event
        db_connection.execute("""
            INSERT INTO orchestrator_audit_events (
                timestamp, orchestrator_name, workflow_stage, activity,
                correlation_id, status, input_parameters, output_results
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            '2026-02-17T10:00:00Z',
            'TestOrchestrator',
            'EXECUTION',
            'TEST_ACTIVITY',
            'test-correlation-123',
            'COMPLETED',
            '{"param1": "value1"}',
            '{"result": "success"}'
        ))
        
        db_connection.commit()
        
        # Verify insertion
        cursor = db_connection.execute(
            "SELECT * FROM orchestrator_audit_events WHERE correlation_id = ?",
            ('test-correlation-123',)
        )
        result = cursor.fetchone()
        assert result is not None
        assert result['orchestrator_name'] == 'TestOrchestrator'
        assert result['status'] == 'COMPLETED'

    def test_query_golden_test_audit_trail_view(self, db_connection: sqlite3.Connection):
        """Should be able to query golden test audit trail view."""
        schema_path = Path(__file__).parent.parent.parent.parent / "cortex_intelligence" / "audit" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        db_connection.executescript(schema_sql)
        
        # Insert test data
        db_connection.execute("""
            INSERT INTO orchestrator_audit_events (
                timestamp, orchestrator_name, workflow_stage, activity,
                correlation_id, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            '2026-02-17T10:00:00Z',
            'TestOrchestrator',
            'EXECUTION',
            'TEST_ACTIVITY',
            'view-test-123',
            'COMPLETED'
        ))
        db_connection.commit()
        
        # Query view
        cursor = db_connection.execute(
            "SELECT * FROM v_golden_test_audit_trail WHERE correlation_id = ?",
            ('view-test-123',)
        )
        result = cursor.fetchone()
        assert result is not None
        assert result['orchestrator_name'] == 'TestOrchestrator'
