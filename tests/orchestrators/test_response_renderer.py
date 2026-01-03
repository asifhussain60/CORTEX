"""
Unit Tests for ResponseRenderer - Unified response rendering component.

Tests cover:
    - Tier routing (auto-detection and explicit)
    - Block selection (conditional and mandatory blocks)
    - Template rendering
    - Status emoji mapping
    - Error handling
    - Performance benchmarks
    - Template caching

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the class under test
from src.orchestrators.response_renderer import (
    ResponseRenderer,
    ResponseTier,
    OrchestratorResult,
    OrchestratorStatus
)


@pytest.fixture
def renderer():
    """Create ResponseRenderer instance with default templates."""
    # Use default templates (no file dependency)
    with patch.object(ResponseRenderer, '_load_templates') as mock_load:
        mock_load.return_value = {
            'blocks': {
                'cortex_header': {'emoji': '🧠', 'title': 'CORTEX Response'},
                'progress_tracker': {},
                'error_details': {},
                'response': {},
                'changes': {},
                'completion': {},
                'next_steps': {}
            }
        }
        return ResponseRenderer()


@pytest.fixture
def instant_result():
    """Create OrchestratorResult for INSTANT tier."""
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message="Done",
        data={}
    )


@pytest.fixture
def focused_result():
    """Create OrchestratorResult for FOCUSED tier."""
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message="Operation completed successfully with details here and some more context.",
        data={'plan_id': 'test-123'},
        execution_time_seconds=2.5
    )


@pytest.fixture
def structured_result():
    """Create OrchestratorResult for STRUCTURED tier."""
    message = "This is a multi-faceted response with significant detail. " * 10
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message=message,
        data={
            'plan_id': 'test-456',
            'phase_count': 5,
            'artifacts': ['file1.py', 'file2.py', 'file3.md']
        },
        execution_time_seconds=15.3
    )


@pytest.fixture
def comprehensive_result():
    """Create OrchestratorResult for COMPREHENSIVE tier."""
    message = "This is a comprehensive response with extensive detail and multiple sections. " * 35  # 682 tokens (>600)
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        message=message,
        data={
            'plan_id': 'test-789',
            'phase_count': 10,
            'complexity': 'high',
            'artifacts': [f'file{i}.py' for i in range(15)]
        },
        execution_time_seconds=45.7
    )


@pytest.fixture
def error_result():
    """Create OrchestratorResult for error scenarios."""
    return OrchestratorResult(
        status=OrchestratorStatus.FAILED,
        success=False,
        message="Operation failed due to invalid input",
        errors=[
            "ValueError: Invalid parameter 'foo'",
            "FileNotFoundError: config.yaml not found",
            "RuntimeError: Execution timeout"
        ]
    )


class TestTierRouting:
    """Test tier routing logic (auto-detection and explicit)."""
    
    def test_render_instant_tier(self, renderer, instant_result):
        """Test rendering with INSTANT tier (simple success)."""
        markdown = renderer.render(instant_result, tier='INSTANT')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅ Done" in markdown
        assert len(markdown) < 200  # Should be concise
    
    def test_render_focused_tier(self, renderer, focused_result):
        """Test rendering with FOCUSED tier (single concept)."""
        markdown = renderer.render(focused_result, tier='FOCUSED')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅ Operation completed successfully" in markdown
        assert "⏱️ **Duration:** 2.5s" in markdown
    
    def test_render_structured_tier(self, renderer, structured_result):
        """Test rendering with STRUCTURED tier (multi-faceted)."""
        markdown = renderer.render(structured_result, tier='STRUCTURED')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅" in markdown
        assert "📁 Artifacts Created" in markdown
        assert "file1.py" in markdown
        assert "⏱️ **Duration:** 15.3s" in markdown
    
    def test_render_comprehensive_tier(self, renderer, comprehensive_result):
        """Test rendering with COMPREHENSIVE tier (complex operation)."""
        markdown = renderer.render(comprehensive_result, tier='COMPREHENSIVE')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅" in markdown
        assert "📁 Artifacts Created" in markdown
        assert "⏱️ **Duration:** 45.7s" in markdown
        assert "---" in markdown  # Tier-specific separator
    
    def test_auto_tier_detection_instant(self, renderer, instant_result):
        """Test auto-detection of INSTANT tier."""
        markdown = renderer.render(instant_result, tier='auto')
        
        # Should be concise (INSTANT detected)
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅ Done" in markdown
    
    def test_auto_tier_detection_focused(self, renderer, focused_result):
        """Test auto-detection of FOCUSED tier."""
        markdown = renderer.render(focused_result, tier='auto')
        
        # Should include duration (FOCUSED detected)
        assert "⏱️ **Duration:**" in markdown
    
    def test_auto_tier_detection_structured(self, renderer, structured_result):
        """Test auto-detection of STRUCTURED tier."""
        markdown = renderer.render(structured_result, tier='auto')
        
        # Should include artifacts (STRUCTURED detected)
        assert "📁 Artifacts Created" in markdown
    
    def test_auto_tier_detection_comprehensive(self, renderer, comprehensive_result):
        """Test auto-detection of COMPREHENSIVE tier."""
        markdown = renderer.render(comprehensive_result, tier='auto')
        
        # Should include separator (COMPREHENSIVE detected)
        assert "---" in markdown
    
    def test_invalid_tier_fallback(self, renderer, focused_result):
        """Test that invalid tier falls back to auto-detection."""
        markdown = renderer.render(focused_result, tier='INVALID_TIER')
        
        # Should still render successfully with auto-detection
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅" in markdown


class TestBlockSelection:
    """Test block selection logic (conditional and mandatory)."""
    
    def test_block_selection_basic(self, renderer, instant_result):
        """Test that mandatory blocks are always included."""
        markdown = renderer.render(instant_result)
        
        # Mandatory blocks
        assert "## 🧠 CORTEX Response" in markdown  # cortex_header
        assert "✅" in markdown  # response body
    
    def test_block_selection_with_progress(self, renderer, focused_result):
        """Test progress block included for multi-phase operations."""
        context = {
            'multi_phase_operation': True,
            'progress': {'current': 3, 'total': 5}
        }
        markdown = renderer.render(focused_result, context=context)
        
        assert "**Progress:** 3/5 (60%)" in markdown
    
    def test_block_selection_with_errors(self, renderer, error_result):
        """Test error block included when status is FAILED."""
        markdown = renderer.render(error_result)
        
        assert "### ❌ Errors" in markdown
        assert "ValueError: Invalid parameter 'foo'" in markdown
        assert "FileNotFoundError: config.yaml not found" in markdown
        assert "RuntimeError: Execution timeout" in markdown
    
    def test_block_selection_with_artifacts(self, renderer, structured_result):
        """Test changes block included when artifacts present."""
        markdown = renderer.render(structured_result)
        
        assert "📁 Artifacts Created" in markdown
        assert "file1.py" in markdown
        assert "file2.py" in markdown
        assert "file3.md" in markdown
    
    def test_block_selection_completion_vs_next_steps(self, renderer, focused_result):
        """Test completion block for COMPLETED status."""
        markdown = renderer.render(focused_result)
        
        # Should have completion block (with duration)
        assert "⏱️ **Duration:**" in markdown
        
        # Should NOT have next steps
        assert "**Next Steps:**" not in markdown
    
    def test_block_selection_next_steps_for_running(self, renderer):
        """Test next steps block for RUNNING status."""
        running_result = OrchestratorResult(
            status=OrchestratorStatus.RUNNING,
            success=True,
            message="Operation in progress..."
        )
        
        context = {
            'next_steps': [
                "Wait for phase 2 completion",
                "Review intermediate results"
            ]
        }
        
        markdown = renderer.render(running_result, context=context)
        
        assert "**Next Steps:**" in markdown
        assert "1. Wait for phase 2 completion" in markdown
        assert "2. Review intermediate results" in markdown


class TestTemplateRendering:
    """Test template rendering and formatting."""
    
    def test_status_emoji_mapping(self, renderer):
        """Test correct emoji for each orchestrator status."""
        statuses = {
            OrchestratorStatus.COMPLETED: '✅',
            OrchestratorStatus.FAILED: '❌',
            OrchestratorStatus.CANCELLED: '🚫',
            OrchestratorStatus.RUNNING: '⏳'
        }
        
        for status, expected_emoji in statuses.items():
            result = OrchestratorResult(
                status=status,
                success=(status != OrchestratorStatus.FAILED),
                message="Test message"
            )
            markdown = renderer.render(result)
            
            assert expected_emoji in markdown, f"Expected emoji {expected_emoji} for status {status}"
    
    def test_empty_result_message(self, renderer):
        """Test handling of empty or None message."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message=""
        )
        
        markdown = renderer.render(result)
        
        # Should still render header
        assert "## 🧠 CORTEX Response" in markdown
    
    def test_artifacts_truncation(self, renderer):
        """Test that artifact list truncates after 10 items."""
        many_artifacts = [f'file{i}.py' for i in range(25)]
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Created many files",
            data={'artifacts': many_artifacts}
        )
        
        markdown = renderer.render(result)
        
        # Should show first 10
        assert "file0.py" in markdown
        assert "file9.py" in markdown
        
        # Should show truncation message
        assert "... and 15 more" in markdown
        
        # Should NOT show all 25
        assert "file24.py" not in markdown


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_template_path(self):
        """Test handling of missing template file."""
        # Should not raise exception, should use defaults
        renderer = ResponseRenderer(template_path="nonexistent.yaml")
        
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test"
        )
        
        markdown = renderer.render(result)
        assert "## 🧠 CORTEX Response" in markdown
    
    def test_block_rendering_failure(self, renderer, focused_result):
        """Test that single block failure doesn't crash entire render."""
        # Mock a block renderer to raise exception
        with patch.object(renderer, '_render_progress', side_effect=Exception("Block error")):
            context = {'multi_phase_operation': True}
            
            # Should still render successfully (skip failed block)
            markdown = renderer.render(focused_result, context=context)
            
            assert "## 🧠 CORTEX Response" in markdown
            assert "✅" in markdown
    
    def test_none_context(self, renderer, focused_result):
        """Test that None context is handled gracefully."""
        markdown = renderer.render(focused_result, context=None)
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅" in markdown
    
    def test_missing_execution_time(self, renderer):
        """Test handling of missing execution_time_seconds."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test",
            execution_time_seconds=None
        )
        
        markdown = renderer.render(result)
        
        # Should not crash, should just not show duration
        assert "## 🧠 CORTEX Response" in markdown
        assert "⏱️" not in markdown


class TestPerformance:
    """Test performance benchmarks."""
    
    def test_rendering_performance_instant(self, renderer, instant_result):
        """Test INSTANT tier renders in <2ms."""
        start = time.perf_counter()
        markdown = renderer.render(instant_result, tier='INSTANT')
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 2.0, f"INSTANT render took {duration_ms:.2f}ms (target: <2ms)"
        assert len(markdown) > 0
    
    def test_rendering_performance_focused(self, renderer, focused_result):
        """Test FOCUSED tier renders in <5ms."""
        start = time.perf_counter()
        markdown = renderer.render(focused_result, tier='FOCUSED')
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 5.0, f"FOCUSED render took {duration_ms:.2f}ms (target: <5ms)"
        assert len(markdown) > 0
    
    def test_rendering_performance_comprehensive(self, renderer, comprehensive_result):
        """Test COMPREHENSIVE tier renders in <10ms."""
        start = time.perf_counter()
        markdown = renderer.render(comprehensive_result, tier='COMPREHENSIVE')
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 10.0, f"COMPREHENSIVE render took {duration_ms:.2f}ms (target: <10ms)"
        assert len(markdown) > 0
    
    def test_template_caching(self, renderer, focused_result):
        """Test that template caching improves performance."""
        # First render (cache miss)
        start1 = time.perf_counter()
        markdown1 = renderer.render(focused_result)
        duration1_ms = (time.perf_counter() - start1) * 1000
        
        # Second render (cache hit)
        start2 = time.perf_counter()
        markdown2 = renderer.render(focused_result)
        duration2_ms = (time.perf_counter() - start2) * 1000
        
        # Second render should be at least as fast (ideally faster)
        # Allow small variance due to system noise
        assert duration2_ms <= duration1_ms * 1.5, \
            f"Cache not improving performance: {duration1_ms:.2f}ms vs {duration2_ms:.2f}ms"
        
        # Both should produce same output
        assert markdown1 == markdown2


class TestIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_planning_orchestrator_success(self, renderer):
        """Test rendering Planning v5 success response."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Plan 'user-authentication' created successfully",
            data={
                'plan_id': 'user-authentication',
                'feature_name': 'user-authentication',
                'phases_completed': 5,
                'artifacts': [
                    'cortex-brain/documents/planning/active/user-authentication/00-master-plan.md',
                    'cortex-brain/documents/planning/active/user-authentication/tracking/progress.json'
                ]
            },
            execution_time_seconds=12.3
        )
        
        markdown = renderer.render(result, tier='FOCUSED')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "✅ Plan 'user-authentication' created successfully" in markdown
        assert "📁 Artifacts Created" in markdown
        assert "00-master-plan.md" in markdown
        assert "⏱️ **Duration:** 12.3s" in markdown
    
    def test_vacuum_orchestrator_with_errors(self, renderer):
        """Test rendering Vacuum v2 error response."""
        result = OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message="Vacuum operation failed",
            errors=[
                "PermissionError: Cannot delete protected file 'config.yaml'",
                "RuntimeError: Dry-run validation failed"
            ]
        )
        
        markdown = renderer.render(result, tier='FOCUSED')
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "❌ Vacuum operation failed" in markdown
        assert "### ❌ Errors" in markdown
        assert "PermissionError" in markdown
        assert "RuntimeError" in markdown
    
    def test_multi_phase_operation_progress(self, renderer):
        """Test rendering multi-phase operation with progress."""
        result = OrchestratorResult(
            status=OrchestratorStatus.RUNNING,
            success=True,
            message="Sanitization in progress (Phase 3 of 7)"
        )
        
        context = {
            'multi_phase_operation': True,
            'progress': {'current': 3, 'total': 7},
            'next_steps': [
                "Complete Phase 4: AST transformation",
                "Review mapping file"
            ]
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "## 🧠 CORTEX Response" in markdown
        assert "⏳ Sanitization in progress" in markdown
        assert "**Progress:** 3/7 (43%)" in markdown
        assert "**Next Steps:**" in markdown
        assert "Complete Phase 4" in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
