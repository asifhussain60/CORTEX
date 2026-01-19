"""
Unit Tests for Result Pattern

Tests Ok/Err result types for explicit error handling.
"""

import pytest

from cortex.brain.core.result import Ok, Err, ok, err, Result


class TestOk:
    """Tests for Ok result type."""
    
    def test_is_ok_returns_true(self):
        """Ok should report is_ok as True."""
        result = Ok("value")
        assert result.is_ok() is True
    
    def test_is_err_returns_false(self):
        """Ok should report is_err as False."""
        result = Ok("value")
        assert result.is_err() is False
    
    def test_unwrap_returns_value(self):
        """unwrap should return the contained value."""
        result = Ok("test_value")
        assert result.unwrap() == "test_value"
    
    def test_unwrap_or_returns_value(self):
        """unwrap_or should return the contained value, not default."""
        result = Ok("actual")
        assert result.unwrap_or("default") == "actual"
    
    def test_can_contain_complex_types(self):
        """Ok should work with complex types."""
        data = {"key": "value", "list": [1, 2, 3]}
        result = Ok(data)
        assert result.unwrap() == data


class TestErr:
    """Tests for Err result type."""
    
    def test_is_ok_returns_false(self):
        """Err should report is_ok as False."""
        result = Err("error message")
        assert result.is_ok() is False
    
    def test_is_err_returns_true(self):
        """Err should report is_err as True."""
        result = Err("error message")
        assert result.is_err() is True
    
    def test_unwrap_raises_error(self):
        """unwrap on Err should raise ValueError."""
        result = Err("something went wrong")
        
        with pytest.raises(ValueError, match="something went wrong"):
            result.unwrap()
    
    def test_unwrap_or_returns_default(self):
        """unwrap_or should return default value for Err."""
        result = Err("error")
        assert result.unwrap_or("default") == "default"
    
    def test_error_message_preserved(self):
        """Error message should be accessible."""
        result = Err("specific error")
        assert result.error == "specific error"


class TestHelperFunctions:
    """Tests for ok() and err() helper functions."""
    
    def test_ok_creates_ok_result(self):
        """ok() should create an Ok instance."""
        result = ok("value")
        assert isinstance(result, Ok)
        assert result.unwrap() == "value"
    
    def test_err_creates_err_result(self):
        """err() should create an Err instance."""
        result = err("error message")
        assert isinstance(result, Err)
        assert result.error == "error message"


class TestResultPatternUsage:
    """Tests demonstrating idiomatic Result pattern usage."""
    
    def test_function_returning_result(self):
        """Example of function returning Result."""
        def divide(a: int, b: int) -> Result[float]:
            if b == 0:
                return err("Cannot divide by zero")
            return ok(a / b)
        
        # Success case
        result = divide(10, 2)
        assert result.is_ok()
        assert result.unwrap() == 5.0
        
        # Error case
        result = divide(10, 0)
        assert result.is_err()
        assert "zero" in result.error
    
    def test_chaining_results(self):
        """Example of handling results in sequence."""
        def step1() -> Result[int]:
            return ok(10)
        
        def step2(value: int) -> Result[int]:
            return ok(value * 2)
        
        result1 = step1()
        if result1.is_ok():
            result2 = step2(result1.unwrap())
            assert result2.unwrap() == 20
