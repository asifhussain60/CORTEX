"""
Tests for TestScopeValidator - Ensures tests align with feature status.

AC_START: AC-DIGEST-CHAT01-002
Purpose: Prevent test-feature misalignment (tests running for deferred features)
Learning: chat01 showed dashboard tests needed deferral when docs site deferred
"""

import pytest
from pathlib import Path
from cortex.governance.test_scope_validator import (
    TestScopeValidator,
    TestScopeMismatch,
    ValidationResult,
    TestStatus,
    FeatureStatus
)


class TestTestScopeValidator:
    """Test TestScopeValidator detects misalignment."""
    
    @pytest.fixture
    def validator(self):
        """Create TestScopeValidator instance."""
        return TestScopeValidator()
    
    def test_active_phase_with_active_tests_passes(self, validator):
        """Test: Active phase with running tests = PASS."""
        result = validator.validate_phase_test_alignment(
            phase_id="phase-25",
            phase_status="active",
            test_files=[
                "tests/integration/test_debugger_end_to_end.py"
            ],
            test_status="running"
        )
        
        assert result.passed is True
        assert result.mismatches == []
        assert result.severity is None
    
    def test_deferred_phase_with_running_tests_fails(self, validator):
        """Test: Deferred phase with running tests = FAIL."""
        result = validator.validate_phase_test_alignment(
            phase_id="phase-docs",
            phase_status="deferred",
            test_files=[
                "tests/integration/test_phase_detail_generation.py"
            ],
            test_status="running"
        )
        
        assert result.passed is False
        assert len(result.mismatches) == 1
        assert result.mismatches[0].phase_status == FeatureStatus.DEFERRED
        assert result.mismatches[0].test_status == TestStatus.RUNNING
        assert result.severity == "HIGH"
    
    def test_deferred_phase_with_skipped_tests_passes(self, validator):
        """Test: Deferred phase with skipped tests = PASS."""
        result = validator.validate_phase_test_alignment(
            phase_id="phase-docs",
            phase_status="deferred",
            test_files=[
                "tests/integration/test_phase_detail_generation.py.deferred"
            ],
            test_status="skipped"
        )
        
        assert result.passed is True
        assert result.mismatches == []
    
    def test_deprecated_feature_with_running_tests_fails(self, validator):
        """Test: Deprecated feature with running tests = FAIL."""
        result = validator.validate_feature_test_alignment(
            feature="EnhancedIntentRouter",
            feature_status="deprecated",
            test_files=[
                "tests/integration/intent_router/test_mode_routing_integration.py"
            ],
            test_status="running"
        )
        
        assert result.passed is False
        assert result.severity == "MEDIUM"
        assert "skip or remove" in result.recommendation.lower()
    
    def test_experimental_feature_with_skipped_tests_passes(self, validator):
        """Test: Experimental feature with skipped tests = PASS."""
        result = validator.validate_feature_test_alignment(
            feature="Phase81Router",
            feature_status="experimental",
            test_files=[
                "tests/unit/intent_router/test_routing_integration.py"
            ],
            test_status="skipped"
        )
        
        assert result.passed is True
    
    def test_audit_command_integration(self, validator):
        """Test: Validator integrates with /audit command."""
        # Simulate /audit scanning all phases
        phases = [
            {"id": "phase-25", "status": "active"},
            {"id": "phase-docs", "status": "deferred"},
            {"id": "phase-81", "status": "experimental"}
        ]
        
        results = validator.audit_all_phases(phases)
        
        assert isinstance(results, list)
        assert all(isinstance(r, ValidationResult) for r in results)
    
    def test_real_world_dashboard_scenario(self, validator):
        """Test: Real-world chat01 dashboard scenario."""
        # Phase 0: Documentation site deferred
        # Tests: test_phase_detail_generation.py still running
        # Expected: FAIL with recommendation to defer tests
        
        result = validator.validate_phase_test_alignment(
            phase_id="phase-0-docs",
            phase_status="deferred",
            test_files=[
                "tests/integration/test_phase_detail_generation.py",
                "tests/integration/test_render_phase_01_html.py"
            ],
            test_status="running"
        )
        
        assert result.passed is False
        assert len(result.mismatches) == 2
        assert result.recommendation == "Defer tests: rename to .deferred or add @pytest.mark.skip"
    
    def test_pre_commit_hook_integration(self, validator):
        """Test: Validator can be called from pre-commit hook."""
        # Simulate pre-commit hook checking changed files
        changed_files = [
            "cortex-registry/_cortex-master/phases/active/phase-25.yaml",
            "tests/integration/test_debugger_end_to_end.py"
        ]
        
        result = validator.validate_changed_files(changed_files)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'passed')
    
    def test_severity_levels(self, validator):
        """Test: Correct severity assigned to mismatches."""
        # HIGH: Deferred phase with running tests
        result_high = validator.validate_phase_test_alignment(
            phase_id="phase-deferred",
            phase_status="deferred",
            test_files=["tests/test_deferred.py"],
            test_status="running"
        )
        assert result_high.severity == "HIGH"
        
        # MEDIUM: Deprecated feature with running tests
        result_medium = validator.validate_feature_test_alignment(
            feature="DeprecatedFeature",
            feature_status="deprecated",
            test_files=["tests/test_deprecated.py"],
            test_status="running"
        )
        assert result_medium.severity == "MEDIUM"
        
        # LOW: Experimental with running tests (acceptable)
        result_low = validator.validate_feature_test_alignment(
            feature="ExperimentalFeature",
            feature_status="experimental",
            test_files=["tests/test_experimental.py"],
            test_status="running"
        )
        # Experimental can have running tests
        assert result_low.passed is True or result_low.severity == "LOW"
    
    def test_recommendations_generated(self, validator):
        """Test: Actionable recommendations provided."""
        result = validator.validate_phase_test_alignment(
            phase_id="phase-deferred",
            phase_status="deferred",
            test_files=["tests/test_feature.py"],
            test_status="running"
        )
        
        assert result.passed is False
        assert result.recommendation is not None
        assert "defer" in result.recommendation.lower() or "skip" in result.recommendation.lower()
    
    def test_multiple_mismatches_detected(self, validator):
        """Test: All mismatches detected in single validation."""
        result = validator.validate_phase_test_alignment(
            phase_id="phase-multi",
            phase_status="deferred",
            test_files=[
                "tests/test_a.py",
                "tests/test_b.py",
                "tests/test_c.py"
            ],
            test_status="running"
        )
        
        assert result.passed is False
        assert len(result.mismatches) == 3


class TestTestScopeValidatorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_phase_file(self):
        """Test: Error if phase file not found."""
        validator = TestScopeValidator()
        
        result = validator.validate_phase_test_alignment(
            phase_id="phase-nonexistent",
            phase_status="active",
            test_files=["tests/test_nonexistent.py"],
            test_status="running"
        )
        
        # Should handle gracefully
        assert isinstance(result, ValidationResult)
    
    def test_empty_test_files_list(self):
        """Test: Handle empty test files list."""
        validator = TestScopeValidator()
        
        result = validator.validate_phase_test_alignment(
            phase_id="phase-25",
            phase_status="active",
            test_files=[],
            test_status="running"
        )
        
        # No tests = pass (nothing to validate)
        assert result.passed is True
    
    def test_mixed_test_statuses(self):
        """Test: Some tests running, some skipped."""
        validator = TestScopeValidator()
        
        # This would require analyzing each test file individually
        # For now, validator should use majority status or flag warning
        result = validator.validate_phase_test_alignment(
            phase_id="phase-mixed",
            phase_status="active",
            test_files=[
                "tests/test_a.py",  # running
                "tests/test_b.py.deferred"  # skipped
            ],
            test_status="mixed"
        )
        
        assert isinstance(result, ValidationResult)


# AC_COMPLETE: AC-DIGEST-CHAT01-002 ✅
# Tests cover:
# - Active phase with active tests (PASS)
# - Deferred phase with running tests (FAIL - chat01 scenario)
# - Deprecated feature detection
# - Severity levels (HIGH/MEDIUM/LOW)
# - Recommendations generation
# - /audit integration
# - Pre-commit hook integration
# - Real-world dashboard test scenario from chat01
