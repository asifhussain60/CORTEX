"""
Parametrized and Property-Based Test Generation for TDD Mastery

Generates @pytest.mark.parametrize tests and Hypothesis property-based tests
for comprehensive scenario coverage.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 1 - Milestone 1.4
"""

import ast
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParametrizedScenario:
    """Represents a parametrized test scenario."""
    name: str
    description: str
    parameters: List[str]  # Parameter names
    scenarios: List[Tuple[Any, ...]]  # Test case values
    expected_behavior: str  # "return", "raise", "mutate"
    confidence: float = 0.8


@dataclass
class PropertyTest:
    """Represents a property-based test."""
    name: str
    description: str
    property_invariant: str  # Description of the invariant
    strategy_code: str  # Hypothesis strategy code
    assertion_template: str
    confidence: float = 0.8


class ParametrizedTestGenerator:
    """Generates parametrized and property-based tests."""
    
    def __init__(self):
        """Initialize parametrized test generator."""
        self.parametrized_tests: List[ParametrizedScenario] = []
        self.property_tests: List[PropertyTest] = []
    
    def analyze_function(self, func_node: ast.FunctionDef, source_code: str) -> Tuple[List[ParametrizedScenario], List[PropertyTest]]:
        """
        Analyze function and generate parametrized/property tests.
        
        Args:
            func_node: AST node for the function
            source_code: Source code containing the function
            
        Returns:
            Tuple of (parametrized scenarios, property tests)
        """
        self.parametrized_tests = []
        self.property_tests = []
        
        # Extract function metadata
        func_info = self._extract_function_info(func_node)
        
        # Generate parametrized tests for common patterns
        self._generate_boundary_parametrized_tests(func_info)
        self._generate_combination_parametrized_tests(func_info)
        self._generate_equivalence_class_tests(func_info)
        
        # Generate property-based tests
        self._generate_property_tests(func_info)
        
        return self.parametrized_tests, self.property_tests
    
    def _extract_function_info(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract metadata from function node."""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": None,
            }
            
            # Extract type annotation
            if arg.annotation:
                param_info["type"] = self._get_type_name(arg.annotation)
            
            parameters.append(param_info)
        
        # Extract return type
        return_type = None
        if func_node.returns:
            return_type = self._get_type_name(func_node.returns)
        
        return {
            "name": func_node.name,
            "parameters": parameters,
            "return_type": return_type,
            "docstring": ast.get_docstring(func_node),
            "ast_node": func_node,
        }
    
    def _get_type_name(self, node: ast.AST) -> str:
        """Extract type name from annotation node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            base = self._get_type_name(node.value)
            arg = self._get_type_name(node.slice)
            return f"{base}[{arg}]"
        else:
            return ast.unparse(node)
    
    def _generate_boundary_parametrized_tests(self, func_info: Dict[str, Any]):
        """Generate parametrized tests for boundary values."""
        func_name = func_info["name"]
        
        for param in func_info["parameters"]:
            param_name = param["name"]
            param_type = param.get("type")
            
            # Numeric boundaries
            if param_type in ["int", "float"]:
                scenarios = [
                    (0, "zero"),
                    (1, "one"),
                    (-1, "negative one"),
                    (100, "normal positive"),
                    (-100, "normal negative"),
                ]
                
                if param_type == "float":
                    scenarios.extend([
                        (0.0, "float zero"),
                        (0.1, "small positive"),
                        (-0.1, "small negative"),
                        (3.14159, "pi"),
                    ])
                
                self.parametrized_tests.append(ParametrizedScenario(
                    name=f"test_{func_name}_{param_name}_boundaries",
                    description=f"Boundary value testing for {param_name}",
                    parameters=[param_name, "description"],
                    scenarios=scenarios,
                    expected_behavior="return",
                    confidence=0.85
                ))
            
            # String length boundaries
            elif param_type == "str":
                scenarios = [
                    ("", "empty"),
                    ("a", "single char"),
                    ("ab", "two chars"),
                    ("hello", "normal length"),
                    ("x" * 100, "long string"),
                    ("x" * 1000, "very long string"),
                ]
                
                self.parametrized_tests.append(ParametrizedScenario(
                    name=f"test_{func_name}_{param_name}_lengths",
                    description=f"String length boundary testing for {param_name}",
                    parameters=[param_name, "description"],
                    scenarios=scenarios,
                    expected_behavior="return",
                    confidence=0.8
                ))
            
            # Collection size boundaries
            elif param_type in ["list", "List", "dict", "Dict"]:
                if "list" in param_type.lower():
                    scenarios = [
                        ([], "empty"),
                        ([1], "one item"),
                        ([1, 2], "two items"),
                        (list(range(10)), "ten items"),
                        (list(range(100)), "hundred items"),
                    ]
                else:  # dict
                    scenarios = [
                        ({}, "empty"),
                        ({"a": 1}, "one item"),
                        ({"a": 1, "b": 2}, "two items"),
                        ({str(i): i for i in range(10)}, "ten items"),
                    ]
                
                self.parametrized_tests.append(ParametrizedScenario(
                    name=f"test_{func_name}_{param_name}_sizes",
                    description=f"Collection size boundary testing for {param_name}",
                    parameters=[param_name, "description"],
                    scenarios=scenarios,
                    expected_behavior="return",
                    confidence=0.8
                ))
    
    def _generate_combination_parametrized_tests(self, func_info: Dict[str, Any]):
        """Generate parametrized tests for parameter combinations."""
        func_name = func_info["name"]
        parameters = func_info["parameters"]
        
        # Only generate combinations for functions with 2-3 parameters
        if len(parameters) < 2 or len(parameters) > 3:
            return
        
        # Generate small set of representative combinations
        if len(parameters) == 2:
            param1, param2 = parameters[0], parameters[1]
            
            # Generate scenarios based on types
            scenarios = self._generate_2param_combinations(param1, param2)
            
            if scenarios:
                self.parametrized_tests.append(ParametrizedScenario(
                    name=f"test_{func_name}_combinations",
                    description=f"Parameter combination testing",
                    parameters=[param1["name"], param2["name"], "description"],
                    scenarios=scenarios,
                    expected_behavior="return",
                    confidence=0.75
                ))
    
    def _generate_2param_combinations(self, param1: Dict[str, Any], param2: Dict[str, Any]) -> List[Tuple[Any, ...]]:
        """Generate test combinations for 2 parameters."""
        type1 = param1.get("type", "Any")
        type2 = param2.get("type", "Any")
        
        scenarios = []
        
        # Numeric + Numeric
        if type1 in ["int", "float"] and type2 in ["int", "float"]:
            scenarios = [
                (0, 0, "both zero"),
                (1, 1, "both one"),
                (5, 3, "positive numbers"),
                (-5, 3, "mixed signs"),
                (10, -2, "reverse mixed signs"),
            ]
        
        # String + String
        elif type1 == "str" and type2 == "str":
            scenarios = [
                ("", "", "both empty"),
                ("hello", "", "first non-empty"),
                ("", "world", "second non-empty"),
                ("hello", "world", "both non-empty"),
                ("test", "test", "identical strings"),
            ]
        
        # String + Int (common pattern: string formatting, substring, etc.)
        elif (type1 == "str" and type2 in ["int", "float"]) or (type2 == "str" and type1 in ["int", "float"]):
            scenarios = [
                ("test", 0, "string with zero"),
                ("test", 1, "string with one"),
                ("test", 5, "string with positive"),
                ("", 0, "empty string with zero"),
                ("hello", -1, "string with negative"),
            ]
        
        # Collection + Any (filtering, searching, etc.)
        elif "list" in type1.lower() or "dict" in type1.lower():
            if "list" in type1.lower():
                scenarios = [
                    ([], "any", "empty list"),
                    ([1, 2, 3], 2, "list with target"),
                    ([1, 2, 3], 5, "list without target"),
                ]
        
        return scenarios
    
    def _generate_equivalence_class_tests(self, func_info: Dict[str, Any]):
        """Generate parametrized tests for equivalence classes."""
        func_name = func_info["name"]
        
        # Detect domain from function name
        if any(word in func_name.lower() for word in ["calculate", "compute", "eval"]):
            # Mathematical function - test equivalence classes
            scenarios = [
                (10, 20, "normal range"),
                (0, 0, "boundary zeros"),
                (1000, 2000, "large values"),
                (-10, -20, "negative range"),
            ]
            
            self.parametrized_tests.append(ParametrizedScenario(
                name=f"test_{func_name}_equivalence_classes",
                description=f"Equivalence class partitioning",
                parameters=["input1", "input2", "description"],
                scenarios=scenarios,
                expected_behavior="return",
                confidence=0.7
            ))
        
        elif any(word in func_name.lower() for word in ["validate", "check", "verify"]):
            # Validation function - test valid/invalid classes
            param = func_info["parameters"][0] if func_info["parameters"] else None
            
            if param:
                param_name = param["name"]
                param_type = param.get("type", "str")
                
                if param_type == "str":
                    scenarios = [
                        ("valid@example.com", True, "valid input"),
                        ("invalid", False, "invalid format"),
                        ("", False, "empty"),
                        ("@example.com", False, "missing prefix"),
                    ]
                    
                    self.parametrized_tests.append(ParametrizedScenario(
                        name=f"test_{func_name}_validation_classes",
                        description=f"Validation equivalence classes",
                        parameters=[param_name, "expected_valid", "description"],
                        scenarios=scenarios,
                        expected_behavior="return",
                        confidence=0.8
                    ))
    
    def _generate_property_tests(self, func_info: Dict[str, Any]):
        """Generate property-based tests using Hypothesis."""
        func_name = func_info["name"]
        return_type = func_info.get("return_type")
        
        # Property 1: Idempotence (f(f(x)) == f(x))
        if self._is_idempotent_candidate(func_info):
            self.property_tests.append(PropertyTest(
                name=f"test_{func_name}_idempotence_property",
                description=f"Property: {func_name} is idempotent",
                property_invariant="Applying function twice yields same result as once",
                strategy_code=self._generate_strategy_code(func_info["parameters"]),
                assertion_template=f"assert {func_name}({func_name}(x)) == {func_name}(x)",
                confidence=0.75
            ))
        
        # Property 2: Commutative (f(x, y) == f(y, x))
        if self._is_commutative_candidate(func_info):
            params = func_info["parameters"]
            if len(params) == 2:
                p1, p2 = params[0]["name"], params[1]["name"]
                self.property_tests.append(PropertyTest(
                    name=f"test_{func_name}_commutativity_property",
                    description=f"Property: {func_name} is commutative",
                    property_invariant="Order of arguments doesn't matter",
                    strategy_code=self._generate_strategy_code(params),
                    assertion_template=f"assert {func_name}({p1}, {p2}) == {func_name}({p2}, {p1})",
                    confidence=0.7
                ))
        
        # Property 3: Length preservation (len(f(x)) == len(x))
        if self._is_length_preserving_candidate(func_info):
            param = func_info["parameters"][0] if func_info["parameters"] else None
            if param:
                self.property_tests.append(PropertyTest(
                    name=f"test_{func_name}_length_preservation_property",
                    description=f"Property: {func_name} preserves collection length",
                    property_invariant="Output length equals input length",
                    strategy_code="st.lists(st.integers())",
                    assertion_template=f"assert len({func_name}({param['name']})) == len({param['name']})",
                    confidence=0.8
                ))
        
        # Property 4: Type preservation
        if return_type and func_info["parameters"]:
            param = func_info["parameters"][0]
            if param.get("type") == return_type:
                self.property_tests.append(PropertyTest(
                    name=f"test_{func_name}_type_preservation_property",
                    description=f"Property: {func_name} preserves type",
                    property_invariant="Output type matches input type",
                    strategy_code=self._generate_strategy_code([param]),
                    assertion_template=f"assert type({func_name}({param['name']})) == type({param['name']})",
                    confidence=0.75
                ))
        
        # Property 5: Non-negative result (for functions that compute sizes, counts, etc.)
        if self._is_non_negative_candidate(func_info):
            self.property_tests.append(PropertyTest(
                name=f"test_{func_name}_non_negative_property",
                description=f"Property: {func_name} returns non-negative value",
                property_invariant="Result is always >= 0",
                strategy_code=self._generate_strategy_code(func_info["parameters"]),
                assertion_template=f"assert {func_name}(...) >= 0",
                confidence=0.85
            ))
    
    def _is_idempotent_candidate(self, func_info: Dict[str, Any]) -> bool:
        """Check if function is likely idempotent."""
        func_name = func_info["name"].lower()
        
        # Common idempotent operations
        idempotent_patterns = [
            "normalize", "clean", "trim", "strip", "lower", "upper",
            "sort", "deduplicate", "unique", "abs", "round"
        ]
        
        return any(pattern in func_name for pattern in idempotent_patterns)
    
    def _is_commutative_candidate(self, func_info: Dict[str, Any]) -> bool:
        """Check if function is likely commutative."""
        func_name = func_info["name"].lower()
        params = func_info["parameters"]
        
        # Need exactly 2 parameters of same type
        if len(params) != 2:
            return False
        
        if params[0].get("type") != params[1].get("type"):
            return False
        
        # Common commutative operations
        commutative_patterns = [
            "add", "sum", "multiply", "product", "max", "min",
            "gcd", "lcm", "intersect", "union"
        ]
        
        return any(pattern in func_name for pattern in commutative_patterns)
    
    def _is_length_preserving_candidate(self, func_info: Dict[str, Any]) -> bool:
        """Check if function is likely to preserve collection length."""
        func_name = func_info["name"].lower()
        
        # Common length-preserving operations
        length_preserving_patterns = [
            "transform", "map", "convert", "encode", "decode",
            "reverse", "shuffle", "rotate", "sort"
        ]
        
        # Check if it operates on collections
        has_collection_param = any(
            p.get("type") in ["list", "List", "tuple", "Tuple"]
            for p in func_info["parameters"]
        )
        
        return has_collection_param and any(pattern in func_name for pattern in length_preserving_patterns)
    
    def _is_non_negative_candidate(self, func_info: Dict[str, Any]) -> bool:
        """Check if function should return non-negative values."""
        func_name = func_info["name"].lower()
        
        # Functions that typically return non-negative values
        non_negative_patterns = [
            "count", "size", "length", "total", "sum",
            "distance", "duration", "age", "quantity"
        ]
        
        return any(pattern in func_name for pattern in non_negative_patterns)
    
    def _generate_strategy_code(self, parameters: List[Dict[str, Any]]) -> str:
        """Generate Hypothesis strategy code for parameters."""
        if not parameters:
            return ""
        
        strategies = []
        
        for param in parameters:
            param_type = param.get("type", "Any")
            param_name = param["name"]
            
            if param_type == "int":
                strategies.append(f"{param_name}=st.integers()")
            elif param_type == "float":
                strategies.append(f"{param_name}=st.floats(allow_nan=False, allow_infinity=False)")
            elif param_type == "str":
                strategies.append(f"{param_name}=st.text()")
            elif param_type in ["list", "List"]:
                strategies.append(f"{param_name}=st.lists(st.integers())")
            elif param_type in ["dict", "Dict"]:
                strategies.append(f"{param_name}=st.dictionaries(st.text(), st.integers())")
            elif param_type == "bool":
                strategies.append(f"{param_name}=st.booleans()")
            else:
                strategies.append(f"{param_name}=st.none()")  # Fallback
        
        return ", ".join(strategies)
    
    def filter_by_confidence(self, min_confidence: float = 0.7) -> Tuple[List[ParametrizedScenario], List[PropertyTest]]:
        """Filter tests by confidence threshold."""
        filtered_parametrized = [t for t in self.parametrized_tests if t.confidence >= min_confidence]
        filtered_property = [t for t in self.property_tests if t.confidence >= min_confidence]
        
        return filtered_parametrized, filtered_property
    
    def prioritize_tests(self) -> Tuple[List[ParametrizedScenario], List[PropertyTest]]:
        """Sort tests by priority (confidence)."""
        sorted_parametrized = sorted(self.parametrized_tests, key=lambda t: t.confidence, reverse=True)
        sorted_property = sorted(self.property_tests, key=lambda t: t.confidence, reverse=True)
        
        return sorted_parametrized, sorted_property
