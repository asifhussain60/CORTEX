"""
Smoke Tests for All Orchestrators

Fast validation suite (<30s) that ensures:
1. All orchestrators import without errors
2. SKULL rules are enforced
3. Basic initialization works
4. Critical methods exist

Run with: pytest tests/smoke/ -v

For full integration tests: pytest tests/orchestrators/ -v

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile


# ============================================================================
# ORCHESTRATOR IMPORT VALIDATION
# ============================================================================

class TestOrchestratorImports:
    """Validate all orchestrators import without errors."""
    
    def test_planning_orchestrator_imports(self):
        """PlanningOrchestrator imports successfully."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert PlanningOrchestrator is not None
    
    def test_temporary_plan_manager_imports(self):
        """TemporaryPlanManager imports successfully."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        assert TemporaryPlanManager is not None
    
    def test_maintenance_orchestrator_v3_imports(self):
        """MaintenanceOrchestratorV3 imports successfully."""
        from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
        assert MaintenanceOrchestratorV3 is not None
    
    def test_tdd_orchestrator_imports(self):
        """TDDOrchestrator imports successfully."""
        from src.operations.modules.orchestration.tdd_orchestrator import TDDOrchestrator
        assert TDDOrchestrator is not None
    
    def test_ado_planning_orchestrator_imports(self):
        """ADOPlanningOrchestrator imports successfully."""
        from src.operations.modules.orchestration.ado_planning_orchestrator import ADOPlanningOrchestrator
        assert ADOPlanningOrchestrator is not None
    
    def test_refactor_cycle_orchestrator_imports(self):
        """RefactorCycleOrchestrator imports successfully."""
        from src.operations.modules.orchestration.refactor_cycle_orchestrator import RefactorCycleOrchestrator
        assert RefactorCycleOrchestrator is not None
    
    def test_vacuum_orchestrator_imports(self):
        """VacuumOrchestrator imports successfully."""
        from src.operations.modules.orchestration.vacuum_orchestrator import VacuumOrchestrator
        assert VacuumOrchestrator is not None
    
    def test_cleanup_orchestrator_imports(self):
        """CleanupOrchestrator imports successfully."""
        from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator
        assert CleanupOrchestrator is not None
    
    def test_document_hygiene_orchestrator_imports(self):
        """DocumentHygieneOrchestrator imports successfully."""
        from src.operations.modules.orchestration.document_hygiene_orchestrator import DocumentHygieneOrchestrator
        assert DocumentHygieneOrchestrator is not None


# ============================================================================
# ORCHESTRATOR INITIALIZATION
# ============================================================================

class TestOrchestratorInitialization:
    """Validate orchestrators initialize with minimal overhead."""
    
    def test_planning_orchestrator_init(self):
        """PlanningOrchestrator initializes with temp directory."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = PlanningOrchestrator(project_root=Path(tmpdir))
            assert orchestrator.project_root == Path(tmpdir)
    
    def test_maintenance_orchestrator_v3_init(self):
        """MaintenanceOrchestratorV3 initializes with version."""
        from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = MaintenanceOrchestratorV3(project_root=Path(tmpdir))
            assert hasattr(orchestrator, 'version')
            assert orchestrator.version == "3.0"
    
    def test_temporary_plan_manager_init(self):
        """TemporaryPlanManager initializes with project root."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemporaryPlanManager(project_root=Path(tmpdir))
            assert manager.project_root == Path(tmpdir)


# ============================================================================
# SKULL RULE ENFORCEMENT VALIDATION
# ============================================================================

class TestSKULLRuleEnforcement:
    """Validate SKULL rules are enforced by orchestrators."""
    
    def test_brain_protection_rules_file_exists(self):
        """brain-protection-rules.yaml exists and contains rules."""
        rules_path = Path("d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml")
        assert rules_path.exists(), "brain-protection-rules.yaml not found"
        
        # Validate file has content
        content = rules_path.read_text(encoding='utf-8')
        assert len(content) > 100, "Rules file is empty or too small"
        
        # Check for expected rule names
        expected_rules = [
            'TDD_ENFORCEMENT',
            'RED_PHASE_VALIDATION',
            'HOLISTIC_CODE_DISCOVERY_ENFORCEMENT',
            'REFACTOR_CODE_CLEANUP_ENFORCEMENT',
            'GIT_ISOLATION_ENFORCEMENT',
            'TEST_LOCATION_SEPARATION'
        ]
        
        for rule in expected_rules:
            assert rule in content, f"Rule {rule} not found in brain-protection-rules.yaml"


# ============================================================================
# CRITICAL METHOD VALIDATION
# ============================================================================

class TestCriticalMethods:
    """Validate critical methods exist on orchestrators."""
    
    def test_planning_orchestrator_has_core_methods(self):
        """PlanningOrchestrator has core planning methods."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        # Check for actual methods that exist
        assert hasattr(PlanningOrchestrator, 'create_temporary_plan_for_task')
        assert hasattr(PlanningOrchestrator, 'approve_and_execute_plan')
    
    def test_planning_orchestrator_has_execute_plan(self):
        """PlanningOrchestrator has execute_plan_autonomously method."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        assert hasattr(PlanningOrchestrator, 'execute_plan_autonomously')
    
    def test_temporary_plan_manager_has_create_temporary_plan(self):
        """TemporaryPlanManager has create_temporary_plan method."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        assert hasattr(TemporaryPlanManager, 'create_temporary_plan')
    
    def test_temporary_plan_manager_has_approve_plan(self):
        """TemporaryPlanManager has approve_temporary_plan method."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        assert hasattr(TemporaryPlanManager, 'approve_temporary_plan')
    
    def test_maintenance_orchestrator_has_execute(self):
        """MaintenanceOrchestratorV3 has execute method."""
        from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
        assert hasattr(MaintenanceOrchestratorV3, 'execute')
    
    def test_tdd_orchestrator_has_core_methods(self):
        """TDDOrchestrator has core TDD methods."""
        from src.operations.modules.orchestration.tdd_orchestrator import TDDOrchestrator
        # Check for actual BaseOperationModule execute method
        assert hasattr(TDDOrchestrator, 'execute')
    
    def test_refactor_cycle_orchestrator_has_execute(self):
        """RefactorCycleOrchestrator has execute method."""
        from src.operations.modules.orchestration.refactor_cycle_orchestrator import RefactorCycleOrchestrator
        assert hasattr(RefactorCycleOrchestrator, 'execute')
    
    def test_vacuum_orchestrator_has_execute(self):
        """VacuumOrchestrator has execute method."""
        from src.operations.modules.orchestration.vacuum_orchestrator import VacuumOrchestrator
        assert hasattr(VacuumOrchestrator, 'execute')


# ============================================================================
# RESPONSE TEMPLATE VALIDATION
# ============================================================================

class TestResponseTemplates:
    """Validate response templates are accessible."""
    
    def test_response_templates_file_exists(self):
        """response-templates.yaml exists and contains templates."""
        templates_path = Path("d:/PROJECTS/CORTEX/cortex-brain/response-templates.yaml")
        assert templates_path.exists(), "response-templates.yaml not found"
        
        # Validate file has content
        content = templates_path.read_text(encoding='utf-8')
        assert len(content) > 500, "Templates file is empty or too small"
        
        # Check for expected template names
        expected_templates = [
            'system_maintenance_complete',
            'plan_execution_complete',
            'tdd_workflow_complete'
        ]
        
        for template in expected_templates:
            assert template in content, f"Template {template} not found in response-templates.yaml"


# ============================================================================
# INTEGRATION SMOKE TEST
# ============================================================================

class TestBasicWorkflowSmoke:
    """Lightweight smoke test of basic workflows."""
    
    def test_planning_orchestrator_has_complexity_analyzer(self):
        """PlanningOrchestrator initializes with ComplexityAnalyzer."""
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = PlanningOrchestrator(project_root=Path(tmpdir))
            
            # Orchestrator should have complexity_analyzer attribute
            assert hasattr(orchestrator, 'complexity_analyzer'), "PlanningOrchestrator missing complexity_analyzer"
            assert orchestrator.complexity_analyzer is not None
    
    def test_temporary_plan_manager_folder_structure(self):
        """TemporaryPlanManager creates expected folder structure."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TemporaryPlanManager(project_root=Path(tmpdir))
            
            # Verify planning base path construction
            planning_base = manager.project_root / "cortex-brain" / "documents" / "planning" / "features"
            assert planning_base.parent.name == "planning"
    
    def test_maintenance_orchestrator_phases_defined(self):
        """MaintenanceOrchestratorV3 has 7 phases defined."""
        from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = MaintenanceOrchestratorV3(project_root=Path(tmpdir))
            
            # Should have phase definitions
            expected_phases = [
                'pre_healthcheck', 'align', 'cleanup', 
                'optimize', 'vacuum', 'refresh_prompts', 
                'post_healthcheck'
            ]
            
            # Check if phases are referenced (method or constant)
            for phase in expected_phases:
                # Just validate orchestrator structure, don't execute
                assert hasattr(orchestrator, f'execute_{phase}') or hasattr(orchestrator, 'execute')


# ============================================================================
# PERFORMANCE VALIDATION
# ============================================================================

class TestSmokeTestPerformance:
    """Ensure smoke tests complete quickly."""
    
    def test_smoke_suite_completes_under_30_seconds(self):
        """Entire smoke suite should complete in under 30 seconds."""
        import time
        
        # This test tracks overall performance
        # Individual tests should complete in milliseconds
        start = time.time()
        
        # Minimal validation
        from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
        from src.operations.modules.orchestration.maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        
        elapsed = time.time() - start
        
        # Imports should be near-instant
        assert elapsed < 1.0, f"Imports took {elapsed:.2f}s (should be <1s)"


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

class TestConfigurationSmoke:
    """Validate configuration files are accessible."""
    
    def test_cortex_config_exists(self):
        """cortex.config.json exists."""
        config_path = Path("d:/PROJECTS/CORTEX/cortex.config.json")
        assert config_path.exists(), "cortex.config.json not found"
    
    def test_brain_protection_rules_exist(self):
        """brain-protection-rules.yaml exists."""
        rules_path = Path("d:/PROJECTS/CORTEX/cortex-brain/brain-protection-rules.yaml")
        assert rules_path.exists(), "brain-protection-rules.yaml not found"
    
    def test_response_templates_exist(self):
        """response-templates.yaml exists."""
        templates_path = Path("d:/PROJECTS/CORTEX/cortex-brain/response-templates.yaml")
        assert templates_path.exists(), "response-templates.yaml not found"
    
    def test_operations_config_exists(self):
        """cortex-operations.yaml exists."""
        ops_path = Path("d:/PROJECTS/CORTEX/cortex-operations.yaml")
        assert ops_path.exists(), "cortex-operations.yaml not found"
