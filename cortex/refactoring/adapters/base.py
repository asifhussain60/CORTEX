"""
Base adapter interface for external refactoring tools.

AC_START: AC-PHASE24.1.1-004
Description: Abstract base class for refactoring tool adapters
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union

from cortex.brain.core.result import Ok, Err
from cortex.refactoring.models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)


class RefactoringToolAdapter(ABC):
    """Abstract base class for external refactoring tool adapters.
    
    Each adapter integrates a specific external tool (Rope, Roslyn, TypeScript LS, etc.)
    and provides a uniform interface for executing refactoring operations.
    
    Subclasses must implement:
        - get_supported_operations(): List available refactoring operations
        - get_language(): Return the programming language this adapter handles
        - is_available(): Check if the external tool is installed/accessible
        - execute_refactoring(): Execute a refactoring operation
        - validate_request(): Validate a refactoring request before execution
    
    Design principles:
        - Graceful degradation when tools unavailable
        - Type-safe operations (leverage external tool capabilities)
        - Performance optimization (lazy init, process pooling)
        - Full audit logging (CORE-027)
    
    Example:
        >>> class RopeAdapter(RefactoringToolAdapter):
        ...     def get_language(self) -> RefactoringLanguage:
        ...         return RefactoringLanguage.PYTHON
        ...     
        ...     def is_available(self) -> bool:
        ...         try:
        ...             import rope
        ...             return True
        ...         except ImportError:
        ...             return False
        ...     
        ...     # ... implement other methods
    """
    
    @abstractmethod
    def get_supported_operations(self) -> List[str]:
        """Return list of supported refactoring operations.
        
        Examples: ["extract_method", "rename", "inline", "encapsulate"]
        
        Returns:
            List of operation names supported by this adapter
        """
        pass
    
    @abstractmethod
    def get_language(self) -> RefactoringLanguage:
        """Return the programming language this adapter handles.
        
        Returns:
            RefactoringLanguage enum value
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the external tool is available.
        
        Should check:
            - Tool installation (e.g., import rope)
            - External process accessibility (e.g., Roslyn server)
            - Configuration validity
        
        Returns:
            True if tool is available and ready to use, False otherwise
        """
        pass
    
    @abstractmethod
    def execute_refactoring(self, request: RefactoringRequest) -> Union[Ok[RefactoringResult], Err]:
        """Execute a refactoring operation.
        
        Args:
            request: RefactoringRequest containing operation details
            
        Returns:
            Union[Ok[RefactoringResult], Err]: Success with RefactoringResult or error message
            
        Implementation guidelines:
            - Validate request first (call validate_request)
            - Check tool availability (call is_available)
            - Execute operation via external tool
            - Capture modified files, warnings, errors
            - Return comprehensive result
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: RefactoringRequest) -> Union[Ok[None], Err]:
        """Validate a refactoring request before execution.
        
        Args:
            request: RefactoringRequest to validate
            
        Returns:
            Union[Ok[None], Err]: Ok if valid, Err with error message if invalid
            
        Validation checks:
            - Operation supported by this adapter
            - Language matches adapter language
            - Required parameters present
            - File exists and is readable
            - Parameters are valid for operation
        """
        pass


# AC_COMPLETE: AC-PHASE24.1.1-004 ✅
