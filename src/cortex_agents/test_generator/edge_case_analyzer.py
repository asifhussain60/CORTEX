"""
Edge Case Intelligence for TDD Test Generation

Analyzes function signatures, docstrings, and patterns to automatically
generate comprehensive edge case tests.

Author: Asif Hussain
Created: 2025-11-21
Phase: TDD Mastery Phase 1
"""

import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EdgeCase:
    """Represents a single edge case scenario."""
    name: str
    description: str
    input_values: Dict[str, Any]
    expected_behavior: str  # "return", "raise", "mutate"
    expected_value: Optional[Any] = None
    expected_exception: Optional[str] = None
    confidence: float = 0.8  # How confident we are this is a valid edge case


class EdgeCaseAnalyzer:
    """Analyzes code to identify edge cases automatically."""
    
    # Common edge case patterns
    NUMERIC_EDGE_CASES = [
        "zero",
        "negative",
        "positive",
        "max_value",
        "min_value",
        "float_precision",
    ]
    
    STRING_EDGE_CASES = [
        "empty",
        "whitespace_only",
        "unicode",
        "very_long",
        "special_characters",
        "null_bytes",
    ]
    
    COLLECTION_EDGE_CASES = [
        "empty",
        "single_item",
        "large_collection",
        "duplicates",
        "nested",
    ]
    
    def __init__(self):
        """Initialize edge case analyzer."""
        self.edge_cases: List[EdgeCase] = []
    
    def analyze_function(self, func_node: ast.FunctionDef, source_code: str) -> List[EdgeCase]:
        """
        Analyze a function and generate edge cases.
        
        Args:
            func_node: AST node for the function
            source_code: Source code containing the function
            
        Returns:
            List of identified edge cases
        """
        self.edge_cases = []
        
        # Extract function metadata
        func_info = self._extract_function_info(func_node)
        
        # Analyze parameters
        for param in func_info["parameters"]:
            self._analyze_parameter_edge_cases(param, func_info)
        
        # Analyze return type
        self._analyze_return_edge_cases(func_info)
        
        # Analyze docstring for hints
        if func_info["docstring"]:
            self._analyze_docstring_edge_cases(func_info["docstring"], func_info)
        
        # Analyze function body for patterns
        self._analyze_body_edge_cases(func_node, func_info)
        
        return self.edge_cases
    
    def _extract_function_info(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract metadata from function node."""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": None,
                "default": None,
            }
            
            # Extract type annotation
            if arg.annotation:
                param_info["type"] = self._get_type_name(arg.annotation)
            
            parameters.append(param_info)
        
        # Extract defaults
        defaults = func_node.args.defaults
        if defaults:
            for i, default in enumerate(reversed(defaults)):
                param_idx = len(parameters) - len(defaults) + i
                if param_idx >= 0:
                    parameters[param_idx]["default"] = ast.unparse(default)
        
        # Extract return type
        return_type = None
        if func_node.returns:
            return_type = self._get_type_name(func_node.returns)
        
        # Extract docstring
        docstring = ast.get_docstring(func_node)
        
        return {
            "name": func_node.name,
            "parameters": parameters,
            "return_type": return_type,
            "docstring": docstring,
        }
    
    def _get_type_name(self, node: ast.AST) -> str:
        """Extract type name from annotation node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            # Handle generic types like List[str]
            base = self._get_type_name(node.value)
            arg = self._get_type_name(node.slice)
            return f"{base}[{arg}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ast.unparse(node)
    
    def _analyze_parameter_edge_cases(self, param: Dict[str, Any], func_info: Dict[str, Any]):
        """Generate edge cases based on parameter type."""
        param_name = param["name"]
        param_type = param["type"]
        
        if not param_type:
            # No type annotation - try to infer from name/usage
            param_type = self._infer_type_from_name(param_name)
        
        # Numeric types
        if param_type in ["int", "float", "Decimal"]:
            self._add_numeric_edge_cases(param_name, func_info)
        
        # String types
        elif param_type == "str":
            self._add_string_edge_cases(param_name, func_info)
        
        # Collection types
        elif param_type in ["list", "List", "dict", "Dict", "set", "Set", "tuple", "Tuple"]:
            self._add_collection_edge_cases(param_name, param_type, func_info)
        
        # Boolean types
        elif param_type == "bool":
            self._add_boolean_edge_cases(param_name, func_info)
        
        # None/Optional
        if "Optional" in str(param_type) or param.get("default") == "None":
            self._add_none_edge_case(param_name, func_info)
    
    def _add_numeric_edge_cases(self, param_name: str, func_info: Dict[str, Any]):
        """Add edge cases for numeric parameters."""
        func_name = func_info["name"]
        
        # Zero
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_zero",
            description=f"Edge case: {param_name} is zero",
            input_values={param_name: 0},
            expected_behavior="return",
            confidence=0.9
        ))
        
        # Negative value
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_negative",
            description=f"Edge case: {param_name} is negative",
            input_values={param_name: -1},
            expected_behavior="raise",
            expected_exception="ValueError",
            confidence=0.7
        ))
        
        # Large value
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_large",
            description=f"Edge case: {param_name} is very large",
            input_values={param_name: 999999999},
            expected_behavior="return",
            confidence=0.6
        ))
    
    def _add_string_edge_cases(self, param_name: str, func_info: Dict[str, Any]):
        """Add edge cases for string parameters."""
        func_name = func_info["name"]
        
        # Empty string
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_empty",
            description=f"Edge case: {param_name} is empty string",
            input_values={param_name: ""},
            expected_behavior="raise",
            expected_exception="ValueError",
            confidence=0.8
        ))
        
        # Whitespace only
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_whitespace",
            description=f"Edge case: {param_name} is whitespace only",
            input_values={param_name: "   "},
            expected_behavior="raise",
            expected_exception="ValueError",
            confidence=0.7
        ))
        
        # Unicode characters
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_unicode",
            description=f"Edge case: {param_name} contains Unicode",
            input_values={param_name: "こんにちは"},
            expected_behavior="return",
            confidence=0.6
        ))
        
        # Very long string
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_very_long",
            description=f"Edge case: {param_name} is very long",
            input_values={param_name: "x" * 10000},
            expected_behavior="return",
            confidence=0.5
        ))
    
    def _add_collection_edge_cases(self, param_name: str, param_type: str, func_info: Dict[str, Any]):
        """Add edge cases for collection parameters."""
        func_name = func_info["name"]
        
        # Empty collection
        empty_value = [] if "list" in param_type.lower() else {}
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_empty",
            description=f"Edge case: {param_name} is empty",
            input_values={param_name: empty_value},
            expected_behavior="return",
            expected_value=0 if "total" in func_name.lower() or "count" in func_name.lower() else None,
            confidence=0.9
        ))
        
        # Single item
        if "list" in param_type.lower():
            self.edge_cases.append(EdgeCase(
                name=f"test_{func_name}_{param_name}_single_item",
                description=f"Edge case: {param_name} has single item",
                input_values={param_name: [1]},
                expected_behavior="return",
                confidence=0.7
            ))
        
        # Large collection
        large_value = list(range(10000)) if "list" in param_type.lower() else {str(i): i for i in range(10000)}
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_large",
            description=f"Edge case: {param_name} is very large",
            input_values={param_name: large_value},
            expected_behavior="return",
            confidence=0.5
        ))
    
    def _add_boolean_edge_cases(self, param_name: str, func_info: Dict[str, Any]):
        """Add edge cases for boolean parameters."""
        func_name = func_info["name"]
        
        # True case
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_true",
            description=f"Edge case: {param_name} is True",
            input_values={param_name: True},
            expected_behavior="return",
            confidence=0.8
        ))
        
        # False case
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_false",
            description=f"Edge case: {param_name} is False",
            input_values={param_name: False},
            expected_behavior="return",
            confidence=0.8
        ))
    
    def _add_none_edge_case(self, param_name: str, func_info: Dict[str, Any]):
        """Add edge case for None value."""
        func_name = func_info["name"]
        
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_{param_name}_none",
            description=f"Edge case: {param_name} is None",
            input_values={param_name: None},
            expected_behavior="raise",
            expected_exception="TypeError",
            confidence=0.9
        ))
    
    def _analyze_return_edge_cases(self, func_info: Dict[str, Any]):
        """Analyze return type for edge cases."""
        return_type = func_info.get("return_type")
        if not return_type:
            return
        
        # If returns collection, test for empty returns
        if "list" in return_type.lower() or "dict" in return_type.lower():
            func_name = func_info["name"]
            self.edge_cases.append(EdgeCase(
                name=f"test_{func_name}_returns_empty",
                description="Edge case: function returns empty collection",
                input_values={},
                expected_behavior="return",
                expected_value=[] if "list" in return_type.lower() else {},
                confidence=0.6
            ))
    
    def _analyze_docstring_edge_cases(self, docstring: str, func_info: Dict[str, Any]):
        """Extract edge case hints from docstring."""
        if not docstring:
            return
        
        # Look for raises/exceptions mentioned
        exception_pattern = r"(?:Raises?|Throws?)\s*:\s*(\w+)"
        matches = re.findall(exception_pattern, docstring, re.IGNORECASE)
        
        for exception in matches:
            # Try to infer what causes this exception
            self._add_exception_edge_case(exception, func_info)
    
    def _add_exception_edge_case(self, exception: str, func_info: Dict[str, Any]):
        """Add edge case for expected exception."""
        func_name = func_info["name"]
        
        self.edge_cases.append(EdgeCase(
            name=f"test_{func_name}_raises_{exception.lower()}",
            description=f"Edge case: function raises {exception}",
            input_values={},  # Will need context to determine
            expected_behavior="raise",
            expected_exception=exception,
            confidence=0.7
        ))
    
    def _analyze_body_edge_cases(self, func_node: ast.FunctionDef, func_info: Dict[str, Any]):
        """Analyze function body for edge case patterns."""
        # Look for division operations (potential DivisionByZero)
        for node in ast.walk(func_node):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                self._add_division_by_zero_edge_case(func_info)
                break
        
        # Look for index access (potential IndexError)
        for node in ast.walk(func_node):
            if isinstance(node, ast.Subscript):
                self._add_index_error_edge_case(func_info)
                break
        
        # Look for dictionary access (potential KeyError)
        for node in ast.walk(func_node):
            if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
                # Check if it might be a dict
                self._add_key_error_edge_case(func_info)
                break
    
    def _add_division_by_zero_edge_case(self, func_info: Dict[str, Any]):
        """Add edge case for division by zero."""
        func_name = func_info["name"]
        
        # Find numeric parameters that might be divisors
        for param in func_info["parameters"]:
            if param["type"] in ["int", "float", "Decimal"] or "divisor" in param["name"].lower():
                self.edge_cases.append(EdgeCase(
                    name=f"test_{func_name}_division_by_zero",
                    description=f"Edge case: {param['name']} is zero causing division error",
                    input_values={param["name"]: 0},
                    expected_behavior="raise",
                    expected_exception="ZeroDivisionError",
                    confidence=0.8
                ))
                break
    
    def _add_index_error_edge_case(self, func_info: Dict[str, Any]):
        """Add edge case for index out of range."""
        func_name = func_info["name"]
        
        # Find list/sequence parameters
        for param in func_info["parameters"]:
            if "list" in str(param["type"]).lower() or "sequence" in param["name"].lower():
                self.edge_cases.append(EdgeCase(
                    name=f"test_{func_name}_index_out_of_range",
                    description=f"Edge case: accessing index beyond {param['name']} length",
                    input_values={param["name"]: []},
                    expected_behavior="raise",
                    expected_exception="IndexError",
                    confidence=0.7
                ))
                break
    
    def _add_key_error_edge_case(self, func_info: Dict[str, Any]):
        """Add edge case for missing dictionary key."""
        func_name = func_info["name"]
        
        # Find dict parameters
        for param in func_info["parameters"]:
            if "dict" in str(param["type"]).lower() or "mapping" in param["name"].lower():
                self.edge_cases.append(EdgeCase(
                    name=f"test_{func_name}_missing_key",
                    description=f"Edge case: accessing missing key in {param['name']}",
                    input_values={param["name"]: {}},
                    expected_behavior="raise",
                    expected_exception="KeyError",
                    confidence=0.6
                ))
                break
    
    def _infer_type_from_name(self, param_name: str) -> Optional[str]:
        """Infer parameter type from name."""
        name_lower = param_name.lower()
        
        # Common naming patterns
        if any(word in name_lower for word in ["count", "num", "size", "length", "total"]):
            return "int"
        elif any(word in name_lower for word in ["price", "amount", "rate", "percent"]):
            return "float"
        elif any(word in name_lower for word in ["name", "text", "message", "description"]):
            return "str"
        elif any(word in name_lower for word in ["items", "list", "collection"]):
            return "list"
        elif any(word in name_lower for word in ["data", "config", "mapping"]):
            return "dict"
        elif any(word in name_lower for word in ["enabled", "active", "is_", "has_"]):
            return "bool"
        
        return None
    
    def filter_by_confidence(self, min_confidence: float = 0.6) -> List[EdgeCase]:
        """Filter edge cases by confidence threshold."""
        return [ec for ec in self.edge_cases if ec.confidence >= min_confidence]
    
    def prioritize_edge_cases(self) -> List[EdgeCase]:
        """Sort edge cases by priority (confidence * impact)."""
        # High-impact edge cases
        high_impact = ["zero", "empty", "none", "negative"]
        
        def priority_score(edge_case: EdgeCase) -> float:
            score = edge_case.confidence
            
            # Boost score for high-impact patterns
            if any(pattern in edge_case.name.lower() for pattern in high_impact):
                score += 0.2
            
            # Boost score for exception-raising cases
            if edge_case.expected_behavior == "raise":
                score += 0.1
            
            return min(score, 1.0)
        
        return sorted(self.edge_cases, key=priority_score, reverse=True)
