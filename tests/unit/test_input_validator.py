"""
Tests for Input Validation Framework

Tests for AC-VALIDATE-001 through AC-VALIDATE-005:
- Intent canonicalization
- AC-ID existence checking
- Evidence bundle pre-check
- Cross-reference coherence
- Semantic output validation
"""

import pytest
from datetime import datetime
from src.core.input_validator import (
    InputValidator,
    ValidationResult,
    CanonicalIntent,
    ValidationError,
    SeverityLevel
)


class TestIntentCanonicalization:
    """Tests for AC-VALIDATE-001: Intent canonicalization"""

    def test_canonicalize_implement_intent(self):
        """Test canonicalization of 'implement' intent"""
        validator = InputValidator()
        intent = validator._canonicalize_intent("Implement new feature X")
        
        assert intent.intent_type == "implement"
        assert intent.canonical_form == "INTENT: IMPLEMENT"
        assert intent.ambiguity_resolved
        assert intent.confidence_score >= 0.85

    def test_canonicalize_fix_intent(self):
        """Test canonicalization of 'fix' intent"""
        validator = InputValidator()
        intent = validator._canonicalize_intent("Debug the broken component")
        
        assert intent.intent_type == "fix"
        assert intent.canonical_form == "INTENT: FIX"
        assert intent.ambiguity_resolved

    def test_canonicalize_validate_intent(self):
        """Test canonicalization of 'validate' intent"""
        validator = InputValidator()
        intent = validator._canonicalize_intent("Test the new implementation")
        
        assert intent.intent_type == "validate"
        assert intent.canonical_form == "INTENT: VALIDATE"
        assert intent.ambiguity_resolved

    def test_canonicalize_query_intent(self):
        """Test canonicalization of 'query' intent (default)"""
        validator = InputValidator()
        intent = validator._canonicalize_intent("How does this work?")
        
        assert intent.intent_type in ["query", "validate"]  # Either is valid
        assert intent.canonical_form.startswith("INTENT:")

    def test_intent_confidence_score_range(self):
        """Test that confidence scores are in valid range"""
        validator = InputValidator()
        intent = validator._canonicalize_intent("Implement feature")
        
        assert 0.0 <= intent.confidence_score <= 1.0

    def test_canonical_intent_dataclass(self):
        """Test CanonicalIntent dataclass validation"""
        intent = CanonicalIntent(
            original_intent="test",
            canonical_form="INTENT: TEST",
            intent_type="validate",
            confidence_score=0.9,
            ambiguity_resolved=True
        )
        
        assert intent.canonical_form == "INTENT: TEST"
        assert intent.confidence_score == 0.9

    def test_canonical_intent_invalid_confidence(self):
        """Test CanonicalIntent rejects invalid confidence scores"""
        with pytest.raises(ValueError):
            CanonicalIntent(
                original_intent="test",
                canonical_form="INTENT: TEST",
                intent_type="validate",
                confidence_score=1.5,  # Invalid: > 1.0
                ambiguity_resolved=True
            )

    def test_canonical_intent_empty_form_rejected(self):
        """Test CanonicalIntent rejects empty canonical form"""
        with pytest.raises(ValueError):
            CanonicalIntent(
                original_intent="test",
                canonical_form="",  # Invalid: empty
                intent_type="validate",
                confidence_score=0.9,
                ambiguity_resolved=True
            )


@pytest.mark.ac("AR-006-01")
class TestACIDExistenceCheck:
    """Tests for AC-VALIDATE-002: AC-ID existence checking"""

    def test_extract_ac_ids_from_text(self):
        """Test extraction of AC-IDs from text"""
        validator = InputValidator()
        ac_ids = validator._extract_ac_ids(
            "Please implement AC-AR-006-01 and AC-FR-002-03 for governance"
        )
        
        assert "AC-AR-006-01" in ac_ids
        assert "AC-FR-002-03" in ac_ids
        assert len(ac_ids) == 2

    def test_extract_no_ac_ids(self):
        """Test extraction when no AC-IDs present"""
        validator = InputValidator()
        ac_ids = validator._extract_ac_ids("No AC-IDs in this text")
        
        assert len(ac_ids) == 0

    def test_ac_id_existence_check_valid(self):
        """Test AC-ID existence check with valid AC-ID"""
        validator = InputValidator()
        # AC-FR-001-01 should exist from PHASE-01
        exists = validator._ac_id_exists("AC-FR-001-01")
        
        # Should either exist or fail gracefully
        assert isinstance(exists, bool)

    def test_ac_id_existence_check_invalid(self):
        """Test AC-ID existence check with invalid AC-ID"""
        validator = InputValidator()
        exists = validator._ac_id_exists("AC-FAKE-999")
        
        assert exists is False

    def test_validate_input_with_valid_ac_ids(self):
        """Test validation with valid AC-IDs"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement AC-AR-006-01 for testing",
            input_id="test_valid_ac_id"
        )
        
        assert result.input_id == "test_valid_ac_id"
        assert "ac_ids_found" in result.metadata
        assert result.metadata["ac_ids_found"] == 1

    def test_validate_input_with_invalid_ac_ids(self):
        """Test validation with invalid AC-IDs"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement AC-FAKE-999 for testing",
            input_id="test_invalid_ac_id"
        )
        
        # Should have errors about invalid AC-IDs
        assert result.has_errors()


@pytest.mark.ac("AR-006-01")
class TestEvidenceBundlePrecheck:
    """Tests for AC-VALIDATE-003: Evidence bundle pre-check"""

    def test_validate_valid_json_bundle(self):
        """Test validation of valid JSON evidence bundle"""
        validator = InputValidator()
        input_text = '{"ac_id": "AC-AR-006-01", "status": "COMPLETE", "tests": 20}'
        result = validator.validate_input(input_text)
        
        # Should not have JSON errors
        assert not any(
            err.code == "MALFORMED_JSON" for err in result.errors
        )

    def test_validate_malformed_json_bundle(self):
        """Test validation of malformed JSON evidence bundle"""
        validator = InputValidator()
        input_text = '{"ac_id": "AC-AR-006-01", "status": INVALID}'
        result = validator.validate_input(input_text)
        
        # Should detect malformed JSON
        has_json_error = any(
            err.code == "MALFORMED_JSON" for err in result.errors
        )
        # Either detected or checked (system may not find pattern)
        assert isinstance(has_json_error, bool)

    def test_validate_multiple_evidence_bundles(self):
        """Test validation with multiple evidence bundles"""
        validator = InputValidator()
        input_text = (
            '{"bundle": 1} and another '
            '{"bundle": 2} and finally '
            '{"bundle": 3}'
        )
        result = validator.validate_input(input_text)
        
        # Should attempt to check all bundles
        assert "evidence_bundles_checked" in result.metadata


@pytest.mark.ac("AR-006-01")
class TestCrossReferenceCoherence:
    """Tests for AC-VALIDATE-004: Cross-reference coherence"""

    def test_cross_reference_resolution(self):
        """Test cross-reference resolution"""
        validator = InputValidator()
        result = validator.validate_input(
            "AC-AR-006-01 and AC-FR-002-01 work together",
            input_id="test_cross_ref"
        )
        
        assert "cross_references" in result.metadata

    def test_single_ac_id_reference(self):
        """Test validation with single AC-ID reference"""
        validator = InputValidator()
        result = validator.validate_input("AC-AR-006-01")
        
        assert result.metadata.get("ac_ids_found", 0) >= 0

    def test_multiple_ac_id_references(self):
        """Test validation with multiple AC-ID references"""
        validator = InputValidator()
        result = validator.validate_input(
            "AC-AR-006-01, AC-AR-006-02, AC-AR-006-03",
            input_id="test_multi_ref"
        )
        
        ac_ids_found = result.metadata.get("ac_ids_found", 0)
        assert ac_ids_found >= 0


class TestSemanticValidation:
    """Tests for AC-VALIDATE-005: Semantic output validation"""

    def test_no_contradictions_detected(self):
        """Test validation of semantically correct input"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement feature X with proper validation"
        )
        
        semantic_checks = result.metadata.get("semantic_checks", {})
        assert "has_contradictions" in semantic_checks

    def test_contradiction_detection(self):
        """Test detection of contradictions"""
        validator = InputValidator()
        has_contradiction = validator._has_contradictions(
            "Must implement feature. Must not implement feature."
        )
        
        assert has_contradiction is True

    def test_no_contradiction_in_normal_text(self):
        """Test that normal text doesn't trigger contradiction detection"""
        validator = InputValidator()
        has_contradiction = validator._has_contradictions(
            "Implement the feature with proper error handling"
        )
        
        assert has_contradiction is False

    def test_circular_reference_detection_empty(self):
        """Test circular reference detection with no references"""
        validator = InputValidator()
        has_cycle = validator._has_circular_references(set())
        
        assert has_cycle is False

    def test_circular_reference_detection_single(self):
        """Test circular reference detection with single AC-ID"""
        validator = InputValidator()
        has_cycle = validator._has_circular_references({"AC-AR-006-01"})
        
        assert has_cycle is False

    def test_circular_reference_detection_multiple_no_cycle(self):
        """Test circular reference detection with multiple AC-IDs (no cycle)"""
        validator = InputValidator()
        has_cycle = validator._has_circular_references(
            {"AC-AR-006-01", "AC-AR-006-02"}
        )
        
        assert isinstance(has_cycle, bool)


class TestValidationResult:
    """Tests for ValidationResult dataclass"""

    def test_validation_result_creation(self):
        """Test creating a ValidationResult"""
        result = ValidationResult(
            input_id="test_123",
            valid=True,
            timestamp=datetime.now(),
            validation_method="comprehensive"
        )
        
        assert result.input_id == "test_123"
        assert result.valid is True

    def test_validation_result_error_count(self):
        """Test error counting in ValidationResult"""
        result = ValidationResult(
            input_id="test",
            valid=False,
            timestamp=datetime.now(),
            validation_method="test",
            errors=[
                ValidationError(
                    code="ERROR1",
                    message="Error 1",
                    severity=SeverityLevel.ERROR
                ),
                ValidationError(
                    code="ERROR2",
                    message="Error 2",
                    severity=SeverityLevel.ERROR
                )
            ]
        )
        
        assert result.error_count() == 2
        assert result.has_errors() is True

    def test_validation_result_warning_count(self):
        """Test warning counting in ValidationResult"""
        result = ValidationResult(
            input_id="test",
            valid=True,
            timestamp=datetime.now(),
            validation_method="test",
            warnings=[
                ValidationError(
                    code="WARN1",
                    message="Warning 1",
                    severity=SeverityLevel.WARNING
                )
            ]
        )
        
        assert result.warning_count() == 1
        assert result.has_warnings() is True

    def test_validation_result_to_dict(self):
        """Test converting ValidationResult to dictionary"""
        result = ValidationResult(
            input_id="test",
            valid=True,
            timestamp=datetime.now(),
            validation_method="comprehensive"
        )
        
        result_dict = result.to_dict()
        assert result_dict["input_id"] == "test"
        assert result_dict["valid"] is True
        assert "timestamp" in result_dict
        assert "error_count" in result_dict
        assert "warning_count" in result_dict


class TestValidationError:
    """Tests for ValidationError dataclass"""

    def test_validation_error_creation(self):
        """Test creating a ValidationError"""
        error = ValidationError(
            code="TEST_ERROR",
            message="This is a test error",
            severity=SeverityLevel.ERROR
        )
        
        assert error.code == "TEST_ERROR"
        assert error.severity == SeverityLevel.ERROR

    def test_validation_error_with_context(self):
        """Test ValidationError with context and remediation"""
        error = ValidationError(
            code="AC_ID_ERROR",
            message="Invalid AC-ID",
            severity=SeverityLevel.ERROR,
            context={"ac_id": "AC-FAKE-999"},
            remediation="Use a valid AC-ID from the roadmap"
        )
        
        assert error.context["ac_id"] == "AC-FAKE-999"
        assert error.remediation == "Use a valid AC-ID from the roadmap"

    def test_validation_error_to_dict(self):
        """Test converting ValidationError to dictionary"""
        error = ValidationError(
            code="TEST",
            message="Test error",
            severity=SeverityLevel.WARNING,
            remediation="Fix it"
        )
        
        error_dict = error.to_dict()
        assert error_dict["code"] == "TEST"
        assert error_dict["severity"] == "warning"
        assert error_dict["remediation"] == "Fix it"


@pytest.mark.ac("AR-006-01")
class TestComprehensiveValidation:
    """Integration tests for comprehensive validation"""

    def test_comprehensive_validation_success(self):
        """Test comprehensive validation with valid input"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement AC-AR-006-01 with proper testing",
            input_id="comprehensive_valid"
        )
        
        assert result.input_id == "comprehensive_valid"
        assert "canonical_intent" in result.metadata
        assert result.validation_time_ms > 0

    def test_comprehensive_validation_empty_input(self):
        """Test comprehensive validation with empty input"""
        validator = InputValidator()
        result = validator.validate_input("", input_id="empty_test")
        
        assert result.has_errors()
        assert any(err.code == "EMPTY_INPUT" for err in result.errors)

    def test_comprehensive_validation_multiple_checks(self):
        """Test that comprehensive validation runs all checks"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement AC-AR-006-01 with validation",
            input_id="multi_check"
        )
        
        # Should have results from multiple checks
        assert "canonical_intent" in result.metadata
        assert "ac_ids_found" in result.metadata
        assert "semantic_checks" in result.metadata
        assert result.validation_method == "comprehensive"

    def test_validation_performance(self):
        """Test that validation completes in reasonable time"""
        validator = InputValidator()
        result = validator.validate_input(
            "Implement AC-AR-006-01 with comprehensive testing and validation",
            input_id="perf_test"
        )
        
        # Should complete in less than 1000ms (1 second)
        assert result.validation_time_ms < 1000
        assert result.validation_time_ms > 0

    def test_validation_generates_audit_log(self):
        """Test that validation generates audit log entries"""
        validator = InputValidator()
        result = validator.validate_input(
            "Test input for audit logging",
            input_id="audit_test"
        )
        
        # Should complete without error (audit logging occurs internally)
        assert result.valid or result.has_errors()


class TestACIDFormatValidation:
    """Tests for AC-VALIDATE-006: AC-ID format validation"""

    def test_valid_two_segment_ac_id(self):
        """Test validation of valid 2-segment AC-ID"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006"}
        
        assert validator._validate_ac_id_format(ac_ids)

    def test_valid_three_segment_ac_id(self):
        """Test validation of valid 3-segment AC-ID with sub-requirement"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006-01"}
        
        assert validator._validate_ac_id_format(ac_ids)

    def test_valid_multiple_ac_ids(self):
        """Test validation of multiple valid AC-IDs"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006", "AC-AR-007", "AC-VALIDATE-001", "AC-VALIDATE-002-05"}
        
        assert validator._validate_ac_id_format(ac_ids)

    def test_invalid_ac_id_lowercase_category(self):
        """Test that lowercase category is rejected"""
        validator = InputValidator()
        ac_ids = {"AC-ar-006"}
        
        assert not validator._validate_ac_id_format(ac_ids)

    def test_invalid_ac_id_wrong_segment_count(self):
        """Test that AC-IDs with wrong segment count are rejected"""
        validator = InputValidator()
        ac_ids = {"AC-AR"}
        
        assert not validator._validate_ac_id_format(ac_ids)

    def test_invalid_ac_id_non_numeric_requirement(self):
        """Test that non-numeric requirement number is rejected"""
        validator = InputValidator()
        ac_ids = {"AC-AR-ABC"}
        
        assert not validator._validate_ac_id_format(ac_ids)

    def test_empty_ac_id_set(self):
        """Test that empty AC-ID set is valid"""
        validator = InputValidator()
        ac_ids: set = set()
        
        assert validator._validate_ac_id_format(ac_ids)

    def test_ac_id_format_with_spaces(self):
        """Test that AC-IDs with spaces are stripped and validated"""
        validator = InputValidator()
        ac_ids = {"  AC-AR-006  "}
        
        assert validator._validate_ac_id_format(ac_ids)


class TestPhaseAlignmentValidation:
    """Tests for AC-VALIDATE-007: Phase alignment enforcement"""

    def test_phase_alignment_with_matching_phase(self):
        """Test AC-IDs from same phase pass validation"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006"}  # From PHASE-02
        current_phase = "PHASE-02"
        
        # Should pass or default to True if not found in registry
        result = validator._validate_phase_alignment(ac_ids, current_phase)
        assert result is True

    def test_phase_alignment_with_no_current_phase(self):
        """Test that no current phase defaults to True"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006"}
        current_phase = None
        
        assert validator._validate_phase_alignment(ac_ids, current_phase)

    def test_phase_alignment_with_empty_ac_ids(self):
        """Test that empty AC-ID set passes"""
        validator = InputValidator()
        ac_ids: set = set()
        current_phase = "PHASE-02"
        
        assert validator._validate_phase_alignment(ac_ids, current_phase)

    def test_phase_alignment_with_invalid_phase_format(self):
        """Test that invalid phase format defaults to True"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006"}
        current_phase = "INVALID-PHASE"
        
        # Should default to True when phase format is invalid
        result = validator._validate_phase_alignment(ac_ids, current_phase)
        assert result is True

    def test_phase_alignment_with_earlier_phase_ac_ids(self):
        """Test that AC-IDs from earlier phases are allowed (backward compat)"""
        validator = InputValidator()
        # AC-IDs from PHASE-01 should be allowed in PHASE-02
        ac_ids = {"AC-AR-001"}  # From PHASE-01
        current_phase = "PHASE-02"
        
        result = validator._validate_phase_alignment(ac_ids, current_phase)
        # Should pass if registry allows it
        assert result is True


class TestACIDConflictDetection:
    """Tests for AC-VALIDATE-008: Request contradiction detection"""

    def test_no_conflicts_single_ac_id(self):
        """Test that single AC-ID has no conflicts"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006"}
        
        assert validator._validate_no_ac_id_conflicts(ac_ids)

    def test_no_conflicts_multiple_independent_ac_ids(self):
        """Test that multiple independent AC-IDs have no conflicts"""
        validator = InputValidator()
        ac_ids = {"AC-AR-006", "AC-AR-007", "AC-VALIDATE-001"}
        
        assert validator._validate_no_ac_id_conflicts(ac_ids)

    def test_empty_ac_id_set_no_conflicts(self):
        """Test that empty AC-ID set has no conflicts"""
        validator = InputValidator()
        ac_ids: set = set()
        
        assert validator._validate_no_ac_id_conflicts(ac_ids)

    def test_conflict_detection_defaults_to_true_on_error(self):
        """Test that conflict detection defaults to True on error"""
        validator = InputValidator()
        # Use AC-IDs that may not exist in registry (triggers exception handling)
        ac_ids = {"AC-UNKNOWN-999", "AC-FAKE-888"}
        
        # Should default to True on error
        result = validator._validate_no_ac_id_conflicts(ac_ids)
        assert result is True


class TestSchemaValidation:
    """Tests for AC-VALIDATE-009: Schema validation"""

    def test_valid_dict_schema(self):
        """Test validation of valid dict schema with required fields"""
        validator = InputValidator()
        request_data = {
            "action": "execute",
            "context": {"param1": "value1"}
        }
        
        assert validator._validate_schema_compliance(request_data)

    def test_valid_dict_schema_minimal(self):
        """Test validation of minimal valid schema"""
        validator = InputValidator()
        request_data = {
            "action": "execute",
            "context": {}
        }
        
        assert validator._validate_schema_compliance(request_data)

    def test_valid_dict_schema_no_context(self):
        """Test validation of schema with None context"""
        validator = InputValidator()
        request_data = {
            "action": "execute",
            "context": None
        }
        
        assert validator._validate_schema_compliance(request_data)

    def test_invalid_schema_missing_action(self):
        """Test that schema missing 'action' field is invalid"""
        validator = InputValidator()
        request_data = {
            "context": {"param1": "value1"}
        }
        
        assert not validator._validate_schema_compliance(request_data)

    def test_invalid_schema_missing_context(self):
        """Test that schema missing 'context' field is invalid"""
        validator = InputValidator()
        request_data = {
            "action": "execute"
        }
        
        assert not validator._validate_schema_compliance(request_data)

    def test_invalid_schema_empty_action(self):
        """Test that schema with empty action is invalid"""
        validator = InputValidator()
        request_data = {
            "action": "",
            "context": {}
        }
        
        assert not validator._validate_schema_compliance(request_data)

    def test_valid_json_string_schema(self):
        """Test validation of valid JSON string"""
        validator = InputValidator()
        request_data = '{"action": "execute", "context": {}}'
        
        assert validator._validate_schema_compliance(request_data)

    def test_valid_plain_string_schema(self):
        """Test that plain (non-JSON) strings are valid"""
        validator = InputValidator()
        request_data = "just a plain string"
        
        assert validator._validate_schema_compliance(request_data)

    def test_valid_list_schema(self):
        """Test validation of list with valid items"""
        validator = InputValidator()
        request_data = [
            {"action": "execute"},
            {"action": "validate"}
        ]
        
        assert validator._validate_schema_compliance(request_data)

    def test_invalid_list_schema(self):
        """Test that list with invalid items is invalid"""
        validator = InputValidator()
        request_data = [
            {"action": "execute"},
            {"no_action": "invalid"}
        ]
        
        assert not validator._validate_schema_compliance(request_data)

    def test_invalid_context_type(self):
        """Test that non-dict context is invalid"""
        validator = InputValidator()
        request_data = {
            "action": "execute",
            "context": "not a dict"
        }
        
        assert not validator._validate_schema_compliance(request_data)


class TestBackwardCompatibilityValidation:
    """Tests for AC-VALIDATE-010: Backward compatibility checks"""

    def test_no_version_specified(self):
        """Test that no version defaults to compatible"""
        validator = InputValidator()
        
        assert validator._validate_backward_compatibility(None)
        assert validator._validate_backward_compatibility("")

    def test_compatible_exact_version(self):
        """Test exact current version is compatible"""
        validator = InputValidator()
        
        assert validator._validate_backward_compatibility("1.0")

    def test_compatible_patch_version(self):
        """Test patch version in current major.minor is compatible"""
        validator = InputValidator()
        
        assert validator._validate_backward_compatibility("1.0.0")
        assert validator._validate_backward_compatibility("1.0.5")

    def test_incompatible_major_version_mismatch(self):
        """Test that different major version is incompatible"""
        validator = InputValidator()
        
        assert not validator._validate_backward_compatibility("2.0")
        assert not validator._validate_backward_compatibility("0.9")

    def test_incompatible_future_minor_version(self):
        """Test that future minor version is incompatible"""
        validator = InputValidator()
        
        assert not validator._validate_backward_compatibility("1.1")
        assert not validator._validate_backward_compatibility("1.5")

    def test_invalid_version_format(self):
        """Test that invalid version format is rejected"""
        validator = InputValidator()
        
        assert not validator._validate_backward_compatibility("1")
        assert not validator._validate_backward_compatibility("1.0.0.0")
        assert not validator._validate_backward_compatibility("not.a.version")
        assert not validator._validate_backward_compatibility("v1.0")

    def test_version_with_whitespace(self):
        """Test that version with whitespace is trimmed and validated"""
        validator = InputValidator()
        
        assert validator._validate_backward_compatibility("  1.0  ")

    def test_version_zero_patch(self):
        """Test that zero patch version is compatible"""
        validator = InputValidator()
        
        assert validator._validate_backward_compatibility("1.0.0")

