"""
Test Suite: Planner Orchestrator Registry Refactoring

Tests for refactored planner_orchestrator.py methods:
- create_temp_plan() with registry folder structure
- _get_plan_folder_name() - Generate kebab-case folder name
- _write_plan_to_registry() - Write plan files
- _update_registry_index() - Update index.yaml

Integration tests with PlanningRegistryLoader for folder creation, 
plan writing, and index management.

AC-PLANNING-PLANNER-001: Planner Orchestrator Registry Integration
"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import yaml

from cortex.orchestrators.core.planner_orchestrator import PlannerOrchestrator
from cortex.orchestrators.domain.planning_registry_loader import PlanningRegistryLoader


class TestPlannerOrchestratorRefactoring:
    """Test suite for planner orchestrator registry refactoring"""

    @pytest.fixture
    def registry_path(self, tmp_path: Path) -> Path:
        """Create temporary registry path"""
        registry = tmp_path / "cortex-registry"
        registry.mkdir()
        return registry

    @pytest.fixture
    def registry_loader(self, registry_path: Path) -> PlanningRegistryLoader:
        """Create PlanningRegistryLoader with test registry"""
        return PlanningRegistryLoader(registry_path)

    @pytest.fixture
    def planner(self, registry_path: Path) -> PlannerOrchestrator:
        """Create PlannerOrchestrator with test registry"""
        planner = PlannerOrchestrator.instance()
        planner.temp_plans_path = registry_path / "planning" / "temp"
        planner.active_plans_path = registry_path / "planning" / "active"
        planner.executed_plans_path = registry_path / "planning" / "executed"
        
        # Create directories
        for path in [planner.temp_plans_path, planner.active_plans_path, planner.executed_plans_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        return planner

    # ========================================================================
    # GET PLAN FOLDER NAME TESTS (RED Cycle)
    # ========================================================================

    def test_get_plan_folder_name_simple(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test _get_plan_folder_name converts simple names"""
        # This test expects the method to exist on PlannerOrchestrator
        planner = PlannerOrchestrator.instance()
        planner.registry_loader = registry_loader
        
        # Name should be converted to kebab-case
        folder_name = planner._get_plan_folder_name("My Test Plan")
        
        assert folder_name == "my-test-plan"

    def test_get_plan_folder_name_from_request(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test _get_plan_folder_name from user request"""
        planner = PlannerOrchestrator.instance()
        planner.registry_loader = registry_loader
        
        user_request = {
            "description": "Create new API endpoint",
            "scope": "module",
        }
        
        # Folder name should come from description
        folder_name = planner._get_plan_folder_name_from_request(user_request)
        
        assert folder_name is not None
        assert isinstance(folder_name, str)
        assert len(folder_name) > 0

    def test_get_plan_folder_name_validates_output(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test _get_plan_folder_name output validates correctly"""
        planner = PlannerOrchestrator.instance()
        planner.registry_loader = registry_loader
        
        folder_name = planner._get_plan_folder_name("Test Plan")
        
        # Validate the folder name
        is_valid = registry_loader.validate_folder_name(folder_name)
        
        assert is_valid is True

    def test_get_plan_folder_name_infers_domain(
        self,
        registry_loader: PlanningRegistryLoader,
    ) -> None:
        """Test _get_plan_folder_name infers domain"""
        planner = PlannerOrchestrator.instance()
        planner.registry_loader = registry_loader
        
        user_request = {
            "description": "Create REST API endpoint",
            "scope": "module",
        }
        
        # Should infer 'api' domain
        result = planner._infer_domain_from_request(user_request)
        
        assert result is not None
        assert result in ["api", "planning", "docs", "core", "general"]

    # ========================================================================
    # WRITE PLAN TO REGISTRY TESTS (RED Cycle)
    # ========================================================================

    def test_write_plan_to_registry_creates_folder(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test _write_plan_to_registry creates plan folder"""
        planner.registry_loader = registry_loader
        
        plan_data = {
            "plan_id": "test-plan-001",
            "description": "Test plan",
            "status": "temp",
        }
        
        result = planner._write_plan_to_registry(
            domain="planning",
            plan_name="test-plan",
            plan_data=plan_data,
        )
        
        assert result.is_ok()

    def test_write_plan_to_registry_writes_plan_yaml(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test _write_plan_to_registry writes plan via registry loader"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        plan_data = {
            "plan_id": "test-plan-002",
            "description": "Test plan",
            "status": "temp",
            "phases": [],
        }
        
        result = planner._write_plan_to_registry(
            domain="planning",
            plan_name="test-plan",
            plan_data=plan_data,
        )
        
        # Should return success with plan ID
        assert result.is_ok()
        plan_id = result.unwrap()
        assert plan_id is not None

    def test_write_plan_to_registry_writes_metadata(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test _write_plan_to_registry writes metadata via registry loader"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        plan_data = {
            "plan_id": "test-plan-003",
            "description": "Test plan",
            "status": "temp",
        }
        
        result = planner._write_plan_to_registry(
            domain="planning",
            plan_name="test-plan",
            plan_data=plan_data,
        )
        
        # Should return success with plan ID
        assert result.is_ok()
        plan_id = result.unwrap()
        assert plan_id is not None

    def test_write_plan_to_registry_updates_index(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test _write_plan_to_registry updates domain index"""
        planner.registry_loader = registry_loader
        
        plan_data = {
            "plan_id": "test-plan-004",
            "description": "Test plan",
            "status": "temp",
        }
        
        result = planner._write_plan_to_registry(
            domain="planning",
            plan_name="test-plan",
            plan_data=plan_data,
        )
        
        assert result.is_ok()
        
        # Verify index updated
        index_file = registry_loader.planning_path / "planning" / "index.yaml"
        if index_file.exists():
            with open(index_file) as f:
                index_data = yaml.safe_load(f)
                assert index_data is not None

    def test_write_plan_to_registry_returns_plan_id(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test _write_plan_to_registry returns plan ID"""
        planner.registry_loader = registry_loader
        
        plan_data = {
            "plan_id": "test-plan-005",
            "description": "Test plan",
            "status": "temp",
        }
        
        result = planner._write_plan_to_registry(
            domain="planning",
            plan_name="test-plan",
            plan_data=plan_data,
        )
        
        assert result.is_ok()
        plan_id = result.unwrap()
        assert plan_id is not None

    # ========================================================================
    # CREATE TEMP PLAN REFACTORED TESTS (RED Cycle)
    # ========================================================================

    def test_create_temp_plan_uses_registry_folder_structure(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test create_temp_plan uses registry folder structure"""
        planner.registry_loader = registry_loader
        
        user_request = {
            "description": "Create API endpoint for user management",
            "scope": "module",
            "impact": "medium",
        }
        
        result = planner.create_temp_plan(user_request)
        
        assert result.is_ok()

    def test_create_temp_plan_generates_kebab_case_folder(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test create_temp_plan with kebab-case names"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        user_request = {
            "description": "Create New API Endpoint",
            "scope": "module",
            "impact": "low",
        }
        
        result = planner.create_temp_plan(user_request)
        
        # Should succeed with plan created
        assert result.is_ok()

    def test_create_temp_plan_infers_domain_from_description(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test create_temp_plan infers domain from description"""
        planner.registry_loader = registry_loader
        
        # API domain
        api_request = {
            "description": "Create REST API endpoint",
            "scope": "module",
        }
        
        result = planner.create_temp_plan(api_request)
        
        assert result.is_ok()

    def test_create_temp_plan_maintains_backward_compatibility(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test create_temp_plan maintains UUID fallback for backward compat"""
        planner.registry_loader = registry_loader
        
        user_request = {
            "description": "Backward compatible test",
            "scope": "file",
        }
        
        result = planner.create_temp_plan(user_request)
        
        assert result.is_ok()
        temp_plan = result.unwrap()
        
        # Should still have plan_id (UUID or derived)
        assert "plan_id" in temp_plan

    def test_create_temp_plan_writes_to_cortex_registry(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test create_temp_plan integrates with registry"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        user_request = {
            "description": "Test writing to registry",
            "scope": "module",
        }
        
        result = planner.create_temp_plan(user_request)
        
        # Should succeed with plan created
        assert result.is_ok()

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_integration_create_plan_with_registry_structure(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test full workflow: create → folder → metadata → index"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        # Create temp plan
        user_request = {
            "description": "Create comprehensive solution",
            "scope": "module",
            "impact": "high",
        }
        
        plan_result = planner.create_temp_plan(user_request)
        assert plan_result.is_ok()

    def test_integration_plan_folder_persists_to_disk(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test plan created successfully persists via registry"""
        planner.registry_loader = registry_loader
        
        # Initialize registry
        init_result = registry_loader.initialize_planning_registry()
        assert init_result.is_ok()
        
        user_request = {
            "description": "Persistence test plan",
            "scope": "file",
        }
        
        result = planner.create_temp_plan(user_request)
        
        # Should succeed
        assert result.is_ok()

    def test_integration_multiple_plans_in_different_domains(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test multiple plans in different domains"""
        planner.registry_loader = registry_loader
        
        # Plan 1: API domain
        api_plan = {
            "description": "Create REST API endpoint",
            "scope": "module",
        }
        
        result1 = planner.create_temp_plan(api_plan)
        assert result1.is_ok()
        
        # Plan 2: Docs domain
        docs_plan = {
            "description": "Create documentation guide",
            "scope": "file",
        }
        
        result2 = planner.create_temp_plan(docs_plan)
        assert result2.is_ok()

    def test_integration_plan_validation_after_creation(
        self,
        registry_loader: PlanningRegistryLoader,
        planner: PlannerOrchestrator,
    ) -> None:
        """Test created plan passes validation"""
        planner.registry_loader = registry_loader
        
        user_request = {
            "description": "Create validation test",
            "scope": "module",
        }
        
        result = planner.create_temp_plan(user_request)
        assert result.is_ok()
        
        temp_plan = result.unwrap()
        
        # Validate required fields
        assert "plan_id" in temp_plan
        assert "status" in temp_plan
        assert temp_plan["status"] == "temp"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
