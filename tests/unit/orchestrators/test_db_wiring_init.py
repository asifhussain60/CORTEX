"""
Tests for Database-Backed Wiring Initialization

AC-ID: AC-DB-SSOT-001
Authority: CORE-031 (Single Orchestrator Registry)

Tests verify:
1. All 23 orchestrators are defined
2. Definitions are valid and consistent
3. Registration works correctly
4. Categories are correct
"""

import shutil
import tempfile
import pytest
from pathlib import Path

from cortex.infrastructure.database import DatabaseConfig, DatabaseManager
from cortex.orchestrators.core.database_registry import (
    DatabaseBackedRegistry,
    OrchestratorCategory,
)
from cortex.orchestrators.core.db_wiring_init import (
    ALL_ORCHESTRATORS,
    CORE_ORCHESTRATORS,
    DOMAIN_ORCHESTRATORS,
    SUPPORT_ORCHESTRATORS,
    get_orchestrator_count_by_category,
    register_all_orchestrators,
    validate_orchestrator_definitions,
)


class TestOrchestratorDefinitions:
    """Tests for orchestrator definition structures."""
    
    def test_total_orchestrator_count(self):
        """Should have exactly 23 orchestrators defined."""
        assert len(ALL_ORCHESTRATORS) == 23
    
    def test_core_orchestrator_count(self):
        """Should have 6 core orchestrators."""
        assert len(CORE_ORCHESTRATORS) == 6
    
    def test_domain_orchestrator_count(self):
        """Should have 6 domain orchestrators."""
        assert len(DOMAIN_ORCHESTRATORS) == 6
    
    def test_support_orchestrator_count(self):
        """Should have 11 support orchestrators."""
        assert len(SUPPORT_ORCHESTRATORS) == 11
    
    def test_counts_match_total(self):
        """Sum of categories should equal total."""
        counts = get_orchestrator_count_by_category()
        assert counts["core"] + counts["domain"] + counts["support"] == counts["total"]
    
    def test_all_definitions_valid(self):
        """All orchestrator definitions should be valid."""
        errors = validate_orchestrator_definitions()
        assert errors == [], f"Validation errors: {errors}"
    
    def test_unique_names(self):
        """All orchestrators should have unique names."""
        names = [config.name for config in ALL_ORCHESTRATORS]
        assert len(names) == len(set(names)), "Duplicate orchestrator names found"
    
    def test_unique_priorities(self):
        """All orchestrators should have unique priorities."""
        priorities = [config.priority for config in ALL_ORCHESTRATORS]
        assert len(priorities) == len(set(priorities)), "Duplicate priorities found"


class TestCoreOrchestrators:
    """Tests for core orchestrator definitions."""
    
    def test_master_orchestrator_first(self):
        """MasterOrchestrator should have priority 1."""
        master = next(c for c in CORE_ORCHESTRATORS if c.name == "MasterOrchestrator")
        assert master.priority == 1
    
    def test_core_orchestrators_have_core_category(self):
        """All core orchestrators should be category CORE."""
        for config in CORE_ORCHESTRATORS:
            assert config.category == OrchestratorCategory.CORE
    
    def test_interaction_orchestrator_depends_on_master(self):
        """InteractionOrchestrator should depend on MasterOrchestrator."""
        interaction = next(c for c in CORE_ORCHESTRATORS if c.name == "InteractionOrchestrator")
        assert "MasterOrchestrator" in interaction.dependencies
    
    def test_intent_router_depends_on_interaction(self):
        """IntentRouter should depend on InteractionOrchestrator."""
        router = next(c for c in CORE_ORCHESTRATORS if c.name == "IntentRouter")
        assert "InteractionOrchestrator" in router.dependencies


class TestDomainOrchestrators:
    """Tests for domain orchestrator definitions."""
    
    def test_domain_orchestrators_have_domain_category(self):
        """All domain orchestrators should be category DOMAIN."""
        for config in DOMAIN_ORCHESTRATORS:
            assert config.category == OrchestratorCategory.DOMAIN
    
    def test_domain_priorities_in_range(self):
        """Domain orchestrators should have priorities 10-19."""
        for config in DOMAIN_ORCHESTRATORS:
            assert 10 <= config.priority < 20


class TestSupportOrchestrators:
    """Tests for support orchestrator definitions."""
    
    def test_support_orchestrators_have_support_category(self):
        """All support orchestrators should be category SUPPORT."""
        for config in SUPPORT_ORCHESTRATORS:
            assert config.category == OrchestratorCategory.SUPPORT
    
    def test_support_priorities_in_range(self):
        """Support orchestrators should have priorities 20+."""
        for config in SUPPORT_ORCHESTRATORS:
            assert config.priority >= 20


class TestRegistration:
    """Tests for orchestrator registration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test_wiring.db"
        config = DatabaseConfig(db_path=self.db_path)
        self.db = DatabaseManager(config)
        self.registry = DatabaseBackedRegistry(self.db)
        self.registry.initialize_schema()
        DatabaseBackedRegistry.reset_instance()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        DatabaseBackedRegistry.reset_instance()
    
    def test_register_all_orchestrators(self):
        """Should register all 23 orchestrators."""
        count = register_all_orchestrators(self.registry)
        assert count == 23
    
    def test_statistics_after_registration(self):
        """Statistics should reflect all registered orchestrators."""
        register_all_orchestrators(self.registry)
        
        stats = self.registry.get_wiring_statistics()
        assert stats["total_registered"] == 23
        assert stats["by_category"]["core"] == 6
        assert stats["by_category"]["domain"] == 6
        assert stats["by_category"]["support"] == 11
    
    def test_retrieve_registered_orchestrator(self):
        """Should be able to retrieve registered orchestrator config."""
        register_all_orchestrators(self.registry)
        
        master = self.registry.get("MasterOrchestrator")
        assert master is not None
        assert master.name == "MasterOrchestrator"
        assert master.category == OrchestratorCategory.CORE
    
    def test_idempotent_registration(self):
        """Multiple registrations should be idempotent."""
        count1 = register_all_orchestrators(self.registry)
        count2 = register_all_orchestrators(self.registry)
        
        # Should still have exactly 23
        stats = self.registry.get_wiring_statistics()
        assert stats["total_registered"] == 23


class TestPublicAPI:
    """Tests for public API exports."""
    
    def test_import_from_orchestrators_package(self):
        """Should be able to import initialization functions."""
        from cortex.orchestrators import (
            ALL_ORCHESTRATORS,
            CORE_ORCHESTRATORS,
            DOMAIN_ORCHESTRATORS,
            SUPPORT_ORCHESTRATORS,
            get_orchestrator_count_by_category,
            initialize_database_wiring,
            register_all_orchestrators,
        )
        
        assert len(ALL_ORCHESTRATORS) == 23
        assert callable(initialize_database_wiring)
        assert callable(register_all_orchestrators)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
