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
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Union

T = TypeVar('T')


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


# Type alias for Result
Result = Union[Ok[T], Err]


def ok(value: T) -> Ok[T]:
    """Create a success result."""
    return Ok(value)


def err(message: str) -> Err:
    """Create an error result."""
    return Err(message)
