"""
Test suite for GovernanceDatabaseManager CRUD operations.

Purpose:
    Test all Create, Read, Update, Delete operations on governance rules,
    including schema integrity, transactions, and error handling.

Coverage:
    - create_project_rule()
    - get_rule(), list_rules()
    - update_rule()
    - Database schema integrity
    - Error handling and constraints

Author: Asif Hussain
Version: 1.0
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from typing import Generator
from cortex.brain.core.governance_database import (
    GovernanceDatabaseManager,
    GovernanceRule,
    RuleTier,
)


class TestCRUDOperations:
    """Test suite for CRUD operations."""

    @pytest.fixture
    def temp_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            yield mgr
            mgr.close()

    def test_create_rule_success(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test successful rule creation."""
        rule = temp_db.create_project_rule(
            rule_id="TEST-001",
            name="Test Rule",
            category="security",
            severity="blocked",
            description="Test rule description",
            enforcement_point="validator",
            audit_event="SECURITY_CHECK",
            created_by="test_user",
        )

        assert rule.rule_id == "TEST-001"
        assert rule.name == "Test Rule"
        assert rule.category == "security"
        assert rule.severity == "blocked"
        assert rule.is_active is True
        assert rule.tier == RuleTier.TIER_1.value

    def test_create_rule_with_metadata(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test rule creation with metadata."""
        metadata = {
            "severity_level": 1,
            "tags": ["critical", "auto-fix"],
            "owner": "security-team",
        }

        rule = temp_db.create_project_rule(
            rule_id="META-001",
            name="Rule with Metadata",
            category="security",
            severity="blocked",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
            metadata=metadata,
        )

        assert rule.metadata is not None
        retrieved = temp_db.get_rule("META-001")
        assert retrieved is not None
        assert retrieved.metadata is not None

    def test_create_duplicate_rule_fails(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test that creating duplicate rule_id raises error."""
        temp_db.create_project_rule(
            rule_id="DUP-001",
            name="First",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Try to create duplicate
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.create_project_rule(
                rule_id="DUP-001",
                name="Duplicate",
                category="test",
                severity="info",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )

    def test_read_existing_rule(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test reading an existing rule."""
        # Create rule
        created = temp_db.create_project_rule(
            rule_id="READ-001",
            name="Read Test",
            category="quality",
            severity="warning",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Read it back
        retrieved = temp_db.get_rule("READ-001")

        assert retrieved is not None
        assert retrieved.rule_id == created.rule_id
        assert retrieved.name == created.name
        assert retrieved.category == created.category

    def test_read_nonexistent_rule_returns_none(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test reading nonexistent rule returns None."""
        result = temp_db.get_rule("NONEXISTENT")
        assert result is None

    def test_list_rules_empty(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test listing rules from empty database."""
        rules = temp_db.list_rules()
        assert len(rules) == 0

    def test_list_rules_with_filter(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test listing rules with category filter."""
        # Create rules in different categories
        for i in range(3):
            temp_db.create_project_rule(
                rule_id=f"SEC-{i}",
                name=f"Security Rule {i}",
                category="security",
                severity="blocked",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )

        for i in range(2):
            temp_db.create_project_rule(
                rule_id=f"PERF-{i}",
                name=f"Performance Rule {i}",
                category="performance",
                severity="warning",
                description="Test",
                enforcement_point="test",
                audit_event="TEST",
                created_by="test_user",
            )

        # List with filter
        sec_rules = temp_db.list_rules(category="security")
        assert len(sec_rules) == 3
        assert all(r.category == "security" for r in sec_rules)

        perf_rules = temp_db.list_rules(category="performance")
        assert len(perf_rules) == 2

    def test_list_rules_inactive_filter(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test listing only active/inactive rules."""
        # Create rules
        temp_db.create_project_rule(
            rule_id="ACTIVE-001",
            name="Active",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        temp_db.create_project_rule(
            rule_id="INACTIVE-001",
            name="Inactive",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Deactivate one
        temp_db.update_rule("INACTIVE-001", updated_by="test_user", is_active=False)

        # List active
        active = temp_db.list_rules(is_active=True)
        assert len(active) == 1
        assert active[0].rule_id == "ACTIVE-001"

        # List inactive
        inactive = temp_db.list_rules(is_active=False)
        assert len(inactive) == 1
        assert inactive[0].rule_id == "INACTIVE-001"

    def test_update_rule_basic(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test basic rule update."""
        # Create rule
        temp_db.create_project_rule(
            rule_id="UPD-001",
            name="Original",
            category="test",
            severity="info",
            description="Original description",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Update it
        updated = temp_db.update_rule(
            "UPD-001",
            updated_by="admin_user",
            name="Updated",
            description="New description",
        )

        assert updated.name == "Updated"
        assert updated.description == "New description"
        assert updated.updated_by == "admin_user"

        # Verify persistence
        retrieved = temp_db.get_rule("UPD-001")
        assert retrieved.name == "Updated"

    def test_update_rule_severity(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test updating rule severity."""
        temp_db.create_project_rule(
            rule_id="SEV-001",
            name="Test",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Update severity
        updated = temp_db.update_rule(
            "SEV-001",
            updated_by="test_user",
            severity="blocked",
        )

        assert updated.severity == "blocked"

    def test_update_rule_deactivate(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test deactivating a rule."""
        temp_db.create_project_rule(
            rule_id="DEACT-001",
            name="Test",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Deactivate
        updated = temp_db.update_rule(
            "DEACT-001",
            updated_by="test_user",
            is_active=False,
        )

        # SQLite returns 0 for False
        assert updated.is_active == 0 or updated.is_active is False

        # Verify not in active list
        active_rules = temp_db.list_rules(is_active=True)
        assert all(r.rule_id != "DEACT-001" for r in active_rules)

    def test_update_nonexistent_rule_fails(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test updating nonexistent rule raises error."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.update_rule(
                "NONEXISTENT",
                updated_by="test_user",
                name="New Name",
            )

    def test_update_multiple_fields(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test updating multiple fields at once."""
        temp_db.create_project_rule(
            rule_id="MULTI-001",
            name="Original",
            category="test",
            severity="info",
            description="Original",
            enforcement_point="original",
            audit_event="TEST",
            created_by="test_user",
        )

        # Update multiple fields
        updated = temp_db.update_rule(
            "MULTI-001",
            updated_by="test_user",
            name="New Name",
            severity="warning",
            description="New description",
            enforcement_point="new_point",
        )

        assert updated.name == "New Name"
        assert updated.severity == "warning"
        assert updated.description == "New description"
        assert updated.enforcement_point == "new_point"


class TestSchemaIntegrity:
    """Test suite for database schema integrity."""

    @pytest.fixture
    def temp_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            yield mgr
            mgr.close()

    def test_schema_verification_passes(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test schema verification passes for initialized database."""
        assert temp_db.verify_schema() is True

    def test_all_required_tables_exist(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test all required tables are created."""
        conn = temp_db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {
            "project_rules",
            "team_rules",
            "governance_audit_log",
            "rule_versions",
        }

        assert required_tables.issubset(tables)

    def test_required_indexes_exist(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test all required indexes are created."""
        conn = temp_db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}

        required_indexes = {
            "idx_project_rules_tier",
            "idx_project_rules_category",
            "idx_project_rules_active",
            "idx_team_rules_team",
            "idx_audit_rule_id",
            "idx_audit_timestamp",
        }

        assert required_indexes.issubset(indexes)

    def test_project_rules_columns(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test project_rules table has all required columns."""
        conn = temp_db._get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(project_rules)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "rule_id",
            "tier",
            "name",
            "category",
            "severity",
            "description",
            "enforcement_point",
            "audit_event",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_active",
            "metadata",
        }

        assert required_columns.issubset(columns)

    def test_audit_log_columns(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test governance_audit_log table has all required columns."""
        conn = temp_db._get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(governance_audit_log)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "audit_id",
            "rule_id",
            "action",
            "actor",
            "timestamp",
            "previous_state",
            "new_state",
            "reason",
            "is_compliant",
        }

        assert required_columns.issubset(columns)


class TestTransactionHandling:
    """Test suite for transaction handling and consistency."""

    @pytest.fixture
    def temp_db(self) -> Generator[GovernanceDatabaseManager, None, None]:
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            mgr = GovernanceDatabaseManager(db_path=db_path)
            mgr.initialize()
            yield mgr
            mgr.close()

    def test_create_transaction_atomicity(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test create operation is atomic."""
        rule = temp_db.create_project_rule(
            rule_id="ATOM-001",
            name="Atomic",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Should be able to retrieve immediately
        retrieved = temp_db.get_rule("ATOM-001")
        assert retrieved is not None
        assert retrieved.name == "Atomic"

    def test_update_transaction_atomicity(self, temp_db: GovernanceDatabaseManager) -> None:
        """Test update operation is atomic."""
        temp_db.create_project_rule(
            rule_id="UPAT-001",
            name="Original",
            category="test",
            severity="info",
            description="Test",
            enforcement_point="test",
            audit_event="TEST",
            created_by="test_user",
        )

        # Update and verify
        temp_db.update_rule("UPAT-001", updated_by="test_user", name="Modified")

        retrieved = temp_db.get_rule("UPAT-001")
        assert retrieved.name == "Modified"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
