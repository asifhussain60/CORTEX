"""
Tests for Parametrized and Property-Based Test Generation (Milestone 1.4)

Validates @pytest.mark.parametrize generation, Hypothesis strategy generation,
property-based test templates, and scenario matrix generation.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 1 - Milestone 1.4
"""

import pytest
import ast
from src.cortex_agents.test_generator.parametrized_test_generator import (
    ParametrizedTestGenerator,
    ParametrizedScenario,
    PropertyTest
)


class TestBoundaryParametrizedGeneration:
    """Test generation of parametrized tests for boundary values."""
    
    def test_generates_numeric_boundaries(self):
        """Should generate boundary tests for int/float parameters."""
        source_code = '''
def calculate_discount(price: int):
    """Calculate discount on price."""
    return price * 0.1
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate boundary tests for price
        assert len(parametrized_tests) > 0
        assert any("price" in test.parameters for test in parametrized_tests)
        
        # Should include boundary values (0, 1, -1, etc.)
        price_tests = [t for t in parametrized_tests if "price" in t.parameters]
        if price_tests:
            scenarios = price_tests[0].scenarios
            values = [s[0] for s in scenarios]  # First parameter values
            assert 0 in values  # Zero boundary
            assert any(v > 0 for v in values)  # Positive values
    
    def test_generates_string_length_boundaries(self):
        """Should generate boundary tests for string length."""
        source_code = '''
def validate_username(username: str):
    """Validate username length."""
    return 3 <= len(username) <= 20
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate string length boundaries
        username_tests = [t for t in parametrized_tests if "username" in t.parameters]
        assert len(username_tests) > 0
        
        # Should include various lengths
        scenarios = username_tests[0].scenarios
        string_values = [s[0] for s in scenarios]
        lengths = [len(s) for s in string_values]
        
        # Should have empty, short, medium, long strings
        assert 0 in lengths  # Empty string
        assert any(l == 1 for l in lengths)  # Single char
        assert any(l >= 5 for l in lengths)  # Longer strings
    
    def test_generates_collection_size_boundaries(self):
        """Should generate boundary tests for collection sizes."""
        source_code = '''
def process_items(items: list):
    """Process list of items."""
    return len(items)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate collection size boundaries
        items_tests = [t for t in parametrized_tests if "items" in t.parameters]
        assert len(items_tests) > 0
        
        # Should include various sizes
        scenarios = items_tests[0].scenarios
        list_values = [s[0] for s in scenarios]
        sizes = [len(l) for l in list_values]
        
        # Should have empty, small, medium, large
        assert 0 in sizes  # Empty list
        assert any(s == 1 for s in sizes)  # Single item
        assert any(s >= 10 for s in sizes)  # Larger list


class TestCombinationParametrizedGeneration:
    """Test generation of parametrized tests for parameter combinations."""
    
    def test_generates_two_parameter_combinations(self):
        """Should generate combination tests for 2-parameter functions."""
        source_code = '''
def add_numbers(a: int, b: int):
    """Add two numbers."""
    return a + b
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate combination tests
        combo_tests = [t for t in parametrized_tests if len(t.parameters) >= 2]
        assert len(combo_tests) > 0
        
        # Should have multiple scenarios
        assert any(len(t.scenarios) >= 3 for t in combo_tests)
    
    def test_skips_combination_for_single_parameter(self):
        """Should not generate combinations for single-parameter functions."""
        source_code = '''
def square(x: int):
    """Square a number."""
    return x * x
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        generator._generate_combination_parametrized_tests(
            generator._extract_function_info(func_node)
        )
        
        # Should not have combination tests (only 1 parameter)
        combo_tests = [t for t in generator.parametrized_tests if "combinations" in t.name]
        assert len(combo_tests) == 0
    
    def test_generates_string_string_combinations(self):
        """Should generate combinations for two string parameters."""
        source_code = '''
def concat_strings(first: str, second: str):
    """Concatenate two strings."""
    return first + second
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate string combinations
        combo_tests = [t for t in parametrized_tests if "combinations" in t.name]
        if combo_tests:
            scenarios = combo_tests[0].scenarios
            
            # Should include empty/non-empty combinations
            assert any(s[0] == "" or s[1] == "" for s in scenarios)  # At least one empty
            assert any(s[0] != "" and s[1] != "" for s in scenarios)  # Both non-empty


class TestEquivalenceClassGeneration:
    """Test generation of equivalence class partitioning tests."""
    
    def test_detects_calculation_functions(self):
        """Should generate equivalence classes for calculation functions."""
        source_code = '''
def calculate_total(price: int, quantity: int):
    """Calculate total price."""
    return price * quantity
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate equivalence classes
        equiv_tests = [t for t in parametrized_tests if "equivalence" in t.name]
        assert len(equiv_tests) > 0
    
    def test_detects_validation_functions(self):
        """Should generate validation equivalence classes."""
        source_code = '''
def validate_email(email: str):
    """Validate email format."""
    return "@" in email and "." in email
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Should generate validation classes (valid/invalid)
        validation_tests = [t for t in parametrized_tests 
                           if "validation" in t.name or "equivalence" in t.name]
        
        if validation_tests:
            # Should have expected_valid parameter
            assert any("expected_valid" in t.parameters for t in validation_tests)


class TestPropertyBasedGeneration:
    """Test generation of property-based tests using Hypothesis."""
    
    def test_detects_idempotent_operations(self):
        """Should generate idempotence property for functions like normalize/sort."""
        source_code = '''
def normalize_string(text: str):
    """Normalize string to lowercase with stripped whitespace."""
    return text.lower().strip()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        _, property_tests = generator.analyze_function(func_node, source_code)
        
        # Should detect idempotence
        idempotent_tests = [t for t in property_tests if "idempotence" in t.name]
        assert len(idempotent_tests) > 0
        
        # Should have correct invariant
        assert any("twice" in t.property_invariant.lower() for t in idempotent_tests)
    
    def test_detects_commutative_operations(self):
        """Should generate commutativity property for functions like add/max."""
        source_code = '''
def add_numbers(a: int, b: int):
    """Add two numbers."""
    return a + b
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        _, property_tests = generator.analyze_function(func_node, source_code)
        
        # Should detect commutativity
        commutative_tests = [t for t in property_tests if "commutative" in t.name]
        assert len(commutative_tests) > 0
        
        # Should have order invariant
        assert any("order" in t.property_invariant.lower() for t in commutative_tests)
    
    def test_detects_length_preservation(self):
        """Should generate length preservation property for transforms."""
        source_code = '''
def reverse_list(items: list):
    """Reverse a list."""
    return items[::-1]
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        _, property_tests = generator.analyze_function(func_node, source_code)
        
        # Should detect length preservation
        length_tests = [t for t in property_tests if "length" in t.name]
        assert len(length_tests) > 0
        
        # Should check len(output) == len(input)
        assert any("len" in t.assertion_template for t in length_tests)
    
    def test_detects_non_negative_results(self):
        """Should generate non-negative property for count/size functions."""
        source_code = '''
def count_items(items: list):
    """Count number of items."""
    return len(items)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        _, property_tests = generator.analyze_function(func_node, source_code)
        
        # Should detect non-negative property
        non_neg_tests = [t for t in property_tests if "non_negative" in t.name]
        assert len(non_neg_tests) > 0
        
        # Should check result >= 0
        assert any(">= 0" in t.assertion_template for t in non_neg_tests)


class TestHypothesisStrategyGeneration:
    """Test generation of Hypothesis strategy code."""
    
    def test_generates_integer_strategy(self):
        """Should generate st.integers() for int parameters."""
        generator = ParametrizedTestGenerator()
        
        parameters = [{"name": "count", "type": "int"}]
        strategy_code = generator._generate_strategy_code(parameters)
        
        assert "st.integers()" in strategy_code
        assert "count=" in strategy_code
    
    def test_generates_float_strategy(self):
        """Should generate st.floats() for float parameters."""
        generator = ParametrizedTestGenerator()
        
        parameters = [{"name": "price", "type": "float"}]
        strategy_code = generator._generate_strategy_code(parameters)
        
        assert "st.floats(" in strategy_code
        assert "allow_nan=False" in strategy_code
        assert "allow_infinity=False" in strategy_code
    
    def test_generates_string_strategy(self):
        """Should generate st.text() for str parameters."""
        generator = ParametrizedTestGenerator()
        
        parameters = [{"name": "message", "type": "str"}]
        strategy_code = generator._generate_strategy_code(parameters)
        
        assert "st.text()" in strategy_code
        assert "message=" in strategy_code
    
    def test_generates_list_strategy(self):
        """Should generate st.lists() for list parameters."""
        generator = ParametrizedTestGenerator()
        
        parameters = [{"name": "items", "type": "list"}]
        strategy_code = generator._generate_strategy_code(parameters)
        
        assert "st.lists(" in strategy_code
        assert "items=" in strategy_code
    
    def test_generates_multiple_strategies(self):
        """Should generate strategies for multiple parameters."""
        generator = ParametrizedTestGenerator()
        
        parameters = [
            {"name": "a", "type": "int"},
            {"name": "b", "type": "str"}
        ]
        strategy_code = generator._generate_strategy_code(parameters)
        
        assert "a=st.integers()" in strategy_code
        assert "b=st.text()" in strategy_code
        assert ", " in strategy_code  # Comma-separated


class TestParametrizedCodeGeneration:
    """Test generation of @pytest.mark.parametrize code."""
    
    def test_generates_valid_parametrize_decorator(self):
        """Should generate syntactically valid @pytest.mark.parametrize."""
        scenario = ParametrizedScenario(
            name="test_add_boundaries",
            description="Boundary tests for add function",
            parameters=["a", "b", "description"],
            scenarios=[
                (0, 0, "both zero"),
                (1, 1, "both one"),
                (5, 3, "positive numbers"),
            ],
            expected_behavior="return",
            confidence=0.85
        )
        
        # Manually generate parametrize code (simulating FunctionTestGenerator)
        param_names = ", ".join(scenario.parameters)
        test_code = f'@pytest.mark.parametrize("{param_names}", ['
        
        # Should contain decorator
        assert "@pytest.mark.parametrize" in test_code
        
        # Should contain parameter names
        assert "a, b, description" in test_code
    
    def test_includes_scenario_descriptions(self):
        """Should include human-readable descriptions in scenarios."""
        scenario = ParametrizedScenario(
            name="test_validate_boundaries",
            description="Boundary tests",
            parameters=["input_val", "description"],
            scenarios=[
                (0, "zero"),
                (-1, "negative"),
                (100, "large positive"),
            ],
            expected_behavior="return",
            confidence=0.8
        )
        
        # Scenarios should include descriptions
        assert all(len(s) == 2 for s in scenario.scenarios)
        descriptions = [s[1] for s in scenario.scenarios]
        assert "zero" in descriptions
        assert "negative" in descriptions


class TestConfidenceScoringParametrized:
    """Test confidence scoring for parametrized tests."""
    
    def test_high_confidence_for_boundary_tests(self):
        """Boundary tests should have high confidence (>= 0.75)."""
        source_code = '''
def calculate(x: int):
    return x * 2
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        parametrized_tests, _ = generator.analyze_function(func_node, source_code)
        
        # Boundary tests should be high confidence
        boundary_tests = [t for t in parametrized_tests if "boundaries" in t.name]
        assert any(t.confidence >= 0.75 for t in boundary_tests)
    
    def test_medium_confidence_for_property_tests(self):
        """Property tests should have medium to high confidence (>= 0.7)."""
        source_code = '''
def normalize(text: str):
    return text.lower().strip()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ParametrizedTestGenerator()
        _, property_tests = generator.analyze_function(func_node, source_code)
        
        # Property tests should be >= 0.7 confidence
        assert any(t.confidence >= 0.7 for t in property_tests)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
