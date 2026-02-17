"""
Test CORE-002 Response Validator

Authority: CORE-002-RESPONSE
Phase: CORTEX Inline-First Architecture
"""

import pytest
from cortex.governance.response_validator import (
    ResponseValidator,
    validate_response,
    transform_response,
)


class TestResponseValidator:
    """Test CORE-002 response validation."""
    
    def test_detects_create_file_md_violation(self):
        """Should detect create_file for .md files."""
        response = 'Run: create_file("report.md", content)'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert len(violations) > 0
        assert "create_file" in violations[0].lower()
    
    def test_detects_create_file_txt_violation(self):
        """Should detect create_file for .txt files."""
        response = 'Execute: create_file("output.txt", data)'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert len(violations) > 0
    
    def test_detects_cat_redirect_violation(self):
        """Should detect cat > file.md patterns."""
        response = 'Run in terminal: cat > report.md'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert "Shell redirection" in violations[0]
    
    def test_detects_comprehensive_report_violation(self):
        """Should detect 'create comprehensive report' patterns."""
        response = 'Let me create a comprehensive report: report.md'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert len(violations) > 0
    
    def test_detects_created_file_confirmation(self):
        """Should detect 'Created [file]' confirmations."""
        response = 'Created [](file:///path/HEALTH_REPORT.txt)'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert "File creation confirmation" in violations[0]
    
    def test_allows_github_prompts_path(self):
        """Should allow .github/prompts/*.md files."""
        response = 'Update file: .github/prompts/cortex-architect.prompt.md'
        is_valid, violations = validate_response(response)
        
        assert is_valid
        assert len(violations) == 0
    
    def test_allows_github_agents_path(self):
        """Should allow .github/agents/*.md files."""
        response = 'Update agent spec: .github/agents/core/CORTEX.md'
        is_valid, violations = validate_response(response)
        
        assert is_valid
        assert len(violations) == 0
    
    def test_allows_readme_md(self):
        """Should allow README.md."""
        response = 'Update README.md with new instructions'
        is_valid, violations = validate_response(response)
        
        assert is_valid
        assert len(violations) == 0
    
    def test_transforms_create_file_to_inline(self):
        """Should transform create_file to inline display."""
        response = 'Run: create_file("report.md", data)'
        transformed = transform_response(response)
        
        assert "create_file" not in transformed
        assert "inline" in transformed.lower()
        assert "CORE-002" in transformed
    
    def test_transforms_cat_redirect_to_inline(self):
        """Should transform cat > to inline display."""
        response = 'Execute: cat > output.txt'
        transformed = transform_response(response)
        
        assert "cat >" not in transformed
        assert "inline" in transformed.lower()
    
    def test_transforms_generate_report_to_inline(self):
        """Should transform 'generate report' to inline."""
        response = 'Generate comprehensive markdown report'
        transformed = transform_response(response)
        
        assert "generate" not in transformed.lower() or "markdown" not in transformed.lower()
        assert "inline" in transformed.lower()
    
    def test_enforce_with_auto_transform(self):
        """Should auto-transform when enforce called."""
        response = 'Create report.md file'
        result = ResponseValidator.enforce(response, auto_transform=True)
        
        assert not result["compliant"]
        assert len(result["violations"]) > 0
        assert "inline" in result["transformed_text"].lower()
        assert "Auto-transformed" in result["action"]
    
    def test_enforce_without_auto_transform(self):
        """Should not transform when auto_transform=False."""
        response = 'Create report.md file'
        result = ResponseValidator.enforce(response, auto_transform=False)
        
        assert not result["compliant"]
        assert result["transformed_text"] == response
        assert "no transformation" in result["action"].lower()
    
    def test_enforce_compliant_response(self):
        """Should pass compliant responses."""
        response = 'Display results inline using markdown table'
        result = ResponseValidator.enforce(response)
        
        assert result["compliant"]
        assert len(result["violations"]) == 0
        assert result["action"] == "No violations detected"
    
    def test_multiple_violations_detected(self):
        """Should detect multiple violations."""
        response = '''
        First, create report.md with: create_file("report.md", data)
        Then run: cat > summary.txt
        Finally generate comprehensive analysis
        '''
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert len(violations) >= 2  # At least 2 violations
    
    def test_case_insensitive_detection(self):
        """Should detect violations case-insensitively."""
        response = 'CREATE_FILE("REPORT.MD", data)'
        is_valid, violations = validate_response(response)
        
        assert not is_valid
        assert len(violations) > 0


# AC_START: test_response_validator_core_002
# Test validates CORE-002-RESPONSE enforcement
# Coverage: Detection, transformation, enforcement
# Expected: All tests pass, 100% violation detection
# AC_END
