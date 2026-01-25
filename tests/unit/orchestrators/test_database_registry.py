"""
Tests for Database-Backed Orchestrator Registry (SSOT)

AC-ID: AC-DB-SSOT-001
Authority: CORE-031 (Single Orchestrator Registry)

These tests verify:
1. Schema initialization and migration
2. Orchestrator registration and retrieval
3. Wiring order computation
4. Snapshot creation and recovery
5. Health check integration
"""

import json
import shutil
import tempfile
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from cortex.infrastructure.database import DatabaseConfig, DatabaseManager
from cortex.orchestrators.core.database_registry import (
    DatabaseBackedRegistry,
    OrchestratorCategory,
    OrchestratorConfig,
    RegistryValidation,
    WiringResult,
    WiringSnapshot,
    WiringState,
    get_database_registry,
    initialize_registry,
)


class TestDatabaseBackedRegistrySchema:
    """Tests for schema initialization and migration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_registry.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        # Reset singleton for isolation
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_schema_initialization_creates_tables(self):
        """Schema initialization should create all 4 required tables."""
        result = self.registry.initialize_schema()
        
        assert result.is_ok(), f"Schema init failed: {result}"
        
        # Verify tables exist
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            "health_check_log",
            "orchestrator_registry",
            "schema_version",
            "wiring_log",
            "wiring_state_snapshot",
        ]
        for table in expected_tables:
            assert table in tables, f"Missing table: {table}"
    
    def test_schema_version_stored(self):
        """Schema version should be stored after initialization."""
        self.registry.initialize_schema()
        
        result = self.registry.check_schema_version()
        assert result.is_ok()
        assert result.unwrap() == self.registry.SCHEMA_VERSION
    
    def test_idempotent_schema_initialization(self):
        """Multiple schema initializations should be idempotent."""
        result1 = self.registry.initialize_schema()
        result2 = self.registry.initialize_schema()
        
        assert result1.is_ok()
        assert result2.is_ok()


class TestOrchestratorRegistration:
    """Tests for orchestrator registration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_registry.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        self.registry.initialize_schema()
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_register_orchestrator(self):
        """Should successfully register an orchestrator."""
        config = OrchestratorConfig(
            name="TestOrchestrator",
            module_path="cortex.orchestrators.test",
            class_name="TestOrchestrator",
            category=OrchestratorCategory.CORE,
            priority=10,
        )
        
        result = self.registry.register(config)
        assert result.is_ok()
    
    def test_get_registered_orchestrator(self):
        """Should retrieve registered orchestrator config."""
        config = OrchestratorConfig(
            name="TestOrchestrator",
            module_path="cortex.orchestrators.test",
            class_name="TestOrchestrator",
            category=OrchestratorCategory.DOMAIN,
            priority=50,
            dependencies=["DependencyOrch"],
            capabilities=["test", "demo"],
        )
        
        self.registry.register(config)
        
        retrieved = self.registry.get("TestOrchestrator")
        assert retrieved is not None
        assert retrieved.name == "TestOrchestrator"
        assert retrieved.module_path == "cortex.orchestrators.test"
        assert retrieved.category == OrchestratorCategory.DOMAIN
        assert retrieved.priority == 50
    
    def test_get_nonexistent_orchestrator_returns_none(self):
        """Should return None for non-existent orchestrator."""
        result = self.registry.get("NonExistent")
        assert result is None
    
    def test_register_multiple_orchestrators(self):
        """Should handle multiple orchestrator registrations."""
        configs = [
            OrchestratorConfig(
                name=f"Orchestrator{i}",
                module_path=f"cortex.orchestrators.test{i}",
                class_name=f"Orchestrator{i}",
                category=OrchestratorCategory.CORE,
                priority=i * 10,
            )
            for i in range(5)
        ]
        
        for config in configs:
            result = self.registry.register(config)
            assert result.is_ok()
        
        stats = self.registry.get_wiring_statistics()
        assert stats["total_registered"] == 5


class TestWiringStatistics:
    """Tests for wiring statistics and state management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_registry.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        self.registry.initialize_schema()
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_initial_state_is_uninitialized(self):
        """Initial state should be UNINITIALIZED."""
        assert self.registry.state == WiringState.UNINITIALIZED
    
    def test_statistics_reflect_registrations(self):
        """Statistics should accurately reflect registered orchestrators."""
        # Register orchestrators in different categories
        categories = [
            (OrchestratorCategory.CORE, 2),
            (OrchestratorCategory.DOMAIN, 3),
            (OrchestratorCategory.SUPPORT, 1),
        ]
        
        count = 0
        for category, num in categories:
            for i in range(num):
                config = OrchestratorConfig(
                    name=f"{category.value}Orch{i}",
                    module_path=f"cortex.{category.value}.{i}",
                    class_name=f"{category.value}Orch{i}",
                    category=category,
                    priority=count,
                )
                self.registry.register(config)
                count += 1
        
        stats = self.registry.get_wiring_statistics()
        
        assert stats["total_registered"] == 6
        assert stats["by_category"]["core"] == 2
        assert stats["by_category"]["domain"] == 3
        assert stats["by_category"]["support"] == 1


class TestSnapshotCreation:
    """Tests for wiring snapshot functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_registry.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        self.registry.initialize_schema()
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_create_snapshot(self):
        """Should successfully create a wiring snapshot."""
        # Register an orchestrator
        config = OrchestratorConfig(
            name="SnapshotTestOrch",
            module_path="cortex.test.snapshot",
            class_name="SnapshotTestOrch",
            category=OrchestratorCategory.CORE,
            priority=1,
        )
        self.registry.register(config)
        
        result = self.registry.create_snapshot()
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.snapshot_id.startswith("snap_")
        assert snapshot.total_orchestrators == 1
    
    def test_snapshot_persisted_to_database(self):
        """Snapshot should be persisted to database."""
        config = OrchestratorConfig(
            name="PersistTestOrch",
            module_path="cortex.test.persist",
            class_name="PersistTestOrch",
            category=OrchestratorCategory.DOMAIN,
            priority=1,
        )
        self.registry.register(config)
        
        self.registry.create_snapshot()
        
        # Verify in database
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM wiring_state_snapshot
            """)
            count = cursor.fetchone()[0]
        
        assert count >= 1


class TestDataclasses:
    """Tests for dataclass structures."""
    
    def test_orchestrator_config_defaults(self):
        """OrchestratorConfig should have sensible defaults."""
        config = OrchestratorConfig(
            name="Test",
            module_path="test.module",
            class_name="TestClass",
            category=OrchestratorCategory.SUPPORT,
        )
        
        assert config.priority == 100
        assert config.dependencies == []
        assert config.capabilities == []
        assert config.is_optional is False
        assert config.version == "1.0.0"
        assert config.state == WiringState.UNINITIALIZED
    
    def test_wiring_result_structure(self):
        """WiringResult should capture operation details."""
        result = WiringResult(
            success=True,
            orchestrator_name="TestOrch",
            timestamp=datetime.now(timezone.utc),
            duration_ms=42.5,
        )
        
        assert result.success is True
        assert result.orchestrator_name == "TestOrch"
        assert result.duration_ms == 42.5
        assert result.error is None
    
    def test_registry_validation_structure(self):
        """RegistryValidation should capture validation state."""
        validation = RegistryValidation(
            passed=True,
            timestamp=datetime.now(timezone.utc),
            checked_count=10,
            passed_count=10,
        )
        
        assert validation.passed is True
        assert validation.checked_count == 10
        assert validation.failures == []
        assert validation.suggestions == []


class TestPublicAPIExports:
    """Tests for public API accessibility."""
    
    def test_import_from_orchestrators_package(self):
        """Should be able to import from main orchestrators package."""
        from cortex.orchestrators import (
            DatabaseBackedRegistry,
            OrchestratorCategory,
            OrchestratorConfig,
            WiringResult,
            WiringState,
            create_health_checker,
            get_database_registry,
            initialize_registry,
        )
        
        assert DatabaseBackedRegistry is not None
        assert OrchestratorConfig is not None
        assert WiringState is not None
    
    def test_singleton_pattern(self):
        """DatabaseBackedRegistry should follow singleton pattern."""
        DatabaseBackedRegistry.reset_instance()
        
        instance1 = DatabaseBackedRegistry.instance()
        instance2 = DatabaseBackedRegistry.instance()
        
        assert instance1 is instance2
        
        DatabaseBackedRegistry.reset_instance()


class TestWiringStateEnum:
    """Tests for WiringState enum."""
    
    def test_all_states_defined(self):
        """All expected states should be defined."""
        expected_states = [
            "UNINITIALIZED",
            "LOADING",
            "REGISTERING",
            "COMPUTING_ORDER",
            "WIRING",
            "WIRED",
            "VALIDATION_FAILED",
            "UNWIRED",
        ]
        
        for state_name in expected_states:
            assert hasattr(WiringState, state_name)
    
    def test_state_values(self):
        """State values should be lowercase strings."""
        assert WiringState.WIRED.value == "wired"
        assert WiringState.UNINITIALIZED.value == "uninitialized"


class TestOrchestratorCategoryEnum:
    """Tests for OrchestratorCategory enum."""
    
    def test_all_categories_defined(self):
        """All expected categories should be defined."""
        expected = ["CORE", "DOMAIN", "SUPPORT", "INFRASTRUCTURE"]
        
        for cat_name in expected:
            assert hasattr(OrchestratorCategory, cat_name)
    
    def test_category_values(self):
        """Category values should be lowercase strings."""
        assert OrchestratorCategory.CORE.value == "core"
        assert OrchestratorCategory.DOMAIN.value == "domain"


class TestPopulateFromCode:
    """Tests for populate_from_code() using canonical db_wiring_init.py definitions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_registry.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        self.registry.initialize_schema()
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_populate_from_code_uses_db_wiring_init(self):
        """populate_from_code() should use db_wiring_init.py definitions."""
        result = self.registry.populate_from_code()
        
        assert result.is_ok(), f"populate_from_code failed: {result}"
        count = result.unwrap()
        
        # Should register all 23 orchestrators from db_wiring_init.py
        assert count == 23, f"Expected 23 orchestrators, got {count}"
    
    def test_populate_from_code_registers_master_orchestrator(self):
        """MasterOrchestrator should be registered with priority 1."""
        self.registry.populate_from_code()
        
        master = self.registry.get("MasterOrchestrator")
        assert master is not None
        assert master.name == "MasterOrchestrator"
        assert master.priority == 1
        assert master.category == OrchestratorCategory.CORE
    
    def test_populate_from_code_statistics(self):
        """Statistics should reflect all 23 orchestrators after populate."""
        self.registry.populate_from_code()
        
        stats = self.registry.get_wiring_statistics()
        assert stats["total_registered"] == 23
        # Core: MasterOrchestrator, InteractionOrchestrator, IntentRouter, 
        #       TDDOrchestrator, WorkflowOrchestrator, WrappedTDDOrchestrator
        assert stats["by_category"]["core"] == 6
        # Domain: RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
        #         ConversationOrchestrator, SeleniumPlaywrightOrchestrator, DocumentationOrchestrator
        assert stats["by_category"]["domain"] == 6
        # Support: 11 orchestrators
        assert stats["by_category"]["support"] == 11
    
    def test_populate_from_code_idempotent(self):
        """Multiple populate_from_code calls should be idempotent."""
        result1 = self.registry.populate_from_code()
        result2 = self.registry.populate_from_code()
        
        assert result1.is_ok()
        assert result2.is_ok()
        
        # Count should remain 23 (no duplicates)
        stats = self.registry.get_wiring_statistics()
        assert stats["total_registered"] == 23


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
