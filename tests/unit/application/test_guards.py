"""Unit tests for Guard clauses"""
import pytest
from src.application.common.guards import Guard


class TestGuard:
    """Test Guard clause implementations"""
    
    def test_against_null_raises_on_none(self):
        """Test against_null raises ValueError for None"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_null(None, "test_param")
        
        assert "test_param cannot be None" in str(exc_info.value)
    
    def test_against_null_passes_on_value(self):
        """Test against_null passes for non-None values"""
        Guard.against_null("value", "test_param")  # Should not raise
        Guard.against_null(0, "test_param")  # Zero is valid
        Guard.against_null(False, "test_param")  # False is valid
    
    def test_against_null_custom_message(self):
        """Test against_null with custom error message"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_null(None, "param", "Custom error message")
        
        assert "Custom error message" in str(exc_info.value)
    
    def test_against_empty_raises_on_none(self):
        """Test against_empty raises for None"""
        with pytest.raises(ValueError):
            Guard.against_empty(None, "test_param")
    
    def test_against_empty_raises_on_empty_string(self):
        """Test against_empty raises for empty string"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_empty("", "test_param")
        
        assert "test_param cannot be empty" in str(exc_info.value)
    
    def test_against_empty_raises_on_whitespace(self):
        """Test against_empty raises for whitespace-only string"""
        with pytest.raises(ValueError):
            Guard.against_empty("   ", "test_param")
    
    def test_against_empty_passes_on_valid_string(self):
        """Test against_empty passes for valid strings"""
        Guard.against_empty("value", "test_param")  # Should not raise
        Guard.against_empty(" value ", "test_param")  # Whitespace around content is OK
    
    def test_against_negative_raises_on_negative(self):
        """Test against_negative raises for negative numbers"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_negative(-1, "test_param")
        
        assert "test_param cannot be negative" in str(exc_info.value)
        assert "-1" in str(exc_info.value)
    
    def test_against_negative_passes_on_zero(self):
        """Test against_negative passes for zero"""
        Guard.against_negative(0, "test_param")  # Should not raise
    
    def test_against_negative_passes_on_positive(self):
        """Test against_negative passes for positive numbers"""
        Guard.against_negative(1, "test_param")
        Guard.against_negative(100, "test_param")
    
    def test_against_negative_or_zero_raises_on_zero(self):
        """Test against_negative_or_zero raises for zero"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_negative_or_zero(0, "test_param")
        
        assert "test_param must be positive" in str(exc_info.value)
    
    def test_against_negative_or_zero_raises_on_negative(self):
        """Test against_negative_or_zero raises for negative"""
        with pytest.raises(ValueError):
            Guard.against_negative_or_zero(-1, "test_param")
    
    def test_against_negative_or_zero_passes_on_positive(self):
        """Test against_negative_or_zero passes for positive numbers"""
        Guard.against_negative_or_zero(1, "test_param")
        Guard.against_negative_or_zero(100, "test_param")
    
    def test_against_out_of_range_raises_below_min(self):
        """Test against_out_of_range raises when value below minimum"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_out_of_range(0.4, 0.5, 1.0, "test_param")
        
        assert "must be between 0.5 and 1.0" in str(exc_info.value)
        assert "0.4" in str(exc_info.value)
    
    def test_against_out_of_range_raises_above_max(self):
        """Test against_out_of_range raises when value above maximum"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_out_of_range(1.1, 0.0, 1.0, "test_param")
        
        assert "must be between 0.0 and 1.0" in str(exc_info.value)
    
    def test_against_out_of_range_passes_at_boundaries(self):
        """Test against_out_of_range passes at exact boundaries"""
        Guard.against_out_of_range(0.0, 0.0, 1.0, "test_param")  # Min boundary
        Guard.against_out_of_range(1.0, 0.0, 1.0, "test_param")  # Max boundary
    
    def test_against_out_of_range_passes_in_range(self):
        """Test against_out_of_range passes for values in range"""
        Guard.against_out_of_range(0.5, 0.0, 1.0, "test_param")
        Guard.against_out_of_range(0.75, 0.0, 1.0, "test_param")
    
    def test_against_empty_collection_raises_on_none(self):
        """Test against_empty_collection raises for None"""
        with pytest.raises(ValueError):
            Guard.against_empty_collection(None, "test_param")
    
    def test_against_empty_collection_raises_on_empty_list(self):
        """Test against_empty_collection raises for empty list"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_empty_collection([], "test_param")
        
        assert "test_param cannot be empty" in str(exc_info.value)
    
    def test_against_empty_collection_passes_on_non_empty(self):
        """Test against_empty_collection passes for non-empty collections"""
        Guard.against_empty_collection([1, 2, 3], "test_param")
        Guard.against_empty_collection(("a", "b"), "test_param")
        Guard.against_empty_collection({1, 2}, "test_param")
    
    def test_against_invalid_format_raises_on_mismatch(self):
        """Test against_invalid_format raises when pattern doesn't match"""
        with pytest.raises(ValueError) as exc_info:
            Guard.against_invalid_format("abc", r"^\d+$", "test_param")
        
        assert "invalid format" in str(exc_info.value)
    
    def test_against_invalid_format_passes_on_match(self):
        """Test against_invalid_format passes when pattern matches"""
        Guard.against_invalid_format("123", r"^\d+$", "test_param")
        Guard.against_invalid_format("abc", r"^[a-z]+$", "test_param")
