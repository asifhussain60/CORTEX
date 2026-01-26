"""
Test Suite: Planning Registry Loader Builder Methods

Tests for builder methods in planning_registry_loader.py:
- create_plan_folder() - Create domain/plan folder structure
- register_plan() - Write plan.yaml + metadata.yaml
- initialize_planning_registry() - Scaffold empty structure
- validate_metadata_schema() - JSONSCHEMA validation
- regenerate_index_from_filesystem() - Index from folder scan

AC-PLANNING-BUILDER-001: Registry Builder Methods
"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from cortex.orchestrators.domain.planning_registry_loader import (
    PlanningRegistryLoader,
)


class TestPlanningRegistryBuilder:
    """Test suite for planning registry builder methods"""

    @pytest.fixture
    def registry_path(self, tmp_path: Path) -> Path:
        """Create temporary registry path"""
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        return registry

    @pytest.fixture
    def loader(self, registry_path: Path) -> PlanningRegistryLoader:
        """Create PlanningRegistryLoader with test registry"""
        return PlanningRegistryLoader(registry_path)

    # ========================================================================
    # INITIALIZE PLANNING REGISTRY TESTS (RED Cycle)
    # ========================================================================

    def test_initialize_planning_registry_creates_structure(
        self,
        registry_path: Path,
    ) -> None:
        """Test initialize_planning_registry creates folder structure"""
        loader = PlanningRegistryLoader(registry_path)

        result = loader.initialize_planning_registry()

        assert result.is_ok()

        # Verify structure created
        assert (registry_path / "planning").exists()
        assert (registry_path / "planning" / "index.yaml").exists()

    def test_initialize_planning_registry_creates_domains_folder(
        self,
        registry_path: Path,
    ) -> None:
        """Test initialize_planning_registry creates domains folder"""
        loader = PlanningRegistryLoader(registry_path)

        result = loader.initialize_planning_registry()

        assert result.is_ok()
        assert (registry_path / "domains").exists()

    def test_initialize_planning_registry_idempotent(
        self,
        registry_path: Path,
    ) -> None:
        """Test initialize_planning_registry is idempotent"""
        loader = PlanningRegistryLoader(registry_path)

        result1 = loader.initialize_planning_registry()
        result2 = loader.initialize_planning_registry()

        assert result1.is_ok()
        assert result2.is_ok()

    # ========================================================================
    # CREATE PLAN FOLDER TESTS (RED Cycle)
    # ========================================================================

    def test_create_plan_folder_creates_structure(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test create_plan_folder creates folder structure"""
        result = loader.create_plan_folder(
            domain="planning",
            plan_name="master-plan-v1",
        )

        assert result.is_ok()
        folder_path = result.unwrap()
        assert folder_path.exists()
        assert folder_path.name == "master-plan-v1"

    def test_create_plan_folder_path_structure(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test create_plan_folder creates correct path structure"""
        result = loader.create_plan_folder(
            domain="docs",
            plan_name="api-documentation",
        )

        assert result.is_ok()
        folder_path = result.unwrap()

        # Should be at: registry/planning/docs/api-documentation
        assert "planning" in str(folder_path)
        assert "docs" in str(folder_path)
        assert "api-documentation" in str(folder_path)

    def test_create_plan_folder_creates_subdirectories(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test create_plan_folder creates plan subdirectories"""
        result = loader.create_plan_folder(
            domain="planning",
            plan_name="test-plan",
        )

        assert result.is_ok()
        folder_path = result.unwrap()

        # Should have subdirectories
        assert (folder_path / "temp").exists()
        assert (folder_path / "artifacts").exists()

    def test_create_plan_folder_error_on_invalid_name(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test create_plan_folder rejects invalid folder name"""
        result = loader.create_plan_folder(
            domain="planning",
            plan_name="invalid name with spaces",
        )

        assert result.is_err()

    # ========================================================================
    # REGISTER PLAN TESTS (RED Cycle)
    # ========================================================================

    def test_register_plan_creates_plan_file(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test register_plan creates plan.yaml"""
        plan_data = {
            "name": "Test Plan",
            "description": "Test plan description",
            "total_phases": 3,
            "phases": [
                {"phase_num": 0, "name": "Phase 1"},
                {"phase_num": 1, "name": "Phase 2"},
            ],
        }

        result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )

        assert result.is_ok()
        plan_id = result.unwrap()

        # Verify plan file exists
        plan_folder = loader.planning_path / "planning" / plan_id
        assert (plan_folder / "plan.yaml").exists()

    def test_register_plan_creates_metadata_file(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test register_plan creates metadata.yaml"""
        plan_data = {
            "name": "Test Plan",
            "description": "Test",
            "total_phases": 1,
        }

        result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )

        assert result.is_ok()
        plan_id = result.unwrap()

        # Verify metadata file exists
        plan_folder = loader.planning_path / "planning" / plan_id
        assert (plan_folder / "metadata.yaml").exists()

    def test_register_plan_updates_index(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test register_plan updates domain index"""
        plan_data = {
            "name": "Test Plan",
            "description": "Test",
            "total_phases": 1,
        }

        result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )

        assert result.is_ok()

        # Verify domain index updated
        index_file = loader.planning_path / "planning" / "index.yaml"
        if index_file.exists():
            with open(index_file) as f:
                index_data = yaml.safe_load(f)
                assert index_data is not None

    def test_register_plan_returns_plan_id(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test register_plan returns valid plan ID"""
        plan_data = {
            "name": "My Plan",
            "description": "Test",
            "total_phases": 1,
        }

        result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )

        assert result.is_ok()
        plan_id = result.unwrap()
        assert isinstance(plan_id, str)
        assert len(plan_id) > 0

    # ========================================================================
    # VALIDATE METADATA SCHEMA TESTS (RED Cycle)
    # ========================================================================

    def test_validate_metadata_schema_valid(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test validate_metadata_schema accepts valid metadata"""
        metadata = {
            "plan_id": "AC-PLAN-001",
            "created_at": "2026-01-26T00:00:00Z",
            "epics": ["EPIC-001", "EPIC-002"],
            "features": ["FEAT-001"],
            "linked_phases": [0, 1, 2],
        }

        result = loader.validate_metadata_schema(metadata)

        assert result.is_ok()

    def test_validate_metadata_schema_missing_required_field(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test validate_metadata_schema rejects missing required fields"""
        metadata = {
            "created_at": "2026-01-26T00:00:00Z",
            # Missing plan_id
        }

        result = loader.validate_metadata_schema(metadata)

        assert result.is_err()

    def test_validate_metadata_schema_invalid_type(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test validate_metadata_schema rejects invalid types"""
        metadata = {
            "plan_id": "AC-PLAN-001",
            "created_at": "2026-01-26T00:00:00Z",
            "epics": "not-a-list",  # Should be list
        }

        result = loader.validate_metadata_schema(metadata)

        assert result.is_err()

    def test_validate_metadata_schema_empty_dict(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test validate_metadata_schema rejects empty dict"""
        result = loader.validate_metadata_schema({})

        assert result.is_err()

    # ========================================================================
    # REGENERATE INDEX TESTS (RED Cycle)
    # ========================================================================

    def test_regenerate_index_from_filesystem(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test regenerate_index_from_filesystem scans folders"""
        # Create some plan folders manually
        planning_path = loader.planning_path / "planning"
        planning_path.mkdir(parents=True, exist_ok=True)

        (planning_path / "plan-1").mkdir()
        (planning_path / "plan-2").mkdir()

        result = loader.regenerate_index_from_filesystem()

        assert result.is_ok()

        # Verify index file created
        index_file = loader.planning_path / "planning" / "index.yaml"
        assert index_file.exists()

    def test_regenerate_index_creates_index_file(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test regenerate_index_from_filesystem creates index.yaml"""
        planning_path = loader.planning_path / "planning"
        planning_path.mkdir(parents=True, exist_ok=True)

        result = loader.regenerate_index_from_filesystem()

        assert result.is_ok()

        index_file = loader.planning_path / "planning" / "index.yaml"
        assert index_file.exists()

    def test_regenerate_index_lists_all_plans(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test regenerate_index_from_filesystem lists all plans"""
        planning_path = loader.planning_path / "planning"
        planning_path.mkdir(parents=True, exist_ok=True)

        # Create domain folders with plans
        docs_path = planning_path / "docs"
        docs_path.mkdir()
        (docs_path / "api-doc-v1").mkdir()
        (docs_path / "user-guide-v2").mkdir()

        result = loader.regenerate_index_from_filesystem()

        assert result.is_ok()

        # Verify index lists plans
        index_file = loader.planning_path / "planning" / "index.yaml"
        with open(index_file) as f:
            index_data = yaml.safe_load(f)
            assert index_data is not None

    def test_regenerate_index_updates_existing(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test regenerate_index_from_filesystem updates existing index"""
        planning_path = loader.planning_path / "planning"
        planning_path.mkdir(parents=True, exist_ok=True)

        # Generate index
        result1 = loader.regenerate_index_from_filesystem()
        assert result1.is_ok()

        # Add new plan folder
        (planning_path / "new-plan").mkdir()

        # Regenerate index
        result2 = loader.regenerate_index_from_filesystem()
        assert result2.is_ok()

        # Should not error
        index_file = loader.planning_path / "planning" / "index.yaml"
        assert index_file.exists()

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_end_to_end_initialize_register_regenerate(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test full workflow: init → register → regenerate"""
        # Initialize
        init_result = loader.initialize_planning_registry()
        assert init_result.is_ok()

        # Register plan
        plan_data = {
            "name": "E2E Test Plan",
            "description": "End-to-end test",
            "total_phases": 2,
            "phases": [
                {"phase_num": 0, "name": "Phase 1"},
                {"phase_num": 1, "name": "Phase 2"},
            ],
        }

        register_result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )
        assert register_result.is_ok()

        # Regenerate index
        regen_result = loader.regenerate_index_from_filesystem()
        assert regen_result.is_ok()

    def test_create_and_register_plan(
        self,
        loader: PlanningRegistryLoader,
    ) -> None:
        """Test create_plan_folder then register_plan workflow"""
        # Create folder
        folder_result = loader.create_plan_folder(
            domain="planning",
            plan_name="workflow-test",
        )
        assert folder_result.is_ok()

        # Register plan
        plan_data = {
            "name": "Workflow Test",
            "description": "Test workflow",
            "total_phases": 1,
        }

        register_result = loader.register_plan(
            domain="planning",
            plan_data=plan_data,
        )
        assert register_result.is_ok()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
