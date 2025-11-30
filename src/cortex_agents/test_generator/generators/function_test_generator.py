"""Function test generation with Edge Case Intelligence and Domain Knowledge."""

import ast
from typing import Dict, Any, List
from ..templates import TemplateManager
from ..edge_case_analyzer import EdgeCaseAnalyzer, EdgeCase
from ..domain_knowledge_integrator import DomainKnowledgeIntegrator
from ..error_condition_generator import ErrorConditionGenerator, ErrorCondition
from ..parametrized_test_generator import ParametrizedTestGenerator, ParametrizedScenario, PropertyTest


class FunctionTestGenerator:
    """Generates test code for functions with intelligent edge case detection and smart assertions."""
    
    def __init__(self, template_manager: TemplateManager):
        """Initialize with template manager."""
        self.templates = template_manager
        self.edge_analyzer = EdgeCaseAnalyzer()
        self.domain_knowledge = DomainKnowledgeIntegrator()
        self.error_generator = ErrorConditionGenerator()
        self.parametrized_generator = ParametrizedTestGenerator()
    
    def generate(self, func_info: Dict[str, Any]) -> str:
        """Generate tests for a function with automatic edge case detection."""
        tests = []
        
        # Basic test (happy path)
        if "basic" in func_info.get("scenarios", ["basic"]):
            tests.append(self.templates.basic_function(func_info))
        
        # Intelligent edge case generation
        if "edge_cases" in func_info.get("scenarios", ["edge_cases"]):
            edge_cases_tests = self._generate_edge_case_tests(func_info)
            tests.extend(edge_cases_tests)
        
        # Error condition tests (NEW - M1.3)
        if "error_conditions" in func_info.get("scenarios", ["error_conditions"]):
            error_tests = self._generate_error_condition_tests(func_info)
            tests.extend(error_tests)
        
        # Parametrized tests (NEW - M1.4)
        if "parametrized" in func_info.get("scenarios", ["parametrized"]):
            parametrized_tests = self._generate_parametrized_tests(func_info)
            tests.extend(parametrized_tests)
        
        # Property-based tests (NEW - M1.4)
        if "property_based" in func_info.get("scenarios", ["property_based"]):
            property_tests = self._generate_property_based_tests(func_info)
            tests.extend(property_tests)
        
        # Error handling test (legacy template)
        if "error_handling" in func_info.get("scenarios", ["error_handling"]):
            tests.append(self.templates.error_handling(func_info))
        
        return '\n\n'.join(tests)
    
    def _generate_edge_case_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate edge case tests using EdgeCaseAnalyzer."""
        # Parse function AST if source code provided
        if "source_code" not in func_info or "ast_node" not in func_info:
            # Fallback to template-based generation
            return [self.templates.edge_cases(func_info)]
        
        # Analyze function for edge cases
        edge_cases = self.edge_analyzer.analyze_function(
            func_info["ast_node"],
            func_info["source_code"]
        )
        
        # Filter by confidence threshold
        edge_cases = self.edge_analyzer.filter_by_confidence(min_confidence=0.6)
        
        # Prioritize edge cases
        edge_cases = self.edge_analyzer.prioritize_edge_cases()
        
        # Generate test code for each edge case
        test_code_list = []
        for edge_case in edge_cases[:10]:  # Limit to top 10 edge cases
            test_code = self._generate_edge_case_test_code(edge_case, func_info)
            test_code_list.append(test_code)
        
        return test_code_list
    
    def _generate_edge_case_test_code(self, edge_case: EdgeCase, func_info: Dict[str, Any]) -> str:
        """Generate Python test code for a single edge case with smart assertions."""
        func_name = func_info["name"]
        
        # Build parameter string
        params = []
        for param in func_info.get("parameters", []):
            param_name = param["name"]
            if param_name in edge_case.input_values:
                value = edge_case.input_values[param_name]
                params.append(f"{param_name}={repr(value)}")
            else:
                # Use default or placeholder
                if param.get("default"):
                    params.append(f"{param_name}={param['default']}")
                else:
                    # Placeholder value
                    params.append(f"{param_name}=None")
        
        param_str = ", ".join(params)
        
        # Get context-aware test information
        context_test = self.domain_knowledge.generate_context_aware_test(
            func_info,
            edge_case
        )
        
        # Generate test based on expected behavior with smart assertions
        if edge_case.expected_behavior == "raise":
            # Exception-raising test with improved matching
            exception = edge_case.expected_exception or "Exception"
            test_code = f'''def {edge_case.name}(self):
    """{edge_case.description}
    
    Confidence: {context_test['confidence']:.0%}
    """
    with pytest.raises({exception}, match=r".+"):
        {func_name}({param_str})'''
        
        elif edge_case.expected_value is not None:
            # Specific value assertion (strong)
            test_code = f'''def {edge_case.name}(self):
    """{edge_case.description}
    
    Confidence: {context_test['confidence']:.0%}
    """
    result = {func_name}({param_str})
    assert result == {repr(edge_case.expected_value)}, f"Expected {{result}} to equal {repr(edge_case.expected_value)}"'''
        
        else:
            # Use domain knowledge for smart assertion
            smart_assertions = context_test['assertions']
            if smart_assertions and "TODO" not in smart_assertions[0]:
                assertion = smart_assertions[0]
            else:
                # Fallback to type checking if available
                assertion = "assert result is not None  # TODO: Add specific assertion"
            
            test_code = f'''def {edge_case.name}(self):
    """{edge_case.description}
    
    Confidence: {context_test['confidence']:.0%}
    """
    result = {func_name}({param_str})
    {assertion}'''
        
        # Improve assertion strength using domain knowledge
        test_code = self.domain_knowledge.improve_assertion_strength(test_code)
        
        return test_code
    
    def _generate_error_condition_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate error condition tests using ErrorConditionGenerator."""
        # Analyze function for error conditions
        if "source_code" not in func_info or "ast_node" not in func_info:
            return []
        
        error_conditions = self.error_generator.analyze_function(
            func_info["ast_node"],
            func_info["source_code"]
        )
        
        # Filter by confidence threshold
        error_conditions = self.error_generator.filter_by_confidence(min_confidence=0.7)
        
        # Prioritize error conditions
        error_conditions = self.error_generator.prioritize_error_conditions()
        
        # Generate test code for each error condition
        test_code_list = []
        for error_condition in error_conditions[:10]:  # Limit to top 10
            test_code = self._generate_error_condition_test_code(error_condition, func_info)
            test_code_list.append(test_code)
        
        return test_code_list
    
    def _generate_error_condition_test_code(self, error_condition: ErrorCondition, func_info: Dict[str, Any]) -> str:
        """Generate Python test code for an error condition with pytest.raises."""
        func_name = func_info["name"]
        
        # Build parameter string
        params = []
        for param in func_info.get("parameters", []):
            param_name = param["name"]
            if param_name in error_condition.input_values:
                value = error_condition.input_values[param_name]
                params.append(f"{param_name}={repr(value)}")
            else:
                # Use placeholder
                params.append(f"{param_name}=None")
        
        param_str = ", ".join(params) if params else ""
        
        # Generate pytest.raises test with regex matching
        test_code = f'''def {error_condition.name}(self):
    """{error_condition.description}
    
    Confidence: {error_condition.confidence:.0%}
    """
    with pytest.raises({error_condition.exception_type}, match=r"{error_condition.expected_message_regex}"):
        {func_name}({param_str})'''
        
        return test_code
    
    def _generate_parametrized_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate parametrized tests using ParametrizedTestGenerator."""
        if "source_code" not in func_info or "ast_node" not in func_info:
            return []
        
        # Analyze function for parametrized scenarios
        parametrized_tests, _ = self.parametrized_generator.analyze_function(
            func_info["ast_node"],
            func_info["source_code"]
        )
        
        # Filter by confidence
        parametrized_tests, _ = self.parametrized_generator.filter_by_confidence(min_confidence=0.7)
        
        # Prioritize tests
        parametrized_tests, _ = self.parametrized_generator.prioritize_tests()
        
        # Generate test code for each parametrized scenario
        test_code_list = []
        for scenario in parametrized_tests[:5]:  # Limit to top 5 scenarios
            test_code = self._generate_parametrized_test_code(scenario, func_info)
            test_code_list.append(test_code)
        
        return test_code_list
    
    def _generate_parametrized_test_code(self, scenario: ParametrizedScenario, func_info: Dict[str, Any]) -> str:
        """Generate Python test code for a parametrized scenario."""
        func_name = func_info["name"]
        
        # Build pytest.mark.parametrize decorator
        param_names = ", ".join(scenario.parameters)
        
        # Format scenarios
        scenario_values = []
        for scenario_tuple in scenario.scenarios:
            scenario_values.append(repr(scenario_tuple))
        
        scenarios_str = ",\n        ".join(scenario_values)
        
        # Build test function
        test_code = f'''@pytest.mark.parametrize("{param_names}", [
        {scenarios_str}
    ])
def {scenario.name}(self, {param_names}):
    """{scenario.description}
    
    Confidence: {scenario.confidence:.0%}
    """
    # Extract description if present
    if "description" in "{param_names}":
        # Last parameter is description, don't pass to function
        func_params = [{", ".join(f'"{p}"' for p in scenario.parameters[:-1])}]
        param_values = [{", ".join(scenario.parameters[:-1])}]
        result = {func_name}(*param_values)
    else:
        result = {func_name}({", ".join(scenario.parameters)})
    
    # Assertion based on expected behavior
    '''
        
        if scenario.expected_behavior == "raise":
            test_code += f'''with pytest.raises(Exception):
        {func_name}({", ".join(scenario.parameters)})'''
        else:
            test_code += "assert result is not None  # TODO: Add specific assertion"
        
        return test_code
    
    def _generate_property_based_tests(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate property-based tests using Hypothesis."""
        if "source_code" not in func_info or "ast_node" not in func_info:
            return []
        
        # Analyze function for property tests
        _, property_tests = self.parametrized_generator.analyze_function(
            func_info["ast_node"],
            func_info["source_code"]
        )
        
        # Filter by confidence
        _, property_tests = self.parametrized_generator.filter_by_confidence(min_confidence=0.7)
        
        # Prioritize tests
        _, property_tests = self.parametrized_generator.prioritize_tests()
        
        # Generate test code for each property test
        test_code_list = []
        for prop_test in property_tests[:5]:  # Limit to top 5 properties
            test_code = self._generate_property_test_code(prop_test, func_info)
            test_code_list.append(test_code)
        
        return test_code_list
    
    def _generate_property_test_code(self, prop_test: PropertyTest, func_info: Dict[str, Any]) -> str:
        """Generate Python test code for a property-based test using Hypothesis."""
        func_name = func_info["name"]
        
        # Build Hypothesis @given decorator
        test_code = f'''@given({prop_test.strategy_code})
def {prop_test.name}(self, {", ".join(p["name"] for p in func_info["parameters"])}):
    """{prop_test.description}
    
    Property: {prop_test.property_invariant}
    Confidence: {prop_test.confidence:.0%}
    """
    {prop_test.assertion_template}'''
        
        return test_code
