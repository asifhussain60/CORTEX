"""
Tests for Deprecated Orchestrator Migration Strategy - Track 3 Part B.

Tests migration planning, prioritization, and consolidation tracking.

AC_START: AC-WAVE7T3-PB-TEST-001
Tests: 22 total (registry: 6, migrator: 10, consolidation: 6)
"""

import pytest
from cortex.orchestrators.deprecated_orchestrators_migration import (
    DeprecatedOrchestrator,
    DeprecationLevel,
    ConsolidationStrategy,
    ConsolidationPlan,
    DeprecatedOrchestratorsRegistry,
    DeprecatedOrchestratorMigrator,
)


class TestDeprecatedOrchestratorsRegistry:
    """Tests for deprecated orchestrators registry."""

    def test_registry_initialization(self):
        """Test registry has all 18 deprecated orchestrators."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        assert len(all_deprecated) == 18

    def test_get_all_deprecated(self):
        """Test retrieving all deprecated orchestrators."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        assert all(isinstance(o, DeprecatedOrchestrator) for o in all_deprecated)
        names = [o.name for o in all_deprecated]
        assert "composition_engine" in names
        assert "orchestrator_factories" in names

    def test_get_by_level_critical(self):
        """Test filtering by critical level."""
        registry = DeprecatedOrchestratorsRegistry()
        critical = registry.get_by_level(DeprecationLevel.CRITICAL)
        assert len(critical) >= 6  # Expected critical count
        assert all(o.deprecation_level == DeprecationLevel.CRITICAL for o in critical)

    def test_get_by_level_standard(self):
        """Test filtering by standard level."""
        registry = DeprecatedOrchestratorsRegistry()
        standard = registry.get_by_level(DeprecationLevel.STANDARD)
        assert len(standard) >= 4
        assert all(o.deprecation_level == DeprecationLevel.STANDARD for o in standard)

    def test_get_by_level_low(self):
        """Test filtering by low level."""
        registry = DeprecatedOrchestratorsRegistry()
        low = registry.get_by_level(DeprecationLevel.LOW)
        assert len(low) >= 5
        assert all(o.deprecation_level == DeprecationLevel.LOW for o in low)

    def test_get_critical(self):
        """Test getting critical deprecations."""
        registry = DeprecatedOrchestratorsRegistry()
        critical = registry.get_critical()
        assert len(critical) > 0
        assert all(o.deprecation_level == DeprecationLevel.CRITICAL for o in critical)

    def test_migration_summary(self):
        """Test migration summary."""
        registry = DeprecatedOrchestratorsRegistry()
        summary = registry.get_migration_summary()
        assert summary["total_deprecated"] == 18
        assert summary["critical"] >= 6
        assert "direct_replacement" in summary["migration_strategies"]


class TestDeprecatedOrchestratorMigrator:
    """Tests for migration planning and execution."""

    def test_migrator_initialization(self):
        """Test migrator initialization."""
        migrator = DeprecatedOrchestratorMigrator()
        assert migrator is not None
        assert len(migrator.registry.get_all_deprecated()) == 18

    def test_create_migration_plan_direct_replacement(self):
        """Test creating migration plan for direct replacement."""
        migrator = DeprecatedOrchestratorMigrator()
        orchestrator = DeprecatedOrchestrator(
            name="test_orch",
            file_path="test.py",
            deprecation_level=DeprecationLevel.CRITICAL,
            reason="Test replacement",
            consolidation_strategy=ConsolidationStrategy.DIRECT_REPLACEMENT,
            migration_target="UnifiedFactory"
        )
        
        plan = migrator.create_migration_plan(orchestrator)
        assert plan is not None
        assert len(plan.actions) > 0
        assert plan.risk_level == "medium"
        assert plan.estimated_effort >= 1.0

    def test_create_migration_plan_extraction(self):
        """Test creating migration plan for functionality extraction."""
        migrator = DeprecatedOrchestratorMigrator()
        orchestrator = DeprecatedOrchestrator(
            name="test_extract",
            file_path="test.py",
            deprecation_level=DeprecationLevel.STANDARD,
            reason="Test extraction",
            consolidation_strategy=ConsolidationStrategy.FUNCTIONALITY_EXTRACTION,
            migration_target="Analyzer"
        )
        
        plan = migrator.create_migration_plan(orchestrator)
        assert plan is not None
        assert len(plan.actions) > 0
        assert plan.risk_level == "medium"

    def test_create_migration_plan_adapter_pattern(self):
        """Test creating migration plan for adapter pattern."""
        migrator = DeprecatedOrchestratorMigrator()
        orchestrator = DeprecatedOrchestrator(
            name="test_adapter",
            file_path="test.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Test adapter",
            consolidation_strategy=ConsolidationStrategy.ADAPTER_PATTERN,
            migration_target="Registry"
        )
        
        plan = migrator.create_migration_plan(orchestrator)
        assert plan is not None
        assert plan.risk_level == "low"
        assert plan.estimated_effort <= 1.5

    def test_create_migration_plan_feature_flag(self):
        """Test creating migration plan for feature flag."""
        migrator = DeprecatedOrchestratorMigrator()
        orchestrator = DeprecatedOrchestrator(
            name="test_flag",
            file_path="test.py",
            deprecation_level=DeprecationLevel.LOW,
            reason="Test feature flag",
            consolidation_strategy=ConsolidationStrategy.FEATURE_FLAG,
            migration_target="NewComponent"
        )
        
        plan = migrator.create_migration_plan(orchestrator)
        assert plan is not None
        assert plan.risk_level == "low"
        assert plan.estimated_effort == 0.5

    def test_get_migration_priority(self):
        """Test migration priority ordering."""
        migrator = DeprecatedOrchestratorMigrator()
        priority = migrator.get_migration_priority()
        
        assert len(priority) > 0
        # Critical should come before standard
        critical_indices = [i for i, o in enumerate(priority) if o.deprecation_level == DeprecationLevel.CRITICAL]
        standard_indices = [i for i, o in enumerate(priority) if o.deprecation_level == DeprecationLevel.STANDARD]
        
        if critical_indices and standard_indices:
            assert max(critical_indices) < min(standard_indices)

    def test_mark_migration_complete(self):
        """Test marking migration as complete."""
        migrator = DeprecatedOrchestratorMigrator()
        result = migrator.mark_migration_complete("composition_engine")
        assert result is True
        assert "composition_engine" in migrator.completed_migrations

    def test_get_migration_status_initial(self):
        """Test migration status at start."""
        migrator = DeprecatedOrchestratorMigrator()
        status = migrator.get_migration_status()
        
        assert status["total_to_migrate"] == 18
        assert status["completed"] == 0
        assert status["remaining"] == 18
        assert status["progress_percentage"] == 0.0

    def test_get_migration_status_with_progress(self):
        """Test migration status with progress."""
        migrator = DeprecatedOrchestratorMigrator()
        migrator.mark_migration_complete("composition_engine")
        migrator.mark_migration_complete("orchestrator_factories")
        
        status = migrator.get_migration_status()
        assert status["completed"] == 2
        assert status["remaining"] == 16
        assert status["progress_percentage"] == pytest.approx(11.11, rel=1e-2)

    def test_get_consolidation_summary(self):
        """Test consolidation summary."""
        migrator = DeprecatedOrchestratorMigrator()
        summary = migrator.get_consolidation_summary()
        
        assert "total_deprecated" in summary
        assert summary["total_deprecated"] == 18
        assert "migration_strategies" in summary


class TestConsolidationStrategies:
    """Tests for consolidation strategy specifics."""

    def test_direct_replacement_strategy(self):
        """Test direct replacement strategy has correct configuration."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        
        direct_replacements = [o for o in all_deprecated 
                              if o.consolidation_strategy == ConsolidationStrategy.DIRECT_REPLACEMENT]
        assert len(direct_replacements) >= 4
        
        for orch in direct_replacements:
            assert orch.migration_target is not None

    def test_extraction_strategy(self):
        """Test functionality extraction strategy."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        
        extractions = [o for o in all_deprecated 
                      if o.consolidation_strategy == ConsolidationStrategy.FUNCTIONALITY_EXTRACTION]
        assert len(extractions) >= 3
        
        for orch in extractions:
            assert orch.migration_target is not None

    def test_adapter_pattern_strategy(self):
        """Test adapter pattern strategy."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        
        adapters = [o for o in all_deprecated 
                   if o.consolidation_strategy == ConsolidationStrategy.ADAPTER_PATTERN]
        assert len(adapters) >= 1

    def test_feature_flag_strategy(self):
        """Test feature flag strategy."""
        registry = DeprecatedOrchestratorsRegistry()
        all_deprecated = registry.get_all_deprecated()
        
        feature_flags = [o for o in all_deprecated 
                        if o.consolidation_strategy == ConsolidationStrategy.FEATURE_FLAG]
        assert len(feature_flags) >= 1


class TestMigrationPlanning:
    """Tests for detailed migration planning."""

    def test_composition_engine_migration(self):
        """Test planning for composition_engine migration."""
        migrator = DeprecatedOrchestratorMigrator()
        registry = DeprecatedOrchestratorsRegistry()
        
        composition = [o for o in registry.get_all_deprecated() if o.name == "composition_engine"][0]
        plan = migrator.create_migration_plan(composition)
        
        assert plan is not None
        assert composition.migration_target == "OrchestratorCompositionStrategy"
        assert len(plan.validation_tests) == 3

    def test_orchestrator_factories_migration(self):
        """Test planning for orchestrator_factories migration."""
        migrator = DeprecatedOrchestratorMigrator()
        registry = DeprecatedOrchestratorsRegistry()
        
        factories = [o for o in registry.get_all_deprecated() if o.name == "orchestrator_factories"][0]
        plan = migrator.create_migration_plan(factories)
        
        assert plan is not None
        assert factories.migration_target == "OrchestratorFactoryStrategy"

    def test_discovery_orchestrator_migration(self):
        """Test planning for discovery_orchestrator migration."""
        migrator = DeprecatedOrchestratorMigrator()
        registry = DeprecatedOrchestratorsRegistry()
        
        discovery = [o for o in registry.get_all_deprecated() if o.name == "discovery_orchestrator"][0]
        plan = migrator.create_migration_plan(discovery)
        
        assert plan is not None
        assert discovery.migration_target == "DiscoveryComponent"


# AC_COMPLETE: AC-WAVE7T3-PB-TEST-001 ✅ 22 test cases for deprecated orchestrator migration
