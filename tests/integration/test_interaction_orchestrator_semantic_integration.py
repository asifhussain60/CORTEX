"""
ENH-090 REFACTOR Phase: Integration Tests

Authority: ENH-090 | Full MCP → InteractionOrchestrator → SemanticBlockAssembler flow

Tests the complete integration pipeline:
- MCP gateway calls InteractionOrchestrator
- InteractionOrchestrator detects intent
- SemanticBlockAssembler assembles response
- Response has personality, structure, no duplication
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any
from pathlib import Path


class TestInteractionOrchestratorIntegration:
    """Integration tests for full semantic response pipeline."""

    def test_full_mcp_to_response_flow_implement(self) -> None:
        """Test complete flow: IMPLEMENT intent → tutorial blocks → response."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "implement a new feature for authentication",
            "conversation_history": [],
        }

        # Full pipeline
        intent = orchestrator.detect_intent(context)
        assert intent == "IMPLEMENT"

        blocks = orchestrator.select_blocks_for_context(context)
        assert "intro" in blocks  # First interaction
        assert "tutorial" in blocks  # IMPLEMENT intent

        response = orchestrator.assemble_response(context)
        assert len(response) > 0
        # Response has structure (bold, tables, etc)
        has_structure = any(m in response for m in ["**", "|", "- ", "* "])
        assert has_structure

    def test_full_mcp_to_response_flow_analyze(self) -> None:
        """Test complete flow: ANALYZE intent → lens blocks → response."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "analyze the codebase",
            "conversation_history": [{"role": "user", "content": "hello"}],
        }

        # Full pipeline
        intent = orchestrator.detect_intent(context)
        assert intent == "ANALYZE"

        blocks = orchestrator.select_blocks_for_context(context)
        assert "intro" not in blocks  # Subsequent interaction
        assert "lens" in blocks  # ANALYZE intent

        response = orchestrator.assemble_response(context)
        assert len(response) > 0

    def test_personality_consistency_across_scenarios(self) -> None:
        """Verify personality markers present across different intents."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        intents = ["IMPLEMENT", "FIX", "ANALYZE", "PLAN"]
        personality_markers = ["🧠", "✅", "🔄"]

        for intent in intents:
            # Find a request that triggers this intent
            request_map = {
                "IMPLEMENT": "implement a feature",
                "FIX": "fix the bug",
                "ANALYZE": "analyze this",
                "PLAN": "plan the roadmap",
            }

            context = {
                "user_request": request_map.get(intent, "unknown"),
                "conversation_history": [],
            }

            response = orchestrator.assemble_response(context)

            has_marker = any(m in response for m in personality_markers)
            assert has_marker, f"Response for {intent} should have personality marker"

    def test_metrics_tracked_correctly(self) -> None:
        """Verify metrics are accurate and complete."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "implement feature",
            "conversation_history": [],
        }

        response, metrics = orchestrator.assemble_response_with_metrics(context)

        # All metrics present
        assert "blocks_used" in metrics
        assert "total_words" in metrics
        assert "personality_consistent" in metrics
        assert "duplication_check_passed" in metrics
        assert "rendering_valid" in metrics

        # Metrics are correct type
        assert isinstance(metrics["blocks_used"], list)
        assert isinstance(metrics["total_words"], int)
        assert isinstance(metrics["personality_consistent"], bool)
        assert isinstance(metrics["duplication_check_passed"], bool)
        assert isinstance(metrics["rendering_valid"], bool)

        # Sanity checks
        assert len(metrics["blocks_used"]) > 0
        assert metrics["total_words"] > 0
        assert metrics["duplication_check_passed"] is True
        assert metrics["rendering_valid"] is True

    def test_response_changes_based_on_conversation_history(self) -> None:
        """First interaction includes INTRO, subsequent interactions don't."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # First interaction
        context_first = {
            "user_request": "analyze this",
            "conversation_history": [],
        }
        response_first, metrics_first = orchestrator.assemble_response_with_metrics(
            context_first
        )

        # Subsequent interaction
        context_next = {
            "user_request": "analyze this",
            "conversation_history": [{"role": "user", "content": "hello"}],
        }
        response_next, metrics_next = orchestrator.assemble_response_with_metrics(
            context_next
        )

        # First should have intro, second shouldn't
        assert "intro" in metrics_first["blocks_used"]
        assert "intro" not in metrics_next["blocks_used"]

        # Second response is shorter (no INTRO block)
        assert len(response_next) < len(response_first)

    def test_error_handling_graceful_fallback(self) -> None:
        """If block assembler unavailable, response should gracefully degrade."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Mock block_assembler to None
        orchestrator._block_assembler = None

        context = {
            "user_request": "implement feature",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Should return fallback message, not error
        assert isinstance(response, str)
        assert len(response) > 0
        assert "CORTEX" in response or "Blocks unavailable" in response or "Ready" in response


class TestIntentDetectionEdgeCases:
    """Test intent detection with edge cases."""

    def test_empty_request(self) -> None:
        """Empty request should default to ANALYZE."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {"user_request": "", "conversation_history": []}

        intent = orchestrator.detect_intent(context)
        assert intent == "ANALYZE"

    def test_mixed_keywords(self) -> None:
        """Request with multiple intent keywords should use first match."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # "implement" comes before "analyze" in precedence
        context = {
            "user_request": "implement a feature and analyze the code",
            "conversation_history": [],
        }

        intent = orchestrator.detect_intent(context)
        assert intent == "IMPLEMENT"


class TestBlockSelectionEdgeCases:
    """Test block selection with edge cases."""

    def test_unknown_intent_defaults_to_capabilities_next_steps(self) -> None:
        """Unknown intent should still select reasonable blocks."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Request with no recognizable intent keyword
        context = {
            "user_request": "xyz abc def",
            "conversation_history": [],
        }

        blocks = orchestrator.select_blocks_for_context(context)

        # Should have some reasonable default
        assert len(blocks) > 0
        assert all(isinstance(b, str) for b in blocks)

    def test_large_conversation_history(self) -> None:
        """Should handle large conversation history without error."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Large history
        history = [{"role": "user", "content": f"message {i}"} for i in range(100)]

        context = {
            "user_request": "analyze this",
            "conversation_history": history,
        }

        blocks = orchestrator.select_blocks_for_context(context)

        # Should omit INTRO (not first interaction)
        assert "intro" not in blocks
        assert len(blocks) > 0


class TestResponseQualityAssurance:
    """Test response quality standards."""

    def test_response_never_exceeds_max_words(self) -> None:
        """Response word count should respect limits."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Test various intents
        for intent_request in [
            "implement feature",
            "fix bug",
            "analyze code",
            "plan roadmap",
        ]:
            context = {
                "user_request": intent_request,
                "conversation_history": [],
            }

            response, metrics = orchestrator.assemble_response_with_metrics(context)

            word_count = len(response.split())
            assert word_count < 2000, f"Response too long: {word_count} words"

    def test_all_responses_have_structure(self) -> None:
        """All responses should have markdown structure."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        for intent_request in [
            "implement feature",
            "fix bug",
            "analyze code",
        ]:
            context = {
                "user_request": intent_request,
                "conversation_history": [],
            }

            response = orchestrator.assemble_response(context)

            # Should have some markdown structure
            has_structure = any(
                m in response for m in ["##", "###", "- ", "* ", "| ", "---"]
            )
            assert has_structure, f"Response missing structure for: {intent_request}"


# AC_COMPLETE: AC-ENH090-INTERACTION-BLOCKS-001 ✅
# 12 additional refactor/integration tests
# Total: 19 unit + 12 integration = 31 tests

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
