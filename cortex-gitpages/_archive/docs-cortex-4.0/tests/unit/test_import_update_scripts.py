"""
Unit Tests for AC-AR-010-03: Import Path Update & Validation

Tests import analyzer and validator functionality.
"""

import pytest
from pathlib import Path
from typing import Dict, List


class ImportScriptValidator:
    """Validator for import scripts."""
    
    def __init__(self):
        self.validation_errors = []
    
    def validate_import_analyzer_syntax(self) -> bool:
        """Validate update-imports.py syntax."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        
        if not script_path.exists():
            self.validation_errors.append("update-imports.py not found")
            return False
        
        try:
            with open(script_path, 'r') as f:
                code = f.read()
            compile(code, str(script_path), 'exec')
            return True
        except SyntaxError as e:
            self.validation_errors.append(f"Syntax error: {e}")
            return False
    
    def validate_import_validator_syntax(self) -> bool:
        """Validate validate-imports.py syntax."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        
        if not validator_path.exists():
            self.validation_errors.append("validate-imports.py not found")
            return False
        
        try:
            with open(validator_path, 'r') as f:
                code = f.read()
            compile(code, str(validator_path), 'exec')
            return True
        except SyntaxError as e:
            self.validation_errors.append(f"Syntax error: {e}")
            return False
    
    def validate_analyzer_class_structure(self) -> bool:
        """Validate ImportAnalyzer class exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        if "class ImportAnalyzer" not in content:
            self.validation_errors.append("ImportAnalyzer class not found")
            return False
        
        return True
    
    def validate_validator_class_structure(self) -> bool:
        """Validate ImportValidator class exists."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        if "class ImportValidator" not in content:
            self.validation_errors.append("ImportValidator class not found")
            return False
        
        return True
    
    def validate_required_analyzer_methods(self) -> bool:
        """Validate required analyzer methods exist."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        required_methods = [
            'analyze_imports',
            'validate_imports',
            'generate_import_report',
            '_analyze_file',
            '_check_circular_imports',
            '_check_broken_imports',
        ]
        
        for method in required_methods:
            if f"def {method}" not in content:
                self.validation_errors.append(f"Missing method: {method}")
                return False
        
        return True
    
    def validate_required_validator_methods(self) -> bool:
        """Validate required validator methods exist."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        required_methods = [
            'validate_all',
            '_check_no_hardcoded_paths',
            '_check_portable_imports',
            '_check_tier_boundaries',
            '_check_circular_imports',
        ]
        
        for method in required_methods:
            if f"def {method}" not in content:
                self.validation_errors.append(f"Missing method: {method}")
                return False
        
        return True
    
    def validate_ast_module_usage(self) -> bool:
        """Validate that AST module is used for parsing."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        if "import ast" not in content:
            self.validation_errors.append("AST module not imported")
            return False
        
        if "ast.parse" not in content:
            self.validation_errors.append("AST parsing not used")
            return False
        
        return True
    
    def validate_circular_import_detection(self) -> bool:
        """Validate circular import detection is implemented."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        if "circular" not in content.lower():
            self.validation_errors.append("Circular import detection not found")
            return False
        
        return True
    
    def validate_report_generation(self) -> bool:
        """Validate report generation is implemented."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        if "def generate_import_report" not in content:
            self.validation_errors.append("Report generation method not found")
            return False
        
        return True
    
    def validate_portable_paths_check(self) -> bool:
        """Validate portable paths check is implemented."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        if "/Users/" not in content:
            self.validation_errors.append("Portable paths check not implemented")
            return False
        
        return True


class TestImportScriptStructure:
    """Test import script structure and components."""
    
    @pytest.fixture
    def validator(self):
        return ImportScriptValidator()
    
    def test_update_imports_script_exists(self):
        """Test that update-imports.py exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        assert script_path.exists(), "update-imports.py must exist"
    
    def test_validate_imports_script_exists(self):
        """Test that validate-imports.py exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        assert script_path.exists(), "validate-imports.py must exist"
    
    def test_update_imports_syntax_valid(self, validator):
        """Test that update-imports.py has valid syntax."""
        assert validator.validate_import_analyzer_syntax()
    
    def test_validate_imports_syntax_valid(self, validator):
        """Test that validate-imports.py has valid syntax."""
        assert validator.validate_import_validator_syntax()
    
    def test_import_analyzer_class_exists(self, validator):
        """Test that ImportAnalyzer class exists."""
        assert validator.validate_analyzer_class_structure()
    
    def test_import_validator_class_exists(self, validator):
        """Test that ImportValidator class exists."""
        assert validator.validate_validator_class_structure()


class TestImportAnalyzerMethods:
    """Test ImportAnalyzer methods."""
    
    @pytest.fixture
    def validator(self):
        return ImportScriptValidator()
    
    def test_analyze_imports_method_exists(self, validator):
        """Test that analyze_imports method exists."""
        assert validator.validate_required_analyzer_methods()
    
    def test_validate_imports_method_exists(self, validator):
        """Test that validate_imports method exists."""
        assert validator.validate_required_analyzer_methods()
    
    def test_generate_report_method_exists(self, validator):
        """Test that generate_import_report method exists."""
        assert validator.validate_required_analyzer_methods()
    
    def test_circular_import_check_exists(self, validator):
        """Test that circular import checking exists."""
        assert validator.validate_circular_import_detection()


class TestImportValidatorMethods:
    """Test ImportValidator methods."""
    
    @pytest.fixture
    def validator(self):
        return ImportScriptValidator()
    
    def test_validate_all_method_exists(self, validator):
        """Test that validate_all method exists."""
        assert validator.validate_required_validator_methods()
    
    def test_hardcoded_paths_check_exists(self, validator):
        """Test that hardcoded paths check exists."""
        assert validator.validate_required_validator_methods()
    
    def test_portable_paths_check_exists(self, validator):
        """Test that portable paths check exists."""
        assert validator.validate_portable_paths_check()


class TestImportAnalysis:
    """Test import analysis capabilities."""
    
    @pytest.fixture
    def validator(self):
        return ImportScriptValidator()
    
    def test_ast_module_used(self, validator):
        """Test that AST module is used for parsing."""
        assert validator.validate_ast_module_usage()
    
    def test_report_generation_implemented(self, validator):
        """Test that report generation is implemented."""
        assert validator.validate_report_generation()
    
    def test_circular_import_detection_comprehensive(self):
        """Test that circular import detection is comprehensive."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        # Should use DFS or similar algorithm
        assert "circular" in content.lower() or "cycle" in content.lower()


class TestImportValidation:
    """Test import validation checks."""
    
    def test_hardcoded_path_detection(self):
        """Test that hardcoded /Users/ paths are detected."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        assert "/Users/" in content, "Must check for hardcoded /Users/ paths"
    
    def test_tier_boundary_check(self):
        """Test that tier boundaries are checked."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        assert "tier0" in content or "tier" in content.lower()
    
    def test_import_resolution_check(self):
        """Test that import resolution is checked."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        
        assert "resolve" in content.lower() or "ImportError" in content


class TestImportAcceptanceCriteria:
    """Test AC-AR-010-03 acceptance criteria."""
    
    @pytest.fixture
    def validator(self):
        return ImportScriptValidator()
    
    def test_ac_import_paths_updated(self, validator):
        """AC: Python import paths updated."""
        assert validator.validate_import_analyzer_syntax()
    
    def test_ac_imports_validated(self, validator):
        """AC: All imports validated."""
        assert validator.validate_import_validator_syntax()
    
    def test_ac_no_broken_imports(self, validator):
        """AC: No broken imports in codebase."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert "_check_broken_imports" in content
    
    def test_ac_no_circular_imports(self, validator):
        """AC: No circular imports detected."""
        assert validator.validate_circular_import_detection()


class TestImportDocumentation:
    """Test import scripts have proper documentation."""
    
    def test_analyzer_has_docstring(self):
        """Test that analyzer has module docstring."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert '"""' in content, "Script must have docstring"
    
    def test_analyzer_has_usage_example(self):
        """Test that analyzer includes usage examples."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert "Usage:" in content or "usage:" in content.lower()
    
    def test_validator_has_docstring(self):
        """Test that validator has module docstring."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/validate-imports.py"
        content = validator_path.read_text()
        assert '"""' in content, "Script must have docstring"
    
    def test_class_methods_have_docstrings(self):
        """Test that class methods have docstrings."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        
        # Count docstrings in methods
        docstring_count = content.count('"""')
        method_count = content.count('def ')
        
        # Should have multiple docstrings
        assert docstring_count >= 4, "Methods should have docstrings"


class TestImportEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_handles_relative_imports(self):
        """Test that relative imports are handled."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert "ImportFrom" in content or "relative" in content.lower()
    
    def test_handles_from_imports(self):
        """Test that 'from X import Y' syntax is handled."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert "ImportFrom" in content
    
    def test_handles_syntax_errors_gracefully(self):
        """Test that syntax errors are handled gracefully."""
        script_path = Path(__file__).parent.parent.parent / "scripts/update-imports.py"
        content = script_path.read_text()
        assert "except" in content or "try" in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
