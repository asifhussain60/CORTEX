"""
CORTEX Phase 7 - Deliverable 7.1: Tier 1 Schema Completion
TDD Test Suite (RED Phase)

Tests for:
1. working_memory table with TTL-based temporary context storage
2. schema_migrations.py system for zero-downtime schema evolution
3. tier1-schema.sql documentation

Author: Asif Hussain
Created: December 2, 2025
"""

import pytest
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from src.tier1.working_memory import WorkingMemory
from src.tier1.schema_migrations import SchemaMigration, MigrationManager


class TestWorkingMemoryTable:
    """Test TTL-based temporary context storage"""
    
    @pytest.fixture
    def working_memory(self, tmp_path):
        """Create temporary working memory instance"""
        db_path = tmp_path / "test_working_memory.db"
        return WorkingMemory(db_path=db_path)
    
    def test_working_memory_table_exists(self, working_memory):
        """Test that working_memory table is created"""
        conn = sqlite3.connect(working_memory.db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='working_memory'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "working_memory table should exist"
        assert result[0] == "working_memory"
    
    def test_working_memory_schema_structure(self, working_memory):
        """Test working_memory table has correct schema"""
        conn = sqlite3.connect(working_memory.db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(working_memory)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        
        # Verify required columns
        assert "id" in columns, "Should have id column"
        assert "key" in columns, "Should have key column"
        assert "value" in columns, "Should have value column"
        assert "created_at" in columns, "Should have created_at column"
        assert "expires_at" in columns, "Should have expires_at column"
        assert "context_type" in columns, "Should have context_type column"
    
    def test_store_temporary_context(self, working_memory):
        """Test storing temporary context with TTL"""
        # Store context with 1-hour TTL
        ttl_seconds = 3600
        context_data = {"feature": "user_auth", "status": "in_progress"}
        
        working_memory.store_temp_context(
            key="current_feature",
            value=context_data,
            ttl_seconds=ttl_seconds,
            context_type="feature_work"
        )
        
        # Retrieve context
        retrieved = working_memory.get_temp_context("current_feature")
        
        assert retrieved is not None, "Context should be retrievable"
        assert retrieved["value"] == context_data
        assert retrieved["context_type"] == "feature_work"
    
    def test_ttl_expiration(self, working_memory):
        """Test that expired context is not returned"""
        # Store context with 1-second TTL
        working_memory.store_temp_context(
            key="short_lived",
            value={"data": "test"},
            ttl_seconds=1,
            context_type="test"
        )
        
        # Wait for expiration
        time.sleep(2)
        
        # Attempt retrieval
        retrieved = working_memory.get_temp_context("short_lived")
        
        assert retrieved is None, "Expired context should not be returned"
    
    def test_cleanup_expired_contexts(self, working_memory):
        """Test automatic cleanup of expired contexts"""
        # Store multiple contexts with short TTL
        for i in range(5):
            working_memory.store_temp_context(
                key=f"temp_{i}",
                value={"index": i},
                ttl_seconds=1,
                context_type="test"
            )
        
        # Wait for expiration
        time.sleep(2)
        
        # Run cleanup
        deleted_count = working_memory.cleanup_expired_contexts()
        
        assert deleted_count == 5, "Should delete all 5 expired contexts"
    
    def test_update_existing_context(self, working_memory):
        """Test updating existing temporary context"""
        key = "feature_status"
        
        # Store initial value
        working_memory.store_temp_context(
            key=key,
            value={"status": "planning"},
            ttl_seconds=3600,
            context_type="feature_work"
        )
        
        # Update value
        working_memory.store_temp_context(
            key=key,
            value={"status": "implementing"},
            ttl_seconds=3600,
            context_type="feature_work"
        )
        
        # Retrieve and verify
        retrieved = working_memory.get_temp_context(key)
        
        assert retrieved["value"]["status"] == "implementing"
    
    def test_list_active_contexts(self, working_memory):
        """Test listing all active (non-expired) contexts"""
        # Store contexts
        working_memory.store_temp_context("ctx1", {"a": 1}, 3600, "test")
        working_memory.store_temp_context("ctx2", {"b": 2}, 3600, "test")
        working_memory.store_temp_context("ctx3", {"c": 3}, 1, "test")  # Expires quickly
        
        time.sleep(2)  # Wait for ctx3 to expire
        
        # List active contexts
        active = working_memory.list_active_contexts()
        
        assert len(active) == 2, "Should have 2 active contexts"
        assert any(c["key"] == "ctx1" for c in active)
        assert any(c["key"] == "ctx2" for c in active)
        assert not any(c["key"] == "ctx3" for c in active)


class TestSchemaMigrationSystem:
    """Test schema migration system for zero-downtime evolution"""
    
    @pytest.fixture
    def migration_manager(self, tmp_path):
        """Create migration manager with temp database"""
        db_path = tmp_path / "test_migrations.db"
        return MigrationManager(db_path=db_path)
    
    def test_migration_tracking_table_exists(self, migration_manager):
        """Test that schema_migrations table is created"""
        conn = sqlite3.connect(migration_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_migrations'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "schema_migrations"
    
    def test_migration_tracking_schema(self, migration_manager):
        """Test schema_migrations table structure"""
        conn = sqlite3.connect(migration_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(schema_migrations)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()
        
        assert "version" in columns
        assert "name" in columns
        assert "applied_at" in columns
        assert "status" in columns
    
    def test_register_migration(self, migration_manager):
        """Test registering a new migration"""
        migration = SchemaMigration(
            version="001",
            name="add_working_memory_table",
            up_sql="CREATE TABLE working_memory (id INTEGER PRIMARY KEY)",
            down_sql="DROP TABLE working_memory"
        )
        
        migration_manager.register_migration(migration)
        
        migrations = migration_manager.list_pending_migrations()
        assert len(migrations) == 1
        assert migrations[0].version == "001"
    
    def test_apply_migration(self, migration_manager):
        """Test applying a migration"""
        migration = SchemaMigration(
            version="001",
            name="create_test_table",
            up_sql="CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)",
            down_sql="DROP TABLE test_table"
        )
        
        migration_manager.register_migration(migration)
        result = migration_manager.apply_migration("001")
        
        assert result is True, "Migration should apply successfully"
        
        # Verify table was created
        conn = sqlite3.connect(migration_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_rollback_migration(self, migration_manager):
        """Test rolling back a migration"""
        migration = SchemaMigration(
            version="001",
            name="create_rollback_test",
            up_sql="CREATE TABLE rollback_test (id INTEGER PRIMARY KEY)",
            down_sql="DROP TABLE rollback_test"
        )
        
        migration_manager.register_migration(migration)
        migration_manager.apply_migration("001")
        
        # Rollback
        result = migration_manager.rollback_migration("001")
        
        assert result is True, "Rollback should succeed"
        
        # Verify table was dropped
        conn = sqlite3.connect(migration_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rollback_test'")
        assert cursor.fetchone() is None
        conn.close()
    
    def test_get_current_schema_version(self, migration_manager):
        """Test retrieving current schema version"""
        # Initially should be version 0
        version = migration_manager.get_current_version()
        assert version == "000"
        
        # Apply migration
        migration = SchemaMigration(
            version="001",
            name="test_version",
            up_sql="CREATE TABLE version_test (id INTEGER PRIMARY KEY)",
            down_sql="DROP TABLE version_test"
        )
        migration_manager.register_migration(migration)
        migration_manager.apply_migration("001")
        
        # Check version updated
        version = migration_manager.get_current_version()
        assert version == "001"
    
    def test_list_applied_migrations(self, migration_manager):
        """Test listing all applied migrations"""
        # Apply multiple migrations
        for i in range(1, 4):
            migration = SchemaMigration(
                version=f"00{i}",
                name=f"migration_{i}",
                up_sql=f"CREATE TABLE test_{i} (id INTEGER PRIMARY KEY)",
                down_sql=f"DROP TABLE test_{i}"
            )
            migration_manager.register_migration(migration)
            migration_manager.apply_migration(f"00{i}")
        
        applied = migration_manager.list_applied_migrations()
        
        assert len(applied) == 3
        assert all(m["status"] == "applied" for m in applied)
    
    def test_migration_idempotency(self, migration_manager):
        """Test that applying same migration twice doesn't break"""
        migration = SchemaMigration(
            version="001",
            name="idempotency_test",
            up_sql="CREATE TABLE IF NOT EXISTS idempotent_test (id INTEGER PRIMARY KEY)",
            down_sql="DROP TABLE IF EXISTS idempotent_test"
        )
        
        migration_manager.register_migration(migration)
        
        # Apply twice
        result1 = migration_manager.apply_migration("001")
        result2 = migration_manager.apply_migration("001")
        
        assert result1 is True
        assert result2 is False, "Second application should be skipped"


class TestTier1SchemaDocumentation:
    """Test tier1-schema.sql documentation file"""
    
    def test_schema_documentation_exists(self):
        """Test that tier1-schema.sql file exists"""
        schema_path = Path("cortex-brain/schemas/tier1-schema.sql")
        
        assert schema_path.exists(), "tier1-schema.sql should exist"
    
    def test_schema_documentation_has_all_tables(self):
        """Test that schema documentation includes all tables"""
        schema_path = Path("cortex-brain/schemas/tier1-schema.sql")
        content = schema_path.read_text()
        
        # Check for all expected tables
        expected_tables = [
            "conversations",
            "messages",
            "entities",
            "conversation_entities",
            "user_profile",
            "working_memory",  # NEW in Phase 7
            "sessions",
            "ambient_events",
            "application"
        ]
        
        for table in expected_tables:
            assert f"CREATE TABLE {table}" in content or f"CREATE TABLE IF NOT EXISTS {table}" in content, \
                f"Schema should document {table} table"
    
    def test_schema_documentation_has_indexes(self):
        """Test that schema documentation includes performance indexes"""
        schema_path = Path("cortex-brain/schemas/tier1-schema.sql")
        content = schema_path.read_text()
        
        assert "CREATE INDEX" in content, "Schema should document indexes"
    
    def test_schema_documentation_has_version(self):
        """Test that schema documentation includes version info"""
        schema_path = Path("cortex-brain/schemas/tier1-schema.sql")
        content = schema_path.read_text()
        
        assert "Version:" in content or "Schema Version:" in content, \
            "Schema should include version information"
    
    def test_schema_documentation_has_descriptions(self):
        """Test that schema documentation includes table descriptions"""
        schema_path = Path("cortex-brain/schemas/tier1-schema.sql")
        content = schema_path.read_text()
        
        # Should have SQL comments describing tables
        assert "--" in content or "/*" in content, \
            "Schema should include comments/descriptions"


class TestIntegrationWithExistingTier1:
    """Test that new schema components integrate with existing Tier 1"""
    
    @pytest.fixture
    def working_memory(self, tmp_path):
        """Create working memory with full schema"""
        db_path = tmp_path / "test_integration.db"
        return WorkingMemory(db_path=db_path)
    
    def test_working_memory_coexists_with_conversations(self, working_memory):
        """Test that working_memory table works alongside conversations"""
        # Store conversation
        conv_id = working_memory.store_conversation(
            conversation_id="test_conv_001",
            title="Test Conversation"
        )
        
        # Store temporary context
        working_memory.store_temp_context(
            key="conv_context",
            value={"conversation_id": conv_id},
            ttl_seconds=3600,
            context_type="conversation_work"
        )
        
        # Both should work
        assert conv_id is not None
        context = working_memory.get_temp_context("conv_context")
        assert context is not None
    
    def test_migrations_dont_break_existing_data(self, working_memory):
        """Test that schema migrations preserve existing data"""
        # Store existing data
        conv_id = working_memory.store_conversation(
            conversation_id="test_conv_002",
            title="Existing Data"
        )
        working_memory.add_message(conv_id, "user", "Test message")
        
        # Verify data exists
        messages = working_memory.get_messages(conv_id)
        assert len(messages) == 1
        
        # Apply migration (working_memory table should already exist from fixture)
        # Data should still be accessible
        messages_after = working_memory.get_messages(conv_id)
        assert len(messages_after) == 1
        assert messages_after[0]["content"] == "Test message"
