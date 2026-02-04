"""
Tests for ArchitectureIntegrityAgent (CORE-017-020, 032, 034, 035, 038-041 enforcement).

Enforces:
- CORE-017-020: Versioned filenames, temporal naming
- CORE-032: Code review requirements
- CORE-034: Performance budgets
- CORE-035: Single implementation (no _v2 files)
- CORE-038-041: Turn budgets, context management, performance, event-driven architecture
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.enforcement_orchestrator import (
    ArchitectureIntegrityAgent,
    EnforcementLevel,
    EnforcementResult,
)


class TestArchitectureIntegrityAgent:
    """Test suite for ArchitectureIntegrityAgent."""

    @pytest.fixture
    def agent(self) -> ArchitectureIntegrityAgent:
        """Create agent instance for testing."""
        return ArchitectureIntegrityAgent()

    # -------------------------------------------------------------------------
    # CORE-035: Single Implementation Tests (No _v2 files)
    # -------------------------------------------------------------------------

    def test_validate_v2_filename_blocked(self, agent: ArchitectureIntegrityAgent):
        """File with _v2 suffix should be BLOCKED."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["orchestrator_v2.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) > 0
        assert "CORE-035" in result.violations[0]
        assert "_v2" in result.violations[0]

    def test_validate_v3_filename_blocked(self, agent: ArchitectureIntegrityAgent):
        """File with _v3 suffix should be BLOCKED."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["handler_v3.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert "CORE-035" in result.violations[0]

    def test_validate_multiple_versioned_files_blocked(self, agent: ArchitectureIntegrityAgent):
        """Multiple versioned files should all be BLOCKED."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["service_v2.py", "handler_v3.py", "util_v4.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) == 3

    def test_validate_clean_filename_passes(self, agent: ArchitectureIntegrityAgent):
        """File without version suffix should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["orchestrator.py"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    # -------------------------------------------------------------------------
    # CORE-038: Turn Budget Tests (max 20 turns per session)
    # -------------------------------------------------------------------------

    def test_validate_normal_turn_count_passes(self, agent: ArchitectureIntegrityAgent):
        """Normal turn count (<20) should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "turn_count": 10,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_high_turn_count_warned(self, agent: ArchitectureIntegrityAgent):
        """High turn count (>20) should generate WARNING."""
        context = {
            "intent": "IMPLEMENT",
            "turn_count": 25,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING
        assert len(result.warnings) > 0
        assert "CORE-038" in result.warnings[0]
        assert "25 turns" in result.warnings[0]
        assert "limit: 20" in result.warnings[0]

    def test_validate_boundary_20_turns_passes(self, agent: ArchitectureIntegrityAgent):
        """Exactly 20 turns should PASS (boundary condition)."""
        context = {
            "intent": "IMPLEMENT",
            "turn_count": 20,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_boundary_21_turns_warned(self, agent: ArchitectureIntegrityAgent):
        """21 turns should generate WARNING (boundary condition)."""
        context = {
            "intent": "IMPLEMENT",
            "turn_count": 21,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING

    # -------------------------------------------------------------------------
    # CORE-034: Performance Budget Tests
    # -------------------------------------------------------------------------

    def test_validate_fast_operation_passes(self, agent: ArchitectureIntegrityAgent):
        """Fast operation (<5s) should PASS."""
        context = {
            "intent": "ANALYZE",
            "estimated_duration_seconds": 3.0,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_slow_operation_warned(self, agent: ArchitectureIntegrityAgent):
        """Slow operation (>10s) should generate WARNING."""
        context = {
            "intent": "ANALYZE",
            "estimated_duration_seconds": 15.0,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.WARNING
        assert len(result.warnings) > 0
        assert "CORE-034" in result.warnings[0]
        assert "15.0s" in result.warnings[0]
        assert "limit: 10s" in result.warnings[0]

    # -------------------------------------------------------------------------
    # CORE-017-020: Versioned/Temporal Filename Tests
    # -------------------------------------------------------------------------

    def test_validate_date_versioned_file_passes(self, agent: ArchitectureIntegrityAgent):
        """Date-versioned file should PASS (temporal naming allowed)."""
        context = {
            "intent": "DOCUMENT",
            "output_files": ["report-2026-02-04.md"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_semantic_version_passes(self, agent: ArchitectureIntegrityAgent):
        """Semantic version in filename should PASS."""
        context = {
            "intent": "RELEASE",
            "output_files": ["release-v1.2.3.yaml"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    # -------------------------------------------------------------------------
    # Combined Violation Tests
    # -------------------------------------------------------------------------

    def test_validate_multiple_violation_types(self, agent: ArchitectureIntegrityAgent):
        """Multiple violation types should all be captured."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["service_v2.py", "handler_v3.py"],
            "turn_count": 25,
            "estimated_duration_seconds": 15.0,
        }

        result = agent.validate(context)

        # Should have violations for: 2 versioned files + turn budget + performance
        assert result.level == EnforcementLevel.BLOCKED  # Versioned files block
        assert len(result.violations) >= 2  # At least the versioned files

    def test_validate_no_violations_passes(self, agent: ArchitectureIntegrityAgent):
        """Clean context with no violations should PASS."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["service.py"],
            "turn_count": 5,
            "estimated_duration_seconds": 2.0,
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS
        assert len(result.violations) == 0

    # -------------------------------------------------------------------------
    # Edge Cases & Metadata Tests
    # -------------------------------------------------------------------------

    def test_validate_missing_optional_fields_passes(self, agent: ArchitectureIntegrityAgent):
        """Missing optional fields should PASS (benefit of doubt)."""
        context = {
            "intent": "ANALYZE",
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_empty_output_files_passes(self, agent: ArchitectureIntegrityAgent):
        """Empty output_files list should PASS."""
        context = {
            "intent": "ANALYZE",
            "output_files": [],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.PASS

    def test_validate_returns_correct_metadata(self, agent: ArchitectureIntegrityAgent):
        """Validation result should include correct metadata."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["service_v2.py"],
        }

        result = agent.validate(context)

        assert result.metadata["agent"] == "ArchitectureIntegrityAgent"
        assert result.level == EnforcementLevel.BLOCKED
        assert "CORE-017" in result.metadata["rules_checked"]
        assert "CORE-035" in result.metadata["rules_checked"]

    def test_validate_case_insensitive_v2_detection(self, agent: ArchitectureIntegrityAgent):
        """_v2 detection should be case-insensitive."""
        context = {
            "intent": "IMPLEMENT",
            "output_files": ["Service_V2.py", "handler_V3.PY"],
        }

        result = agent.validate(context)

        assert result.level == EnforcementLevel.BLOCKED
        assert len(result.violations) == 2
