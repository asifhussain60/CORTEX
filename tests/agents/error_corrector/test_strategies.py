"""Tests for ErrorCorrector strategies."""

import pytest
from pathlib import Path
import tempfile
from CORTEX.src.cortex_agents.error_corrector.strategies import (
    IndentationFixStrategy,
    ImportFixStrategy,
    SyntaxFixStrategy,
    PackageFixStrategy
)


class TestIndentationFixStrategy:
    """Tests for indentation fix strategy."""
    
    def test_can_fix_indentation_error(self):
        strategy = IndentationFixStrategy()
        parsed_error = {"category": "indentation"}
        fix_pattern = {"action": "normalize_indentation", "params": {"spaces": 4}}
        assert strategy.can_fix(parsed_error, fix_pattern) is True
    
    def test_fix_indentation(self):
        strategy = IndentationFixStrategy()
        
        # Create temp file with tabs
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n\tprint('hello')\n\tprint('world')")
            temp_path = f.name
        
        try:
            parsed_error = {"category": "indentation"}
            fix_pattern = {"action": "normalize_indentation", "params": {"spaces": 4}}
            result = strategy.apply_fix(parsed_error, fix_pattern, temp_path)
            
            assert result["success"] is True
            assert "Normalized indentation" in result["message"]
            assert "fixed_content" in result
            assert "\t" not in result["fixed_content"]
        finally:
            Path(temp_path).unlink()


class TestImportFixStrategy:
    """Tests for import fix strategy."""
    
    def test_can_fix_import_error(self):
        strategy = ImportFixStrategy()
        parsed_error = {"category": "import"}
        fix_pattern = {"action": "add_import"}
        assert strategy.can_fix(parsed_error, fix_pattern) is True
    
    def test_add_known_import(self):
        strategy = ImportFixStrategy()
        parsed_error = {"undefined_name": "Path"}
        fix_pattern = {"action": "add_import", "params": {}}
        result = strategy.apply_fix(parsed_error, fix_pattern, None)
        
        assert result["success"] is True
        assert "from pathlib import Path" in result["import_statement"]
    
    def test_add_unknown_import(self):
        strategy = ImportFixStrategy()
        parsed_error = {"undefined_name": "MyClass"}
        fix_pattern = {"action": "add_import", "params": {}}
        result = strategy.apply_fix(parsed_error, fix_pattern, None)
        
        assert result["success"] is True
        assert "import MyClass" in result["import_statement"]
    
    def test_remove_unused_import(self):
        strategy = ImportFixStrategy()
        parsed_error = {"line": 5}
        fix_pattern = {"action": "remove_import", "params": {}}
        result = strategy.apply_fix(parsed_error, fix_pattern, "test.py")
        
        assert result["success"] is True
        assert "Remove unused import" in result["message"]
        assert result["line_to_remove"] == 5


class TestSyntaxFixStrategy:
    """Tests for syntax fix strategy."""
    
    def test_can_fix_syntax_error(self):
        strategy = SyntaxFixStrategy()
        parsed_error = {"category": "invalid_syntax"}
        fix_pattern = {"action": "fix_syntax"}
        assert strategy.can_fix(parsed_error, fix_pattern) is True
    
    def test_fix_missing_colon(self):
        strategy = SyntaxFixStrategy()
        
        # Create temp file with missing colon
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test()\n    print('hello')")
            temp_path = f.name
        
        try:
            parsed_error = {"line": 1}
            fix_pattern = {"action": "fix_syntax", "params": {}}
            result = strategy.apply_fix(parsed_error, fix_pattern, temp_path)
            
            assert result["success"] is True
            assert "missing colon" in result["message"].lower()
            assert result["fixed_line"].endswith(':')
        finally:
            Path(temp_path).unlink()


class TestPackageFixStrategy:
    """Tests for package fix strategy."""
    
    def test_can_fix_package_error(self):
        strategy = PackageFixStrategy()
        parsed_error = {"missing_module": "requests"}
        fix_pattern = {"action": "install_package"}
        assert strategy.can_fix(parsed_error, fix_pattern) is True
    
    def test_suggest_package_install(self):
        strategy = PackageFixStrategy()
        parsed_error = {"missing_module": "requests"}
        fix_pattern = {"action": "install_package", "params": {}}
        result = strategy.apply_fix(parsed_error, fix_pattern, None)
        
        assert result["success"] is True
        assert "Install missing package" in result["message"]
        assert "pip install requests" in result["command"]
    
    def test_suggest_package_from_pattern(self):
        strategy = PackageFixStrategy()
        parsed_error = {}
        fix_pattern = {"action": "install_package", "params": {"package": "numpy"}}
        result = strategy.apply_fix(parsed_error, fix_pattern, None)
        
        assert result["success"] is True
        assert "numpy" in result["command"]
