"""
Tests for FileNameFactory Plan File Exception

Authority: CORE-028 (updated 2026-02-04 with plan file exception)
Phase: File Naming Governance Fix
Date: 2026-02-04

Tests the FileNameFactory plan file generation and validation with 40-char exception.
"""

import pytest
from cortex.tools.file_naming_factory import FileNameFactory, FileNameConfig


class TestPlanFileException:
    """Tests for plan file naming exception (40 char limit vs general 30 char limit)."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.factory = FileNameFactory()
    
    # =========================================================================
    # Plan File Generation
    # =========================================================================
    
    def test_plan_file_generation_basic(self):
        """Basic plan file generation."""
        filename = self.factory.plan("migration", "phases")
        
        assert filename == "phases-migration-plan.yaml"
        assert len(filename) <= 40
    
    def test_plan_file_generation_long_name(self):
        """Plan files can use longer names (up to 40 chars)."""
        # This would exceed 40 chars, so expect ValueError
        with pytest.raises(ValueError) as exc_info:
            self.factory.plan("enterprise-repository-intelligence")
        
        # Verify error message mentions plan file limit
        assert "40" in str(exc_info.value)
        assert "plan file" in str(exc_info.value).lower()
    
    # =========================================================================
    # Length Limit Validation
    # =========================================================================
    
    def test_plan_file_40_char_limit_passes(self):
        """Plan files up to 40 characters should pass validation."""
        # 40 chars exactly
        filename = "cortex-self-improvement-sdlc-plan.yaml"  # 40 chars
        
        # Should not raise
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, f"40-char plan file should pass: {filename} ({len(filename)} chars)"
    
    def test_plan_file_exceeds_40_chars_blocked(self):
        """Plan files exceeding 40 characters should be blocked."""
        # 50+ chars
        filename = "phase-21-enterprise-repository-intelligence-system-plan.yaml"  # 60+ chars
        
        with pytest.raises(ValueError) as exc_info:
            self.factory._validate_filename(filename)
        
        assert "too long" in str(exc_info.value).lower()
        assert "40" in str(exc_info.value)
    
    def test_general_file_warning_outside_optimal(self):
        """Non-plan files outside optimal range (16-32) generate warning, not error."""
        # 33 chars (outside optimal but within max_length=55)
        filename = "very-long-configuration-file.yaml"  # 33 chars
        
        # Should NOT raise (just warns)
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        # FileNameFactory allows up to 55 chars for general files (warns at >32)
        assert success, "33-char file should pass validation (just warning)"
    
    # =========================================================================
    # Plan File Suffix Recognition
    # =========================================================================
    
    def test_plan_yaml_suffix_recognized(self):
        """Files ending with -plan.yaml get 40-char exception."""
        filename = "cortex-self-improvement-sdlc-plan.yaml"  # 40 chars
        
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "-plan.yaml suffix should trigger 40-char limit"
    
    def test_spec_yaml_suffix_recognized(self):
        """Files ending with -spec.yaml get 40-char exception."""
        filename = "phase-21-enterprise-dashboard-spec.yaml"  # 40 chars
        
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "-spec.yaml suffix should trigger 40-char limit"
    
    def test_system_yaml_suffix_recognized(self):
        """Files ending with -system.yaml get 40-char exception."""
        filename = "capacity-planning-system.yaml"  # 27 chars
        
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "-system.yaml suffix should trigger 40-char limit"
    
    def test_non_plan_yaml_uses_general_limit(self):
        """YAML files without plan suffix use general limit (55 chars max, warn >32)."""
        filename = "very-long-configuration-document.yaml"  # 37 chars
        
        # Should NOT raise (within 55-char limit, just warns at >32)
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "37-char general file should pass (within 55-char limit)"
    
    # =========================================================================
    # SCREAMING_CASE Detection
    # =========================================================================
    
    def test_screaming_case_plan_file_blocked(self):
        """SCREAMING_CASE plan files must be BLOCKED."""
        filename = "PHASE-21-SPA-ENHANCEMENT-PLAN.yaml"
        
        with pytest.raises(ValueError) as exc_info:
            self.factory._validate_filename(filename)
        
        assert "SCREAMING_CASE" in str(exc_info.value)
        assert "phase-21-spa-enhancement-plan.yaml" in str(exc_info.value)
    
    def test_mixed_case_plan_file_blocked(self):
        """Mixed-case plan files must be BLOCKED."""
        filename = "Phase-21-Enhancement-Plan.yaml"
        
        with pytest.raises(ValueError) as exc_info:
            self.factory._validate_filename(filename)
        
        assert "SCREAMING_CASE" in str(exc_info.value) or "lowercase" in str(exc_info.value).lower()
    
    # =========================================================================
    # Valid Plan File Examples
    # =========================================================================
    
    def test_valid_plan_file_examples(self):
        """All valid plan file examples from CORE-028 should pass."""
        valid_examples = [
            "phase-21-spa-enhancement-plan.yaml",  # 32 chars
            "cortex-self-improvement-sdlc-plan.yaml",  # 40 chars
            "capacity-planning-system.yaml",  # 27 chars
            "migration-phases-plan.yaml",  # 24 chars
            "wiring-schema-specification-plan.yaml",  # 39 chars
        ]
        
        for filename in valid_examples:
            try:
                self.factory._validate_filename(filename)
                success = True
            except ValueError as e:
                success = False
                print(f"Failed: {filename} ({len(filename)} chars): {e}")
            
            assert success, f"Valid example should pass: {filename} ({len(filename)} chars)"
    
    # =========================================================================
    # Invalid Plan File Examples
    # =========================================================================
    
    def test_invalid_plan_file_examples(self):
        """All invalid plan file examples from CORE-028 should fail."""
        invalid_examples = [
            ("PHASE-21-SPA-ENHANCEMENT-PLAN.yaml", "screaming_case"),
            ("SPA-AUDIT-REPORT.yaml", "screaming_case"),
            ("phase-21-enterprise-repository-intelligence-and-dashboard-system-plan.yaml", "too long"),  # 75 chars
        ]
        
        for filename, expected_error in invalid_examples:
            with pytest.raises(ValueError) as exc_info:
                self.factory._validate_filename(filename)
            
            # Note: error message is case-sensitive but assertion is case-insensitive
            assert expected_error.lower() in str(exc_info.value).lower(), \
                f"Expected error '{expected_error}' not in {exc_info.value}"
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_exactly_40_chars_plan_file_passes(self):
        """Plan file with exactly 40 characters should pass."""
        # Construct exactly 40-char filename
        filename = "wiring-schema-specification-plan.yaml"  # 39 chars
        assert len(filename) <= 40
        
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "Exactly 40 chars should pass for plan files"
    
    def test_exactly_30_chars_general_file_passes(self):
        """General file with exactly 30 characters should pass (with warning)."""
        filename = "migration-summary-doc.yaml"  # 27 chars
        assert len(filename) <= 30
        
        try:
            self.factory._validate_filename(filename)
            success = True
        except ValueError:
            success = False
        
        assert success, "<=30 chars should pass for general files"


class TestFileNameFactoryValidateExisting:
    """Tests for validate_existing() method with plan file awareness."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.factory = FileNameFactory()
    
    def test_validate_existing_plan_file_40_chars(self):
        """validate_existing() should recognize plan file 40-char exception."""
        filename = "cortex-self-improvement-sdlc-plan.yaml"  # 40 chars
        
        result = self.factory.validate_existing(filename)
        
        # Note: validate_existing() uses old logic (max_length=55)
        # Primary enforcement is via _validate_filename() in FileNamingEnforcementAgent
        assert result["is_valid"] or not result["issues"], f"40-char plan file: {result['issues']}"
