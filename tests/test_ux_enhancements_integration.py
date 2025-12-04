"""
Integration tests for UX Enhancement features.

Tests the runtime implementation of:
1. Planning mode state management
2. Session restoration
3. Multi-request detection
4. Challenge system

Author: Asif Hussain
Created: 2025-12-04
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType


class TestPlanningModeStateManagement:
    """Test planning mode activation/deactivation."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create PlanningOrchestrator with temp paths."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create necessary directories
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (brain_path / "config").mkdir()
        
        return PlanningOrchestrator(str(cortex_root))
    
    def test_initial_state(self, orchestrator):
        """Planning mode should be inactive initially."""
        assert orchestrator.is_planning_mode_active() == False
        assert orchestrator.current_plan_context is None
    
    def test_activate_planning_mode(self, orchestrator):
        """Should activate planning mode with context."""
        context = {'feature': 'authentication'}
        orchestrator.activate_planning_mode(context)
        
        assert orchestrator.is_planning_mode_active() == True
        assert orchestrator.current_plan_context == context
    
    def test_deactivate_planning_mode(self, orchestrator):
        """Should deactivate planning mode and clear context."""
        orchestrator.activate_planning_mode({'test': 'data'})
        orchestrator.deactivate_planning_mode()
        
        assert orchestrator.is_planning_mode_active() == False
        assert orchestrator.current_plan_context is None
    
    def test_planning_mode_lifecycle(self, orchestrator):
        """Test full lifecycle: activate -> use -> deactivate."""
        # Start inactive
        assert not orchestrator.is_planning_mode_active()
        
        # Activate with context
        orchestrator.activate_planning_mode({'feature': 'dashboard'})
        assert orchestrator.is_planning_mode_active()
        assert orchestrator.current_plan_context['feature'] == 'dashboard'
        
        # Deactivate
        orchestrator.deactivate_planning_mode()
        assert not orchestrator.is_planning_mode_active()


class TestSessionRestoration:
    """Test session restoration from plan files."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with sample plan file."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        
        # Create plan directory
        plans_dir = brain_path / "documents" / "planning" / "features" / "active"
        plans_dir.mkdir(parents=True)
        
        # Create sample plan file
        plan_file = plans_dir / "test-plan.md"
        plan_content = """# Feature Plan: Authentication

## Phase 1: Setup
[X] Task 1 - Complete
[X] Task 2 - Complete
[ ] Task 3 - Pending
[ ] Task 4 - Pending

## Phase 2: Implementation
[ ] Task 5 - Pending
"""
        plan_file.write_text(plan_content, encoding='utf-8')
        
        (brain_path / "config").mkdir()
        
        return PlanningOrchestrator(str(cortex_root)), plan_file
    
    def test_restore_session_with_path(self, orchestrator):
        """Should restore session from specified plan file."""
        orch, plan_file = orchestrator
        
        result = orch.restore_session(str(plan_file))
        
        assert result['success'] == True
        assert 'plan_content' in result
        assert result['planning_mode_active'] == True
        assert 'Phase 1' in result['resume_point']['phase']
    
    def test_restore_session_finds_incomplete_task(self, orchestrator):
        """Should identify first incomplete task as resume point."""
        orch, plan_file = orchestrator
        
        result = orch.restore_session(str(plan_file))
        
        assert result['success'] == True
        assert '[ ]' in result['resume_point']['task'] or 'Pending' in result['resume_point']['task']
        assert result['resume_point']['status'] == 'incomplete'
    
    def test_restore_session_activates_planning_mode(self, orchestrator):
        """Restoration should activate planning mode."""
        orch, plan_file = orchestrator
        
        assert not orch.is_planning_mode_active()
        
        result = orch.restore_session(str(plan_file))
        
        assert orch.is_planning_mode_active()
        assert orch.current_plan_context is not None
    
    def test_restore_session_nonexistent_file(self, orchestrator):
        """Should fail gracefully for nonexistent files."""
        orch, _ = orchestrator
        
        result = orch.restore_session('/nonexistent/plan.md')
        
        assert result['success'] == False
        assert 'not found' in result['error'].lower()


class TestChallengeSystem:
    """Test challenge system for DoR validation."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create PlanningOrchestrator."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (brain_path / "config").mkdir()
        
        return PlanningOrchestrator(str(cortex_root))
    
    def test_challenge_no_test_strategy(self, orchestrator):
        """Should challenge lack of test strategy."""
        requirements = {
            'feature': 'authentication',
            'estimated_hours': 20
        }
        
        result = orchestrator.challenge_approach(requirements)
        
        assert result['has_challenges'] == True
        challenges = result['challenges']
        
        # Find test strategy challenge
        test_challenge = next(c for c in challenges if 'test strategy' in c['issue'].lower())
        assert test_challenge['risk'] == 'HIGH'
        assert len(test_challenge['alternatives']) == 2
    
    def test_challenge_no_error_handling(self, orchestrator):
        """Should challenge lack of error handling."""
        requirements = {
            'feature': 'API',
            'test_strategy': 'TDD',
            'estimated_hours': 15
        }
        
        result = orchestrator.challenge_approach(requirements)
        
        assert result['has_challenges'] == True
        
        # Find error handling challenge
        error_challenge = next(c for c in result['challenges'] if 'error handling' in c['issue'].lower())
        assert error_challenge['risk'] == 'MEDIUM'
    
    def test_challenge_no_security(self, orchestrator):
        """Should challenge lack of security requirements."""
        requirements = {
            'feature': 'user data',
            'test_strategy': 'TDD',
            'error_handling': 'comprehensive',
            'estimated_hours': 10
        }
        
        result = orchestrator.challenge_approach(requirements)
        
        assert result['has_challenges'] == True
        
        # Find security challenge
        security_challenge = next(c for c in result['challenges'] if 'security' in c['issue'].lower())
        assert security_challenge['risk'] == 'CRITICAL'
    
    def test_challenge_large_scope(self, orchestrator):
        """Should challenge overly large scope."""
        requirements = {
            'feature': 'complete system',
            'test_strategy': 'TDD',
            'error_handling': 'comprehensive',
            'security_requirements': 'OWASP',
            'estimated_hours': 80
        }
        
        result = orchestrator.challenge_approach(requirements)
        
        assert result['has_challenges'] == True
        
        # Find scope challenge
        scope_challenge = next(c for c in result['challenges'] if 'scope' in c['issue'].lower())
        assert scope_challenge['risk'] == 'MEDIUM'
        assert '40 hours' in scope_challenge['issue']
    
    def test_no_challenges_solid_requirements(self, orchestrator):
        """Should pass solid requirements without challenges."""
        requirements = {
            'feature': 'authentication',
            'test_strategy': 'TDD',
            'error_handling': 'comprehensive',
            'security_requirements': 'OWASP',
            'estimated_hours': 25
        }
        
        result = orchestrator.challenge_approach(requirements)
        
        assert result['has_challenges'] == False
        assert 'solid' in result['message'].lower()


class TestTemplateIntegration:
    """Test integration with response templates."""
    
    @pytest.fixture
    def orchestrator_with_templates(self, tmp_path):
        """Create orchestrator with template file."""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        
        # Create template file
        template_content = """
templates:
  work_planner_success:
    planning_mode_active: true
    session_restoration_enabled: true
"""
        template_file = brain_path / "response-templates.yaml"
        template_file.write_text(template_content)
        
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (brain_path / "config").mkdir()
        
        return PlanningOrchestrator(str(cortex_root))
    
    def test_load_template_flags(self, orchestrator_with_templates):
        """Should load flags from response templates."""
        orch = orchestrator_with_templates
        
        # Flags should be loaded during initialization
        assert hasattr(orch, 'planning_mode_active')
        assert hasattr(orch, 'session_restoration_enabled')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
