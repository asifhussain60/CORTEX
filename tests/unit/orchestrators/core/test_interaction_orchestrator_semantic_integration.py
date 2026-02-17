"""
ENH-090 RED Phase: InteractionOrchestrator + SemanticBlockAssembler Integration Tests

Authority: ENH-090 | TDD-first testing for semantic response generation
AC_START: AC-ENH090-INTERACTION-BLOCKS-001

Tests that InteractionOrchestrator dynamically assembles responses using
SemanticBlockAssembler based on intent classification and conversation context.

Key Requirements:
1. Detect user intent (IMPLEMENT/FIX/ANALYZE/AUDIT/etc)
2. Load appropriate semantic blocks for scenario
3. Assemble personality-consistent responses
4. Render for VSCode Copilot Chat
5. Track block usage metrics
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any
from pathlib import Path
from dataclasses import dataclass


# =============================================================================
# RED PHASE: Tests (expectations before implementation)
# =============================================================================


class TestInteractionOrchestratorSemanticIntegration:
    """Test InteractionOrchestrator semantic block assembly capability."""

    def test_interaction_orchestrator_loads_block_assembler(self) -> None:
        """InteractionOrchestrator must initialize SemanticBlockAssembler."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        assert hasattr(
            orchestrator, "block_assembler"
        ), "Must have block_assembler attribute"
        assert orchestrator.block_assembler is not None

    def test_interaction_orchestrator_detects_intent(self) -> None:
        """InteractionOrchestrator must classify user intent."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Test intent detection
        context = {
            "user_request": "implement a new feature for user authentication",
            "conversation_history": [],
        }

        intent = orchestrator.detect_intent(context)
        assert intent in [
            "IMPLEMENT",
            "FIX",
            "REFACTOR",
            "ANALYZE",
            "AUDIT",
            "PLAN",
        ], f"Intent must be valid, got {intent}"

    def test_interaction_orchestrator_selects_blocks_for_intent(self) -> None:
        """InteractionOrchestrator must select appropriate blocks for intent."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # For IMPLEMENT intent, should select capability-appropriate blocks
        selected_blocks = orchestrator.select_blocks_for_intent("IMPLEMENT")

        assert isinstance(selected_blocks, list), "Should return list of block names"
        assert len(selected_blocks) > 0, "Should select at least one block"
        assert all(
            isinstance(b, str) for b in selected_blocks
        ), "All blocks must be strings"

    def test_interaction_orchestrator_assembles_response(self) -> None:
        """InteractionOrchestrator must assemble semantic response."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "analyze this code",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        assert response is not None, "Must return assembled response"
        assert isinstance(response, str), "Response must be string"
        assert len(response) > 0, "Response must not be empty"

    def test_interaction_orchestrator_enforces_personality(self) -> None:
        """InteractionOrchestrator must enforce personality in responses."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "what can cortex do?",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Personality markers: knowledgeable, patient, teaching-focused
        # Should have emoji (shows personality), structure (shows organization)
        assert any(
            emoji in response for emoji in ["🧠", "✅", "🔄", "📋", "🎯"]
        ), "Response should include personality emoji markers"


class TestIntentDetectionScenarios:
    """Test intent detection across various user requests."""

    def test_detect_implement_intent(self) -> None:
        """Should detect IMPLEMENT intent from requests."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        test_cases = [
            "implement a new payment module",
            "create a validation service",
            "/implement feature",
            "build a caching layer",
        ]

        for request in test_cases:
            context = {"user_request": request, "conversation_history": []}
            intent = orchestrator.detect_intent(context)
            assert intent == "IMPLEMENT", f"Failed for: {request}"

    def test_detect_fix_intent(self) -> None:
        """Should detect FIX intent from requests."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        test_cases = [
            "fix the authentication bug",
            "there's an error in the query",
            "/fix issue",
            "debug the timeout problem",
        ]

        for request in test_cases:
            context = {"user_request": request, "conversation_history": []}
            intent = orchestrator.detect_intent(context)
            assert intent == "FIX", f"Failed for: {request}"

    def test_detect_analyze_intent(self) -> None:
        """Should detect ANALYZE intent from requests."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        test_cases = [
            "analyze the codebase",
            "what's the architecture?",
            "/analyze code",
            "show me the dependencies",
        ]

        for request in test_cases:
            context = {"user_request": request, "conversation_history": []}
            intent = orchestrator.detect_intent(context)
            assert intent == "ANALYZE", f"Failed for: {request}"


class TestBlockSelectionRules:
    """Test block selection logic for different intents."""

    def test_implement_blocks_include_tutorial(self) -> None:
        """IMPLEMENT intent should include TUTORIAL block."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        blocks = orchestrator.select_blocks_for_intent("IMPLEMENT")

        assert "tutorial" in blocks, "IMPLEMENT should include tutorial block"

    def test_analyze_blocks_include_lens(self) -> None:
        """ANALYZE intent should include LENS block."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        blocks = orchestrator.select_blocks_for_intent("ANALYZE")

        assert "lens" in blocks, "ANALYZE should include lens block"

    def test_first_interaction_includes_intro(self) -> None:
        """First user interaction should include INTRO block."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Empty history = first interaction
        context = {"user_request": "hello", "conversation_history": []}

        blocks = orchestrator.select_blocks_for_context(context)

        assert "intro" in blocks, "First interaction should include intro block"

    def test_subsequent_interaction_omits_intro(self) -> None:
        """Subsequent interactions should omit INTRO block."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        # Non-empty history = not first interaction
        context = {
            "user_request": "analyze this",
            "conversation_history": [{"role": "user", "content": "hello"}],
        }

        blocks = orchestrator.select_blocks_for_context(context)

        assert "intro" not in blocks, "Subsequent interaction should omit intro block"


class TestResponseAssemblyQuality:
    """Test response assembly meets quality standards."""

    def test_assembled_response_is_under_word_limit(self) -> None:
        """Assembled response must respect word count limits."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "implement a feature",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Count words (rough estimate: split on whitespace)
        word_count = len(response.split())

        assert (
            word_count < 2000
        ), f"Response should be under 2000 words, got {word_count}"

    def test_assembled_response_has_structure(self) -> None:
        """Assembled response must have markdown structure."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "what can you do?",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Should have markdown headers (#, ##) or lists (-, *)
        has_structure = any(
            marker in response for marker in ["##", "###", "- ", "* ", "| "]
        )

        assert (
            has_structure
        ), "Response should have markdown structure (headers, lists, tables)"

    def test_assembled_response_has_no_duplication(self) -> None:
        """Assembled response must not have duplicate content."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "analyze the code",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Split into sentences and check for duplicates
        sentences = [s.strip() for s in response.split(".") if s.strip()]
        unique_sentences = set(sentences)

        duplicate_count = len(sentences) - len(unique_sentences)

        assert (
            duplicate_count == 0
        ), f"Response should have no duplicate sentences, found {duplicate_count}"


class TestBlockAssemblyMetrics:
    """Test that block assembly tracks metrics."""

    def test_blocks_used_tracked(self) -> None:
        """Must track which blocks were used in assembly."""
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

        assert "blocks_used" in metrics, "Must track blocks_used"
        assert isinstance(metrics["blocks_used"], list), "blocks_used must be a list"

    def test_assembly_metrics_include_word_count(self) -> None:
        """Must track total word count in metrics."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "what's available?",
            "conversation_history": [],
        }

        response, metrics = orchestrator.assemble_response_with_metrics(context)

        assert "total_words" in metrics, "Must track total_words"
        assert isinstance(metrics["total_words"], int), "total_words must be int"
        assert metrics["total_words"] > 0, "total_words must be > 0"


class TestInteractionOrchestratorVsCodeRendering:
    """Test that assembled responses render correctly in VSCode."""

    def test_response_uses_markdown_tables_not_trees(self) -> None:
        """Response should use markdown tables, not ASCII tree chars."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "show orchestrators",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Should have pipe chars (tables) not tree chars in main content
        has_tables = "|" in response
        has_tree_outside_code = (
            "├─" in response or "└─" in response
        ) and "```" not in response.split("├─" if "├─" in response else "└─")[0]

        assert has_tables or (
            not has_tree_outside_code
        ), "Should use markdown tables, not tree chars outside code blocks"

    def test_response_has_proper_spacing(self) -> None:
        """Response must have proper spacing for VSCode rendering."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(conversation_protocol=mock_protocol)

        context = {
            "user_request": "test spacing",
            "conversation_history": [],
        }

        response = orchestrator.assemble_response(context)

        # Check for blank lines between sections
        sections = response.split("\n\n")

        assert len(sections) > 1, "Response should have multiple sections with spacing"


# =============================================================================
# AC_START: AC-ENH090-INTERACTION-BLOCKS-001
# =============================================================================
# 16 tests total (above)
# Test layers: Intent Detection (3 tests)
#             Block Selection (5 tests)
#             Response Quality (3 tests)
#             Metrics Tracking (2 tests)
#             VSCode Rendering (3 tests)
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
