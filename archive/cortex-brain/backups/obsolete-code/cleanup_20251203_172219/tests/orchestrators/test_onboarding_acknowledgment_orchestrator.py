"""
Tests for Onboarding Acknowledgment Orchestrator

Tests 3-step governance acknowledgment flow for first-time users.

Author: Asif Hussain
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.onboarding_acknowledgment_orchestrator import (
    OnboardingAcknowledgmentOrchestrator,
    OnboardingStep
)


class TestOnboardingAcknowledgmentOrchestrator:
    """Test suite for OnboardingAcknowledgmentOrchestrator."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def orchestrator(self, temp_db):
        """Create orchestrator instance with temp database."""
        return OnboardingAcknowledgmentOrchestrator(db_path=temp_db)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.governance is not None
        assert orchestrator.current_step == OnboardingStep.WELCOME
    
    def test_needs_onboarding_new_user(self, orchestrator):
        """Test needs_onboarding returns True for new users."""
        assert orchestrator.needs_onboarding() is True
    
    def test_needs_onboarding_returning_user(self, orchestrator):
        """Test needs_onboarding returns False for returning users."""
        # Record acknowledgment
        orchestrator.record_acknowledgment()
        
        # Should not need onboarding again
        assert orchestrator.needs_onboarding() is False
    
    def test_get_onboarding_status_new_user(self, orchestrator):
        """Test onboarding status for new user."""
        status = orchestrator.get_onboarding_status()
        
        assert status is not None
        assert "acknowledged" in status
        assert status["acknowledged"] is False
    
    def test_get_onboarding_status_acknowledged_user(self, orchestrator):
        """Test onboarding status for acknowledged user."""
        # Record acknowledgment
        orchestrator.record_acknowledgment()
        
        status = orchestrator.get_onboarding_status()
        
        assert status is not None
        assert status["acknowledged"] is True
        assert "acknowledged_at" in status
    
    def test_execute_step_1_welcome(self, orchestrator):
        """Test Step 1: Welcome & Introduction."""
        result = orchestrator.execute_step_1_welcome()
        
        assert result is not None
        assert result["step"] == 1
        assert result["title"] == "Welcome & Introduction"
        assert "content" in result
        assert "CORTEX" in result["content"]
        assert result["next_step"] == "rulebook"
        assert result["progress"] == "1/3"
        
        # Check step progression
        assert orchestrator.current_step == OnboardingStep.RULEBOOK
    
    def test_execute_step_2_rulebook(self, orchestrator):
        """Test Step 2: Rulebook Display."""
        result = orchestrator.execute_step_2_rulebook()
        
        assert result is not None
        assert result["step"] == 2
        assert result["title"] == "Rulebook Overview"
        assert "content" in result
        assert "Definition of Ready" in result["content"]
        assert "Definition of Done" in result["content"]
        assert "TDD Enforcement" in result["content"]
        assert result["next_step"] == "acknowledgment"
        assert result["progress"] == "2/3"
        
        # Check step progression
        assert orchestrator.current_step == OnboardingStep.ACKNOWLEDGMENT
    
    def test_execute_step_3_acknowledgment(self, orchestrator):
        """Test Step 3: Acknowledgment."""
        result = orchestrator.execute_step_3_acknowledgment()
        
        assert result is not None
        assert result["step"] == 3
        assert result["title"] == "Acknowledgment & Completion"
        assert "content" in result
        assert "acknowledge" in result["content"].lower()
        assert result["next_step"] == "complete"
        assert result["progress"] == "3/3"
        
        # Check step progression
        assert orchestrator.current_step == OnboardingStep.COMPLETE
    
    def test_record_acknowledgment_success(self, orchestrator):
        """Test successful acknowledgment recording."""
        result = orchestrator.record_acknowledgment()
        
        assert result is not None
        assert result["success"] is True
        assert "message" in result
        assert "content" in result
        assert "Onboarding Complete" in result["content"]
        assert "acknowledged_at" in result
    
    def test_record_acknowledgment_persists(self, orchestrator):
        """Test acknowledgment persists across checks."""
        # Record acknowledgment
        orchestrator.record_acknowledgment()
        
        # Verify persistence
        assert orchestrator.needs_onboarding() is False
        
        status = orchestrator.get_onboarding_status()
        assert status["acknowledged"] is True
    
    def test_get_current_step(self, orchestrator):
        """Test getting current step."""
        assert orchestrator.get_current_step() == OnboardingStep.WELCOME
        
        orchestrator.execute_step_1_welcome()
        assert orchestrator.get_current_step() == OnboardingStep.RULEBOOK
        
        orchestrator.execute_step_2_rulebook()
        assert orchestrator.get_current_step() == OnboardingStep.ACKNOWLEDGMENT
    
    def test_reset_onboarding(self, orchestrator):
        """Test resetting onboarding status."""
        # Complete onboarding
        orchestrator.record_acknowledgment()
        assert orchestrator.needs_onboarding() is False
        
        # Reset
        result = orchestrator.reset_onboarding()
        assert result is True
        
        # Should need onboarding again
        assert orchestrator.needs_onboarding() is True
    
    def test_full_workflow(self, orchestrator):
        """Test complete onboarding workflow."""
        # Verify needs onboarding
        assert orchestrator.needs_onboarding() is True
        
        # Step 1: Welcome
        step1 = orchestrator.execute_step_1_welcome()
        assert step1["step"] == 1
        assert orchestrator.current_step == OnboardingStep.RULEBOOK
        
        # Step 2: Rulebook
        step2 = orchestrator.execute_step_2_rulebook()
        assert step2["step"] == 2
        assert orchestrator.current_step == OnboardingStep.ACKNOWLEDGMENT
        
        # Step 3: Acknowledgment
        step3 = orchestrator.execute_step_3_acknowledgment()
        assert step3["step"] == 3
        assert orchestrator.current_step == OnboardingStep.COMPLETE
        
        # Record acknowledgment
        result = orchestrator.record_acknowledgment()
        assert result["success"] is True
        
        # Verify no longer needs onboarding
        assert orchestrator.needs_onboarding() is False
    
    def test_content_quality_step1(self, orchestrator):
        """Test Step 1 content quality and completeness."""
        result = orchestrator.execute_step_1_welcome()
        content = result["content"]
        
        # Verify key topics covered
        assert "Governance" in content
        assert "Quality Enforcement" in content
        assert "Brain Protection" in content
        assert "Rollback Safety" in content
        assert "3-step onboarding" in content
    
    def test_content_quality_step2(self, orchestrator):
        """Test Step 2 content quality and completeness."""
        result = orchestrator.execute_step_2_rulebook()
        content = result["content"]
        
        # Verify all 7 protection layers mentioned
        assert "Definition of Ready" in content
        assert "Definition of Done" in content
        assert "TDD Enforcement" in content
        assert "Git Checkpoint System" in content
        assert "SOLID Principles" in content
        assert "Security Standards" in content or "OWASP" in content
        assert "Brain Integrity" in content
    
    def test_content_quality_step3(self, orchestrator):
        """Test Step 3 content quality and completeness."""
        result = orchestrator.execute_step_3_acknowledgment()
        content = result["content"]
        
        # Verify acknowledgment requirements
        assert "acknowledge" in content.lower()
        assert "understand" in content.lower()
        assert "governance rules" in content.lower()
        
        # Verify user rights mentioned
        assert "show rules" in content or "review rules" in content
        assert "compliance" in content.lower()
    
    def test_step_isolation(self, orchestrator):
        """Test steps can be executed independently."""
        # Execute Step 2 without Step 1
        step2 = orchestrator.execute_step_2_rulebook()
        assert step2["step"] == 2
        
        # Execute Step 3 directly
        step3 = orchestrator.execute_step_3_acknowledgment()
        assert step3["step"] == 3
    
    def test_acknowledgment_without_steps(self, orchestrator):
        """Test acknowledgment can be recorded without going through steps."""
        # Direct acknowledgment (user says "I acknowledge" immediately)
        result = orchestrator.record_acknowledgment()
        
        assert result["success"] is True
        assert orchestrator.needs_onboarding() is False
