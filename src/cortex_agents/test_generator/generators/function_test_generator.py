"""Function test generation with Edge Case Intelligence and Domain Knowledge."""

import ast
from typing import Dict, Any, List
from ..templates import TemplateManager
from ..edge_case_analyzer import EdgeCaseAnalyzer, EdgeCase
from ..domain_knowledge_integrator import DomainKnowledgeIntegrator


class FunctionTestGenerator:
    """Generates test code for functions with intelligent edge case detection and smart assertions."""
    
    def __init__(self, template_manager: TemplateManager):
        """Initialize with template manager."""
        self.templates = template_manager
        self.edge_analyzer = EdgeCaseAnalyzer()
        self.domain_knowledge = DomainKnowledgeIntegrator()
    
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
        
        # Error handling test
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
