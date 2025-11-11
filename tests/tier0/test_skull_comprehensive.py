"""
Comprehensive SKULL Protection Layer Tests

Tests the complete SKULL protection system including:
- ASCII banner rendering
- All 5 SKULL rules (001-005)
- Real-world incident prevention
- Multi-violation scenarios
- Enforcement level behavior
- Response template integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
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


class TestSkullBanner:
    """Test SKULL ASCII banner and branding."""
    
    def test_skull_banner_renders(self):
        """Verify SKULL banner includes copyright and branding."""
        skull = SkullProtector()
        
        # Get banner (if SkullProtector has a banner method)
        # This would test header_utils.print_banner_header integration
        banner = skull.get_banner() if hasattr(skull, 'get_banner') else None
        
        if banner:
            assert "CORTEX" in banner
            assert "Asif Hussain" in banner
            assert "github.com/asifhussain60/CORTEX" in banner
        else:
            pytest.skip("Banner method not yet implemented")
    
    def test_violation_message_includes_branding(self):
        """SKULL violations should include proper attribution."""
        skull = SkullProtector()
        
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],
            verification=None,
            description="Untested fix"
        )
        
        validation = skull.validate_fix(request)
        
        # Violation messages should be properly branded
        assert "SKULL" in validation.message
        assert not validation.passed


class TestSkull001TestBeforeClaim:
    """Test SKULL-001: Test Before Claim (BLOCKING)."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_blocks_success_claim_without_tests(self, skull):
        """Must block any success claim without test validation."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],
            verification=None,
            description="Fixed the button ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.rule_id == SkullRuleId.TEST_BEFORE_CLAIM
        assert validation.enforcement == EnforcementLevel.BLOCKING
        assert "SKULL-001" in validation.message
    
    def test_passes_with_test_validation(self, skull):
        """Must pass when tests are provided."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=["test_button_works"],
            verification={"test_passed": True},
            description="Fixed button ✅ (Verified by test_button_works)"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    @pytest.mark.parametrize("claim", [
        "fixed ✅",
        "complete ✅",
        "done ✅",
        "implemented ✅",
        "resolved ✅",
        "working ✅"
    ])
    def test_detects_all_success_claims(self, skull, claim):
        """Must detect all forms of success claims."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],
            verification=None,
            description=f"The issue is now {claim}"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed, f"Should detect claim: {claim}"


class TestSkull002IntegrationVerification:
    """Test SKULL-002: Integration Verification (BLOCKING)."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_blocks_integration_without_e2e_test(self, skull):
        """Must block integration claims without end-to-end tests."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_component_a_unit", "test_component_b_unit"],
            verification=None,
            description="Integrated Vision API with Intent Router"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.rule_id == SkullRuleId.INTEGRATION_VERIFICATION
        assert "SKULL-002" in validation.message
    
    def test_passes_with_e2e_test(self, skull):
        """Must pass when end-to-end test is provided."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_vision_api_intent_router_e2e"],
            verification={"end_to_end_verified": True},
            description="Integrated Vision API with Intent Router"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    @pytest.mark.parametrize("test_name", [
        "test_full_integration",
        "test_end_to_end_workflow",
        "test_e2e_pipeline",
        "test_integration_complete"
    ])
    def test_detects_integration_test_patterns(self, skull, test_name):
        """Must recognize various integration test naming patterns."""
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=[test_name],
            verification=None,
            description="Component integration"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should recognize: {test_name}"


class TestSkull003VisualRegression:
    """Test SKULL-003: Visual Regression (WARNING)."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_warns_css_change_without_visual_test(self, skull):
        """Must warn on CSS changes without visual validation."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_file_exists"],
            verification=None,
            description="Fixed title color"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.rule_id == SkullRuleId.VISUAL_REGRESSION
        assert validation.enforcement == EnforcementLevel.WARNING
        assert "SKULL-003" in validation.message
    
    def test_passes_css_change_with_visual_test(self, skull):
        """Must pass CSS changes with visual validation."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_computed_style_title_color"],
            verification={"computed_style": "rgb(31, 41, 55)"},
            description="Fixed title color"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    @pytest.mark.parametrize("test_name", [
        "test_visual_regression",
        "test_computed_style",
        "test_browser_render",
        "test_playwright_screenshot",
        "test_css_computed"
    ])
    def test_detects_visual_test_patterns(self, skull, test_name):
        """Must recognize various visual test naming patterns."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=[test_name],
            verification=None,
            description="UI update"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed, f"Should recognize: {test_name}"


class TestSkull004RetryWithoutLearning:
    """Test SKULL-004: Retry Without Learning (WARNING)."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_warns_retry_without_diagnosis(self, skull):
        """Must warn on retries without root cause diagnosis."""
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=["test_same_approach"],
            verification={"retry": True},
            description="Retry CSS fix (attempt 2)"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.rule_id == SkullRuleId.RETRY_WITHOUT_LEARNING
        assert "SKULL-004" in validation.message
    
    def test_passes_retry_with_diagnosis(self, skull):
        """Must pass retries that include diagnosis."""
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=["test_after_cache_clear"],
            verification={
                "diagnosis": "Root cause: Browser cache not cleared",
                "approach_changed": True
            },
            description="Retry after diagnosis: cache issue"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    def test_requires_changed_approach(self, skull):
        """Must detect if approach actually changed."""
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=["test_same_test"],
            verification={
                "diagnosis": "I looked at it",
                "approach_changed": False  # Same approach!
            },
            description="Retry with same approach"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed


class TestSkull005TransformationVerification:
    """Test SKULL-005: Transformation Verification (BLOCKING)."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_blocks_transformation_claim_without_changes(self, skull):
        """Must block transformation claims without file changes."""
        request = FixValidationRequest(
            fix_type="transformation",
            tests_run=["test_operation_runs"],
            verification={
                "file_hash_before": "abc123",
                "file_hash_after": "abc123"  # NO CHANGE!
            },
            description="Transformation complete ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.rule_id == SkullRuleId.TRANSFORMATION_VERIFICATION
        assert "SKULL-005" in validation.message
    
    def test_passes_transformation_with_changes(self, skull):
        """Must pass when transformation produces actual changes."""
        request = FixValidationRequest(
            fix_type="transformation",
            tests_run=["test_operation_runs"],
            verification={
                "file_hash_before": "abc123",
                "file_hash_after": "def456"  # CHANGED!
            },
            description="Transformation complete ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    def test_allows_validation_only_operations(self, skull):
        """Must allow operations marked as validation-only."""
        request = FixValidationRequest(
            fix_type="validation_only",
            tests_run=["test_validation_passed"],
            verification={
                "file_hash_before": "abc123",
                "file_hash_after": "abc123",  # No change expected
                "validation_only": True  # Explicit marker
            },
            description="Validation complete ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert validation.passed
    
    def test_detects_pass_through_operations(self, skull):
        """Must detect when operation is a pass-through."""
        request = FixValidationRequest(
            fix_type="transformation",
            tests_run=["test_runs"],
            verification={
                "input_content": "Hello World",
                "output_content": "Hello World",  # PASS-THROUGH!
                "git_diff_lines": 0
            },
            description="Applied transformation ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed


class TestRealWorldIncidentPrevention:
    """Test prevention of actual historical incidents."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_prevents_november_9th_css_incident(self, skull):
        """
        Prevent: CSS applied 3 times, claimed "fixed" each time, no tests.
        """
        # Attempt 1: No test
        attempt_1 = FixValidationRequest(
            fix_type="css_change",
            tests_run=[],
            verification=None,
            description="Fixed title color ✅"
        )
        
        validation_1 = skull.validate_fix(attempt_1)
        assert not validation_1.passed, "SKULL should block attempt 1"
        
        # Attempt 2: Still no test (SKULL-004 warning)
        attempt_2 = FixValidationRequest(
            fix_type="retry",
            tests_run=[],
            verification=None,
            description="Fixed title color again ✅ (attempt 2)"
        )
        
        validation_2 = skull.validate_fix(attempt_2)
        assert not validation_2.passed, "SKULL should block attempt 2"
        
        # Attempt 3: CORRECT - with visual test
        attempt_3 = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_title_computed_style"],
            verification={"computed_color": "rgb(31, 41, 55)"},
            description="Fixed title color ✅ (Verified by test)"
        )
        
        validation_3 = skull.validate_fix(attempt_3)
        assert validation_3.passed, "SKULL should pass attempt 3"
    
    def test_prevents_november_9th_vision_api_incident(self, skull):
        """
        Prevent: Integration "implemented", config changed, no E2E test.
        """
        # False claim: Config only
        false_claim = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_config_has_vision_key"],
            verification=None,
            description="Vision API auto-engages ✅"
        )
        
        validation = skull.validate_fix(false_claim)
        assert not validation.passed, "SKULL should block false claim"
        assert "SKULL-002" in validation.message
        
        # CORRECT: With E2E test
        proper_implementation = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_vision_api_auto_engagement_e2e"],
            verification={"vision_api_called": True},
            description="Vision API auto-engages ✅ (E2E verified)"
        )
        
        validation = skull.validate_fix(proper_implementation)
        assert validation.passed
    
    def test_prevents_november_10th_story_refresh_incident(self, skull):
        """
        Prevent: Operation claims "transformation complete" but produces no changes.
        """
        # Pass-through operation claiming transformation
        fake_transformation = FixValidationRequest(
            fix_type="transformation",
            tests_run=["test_operation_runs"],
            verification={
                "file_hash_before": "abc123",
                "file_hash_after": "abc123",
                "git_diff_empty": True
            },
            description="Story refresh transformation complete ✅"
        )
        
        validation = skull.validate_fix(fake_transformation)
        assert not validation.passed, "SKULL should detect fake transformation"
        assert "SKULL-005" in validation.message


class TestMultipleViolations:
    """Test scenarios with multiple SKULL violations."""
    
    @pytest.fixture
    def skull(self):
        return SkullProtector()
    
    def test_css_retry_without_tests_or_diagnosis(self, skull):
        """
        Multiple violations:
        - SKULL-001: No tests
        - SKULL-003: CSS without visual test
        - SKULL-004: Retry without diagnosis
        """
        request = FixValidationRequest(
            fix_type="retry",
            tests_run=[],
            verification=None,
            description="Retry CSS fix (attempt 3)"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        # Should report the most severe violation first (BLOCKING > WARNING)
        assert validation.enforcement == EnforcementLevel.BLOCKING
    
    def test_integration_transformation_without_verification(self, skull):
        """
        Multiple violations:
        - SKULL-002: No E2E test
        - SKULL-005: No file changes
        """
        request = FixValidationRequest(
            fix_type="integration",
            tests_run=["test_unit_only"],
            verification={
                "file_hash_before": "xyz",
                "file_hash_after": "xyz"
            },
            description="Integration complete, files transformed ✅"
        )
        
        validation = skull.validate_fix(request)
        
        assert not validation.passed
        assert validation.enforcement == EnforcementLevel.BLOCKING


class TestEnforcementBehavior:
    """Test enforcement level behavior."""
    
    def test_blocking_raises_exception(self):
        """BLOCKING violations must raise SkullProtectionError."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=[],
            verification=None,
            description="Fixed ✅"
        )
        
        with pytest.raises(SkullProtectionError) as exc_info:
            enforce_skull(request)
        
        assert "SKULL" in str(exc_info.value)
    
    def test_warning_returns_validation(self):
        """WARNING violations return validation result, don't raise."""
        request = FixValidationRequest(
            fix_type="css_change",
            tests_run=["test_file_changed"],
            verification=None,
            description="CSS updated"
        )
        
        # Should not raise, but validation fails
        validation = enforce_skull(request)
        
        assert not validation.passed
        assert validation.enforcement == EnforcementLevel.WARNING
    
    def test_safe_passes_through(self):
        """Safe requests pass without issues."""
        request = FixValidationRequest(
            fix_type="bug_fix",
            tests_run=["test_bug_fixed"],
            verification={"test_passed": True},
            description="Fixed bug ✅ (Verified)"
        )
        
        validation = enforce_skull(request)
        
        assert validation.passed
        assert validation.enforcement == EnforcementLevel.SAFE


class TestSkullResponseTemplateIntegration:
    """Test SKULL integration with response templates."""
    
    def test_help_command_shows_skull_banner(self):
        """
        Verify response template includes SKULL ASCII banner.
        This tests the YAML update made to response-templates.yaml.
        """
        # This would require loading response-templates.yaml
        # and checking the help_table template
        import yaml
        from pathlib import Path
        
        template_path = Path("d:/PROJECTS/CORTEX/cortex-brain/response-templates.yaml")
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            help_template = templates.get('templates', {}).get('help_table', {})
            content = help_template.get('content', '')
            
            # Check for ASCII banner elements
            assert "██" in content or "╔" in content, "Should include ASCII art"
            assert "CORTEX" in content
            assert "Asif Hussain" in content
        else:
            pytest.skip("Response templates file not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
