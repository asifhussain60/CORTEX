"""Guard clauses for input validation (fail fast pattern)"""
from typing import Any, Optional, Iterable


class Guard:
    """Guard clauses for defensive programming
    
    Guards provide early validation of inputs, failing fast with clear errors.
    Based on Ardalis.GuardClauses pattern from Clean Architecture.
    
    Example:
        def process_conversation(title: str, content: str):
            Guard.against_null(title, "title")
            Guard.against_empty(content, "content")
            Guard.against_out_of_range(len(title), 1, 200, "title length")
            # Continue processing...
    """
    
    @staticmethod
    def against_null(value: Any, parameter_name: str, message: Optional[str] = None) -> None:
        """Guard against null/None values
        
        Args:
            value: Value to check
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If value is None
        """
        if value is None:
            msg = message or f"{parameter_name} cannot be None"
            raise ValueError(msg)
    
    @staticmethod
    def against_empty(value: str, parameter_name: str, message: Optional[str] = None) -> None:
        """Guard against empty strings
        
        Args:
            value: String to check
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If string is None, empty, or whitespace only
        """
        if value is None or not value or not value.strip():
            msg = message or f"{parameter_name} cannot be empty or whitespace"
            raise ValueError(msg)
    
    @staticmethod
    def against_negative(value: int, parameter_name: str, message: Optional[str] = None) -> None:
        """Guard against negative numbers
        
        Args:
            value: Number to check
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If value is negative
        """
        if value < 0:
            msg = message or f"{parameter_name} cannot be negative (got {value})"
            raise ValueError(msg)
    
    @staticmethod
    def against_negative_or_zero(value: int, parameter_name: str, 
                                  message: Optional[str] = None) -> None:
        """Guard against negative or zero numbers
        
        Args:
            value: Number to check
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If value is <= 0
        """
        if value <= 0:
            msg = message or f"{parameter_name} must be positive (got {value})"
            raise ValueError(msg)
    
    @staticmethod
    def against_out_of_range(value: float, min_val: float, max_val: float, 
                             parameter_name: str, message: Optional[str] = None) -> None:
        """Guard against values outside valid range
        
        Args:
            value: Value to check
            min_val: Minimum valid value (inclusive)
            max_val: Maximum valid value (inclusive)
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If value is outside [min_val, max_val]
        """
        if not min_val <= value <= max_val:
            msg = message or (
                f"{parameter_name} must be between {min_val} and {max_val} "
                f"(got {value})"
            )
            raise ValueError(msg)
    
    @staticmethod
    def against_empty_collection(value: Iterable, parameter_name: str, 
                                  message: Optional[str] = None) -> None:
        """Guard against empty collections
        
        Args:
            value: Collection to check
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If collection is None or empty
        """
        if value is None or len(list(value)) == 0:
            msg = message or f"{parameter_name} cannot be empty"
            raise ValueError(msg)
    
    @staticmethod
    def against_invalid_format(value: str, pattern: str, parameter_name: str,
                               message: Optional[str] = None) -> None:
        """Guard against strings that don't match expected format
        
        Args:
            value: String to check
            pattern: Regex pattern to match
            parameter_name: Name of parameter for error message
            message: Optional custom error message
            
        Raises:
            ValueError: If string doesn't match pattern
        """
        import re
        if not re.match(pattern, value):
            msg = message or f"{parameter_name} has invalid format (expected {pattern})"
            raise ValueError(msg)
