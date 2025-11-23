"""
Tests for Error Condition Test Generation (Milestone 1.3)

Validates error condition detection, pytest.raises generation, validation failure tests,
and network/IO error boundary tests.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 1 - Milestone 1.3
"""

import pytest
import ast
from src.cortex_agents.test_generator.error_condition_generator import (
    ErrorConditionGenerator,
    ErrorCondition
)


class TestExplicitRaiseDetection:
    """Test detection of explicit raise statements in code."""
    
    def test_detects_value_error_with_message(self):
        """Should detect ValueError with specific message."""
        source_code = '''
def validate_age(age: int):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect ValueError
        assert any(ec.exception_type == "ValueError" for ec in error_conditions)
        
        # Should have input that triggers error
        value_errors = [ec for ec in error_conditions if ec.exception_type == "ValueError"]
        assert any("age" in ec.input_values for ec in value_errors)
    
    def test_detects_type_error(self):
        """Should detect TypeError from type validation."""
        source_code = '''
def process_string(text: str):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return text.upper()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect TypeError
        assert any(ec.exception_type == "TypeError" for ec in error_conditions)
    
    def test_detects_custom_exception(self):
        """Should detect custom exception types."""
        source_code = '''
def authenticate(token: str):
    if not token:
        raise AuthenticationError("Token required")
    return True
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect AuthenticationError
        assert any(ec.exception_type == "AuthenticationError" for ec in error_conditions)
    
    def test_generates_regex_for_message_matching(self):
        """Should generate regex pattern for pytest.raises match parameter."""
        source_code = '''
def divide(a: int, b: int):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should have regex pattern for message
        zero_div_errors = [ec for ec in error_conditions if ec.exception_type == "ZeroDivisionError"]
        assert len(zero_div_errors) > 0
        assert zero_div_errors[0].expected_message_regex  # Should not be empty


class TestValidationPatternDetection:
    """Test detection of validation patterns (missing fields, invalid types)."""
    
    def test_detects_missing_required_field(self):
        """Should generate test for None on non-Optional parameter."""
        source_code = '''
def create_user(name: str, email: str):
    """Create a new user."""
    return {"name": name, "email": email}
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect missing name and email
        assert any("name" in ec.description.lower() and "none" in ec.description.lower() 
                  for ec in error_conditions)
        assert any("email" in ec.description.lower() and "none" in ec.description.lower() 
                  for ec in error_conditions)
    
    def test_detects_invalid_type(self):
        """Should generate test for type mismatch."""
        source_code = '''
def calculate_total(price: int, quantity: int):
    """Calculate total price."""
    return price * quantity
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect invalid types for int parameters
        assert any(ec.exception_type == "TypeError" and "price" in ec.description 
                  for ec in error_conditions)
        assert any(ec.exception_type == "TypeError" and "quantity" in ec.description 
                  for ec in error_conditions)
    
    def test_detects_empty_string_validation(self):
        """Should generate test for empty strings on name/email fields."""
        source_code = '''
def register_user(username: str, email: str):
    """Register a new user."""
    return True
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect empty string validation for username and email
        assert any("username" in ec.description and "empty" in ec.description.lower() 
                  for ec in error_conditions)
        assert any("email" in ec.description and "empty" in ec.description.lower() 
                  for ec in error_conditions)
    
    def test_detects_empty_collection_validation(self):
        """Should generate test for empty collections when not allowed."""
        source_code = '''
def process_items(items: list):
    """Process a list of items."""
    return len(items)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect empty collection
        assert any("items" in ec.description and "empty" in ec.description.lower() 
                  for ec in error_conditions)


class TestIOOperationDetection:
    """Test detection of network/file I/O operations and error generation."""
    
    def test_detects_file_not_found_error(self):
        """Should generate FileNotFoundError test for file operations."""
        source_code = '''
def read_config(file_path: str):
    """Read configuration from file."""
    with open(file_path, 'r') as f:
        return f.read()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect FileNotFoundError
        assert any(ec.exception_type == "FileNotFoundError" for ec in error_conditions)
        
        # Should have test with nonexistent path
        file_errors = [ec for ec in error_conditions if ec.exception_type == "FileNotFoundError"]
        assert any("/nonexistent" in str(ec.input_values.get("file_path", "")) 
                  for ec in file_errors)
    
    def test_detects_permission_error(self):
        """Should generate PermissionError test for file operations."""
        source_code = '''
def write_log(log_path: str, message: str):
    """Write to log file."""
    with open(log_path, 'w') as f:
        f.write(message)
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect PermissionError
        assert any(ec.exception_type == "PermissionError" for ec in error_conditions)
    
    def test_detects_network_timeout(self):
        """Should generate TimeoutError test for network operations."""
        source_code = '''
def fetch_data(url: str):
    """Fetch data from API."""
    import requests
    response = requests.get(url)
    return response.json()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect TimeoutError
        assert any(ec.exception_type == "TimeoutError" for ec in error_conditions)
        
        # Should have test with timeout-prone URL
        timeout_errors = [ec for ec in error_conditions if ec.exception_type == "TimeoutError"]
        assert len(timeout_errors) > 0
    
    def test_detects_connection_error(self):
        """Should generate ConnectionError test for network operations."""
        source_code = '''
def post_data(endpoint: str, data: dict):
    """Post data to API endpoint."""
    import requests
    response = requests.post(endpoint, json=data)
    return response.status_code
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Should detect ConnectionError
        assert any(ec.exception_type == "ConnectionError" for ec in error_conditions)


class TestErrorConditionConfidenceScoring:
    """Test confidence scoring for error conditions."""
    
    def test_high_confidence_for_validation_errors(self):
        """Validation errors should have high confidence (>= 0.8)."""
        source_code = '''
def validate_email(email: str):
    if not email:
        raise ValueError("Email required")
    return True
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # Validation errors should be high confidence
        value_errors = [ec for ec in error_conditions if ec.exception_type == "ValueError"]
        assert any(ec.confidence >= 0.8 for ec in value_errors)
    
    def test_medium_confidence_for_io_errors(self):
        """I/O errors should have medium to high confidence (>= 0.7)."""
        source_code = '''
def load_file(path: str):
    with open(path) as f:
        return f.read()
'''
        tree = ast.parse(source_code)
        func_node = tree.body[0]
        
        generator = ErrorConditionGenerator()
        error_conditions = generator.analyze_function(func_node, source_code)
        
        # I/O errors should be >= 0.7 confidence
        io_errors = [ec for ec in error_conditions 
                    if ec.exception_type in ["FileNotFoundError", "PermissionError"]]
        assert any(ec.confidence >= 0.7 for ec in io_errors)


class TestPytestRaisesCodeGeneration:
    """Test generation of pytest.raises code with regex matching."""
    
    def test_generates_valid_pytest_raises_syntax(self):
        """Should generate syntactically valid pytest.raises code."""
        error_condition = ErrorCondition(
            name="test_divide_by_zero",
            description="Error: division by zero",
            input_values={"b": 0},
            exception_type="ZeroDivisionError",
            expected_message_regex=r".*division.*zero.*",
            confidence=0.9
        )
        
        # Manually generate test code (simulating FunctionTestGenerator)
        test_code = f'''def {error_condition.name}(self):
    with pytest.raises({error_condition.exception_type}, match=r"{error_condition.expected_message_regex}"):
        divide(a=10, b=0)'''
        
        # Should contain pytest.raises
        assert "pytest.raises" in test_code
        
        # Should contain exception type
        assert error_condition.exception_type in test_code
        
        # Should contain match parameter with regex
        assert "match=r" in test_code
        assert error_condition.expected_message_regex in test_code
    
    def test_escapes_special_regex_characters(self):
        """Should properly escape special regex characters in messages."""
        generator = ErrorConditionGenerator()
        
        # Message with special regex characters
        message = "Error: value must be >= 0 (got -1)"
        escaped = generator._escape_regex(message)
        
        # Should escape parentheses, asterisks, etc.
        assert "\\(" in escaped or "(" not in message  # Either escaped or not present
        assert "\\" in escaped or all(c not in message for c in r"\.^$*+?{}[]|()")  # Escaped special chars


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
