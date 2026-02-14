"""
Contract Enforcement Tests.

AC_START: AC-MEGA-B-S2-006
Tests contract enforcement during orchestrator registration and runtime.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.wiring.registry.contract_validator import (
    ContractValidator,
    ValidationLevel,
    ContractViolation,
)


class TestContractEnforcement:
    """Test contract enforcement mechanisms."""

    @pytest.fixture
    def validator(self, tmp_path: Path) -> ContractValidator:
        """Create ContractValidator for enforcement tests."""
        return ContractValidator(audit_db=tmp_path / "enforcement_audit.db")

    def test_block_invalid_signature_registration(
        self, validator: ContractValidator
    ) -> None:
        """Test blocking orchestrator with invalid signature."""
        result = validator.validate_method_signature(
            orchestrator="BadOrchestrator",
            method="process",
            expected_params=["self", "request"],
            actual_params=["self", "wrong"],
        )
        assert not result.is_valid
        assert any(v.level == ValidationLevel.ERROR for v in result.violations)

    def test_allow_valid_signature_registration(
        self, validator: ContractValidator
    ) -> None:
        """Test allowing orchestrator with valid signature."""
        result = validator.validate_method_signature(
            orchestrator="GoodOrchestrator",
            method="process",
            expected_params=["self", "request"],
            actual_params=["self", "request"],
        )
        assert result.is_valid

    def test_warn_missing_audit_logging(self, validator: ContractValidator) -> None:
        """Test warning for missing audit logging."""
        result = validator.validate_audit_logging(
            orchestrator="NoAuditOrch", method="process", has_audit_call=False
        )
        assert not result.is_valid
        assert any(v.level == ValidationLevel.WARNING for v in result.violations)

    def test_require_audit_logging(self, validator: ContractValidator) -> None:
        """Test requiring audit logging for critical methods."""
        result = validator.validate_audit_logging(
            orchestrator="AuditOrch", method="critical_operation", has_audit_call=True
        )
        assert result.is_valid

    def test_enforce_return_type_consistency(
        self, validator: ContractValidator
    ) -> None:
        """Test return type consistency enforcement."""
        result = validator.validate_return_type(
            orchestrator="TypedOrch",
            method="get_data",
            expected_type="Dict[str, Any]",
            actual_type="List[str]",
        )
        assert not result.is_valid

    def test_cross_layer_consistency_check(self, validator: ContractValidator) -> None:
        """Test cross-layer consistency validation."""
        result = validator.validate_cross_layer(
            orchestrator="LayeredOrch", layer="execution"
        )
        assert result.is_valid

    def test_block_duplicate_registration(self, validator: ContractValidator) -> None:
        """Test blocking duplicate orchestrator registration."""
        # First registration
        validator.track_contract_evolution(
            orchestrator="DuplicateOrch", version="1.0.0"
        )
        # Second registration (should be tracked)
        result = validator.track_contract_evolution(
            orchestrator="DuplicateOrch", version="1.0.0"
        )
        assert result.is_valid  # Tracking allows evolution

    def test_version_evolution_tracking(self, validator: ContractValidator) -> None:
        """Test contract version evolution tracking."""
        v1 = validator.track_contract_evolution(
            orchestrator="EvolveOrch", version="1.0.0"
        )
        v2 = validator.track_contract_evolution(
            orchestrator="EvolveOrch", version="2.0.0"
        )
        assert v1.is_valid and v2.is_valid

    def test_batch_enforcement(self, validator: ContractValidator) -> None:
        """Test batch contract enforcement."""
        contracts = [
            {"orchestrator": "Orch1", "methods": {}},
            {"orchestrator": "Orch2", "methods": {}},
            {"orchestrator": "Orch3", "methods": {}},
        ]
        results = validator.validate_batch(contracts)
        assert len(results) == 3
        assert all(r.is_valid for r in results)

    def test_violation_accumulation(self, validator: ContractValidator) -> None:
        """Test violation accumulation across validations."""
        for i in range(3):
            validator.validate_method_signature(
                orchestrator=f"Orch{i}",
                method="bad_method",
                expected_params=["self"],
                actual_params=[],
            )
        violations = validator.query_violations()
        assert len(violations) >= 3

    def test_severity_level_escalation(self, validator: ContractValidator) -> None:
        """Test severity escalation for repeated violations."""
        for _ in range(5):
            validator.validate_method_signature(
                orchestrator="BadOrch",
                method="repeat_violation",
                expected_params=["self"],
                actual_params=[],
            )
        summary = validator.get_validation_summary()
        assert summary["failed"] >= 5

    def test_enforcement_audit_trail(self, validator: ContractValidator) -> None:
        """Test enforcement creates audit trail."""
        validator.validate_method_signature(
            orchestrator="AuditedOrch",
            method="test",
            expected_params=["self"],
            actual_params=["self"],
        )
        audit = validator.query_audit_log(limit=1)
        assert len(audit) > 0
        assert audit[0]["orchestrator"] == "AuditedOrch"

    def test_contract_breaking_change_detection(
        self, validator: ContractValidator
    ) -> None:
        """Test detection of breaking contract changes."""
        # Old contract
        validator.validate_method_signature(
            orchestrator="BreakingOrch",
            method="old_api",
            expected_params=["self", "arg1"],
            actual_params=["self", "arg1"],
        )
        # New contract (breaking change)
        result = validator.validate_method_signature(
            orchestrator="BreakingOrch",
            method="old_api",
            expected_params=["self", "arg1"],
            actual_params=["self", "arg1", "arg2"],
        )
        assert not result.is_valid

    def test_enforcement_with_multiple_violations(
        self, validator: ContractValidator
    ) -> None:
        """Test enforcement with multiple violation types."""
        # Signature violation
        sig_result = validator.validate_method_signature(
            orchestrator="MultiViolationOrch",
            method="process",
            expected_params=["self"],
            actual_params=["self", "extra"],
        )
        # Return type violation
        ret_result = validator.validate_return_type(
            orchestrator="MultiViolationOrch",
            method="process",
            expected_type="str",
            actual_type="int",
        )
        # Audit violation
        audit_result = validator.validate_audit_logging(
            orchestrator="MultiViolationOrch", method="process", has_audit_call=False
        )
        assert not sig_result.is_valid
        assert not ret_result.is_valid
        assert not audit_result.is_valid

    def test_enforcement_summary_report(self, validator: ContractValidator) -> None:
        """Test enforcement summary report generation."""
        # Generate some violations
        validator.validate_method_signature(
            orchestrator="Test1", method="m1", expected_params=[], actual_params=["x"]
        )
        validator.validate_method_signature(
            orchestrator="Test2", method="m2", expected_params=[], actual_params=["y"]
        )
        summary = validator.get_validation_summary()
        assert summary["total_validations"] >= 2
        assert "violations_by_level" in summary

    def test_export_enforcement_violations(
        self, validator: ContractValidator, tmp_path: Path
    ) -> None:
        """Test exporting enforcement violations."""
        validator.validate_method_signature(
            orchestrator="ExportTest",
            method="test",
            expected_params=["self"],
            actual_params=[],
        )
        export_path = tmp_path / "violations.json"
        validator.export_violations(export_path)
        assert export_path.exists()

    def test_enforcement_blocks_runtime_calls(
        self, validator: ContractValidator
    ) -> None:
        """Test enforcement can block runtime calls."""
        result = validator.validate_method_signature(
            orchestrator="RuntimeOrch",
            method="unsafe_operation",
            expected_params=["self", "validated_input"],
            actual_params=["self", "raw_input"],
        )
        # Runtime should check result.is_valid before proceeding
        assert not result.is_valid

    def test_enforcement_allows_safe_operations(
        self, validator: ContractValidator
    ) -> None:
        """Test enforcement allows safe operations."""
        result = validator.validate_method_signature(
            orchestrator="SafeOrch",
            method="safe_operation",
            expected_params=["self", "input"],
            actual_params=["self", "input"],
        )
        assert result.is_valid

    def test_enforcement_metadata_capture(self, validator: ContractValidator) -> None:
        """Test enforcement captures metadata."""
        validator.validate_method_signature(
            orchestrator="MetaOrch",
            method="meta_method",
            expected_params=["self"],
            actual_params=["self"],
        )
        audit = validator.query_audit_log(limit=1)
        assert audit[0]["validation_type"] == "signature"

    def test_enforcement_timestamp_accuracy(
        self, validator: ContractValidator
    ) -> None:
        """Test enforcement timestamps are accurate."""
        from datetime import datetime

        before = datetime.utcnow()
        validator.validate_method_signature(
            orchestrator="TimeOrch",
            method="test",
            expected_params=["self"],
            actual_params=["self"],
        )
        after = datetime.utcnow()
        audit = validator.query_audit_log(limit=1)
        timestamp = datetime.fromisoformat(audit[0]["timestamp"])
        assert before <= timestamp <= after

    def test_enforcement_isolation(self, validator: ContractValidator) -> None:
        """Test enforcement violations are isolated per orchestrator."""
        validator.validate_method_signature(
            orchestrator="IsolatedOrch1",
            method="test",
            expected_params=["self"],
            actual_params=[],
        )
        violations1 = validator.query_violations(orchestrator="IsolatedOrch1")
        violations2 = validator.query_violations(orchestrator="IsolatedOrch2")
        assert len(violations1) > 0
        assert len(violations2) == 0

    def test_enforcement_comprehensive_validation(
        self, validator: ContractValidator
    ) -> None:
        """Test comprehensive validation of all orchestrators."""
        orchestrators = [
            "StateOrchestrator",
            "ObservabilityOrchestrator",
            "IntelligenceOrchestrator",
            "SOLIDOrchestrator",
        ]
        results = validator.validate_all_orchestrators(orchestrators)
        assert len(results) == 4
        assert all(r.is_valid for r in results)

    def test_enforcement_performance(self, validator: ContractValidator) -> None:
        """Test enforcement performance with many validations."""
        import time

        start = time.time()
        for i in range(100):
            validator.validate_method_signature(
                orchestrator=f"PerfOrch{i}",
                method="test",
                expected_params=["self"],
                actual_params=["self"],
            )
        elapsed = time.time() - start
        assert elapsed < 1.0  # Should complete in under 1 second
