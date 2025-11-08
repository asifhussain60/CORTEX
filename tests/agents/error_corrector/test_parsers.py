"""Tests for ErrorCorrector parsers."""

import pytest
from CORTEX.src.cortex_agents.error_corrector.parsers import (
    PytestErrorParser,
    SyntaxErrorParser,
    ImportErrorParser,
    RuntimeErrorParser,
    LinterErrorParser
)


class TestPytestErrorParser:
    """Tests for pytest error parser."""
    
    def test_can_parse_pytest_error(self):
        parser = PytestErrorParser()
        output = "test_file.py::test_function FAILED"
        assert parser.can_parse(output) is True
    
    def test_parse_pytest_assertion_error(self):
        parser = PytestErrorParser()
        output = """
        test_file.py::test_addition FAILED
        test_file.py:10: AssertionError
        assert 2 + 2 == 5
        """
        result = parser.parse(output)
        assert result["file"] == "test_file.py"
        assert result["line"] == 10
        assert result["category"] == "assertion"
        assert "assert 2 + 2 == 5" in result["code_snippet"]
    
    def test_parse_pytest_with_test_name(self):
        parser = PytestErrorParser()
        output = "tests/test_module.py::test_my_function FAILED"
        result = parser.parse(output)
        assert result["file"] == "tests/test_module.py"
        assert result["test_name"] == "test_my_function"


class TestSyntaxErrorParser:
    """Tests for syntax error parser."""
    
    def test_can_parse_syntax_error(self):
        parser = SyntaxErrorParser()
        output = 'File "script.py", line 5\n  SyntaxError: invalid syntax'
        assert parser.can_parse(output) is True
    
    def test_parse_indentation_error(self):
        parser = SyntaxErrorParser()
        output = '''
        File "myfile.py", line 12
            print("hello")
        IndentationError: unexpected indent
        '''
        result = parser.parse(output)
        assert result["file"] == "myfile.py"
        assert result["line"] == 12
        assert result["category"] == "indentation"
    
    def test_parse_invalid_syntax(self):
        parser = SyntaxErrorParser()
        output = '''
        File "test.py", line 3
            if x == 5
                ^
        SyntaxError: invalid syntax
        '''
        result = parser.parse(output)
        assert result["file"] == "test.py"
        assert result["line"] == 3
        assert result["category"] == "invalid_syntax"


class TestImportErrorParser:
    """Tests for import error parser."""
    
    def test_can_parse_import_error(self):
        parser = ImportErrorParser()
        output = "ModuleNotFoundError: No module named 'requests'"
        assert parser.can_parse(output) is True
    
    def test_parse_module_not_found(self):
        parser = ImportErrorParser()
        output = '''
        File "app.py", line 5
        ModuleNotFoundError: No module named 'requests'
        '''
        result = parser.parse(output)
        assert result["missing_module"] == "requests"
        assert result["category"] == "import"
        assert result["file"] == "app.py"
        assert result["line"] == 5
    
    def test_parse_cannot_import_name(self):
        parser = ImportErrorParser()
        output = "ImportError: cannot import name 'MyClass' from 'mymodule'"
        result = parser.parse(output)
        assert result["missing_name"] == "MyClass"
        assert "Cannot import: MyClass" in result["message"]


class TestRuntimeErrorParser:
    """Tests for runtime error parser."""
    
    def test_can_parse_runtime_error(self):
        parser = RuntimeErrorParser()
        output = "Traceback (most recent call last):\nNameError: name 'x' is not defined"
        assert parser.can_parse(output) is True
    
    def test_parse_name_error(self):
        parser = RuntimeErrorParser()
        output = '''
        Traceback (most recent call last):
          File "script.py", line 10, in <module>
            print(undefined_var)
        NameError: name 'undefined_var' is not defined
        '''
        result = parser.parse(output)
        assert result["category"] == "name"
        assert result["undefined_name"] == "undefined_var"
        assert result["file"] == "script.py"
        assert result["line"] == 10
    
    def test_parse_attribute_error(self):
        parser = RuntimeErrorParser()
        output = '''
        Traceback (most recent call last):
          File "test.py", line 15
        AttributeError: 'str' object has no attribute 'missing_attr'
        '''
        result = parser.parse(output)
        assert result["category"] == "attribute"
        assert result["missing_attribute"] == "missing_attr"


class TestLinterErrorParser:
    """Tests for linter error parser."""
    
    def test_can_parse_linter_error(self):
        parser = LinterErrorParser()
        output = "myfile.py:10:5: F821 undefined name 'x'"
        assert parser.can_parse(output) is True
    
    def test_parse_undefined_name(self):
        parser = LinterErrorParser()
        output = "app.py:25:10: F821 undefined name 'logger'"
        result = parser.parse(output)
        assert result["file"] == "app.py"
        assert result["line"] == 25
        assert result["column"] == 10
        assert result["code"] == "F821"
        assert result["category"] == "undefined_name"
    
    def test_parse_unused_import(self):
        parser = LinterErrorParser()
        output = "utils.py:3:1: F401 'json' imported but unused"
        result = parser.parse(output)
        assert result["file"] == "utils.py"
        assert result["line"] == 3
        assert result["category"] == "unused_import"
