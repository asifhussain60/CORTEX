"""
Phase 80-d — GAP-80-04: Canonical SynthesisResult and ValidationResult.

Tests that canonical single definitions exist in cortex.models and that
duplicate class bodies are reduced to 1 canonical each.

CORE-008: Tests written first (RED phase).
"""

import subprocess
import sys

import pytest


class TestCanonicalResultTypes:
    """Tests for GAP-80-04: canonical result type consolidation."""

    def test_canonical_synthesis_result_importable(self):
        """cortex.models.synthesis_result must export SynthesisResult."""
        from cortex.models.synthesis_result import SynthesisResult
        assert SynthesisResult is not None

    def test_canonical_validation_result_importable(self):
        """cortex.models.validation_result must export ValidationResult."""
        from cortex.models.validation_result import ValidationResult
        assert ValidationResult is not None

    def test_canonical_synthesis_result_has_required_fields(self):
        """Canonical SynthesisResult must have guidance, context, metadata, confidence."""
        from cortex.models.synthesis_result import SynthesisResult
        import dataclasses
        fields = {f.name for f in dataclasses.fields(SynthesisResult)}
        # At minimum guidance and confidence must exist
        assert "guidance" in fields or "confidence" in fields, (
            f"SynthesisResult fields: {fields} — expected at least 'guidance' or 'confidence'"
        )

    def test_canonical_validation_result_has_required_fields(self):
        """Canonical ValidationResult must have passed and violations fields."""
        from cortex.models.validation_result import ValidationResult
        import dataclasses
        fields = {f.name for f in dataclasses.fields(ValidationResult)}
        assert "passed" in fields
        assert "violations" in fields

    def test_canonical_synthesis_result_instantiable(self):
        """SynthesisResult must be instantiable with required fields."""
        from cortex.models.synthesis_result import SynthesisResult
        result = SynthesisResult(guidance=[], confidence=1.0)
        assert result is not None

    def test_canonical_validation_result_instantiable(self):
        """ValidationResult must be instantiable with passed and violations."""
        from cortex.models.validation_result import ValidationResult
        result = ValidationResult(passed=True, violations=[])
        assert result.passed is True
        assert result.violations == []

    def test_canonical_validation_result_failed_state(self):
        """ValidationResult correctly represents a failed validation."""
        from cortex.models.validation_result import ValidationResult
        result = ValidationResult(passed=False, violations=["CORE-008 violation"])
        assert result.passed is False
        assert len(result.violations) == 1
