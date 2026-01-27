"""
Result Pattern - Explicit Error Handling

Implements Result[T] pattern for mandatory error checking.
All MCP tools and orchestrators should return Result types.

Usage:
    def process_data(data: str) -> Result[ProcessedData]:
        if not data:
            return Err("Data cannot be empty")
        return Ok(ProcessedData(data))
    
    result = process_data(input_data)
    if result.is_ok():
        print(result.unwrap())
    else:
        print(f"Error: {result.error}")

Author: Asif Hussain
"""

from abc import ABCMeta
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Union

T = TypeVar('T')


class ResultMeta(type):
    """Metaclass for Result to support isinstance checks and subscripting."""
    
    def __instancecheck__(cls, instance):
        """Allow isinstance checks for Ok and Err instances."""
        return isinstance(instance, (Ok, Err))
    
    def __getitem__(cls, item):
        """Support Result[T] syntax for type hints."""
        return Union[Ok[item], Err]


class Result(metaclass=ResultMeta):
    """Base result type for isinstance and type hint support."""
    pass


@dataclass
class Ok(Generic[T]):
    """Success result containing a value."""
    value: T
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        return self.value


@dataclass
class Err:
    """Error result containing an error message."""
    error: str
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True
    
    def unwrap(self):
        raise ValueError(f"Called unwrap on Err: {self.error}")
    
    def unwrap_or(self, default):
        return default
    
    def unwrap_err(self) -> str:
        """Get error message."""
        return self.error


def ok(value: T) -> Ok[T]:
    """Create a success result."""
    return Ok(value)


def err(message: str) -> Err:
    """Create an error result."""
    return Err(message)
