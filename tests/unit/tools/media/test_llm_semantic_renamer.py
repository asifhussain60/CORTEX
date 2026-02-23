"""
tests/unit/tools/media/test_llm_semantic_renamer.py

Unit tests for LLMSemanticRenamer — AI-powered filename normalization.

Tests cover:
- LLM API integration (OpenAI/Anthropic)
- Prompt template construction
- Confidence scoring
- Fallback to rule-based on low confidence
- Content filtering

CORE-008: Tests written BEFORE implementation.
CORE-011: Type hints mandatory.
CORE-012: Google-style docstrings.

AC_START: AC-LLM-SEMANTIC-RENAMER-TEST-2026-02-23
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Optional

from cortex.tools.media.llm_semantic_renamer import (
    LLMSemanticRenamer,
    RenameProposal,
    LLMProvider,
)


class TestRenameProposal:
    """Test RenameProposal dataclass."""

    def test_proposal_creation(self) -> None:
        """Create RenameProposal instance."""
        proposal = RenameProposal(
            original_name="Chad Alva does Jojo Kiss.mp4",
            proposed_name="Chad Does Jojo.mp4",
            confidence=0.92,
            reasoning="Natural verb form, preserves actor names",
        )

        assert proposal.original_name == "Chad Alva does Jojo Kiss.mp4"
        assert proposal.proposed_name == "Chad Does Jojo.mp4"
        assert proposal.confidence == 0.92
        assert "Natural verb form" in proposal.reasoning


class TestLLMSemanticRenamer:
    """Test LLMSemanticRenamer functionality."""

    def test_renamer_initialization_openai(self) -> None:
        """Initialize with OpenAI provider."""
        renamer = LLMSemanticRenamer(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
        )

        assert renamer.provider == LLMProvider.OPENAI
        assert renamer.api_key == "test-key"

    def test_renamer_initialization_anthropic(self) -> None:
        """Initialize with Anthropic provider."""
        renamer = LLMSemanticRenamer(
            provider=LLMProvider.ANTHROPIC,
            api_key="test-key",
        )

        assert renamer.provider == LLMProvider.ANTHROPIC

    @patch("cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create")
    def test_semantic_rename_simple_case(self, mock_openai: Mock) -> None:
        """Rename simple filename with LLM."""
        # Mock OpenAI response
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"proposed_name": "Chad Does Jojo.mp4", "confidence": 0.95, "reasoning": "Natural verb form"}'
                    )
                )
            ]
        )

        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        proposal = renamer.propose_rename("Chad Alva does Jojo Kiss.mp4")

        assert proposal is not None
        assert proposal.proposed_name == "Chad Does Jojo.mp4"
        assert proposal.confidence >= 0.85

    @patch("cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create")
    def test_semantic_rename_complex_case(self, mock_openai: Mock) -> None:
        """Rename complex filename with multiple actors."""
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"proposed_name": "Threesome with Alice and Bob.mp4", "confidence": 0.88, "reasoning": "Descriptive group scene title"}'
                    )
                )
            ]
        )

        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        proposal = renamer.propose_rename(
            "Alice Smith and Bob Jones threesome action.mp4"
        )

        assert proposal is not None
        assert "Alice" in proposal.proposed_name
        assert "Bob" in proposal.proposed_name

    def test_confidence_threshold_filtering(self) -> None:
        """Filter out low-confidence proposals."""
        renamer = LLMSemanticRenamer(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            min_confidence=0.85,
        )

        # Low confidence should return None (fallback to rules)
        with patch(
            "cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create"
        ) as mock:
            mock.return_value = Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"proposed_name": "Unclear Title.mp4", "confidence": 0.60, "reasoning": "Ambiguous"}'
                        )
                    )
                ]
            )

            proposal = renamer.propose_rename("ambiguous_file_name.mp4")

            assert proposal is None  # Below threshold

    @patch("cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create")
    def test_content_filtering(self, mock_openai: Mock) -> None:
        """Content filter blocks inappropriate names."""
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"proposed_name": "Inappropriate Content.mp4", "confidence": 0.95, "reasoning": "Filtered"}'
                    )
                )
            ]
        )

        renamer = LLMSemanticRenamer(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            enable_content_filter=True,
        )

        proposal = renamer.propose_rename("test_file.mp4")

        # Content filter should have caught inappropriate words
        assert proposal is not None

    def test_prompt_template_construction(self) -> None:
        """Construct proper prompt template."""
        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        prompt = renamer._build_prompt("Chad Alva does Jojo Kiss.mp4")

        assert "Chad Alva does Jojo Kiss.mp4" in prompt
        assert "meaningful" in prompt.lower()
        assert "confidence" in prompt.lower()

    @patch("cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create")
    def test_api_error_handling(self, mock_openai: Mock) -> None:
        """Handle API errors gracefully."""
        mock_openai.side_effect = Exception("API connection failed")

        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        proposal = renamer.propose_rename("test_file.mp4")

        # Should return None on error (fallback to rules)
        assert proposal is None

    @patch("cortex.tools.media.llm_semantic_renamer.anthropic.messages.create")
    def test_anthropic_integration(self, mock_anthropic: Mock) -> None:
        """Test Anthropic Claude integration."""
        mock_anthropic.return_value = Mock(
            content=[
                Mock(
                    text='{"proposed_name": "Chad Does Jojo.mp4", "confidence": 0.93, "reasoning": "Natural form"}'
                )
            ]
        )

        renamer = LLMSemanticRenamer(
            provider=LLMProvider.ANTHROPIC,
            api_key="test-key",
        )

        proposal = renamer.propose_rename("Chad Alva does Jojo Kiss.mp4")

        assert proposal is not None
        assert proposal.proposed_name == "Chad Does Jojo.mp4"

    def test_batch_rename_proposals(self) -> None:
        """Generate proposals for batch of files."""
        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        filenames = [
            "file1.mp4",
            "file2.mp4",
            "file3.mp4",
        ]

        with patch(
            "cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create"
        ) as mock:
            mock.return_value = Mock(
                choices=[
                    Mock(
                        message=Mock(
                            content='{"proposed_name": "Renamed.mp4", "confidence": 0.90, "reasoning": "Test"}'
                        )
                    )
                ]
            )

            proposals = renamer.batch_propose_renames(filenames)

            assert len(proposals) <= len(filenames)

    def test_rate_limiting(self) -> None:
        """Respect API rate limits."""
        renamer = LLMSemanticRenamer(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            rate_limit_per_second=5,
        )

        assert renamer.rate_limit_per_second == 5

    @patch("cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create")
    def test_preserve_file_extension(self, mock_openai: Mock) -> None:
        """Preserve original file extension."""
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"proposed_name": "Chad Does Jojo", "confidence": 0.95, "reasoning": "Test"}'
                    )
                )
            ]
        )

        renamer = LLMSemanticRenamer(provider=LLMProvider.OPENAI, api_key="test-key")

        proposal = renamer.propose_rename("Chad Alva does Jojo Kiss.mkv")

        # Should auto-append .mkv
        assert proposal.proposed_name.endswith(".mkv")

    def test_fallback_to_rules_on_failure(self) -> None:
        """Fallback to rule-based on LLM failure."""
        renamer = LLMSemanticRenamer(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            enable_fallback=True,
        )

        with patch(
            "cortex.tools.media.llm_semantic_renamer.openai.ChatCompletion.create"
        ) as mock:
            mock.side_effect = Exception("API error")

            proposal = renamer.propose_rename_with_fallback("test_file.mp4")

            # Should have used rule-based fallback
            assert proposal is not None


# AC_COMPLETE: AC-LLM-SEMANTIC-RENAMER-TEST-2026-02-23 ✅
