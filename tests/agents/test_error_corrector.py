"""
Tests for ErrorCorrector Agent

Validates error parsing and automated fixing capabilities.
"""

import pytest
import tempfile
from pathlib import Path

from src.cortex_agents.error_corrector import ErrorCorrector
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType


class TestErrorCorrectorBasics:
    """Test basic ErrorCorrector functionality."""
    
    def test_initialization(self):
        """Test ErrorCorrector initializes correctly."""
        corrector = ErrorCorrector(name="TestCorrector")
        
        assert corrector.name == "TestCorrector"
        assert corrector.parsers is not None and len(corrector.parsers) > 0
        assert corrector.strategies is not None and len(corrector.strategies) > 0
        assert corrector.path_validator is not None
        assert len(corrector.path_validator.protected_paths) == 3
        assert "CORTEX/tests" in corrector.path_validator.protected_paths
    
    def test_can_handle_fix_intent(self):
        """Test can_handle responds to FIX intent."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={"error_output": "Some error"},
            user_message="Fix this error"
        )
        
        assert corrector.can_handle(request) is True
    
    def test_can_handle_debug_intent(self):
        """Test can_handle responds to DEBUG intent."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.DEBUG.value,
            context={"error_output": "Debug this"},
            user_message="Debug"
        )
        
        assert corrector.can_handle(request) is True
    
    def test_can_handle_error_output(self):
        """Test can_handle responds to error_output in context."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent="analyze",
            context={"error_output": "Traceback..."},
            user_message="What's wrong?"
        )
        
        assert corrector.can_handle(request) is True
    
    def test_cannot_handle_unrelated(self):
        """Test can_handle rejects unrelated intents."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan something"
        )
        
        assert corrector.can_handle(request) is False


class TestProtectedPaths:
    """Test protected path isolation."""
    
    def test_is_protected_cortex_tests(self):
        """Test CORTEX/tests is protected."""
        corrector = ErrorCorrector()
        
        # Create a temp file to simulate CORTEX/tests path
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_tests = Path(tmpdir) / "CORTEX" / "tests" / "test_something.py"
            cortex_tests.parent.mkdir(parents=True)
            cortex_tests.write_text("# test file")
            
            # Should be protected (comparing relative paths)
            # Note: _is_protected_path checks if file is under any protected directory
            assert corrector._is_protected_path("CORTEX/tests/test_file.py")
    
    def test_is_protected_cortex_agents(self):
        """Test CORTEX/src/cortex_agents is protected."""
        corrector = ErrorCorrector()
        
        assert corrector._is_protected_path("CORTEX/src/cortex_agents/base_agent.py")
    
    def test_is_not_protected_application_code(self):
        """Test application code is not protected."""
        corrector = ErrorCorrector()
        
        assert not corrector._is_protected_path("/tmp/app/src/main.py")
        assert not corrector._is_protected_path("app/tests/test_app.py")
    
    def test_rejects_protected_path_in_execute(self):
        """Test execute rejects auto-fixing protected paths."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={
                "error_output": "SyntaxError: invalid syntax in CORTEX/tests/test_agent.py",
                "file_path": "CORTEX/tests/test_agent.py"
            },
            user_message="Fix error"
        )
        
        response = corrector.execute(request)
        
        assert response.success is False
        assert "protected" in response.message.lower()
        assert response.result.get("error") == "protected_path"


class TestErrorParsing:
    """Test error parsing capabilities."""
    
    def test_parse_pytest_error(self):
        """Test parsing pytest assertion error."""
        corrector = ErrorCorrector()
        
        error_output = """
test_file.py::test_addition FAILED [100%]
============================== FAILURES ===============================
_________________________ test_addition __________________________
    def test_addition():
>       assert 1 + 1 == 3
E       assert 2 == 3

test_file.py:5: AssertionError
"""
        
        parsed = corrector._parse_error(error_output, "pytest")
        
        assert parsed["detected"] is True
        assert parsed["type"] == "pytest"
        assert parsed["category"] == "assertion"
        assert "test_file.py" in parsed["file"]
    
    def test_parse_syntax_error(self):
        """Test parsing Python syntax error."""
        corrector = ErrorCorrector()
        
        error_output = """
  File "script.py", line 10
    if x == 5
            ^
SyntaxError: invalid syntax
"""
        
        parsed = corrector._parse_error(error_output, "syntax")
        
        assert parsed["detected"] is True
        assert parsed["type"] == "syntax"
        assert parsed["category"] == "invalid_syntax"
        assert parsed["file"] == "script.py"
        assert parsed["line"] == 10
    
    def test_parse_import_error(self):
        """Test parsing import error."""
        corrector = ErrorCorrector()
        
        error_output = """
Traceback (most recent call last):
  File "app.py", line 3, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
"""
        
        parsed = corrector._parse_error(error_output, "import")
        
        assert parsed["detected"] is True
        assert parsed["type"] == "import"
        assert parsed["category"] == "import"
        assert parsed["missing_module"] == "requests"
        assert "requests" in parsed["message"]
    
    def test_parse_runtime_name_error(self):
        """Test parsing NameError."""
        corrector = ErrorCorrector()
        
        error_output = """
Traceback (most recent call last):
  File "app.py", line 15, in process
    result = calculate_total()
NameError: name 'calculate_total' is not defined
"""
        
        parsed = corrector._parse_error(error_output, "runtime")
        
        assert parsed["detected"] is True
        assert parsed["category"] == "name"
        assert parsed["undefined_name"] == "calculate_total"
    
    def test_parse_indentation_error(self):
        """Test parsing indentation error."""
        corrector = ErrorCorrector()
        
        error_output = """
  File "script.py", line 8
    print("hello")
    ^
IndentationError: unexpected indent
"""
        
        parsed = corrector._parse_error(error_output, "syntax")
        
        assert parsed["detected"] is True
        assert parsed["category"] == "indentation"
        assert parsed["file"] == "script.py"


class TestFixPatterns:
    """Test fix pattern detection and application."""
    
    def test_find_patterns_for_syntax_error(self):
        """Test finding patterns for syntax errors."""
        corrector = ErrorCorrector()
        
        parsed_error = {
            "type": "syntax",
            "category": "indentation",
            "file": "test.py",
            "line": 5
        }
        
        patterns = corrector._find_fix_patterns(parsed_error)
        
        assert len(patterns) > 0
        assert any(p["name"] == "fix_indentation" for p in patterns)
    
    def test_find_patterns_for_import_error(self):
        """Test finding patterns for import errors."""
        corrector = ErrorCorrector()
        
        parsed_error = {
            "type": "import",
            "category": "import",
            "missing_module": "pandas",
            "file": "analysis.py"
        }
        
        patterns = corrector._find_fix_patterns(parsed_error)
        
        assert len(patterns) > 0
        assert any(p["name"] == "install_missing_module" for p in patterns)
        assert any("pandas" in str(p.get("params", {})) for p in patterns)
    
    def test_find_patterns_for_name_error(self):
        """Test finding patterns for NameError."""
        corrector = ErrorCorrector()
        
        parsed_error = {
            "type": "runtime",
            "category": "name",
            "undefined_name": "Path",
            "file": "utils.py"
        }
        
        patterns = corrector._find_fix_patterns(parsed_error)
        
        assert len(patterns) > 0
        assert any(p["name"] == "add_import" for p in patterns)
    
    def test_patterns_sorted_by_confidence(self):
        """Test patterns are sorted by confidence."""
        corrector = ErrorCorrector()
        
        parsed_error = {
            "type": "syntax",
            "category": "indentation"
        }
        
        patterns = corrector._find_fix_patterns(parsed_error)
        
        if len(patterns) > 1:
            for i in range(len(patterns) - 1):
                assert patterns[i]["confidence"] >= patterns[i+1]["confidence"]


class TestFixApplication:
    """Test applying fixes."""
    
    def test_suggest_package_install(self):
        """Test package installation suggestion."""
        corrector = ErrorCorrector()
        
        params = {"package": "numpy"}
        result = corrector._suggest_package_install(params)
        
        assert result["success"] is True
        assert "numpy" in result["message"]
        assert "pip install" in result["command"]
    
    def test_suggest_import_common_module(self):
        """Test import suggestion for common modules."""
        corrector = ErrorCorrector()
        
        parsed_error = {"undefined_name": "Path"}
        params = {"name": "Path"}
        
        result = corrector._suggest_import(parsed_error, params)
        
        assert result["success"] is True
        assert "from pathlib import Path" in result["import_statement"]
    
    def test_suggest_import_unknown_module(self):
        """Test import suggestion for unknown modules."""
        corrector = ErrorCorrector()
        
        parsed_error = {"undefined_name": "UnknownClass"}
        params = {"name": "UnknownClass"}
        
        result = corrector._suggest_import(parsed_error, params)
        
        assert result["success"] is True
        assert "UnknownClass" in result["import_statement"]
    
    def test_fix_indentation_normalizes_tabs(self):
        """Test indentation fix converts tabs to spaces."""
        corrector = ErrorCorrector()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n\t\tprint('hello')\n")
            temp_file = f.name
        
        try:
            params = {"spaces": 4}
            result = corrector._fix_indentation(temp_file, params)
            
            assert result["success"] is True
            assert "normalized" in result["message"].lower()
            assert "\t" not in result["fixed_content"]
        finally:
            Path(temp_file).unlink()


class TestEndToEndCorrection:
    """Test complete error correction flow."""
    
    def test_correct_import_error_flow(self):
        """Test full flow: parse import error → suggest fix."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={
                "error_output": "ModuleNotFoundError: No module named 'requests'",
                "error_type": "import"
            },
            user_message="Fix this import error"
        )
        
        response = corrector.execute(request)
        
        assert response.success is True
        assert "requests" in str(response.result)
    
    def test_correct_syntax_error_flow(self):
        """Test full flow: parse syntax error → suggest fix."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={
                "error_output": """  File "test.py", line 5
    if x == 5
            ^
SyntaxError: invalid syntax""",
                "file_path": "/tmp/test.py"
            },
            user_message="Fix syntax"
        )
        
        response = corrector.execute(request)
        
        # Should detect error and provide fix suggestion (even if file doesn't exist)
        assert "syntax" in str(response.result).lower() or "colon" in str(response.result).lower()
    
    def test_no_fix_available(self):
        """Test response when no automatic fix is available."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={
                "error_output": """
Very obscure error that has no known fix pattern
""",
                "error_type": "unknown"
            },
            user_message="Fix this"
        )
        
        response = corrector.execute(request)
        
        # Should parse but not find fix
        # Accept either parse failure OR successful parse with no fix
        assert response.success is False or "manual review" in response.message.lower()
    
    def test_missing_error_output(self):
        """Test handling missing error output."""
        corrector = ErrorCorrector()
        
        request = AgentRequest(
            intent=IntentType.FIX.value,
            context={},
            user_message="Fix error"
        )
        
        response = corrector.execute(request)
        
        assert response.success is False
        assert "no error output" in response.message.lower()


class TestIsolationValidation:
    """Test that ErrorCorrector respects test isolation."""
    
    def test_cortex_tests_are_protected(self):
        """Test CORTEX/tests directory is in protected list."""
        corrector = ErrorCorrector()
        
        assert "CORTEX/tests" in corrector.protected_paths
    
    def test_cortex_agents_are_protected(self):
        """Test CORTEX/src/cortex_agents is protected."""
        corrector = ErrorCorrector()
        
        assert "CORTEX/src/cortex_agents" in corrector.protected_paths
    
    def test_application_files_not_protected(self):
        """Test application files can be auto-fixed."""
        corrector = ErrorCorrector()
        
        app_files = [
            "app/src/main.py",
            "app/tests/test_app.py",
            "/tmp/project/utils.py"
        ]
        
        for app_file in app_files:
            assert not corrector._is_protected_path(app_file)
    
    def test_protection_documented_in_docstring(self):
        """Test protection is documented."""
        import inspect
        
        docstring = inspect.getdoc(ErrorCorrector)
        
        assert "ISOLATION" in docstring
        assert "CORTEX/tests" in docstring
        assert "TARGET APPLICATION" in docstring


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
