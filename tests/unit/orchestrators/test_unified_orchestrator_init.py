"""
Test suite for Unified Orchestrator Initialization (AC-PERMANENT-FIX-022)

Tests idempotent orchestrator initialization with:
- Schema creation
- Orchestrator registration
- Wiring state management
- Health checker integration
- Permanent fix validation

Authority: CORE-008 (TDD), CORE-027 (Audit), CORE-031 (SSOT)
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from cortex.orchestrators.core.unified_orchestrator_init import (
    UnifiedOrchestratorInitializer,
    initialize_orchestrators,
    get_initialization_status,
    CORE_ORCHESTRATORS,
    DOMAIN_ORCHESTRATORS,
    SUPPORT_ORCHESTRATORS,
)


class TestUnifiedOrchestratorInitializer:
    """Test UnifiedOrchestratorInitializer class"""

    @pytest.fixture
    def temp_db(self):
        """Provide temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_registry.db"
            yield db_path

    def test_initialization_creates_database(self, temp_db):
        """Test that initialization creates database file"""
        # Verify it doesn't exist first
        assert not temp_db.exists()
        
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        result = initializer.initialize()

        assert result["success"] is True
        assert temp_db.exists()

    def test_schema_creation(self, temp_db):
        """Test that database schema is created correctly"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        # Verify tables exist
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert "orchestrators" in tables
        assert "wiring_log" in tables
        assert "registry_metadata" in tables

        conn.close()

    def test_all_23_orchestrators_registered(self, temp_db):
        """Test that all 23 orchestrators are registered"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        result = initializer.initialize()

        total_count = (
            len(CORE_ORCHESTRATORS)
            + len(DOMAIN_ORCHESTRATORS)
            + len(SUPPORT_ORCHESTRATORS)
        )

        assert result["orchestrators_registered"] == total_count
        assert result["orchestrators_registered"] >= 23  # At least 23

    def test_all_orchestrators_wired(self, temp_db):
        """Test that all registered orchestrators have wired=1"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        # Count orchestrators with wired=1
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_count = cursor.fetchone()[0]

        # Count total orchestrators
        cursor.execute("SELECT COUNT(*) FROM orchestrators")
        total_count = cursor.fetchone()[0]

        assert wired_count == total_count
        assert wired_count >= 23

        conn.close()

    def test_idempotent_initialization(self, temp_db):
        """Test that running initialization multiple times is safe"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # First run
        result1 = initializer.initialize()
        assert result1["success"] is True

        # Get first state
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        first_wired_count = cursor.fetchone()[0]
        conn.close()

        # Second run
        result2 = initializer.initialize()
        assert result2["success"] is True

        # Verify state is unchanged
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        second_wired_count = cursor.fetchone()[0]
        conn.close()

        assert first_wired_count == second_wired_count
        assert first_wired_count >= 23

    def test_no_duplicate_registration(self, temp_db):
        """Test that orchestrators aren't duplicated on second run"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # First run
        result1 = initializer.initialize()
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators")
        first_count = cursor.fetchone()[0]
        conn.close()

        # Second run
        result2 = initializer.initialize()
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators")
        second_count = cursor.fetchone()[0]
        conn.close()

        assert first_count == second_count

    def test_core_orchestrators_registered(self, temp_db):
        """Test that all core orchestrators are registered"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM orchestrators WHERE category='core'"
        )
        core_count = cursor.fetchone()[0]

        assert core_count == len(CORE_ORCHESTRATORS)

        conn.close()

    def test_domain_orchestrators_registered(self, temp_db):
        """Test that all domain orchestrators are registered"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM orchestrators WHERE category='domain'"
        )
        domain_count = cursor.fetchone()[0]

        assert domain_count == len(DOMAIN_ORCHESTRATORS)

        conn.close()

    def test_support_orchestrators_registered(self, temp_db):
        """Test that all support orchestrators are registered"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM orchestrators WHERE category='support'"
        )
        support_count = cursor.fetchone()[0]

        assert support_count == len(SUPPORT_ORCHESTRATORS)

        conn.close()

    def test_orchestrator_has_required_fields(self, temp_db):
        """Test that all orchestrators have required metadata"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, module_path, class_name, category, priority, 
                   wired, health_status, description
            FROM orchestrators
            LIMIT 1
        """
        )

        row = cursor.fetchone()
        assert row is not None
        assert all(field is not None for field in row)

        conn.close()

    def test_priority_ordering(self, temp_db):
        """Test that orchestrators have proper priority ordering"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute("SELECT priority FROM orchestrators ORDER BY priority")
        priorities = [row[0] for row in cursor.fetchall()]

        # Priorities should be increasing and unique within categories
        assert len(priorities) == len(set(priorities))  # All unique

        conn.close()

    def test_health_status_initialized(self, temp_db):
        """Test that health status is initialized for all orchestrators"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE health_status IS NOT NULL")
        count = cursor.fetchone()[0]

        total = cursor.execute("SELECT COUNT(*) FROM orchestrators").fetchone()[0]

        assert count == total  # All orchestrators have health status

        conn.close()

    def test_wiring_log_created(self, temp_db):
        """Test that wiring log entries are created"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        initializer.initialize()

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM wiring_log")
        log_count = cursor.fetchone()[0]

        # Should have log entries for initialization
        assert log_count > 0

        conn.close()

    def test_permanent_fix_marker(self, temp_db):
        """Test that permanent fix is properly recorded"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))
        result = initializer.initialize()

        assert "permanent_fix_id" in result
        assert result["permanent_fix_id"] == "AC-PERMANENT-FIX-022"

    def test_no_reset_on_reinitialization(self, temp_db):
        """Test that reinitialization doesn't reset wired flags"""
        # This is the core test for the permanent fix
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # First initialization
        initializer.initialize()

        # Get wired count before second init
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_before = cursor.fetchone()[0]
        conn.close()

        # Second initialization (should not reset)
        initializer.initialize()

        # Get wired count after second init
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_after = cursor.fetchone()[0]
        conn.close()

        # Should be the same (no reset!)
        assert wired_before == wired_after
        assert wired_before >= 23


class TestModuleLevelFunctions:
    """Test module-level functions"""

    @pytest.fixture
    def temp_db(self):
        """Provide temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_registry.db"
            yield db_path

    def test_initialize_orchestrators_function(self, temp_db):
        """Test initialize_orchestrators() module function"""
        result = initialize_orchestrators(str(temp_db))

        assert result["success"] is True
        assert result["orchestrators_registered"] >= 23

    def test_get_initialization_status(self, temp_db):
        """Test get_initialization_status() function"""
        # Before initialization
        status = get_initialization_status(str(temp_db))
        assert status["initialized"] is False

        # After initialization
        initialize_orchestrators(str(temp_db))
        status = get_initialization_status(str(temp_db))

        assert status["initialized"] is True
        assert status["total_orchestrators"] >= 23
        assert status["wired_orchestrators"] >= 23

    def test_status_shows_all_wired(self, temp_db):
        """Test that status shows all orchestrators as wired"""
        initialize_orchestrators(str(temp_db))
        status = get_initialization_status(str(temp_db))

        assert status["total_orchestrators"] == status["wired_orchestrators"]


class TestOrchestratorDefinitions:
    """Test orchestrator definitions"""

    def test_core_orchestrators_not_empty(self):
        """Test that core orchestrators are defined"""
        assert len(CORE_ORCHESTRATORS) > 0

    def test_domain_orchestrators_not_empty(self):
        """Test that domain orchestrators are defined"""
        assert len(DOMAIN_ORCHESTRATORS) > 0

    def test_support_orchestrators_not_empty(self):
        """Test that support orchestrators are defined"""
        assert len(SUPPORT_ORCHESTRATORS) > 0

    def test_total_at_least_23(self):
        """Test that total orchestrators is at least 23"""
        total = (
            len(CORE_ORCHESTRATORS)
            + len(DOMAIN_ORCHESTRATORS)
            + len(SUPPORT_ORCHESTRATORS)
        )
        assert total >= 23

    def test_orchestrator_names_unique(self):
        """Test that all orchestrator names are unique"""
        all_orchs = CORE_ORCHESTRATORS + DOMAIN_ORCHESTRATORS + SUPPORT_ORCHESTRATORS
        names = [o.name for o in all_orchs]

        assert len(names) == len(set(names))  # All unique

    def test_orchestrator_priorities_ordered(self):
        """Test that orchestrators have priorities"""
        all_orchs = CORE_ORCHESTRATORS + DOMAIN_ORCHESTRATORS + SUPPORT_ORCHESTRATORS

        for orch in all_orchs:
            assert orch.priority > 0


class TestPermanentFixValidation:
    """Test validation that permanent fix works correctly"""

    @pytest.fixture
    def temp_db(self):
        """Provide temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_registry.db"
            yield db_path

    def test_phase3_reset_issue_fixed(self, temp_db):
        """
        Test the core issue: Phase 3 was resetting wired flags.
        This test validates the permanent fix.
        """
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # Simulate Phase 3 reset (old behavior)
        result = initializer.initialize()  # First init

        # Manually check database state
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_count_1 = cursor.fetchone()[0]
        conn.close()

        # Simulate "reinitialization" (what Phase 3 used to do)
        result = initializer.initialize()  # Second init

        # Check if flags were preserved (permanent fix)
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orchestrators WHERE wired=1")
        wired_count_2 = cursor.fetchone()[0]
        conn.close()

        # Permanent fix: counts should be equal (no reset!)
        assert wired_count_1 == wired_count_2
        assert wired_count_2 >= 23

    def test_orchestrator_count_stable(self, temp_db):
        """Test that orchestrator count remains stable across runs"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # First run
        result1 = initializer.initialize()
        count1 = result1["orchestrators_registered"]

        # Second run - health checker might unwire, so disable it
        initializer2 = UnifiedOrchestratorInitializer(str(temp_db))
        result2 = initializer2.initialize()
        count2 = result2["orchestrators_registered"]

        # Third run
        initializer3 = UnifiedOrchestratorInitializer(str(temp_db))
        result3 = initializer3.initialize()
        count3 = result3["orchestrators_registered"]

        # New registrations should be 0 after first run (idempotent)
        assert count1 > 0
        assert count2 == 0  # No new registrations (already registered)
        assert count3 == 0  # No new registrations (already registered)

    def test_no_corruption_on_multiple_runs(self, temp_db):
        """Test database integrity after multiple runs"""
        initializer = UnifiedOrchestratorInitializer(str(temp_db))

        # Run initialization 5 times
        for i in range(5):
            result = initializer.initialize()
            assert result["success"] is True

        # Verify final state
        status = get_initialization_status(str(temp_db))
        assert status["initialized"] is True
        assert status["total_orchestrators"] >= 23
        assert status["wired_orchestrators"] >= 23
        assert status["total_orchestrators"] == status["wired_orchestrators"]
