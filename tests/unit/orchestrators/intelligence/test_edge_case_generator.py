"""
Tests for EdgeCaseGenerator.

Validates generation of boundary, null, empty collection, and overflow tests.
"""

import pytest
from typing import List, Any
from cortex.orchestrators.intelligence.edge_case_generator import (
    EdgeCaseGenerator,
    EdgeCase,
    EdgeCaseType,
    ParameterInfo,
)


class TestEdgeCaseGeneratorInitialization:
    """Test EdgeCaseGenerator initialization."""

    def test_generator_initialization_default(self):
        """Test generator initializes with default configuration."""
        generator = EdgeCaseGenerator()
        
        assert generator is not None
        assert generator.include_boundary_tests is True
        assert generator.include_null_tests is True
        assert generator.include_overflow_tests is True

    def test_generator_initialization_custom_config(self):
        """Test generator initializes with custom configuration."""
        generator = EdgeCaseGenerator(
            include_boundary_tests=False,
            include_null_tests=True,
            include_overflow_tests=False
        )
        
        assert generator.include_boundary_tests is False
        assert generator.include_null_tests is True
        assert generator.include_overflow_tests is False


class TestGenerateBoundaryTests:
    """Test boundary value generation."""

    def test_generate_boundary_numeric_parameter(self):
        """Test boundary tests for numeric parameters."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="age",
            type_hint="int",
            min_value=0,
            max_value=120,
        )
        
        edge_cases = generator.generate_boundary_tests(param)
        
        assert len(edge_cases) > 0
        # Should generate: min, min-1, max, max+1, 0
        values = {case.test_value for case in edge_cases}
        assert -1 in values  # min-1
        assert 0 in values   # min
        assert 120 in values # max
        assert 121 in values # max+1

    def test_generate_boundary_string_parameter(self):
        """Test boundary tests for string parameters."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="username",
            type_hint="str",
            min_length=3,
            max_length=20,
        )
        
        edge_cases = generator.generate_boundary_tests(param)
        
        assert len(edge_cases) > 0
        # Should test: min length, max length, empty, too long
        lengths = {len(case.test_value) for case in edge_cases if isinstance(case.test_value, str)}
        assert 0 in lengths  # Empty string
        assert 3 in lengths  # Min length
        assert 20 in lengths # Max length
        assert 21 in lengths # Max+1 length

    def test_generate_boundary_disabled(self):
        """Test boundary generation can be disabled."""
        generator = EdgeCaseGenerator(include_boundary_tests=False)
        param = ParameterInfo(
            name="value",
            type_hint="int",
            min_value=0,
            max_value=100,
        )
        
        edge_cases = generator.generate_boundary_tests(param)
        
        assert len(edge_cases) == 0


class TestGenerateNullTests:
    """Test null/None value generation."""

    def test_generate_null_optional_parameter(self):
        """Test null tests for optional parameters."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="email",
            type_hint="Optional[str]",
            nullable=True,
        )
        
        edge_cases = generator.generate_null_tests(param)
        
        assert len(edge_cases) > 0
        assert any(case.test_value is None for case in edge_cases)
        assert any(case.type == EdgeCaseType.NULL for case in edge_cases)

    def test_generate_null_required_parameter(self):
        """Test null tests for required parameters (should generate to catch bugs)."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="user_id",
            type_hint="str",
            nullable=False,
        )
        
        edge_cases = generator.generate_null_tests(param)
        
        # Should still generate None test to verify proper validation
        assert len(edge_cases) > 0
        assert any(case.test_value is None for case in edge_cases)
        assert any("should raise" in case.description.lower() for case in edge_cases)

    def test_generate_null_disabled(self):
        """Test null generation can be disabled."""
        generator = EdgeCaseGenerator(include_null_tests=False)
        param = ParameterInfo(
            name="value",
            type_hint="Optional[str]",
            nullable=True,
        )
        
        edge_cases = generator.generate_null_tests(param)
        
        assert len(edge_cases) == 0


class TestGenerateEmptyCollectionTests:
    """Test empty collection generation."""

    def test_generate_empty_list(self):
        """Test empty list generation."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="items",
            type_hint="List[str]",
        )
        
        edge_cases = generator.generate_empty_collection_tests(param)
        
        assert len(edge_cases) > 0
        assert any(case.test_value == [] for case in edge_cases)
        assert any(case.type == EdgeCaseType.EMPTY_COLLECTION for case in edge_cases)

    def test_generate_empty_dict(self):
        """Test empty dict generation."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="config",
            type_hint="Dict[str, Any]",
        )
        
        edge_cases = generator.generate_empty_collection_tests(param)
        
        assert len(edge_cases) > 0
        assert any(case.test_value == {} for case in edge_cases)

    def test_generate_single_item_collection(self):
        """Test single-item collection generation."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="tags",
            type_hint="List[str]",
        )
        
        edge_cases = generator.generate_empty_collection_tests(param)
        
        # Should generate both empty and single-item
        assert len(edge_cases) >= 2
        assert any(case.test_value == [] for case in edge_cases)
        assert any(isinstance(case.test_value, list) and len(case.test_value) == 1 
                   for case in edge_cases)


class TestGenerateOverflowTests:
    """Test overflow/underflow generation."""

    def test_generate_integer_overflow(self):
        """Test integer overflow tests."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="count",
            type_hint="int",
        )
        
        edge_cases = generator.generate_overflow_tests(param)
        
        assert len(edge_cases) > 0
        values = {case.test_value for case in edge_cases}
        # Should test: max int, min int, large values
        assert 2**31 - 1 in values or 2**63 - 1 in values  # Max int32 or int64
        assert -(2**31) in values or -(2**63) in values     # Min int32 or int64

    def test_generate_string_overflow(self):
        """Test string overflow tests (very long strings)."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="description",
            type_hint="str",
        )
        
        edge_cases = generator.generate_overflow_tests(param)
        
        assert len(edge_cases) > 0
        # Should generate very long string
        assert any(len(case.test_value) > 10000 for case in edge_cases 
                   if isinstance(case.test_value, str))

    def test_generate_overflow_disabled(self):
        """Test overflow generation can be disabled."""
        generator = EdgeCaseGenerator(include_overflow_tests=False)
        param = ParameterInfo(
            name="value",
            type_hint="int",
        )
        
        edge_cases = generator.generate_overflow_tests(param)
        
        assert len(edge_cases) == 0


class TestGenerateForParameter:
    """Test comprehensive parameter analysis."""

    def test_generate_for_integer_parameter(self):
        """Test comprehensive edge cases for integer parameter."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="age",
            type_hint="int",
            min_value=0,
            max_value=120,
        )
        
        edge_cases = generator.generate_for_parameter(param)
        
        # Should include boundary, null, and overflow tests
        types_found = {case.type for case in edge_cases}
        assert EdgeCaseType.BOUNDARY in types_found
        assert EdgeCaseType.NULL in types_found or EdgeCaseType.OVERFLOW in types_found

    def test_generate_for_list_parameter(self):
        """Test comprehensive edge cases for list parameter."""
        generator = EdgeCaseGenerator()
        param = ParameterInfo(
            name="items",
            type_hint="List[str]",
        )
        
        edge_cases = generator.generate_for_parameter(param)
        
        # Should include empty collection and null tests
        types_found = {case.type for case in edge_cases}
        assert EdgeCaseType.EMPTY_COLLECTION in types_found
        assert EdgeCaseType.NULL in types_found

    def test_generate_respects_configuration(self):
        """Test generation respects configuration flags."""
        generator = EdgeCaseGenerator(
            include_boundary_tests=True,
            include_null_tests=False,
            include_overflow_tests=False,
        )
        param = ParameterInfo(
            name="value",
            type_hint="int",
            min_value=0,
            max_value=100,
        )
        
        edge_cases = generator.generate_for_parameter(param)
        
        # Should only include boundary tests
        types_found = {case.type for case in edge_cases}
        assert EdgeCaseType.BOUNDARY in types_found
        assert EdgeCaseType.NULL not in types_found
        assert EdgeCaseType.OVERFLOW not in types_found
