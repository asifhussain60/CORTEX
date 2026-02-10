"""
Tests for MarkdownSuppressionAgent root directory validation (Phase 71 S1).

Validates CORE-002 extension: Block root markdown files unless explicitly allowed.
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.enforcement_orchestrator import (
    MarkdownSuppressionAgent,
    EnforcementLevel,
    EnforcementResult,
)


class TestMarkdownSuppressionRootValidation:
    """Test suite for root directory markdown validation."""

    @pytest.fixture
    def agent(self) -> MarkdownSuppressionAgent:
        """Create agent instance for testing."""
        return MarkdownSuppressionAgent()

    # -------------------------------------------------------------------------
    # Root Directory Validation Tests
    # -------------------------------------------------------------------------

    def test_validate_root_summary_blocked(self, agent: MarkdownSuppressionAgent):
        """Root PHASE-*-SUMMARY.md files should be BLOCKED."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["/PHASE-71-SUMMARY.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        # Both pattern and root directory violations expected
        assert any("CORE-002" in v for v in result.violations)
        assert any("root directory" in v.lower() for v in result.violations)

    def test_validate_root_completion_blocked(self, agent: MarkdownSuppressionAgent):
        """Root *-COMPLETION.md files should be BLOCKED."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["PHASE-71-COMPLETION-REPORT.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0

    def test_validate_root_session_blocked(self, agent: MarkdownSuppressionAgent):
        """Root SESSION-*.md files should be BLOCKED."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["SESSION-FINAL-2026-02-10.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED

    def test_validate_root_readme_passes(self, agent: MarkdownSuppressionAgent):
        """Root README.md should PASS (explicitly allowed)."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["README.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_docs_markdown_passes(self, agent: MarkdownSuppressionAgent):
        """Markdown in docs/ directory should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["docs/guide.md", "docs/phases/phase-71.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_cortex_registry_passes(self, agent: MarkdownSuppressionAgent):
        """Markdown in cortex-registry/ should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["cortex-registry/phases/phase-71.yaml"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_mixed_root_and_docs_files(self, agent: MarkdownSuppressionAgent):
        """Mixed root and docs files should BLOCK only root violations."""
        context = {
            "intent": "DOCUMENT",
            "output_files": [
                "PHASE-71-SUMMARY.md",  # BLOCKED (pattern + root)
                "docs/phase-71.md",      # ALLOWED
                "README.md",             # ALLOWED
            ],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        # PHASE-71-SUMMARY.md triggers 2 violations (pattern + root directory)
        assert len(result.violations) == 2
        assert any("PHASE-71-SUMMARY.md" in v for v in result.violations)

    def test_validate_explicit_request_overrides_root_block(self, agent: MarkdownSuppressionAgent):
        """User explicit request should override root directory block."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["PHASE-71-SUMMARY.md"],
            "user_explicit_request": True,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS
