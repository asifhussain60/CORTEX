"""
Tests for TestGenerator Agent

Tests test generation functionality including code analysis,
test scenario identification, and pytest code generation.
"""

import os
import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock

from CORTEX.src.cortex_agents.test_generator import TestGenerator
from CORTEX.src.cortex_agents.base_agent import AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType


# Sample code for testing
SAMPLE_FUNCTION = """
def add(a, b):
    return a + b
"""

SAMPLE_FUNCTION_WITH_EDGE_CASES = """
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""

SAMPLE_CLASS = """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        self.result = a + b
        return self.result
    
    def _private_method(self):
        return "private"
"""

SAMPLE_ASYNC_FUNCTION = """
async def fetch_data(url):
    return await some_async_call(url)
"""


class TestTestGeneratorBasics:
    """Test basic TestGenerator functionality."""
    
    def test_initialization(self):
        """Test agent initialization."""
        generator = TestGenerator(name="TestGenerator")
        
        assert generator.name == "TestGenerator"
        assert len(generator.TEST_TEMPLATES) > 0
        assert len(generator.COMMON_FIXTURES) > 0
    
    def test_can_handle_test_intent(self):
        """Test can_handle for test intent."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={},
            user_message="Generate tests"
        )
        
        assert generator.can_handle(request) is True
    
    def test_can_handle_tdd_intent(self):
        """Test can_handle for TDD intent."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TDD.value,
            context={},
            user_message="Do TDD"
        )
        
        assert generator.can_handle(request) is True
    
    def test_can_handle_string_intents(self):
        """Test can_handle for string variants."""
        generator = TestGenerator(name="TestGenerator")
        
        for intent in ["generate_tests", "create_tests", "test_generation"]:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Generate"
            )
            assert generator.can_handle(request) is True
    
    def test_cannot_handle_other_intents(self):
        """Test can_handle rejects non-test intents."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.PLAN.value,
            context={},
            user_message="Plan something"
        )
        
        assert generator.can_handle(request) is False


class TestCodeAnalysis:
    """Test code analysis functionality."""
    
    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = generator._analyze_code(SAMPLE_FUNCTION)
        
        assert analysis["success"] is True
        assert len(analysis["functions"]) == 1
        assert analysis["functions"][0]["name"] == "add"
        assert analysis["functions"][0]["arg_count"] == 2
        assert "basic" in analysis["functions"][0]["scenarios"]
    
    def test_analyze_function_with_error_handling(self):
        """Test analyzing function with error handling."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = generator._analyze_code(SAMPLE_FUNCTION_WITH_EDGE_CASES)
        
        assert analysis["success"] is True
        assert len(analysis["functions"]) == 1
        func = analysis["functions"][0]
        assert func["name"] == "divide"
        assert "error_handling" in func["scenarios"]
        assert "edge_cases" in func["scenarios"]
    
    def test_analyze_class(self):
        """Test analyzing a class."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = generator._analyze_code(SAMPLE_CLASS)
        
        assert analysis["success"] is True
        assert len(analysis["classes"]) == 1
        cls = analysis["classes"][0]
        assert cls["name"] == "Calculator"
        assert cls["has_init"] is True
        assert cls["method_count"] >= 2  # __init__ and add (private excluded)
    
    def test_analyze_async_function(self):
        """Test analyzing async function."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = generator._analyze_code(SAMPLE_ASYNC_FUNCTION)
        
        assert analysis["success"] is True
        assert analysis["has_async"] is True
    
    def test_analyze_invalid_syntax(self):
        """Test analyzing code with syntax errors."""
        generator = TestGenerator(name="TestGenerator")
        
        invalid_code = "def broken(\n    pass"
        analysis = generator._analyze_code(invalid_code)
        
        assert analysis["success"] is False
        assert "error" in analysis


class TestTestGeneration:
    """Test test code generation."""
    
    def test_generate_for_simple_function(self):
        """Test generating tests for simple function."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"source_code": SAMPLE_FUNCTION},
            user_message="Generate tests for add function"
        )
        
        response = generator.execute(request)
        
        assert response.success is True
        assert response.result["test_count"] > 0
        assert "def test_add" in response.result["test_code"]
        assert "import pytest" in response.result["test_code"]
    
    def test_generate_for_class(self):
        """Test generating tests for class."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"source_code": SAMPLE_CLASS},
            user_message="Generate tests for Calculator"
        )
        
        response = generator.execute(request)
        
        assert response.success is True
        assert response.result["test_count"] > 0
        assert "class TestCalculator" in response.result["test_code"]
        assert "def test_calculator_initialization" in response.result["test_code"]
    
    def test_generate_from_file(self):
        """Test generating tests from file path."""
        generator = TestGenerator(name="TestGenerator")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_FUNCTION)
            temp_path = f.name
        
        try:
            request = AgentRequest(
                intent=IntentType.TEST.value,
                context={"file_path": temp_path},
                user_message="Generate tests"
            )
            
            response = generator.execute(request)
            
            assert response.success is True
            assert response.result["test_count"] > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_generate_without_input(self):
        """Test generation fails without input."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={},
            user_message="Generate tests"
        )
        
        response = generator.execute(request)
        
        assert response.success is False
        assert "no file_path or source_code" in response.message.lower()
    
    def test_generate_for_nonexistent_file(self):
        """Test generation fails for nonexistent file."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"file_path": "/nonexistent/file.py"},
            user_message="Generate tests"
        )
        
        response = generator.execute(request)
        
        assert response.success is False
        assert "not found" in response.message.lower()


class TestTestTemplates:
    """Test test template generation."""
    
    def test_basic_function_template(self):
        """Test basic function template."""
        generator = TestGenerator(name="TestGenerator")
        
        func_info = {
            "name": "test_func",
            "args": ["a", "b"],
            "has_return": True,
            "scenarios": ["basic"]
        }
        
        test_code = generator._template_basic_function(func_info)
        
        assert "def test_test_func_basic" in test_code
        assert "mock_a" in test_code
        assert "mock_b" in test_code
        assert "assert result is not None" in test_code
    
    def test_edge_cases_template(self):
        """Test edge cases template."""
        generator = TestGenerator(name="TestGenerator")
        
        func_info = {
            "name": "test_func",
            "args": ["input"],
            "scenarios": ["edge_cases"]
        }
        
        test_code = generator._template_edge_cases(func_info)
        
        assert "def test_test_func_edge_cases" in test_code
        assert "None" in test_code
        assert '""' in test_code
    
    def test_error_handling_template(self):
        """Test error handling template."""
        generator = TestGenerator(name="TestGenerator")
        
        func_info = {
            "name": "test_func",
            "args": [],
            "scenarios": ["error_handling"]
        }
        
        test_code = generator._template_error_handling(func_info)
        
        assert "def test_test_func_error_handling" in test_code
        assert "pytest.raises" in test_code


class TestHelperMethods:
    """Test helper methods."""
    
    def test_count_tests(self):
        """Test counting generated tests."""
        generator = TestGenerator(name="TestGenerator")
        
        test_code = """
def test_one():
    pass

def test_two():
    pass

def helper():  # Not a test
    pass
"""
        
        count = generator._count_tests(test_code)
        assert count == 2
    
    def test_generate_test_header(self):
        """Test generating test file header."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = {"has_async": False}
        header = generator._generate_test_header(analysis)
        
        assert "import pytest" in header
        assert "unittest.mock" in header
    
    def test_generate_test_header_with_async(self):
        """Test header generation with async code."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = {"has_async": True}
        header = generator._generate_test_header(analysis)
        
        assert "import asyncio" in header
    
    def test_generate_fixtures(self):
        """Test fixture generation."""
        generator = TestGenerator(name="TestGenerator")
        
        analysis = {
            "classes": [
                {"name": "MyClass", "methods": []}
            ]
        }
        
        fixtures = generator._generate_fixtures(analysis)
        
        assert "@pytest.fixture" in fixtures
        assert "def myclass_instance" in fixtures
    
    def test_suggest_actions_on_success(self):
        """Test action suggestions after successful generation."""
        generator = TestGenerator(name="TestGenerator")
        
        result = {"success": True, "test_count": 5}
        actions = generator._suggest_next_actions(result)
        
        assert len(actions) > 0
        assert any("review" in a.lower() for a in actions)
        assert any("run" in a.lower() for a in actions)
    
    def test_suggest_actions_on_failure(self):
        """Test action suggestions after failed generation."""
        generator = TestGenerator(name="TestGenerator")
        
        result = {"success": False}
        actions = generator._suggest_next_actions(result)
        
        assert len(actions) > 0
        assert any("fix" in a.lower() for a in actions)


class TestIntegration:
    """Test full TestGenerator workflow."""
    
    def test_full_workflow_with_function(self):
        """Test complete workflow for function."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"source_code": SAMPLE_FUNCTION_WITH_EDGE_CASES},
            user_message="Generate comprehensive tests"
        )
        
        response = generator.execute(request)
        
        assert response.success is True
        assert response.result["test_count"] >= 2  # Basic + error handling
        assert "divide" in response.result["test_code"]
        assert len(response.next_actions) > 0
    
    def test_full_workflow_with_class(self):
        """Test complete workflow for class."""
        generator = TestGenerator(name="TestGenerator")
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"source_code": SAMPLE_CLASS},
            user_message="Generate tests for Calculator class"
        )
        
        response = generator.execute(request)
        
        assert response.success is True
        assert response.result["classes"] == 1
        assert response.result["test_count"] >= 2  # Init + methods
        assert "TestCalculator" in response.result["test_code"]
