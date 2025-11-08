"""
TestGenerator Agent

Analyzes code and generates pytest-compatible test cases.
Creates comprehensive test suites with fixtures, mocks, and edge cases.

The TestGenerator helps maintain high test coverage by automatically
generating test scaffolding for new code.
"""

import os
import ast
import inspect
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType
from CORTEX.src.cortex_agents.utils import safe_get


class TestGenerator(BaseAgent):
    """
    Generates pytest-compatible test cases from code analysis.
    
    The TestGenerator performs code analysis and test generation including:
    - Function/method signature analysis
    - Test scenario identification
    - Fixture generation
    - Mock object creation
    - Edge case detection
    
    Features:
    - AST-based code analysis
    - pytest-style test generation
    - Mock/fixture templates
    - Pattern learning from Tier 2
    - Coverage-aware generation
    
    Example:
        generator = TestGenerator(name="Generator", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="test",
            context={
                "file_path": "/path/to/module.py",
                "target": "MyClass"
            },
            user_message="Generate tests for MyClass"
        )
        
        response = generator.execute(request)
        # Returns: {
        #   "test_code": "...",
        #   "test_count": 5,
        #   "scenarios": ["basic", "edge_cases", "errors"]
        # }
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize TestGenerator with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Test templates for different scenarios
        self.TEST_TEMPLATES = {
            "basic_function": self._template_basic_function,
            "class_method": self._template_class_method,
            "edge_cases": self._template_edge_cases,
            "error_handling": self._template_error_handling
        }
        
        # Common test fixtures
        self.COMMON_FIXTURES = [
            "mock_tier1",
            "mock_tier2", 
            "mock_tier3",
            "temp_file",
            "temp_directory"
        ]
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is test, tdd, or test generation
        """
        valid_intents = [
            IntentType.TEST.value,
            IntentType.TDD.value,
            "generate_tests",
            "create_tests",
            "test_generation"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Generate test cases for code.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with generated test code
        """
        try:
            self.log_request(request)
            self.logger.info("Starting test generation")
            
            # Get file path or code to test
            file_path = safe_get(request.context, "file_path")
            source_code = safe_get(request.context, "source_code")
            target = safe_get(request.context, "target")  # Optional specific target
            
            if not file_path and not source_code:
                return AgentResponse(
                    success=False,
                    result=None,
                    message="No file_path or source_code provided",
                    agent_name=self.name
                )
            
            # Read source code if file path provided
            if file_path and not source_code:
                if not os.path.exists(file_path):
                    return AgentResponse(
                        success=False,
                        result=None,
                        message=f"File not found: {file_path}",
                        agent_name=self.name
                    )
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            
            # Analyze code structure
            analysis = self._analyze_code(source_code, target)
            
            if not analysis["success"]:
                return AgentResponse(
                    success=False,
                    result=analysis,
                    message=analysis.get("error", "Code analysis failed"),
                    agent_name=self.name
                )
            
            # Search Tier 2 for similar test patterns
            similar_patterns = self._find_similar_test_patterns(analysis)
            
            # Generate test code
            test_code = self._generate_test_code(analysis, similar_patterns)
            
            # Count generated tests
            test_count = self._count_tests(test_code)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"TestGenerator: Generated {test_count} tests"
                )
            
            # Store pattern in Tier 2 for learning
            if self.tier2:
                self._store_test_pattern(analysis, test_code)
            
            result = {
                "success": True,
                "test_code": test_code,
                "test_count": test_count,
                "scenarios": analysis["scenarios"],
                "functions": len(analysis["functions"]),
                "classes": len(analysis["classes"]),
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            
            response = AgentResponse(
                success=True,
                result=result,
                message=f"Generated {test_count} tests for {len(analysis['functions'])} functions and {len(analysis['classes'])} classes",
                agent_name=self.name,
                metadata={
                    "test_count": test_count,
                    "scenarios": analysis["scenarios"]
                },
                next_actions=self._suggest_next_actions(result)
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Test generation failed: {str(e)}",
                agent_name=self.name
            )
    
    def _analyze_code(self, source_code: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze source code to identify testable components.
        
        Args:
            source_code: Python source code to analyze
            target: Optional specific class/function to target
        
        Returns:
            Analysis results with functions, classes, and scenarios
        """
        try:
            tree = ast.parse(source_code)
            
            functions = []
            classes = []
            scenarios = []
            
            for node in ast.walk(tree):
                # Find function definitions (both sync and async)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions unless specifically targeted
                    if target or not node.name.startswith('_'):
                        func_info = self._analyze_function(node)
                        
                        # Check if this matches target
                        if not target or node.name == target:
                            functions.append(func_info)
                            scenarios.extend(func_info["scenarios"])
                
                # Find class definitions
                elif isinstance(node, ast.ClassDef):
                    if not target or node.name == target:
                        class_info = self._analyze_class(node)
                        classes.append(class_info)
                        scenarios.extend(class_info["scenarios"])
            
            # Deduplicate scenarios
            scenarios = list(set(scenarios))
            
            return {
                "success": True,
                "functions": functions,
                "classes": classes,
                "scenarios": scenarios,
                "has_async": any(f.get("is_async") for f in functions)
            }
            
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error in source code: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Analyze a function definition.
        
        Args:
            node: AST FunctionDef node
        
        Returns:
            Function analysis info
        """
        # Get function signature
        args = [arg.arg for arg in node.args.args]
        
        # Detect scenarios based on function characteristics
        scenarios = ["basic"]
        
        # Check for error handling
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                scenarios.append("error_handling")
                break
        
        # Check for conditionals (edge cases)
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                scenarios.append("edge_cases")
                break
        
        return {
            "name": node.name,
            "args": args,
            "arg_count": len(args),
            "scenarios": scenarios,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "has_return": any(isinstance(n, ast.Return) for n in ast.walk(node))
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """
        Analyze a class definition.
        
        Args:
            node: AST ClassDef node
        
        Returns:
            Class analysis info
        """
        methods = []
        scenarios = ["basic"]
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item)
                methods.append(method_info)
                scenarios.extend(method_info["scenarios"])
        
        # Check for __init__ method
        has_init = any(m["name"] == "__init__" for m in methods)
        
        if has_init:
            scenarios.append("initialization")
        
        return {
            "name": node.name,
            "methods": methods,
            "method_count": len(methods),
            "scenarios": list(set(scenarios)),
            "has_init": has_init
        }
    
    def _find_similar_test_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search Tier 2 for similar test patterns.
        
        Args:
            analysis: Code analysis results
        
        Returns:
            List of similar test patterns
        """
        if not self.tier2:
            return []
        
        try:
            # Search for test patterns in Tier 2
            # (Simplified - real implementation would use proper API)
            patterns = []
            
            for func in analysis.get("functions", []):
                # Search for tests of similar functions
                query = f"test pattern for function with {func['arg_count']} arguments"
                # results = self.tier2.search(query, limit=3)
                # patterns.extend(results)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to search test patterns: {str(e)}")
            return []
    
    def _generate_test_code(
        self,
        analysis: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """
        Generate test code from analysis.
        
        Args:
            analysis: Code analysis results
            patterns: Similar patterns from Tier 2
        
        Returns:
            Generated test code
        """
        test_parts = []
        
        # Generate header with imports
        test_parts.append(self._generate_test_header(analysis))
        
        # Generate fixtures if needed
        if analysis.get("classes"):
            test_parts.append(self._generate_fixtures(analysis))
        
        # Generate tests for functions
        for func in analysis.get("functions", []):
            test_parts.append(self._generate_function_tests(func))
        
        # Generate tests for classes
        for cls in analysis.get("classes", []):
            test_parts.append(self._generate_class_tests(cls))
        
        return "\n\n".join(test_parts)
    
    def _generate_test_header(self, analysis: Dict[str, Any]) -> str:
        """Generate test file header with imports."""
        imports = [
            '"""',
            'Generated test file',
            '"""',
            '',
            'import pytest',
            'from unittest.mock import Mock, patch, MagicMock'
        ]
        
        if analysis.get("has_async"):
            imports.append('import asyncio')
        
        return '\n'.join(imports)
    
    def _generate_fixtures(self, analysis: Dict[str, Any]) -> str:
        """Generate pytest fixtures for classes."""
        fixtures = []
        
        for cls in analysis.get("classes", []):
            fixture_code = f'''@pytest.fixture
def {cls["name"].lower()}_instance():
    """Fixture for {cls["name"]} instance."""
    return {cls["name"]}()'''
            fixtures.append(fixture_code)
        
        return '\n\n'.join(fixtures) if fixtures else ""
    
    def _generate_function_tests(self, func_info: Dict[str, Any]) -> str:
        """Generate tests for a function."""
        tests = []
        
        # Basic test
        if "basic" in func_info["scenarios"]:
            tests.append(self._template_basic_function(func_info))
        
        # Edge cases test
        if "edge_cases" in func_info["scenarios"]:
            tests.append(self._template_edge_cases(func_info))
        
        # Error handling test
        if "error_handling" in func_info["scenarios"]:
            tests.append(self._template_error_handling(func_info))
        
        return '\n\n'.join(tests)
    
    def _generate_class_tests(self, class_info: Dict[str, Any]) -> str:
        """Generate tests for a class."""
        class_name = class_info["name"]
        test_class_name = f"Test{class_name}"
        
        tests = [f'class {test_class_name}:']
        tests.append(f'    """Tests for {class_name} class."""')
        tests.append('')
        
        # Initialization test
        if class_info["has_init"]:
            tests.append(f'    def test_{class_name.lower()}_initialization(self):')
            tests.append(f'        """Test {class_name} initialization."""')
            tests.append(f'        instance = {class_name}()')
            tests.append(f'        assert instance is not None')
        
        # Method tests
        for method in class_info.get("methods", []):
            if method["name"].startswith("_") and method["name"] != "__init__":
                continue  # Skip private methods
            
            if method["name"] != "__init__":
                tests.append('')
                tests.append(f'    def test_{method["name"]}(self):')
                tests.append(f'        """Test {method["name"]} method."""')
                tests.append(f'        instance = {class_name}()')
                
                # Generate basic call
                if method["args"]:
                    # Filter out 'self'
                    args = [a for a in method["args"] if a != "self"]
                    if args:
                        args_str = ", ".join(f"mock_{a}" for a in args)
                        tests.append(f'        result = instance.{method["name"]}({args_str})')
                    else:
                        tests.append(f'        result = instance.{method["name"]}()')
                else:
                    tests.append(f'        result = instance.{method["name"]}()')
                
                if method.get("has_return"):
                    tests.append(f'        assert result is not None')
        
        return '\n'.join(tests)
    
    def _template_basic_function(self, func_info: Dict[str, Any]) -> str:
        """Template for basic function test."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_basic():',
            f'    """Test basic {func_name} functionality."""',
        ]
        
        # Generate function call
        if func_info["args"]:
            args = func_info["args"]
            args_str = ", ".join(f"mock_{a}" for a in args)
            test.append(f'    result = {func_name}({args_str})')
        else:
            test.append(f'    result = {func_name}()')
        
        # Add assertion
        if func_info.get("has_return"):
            test.append(f'    assert result is not None')
        
        return '\n'.join(test)
    
    def _template_class_method(self, method_info: Dict[str, Any]) -> str:
        """Template for class method test."""
        return self._template_basic_function(method_info)
    
    def _template_edge_cases(self, func_info: Dict[str, Any]) -> str:
        """Template for edge case tests."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_edge_cases():',
            f'    """Test {func_name} edge cases."""',
            f'    # Test with None',
            f'    result = {func_name}(None)',
            f'    assert result is not None',
            '',
            f'    # Test with empty values',
            f'    result = {func_name}("")',
            f'    assert result is not None',
        ]
        
        return '\n'.join(test)
    
    def _template_error_handling(self, func_info: Dict[str, Any]) -> str:
        """Template for error handling tests."""
        func_name = func_info["name"]
        
        test = [
            f'def test_{func_name}_error_handling():',
            f'    """Test {func_name} error handling."""',
            f'    with pytest.raises(Exception):',
            f'        {func_name}(invalid_input)',
        ]
        
        return '\n'.join(test)
    
    def _count_tests(self, test_code: str) -> int:
        """
        Count number of test functions in generated code.
        
        Args:
            test_code: Generated test code
        
        Returns:
            Number of test functions
        """
        try:
            tree = ast.parse(test_code)
            count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        count += 1
            
            return count
        except:
            # Fallback: count lines with "def test_"
            return test_code.count('def test_')
    
    def _store_test_pattern(self, analysis: Dict[str, Any], test_code: str) -> None:
        """
        Store test pattern in Tier 2 for learning.
        
        Args:
            analysis: Code analysis
            test_code: Generated test code
        """
        if not self.tier2:
            return
        
        try:
            pattern_data = {
                "type": "test_generation",
                "functions": len(analysis.get("functions", [])),
                "classes": len(analysis.get("classes", [])),
                "test_count": self._count_tests(test_code),
                "scenarios": analysis.get("scenarios", []),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.debug(f"Storing test pattern: {pattern_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {str(e)}")
    
    def _suggest_next_actions(self, result: Dict[str, Any]) -> List[str]:
        """
        Suggest next actions based on generation result.
        
        Args:
            result: Generation result
        
        Returns:
            List of suggested actions
        """
        actions = []
        
        if result.get("success"):
            actions.append("Review generated tests")
            actions.append("Run tests to verify functionality")
            actions.append("Add assertions specific to your logic")
            actions.append("Implement mock objects for dependencies")
            
            if result.get("test_count", 0) > 10:
                actions.append("Consider splitting into multiple test files")
        else:
            actions.append("Fix code issues before generating tests")
            actions.append("Ensure code is syntactically valid")
        
        return actions
