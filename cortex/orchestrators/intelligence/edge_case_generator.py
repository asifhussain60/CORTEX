"""
Edge Case Generator for boundary and extreme value testing.

Generates test cases for:
- Boundary values (min/max, off-by-one)
- Null/None values
- Empty collections
- Overflow/underflow conditions

Part of WAVE-2 Stage 3: Intelligent Test Generation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class EdgeCaseType(Enum):
    """Types of edge cases."""
    
    BOUNDARY = "boundary"
    NULL = "null"
    EMPTY_COLLECTION = "empty_collection"
    OVERFLOW = "overflow"


@dataclass
class ParameterInfo:
    """Information about a function parameter."""
    
    name: str
    type_hint: str
    nullable: bool = False
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


@dataclass
class EdgeCase:
    """Represents an edge case test."""
    
    type: EdgeCaseType
    parameter_name: str
    test_value: Any
    description: str
    expected_behavior: str = "should handle gracefully"


class EdgeCaseGenerator:
    """
    Generates edge case tests for function parameters.
    
    Automatically creates test cases for boundary conditions,
    null values, empty collections, and overflow scenarios.
    
    Args:
        include_boundary_tests: Generate boundary value tests (default True)
        include_null_tests: Generate null/None tests (default True)
        include_overflow_tests: Generate overflow tests (default True)
    """
    
    def __init__(
        self,
        include_boundary_tests: bool = True,
        include_null_tests: bool = True,
        include_overflow_tests: bool = True,
    ) -> None:
        """Initialize EdgeCaseGenerator with configuration."""
        self.include_boundary_tests = include_boundary_tests
        self.include_null_tests = include_null_tests
        self.include_overflow_tests = include_overflow_tests
    
    def generate_boundary_tests(self, param: ParameterInfo) -> List[EdgeCase]:
        """
        Generate boundary value tests.
        
        For numeric types: min, min-1, max, max+1, zero
        For strings: empty, min length, max length, max+1 length
        For collections: empty, single item, max size
        
        Args:
            param: Parameter information
            
        Returns:
            List of boundary edge cases
        """
        if not self.include_boundary_tests:
            return []
        
        edge_cases = []
        
        # Numeric boundaries
        if param.type_hint in ["int", "float", "Integer"]:
            if param.min_value is not None and param.max_value is not None:
                # Min boundary
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value=param.min_value,
                    description=f"{param.name} at minimum value ({param.min_value})",
                    expected_behavior="should accept minimum value"
                ))
                
                # Min - 1 (below boundary)
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value=param.min_value - 1,
                    description=f"{param.name} below minimum ({param.min_value - 1})",
                    expected_behavior="should reject or handle boundary violation"
                ))
                
                # Max boundary
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value=param.max_value,
                    description=f"{param.name} at maximum value ({param.max_value})",
                    expected_behavior="should accept maximum value"
                ))
                
                # Max + 1 (above boundary)
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value=param.max_value + 1,
                    description=f"{param.name} above maximum ({param.max_value + 1})",
                    expected_behavior="should reject or handle boundary violation"
                ))
        
        # String length boundaries
        if "str" in param.type_hint.lower():
            if param.min_length is not None and param.max_length is not None:
                # Empty string
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value="",
                    description=f"{param.name} with empty string",
                    expected_behavior="should handle empty string"
                ))
                
                # Min length
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value="x" * param.min_length,
                    description=f"{param.name} at minimum length ({param.min_length})",
                    expected_behavior="should accept minimum length"
                ))
                
                # Max length
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value="x" * param.max_length,
                    description=f"{param.name} at maximum length ({param.max_length})",
                    expected_behavior="should accept maximum length"
                ))
                
                # Max + 1 length
                edge_cases.append(EdgeCase(
                    type=EdgeCaseType.BOUNDARY,
                    parameter_name=param.name,
                    test_value="x" * (param.max_length + 1),
                    description=f"{param.name} above maximum length ({param.max_length + 1})",
                    expected_behavior="should reject or truncate"
                ))
        
        return edge_cases
    
    def generate_null_tests(self, param: ParameterInfo) -> List[EdgeCase]:
        """
        Generate null/None value tests.
        
        Tests how functions handle None values for both
        nullable and non-nullable parameters.
        
        Args:
            param: Parameter information
            
        Returns:
            List of null edge cases
        """
        if not self.include_null_tests:
            return []
        
        edge_cases = []
        
        if param.nullable:
            # Parameter accepts None - test it works correctly
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.NULL,
                parameter_name=param.name,
                test_value=None,
                description=f"{param.name} with None value (nullable parameter)",
                expected_behavior="should handle None gracefully"
            ))
        else:
            # Parameter doesn't accept None - test validation
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.NULL,
                parameter_name=param.name,
                test_value=None,
                description=f"{param.name} with None value (should raise error)",
                expected_behavior="should raise TypeError or ValueError"
            ))
        
        return edge_cases
    
    def generate_empty_collection_tests(self, param: ParameterInfo) -> List[EdgeCase]:
        """
        Generate empty collection tests.
        
        Tests empty lists, dicts, sets, and single-item collections
        to ensure proper handling of edge cases.
        
        Args:
            param: Parameter information
            
        Returns:
            List of empty collection edge cases
        """
        edge_cases = []
        
        # List/array types
        if "List" in param.type_hint or "list" in param.type_hint:
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.EMPTY_COLLECTION,
                parameter_name=param.name,
                test_value=[],
                description=f"{param.name} with empty list",
                expected_behavior="should handle empty list"
            ))
            
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.EMPTY_COLLECTION,
                parameter_name=param.name,
                test_value=["single_item"],
                description=f"{param.name} with single-item list",
                expected_behavior="should handle single item"
            ))
        
        # Dict types
        if "Dict" in param.type_hint or "dict" in param.type_hint:
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.EMPTY_COLLECTION,
                parameter_name=param.name,
                test_value={},
                description=f"{param.name} with empty dict",
                expected_behavior="should handle empty dict"
            ))
        
        return edge_cases
    
    def generate_overflow_tests(self, param: ParameterInfo) -> List[EdgeCase]:
        """
        Generate overflow/underflow tests.
        
        Tests extreme values like max int, min int, very long strings,
        and large collections.
        
        Args:
            param: Parameter information
            
        Returns:
            List of overflow edge cases
        """
        if not self.include_overflow_tests:
            return []
        
        edge_cases = []
        
        # Integer overflow
        if param.type_hint == "int":
            # 32-bit max
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.OVERFLOW,
                parameter_name=param.name,
                test_value=2**31 - 1,
                description=f"{param.name} at 32-bit max int",
                expected_behavior="should handle large integers"
            ))
            
            # 32-bit min
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.OVERFLOW,
                parameter_name=param.name,
                test_value=-(2**31),
                description=f"{param.name} at 32-bit min int",
                expected_behavior="should handle large negative integers"
            ))
            
            # 64-bit max
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.OVERFLOW,
                parameter_name=param.name,
                test_value=2**63 - 1,
                description=f"{param.name} at 64-bit max int",
                expected_behavior="should handle very large integers"
            ))
            
            # 64-bit min
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.OVERFLOW,
                parameter_name=param.name,
                test_value=-(2**63),
                description=f"{param.name} at 64-bit min int",
                expected_behavior="should handle very large negative integers"
            ))
        
        # String overflow (very long string)
        if "str" in param.type_hint.lower():
            edge_cases.append(EdgeCase(
                type=EdgeCaseType.OVERFLOW,
                parameter_name=param.name,
                test_value="x" * 100000,  # 100k character string
                description=f"{param.name} with very long string (100k chars)",
                expected_behavior="should handle or reject oversized strings"
            ))
        
        return edge_cases
    
    def generate_for_parameter(self, param: ParameterInfo) -> List[EdgeCase]:
        """
        Generate all applicable edge cases for a parameter.
        
        Combines boundary, null, empty collection, and overflow tests
        based on parameter type and configuration.
        
        Args:
            param: Parameter information
            
        Returns:
            List of all edge cases for the parameter
        """
        edge_cases = []
        
        # Add boundary tests
        edge_cases.extend(self.generate_boundary_tests(param))
        
        # Add null tests
        edge_cases.extend(self.generate_null_tests(param))
        
        # Add empty collection tests
        edge_cases.extend(self.generate_empty_collection_tests(param))
        
        # Add overflow tests
        edge_cases.extend(self.generate_overflow_tests(param))
        
        return edge_cases
