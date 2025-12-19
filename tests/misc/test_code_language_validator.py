"""
Tests for Code Language Validator (Task 3.3)
TDD RED Phase: Write failing tests first
"""
import pytest
from src.validators.code_language_validator import CodeLanguageValidator, ValidationResult


class TestCodeLanguageValidator:
    """Test suite for code language validation in templates"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return CodeLanguageValidator()
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator is not None
        assert hasattr(validator, 'validate_code_block')
    
    def test_validate_english_code_passes(self, validator):
        """Test that English code and comments pass validation"""
        code = """
def calculate_sum(numbers):
    # Calculate the sum of numbers
    total = 0
    for num in numbers:
        total += num
    return total
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is True
        assert len(result.violations) == 0
    
    def test_validate_spanish_comment_fails(self, validator):
        """Test that Spanish comments are detected and flagged"""
        code = """
def calcular_suma(numeros):
    # Calcular la suma de los números
    total = 0
    return total
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        assert len(result.violations) > 0
        assert any('Spanish' in v.language for v in result.violations)
    
    def test_validate_french_comment_fails(self, validator):
        """Test that French comments are detected"""
        code = """
def calculer_somme(nombres):
    # Calculer la somme des nombres
    return sum(nombres)
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        assert any('French' in v.language for v in result.violations)
    
    def test_validate_chinese_comment_fails(self, validator):
        """Test that Chinese comments are detected"""
        code = """
def calculate_sum(numbers):
    # 计算数字总和
    return sum(numbers)
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        assert any('Chinese' in v.language or 'non-English' in v.language.lower() for v in result.violations)
    
    def test_validate_mixed_language_comments_fails(self, validator):
        """Test that mixed language comments are detected"""
        code = """
def process_data(data):
    # Process the data - Procesar los datos
    result = []
    # Return the results - Devolver los resultados
    return result
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        assert len(result.violations) > 0
    
    def test_validate_javascript_english_passes(self, validator):
        """Test JavaScript code with English comments passes"""
        code = """
function calculateTotal(items) {
    // Calculate the total price
    let total = 0;
    items.forEach(item => {
        total += item.price;
    });
    return total;
}
"""
        result = validator.validate_code_block(code, language='javascript')
        assert result.is_valid is True
    
    def test_validate_variable_names_english_only(self, validator):
        """Test that non-English variable names are flagged"""
        code = """
def proceso_datos(datos):
    resultado = []
    return resultado
"""
        result = validator.validate_code_block(code, language='python', strict_mode=True)
        assert result.is_valid is False
        # Should detect Spanish variable names in strict mode
    
    def test_validate_empty_code_passes(self, validator):
        """Test that empty code blocks pass validation"""
        code = ""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is True
    
    def test_validate_code_without_comments_passes(self, validator):
        """Test that code without comments passes if identifiers are English"""
        code = """
def calculate(x, y):
    return x + y
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is True
    
    def test_violation_includes_line_number(self, validator):
        """Test that violations include line numbers"""
        code = """
def test():
    # Esto es un comentario en español
    pass
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        assert len(result.violations) > 0
        violation = result.violations[0]
        assert hasattr(violation, 'line_number')
        assert violation.line_number > 0
    
    def test_violation_includes_snippet(self, validator):
        """Test that violations include code snippet"""
        code = """
def test():
    # Comentario en español
    pass
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is False
        violation = result.violations[0]
        assert hasattr(violation, 'snippet')
        assert len(violation.snippet) > 0
    
    def test_validate_template_with_code_blocks(self, validator):
        """Test validating entire template with embedded code blocks"""
        template = """
# Help Template

Here's an example:

```python
def greet(name):
    # Saludo en español
    return f"Hola {name}"
```

More text here.
"""
        result = validator.validate_template(template)
        assert result.is_valid is False
        assert len(result.violations) > 0
    
    def test_validate_template_multiple_code_blocks(self, validator):
        """Test template with multiple code blocks"""
        template = """
Example 1:
```python
# English comment
def test1():
    pass
```

Example 2:
```javascript
// Comentario en español
function test2() {}
```
"""
        result = validator.validate_template(template)
        assert result.is_valid is False
        # Should find violation in second code block
    
    def test_get_supported_code_languages(self, validator):
        """Test retrieving supported code languages"""
        languages = validator.get_supported_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'java' in languages
        assert len(languages) > 0
    
    def test_strict_mode_more_restrictive(self, validator):
        """Test that strict mode catches more violations"""
        code = """
def calcular(valor):  # Spanish function name, English comment
    # Calculate the value
    return valor * 2
"""
        # Normal mode might pass (English comment)
        result_normal = validator.validate_code_block(code, language='python', strict_mode=False)
        
        # Strict mode should fail (Spanish identifiers)
        result_strict = validator.validate_code_block(code, language='python', strict_mode=True)
        
        # Strict mode should be more restrictive
        assert result_strict.is_valid is False or result_strict.violation_count >= result_normal.violation_count
    
    def test_validation_result_has_summary(self, validator):
        """Test that validation result includes summary"""
        code = """
def test():
    # Comment uno
    # Comment dos
    pass
"""
        result = validator.validate_code_block(code, language='python')
        assert hasattr(result, 'violation_count')
        assert hasattr(result, 'summary')
        if not result.is_valid:
            assert result.violation_count == len(result.violations)
    
    def test_detect_common_non_english_keywords(self, validator):
        """Test detection of common non-English keywords/phrases"""
        test_cases = [
            ("# TODO: hacer esto", False),  # Spanish
            ("# FIXME: corriger cela", False),  # French
            ("# NOTE: これを修正", False),  # Japanese
            ("# TODO: fix this", True),  # English
            ("# FIXME: correct this", True),  # English
        ]
        
        for comment, should_pass in test_cases:
            code = f"def test():\n    {comment}\n    pass"
            result = validator.validate_code_block(code, language='python')
            if should_pass:
                assert result.is_valid is True, f"Expected '{comment}' to pass"
            else:
                assert result.is_valid is False, f"Expected '{comment}' to fail"
    
    def test_ignore_code_keywords(self, validator):
        """Test that code keywords are not flagged as non-English"""
        code = """
def test():
    # Use del to delete items
    items = [1, 2, 3]
    del items[0]
    return items
"""
        result = validator.validate_code_block(code, language='python')
        assert result.is_valid is True
        # 'del' is a Python keyword, not Spanish


class TestCodeLanguageValidatorIntegration:
    """Integration tests for validator with multilingual templates"""
    
    def test_validate_multilingual_template_file(self):
        """Test validating entire multilingual template YAML file"""
        from pathlib import Path
        
        validator = CodeLanguageValidator()
        template_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/multilingual-templates.yaml")
        
        if template_path.exists():
            result = validator.validate_template_file(str(template_path))
            
            # All code blocks in multilingual templates should use English
            assert result.is_valid is True or len(result.violations) == 0, \
                f"Found {len(result.violations)} code language violations in multilingual templates"
    
    def test_validate_response_templates_file(self):
        """Test validating response-templates.yaml file"""
        from pathlib import Path
        
        validator = CodeLanguageValidator()
        template_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/response-templates.yaml")
        
        if template_path.exists():
            result = validator.validate_template_file(str(template_path))
            
            # Response templates should have English code
            assert result.is_valid is True or result.violation_count < 5, \
                "Too many code language violations in response templates"
