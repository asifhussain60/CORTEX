"""
Tests for MarkdownSuppressionAgent (CORE-002 enforcement).

CORE-002: Block generation of markdown files (*-summary.md, *-report.md, 
          *-plan.md, DEPLOYMENT-*.md) unless user explicitly requests them.
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.enforcement_orchestrator import (
    MarkdownSuppressionAgent,
    EnforcementLevel,
    EnforcementResult,
)


class TestMarkdownSuppressionAgent:
    """Test suite for MarkdownSuppressionAgent."""

    @pytest.fixture
    def agent(self) -> MarkdownSuppressionAgent:
        """Create agent instance for testing."""
        return MarkdownSuppressionAgent()

    # -------------------------------------------------------------------------
    # CORE-002: Markdown File Suppression Tests
    # -------------------------------------------------------------------------

    def test_validate_summary_file_blocked(self, agent: MarkdownSuppressionAgent):
        """*-summary.md file creation should be BLOCKED."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["audit-summary.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "CORE-002" in result.violations[0]
        assert "summary" in result.violations[0].lower()

    def test_validate_report_file_blocked(self, agent: MarkdownSuppressionAgent):
        """*-report.md file creation should be BLOCKED."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["health-report.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert "CORE-002" in result.violations[0]
        assert "report" in result.violations[0].lower()

    def test_validate_deployment_file_blocked(self, agent: MarkdownSuppressionAgent):
        """DEPLOYMENT-*.md file creation should be BLOCKED."""
        context = {
            "intent": "DEPLOY",
            "output_files": ["DEPLOYMENT-GUIDE.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert "CORE-002" in result.violations[0]

    def test_validate_multiple_forbidden_files_blocked(self, agent: MarkdownSuppressionAgent):
        """Multiple forbidden markdown files should be BLOCKED with all violations listed."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["audit-summary.md", "health-report.md", "DEPLOYMENT-PLAN.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        # DEPLOYMENT-PLAN.md matches both *-PLAN.md and DEPLOYMENT-*.md patterns
        assert len(result.violations) == 4
        for violation in result.violations:
            assert "CORE-002" in violation

    # -------------------------------------------------------------------------
    # User Explicit Request Exception Tests
    # -------------------------------------------------------------------------

    def test_validate_explicit_request_summary_passes(self, agent: MarkdownSuppressionAgent):
        """User explicit request for summary file should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["audit-summary.md"],
            "user_explicit_request": True,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_explicit_request_report_passes(self, agent: MarkdownSuppressionAgent):
        """User explicit request for report file should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["health-report.md"],
            "user_explicit_request": True,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_explicit_request_deployment_passes(self, agent: MarkdownSuppressionAgent):
        """User explicit request for deployment file should PASS."""
        context = {
            "intent": "DEPLOY",
            "output_files": ["DEPLOYMENT-GUIDE.md"],
            "user_explicit_request": True,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    # -------------------------------------------------------------------------
    # Allowed Markdown Files Tests
    # -------------------------------------------------------------------------

    def test_validate_readme_passes(self, agent: MarkdownSuppressionAgent):
        """README.md file creation should PASS (allowed)."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["README.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_documentation_file_passes(self, agent: MarkdownSuppressionAgent):
        """Regular documentation file should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["docs/architecture/system-overview.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_changelog_passes(self, agent: MarkdownSuppressionAgent):
        """CHANGELOG.md file creation should PASS."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["CHANGELOG.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_guide_passes(self, agent: MarkdownSuppressionAgent):
        """*-guide.md file creation should PASS (not forbidden pattern)."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["user-guide.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    # -------------------------------------------------------------------------
    # Edge Cases & Metadata Tests
    # -------------------------------------------------------------------------

    def test_validate_no_output_files_passes(self, agent: MarkdownSuppressionAgent):
        """No output files should PASS."""
        context = {
            "intent": "ANALYZE",
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_non_markdown_files_passes(self, agent: MarkdownSuppressionAgent):
        """Non-markdown output files should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["module.py", "config.yaml", "data.json"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_mixed_files_blocked_correctly(self, agent: MarkdownSuppressionAgent):
        """Mixed allowed and forbidden files should BLOCK only forbidden ones."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["README.md", "audit-summary.md", "module.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) == 1
        assert "audit-summary.md" in result.violations[0]

    def test_validate_case_insensitive_detection(self, agent: MarkdownSuppressionAgent):
        """Forbidden pattern detection should be case-insensitive."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["AUDIT-SUMMARY.MD", "Health-Report.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) == 2

    def test_validate_returns_correct_metadata(self, agent: MarkdownSuppressionAgent):
        """Validation result should include correct metadata."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["audit-summary.md"],
        }

        result = agent.validate(context)

        assert result.metadata["agent"] == "MarkdownSuppressionAgent"
        assert result.level == EnforcementLevel.BLOCKED
        assert result.metadata["rules_checked"] == ["CORE-002"]
