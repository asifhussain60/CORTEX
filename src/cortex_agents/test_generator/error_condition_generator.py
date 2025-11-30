"""
Error Condition Test Generation for TDD Mastery

Analyzes code to automatically generate comprehensive error condition tests
using pytest.raises with regex message matching.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 1 - Milestone 1.3
"""

import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ErrorCondition:
    """Represents an error condition that should be tested."""
    name: str
    description: str
    input_values: Dict[str, Any]
    exception_type: str
    expected_message_regex: str
    confidence: float = 0.8


class ErrorConditionGenerator:
    """Generates comprehensive error condition tests with smart exception detection."""
    
    def __init__(self):
        """Initialize error condition generator."""
        self.error_conditions: List[ErrorCondition] = []
    
    def analyze_function(self, func_node: ast.FunctionDef, source_code: str) -> List[ErrorCondition]:
        """
        Analyze function for potential error conditions.
        
        Args:
            func_node: AST node for the function
            source_code: Source code containing the function
            
        Returns:
            List of identified error conditions
        """
        self.error_conditions = []
        
        # Extract function metadata
        func_info = self._extract_function_info(func_node)
        
        # Analyze function body for explicit raises
        self._analyze_explicit_raises(func_node, func_info)
        
        # Analyze for validation patterns
        self._analyze_validation_patterns(func_node, func_info)
        
        # Analyze for network/IO operations
        self._analyze_io_operations(func_node, func_info)
        
        # Analyze for type errors
        self._analyze_type_errors(func_node, func_info)
        
        # Analyze docstring for documented exceptions
        if func_info["docstring"]:
            self._analyze_docstring_exceptions(func_info["docstring"], func_info)
        
        return self.error_conditions
    
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
        
        return {
            "name": func_node.name,
            "parameters": parameters,
            "docstring": ast.get_docstring(func_node),
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
    
    def _analyze_explicit_raises(self, func_node: ast.FunctionDef, func_info: Dict[str, Any]):
        """Detect explicit raise statements in function body."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Raise):
                self._extract_raise_condition(node, func_info)
    
    def _extract_raise_condition(self, raise_node: ast.Raise, func_info: Dict[str, Any]):
        """Extract error condition from raise statement."""
        if not raise_node.exc:
            return
        
        func_name = func_info["name"]
        
        # Extract exception type
        exception_type = "Exception"
        exception_msg = None
        
        if isinstance(raise_node.exc, ast.Call):
            # raise ValueError("message")
            if isinstance(raise_node.exc.func, ast.Name):
                exception_type = raise_node.exc.func.id
            
            # Extract message if present
            if raise_node.exc.args:
                if isinstance(raise_node.exc.args[0], ast.Constant):
                    exception_msg = raise_node.exc.args[0].value
                elif isinstance(raise_node.exc.args[0], ast.JoinedStr):
                    # f-string message
                    exception_msg = ".*"  # Regex to match any message
        
        elif isinstance(raise_node.exc, ast.Name):
            # raise ValueError
            exception_type = raise_node.exc.id
        
        # Try to infer what triggers this exception
        trigger_condition = self._infer_trigger_condition(raise_node, func_info)
        
        # Create error condition
        self.error_conditions.append(ErrorCondition(
            name=f"test_{func_name}_raises_{exception_type.lower()}",
            description=f"Error condition: {exception_type} raised when {trigger_condition}",
            input_values=self._generate_error_inputs(trigger_condition, func_info),
            exception_type=exception_type,
            expected_message_regex=self._escape_regex(exception_msg) if exception_msg else ".*",
            confidence=0.85
        ))
    
    def _infer_trigger_condition(self, raise_node: ast.Raise, func_info: Dict[str, Any]) -> str:
        """Infer what condition triggers this exception."""
        # Walk up AST to find containing if statement
        parent = raise_node
        while parent:
            # Look for if statement
            for node in ast.walk(func_info.get("ast_node", raise_node)):
                if isinstance(node, ast.If):
                    # Check if raise is in this if block
                    if raise_node in ast.walk(node):
                        # Extract condition description
                        condition = ast.unparse(node.test)
                        return self._simplify_condition(condition)
            break
        
        return "invalid input"
    
    def _simplify_condition(self, condition: str) -> str:
        """Simplify condition to human-readable description."""
        # Common patterns
        if "is None" in condition or "== None" in condition:
            param = condition.split()[0]
            return f"{param} is None"
        elif "< 0" in condition:
            param = condition.split()[0]
            return f"{param} is negative"
        elif "== 0" in condition:
            param = condition.split()[0]
            return f"{param} is zero"
        elif "len(" in condition and "== 0" in condition:
            param = re.search(r'len\((\w+)\)', condition)
            if param:
                return f"{param.group(1)} is empty"
        
        return condition
    
    def _generate_error_inputs(self, condition: str, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate input values that trigger the error."""
        inputs = {}
        
        # Parse condition to determine inputs
        if "is None" in condition:
            param_name = condition.split()[0]
            inputs[param_name] = None
        elif "is negative" in condition:
            param_name = condition.split()[0]
            inputs[param_name] = -1
        elif "is zero" in condition:
            param_name = condition.split()[0]
            inputs[param_name] = 0
        elif "is empty" in condition:
            param_name = condition.split()[0]
            inputs[param_name] = []
        
        return inputs
    
    def _analyze_validation_patterns(self, func_node: ast.FunctionDef, func_info: Dict[str, Any]):
        """Detect validation patterns (missing fields, invalid types, etc.)."""
        func_name = func_info["name"]
        
        # Pattern 1: Required field validation
        for param in func_info["parameters"]:
            param_name = param["name"]
            param_type = param.get("type")
            
            # Missing required field (not Optional)
            if param_type and "Optional" not in param_type:
                self.error_conditions.append(ErrorCondition(
                    name=f"test_{func_name}_missing_{param_name}",
                    description=f"Validation error: {param_name} is None",
                    input_values={param_name: None},
                    exception_type="ValueError",
                    expected_message_regex=f".*{param_name}.*required.*|.*{param_name}.*cannot be None.*",
                    confidence=0.8
                ))
            
            # Invalid type
            if param_type == "int":
                self.error_conditions.append(ErrorCondition(
                    name=f"test_{func_name}_{param_name}_invalid_type",
                    description=f"Validation error: {param_name} is not an integer",
                    input_values={param_name: "not_an_int"},
                    exception_type="TypeError",
                    expected_message_regex=f".*{param_name}.*must be.*int.*|.*expected.*int.*",
                    confidence=0.75
                ))
            
            elif param_type == "str":
                # Empty string validation
                if "name" in param_name.lower() or "email" in param_name.lower():
                    self.error_conditions.append(ErrorCondition(
                        name=f"test_{func_name}_{param_name}_empty_string",
                        description=f"Validation error: {param_name} is empty string",
                        input_values={param_name: ""},
                        exception_type="ValueError",
                        expected_message_regex=f".*{param_name}.*empty.*|.*{param_name}.*required.*",
                        confidence=0.85
                    ))
            
            elif param_type in ["list", "List", "dict", "Dict"]:
                # Empty collection when not allowed
                empty_val = [] if "list" in param_type.lower() else {}
                self.error_conditions.append(ErrorCondition(
                    name=f"test_{func_name}_{param_name}_empty_collection",
                    description=f"Validation error: {param_name} is empty",
                    input_values={param_name: empty_val},
                    exception_type="ValueError",
                    expected_message_regex=f".*{param_name}.*empty.*|.*{param_name}.*at least one.*",
                    confidence=0.7
                ))
    
    def _analyze_io_operations(self, func_node: ast.FunctionDef, func_info: Dict[str, Any]):
        """Detect network/file I/O operations and generate timeout/error tests."""
        func_name = func_info["name"]
        has_io = False
        
        # Check for file operations
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # File operations: open(), read(), write()
                    if node.func.id in ["open", "read", "write"]:
                        has_io = True
                        self._add_file_io_errors(func_info)
                        break
                
                elif isinstance(node.func, ast.Attribute):
                    # HTTP/Network: requests.get(), urllib.request.urlopen()
                    if node.func.attr in ["get", "post", "put", "delete", "urlopen", "request"]:
                        has_io = True
                        self._add_network_errors(func_info)
                        break
    
    def _add_file_io_errors(self, func_info: Dict[str, Any]):
        """Add file I/O error conditions."""
        func_name = func_info["name"]
        
        # Find file path parameter
        file_param = None
        for param in func_info["parameters"]:
            if "path" in param["name"].lower() or "file" in param["name"].lower():
                file_param = param["name"]
                break
        
        if file_param:
            # File not found
            self.error_conditions.append(ErrorCondition(
                name=f"test_{func_name}_file_not_found",
                description=f"I/O error: file does not exist",
                input_values={file_param: "/nonexistent/path/file.txt"},
                exception_type="FileNotFoundError",
                expected_message_regex=r".*No such file or directory.*",
                confidence=0.9
            ))
            
            # Permission denied
            self.error_conditions.append(ErrorCondition(
                name=f"test_{func_name}_permission_denied",
                description=f"I/O error: insufficient permissions",
                input_values={file_param: "/root/protected.txt"},
                exception_type="PermissionError",
                expected_message_regex=r".*Permission denied.*",
                confidence=0.75
            ))
    
    def _add_network_errors(self, func_info: Dict[str, Any]):
        """Add network error conditions."""
        func_name = func_info["name"]
        
        # Find URL parameter
        url_param = None
        for param in func_info["parameters"]:
            if "url" in param["name"].lower() or "endpoint" in param["name"].lower():
                url_param = param["name"]
                break
        
        if url_param:
            # Connection timeout
            self.error_conditions.append(ErrorCondition(
                name=f"test_{func_name}_connection_timeout",
                description=f"Network error: connection timeout",
                input_values={url_param: "http://192.0.2.1:9999"},  # TEST-NET-1 (non-routable)
                exception_type="TimeoutError",
                expected_message_regex=r".*timeout.*|.*timed out.*",
                confidence=0.85
            ))
            
            # Connection refused
            self.error_conditions.append(ErrorCondition(
                name=f"test_{func_name}_connection_refused",
                description=f"Network error: connection refused",
                input_values={url_param: "http://localhost:9999"},
                exception_type="ConnectionError",
                expected_message_regex=r".*Connection refused.*|.*connection.*failed.*",
                confidence=0.8
            ))
    
    def _analyze_type_errors(self, func_node: ast.FunctionDef, func_info: Dict[str, Any]):
        """Detect potential type errors from usage patterns."""
        func_name = func_info["name"]
        
        # Analyze function body for operations that can cause type errors
        for node in ast.walk(func_node):
            # String operations on non-strings
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Methods like .lower(), .upper(), .strip() require string
                    if node.func.attr in ["lower", "upper", "strip", "split"]:
                        # Find the variable being operated on
                        if isinstance(node.func.value, ast.Name):
                            var_name = node.func.value.id
                            
                            # Check if it's a parameter
                            for param in func_info["parameters"]:
                                if param["name"] == var_name and param.get("type") == "str":
                                    self.error_conditions.append(ErrorCondition(
                                        name=f"test_{func_name}_{var_name}_not_string",
                                        description=f"Type error: {var_name} is not a string",
                                        input_values={var_name: 123},
                                        exception_type="AttributeError",
                                        expected_message_regex=f".*'int' object has no attribute.*|.*{node.func.attr}.*",
                                        confidence=0.7
                                    ))
                                    break
    
    def _analyze_docstring_exceptions(self, docstring: str, func_info: Dict[str, Any]):
        """Extract exception documentation from docstring."""
        func_name = func_info["name"]
        
        # Parse Google-style docstring
        raises_section = re.search(r'Raises?:\s*(.*?)(?:\n\n|\Z)', docstring, re.DOTALL | re.IGNORECASE)
        if raises_section:
            raises_text = raises_section.group(1)
            
            # Extract exception types and descriptions
            # Format: ExceptionType: Description
            exception_pattern = r'(\w+Error|\w+Exception):\s*([^\n]+)'
            matches = re.findall(exception_pattern, raises_text)
            
            for exception_type, description in matches:
                self.error_conditions.append(ErrorCondition(
                    name=f"test_{func_name}_raises_{exception_type.lower()}_documented",
                    description=f"Documented error: {description.strip()}",
                    input_values={},  # Will be inferred from description
                    exception_type=exception_type,
                    expected_message_regex=".*",
                    confidence=0.75
                ))
    
    def _escape_regex(self, message: str) -> str:
        """Escape special regex characters in exception message."""
        if not message:
            return ".*"
        
        # Escape special regex characters
        special_chars = r'\.^$*+?{}[]|()'
        for char in special_chars:
            message = message.replace(char, f'\\{char}')
        
        return message
    
    def filter_by_confidence(self, min_confidence: float = 0.7) -> List[ErrorCondition]:
        """Filter error conditions by confidence threshold."""
        return [ec for ec in self.error_conditions if ec.confidence >= min_confidence]
    
    def prioritize_error_conditions(self) -> List[ErrorCondition]:
        """Sort error conditions by priority."""
        # High-priority error types
        high_priority = [
            "ValueError",  # Validation errors
            "TypeError",   # Type mismatches
            "FileNotFoundError",  # I/O errors
            "PermissionError",
            "TimeoutError",  # Network errors
            "ConnectionError",
        ]
        
        def priority_score(error_cond: ErrorCondition) -> float:
            score = error_cond.confidence
            
            # Boost score for high-priority exception types
            if error_cond.exception_type in high_priority:
                score += 0.2
            
            return min(score, 1.0)
        
        return sorted(self.error_conditions, key=priority_score, reverse=True)
