"""Tests for HolisticValidationOrchestrator - Phase 48 S1.

CORE-008: Tests before code (TDD)
"""

import pytest
from pathlib import Path
from cortex.orchestrators.holistic.holistic_validation_orchestrator import (
    HolisticValidationOrchestrator,
    ValidationVerdict,
    ValidationResult,
    ValidationEvidence,
)


class TestValidationEvidence:
    """Test ValidationEvidence dataclass."""

    def test_evidence_creation(self) -> None:
        """Test creating ValidationEvidence."""
        evidence = ValidationEvidence(
            check_name="Test Check",
            status=ValidationVerdict.PASS,
            description="All good",
        )
        assert evidence.check_name == "Test Check"
        assert evidence.status == ValidationVerdict.PASS

    def test_evidence_with_remediation(self) -> None:
        """Test evidence with remediation."""
        evidence = ValidationEvidence(
            check_name="Failed Check",
            status=ValidationVerdict.BLOCK,
            description="Something failed",
            remediation="Fix it by doing X",
        )
        assert evidence.remediation == "Fix it by doing X"


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating ValidationResult."""
        result = ValidationResult(
            verdict=ValidationVerdict.PASS,
            target="test_file.py",
            operation="IMPLEMENT",
            evidence=[],
        )
        assert result.verdict == ValidationVerdict.PASS
        assert result.target == "test_file.py"

    def test_is_blocked(self) -> None:
        """Test is_blocked method."""
        blocked_result = ValidationResult(
            verdict=ValidationVerdict.BLOCK,
            target="test.py",
            operation="IMPLEMENT",
            evidence=[],
        )
        assert blocked_result.is_blocked() is True

        passed_result = ValidationResult(
            verdict=ValidationVerdict.PASS,
            target="test.py",
            operation="IMPLEMENT",
            evidence=[],
        )
        assert passed_result.is_blocked() is False

    def test_is_warned(self) -> None:
        """Test is_warned method."""
        warned_result = ValidationResult(
            verdict=ValidationVerdict.WARN,
            target="test.py",
            operation="IMPLEMENT",
            evidence=[],
        )
        assert warned_result.is_warned() is True

        passed_result = ValidationResult(
            verdict=ValidationVerdict.PASS,
            target="test.py",
            operation="IMPLEMENT",
            evidence=[],
        )
        assert passed_result.is_warned() is False


class TestHolisticValidationOrchestrator:
    """Test HolisticValidationOrchestrator."""

    @pytest.fixture
    def validator(self) -> HolisticValidationOrchestrator:
        """Create a validator instance."""
        return HolisticValidationOrchestrator()

    def test_validator_initialization(self, validator: HolisticValidationOrchestrator) -> None:
        """Test orchestrator initializes correctly."""
        assert validator.registry_data is not None
        assert validator.wiring_data is not None
        assert validator.index_file.exists()

    def test_validator_invalid_registry_path(self) -> None:
        """Test validator rejects invalid registry path."""
        with pytest.raises(ValueError, match="Registry path not found"):
            HolisticValidationOrchestrator(registry_path=Path("/nonexistent/path"))

    def test_registry_consistency_check(self, validator: HolisticValidationOrchestrator) -> None:
        """Test registry consistency validation."""
        evidence = validator._check_registry_consistency()
        assert evidence.check_name == "Registry Consistency"
        assert evidence.status in [ValidationVerdict.PASS, ValidationVerdict.WARN, ValidationVerdict.BLOCK]

    def test_wiring_consistency_check(self, validator: HolisticValidationOrchestrator) -> None:
        """Test wiring consistency validation."""
        evidence = validator._check_wiring_consistency()
        assert evidence.check_name == "Wiring Consistency"
        assert evidence.status in [ValidationVerdict.PASS, ValidationVerdict.WARN, ValidationVerdict.BLOCK]

    def test_orchestrator_dependencies_check(self, validator: HolisticValidationOrchestrator) -> None:
        """Test orchestrator dependency validation."""
        evidence = validator._check_orchestrator_dependencies()
        assert evidence.check_name == "Orchestrator Dependencies"
        assert "total_dependencies" in evidence.details
        assert "valid" in evidence.details

    def test_circular_dependencies_check(self, validator: HolisticValidationOrchestrator) -> None:
        """Test circular dependency detection."""
        evidence = validator._check_circular_dependencies()
        assert evidence.check_name == "Circular Dependencies"
        assert "cycles_found" in evidence.details

    def test_core_rules_check(self, validator: HolisticValidationOrchestrator) -> None:
        """Test CORE rules alignment check."""
        evidence = validator._check_core_rules_alignment()
        assert evidence.check_name == "CORE Rules Alignment"
        assert evidence.status == ValidationVerdict.PASS

    def test_validate_implement_operation(self, validator: HolisticValidationOrchestrator) -> None:
        """Test validation for IMPLEMENT operation."""
        result = validator.validate(operation="IMPLEMENT", target="cortex/new_feature.py")
        assert result.operation == "IMPLEMENT"
        assert result.target == "cortex/new_feature.py"
        assert result.verdict in [
            ValidationVerdict.PASS,
            ValidationVerdict.WARN,
            ValidationVerdict.BLOCK,
        ]

    def test_validate_fix_operation(self, validator: HolisticValidationOrchestrator) -> None:
        """Test validation for FIX operation."""
        result = validator.validate(operation="FIX", target="cortex/bug_fix.py")
        assert result.operation == "FIX"
        assert result.verdict in [
            ValidationVerdict.PASS,
            ValidationVerdict.WARN,
            ValidationVerdict.BLOCK,
        ]

    def test_validate_refactor_operation(self, validator: HolisticValidationOrchestrator) -> None:
        """Test validation for REFACTOR operation."""
        result = validator.validate(operation="REFACTOR", target="cortex/refactor.py")
        assert result.operation == "REFACTOR"
        assert result.verdict in [
            ValidationVerdict.PASS,
            ValidationVerdict.WARN,
            ValidationVerdict.BLOCK,
        ]

    def test_regression_risk_calculation(self, validator: HolisticValidationOrchestrator) -> None:
        """Test regression risk score calculation."""
        # BLOCK evidence increases risk
        block_evidence = ValidationEvidence(
            check_name="Test",
            status=ValidationVerdict.BLOCK,
            description="Block",
        )

        risk = validator._calculate_regression_risk([block_evidence], "IMPLEMENT")
        assert 0.0 <= risk <= 1.0
        assert risk > 0.5  # BLOCK should have high risk

    def test_impact_radius_calculation(self, validator: HolisticValidationOrchestrator) -> None:
        """Test impact radius calculation."""
        impact = validator._calculate_impact_radius("cortex/orchestrators/test.py")
        assert isinstance(impact, list)

    def test_detect_cycles_no_cycles(self, validator: HolisticValidationOrchestrator) -> None:
        """Test cycle detection with no cycles."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        cycles = validator._detect_cycles(graph)
        assert len(cycles) == 0

    def test_detect_cycles_with_cycles(self, validator: HolisticValidationOrchestrator) -> None:
        """Test cycle detection with cycles present."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        cycles = validator._detect_cycles(graph)
        assert len(cycles) > 0

    def test_validation_result_evidence_count(self, validator: HolisticValidationOrchestrator) -> None:
        """Test that validation includes all evidence types."""
        result = validator.validate(operation="IMPLEMENT", target="test.py")
        # Should have 5 checks (registry, wiring, dependencies, circular, core-rules)
        assert len(result.evidence) >= 5

    def test_validation_duration_recorded(self, validator: HolisticValidationOrchestrator) -> None:
        """Test that validation duration is recorded."""
        result = validator.validate(operation="IMPLEMENT", target="test.py")
        assert result.duration_ms >= 0.0


class TestValidationVerdicts:
    """Test validation verdict enum."""

    def test_verdict_values(self) -> None:
        """Test all verdict values."""
        assert ValidationVerdict.PASS.value == "PASS"
        assert ValidationVerdict.WARN.value == "WARN"
        assert ValidationVerdict.BLOCK.value == "BLOCK"

    def test_verdict_comparison(self) -> None:
        """Test verdict comparison."""
        assert ValidationVerdict.PASS == ValidationVerdict.PASS
        assert ValidationVerdict.BLOCK != ValidationVerdict.PASS
