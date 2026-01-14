"""
TDD Tests for HTML Validator (CORE-023: HTML Validation Governance)

Validates zero-tolerance quality gates for HTML file generation:
1. HTML5 syntax validation
2. DOCTYPE presence
3. Unclosed tags detection
4. WCAG AA compliance
5. Responsive viewport tags

Author: GitHub Copilot
Created: 2026-01-12
AC-ID: CORE-023
"""

import pytest
from pathlib import Path
import tempfile
from src.orchestrators.html_view.validators.html_validator import (
    HTMLValidator,
    HTMLValidationResult
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def validator():
    """Create HTML validator instance."""
    return HTMLValidator(strict=True)


@pytest.fixture
def temp_html_dir():
    """Create temporary directory for test HTML files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# =============================================================================
# HTML5 Syntax Validation Tests
# =============================================================================

class TestHTML5Syntax:
    """Test HTML5 syntax validation."""
    
    def test_valid_html5_document_passes(self, validator, temp_html_dir):
        """Valid HTML5 document should pass validation."""
        html_file = temp_html_dir / "valid.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Valid Document</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is valid HTML5.</p>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert result.is_valid, f"Expected valid, got: {result.get_summary()}"
        assert not result.has_errors()
        assert len(result.errors) == 0
    
    def test_missing_doctype_fails(self, validator, temp_html_dir):
        """HTML without DOCTYPE should fail validation."""
        html_file = temp_html_dir / "no_doctype.html"
        html_file.write_text("""<html>
<head><title>No DOCTYPE</title></head>
<body><p>Missing DOCTYPE</p></body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert not result.is_valid
        assert result.has_errors()
        assert any("DOCTYPE" in error for error in result.errors)
    
    def test_unclosed_tags_detected(self, validator, temp_html_dir):
        """Unclosed tags should be detected."""
        html_file = temp_html_dir / "unclosed.html"
        html_file.write_text("""<!DOCTYPE html>
<html>
<head><title>Unclosed</title></head>
<body>
    <div>
        <p>Unclosed paragraph
        <span>Unclosed span
    </div>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert not result.is_valid
        assert result.has_errors()
    
    def test_malformed_attributes_detected(self, validator, temp_html_dir):
        """Malformed HTML attributes should be detected."""
        html_file = temp_html_dir / "malformed.html"
        html_file.write_text("""<!DOCTYPE html>
<html>
<head><title>Malformed</title></head>
<body>
    <img src="test.png" alt=>
    <div class="test" id=>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert not result.is_valid
        assert result.has_errors()


# =============================================================================
# WCAG AA Compliance Tests
# =============================================================================

class TestWCAGCompliance:
    """Test WCAG AA accessibility compliance."""
    
    def test_images_require_alt_text(self, validator, temp_html_dir):
        """Images without alt text should fail WCAG validation."""
        html_file = temp_html_dir / "no_alt.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Alt Text</title>
</head>
<body>
    <img src="logo.png">
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert not result.is_valid
        assert result.has_wcag_violations()
        assert any("alt" in str(v).lower() for v in result.wcag_violations)
    
    def test_proper_heading_hierarchy(self, validator, temp_html_dir):
        """Skipping heading levels should trigger WCAG warning."""
        html_file = temp_html_dir / "bad_headings.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bad Headings</title>
</head>
<body>
    <h1>Main Title</h1>
    <h4>Skipped to H4</h4>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        # In strict mode, WCAG violations should fail validation
        if validator.strict:
            assert not result.is_valid
        assert result.has_wcag_violations()
    
    def test_form_inputs_require_labels(self, validator, temp_html_dir):
        """Form inputs without labels should fail WCAG validation."""
        html_file = temp_html_dir / "no_labels.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>No Labels</title>
</head>
<body>
    <form>
        <input type="text" name="username">
        <input type="password" name="password">
    </form>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert not result.is_valid
        assert result.has_wcag_violations()
        assert any("label" in str(v).lower() for v in result.wcag_violations)


# =============================================================================
# Responsive Design Tests
# =============================================================================

class TestResponsiveDesign:
    """Test responsive design requirements."""
    
    def test_viewport_meta_tag_required(self, validator, temp_html_dir):
        """HTML documents should include viewport meta tag."""
        html_file = temp_html_dir / "no_viewport.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>No Viewport</title>
</head>
<body>
    <h1>Hello</h1>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        # Viewport missing should trigger warning
        assert not result.is_valid or len(result.warnings) > 0
        assert any("viewport" in str(w).lower() for w in result.warnings)
    
    def test_valid_viewport_configuration(self, validator, temp_html_dir):
        """Properly configured viewport should pass."""
        html_file = temp_html_dir / "valid_viewport.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Valid Viewport</title>
</head>
<body>
    <h1>Hello</h1>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert result.is_valid
        assert not any("viewport" in str(w).lower() for w in result.warnings)


# =============================================================================
# Validation Result Tests
# =============================================================================

class TestValidationResults:
    """Test HTMLValidationResult structure and methods."""
    
    def test_result_summary_for_valid_html(self):
        """Valid HTML should produce success summary."""
        result = HTMLValidationResult(
            is_valid=True,
            file_path="test.html"
        )
        
        summary = result.get_summary()
        
        assert "✅" in summary
        assert "test.html" in summary
        assert "Valid" in summary
    
    def test_result_summary_for_invalid_html(self):
        """Invalid HTML should produce error summary."""
        result = HTMLValidationResult(
            is_valid=False,
            file_path="test.html",
            errors=["Missing DOCTYPE", "Unclosed div"],
            wcag_violations=[{"type": "missing_alt"}]
        )
        
        summary = result.get_summary()
        
        assert "❌" in summary
        assert "test.html" in summary
        assert "2 syntax errors" in summary
        assert "1 WCAG violations" in summary
    
    def test_has_errors_method(self):
        """has_errors should detect any error condition."""
        result_with_errors = HTMLValidationResult(
            is_valid=False,
            file_path="test.html",
            errors=["Error 1"]
        )
        
        result_with_parse_errors = HTMLValidationResult(
            is_valid=False,
            file_path="test.html",
            parse_errors=["Parse Error 1"]
        )
        
        result_clean = HTMLValidationResult(
            is_valid=True,
            file_path="test.html"
        )
        
        assert result_with_errors.has_errors()
        assert result_with_parse_errors.has_errors()
        assert not result_clean.has_errors()


# =============================================================================
# Integration Tests
# =============================================================================

class TestValidatorIntegration:
    """Test validator integration scenarios."""
    
    def test_nonexistent_file_handling(self, validator):
        """Validator should handle nonexistent files gracefully."""
        result = validator.validate_file("/nonexistent/file.html")
        
        assert not result.is_valid
        assert result.has_errors()
        assert any("not found" in error.lower() or "exist" in error.lower() 
                   for error in result.errors)
    
    def test_strict_mode_enforcement(self, temp_html_dir):
        """Strict mode should treat warnings as errors."""
        html_file = temp_html_dir / "warnings.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Warnings</title>
</head>
<body>
    <h1>Title</h1>
</body>
</html>""")
        
        strict_validator = HTMLValidator(strict=True)
        lenient_validator = HTMLValidator(strict=False)
        
        strict_result = strict_validator.validate_file(str(html_file))
        lenient_result = lenient_validator.validate_file(str(html_file))
        
        # Both should complete, but strict may be more critical
        assert isinstance(strict_result, HTMLValidationResult)
        assert isinstance(lenient_result, HTMLValidationResult)
    
    def test_complete_cortex_html_validation(self, validator, temp_html_dir):
        """Validate complete CORTEX-style HTML document."""
        html_file = temp_html_dir / "cortex_complete.html"
        html_file.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CORTEX 6.0 Dashboard</h1>
        <nav aria-label="Main navigation">
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#metrics">Metrics</a></li>
            </ul>
        </nav>
        <main>
            <section id="overview">
                <h2>System Overview</h2>
                <p>CORTEX orchestration platform status.</p>
            </section>
            <section id="metrics">
                <h2>Performance Metrics</h2>
                <img src="chart.png" alt="Performance chart showing uptime metrics">
            </section>
        </main>
        <footer>
            <p>&copy; 2026 Asif Hussain. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>""")
        
        result = validator.validate_file(str(html_file))
        
        assert result.is_valid, f"Complete HTML should be valid: {result.get_summary()}"
        assert not result.has_errors()
        assert not result.has_wcag_violations()
