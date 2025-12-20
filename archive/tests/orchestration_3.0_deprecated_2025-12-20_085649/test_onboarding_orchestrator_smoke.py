"""
Smoke tests for Onboarding Orchestrator.
Tests project, user, and team onboarding workflows.
"""

import pytest
from pathlib import Path

from src.orchestration_3_0.orchestrators.onboarding import (
    OnboardingOrchestrator,
    create_onboarding_orchestrator,
    ProjectOnboardingResult,
    UserOnboardingResult,
    TeamOnboardingResult
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext


class TestOnboardingOrchestrator:
    """Smoke tests for Onboarding Orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = create_onboarding_orchestrator()
        
        assert orchestrator is not None
        assert orchestrator.orchestrator_name == "OnboardingOrchestrator"
        assert orchestrator.state_machine is not None
        assert orchestrator.session_manager is not None
    
    def test_project_onboarding_workflow(self):
        """Test project onboarding workflow executes successfully."""
        orchestrator = create_onboarding_orchestrator()
        
        # Use CORTEX repo as test project
        test_project_path = str(Path("d:/PROJECTS/CORTEX").resolve())
        
        # Execute project onboarding
        result = orchestrator.onboard_project(
            project_path=test_project_path,
            template=None
        )
        
        # Verify result structure
        assert isinstance(result, ProjectOnboardingResult)
        assert result.success is True
        assert result.project_id is not None
        assert len(result.tech_stack) > 0
        assert result.dashboard_url is not None
        assert len(result.next_steps) > 0
    
    def test_user_onboarding_workflow(self):
        """Test user onboarding workflow."""
        orchestrator = create_onboarding_orchestrator()
        
        # Execute user onboarding
        result = orchestrator.onboard_user(
            role="developer",
            language="en"
        )
        
        # Verify result structure
        assert isinstance(result, UserOnboardingResult)
        assert result.success is True
        assert result.user_profile["role"] == "developer"
        assert result.tutorial_completed is True
        assert result.completion_percentage == 1.0
        assert len(result.achievements_awarded) > 0
        assert len(result.next_steps) > 0
    
    def test_team_onboarding_workflow(self):
        """Test team onboarding workflow."""
        orchestrator = create_onboarding_orchestrator()
        
        # Execute team onboarding
        result = orchestrator.onboard_team(
            team_name="Engineering Team Alpha",
            member_ids=["user1", "user2", "user3"],
            team_role="dev_team"
        )
        
        # Verify result structure
        assert isinstance(result, TeamOnboardingResult)
        assert result.success is True
        assert result.team_id is not None
        assert result.team_dashboard_url is not None
        assert result.rbac_configured is True
        assert result.member_count == 3
        assert len(result.next_steps) > 0
    
    def test_dor_validation_project(self):
        """Test Definition of Ready validation for project onboarding."""
        orchestrator = create_onboarding_orchestrator()
        
        # Valid project onboarding context
        context = WorkflowContext(
            tenant_id="test_tenant",
            project_id="test_project",
            user_id="test_user",
            session_id="test_session",
            inputs={
                "project_path": "d:/PROJECTS/CORTEX"
            },
            metadata={
                "onboarding_type": "project"
            }
        )
        
        result = orchestrator.validate_dor(context)
        
        # Should pass (project path exists)
        assert result.passed is True
    
    def test_dor_validation_user(self):
        """Test Definition of Ready validation for user onboarding."""
        orchestrator = create_onboarding_orchestrator()
        
        # Valid user onboarding context
        context = WorkflowContext(
            tenant_id="test_tenant",
            project_id="test_project",
            user_id="test_user",
            session_id="test_session",
            inputs={
                "role": "developer"
            },
            metadata={
                "onboarding_type": "user"
            }
        )
        
        result = orchestrator.validate_dor(context)
        
        # Should pass (valid role)
        assert result.passed is True
    
    def test_dod_validation_success(self):
        """Test Definition of Done validation with successful result."""
        orchestrator = create_onboarding_orchestrator()
        
        # Create context with successful onboarding result
        onboarding_result = UserOnboardingResult(
            success=True,
            user_profile={"user_id": "test_user", "role": "developer"},
            tutorial_completed=True,
            achievements_awarded=["Welcome"],
            completion_percentage=1.0,
            next_steps=["Create first plan"]
        )
        
        context = WorkflowContext(
            tenant_id="test_tenant",
            project_id="test_project",
            user_id="test_user",
            session_id="test_session",
            inputs={},
            metadata={"onboarding_type": "user"},
            outputs={"result": onboarding_result}  # DoD validation reads from outputs
        )
        
        result = orchestrator.validate_dod(context)
        
        # Should pass (tutorial completed, next steps provided)
        assert result.passed is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
