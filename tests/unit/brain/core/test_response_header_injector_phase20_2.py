"""
Tests for ResponseHeaderInjector Phase 20.2 Enhancement.

Authority: AC-UX-VISIBILITY-001
Rule: CORE-008 (TDD First)
"""

import pytest
import os
from unittest.mock import Mock, patch
from cortex.brain.core.response_header_injector import ResponseHeaderInjector
from cortex.observability.visibility_controller import (
    OrchestratorContext,
    IntelligenceFlags,
    VisibilityMode,
)


class TestResponseHeaderInjectorPhase20_2:
    """Test Phase 20.2 enhancements to ResponseHeaderInjector."""
    
    @pytest.fixture
    def injector(self):
        """Create ResponseHeaderInjector instance."""
        return ResponseHeaderInjector()
    
    def test_format_orchestrator_badge_full_visibility(self, injector):
        """Test _format_orchestrator_badge in FULL visibility mode."""
        context = OrchestratorContext(
            orchestrator_name="TDDOrchestrator",
            orchestrator_icon="🧪",
            current_stage=3,
            stages_completed=["Examination", "Routing", "Synthesis"],
            intelligence_active=IntelligenceFlags(
                lens_enabled=True,
                knowledge_enabled=True,
                synthesis_enabled=True
            ),
            failure_stage=None,
            failure_reason=None
        )
        
        with patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
            badge = injector._format_orchestrator_badge(context)
        
        assert "🧪" in badge
        assert "TDDOrchestrator" in badge
        assert "●●●" in badge  # Stage progress
        assert "🧠📚" in badge  # Intelligence badges
    
    def test_format_orchestrator_badge_with_failure(self, injector):
        """Test _format_orchestrator_badge with failure stage."""
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
        
        with patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
            badge = injector._format_orchestrator_badge(context)
        
        assert "🔧" in badge
        assert "FixOrchestrator" in badge
        assert "✗" in badge  # Failure indicator
    
    def test_format_orchestrator_badge_off_mode_no_failure(self, injector):
        """Test _format_orchestrator_badge returns empty in OFF mode without failure."""
        context = OrchestratorContext(
            orchestrator_name="TDDOrchestrator",
            orchestrator_icon="🧪",
            current_stage=4,
            stages_completed=["Examination", "Routing", "Synthesis", "Navigation"],
            intelligence_active=IntelligenceFlags(
                lens_enabled=True,
                knowledge_enabled=True,
                synthesis_enabled=True
            ),
            failure_stage=None,
            failure_reason=None
        )
        
        with patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "off"}):
            badge = injector._format_orchestrator_badge(context)
        
        assert badge == ""
    
    def test_format_stage_progress_all_complete(self, injector):
        """Test _format_stage_progress with all stages complete."""
        progress = injector._format_stage_progress(
            current=4,
            completed=["Examination", "Routing", "Synthesis", "Navigation"],
            failed=None
        )
        
        assert progress == "●●●●"
    
    def test_format_stage_progress_partial(self, injector):
        """Test _format_stage_progress with partial completion."""
        progress = injector._format_stage_progress(
            current=2,
            completed=["Examination", "Routing"],
            failed=None
        )
        
        assert progress == "●●○○"
    
    def test_format_stage_progress_with_failure(self, injector):
        """Test _format_stage_progress with failure at stage 3."""
        progress = injector._format_stage_progress(
            current=3,
            completed=["Examination", "Routing"],
            failed=3
        )
        
        assert "●●" in progress  # First 2 stages complete
        assert "✗" in progress   # Failure indicator
    
    def test_format_intelligence_badges_full_synthesis(self, injector):
        """Test _format_intelligence_badges with full synthesis."""
        flags = IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=True,
            synthesis_enabled=True
        )
        
        badges = injector._format_intelligence_badges(flags)
        
        assert badges == "🧠📚"
    
    def test_format_intelligence_badges_lens_only(self, injector):
        """Test _format_intelligence_badges with LENS only."""
        flags = IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=False,
            synthesis_enabled=False
        )
        
        badges = injector._format_intelligence_badges(flags)
        
        assert badges == "🧠"
    
    def test_format_intelligence_badges_knowledge_only(self, injector):
        """Test _format_intelligence_badges with knowledge only."""
        flags = IntelligenceFlags(
            lens_enabled=False,
            knowledge_enabled=True,
            synthesis_enabled=False
        )
        
        badges = injector._format_intelligence_badges(flags)
        
        assert badges == "📚"
    
    def test_format_intelligence_badges_none(self, injector):
        """Test _format_intelligence_badges with no intelligence active."""
        flags = IntelligenceFlags(
            lens_enabled=False,
            knowledge_enabled=False,
            synthesis_enabled=False
        )
        
        badges = injector._format_intelligence_badges(flags)
        
        assert badges == ""
    
    def test_inject_header_with_orchestrator_context_full_mode(self, injector):
        """Test inject_header with orchestrator context in FULL mode."""
        context = OrchestratorContext(
            orchestrator_name="RefactoringOrchestrator",
            orchestrator_icon="♻️",
            current_stage=2,
            stages_completed=["Examination", "Routing"],
            intelligence_active=IntelligenceFlags(
                lens_enabled=True,
                knowledge_enabled=False,
                synthesis_enabled=False
            ),
            failure_stage=None,
            failure_reason=None
        )
        
        with patch.dict(os.environ, {"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
            header = injector.inject_header(
                operation="Refactoring",
                orchestrator_context=context
            )
        
        assert "## 🧠 CORTEX Refactoring" in header
        assert "**Author:** Asif Hussain" in header
        assert "♻️ RefactoringOrchestrator" in header
        assert "●●○○" in header
        assert "🧠" in header
    
    def test_inject_header_without_orchestrator_context(self, injector):
        """Test inject_header without orchestrator context (backward compatibility)."""
        header = injector.inject_header(operation="Implementation")
        
        assert "## 🧠 CORTEX Implementation" in header
        assert "**Author:** Asif Hussain" in header
        assert "---" in header


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
