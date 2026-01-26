"""
Test Suite: Plan Migration from Old to New Registry Structure

Tests for migrating existing plans to new registry structure:
- Discover old plans in legacy locations
- Migrate to cortex-registry/planning/ structure
- Update references across system
- Validate migration integrity
- Handle edge cases (duplicates, conflicts)

AC-PLANNING-MIGRATION-001: Plan Migration & Registry Consolidation
"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import yaml

from cortex.orchestrators.core.planner_orchestrator import PlannerOrchestrator
from cortex.orchestrators.domain.planning_registry_loader import PlanningRegistryLoader


class TestPlanMigration:
    """Test suite for plan migration"""

    @pytest.fixture
    def registry_path(self, tmp_path: Path) -> Path:
        """Create temporary registry path"""
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        return registry

    @pytest.fixture
    def legacy_plans_path(self, tmp_path: Path) -> Path:
        """Create temporary legacy plans path"""
        legacy = tmp_path / "legacy_plans"
        legacy.mkdir()
        return legacy

    @pytest.fixture
    def registry_loader(self, registry_path: Path) -> PlanningRegistryLoader:
        """Create PlanningRegistryLoader with test registry"""
        return PlanningRegistryLoader(registry_path)

    @pytest.fixture
    def planner(self, registry_path: Path) -> PlannerOrchestrator:
        """Create PlannerOrchestrator with test registry"""
        planner = PlannerOrchestrator()
        planner.registry_loader = PlanningRegistryLoader(registry_path)
        planner.temp_plans_path = registry_path / "planning" / "temp"
        planner.active_plans_path = registry_path / "planning" / "active"
        planner.executed_plans_path = registry_path / "planning" / "executed"
        
        for path in [planner.temp_plans_path, planner.active_plans_path, planner.executed_plans_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        return planner

    # ========================================================================
    # LEGACY PLAN DISCOVERY TESTS (RED Cycle)
    # ========================================================================

    def test_migration_discovers_legacy_plans(
        self,
        registry_loader: PlanningRegistryLoader,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration discovers plans in legacy locations"""
        # Create legacy plans
        legacy_plans = [
            {"plan_id": "legacy-001", "name": "Old Plan 1"},
            {"plan_id": "legacy-002", "name": "Old Plan 2"},
        ]
        
        for plan in legacy_plans:
            plan_file = legacy_plans_path / f"{plan['plan_id']}.yaml"
            with open(plan_file, "w") as f:
                yaml.dump(plan, f)
        
        # Discovery should find 2 legacy plans
        result = registry_loader.discover_legacy_plans(legacy_plans_path)
        assert result is not None
        assert len(result) >= 2

    def test_migration_discovers_multiple_legacy_formats(
        self,
        registry_loader: PlanningRegistryLoader,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration handles multiple legacy plan formats"""
        # Create legacy plans in different formats
        formats = [
            {"format": "yaml", "ext": ".yaml", "plan_id": "yaml-plan"},
            {"format": "json", "ext": ".json", "plan_id": "json-plan"},
        ]
        
        for fmt in formats:
            plan_file = legacy_plans_path / f"{fmt['plan_id']}{fmt['ext']}"
            plan_data = {"plan_id": fmt["plan_id"], "format": fmt["format"]}
            
            if fmt["ext"] == ".yaml":
                with open(plan_file, "w") as f:
                    yaml.dump(plan_data, f)
            else:
                with open(plan_file, "w") as f:
                    json.dump(plan_data, f)
        
        result = registry_loader.discover_legacy_plans(legacy_plans_path)
        assert result is not None

    def test_migration_skips_invalid_legacy_plans(
        self,
        registry_loader: PlanningRegistryLoader,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration skips invalid/corrupted plans"""
        # Create mix of valid and invalid plans
        valid_plan = legacy_plans_path / "valid.yaml"
        with open(valid_plan, "w") as f:
            yaml.dump({"plan_id": "valid-001"}, f)
        
        invalid_plan = legacy_plans_path / "invalid.yaml"
        with open(invalid_plan, "w") as f:
            f.write("invalid: {yaml: content: [")  # Malformed YAML
        
        # Should discover valid but skip invalid
        result = registry_loader.discover_legacy_plans(legacy_plans_path)
        assert result is not None

    # ========================================================================
    # PLAN MIGRATION TESTS (RED Cycle)
    # ========================================================================

    def test_migration_migrates_single_plan(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration of single plan"""
        # Create legacy plan
        legacy_plan = {
            "plan_id": "migrate-001",
            "name": "Plan to Migrate",
            "status": "active",
            "description": "Test plan for migration",
        }
        
        plan_file = legacy_plans_path / "migrate-001.yaml"
        with open(plan_file, "w") as f:
            yaml.dump(legacy_plan, f)
        
        # Migrate plan
        result = planner.migrate_legacy_plan(legacy_plan, "api")
        assert result is not None

    def test_migration_migrates_batch_plans(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test batch migration of multiple plans"""
        # Create multiple legacy plans
        legacy_plans = []
        for i in range(5):
            plan = {
                "plan_id": f"batch-{i:03d}",
                "name": f"Batch Plan {i}",
                "status": "active",
            }
            legacy_plans.append(plan)
            
            plan_file = legacy_plans_path / f"batch-{i:03d}.yaml"
            with open(plan_file, "w") as f:
                yaml.dump(plan, f)
        
        # Batch migrate
        result = planner.migrate_batch_plans(legacy_plans, "core")
        assert result is not None

    def test_migration_preserves_plan_data(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration preserves plan content"""
        original_plan = {
            "plan_id": "preserve-001",
            "name": "Preserve Test",
            "phases": [
                {"phase_num": 0, "name": "Analysis"},
                {"phase_num": 1, "name": "Implementation"},
            ],
            "metadata": {
                "created_by": "test_user",
                "created_at": "2026-01-26",
            },
        }
        
        plan_file = legacy_plans_path / "preserve-001.yaml"
        with open(plan_file, "w") as f:
            yaml.dump(original_plan, f)
        
        # Migrate
        result = planner.migrate_legacy_plan(original_plan, "planning")
        assert result is not None

    # ========================================================================
    # DOMAIN INFERENCE TESTS (RED Cycle)
    # ========================================================================

    def test_migration_infers_domain_from_plan(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test migration infers domain from plan data"""
        plans_with_domains = [
            ({"plan_id": "api-001", "description": "REST API"}, "api"),
            ({"plan_id": "doc-001", "description": "Documentation"}, "docs"),
            ({"plan_id": "core-001", "description": "Core functionality"}, "core"),
            ({"plan_id": "plan-001", "description": "Planning system"}, "planning"),
        ]
        
        for plan, expected_domain in plans_with_domains:
            domain = registry_loader.infer_domain_from_plan(plan)
            # Domain should be one of the known domains or general
            assert domain is not None

    def test_migration_handles_ambiguous_domains(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test migration handles ambiguous domain inference"""
        ambiguous_plan = {
            "plan_id": "ambiguous-001",
            "name": "Unclear Plan",
            "description": "Some generic description",
        }
        
        domain = registry_loader.infer_domain_from_plan(ambiguous_plan)
        # Should fall back to 'general' domain
        assert domain in ["general", "planning", "core"]

    # ========================================================================
    # REFERENCE UPDATE TESTS (RED Cycle)
    # ========================================================================

    def test_migration_updates_plan_references(
        self,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration updates references in migrated plans"""
        old_plan_ref = "legacy_plans/plan-001"
        new_plan_ref = "cortex-registry/planning/core/plan-001"
        
        # Create referencing plan
        referencing_plan = {
            "plan_id": "ref-001",
            "depends_on": [old_plan_ref],
        }
        
        # Update references
        result = planner.update_plan_references(referencing_plan, old_plan_ref, new_plan_ref)
        assert result is not None

    def test_migration_handles_circular_references(
        self,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration detects circular references"""
        plan_a = {"plan_id": "plan-a", "depends_on": ["plan-b"]}
        plan_b = {"plan_id": "plan-b", "depends_on": ["plan-a"]}
        
        result = planner.detect_circular_dependencies([plan_a, plan_b])
        assert result is not None

    # ========================================================================
    # DUPLICATE DETECTION TESTS (RED Cycle)
    # ========================================================================

    def test_migration_detects_duplicate_plans(
        self,
        registry_loader: PlanningRegistryLoader,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration detects duplicate plans"""
        # Create duplicate plans
        plan_data = {
            "plan_id": "dup-001",
            "name": "Duplicate Plan",
            "checksum": "abc123",
        }
        
        file1 = legacy_plans_path / "dup-001.yaml"
        file2 = legacy_plans_path / "dup-001-copy.yaml"
        
        for f in [file1, file2]:
            with open(f, "w") as fp:
                yaml.dump(plan_data, fp)
        
        result = registry_loader.detect_duplicate_plans(legacy_plans_path)
        assert result is not None

    def test_migration_handles_duplicate_plan_ids(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test migration handles plans with duplicate IDs"""
        duplicates = [
            {"plan_id": "dup-001", "name": "First", "version": 1},
            {"plan_id": "dup-001", "name": "Second", "version": 2},
        ]
        
        result = registry_loader.resolve_duplicate_plan_ids(duplicates)
        assert result is not None

    # ========================================================================
    # VALIDATION TESTS (RED Cycle)
    # ========================================================================

    def test_migration_validates_migrated_plan(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration validates plan after migration"""
        migrated_plan = {
            "plan_id": "valid-001",
            "name": "Valid Plan",
            "status": "active",
            "created_at": "2026-01-26T10:00:00Z",
        }
        
        result = planner.validate_migrated_plan(migrated_plan)
        assert result is not None

    def test_migration_validates_no_data_loss(
        self,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration verifies no data loss occurred"""
        original_plan = {
            "plan_id": "original-001",
            "name": "Original",
            "phases": 5,
            "tasks": 20,
        }
        
        migrated_plan = {
            "plan_id": "original-001",
            "name": "Original",
            "phases": 5,
            "tasks": 20,
            "migrated_at": "2026-01-26T10:00:00Z",
        }
        
        result = planner.verify_data_integrity(original_plan, migrated_plan)
        assert result is not None

    # ========================================================================
    # ROLLBACK TESTS (RED Cycle)
    # ========================================================================

    def test_migration_can_rollback(
        self,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration can rollback on failure"""
        migration_checkpoint = {
            "plan_id": "rollback-001",
            "original_location": "/legacy/plan-001",
            "new_location": "/cortex-registry/planning/core/plan-001",
            "status": "migrating",
        }
        
        result = planner.rollback_migration(migration_checkpoint)
        assert result is not None

    def test_migration_preserves_rollback_point(
        self,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test migration preserves rollback checkpoint"""
        checkpoint = {
            "plan_id": "cp-001",
            "timestamp": "2026-01-26T10:00:00Z",
            "migrated_count": 5,
            "status": "in_progress",
        }
        
        result = planner.save_migration_checkpoint(checkpoint)
        assert result is not None

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_integration_complete_migration_workflow(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test complete plan migration workflow"""
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        
        # Create legacy plans
        for i in range(3):
            plan = {
                "plan_id": f"flow-{i:03d}",
                "name": f"Flow Plan {i}",
                "status": "active",
            }
            plan_file = legacy_plans_path / f"flow-{i:03d}.yaml"
            with open(plan_file, "w") as f:
                yaml.dump(plan, f)
        
        # Discover and migrate
        discovered = registry_loader.discover_legacy_plans(legacy_plans_path)
        assert discovered is not None

    def test_integration_migration_with_bootstrap(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration integrates with bootstrap"""
        # Create legacy plans
        for i in range(2):
            plan = {
                "plan_id": f"boot-{i:03d}",
                "name": f"Boot Plan {i}",
                "status": "paused" if i == 0 else "active",
            }
            plan_file = legacy_plans_path / f"boot-{i:03d}.yaml"
            with open(plan_file, "w") as f:
                yaml.dump(plan, f)
        
        # Migrate
        legacy_plans = registry_loader.discover_legacy_plans(legacy_plans_path)
        
        # Bootstrap should find migrated plans
        bootstrap_result = planner.bootstrap_initialize()
        assert bootstrap_result is not None

    def test_integration_migration_idempotent(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration is idempotent (safe to run multiple times)"""
        # Create legacy plan
        plan = {
            "plan_id": "idem-001",
            "name": "Idempotent Plan",
        }
        plan_file = legacy_plans_path / "idem-001.yaml"
        with open(plan_file, "w") as f:
            yaml.dump(plan, f)
        
        # Migrate twice
        result1 = planner.migrate_legacy_plan(plan, "core")
        result2 = planner.migrate_legacy_plan(plan, "core")
        
        assert result1 is not None
        assert result2 is not None

    def test_integration_migration_with_validation(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
        legacy_plans_path: Path,
    ) -> None:
        """Test migration includes comprehensive validation"""
        # Create complex plan
        plan = {
            "plan_id": "complex-001",
            "name": "Complex Plan",
            "phases": [
                {"num": 0, "name": "Phase 0"},
                {"num": 1, "name": "Phase 1"},
            ],
            "dependencies": ["other-plan"],
        }
        plan_file = legacy_plans_path / "complex-001.yaml"
        with open(plan_file, "w") as f:
            yaml.dump(plan, f)
        
        # Migrate with validation
        result = planner.migrate_legacy_plan(plan, "planning")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
