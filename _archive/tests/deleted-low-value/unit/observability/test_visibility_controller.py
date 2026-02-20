"""
Tests for VisibilityController (Phase 20.2 Component #1).

Authority: AC-UX-VISIBILITY-001
Rule: CORE-008 (TDD First)
"""

import pytest
import os
from unittest.mock import Mock, patch
from enum import Enum

from cortex.observability.visibility_controller import (
    VisibilityController,
    VisibilityMode,
    OrchestratorContext,
    IntelligenceFlags,
)


class TestVisibilityMode:
    """Test VisibilityMode enum."""
    
    def test_visibility_mode_values(self):
        """Test VisibilityMode has correct values."""
        assert VisibilityMode.FULL == "full"
        assert VisibilityMode.FAILURES_ONLY == "failures"
        assert VisibilityMode.OFF == "off"


class TestVisibilityController:
    """Test VisibilityController toggle logic."""
    
    @pytest.fixture
    def controller(self):
        """Create VisibilityController instance."""
        return VisibilityController()
    
    def test_controller_initializes(self, controller):
        """Test controller initializes correctly."""
        assert controller is not None
        assert controller._mode_cache is None
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"})
    def test_get_visibility_mode_env_var_full(self):
        """Test get_visibility_mode reads from environment variable (full)."""
        controller = VisibilityController()
        mode = controller.get_visibility_mode()
        
        assert mode == VisibilityMode.FULL
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "failures"})
    def test_get_visibility_mode_env_var_failures(self):
        """Test get_visibility_mode reads from environment variable (failures)."""
        controller = VisibilityController()
        mode = controller.get_visibility_mode()
        
        assert mode == VisibilityMode.FAILURES_ONLY
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "off"})
    def test_get_visibility_mode_env_var_off(self):
        """Test get_visibility_mode reads from environment variable (off)."""
        controller = VisibilityController()
        mode = controller.get_visibility_mode()
        
        assert mode == VisibilityMode.OFF
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "invalid"}, clear=True)
    def test_get_visibility_mode_invalid_env_var(self):
        """Test get_visibility_mode falls back to default for invalid env var."""
        controller = VisibilityController()
        mode = controller.get_visibility_mode()
        
        assert mode == VisibilityMode.FULL  # Default
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_visibility_mode_no_env_var(self):
        """Test get_visibility_mode defaults to FULL when no env var."""
        controller = VisibilityController()
        mode = controller.get_visibility_mode()
        
        assert mode == VisibilityMode.FULL
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"})
    def test_should_show_success_details_full_mode(self):
        """Test should_show_success_details returns True in FULL mode."""
        controller = VisibilityController()
        
        assert controller.should_show_success_details() is True
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "failures"})
    def test_should_show_success_details_failures_mode(self):
        """Test should_show_success_details returns False in FAILURES_ONLY mode."""
        controller = VisibilityController()
        
        assert controller.should_show_success_details() is False
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "off"})
    def test_should_show_success_details_off_mode(self):
        """Test should_show_success_details returns False in OFF mode."""
        controller = VisibilityController()
        
        assert controller.should_show_success_details() is False
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"})
    def test_should_show_failure_details_full_mode(self):
        """Test should_show_failure_details returns True in FULL mode."""
        controller = VisibilityController()
        
        assert controller.should_show_failure_details() is True
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "failures"})
    def test_should_show_failure_details_failures_mode(self):
        """Test should_show_failure_details returns True in FAILURES_ONLY mode."""
        controller = VisibilityController()
        
        assert controller.should_show_failure_details() is True
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "off"})
    def test_should_show_failure_details_off_mode(self):
        """Test should_show_failure_details returns False in OFF mode."""
        controller = VisibilityController()
        
        assert controller.should_show_failure_details() is False
    
    @patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"})
    def test_mode_caching(self):
        """Test visibility mode is cached after first read."""
        controller = VisibilityController()
        
        # First call
        mode1 = controller.get_visibility_mode()
        # Second call (should use cache)
        mode2 = controller.get_visibility_mode()
        
        assert mode1 == mode2
        assert mode1 == VisibilityMode.FULL


class TestOrchestratorContext:
    """Test OrchestratorContext dataclass."""
    
    def test_orchestrator_context_creation(self):
        """Test OrchestratorContext can be created."""
        context = OrchestratorContext(
            orchestrator_name="TDDOrchestrator",
            orchestrator_icon="🧪",
            current_stage=2,
            stages_completed=["Examination", "Routing"],
            intelligence_active=IntelligenceFlags(
                lens_enabled=True,
                knowledge_enabled=True,
                synthesis_enabled=True
            ),
            failure_stage=None,
            failure_reason=None
        )
        
        assert context.orchestrator_name == "TDDOrchestrator"
        assert context.orchestrator_icon == "🧪"
        assert context.current_stage == 2
        assert len(context.stages_completed) == 2
        assert context.intelligence_active.lens_enabled is True
        assert context.failure_stage is None
    
    def test_orchestrator_context_with_failure(self):
        """Test OrchestratorContext with failure stage."""
        context = OrchestratorContext(
            orchestrator_name="FixOrchestrator",
            orchestrator_icon="🔧",
            current_stage=3,
            stages_completed=["Examination", "Routing"],
            intelligence_active=IntelligenceFlags(
                lens_enabled=True,
                knowledge_enabled=False,
                synthesis_enabled=False
            ),
            failure_stage=3,
            failure_reason="CORE-013 violation detected"
        )
        
        assert context.failure_stage == 3
        assert context.failure_reason == "CORE-013 violation detected"


class TestIntelligenceFlags:
    """Test IntelligenceFlags dataclass."""
    
    def test_intelligence_flags_all_enabled(self):
        """Test IntelligenceFlags with all flags enabled."""
        flags = IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=True,
            synthesis_enabled=True
        )
        
        assert flags.lens_enabled is True
        assert flags.knowledge_enabled is True
        assert flags.synthesis_enabled is True
    
    def test_intelligence_flags_all_disabled(self):
        """Test IntelligenceFlags with all flags disabled."""
        flags = IntelligenceFlags(
            lens_enabled=False,
            knowledge_enabled=False,
            synthesis_enabled=False
        )
        
        assert flags.lens_enabled is False
        assert flags.knowledge_enabled is False
        assert flags.synthesis_enabled is False
    
    def test_intelligence_flags_mixed(self):
        """Test IntelligenceFlags with mixed flags."""
        flags = IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=False,
            synthesis_enabled=True
        )
        
        assert flags.lens_enabled is True
        assert flags.knowledge_enabled is False
        assert flags.synthesis_enabled is True


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
