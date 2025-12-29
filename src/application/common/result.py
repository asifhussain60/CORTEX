"""Result pattern for explicit success/failure handling"""
from typing import TypeVar, Generic, List, Optional, Union
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    """Represents the result of an operation (success or failure)
    
    Replaces exception-based error handling with explicit results.
    
    Example:
        # Success case
        result = Result.success("data")
        if result.is_success:
            print(result.value)
        
        # Failure case
        result = Result.failure(["Error 1", "Error 2"])
        if result.is_failure:
            print(result.errors)
    """
    succeeded: bool
    value: Optional[T] = None
    errors: Optional[List[str]] = None
    
    @staticmethod
    def success(value: T) -> 'Result[T]':
        """Create a successful result with a value"""
        return Result(succeeded=True, value=value)
    
    @staticmethod
    def failure(errors: Union[List[str], str]) -> 'Result[T]':
        """Create a failed result with error messages"""
        error_list = [errors] if isinstance(errors, str) else errors
        return Result(succeeded=False, errors=error_list)
    
    @property
    def is_success(self) -> bool:
        """Check if the operation succeeded"""
        return self.succeeded
    
    @property
    def is_failure(self) -> bool:
        """Check if the operation failed"""
        return not self.succeeded
    
    def unwrap(self) -> T:
        """Get the value or raise if failed
        
        Raises:
            ValueError: If result is a failure
        """
        if self.is_failure:
            error_msg = ", ".join(self.errors) if self.errors else "Unknown error"
            raise ValueError(f"Cannot unwrap failed result: {error_msg}")
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or return default if failed"""
        return self.value if self.is_success else default
    
    def map(self, func) -> 'Result':
        """Transform the value if successful"""
        if self.is_failure:
            return self
        try:
            return Result.success(func(self.value))
        except Exception as e:
            return Result.failure([str(e)])
    
    def __str__(self) -> str:
        if self.is_success:
            return f"Success({self.value})"
        return f"Failure({self.errors})"
    
    def __repr__(self) -> str:
        return self.__str__()
