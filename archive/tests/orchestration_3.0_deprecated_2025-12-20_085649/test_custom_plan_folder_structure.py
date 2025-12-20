"""
Test suite for custom plan folder structure support.

Validates that planning orchestrator correctly handles:
1. Standard plans: active/{plan_id}/
2. Custom plans: {custom_path}/ (e.g., cortex-4.0/orchestrator-migrations/)

Author: GitHub Copilot
Created: 2025-12-17
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import PlanningOrchestrator


class TestCustomPlanFolderStructure:
    """Test planning orchestrator with custom folder structures."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temp project root."""
        # Create minimal mock orchestrator for testing generate_worker_plans
        orch = MagicMock()
        orch.project_root = tmp_path
        
        # Mock unified plan generator
        orch.unified_plan_generator = MagicMock()
        orch.unified_plan_generator.generate_master_plan.return_value = "# Master Plan Content"
        orch.unified_plan_generator.generate_worker_plan.return_value = "# Worker Plan Content"
        
        # Import real method to test
        from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
        orch.generate_worker_plans = PlanningOrchestrator.generate_worker_plans.__get__(orch)
        
        return orch
    
    def test_standard_plan_folder_structure(self, orchestrator, tmp_path):
        """Test standard plan uses active/{plan_id}/ pattern."""
        plan_id = "PLAN-2024-12-17-feature"
        phases = [
            {"name": "Phase 1", "status": "pending"},
            {"name": "Phase 2", "status": "pending"}
        ]
        metadata = {
            "feature_name": "Test Feature",
            "complexity_tier": 4
        }
        
        result = orchestrator.generate_worker_plans(
            plan_id=plan_id,
            phases=phases,
            metadata=metadata
        )
        
        # Verify standard folder structure
        expected_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / plan_id
        assert expected_folder.exists(), f"Standard folder not created: {expected_folder}"
        
        # Verify master plan in correct location
        master_plan = expected_folder / "master-plan.md"
        assert master_plan.exists(), f"Master plan not found: {master_plan}"
        
        # Verify worker plans in correct location
        worker_1 = expected_folder / "WP01-Phase-1.md"
        worker_2 = expected_folder / "WP02-Phase-2.md"
        assert worker_1.exists(), f"Worker plan 1 not found: {worker_1}"
        assert worker_2.exists(), f"Worker plan 2 not found: {worker_2}"
        
        assert result['success'] is True
    
    def test_custom_plan_folder_structure(self, orchestrator, tmp_path):
        """Test custom plan with slashes uses custom path (no 'active/' prefix)."""
        plan_id = "cortex-4.0/orchestrator-migrations"
        phases = [
            {"name": "Planning Migration", "status": "pending"},
            {"name": "ADO Migration", "status": "pending"},
            {"name": "Maintenance Migration", "status": "pending"}
        ]
        metadata = {
            "feature_name": "CORTEX 4.0 Orchestrator Migrations",
            "complexity_tier": 4
        }
        
        result = orchestrator.generate_worker_plans(
            plan_id=plan_id,
            phases=phases,
            metadata=metadata
        )
        
        # Verify custom folder structure (NO 'active/' prefix)
        expected_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "cortex-4.0" / "orchestrator-migrations"
        assert expected_folder.exists(), f"Custom folder not created: {expected_folder}"
        
        # Verify NOT created under active/
        wrong_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "cortex-4.0" / "orchestrator-migrations"
        assert not wrong_folder.exists(), f"Should NOT create under active/: {wrong_folder}"
        
        # Verify master plan in custom location
        master_plan = expected_folder / "master-plan.md"
        assert master_plan.exists(), f"Master plan not in custom folder: {master_plan}"
        
        # Verify worker plans in custom location
        worker_1 = expected_folder / "WP01-Planning-Migration.md"
        worker_2 = expected_folder / "WP02-ADO-Migration.md"
        worker_3 = expected_folder / "WP03-Maintenance-Migration.md"
        assert worker_1.exists(), f"Worker plan 1 not found: {worker_1}"
        assert worker_2.exists(), f"Worker plan 2 not found: {worker_2}"
        assert worker_3.exists(), f"Worker plan 3 not found: {worker_3}"
        
        assert result['success'] is True
    
    def test_custom_plan_with_backslash(self, orchestrator, tmp_path):
        """Test custom plan with Windows-style backslashes."""
        plan_id = r"cortex-4.0\phases"
        phases = [
            {"name": "Foundation", "status": "pending"}
        ]
        metadata = {
            "feature_name": "CORTEX 4.0 Phases",
            "complexity_tier": 3
        }
        
        result = orchestrator.generate_worker_plans(
            plan_id=plan_id,
            phases=phases,
            metadata=metadata
        )
        
        # Verify custom folder structure
        expected_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "cortex-4.0" / "phases"
        assert expected_folder.exists(), f"Custom folder not created: {expected_folder}"
        
        # Verify master plan in custom location
        master_plan = expected_folder / "master-plan.md"
        assert master_plan.exists(), f"Master plan not in custom folder: {master_plan}"
        
        assert result['success'] is True
    
    def test_execution_folder_created_in_custom_location(self, orchestrator, tmp_path):
        """Test execution/ subfolder created in custom plan location."""
        plan_id = "cortex-5.0/features"
        phases = [
            {"name": "Feature 1", "status": "pending"}
        ]
        metadata = {
            "feature_name": "CORTEX 5.0 Features",
            "complexity_tier": 4
        }
        
        result = orchestrator.generate_worker_plans(
            plan_id=plan_id,
            phases=phases,
            metadata=metadata
        )
        
        # Verify execution folder in custom location
        expected_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "cortex-5.0" / "features"
        execution_folder = expected_folder / "execution"
        assert execution_folder.exists(), f"Execution folder not created: {execution_folder}"
        
        # Verify YAML file in execution folder
        yaml_file = execution_folder / "master-execution.yaml"
        assert yaml_file.exists(), f"YAML file not created: {yaml_file}"
        
        assert result['success'] is True


class TestBackwardCompatibility:
    """Test backward compatibility with existing plans."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temp project root."""
        # Create minimal mock orchestrator for testing generate_worker_plans
        orch = MagicMock()
        orch.project_root = tmp_path
        
        # Mock unified plan generator
        orch.unified_plan_generator = MagicMock()
        orch.unified_plan_generator.generate_master_plan.return_value = "# Master Plan"
        orch.unified_plan_generator.generate_worker_plan.return_value = "# Worker Plan"
        
        # Import real method to test
        from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
        orch.generate_worker_plans = PlanningOrchestrator.generate_worker_plans.__get__(orch)
        
        return orch
    
    def test_existing_plans_still_use_active_folder(self, orchestrator, tmp_path):
        """Verify existing standard plans continue working."""
        standard_plan_ids = [
            "PLAN-2024-12-01-auth",
            "PLAN-2024-12-15-payments",
            "FEATURE-001-dashboard"
        ]
        
        for plan_id in standard_plan_ids:
            phases = [{"name": "Phase 1", "status": "pending"}]
            metadata = {"feature_name": "Test", "complexity_tier": 3}
            
            result = orchestrator.generate_worker_plans(
                plan_id=plan_id,
                phases=phases,
                metadata=metadata
            )
            
            # Verify still uses active/ folder
            expected_folder = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / plan_id
            assert expected_folder.exists(), f"Standard plan should use active/: {plan_id}"
            
            assert result['success'] is True
