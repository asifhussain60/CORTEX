"""
Tests for SKULL Protection Layer.

Validates that SKULL rules prevent the types of violations that occurred
in the November 9th incident (CSS + Vision API testing failures).
"""
import pytest
from src.tier0.skull_protector import (
    SkullProtector,
    SkullProtectionError,
    SkullRuleId,
    EnforcementLevel,
    FixValidationRequest,
    enforce_skull
)


class TestSkullProtector:
    """Test suite for SKULL protection layer."""
    
    @pytest.fixture
    def skull(self):
        """Create SkullProtector instance."""
        return SkullProtector()
    
    # ============================================
    # SKULL-001: Test Before Claim
    # ============================================
    
    def test_skull_001_blocks_fix_without_tests(self, skull):
        """SKULL-001: Must block fixes claimed without test validation."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],  # NO TESTS
            verification=None,
            description="Fix button color"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, "Should fail without tests"
        assert validation.rule_id == SkullRuleId.TEST_BEFORE_CLAIM
        assert validation.enforcement == EnforcementLevel.BLOCKING
        assert "SKULL-001 VIOLATION" in validation.message
    
    def test_skull_001_passes_fix_with_tests(self, skull):
        """SKULL-001: Must pass fixes with test validation."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=["test_button_color_is_dark"],
            verification={"test_passed": True},
            description="Fix button color"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should pass with tests: {validation.message}"
    
    def test_skull_001_raises_exception_on_blocking_violation(self):
        """SKULL-001: Must raise exception for blocking violations."""
        request = FixValidationRequest(
            fix_type="feature",
            tests_run=[],
            verification=None,
            description="Add new feature"
        )
        
        with pytest.raises(SkullProtectionError) as exc_info:
            enforce_skull(request)
        
        assert "SKULL-001" in str(exc_info.value)
    
    # ============================================
    # SKULL-002: Integration Verification
    # ============================================
    
    def test_skull_002_blocks_integration_without_e2e_test(self, skull):
        """SKULL-002: Must block integrations without end-to-end tests."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_unit_component_a", "test_unit_component_b"],  # Only unit tests
            verification=None,
            description="Integrate Vision API with Intent Router"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, "Should fail without integration test"
        assert validation.rule_id == SkullRuleId.INTEGRATION_VERIFICATION
        assert validation.enforcement == EnforcementLevel.BLOCKING
        assert "SKULL-002 VIOLATION" in validation.message
    
    def test_skull_002_passes_integration_with_e2e_test(self, skull):
        """SKULL-002: Must pass integrations with end-to-end tests."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=[
                "test_unit_component_a",
                "test_vision_api_auto_engagement_end_to_end"  # E2E test
            ],
            verification={"integration_verified": True},
            description="Integrate Vision API with Intent Router"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should pass with E2E test: {validation.message}"
    
    def test_skull_002_detects_integration_keyword(self, skull):
        """SKULL-002: Must detect 'integration' keyword in test names."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_screenshot_analyzer_integration"],
            verification=None,
            description="Connect components"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, "Should pass with integration test"
    
    # ============================================
    # SKULL-003: Visual Regression
    # ============================================
    
    def test_skull_003_warns_css_change_without_visual_test(self, skull):
        """SKULL-003: Must warn on CSS changes without visual validation."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_file_exists"],  # Not a visual test
            verification=None,
            description="Fix title color"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, "Should fail without visual test"
        assert validation.rule_id == SkullRuleId.VISUAL_REGRESSION
        assert validation.enforcement == EnforcementLevel.WARNING  # Warning, not blocking
        assert "SKULL-003 VIOLATION" in validation.message
    
    def test_skull_003_passes_css_change_with_visual_test(self, skull):
        """SKULL-003: Must pass CSS changes with visual validation."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_css_title_color_is_dark"],
            verification={"computed_style": "rgb(31, 41, 55)"},
            description="Fix title color"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should pass with CSS test: {validation.message}"
    
    def test_skull_003_detects_visual_keywords(self, skull):
        """SKULL-003: Must detect visual/CSS/style keywords in test names."""
        visual_tests = [
            "test_visual_regression_title",
            "test_css_computed_style",
            "test_browser_renders_correctly",
            "test_style_applied"
        ]
        
        for test_name in visual_tests:
            request = FixValidationRequest(
                fix_type="css_change",
                tests_run=[test_name],
                verification=None,
                description="UI change"
            )
            
            validation = skull.validate_fix(request)
            
            assert validation.passed, f"Should detect visual test: {test_name}"
    
    # ============================================
    # SKULL-004: Retry Without Learning
    # ============================================
    
    def test_skull_004_warns_retry_without_diagnosis(self, skull):
        """SKULL-004: Must warn on retries without root cause diagnosis."""
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=["test_same_as_before"],
            verification={"retry": True},  # No diagnosis
            description="Retry CSS fix"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, "Should fail without diagnosis"
        assert validation.rule_id == SkullRuleId.RETRY_WITHOUT_LEARNING
        assert validation.enforcement == EnforcementLevel.WARNING
        assert "SKULL-004 VIOLATION" in validation.message
    
    def test_skull_004_passes_retry_with_diagnosis(self, skull):
        """SKULL-004: Must pass retries that include diagnosis."""
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=["test_with_cache_cleared"],
            verification={
                "diagnosis": "Root cause: Browser cache not cleared",
                "fix_approach_changed": True
            },
            description="Retry CSS fix after diagnosis"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should pass with diagnosis: {validation.message}"
    
    def test_skull_004_skips_non_retry_requests(self, skull):
        """SKULL-004: Must not check SKULL-004 for non-retry requests."""
        request = FixValidationRequest(
            fix_type="bug_fix",  # Not a retry
            tests_run=["test_feature"],
            verification=None,
            description="Initial fix"
        )
        
        # Should not trigger SKULL-004
        validation = skull.validate_fix(request)
        
        # May fail on other rules, but not SKULL-004
        if not validation.passed:
            assert validation.rule_id != SkullRuleId.RETRY_WITHOUT_LEARNING
    
    # ============================================
    # Real-World Incident Prevention Tests
    # ============================================
    
    def test_prevents_css_incident_november_9th(self, skull):
        """
        Prevent CSS incident from November 9th:
        - CSS applied 3 times
        - Claimed "fixed" each time
        - No visual tests created
        """
        # First attempt - no test
        attempt_1 = FixValidationRequest(
            fix_type="css_change",
            tests_run=[],
            verification=None,
            description="Fix title color (attempt 1)"
        )
        
        validation_1 = skull.validate_fix(attempt_1)
        assert not validation_1.passed, "SKULL should block attempt 1"
        
        # Second attempt - still no test
        attempt_2 = FixValidationRequest(
            fix_type="css_change",
            tests_run=[],
            verification=None,
            description="Fix title color (attempt 2)"
        )
        
        validation_2 = skull.validate_fix(attempt_2)
        assert not validation_2.passed, "SKULL should block attempt 2"
        
        # Third attempt - CORRECT: with visual test
        attempt_3 = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_css_title_color_is_dark"],
            verification={"computed_color": "rgb(31, 41, 55)"},
            description="Fix title color (attempt 3 - with test)"
        )
        
        validation_3 = skull.validate_fix(attempt_3)
        assert validation_3.passed, "SKULL should pass attempt 3 with test"
    
    def test_prevents_vision_api_incident_november_9th(self, skull):
        """
        Prevent Vision API incident from November 9th:
        - Integration "implemented" without testing
        - Config changed but no call chain verified
        - Claimed "auto-engages" without proof
        """
        # Config change without integration test
        false_claim = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_config_has_vision_key"],  # Only config test
            verification=None,
            description="Enable Vision API auto-engagement"
        )
        
        validation = skull.validate_fix(false_claim)
        assert not validation.passed, "SKULL should block false integration claim"
        assert "SKULL-002" in validation.message
        
        # CORRECT: With end-to-end test
        proper_implementation = FixValidationRequest(
            fix_type="integration",
            tests_run=[
                "test_config_has_vision_key",
                "test_vision_api_auto_engagement_end_to_end"
            ],
            verification={"vision_api_called": True},
            description="Enable Vision API with E2E verification"
        )
        
        validation = skull.validate_fix(proper_implementation)
        assert validation.passed, "SKULL should pass proper implementation"
    
    # ============================================
    # Enforcement Level Tests
    # ============================================
    
    def test_blocking_rules_prevent_execution(self):
        """BLOCKING rules must raise exception via enforce_skull()."""
        blocking_request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],  # Triggers SKULL-001 (BLOCKING)
            verification=None,
            description="Untested fix"
        )
        
        with pytest.raises(SkullProtectionError):
            enforce_skull(blocking_request)
    
    def test_warning_rules_allow_execution(self):
        """WARNING rules must not raise exception."""
        warning_request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_file_changed"],  # Triggers SKULL-003 (WARNING)
            verification=None,
            description="CSS without visual test"
        )
        
        # Should not raise exception, but validation fails
        validation = enforce_skull(warning_request)
        assert not validation.passed
        assert validation.enforcement == EnforcementLevel.WARNING
    
    # ============================================
    # Multiple Fix Types
    # ============================================
    
    @pytest.mark.parametrize("fix_type", [
        "bug_fix", "feature", "refactor", "css_change"
    ])
    def test_skull_001_applies_to_all_fix_types(self, skull, fix_type):
        """SKULL-001 must apply to all fix types."""
        request = FixValidationRequest(
            fix_type=fix_type,
            tests_run=[],
            verification=None,
            description=f"Fix of type: {fix_type}"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, f"SKULL-001 should apply to {fix_type}"
        assert validation.rule_id == SkullRuleId.TEST_BEFORE_CLAIM


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
