"""
Tests for IncrementalExecutionAgent (CORE-001, CORE-004 enforcement).

CORE-001: Operations adding/modifying >500 LOC require decomposition.
CORE-004: Continuation requests >1000 tokens receive warnings.
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.enforcement_orchestrator import (
    IncrementalExecutionAgent,
    EnforcementLevel,
    EnforcementResult,
)


class TestIncrementalExecutionAgent:
    """Test suite for IncrementalExecutionAgent."""

    @pytest.fixture
    def agent(self) -> IncrementalExecutionAgent:
        """Create agent instance for testing."""
        return IncrementalExecutionAgent()

    # -------------------------------------------------------------------------
    # CORE-001: LOC Enforcement Tests (<500 LOC operations)
    # -------------------------------------------------------------------------

    def test_validate_small_operation_passes(self, agent: IncrementalExecutionAgent):
        """Small operation (<500 LOC) should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["feature.py"],
            "estimated_loc": 200,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0

    def test_validate_medium_operation_passes(self, agent: IncrementalExecutionAgent):
        """Medium operation (400 LOC) should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["service.py", "handler.py"],
            "estimated_loc": 400,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_large_operation_blocked(self, agent: IncrementalExecutionAgent):
        """Large operation (>500 LOC) should be BLOCKED."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["monolith.py"],
            "estimated_loc": 800,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "CORE-001" in result.violations[0]
        assert "800 LOC" in result.violations[0]
        assert "limit: 500" in result.violations[0]

    def test_validate_very_large_operation_blocked(self, agent: IncrementalExecutionAgent):
        """Very large operation (1500 LOC) should be BLOCKED with strong message."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["huge_module.py"],
            "estimated_loc": 1500,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert "CORE-001" in result.violations[0]
        assert "decompose" in result.violations[0].lower()

    def test_validate_boundary_500_loc_passes(self, agent: IncrementalExecutionAgent):
        """Exactly 500 LOC should PASS (boundary condition)."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["boundary.py"],
            "estimated_loc": 500,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_boundary_501_loc_blocked(self, agent: IncrementalExecutionAgent):
        """501 LOC should be BLOCKED (boundary condition)."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["over_boundary.py"],
            "estimated_loc": 501,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED

    # -------------------------------------------------------------------------
    # CORE-004: Continuation Token Limit Tests (>1000 tokens)
    # -------------------------------------------------------------------------

    def test_validate_small_continuation_passes(self, agent: IncrementalExecutionAgent):
        """Small continuation (<1000 tokens) should PASS."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 500,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_medium_continuation_passes(self, agent: IncrementalExecutionAgent):
        """Medium continuation (900 tokens) should PASS."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 900,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_large_continuation_warned(self, agent: IncrementalExecutionAgent):
        """Large continuation (>1000 tokens) should generate WARNING."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 1500,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING
        assert len(result.warnings) > 0
        assert "CORE-004" in result.warnings[0]
        assert "1500 tokens" in result.warnings[0]

    def test_validate_very_large_continuation_warned(self, agent: IncrementalExecutionAgent):
        """Very large continuation (5000 tokens) should generate strong WARNING."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 5000,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING
        assert len(result.warnings) > 0
        assert "CORE-004" in result.warnings[0]

    def test_validate_boundary_1000_tokens_passes(self, agent: IncrementalExecutionAgent):
        """Exactly 1000 tokens should PASS (boundary condition)."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 1000,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_boundary_1001_tokens_warned(self, agent: IncrementalExecutionAgent):
        """1001 tokens should generate WARNING (boundary condition)."""
        context = {
            "intent": "CONTINUE",
            "continuation_tokens": 1001,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING

    # -------------------------------------------------------------------------
    # Edge Cases & Metadata Tests
    # -------------------------------------------------------------------------

    def test_validate_missing_estimated_loc_passes(self, agent: IncrementalExecutionAgent):
        """Missing estimated_loc should PASS (benefit of doubt)."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["unknown.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_non_implement_intent_passes(self, agent: IncrementalExecutionAgent):
        """Non-IMPLEMENT intents should PASS (LOC enforcement doesn't apply)."""
        context = {
            "intent": "ANALYZE",
            "estimated_loc": 1000,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_returns_correct_metadata(self, agent: IncrementalExecutionAgent):
        """Validation result should include correct metadata."""
        context = {
            "intent": "IMPLEMENT",
            "target_files": ["test.py"],
            "estimated_loc": 600,
        }

        result = agent.validate(context)

        assert result.metadata["agent"] == "IncrementalExecutionAgent"
        assert result.level == EnforcementLevel.BLOCKED
        assert result.metadata["rules_checked"] == ["CORE-001", "CORE-004"]
