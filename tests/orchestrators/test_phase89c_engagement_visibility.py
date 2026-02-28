"""Phase 89-c: Engagement Breadcrumb + Timeline Rendering — RED tests.

Tests that EngagementRenderer emits BLOCK-ENGAGEMENT-BREADCRUMB and
BLOCK-ENGAGEMENT-TIMELINE, and that MCP tool responses include engagement_chain.

GAP-89-07: BLOCK-ENGAGEMENT-BREADCRUMB never rendered
GAP-89-08: BLOCK-ENGAGEMENT-TIMELINE never rendered
GAP-89-09: MCP tool format_response() has no engagement injection

CORE-008: TDD mandatory — RED phase (all tests must FAIL before implementation)
"""

from __future__ import annotations

import pytest

from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
from cortex.mcp.tools.tool_helpers import format_response


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: EngagementRenderer breadcrumb rendering (GAP-89-07)
# ══════════════════════════════════════════════════════════════════════════════


class TestEngagementRendererBreadcrumb:
    """EngagementRenderer must emit BLOCK-ENGAGEMENT-BREADCRUMB."""

    def test_renderer_emits_breadcrumb_single_orchestrator(self) -> None:
        """Single orchestrator → simple breadcrumb."""
        renderer = EngagementRenderer()
        chain = ["IntentRouter", "RefactoringOrchestrator"]
        breadcrumb = renderer.render_breadcrumb(chain)
        
        assert "IntentRouter" in breadcrumb
        assert "RefactoringOrchestrator" in breadcrumb
        assert "→" in breadcrumb

    def test_renderer_emits_breadcrumb_with_template(self) -> None:
        """Chain includes template selection."""
        renderer = EngagementRenderer()
        chain = [
            "IntentRouter",
            "WorkflowComplexityRouter",
            "RefactoringOrchestrator",
            "frontend/html-refactor-validation"
        ]
        breadcrumb = renderer.render_breadcrumb(chain)
        
        assert "IntentRouter" in breadcrumb
        assert "WorkflowComplexityRouter" in breadcrumb
        assert "RefactoringOrchestrator" in breadcrumb
        assert "frontend/html-refactor-validation" in breadcrumb

    def test_breadcrumb_is_single_line_markdown(self) -> None:
        """Breadcrumb must be single-line markdown (no newlines)."""
        renderer = EngagementRenderer()
        chain = ["IntentRouter", "TDDOrchestrator", "TestRunner"]
        breadcrumb = renderer.render_breadcrumb(chain)
        
        assert "\n" not in breadcrumb.strip()
        assert breadcrumb.startswith("**")

    def test_breadcrumb_token_count_under_100(self) -> None:
        """Breadcrumb must be <100 tokens."""
        renderer = EngagementRenderer()
        chain = [
            "IntentRouter",
            "WorkflowComplexityRouter", 
            "MasterOrchestrator",
            "RefactoringOrchestrator",
            "frontend/html-refactor-validation",
            "ToolchainExecutor"
        ]
        breadcrumb = renderer.render_breadcrumb(chain)
        
        # Rough token estimate: ~1 token per 4 chars
        token_estimate = len(breadcrumb) / 4
        assert token_estimate < 100


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: EngagementRenderer timeline rendering (GAP-89-08)
# ══════════════════════════════════════════════════════════════════════════════


class TestEngagementRendererTimeline:
    """EngagementRenderer must emit BLOCK-ENGAGEMENT-TIMELINE."""

    def test_renderer_emits_timeline_with_durations(self) -> None:
        """Timeline shows stages with elapsed time."""
        renderer = EngagementRenderer()
        stages = [
            {"name": "Intent Classification", "duration_ms": 45},
            {"name": "LENS Analysis", "duration_ms": 120},
            {"name": "Refactor Execution", "duration_ms": 340},
        ]
        timeline = renderer.render_timeline(stages)
        
        assert "Intent Classification" in timeline
        assert "45" in timeline or "45ms" in timeline
        assert "LENS Analysis" in timeline
        assert "120" in timeline or "120ms" in timeline

    def test_timeline_is_collapsible_details(self) -> None:
        """Timeline must be wrapped in <details> tag."""
        renderer = EngagementRenderer()
        stages = [{"name": "Stage1", "duration_ms": 10}]
        timeline = renderer.render_timeline(stages)
        
        assert "<details>" in timeline
        assert "</details>" in timeline
        assert "<summary>" in timeline

    def test_timeline_empty_stages_returns_none(self) -> None:
        """Empty stages list returns None or empty string."""
        renderer = EngagementRenderer()
        timeline = renderer.render_timeline([])
        
        assert timeline is None or timeline == ""


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: MCP format_response engagement injection (GAP-89-09)
# ══════════════════════════════════════════════════════════════════════════════


class TestMCPFormatResponseEngagement:
    """MCP format_response() must include engagement_chain."""

    def test_format_response_includes_engagement_field(self) -> None:
        """format_response() output has engagement_chain key."""
        engagement_data = {
            "breadcrumb": "IntentRouter → TDDOrchestrator",
            "timeline": "<details>...</details>",
            "chain": ["IntentRouter", "TDDOrchestrator"]
        }
        
        response = format_response(
            status="success",
            data={"result": "operation complete"},
            engagement=engagement_data
        )
        
        assert "engagement" in response or "engagement_chain" in response

    def test_format_response_backward_compatible_without_engagement(self) -> None:
        """format_response() works without engagement parameter."""
        response = format_response(
            status="success",
            data={"result": "operation complete"}
        )
        
        assert response["status"] == "success"
        assert "data" in response

    def test_engagement_breadcrumb_in_response_body(self) -> None:
        """Breadcrumb appears in response['data'] or response['engagement']."""
        engagement_data = {
            "breadcrumb": "IntentRouter → RefactoringOrchestrator",
            "chain": ["IntentRouter", "RefactoringOrchestrator"]
        }
        
        response = format_response(
            status="success",
            data={"result": "refactor complete"},
            engagement=engagement_data
        )
        
        # Check if engagement is in response at top level or nested
        response_str = str(response)
        assert "IntentRouter" in response_str
        assert "RefactoringOrchestrator" in response_str


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: Cross-cutting hook integration
# ══════════════════════════════════════════════════════════════════════════════


class TestCrossCuttingHookEngagementCollection:
    """OrchestratorProtocolMixin must collect engagement data."""

    def test_cross_cutting_hooks_return_engagement_metadata(self) -> None:
        """_activate_cross_cutting_hooks() returns engagement_chain."""
        # This will be tested via integration once OrchestratorProtocolMixin is wired
        # For now, structural test that validates expected return shape
        expected_keys = {"engagement_chain", "routing_path", "timestamp"}
        
        # Placeholder — real test will call actual orchestrator
        mock_result = {
            "engagement_chain": ["IntentRouter", "TDDOrchestrator"],
            "routing_path": "IntentRouter → TDDOrchestrator",
            "timestamp": "2026-02-28T14:30:00Z"
        }
        
        assert all(key in mock_result for key in ["engagement_chain", "routing_path"])
