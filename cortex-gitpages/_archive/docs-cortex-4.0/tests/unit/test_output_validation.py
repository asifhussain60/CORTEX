"""
Tests for Issue #5: LLM Output Validation Layer

Validates safety checks for LLM responses.
"""

import pytest
import json
from cortex.core.safety.output_validator import (
    LLMOutputValidator,
    ValidationSeverity,
    validate_llm_output,
)


class TestOutputValidation:
    """Test LLM output validation."""
    
    def test_valid_json_passes(self):
        """Valid JSON response should pass validation."""
        validator = LLMOutputValidator()
        output = '{"response": "Hello", "status": "success"}'
        
        result = validator.validate(output)
        
        assert result.is_valid is True
        assert result.score == 1.0
        assert len(result.violations) == 0
    
    def test_invalid_json_fails(self):
        """Invalid JSON should fail validation."""
        validator = LLMOutputValidator()
        output = '{invalid json}'
        
        result = validator.validate(output)
        
        assert result.is_valid is False
        assert any(v.rule == "json_format" for v in result.violations)
    
    def test_token_limit_enforced(self):
        """Response exceeding token limit should fail."""
        validator = LLMOutputValidator(max_tokens=100)
        huge_response = '{"response": "' + " word" * 200 + '"}'
        
        result = validator.validate(huge_response)
        
        assert result.is_valid is False
        assert any(v.rule == "token_limit" for v in result.violations)
    
    def test_token_limit_warning(self):
        """Response close to token limit should warn."""
        validator = LLMOutputValidator(max_tokens=100)
        large_response = '{"response": "' + " word" * 88 + '"}'  # ~88-90% of limit
        
        result = validator.validate(large_response)
        
        assert result.is_valid is True  # Still valid
        assert any(
            v.rule == "token_limit_warning"
            for v in result.violations
        )
    
    def test_harmful_content_detected(self):
        """Harmful patterns should be detected."""
        validator = LLMOutputValidator()
        
        harmful_patterns = [
            '{"cmd": "rm -rf /"}',
            '{"exec": "exec(code)"}',
            '{"sql": "DROP TABLE users"}',
        ]
        
        for pattern in harmful_patterns:
            result = validator.validate(pattern)
            assert result.is_valid is False
            assert any(
                v.rule == "harmful_content"
                for v in result.violations
            )
    
    def test_prompt_leakage_detected(self):
        """System prompt leakage should be detected."""
        validator = LLMOutputValidator()
        
        leaky_patterns = [
            '{"leaked": "system prompt"}',
            '{"note": "system_message"}',
            '{"secret": "your instructions"}',
        ]
        
        for pattern in leaky_patterns:
            result = validator.validate(pattern)
            assert result.is_valid is False
            assert any(
                v.rule == "prompt_leakage"
                for v in result.violations
            )
    
    def test_output_sanitization(self):
        """Output should be sanitized of harmful content."""
        validator = LLMOutputValidator()
        dangerous = '{"response": "rm -rf /", "system_prompt": "evil"}'
        
        result = validator.validate(dangerous)
        
        # Sanitized output should have markers
        assert "[BLOCKED:" in result.sanitized or "system_prompt" not in result.sanitized
    
    def test_json_structure_validation(self):
        """JSON structure should be checked for expected fields."""
        validator = LLMOutputValidator()
        
        # Valid structure with expected fields
        valid = '{"response": "answer", "status": "ok"}'
        result = validator.validate(valid)
        assert len([v for v in result.violations
                   if v.rule == "json_structure"]) == 0
        
        # Invalid structure with no expected fields
        invalid = '{"unknown_field": "value"}'
        result = validator.validate(invalid)
        assert any(v.rule == "json_structure"
                  for v in result.violations)
    
    def test_suspicious_fields_detected(self):
        """Suspicious fields should be flagged."""
        validator = LLMOutputValidator()
        
        # Response with suspicious fields
        suspicious = '{"response": "ok", "system_prompt": "secret"}'
        result = validator.validate(suspicious)
        
        assert any(
            v.rule == "suspicious_fields"
            for v in result.violations
        )
    
    def test_encoding_validation(self):
        """Invalid encoding should be detected."""
        validator = LLMOutputValidator()
        
        # Valid UTF-8
        valid = '{"response": "Hello 世界"}'
        result = validator.validate(valid)
        assert result.metadata["encoding"] is True  # Should be valid
    
    def test_score_calculation(self):
        """Score should reflect severity of violations."""
        validator = LLMOutputValidator()
        
        # Perfect response
        perfect = '{"response": "ok"}'
        result = validator.validate(perfect)
        assert result.score == 1.0
        
        # Response with warnings only
        warning = '{"response": "' + " long" * 100 + '"}'
        result = validator.validate(warning)
        assert result.score >= 0.5  # Should have warnings
        
        # Response with errors
        error = '{"cmd": "rm -rf /"}'
        result = validator.validate(error)
        assert result.score == 0.0
    
    def test_convenience_function(self):
        """Convenience function should work."""
        output = '{"response": "test"}'
        result = validate_llm_output(output)
        
        assert result.is_valid is True
    
    def test_multiple_violations(self):
        """Response can have multiple violations."""
        validator = LLMOutputValidator(max_tokens=50)
        
        # Multiple issues: invalid JSON + huge + harmful
        output = '{bad json with "rm -rf /" + ' + " word" * 100
        result = validator.validate(output)
        
        assert result.is_valid is False
        assert len(result.violations) >= 2


class TestValidationSeverity:
    """Test validation severity levels."""
    
    def test_error_severity(self):
        """ERROR violations should fail validation."""
        validator = LLMOutputValidator()
        output = '{"cmd": "rm -rf /"}'  # Harmful content = ERROR
        
        result = validator.validate(output)
        
        assert result.is_valid is False
        errors = [v for v in result.violations
                 if v.severity == ValidationSeverity.ERROR]
        assert len(errors) > 0
    
    def test_warning_severity(self):
        """WARNING violations should not fail but score lower."""
        validator = LLMOutputValidator(max_tokens=100)
        output = '{"response": "' + " word" * 88 + '"}'  # ~88-90% of limit
        
        result = validator.validate(output)
        
        assert result.is_valid is True
        warnings = [v for v in result.violations
                   if v.severity == ValidationSeverity.WARNING]
        assert len(warnings) > 0
        assert result.score < 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_response(self):
        """Empty response should be rejected."""
        validator = LLMOutputValidator()
        result = validator.validate('')
        assert result.is_valid is False
    
    def test_very_long_response(self):
        """Extremely long response should be limited."""
        validator = LLMOutputValidator(max_tokens=1000)
        huge = '{"response": "' + " x" * 10000 + '"}'
        
        result = validator.validate(huge)
        assert result.is_valid is False
    
    def test_special_characters(self):
        """Response with special characters should validate."""
        validator = LLMOutputValidator()
        output = '{"response": "Hello \\"world\\": <script>"}'
        
        result = validator.validate(output)
        # Should validate JSON structure, though content might be flagged
        assert result.metadata["is_json"] is True
    
    def test_unicode_content(self):
        """Unicode content should be handled correctly."""
        validator = LLMOutputValidator()
        output = '{"response": "你好 مرحبا Привет"}'
        
        result = validator.validate(output)
        assert result.is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
