"""Unit tests for Result pattern"""
import pytest
from src.application.common.result import Result


class TestResult:
    """Test Result pattern implementation"""
    
    def test_success_creates_successful_result(self):
        """Test creating a successful result"""
        result = Result.success("test value")
        
        assert result.is_success
        assert not result.is_failure
        assert result.value == "test value"
        assert result.errors is None
    
    def test_failure_creates_failed_result_with_list(self):
        """Test creating a failed result with error list"""
        result = Result.failure(["error1", "error2"])
        
        assert result.is_failure
        assert not result.is_success
        assert result.value is None
        assert result.errors == ["error1", "error2"]
    
    def test_failure_creates_failed_result_with_string(self):
        """Test creating a failed result with single error string"""
        result = Result.failure("single error")
        
        assert result.is_failure
        assert result.errors == ["single error"]
    
    def test_unwrap_returns_value_on_success(self):
        """Test unwrapping a successful result"""
        result = Result.success(42)
        
        value = result.unwrap()
        assert value == 42
    
    def test_unwrap_raises_on_failure(self):
        """Test unwrapping a failed result raises ValueError"""
        result = Result.failure(["error1", "error2"])
        
        with pytest.raises(ValueError) as exc_info:
            result.unwrap()
        
        assert "error1, error2" in str(exc_info.value)
    
    def test_unwrap_or_returns_value_on_success(self):
        """Test unwrap_or returns value on success"""
        result = Result.success(42)
        
        value = result.unwrap_or(0)
        assert value == 42
    
    def test_unwrap_or_returns_default_on_failure(self):
        """Test unwrap_or returns default on failure"""
        result = Result.failure(["error"])
        
        value = result.unwrap_or(0)
        assert value == 0
    
    def test_map_transforms_successful_value(self):
        """Test mapping a function over successful result"""
        result = Result.success(5)
        
        mapped = result.map(lambda x: x * 2)
        
        assert mapped.is_success
        assert mapped.value == 10
    
    def test_map_preserves_failure(self):
        """Test mapping over failed result preserves failure"""
        result = Result.failure(["error"])
        
        mapped = result.map(lambda x: x * 2)
        
        assert mapped.is_failure
        assert mapped.errors == ["error"]
    
    def test_map_catches_exceptions(self):
        """Test map converts exceptions to failures"""
        result = Result.success(5)
        
        mapped = result.map(lambda x: x / 0)  # Division by zero
        
        assert mapped.is_failure
        assert len(mapped.errors) > 0
    
    def test_str_representation_success(self):
        """Test string representation of success"""
        result = Result.success("value")
        assert str(result) == "Success(value)"
    
    def test_str_representation_failure(self):
        """Test string representation of failure"""
        result = Result.failure(["error1", "error2"])
        assert str(result) == "Failure(['error1', 'error2'])"
