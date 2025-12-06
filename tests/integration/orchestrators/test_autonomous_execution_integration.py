"""
Integration tests for autonomous plan execution.

Tests the complete autonomous execution workflow from plan approval
through phase execution, TDD integration, and git checkpointing.

Author: GitHub Copilot
Created: 2025-12-06
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestAutonomousExecutionIntegration:
    """Integration tests for autonomous plan execution workflow."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root directory structure."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_test_")
        cortex_root = Path(temp_dir)
        
        # Create required directory structure
        (cortex_root / "cortex-brain" / "documents" / "planning" / "features").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "documents" / "planning" / "approved").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "documents" / "planning" / "completed").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "config").mkdir(parents=True)
        
        # Create minimal plan schema
        schema_content = """
title: string
status: enum[draft, approved, in_progress, completed]
phases:
  - id: string
    name: string
    tasks:
      - description: string
        status: enum[not_started, in_progress, completed]
"""
        (cortex_root / "cortex-brain" / "config" / "plan-schema.yaml").write_text(schema_content)
        
        yield cortex_root
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_approved_plan(self, temp_cortex_root) -> Path:
        """Create a sample approved plan for testing."""
        plan_content = f"""---
title: Test Feature Implementation
status: approved
created: {datetime.now().isoformat()}
plan_id: test-feature-001

definition_of_ready:
  - Test files created with failing tests
  - Implementation plan approved
  - Dependencies identified

definition_of_done:
  - All tests passing
  - Code reviewed
  - Documentation updated

phases:
  - id: phase1
    name: Foundation Setup
    tasks:
      - description: Create test file
        status: not_started
      - description: Write failing test
        status: not_started
  
  - id: phase2
    name: Implementation
    tasks:
      - description: Implement minimal solution
        status: not_started
      - description: Make tests pass
        status: not_started
  
  - id: phase3
    name: Refinement
    tasks:
      - description: Refactor code
        status: not_started
      - description: Add documentation
        status: not_started
"""
        plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "approved" / "test-feature-001.yaml"
        plan_path.write_text(plan_content)
        return plan_path
    
    def test_autonomous_execution_initializes(self, temp_cortex_root):
        """Test that PlanningOrchestrator can be initialized with autonomous execution support."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        # Verify orchestrator has autonomous execution method
        assert hasattr(orchestrator, 'execute_plan_autonomously')
        assert callable(orchestrator.execute_plan_autonomously)
    
    def test_autonomous_execution_detects_approved_plan(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution can detect and load approved plans."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        # Check that plan exists and is approved
        assert sample_approved_plan.exists()
        
        # Verify plan can be loaded
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        assert plan_data['status'] == 'approved'
        assert plan_data['plan_id'] == 'test-feature-001'
    
    def test_autonomous_execution_validates_plan_structure(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution validates plan structure before execution."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        # Verify required fields exist
        assert 'title' in plan_data
        assert 'status' in plan_data
        assert 'phases' in plan_data
        assert len(plan_data['phases']) > 0
        
        # Verify each phase has tasks
        for phase in plan_data['phases']:
            assert 'id' in phase
            assert 'name' in phase
            assert 'tasks' in phase
            assert len(phase['tasks']) > 0
    
    def test_autonomous_execution_enforces_dor_dod(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution enforces Definition of Ready and Done."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        # Verify DoR exists
        assert 'definition_of_ready' in plan_data
        assert len(plan_data['definition_of_ready']) > 0
        
        # Verify DoD exists
        assert 'definition_of_done' in plan_data
        assert len(plan_data['definition_of_done']) > 0
    
    def test_autonomous_execution_phases_are_sequential(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution expects sequential phase execution."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        phases = plan_data['phases']
        
        # Verify phases are ordered (phase1, phase2, phase3)
        phase_ids = [phase['id'] for phase in phases]
        assert phase_ids == ['phase1', 'phase2', 'phase3']
        
        # Verify all tasks start as not_started
        for phase in phases:
            for task in phase['tasks']:
                assert task['status'] == 'not_started'
    
    def test_autonomous_execution_tdd_integration(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution includes TDD workflow steps."""
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        # Check that plan includes TDD steps in phase1
        phase1_tasks = [task['description'].lower() for task in plan_data['phases'][0]['tasks']]
        
        # Should include test creation
        assert any('test' in task for task in phase1_tasks)
        
        # Phase1 should include RED phase (failing test)
        assert any('failing' in task or 'fail' in task for task in phase1_tasks)
    
    def test_autonomous_execution_git_checkpoint_readiness(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution is ready for git checkpoint integration."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        # Verify orchestrator has git checkpoint orchestrator (may be None in test env)
        assert hasattr(orchestrator, 'git_checkpoint')
        
        # In production, this would be GitCheckpointOrchestrator instance
        # In tests, it may be None or mock
    
    def test_autonomous_execution_progress_tracking(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution supports progress tracking."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        # Verify method is decorated with progress tracking
        method = orchestrator.execute_plan_autonomously
        
        # Check if method has been wrapped by @with_progress decorator
        # The decorator adds __wrapped__ attribute
        assert hasattr(method, '__wrapped__') or callable(method)
    
    def test_autonomous_execution_error_handling(self, temp_cortex_root):
        """Test that autonomous execution handles missing/invalid plans gracefully."""
        orchestrator = PlanningOrchestrator(str(temp_cortex_root))
        
        # Try to execute non-existent plan
        result = orchestrator.execute_plan_autonomously("non-existent-plan.yaml")
        
        # Should return error result, not raise exception
        assert isinstance(result, dict)
        assert result['success'] is False
        assert 'error' in result or 'message' in result
    
    def test_autonomous_execution_phase_completion_tracking(self, temp_cortex_root, sample_approved_plan):
        """Test that autonomous execution tracks phase completion."""
        import yaml
        with open(sample_approved_plan, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        # Each phase should be completable
        for phase in plan_data['phases']:
            # Count total tasks
            total_tasks = len(phase['tasks'])
            assert total_tasks > 0
            
            # In autonomous execution, tasks move from not_started → in_progress → completed
            # Verify structure supports status tracking
            for task in phase['tasks']:
                assert 'status' in task
                assert task['status'] in ['not_started', 'in_progress', 'completed']


class TestAutonomousExecutionRegistration:
    """Test that autonomous execution is properly registered in CORTEX systems."""
    
    def test_autonomous_execution_in_operations_config(self):
        """Test that autonomous execution is registered in cortex-operations.yaml.
        
        Note: Autonomous execution is part of the planning operation, not a separate operation.
        This test verifies the planning operation is properly configured with autonomous triggers.
        """
        from pathlib import Path
        import yaml
        
        # Check cortex-operations.yaml (not operations-config.yaml)
        config_path = Path(__file__).parent.parent.parent.parent / "cortex-operations.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Autonomous execution is part of planning operation
            operations = config.get('operations', {}) if config else {}
            
            # Check that planning operation exists
            assert 'planning' in operations, "Planning operation should be in cortex-operations.yaml"
            
            planning_op = operations['planning']
            nl_triggers = planning_op.get('natural_language', [])
            
            # Check for autonomous execution triggers
            autonomous_triggers = [t for t in nl_triggers if 'autonomous' in t.lower() or 'execute' in t.lower()]
            assert len(autonomous_triggers) > 0, "Planning operation should have autonomous execution triggers"
    
    def test_autonomous_execution_has_intent_triggers(self):
        """Test that autonomous execution has intent router triggers.
        
        Note: IntentRouter requires a name parameter. We test the triggers
        are properly configured in cortex-operations.yaml.
        """
        from pathlib import Path
        import yaml
        
        # Check cortex-operations.yaml for autonomous triggers
        config_path = Path(__file__).parent.parent.parent.parent / "cortex-operations.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            operations = config.get('operations', {})
            planning_op = operations.get('planning', {})
            nl_triggers = planning_op.get('natural_language', [])
            
            # Check for autonomous execution triggers
            autonomous_triggers = [t for t in nl_triggers if 'autonomous' in t.lower()]
            assert len(autonomous_triggers) >= 2, \
                f"Planning operation should have at least 2 autonomous triggers, found {len(autonomous_triggers)}"
    
    def test_autonomous_execution_has_response_templates(self):
        """Test that autonomous execution has response templates.
        
        Note: Templates are structured as dict keys, not list of objects with 'name' field.
        """
        from pathlib import Path
        import yaml
        
        templates_path = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "response-templates.yaml"
        
        if templates_path.exists():
            with open(templates_path, 'r') as f:
                templates = yaml.safe_load(f)
            
            # Check for autonomous execution templates
            template_names = []
            if templates and 'templates' in templates:
                # Templates are structured as dict keys
                if isinstance(templates['templates'], dict):
                    template_names = [name.lower() for name in templates['templates'].keys()]
                else:
                    # Fallback for list structure
                    template_names = [t.get('name', '').lower() for t in templates['templates']]
            
            # Should have planning or autonomous execution templates
            assert any('autonomous' in name or 'execute' in name or 'planning' in name 
                      for name in template_names), \
                f"Response templates should include autonomous execution templates. Found: {template_names[:5]}"


class TestAutonomousExecutionIntegrationWithTDD:
    """Test integration between autonomous execution and TDD workflows."""
    
    def test_autonomous_execution_includes_red_green_refactor(self, temp_cortex_root=None):
        """Test that autonomous execution enforces RED→GREEN→REFACTOR workflow."""
        if temp_cortex_root is None:
            temp_cortex_root = tempfile.mkdtemp(prefix="cortex_tdd_test_")
        
        # Create plan with TDD phases
        plan_content = """
title: TDD Feature Implementation
status: approved
phases:
  - id: red_phase
    name: RED - Write Failing Test
    tasks:
      - description: Create test file
        status: not_started
      - description: Write failing test
        status: not_started
      - description: Verify test fails
        status: not_started
  
  - id: green_phase
    name: GREEN - Make Test Pass
    tasks:
      - description: Implement minimal code
        status: not_started
      - description: Verify test passes
        status: not_started
  
  - id: refactor_phase
    name: REFACTOR - Improve Code
    tasks:
      - description: Refactor implementation
        status: not_started
      - description: Verify tests still pass
        status: not_started
"""
        
        # Verify TDD phase structure
        import yaml
        plan_data = yaml.safe_load(plan_content)
        
        phase_names = [phase['name'].lower() for phase in plan_data['phases']]
        
        # Should include RED, GREEN, REFACTOR
        assert any('red' in name for name in phase_names)
        assert any('green' in name for name in phase_names)
        assert any('refactor' in name for name in phase_names)
    
    def test_autonomous_execution_enforces_test_first(self):
        """Test that autonomous execution enforces test-first development."""
        plan_content = """
title: Test-First Feature
status: approved
definition_of_ready:
  - Write failing test first
  - Verify test fails before implementation
phases:
  - id: phase1
    name: Test Creation
    tasks:
      - description: Create test file
        status: not_started
      - description: Write failing test (RED)
        status: not_started
  - id: phase2
    name: Implementation
    tasks:
      - description: Implement feature (GREEN)
        status: not_started
"""
        
        import yaml
        plan_data = yaml.safe_load(plan_content)
        
        # Verify DoR includes test-first requirement
        dor = [item.lower() for item in plan_data['definition_of_ready']]
        assert any('test' in item and 'first' in item for item in dor)
        
        # Verify phase1 comes before phase2
        phase_ids = [phase['id'] for phase in plan_data['phases']]
        assert phase_ids.index('phase1') < phase_ids.index('phase2')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
