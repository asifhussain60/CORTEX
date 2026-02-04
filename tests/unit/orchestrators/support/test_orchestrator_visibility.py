"""
Phase 20.2 Component: OrchestratorVisibility Tests (20 tests)

Tests for training wheels orchestrator visibility system.
"""

import pytest
from unittest.mock import Mock, patch
from cortex.orchestrators.support.orchestrator_visibility import (
    OrchestratorVisibility,
    generate_badge,
    generate_stage_progress,
    generate_intelligence_badge,
    should_show_visibility,
)


class TestOrchestratorVisibility:
    """Tests for OrchestratorVisibility orchestrator."""

    def test_initialization(self):
        """Test orchestrator initialization."""
        orch = OrchestratorVisibility()
        assert orch is not None
        assert orch.get_name() == "OrchestratorVisibility"

    def test_generate_visibility_header(self):
        """Test generating complete visibility header."""
        orch = OrchestratorVisibility()
        
        header = orch.generate_visibility_header(
            orchestrator_name="TDDOrchestrator",
            stage=2,
            total_stages=4,
            intelligence=["lens", "knowledge"]
        )
        
        assert "TDDOrchestrator" in header
        assert "●●○○" in header or "●●●●" in header  # Stage progress

    def test_visibility_toggle_enabled(self):
        """Test visibility when enabled."""
        orch = OrchestratorVisibility()
        
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'full'}):
            result = orch.execute({
                "orchestrator": "MasterOrchestrator",
                "stage": 1,
                "total_stages": 4
            })
            
            assert result["visible"] is True
            assert "header" in result

    def test_visibility_toggle_disabled(self):
        """Test visibility when disabled."""
        orch = OrchestratorVisibility()
        
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'off'}):
            result = orch.execute({
                "orchestrator": "MasterOrchestrator",
                "stage": 1,
                "total_stages": 4
            })
            
            assert result["visible"] is False

    def test_generate_badge_tdd(self):
        """Test TDD orchestrator badge."""
        badge = generate_badge("TDDOrchestrator")
        assert "🧪" in badge or "TDD" in badge

    def test_generate_badge_refactoring(self):
        """Test refactoring orchestrator badge."""
        badge = generate_badge("RefactoringOrchestrator")
        assert "♻️" in badge or "Refactor" in badge

    def test_generate_badge_master(self):
        """Test master orchestrator badge."""
        badge = generate_badge("MasterOrchestrator")
        assert "🧠" in badge or "Master" in badge

    def test_generate_badge_unknown(self):
        """Test unknown orchestrator badge."""
        badge = generate_badge("UnknownOrchestrator")
        assert badge is not None  # Should have default

    def test_generate_stage_progress_first(self):
        """Test stage progress at first stage."""
        progress = generate_stage_progress(stage=1, total=4)
        assert progress == "●○○○"

    def test_generate_stage_progress_mid(self):
        """Test stage progress at middle stage."""
        progress = generate_stage_progress(stage=2, total=4)
        assert progress == "●●○○"

    def test_generate_stage_progress_complete(self):
        """Test stage progress at completion."""
        progress = generate_stage_progress(stage=4, total=4)
        assert progress == "●●●●"

    def test_generate_stage_progress_failure(self):
        """Test stage progress with failure."""
        progress = generate_stage_progress(stage=2, total=4, failed=True)
        assert "✗" in progress

    def test_generate_intelligence_badge_lens(self):
        """Test LENS intelligence badge."""
        badge = generate_intelligence_badge(["lens"])
        assert "🧠" in badge or "LENS" in badge

    def test_generate_intelligence_badge_knowledge(self):
        """Test knowledge intelligence badge."""
        badge = generate_intelligence_badge(["knowledge"])
        assert "📚" in badge or "Knowledge" in badge

    def test_generate_intelligence_badge_both(self):
        """Test combined intelligence badge."""
        badge = generate_intelligence_badge(["lens", "knowledge"])
        assert "🧠" in badge or "📚" in badge

    def test_should_show_visibility_full(self):
        """Test visibility check in full mode."""
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'full'}):
            assert should_show_visibility() is True

    def test_should_show_visibility_off(self):
        """Test visibility check in off mode."""
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'off'}):
            assert should_show_visibility() is False

    def test_should_show_visibility_failures_only(self):
        """Test visibility check in failures-only mode."""
        with patch.dict('os.environ', {'CORTEX_ORCHESTRATOR_VISIBILITY': 'failures'}):
            result = should_show_visibility(failed=True)
            assert result is True

    def test_visibility_header_caching(self):
        """Test that visibility headers are cached."""
        orch = OrchestratorVisibility()
        
        header1 = orch.generate_visibility_header("TDDOrchestrator", 1, 4, [])
        header2 = orch.generate_visibility_header("TDDOrchestrator", 1, 4, [])
        
        # Same input should return cached result
        assert header1 == header2

    def test_health_check(self):
        """Test health check method."""
        orch = OrchestratorVisibility()
        health = orch.health_check()
        assert health is True or isinstance(health, dict)
