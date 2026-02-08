"""
RefactoringOrchestrator - Unified API for all refactoring tool adapters.

AC_START: AC-PHASE24.6-002
Description: Orchestrator for coordinating all refactoring tool adapters
Authority: Phase 24.6 - Orchestration + MCP Exposure
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-027 (audit)

Coordinates:
    - Adapter registration and discovery
    - Language-based routing
    - Unified refactoring API
    - Statistics and reporting

Integrates:
    - Python (Rope) - 11 operations
    - C# (Roslyn) - 8 operations
    - TypeScript/JavaScript - 5 operations
    Total: 24 operations across 3 languages
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Union

from cortex.brain.core.result import Ok, Err
from cortex.refactoring.adapters.base import RefactoringToolAdapter
from cortex.refactoring.adapters.rope_adapter import RopeAdapter
from cortex.refactoring.adapters.typescript_adapter import TypeScriptAdapter
from cortex.refactoring.models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)
from cortex.refactoring.registry import RefactoringToolRegistry

# Phase 51: Enhanced response template with semantic color coding
from cortex.agents.core.response_template_generator import ResponseTemplate

logger = logging.getLogger(__name__)


class RefactoringOrchestrator:
    """Orchestrator for coordinating all refactoring tool adapters.
    
    Provides a unified API for executing refactoring operations across multiple
    programming languages. Automatically registers all available adapters and
    routes requests to the appropriate tool.
    
    Supported Languages:
        - Python (via Rope): 11 operations
        - C# (via Roslyn): 8 operations  
        - TypeScript/JavaScript: 5 operations
    
    Features:
        - Automatic adapter discovery and registration
        - Language-based routing
        - Graceful degradation when tools unavailable
        - Statistics and status reporting
        - Full audit logging (CORE-027)
    
    Example:
        >>> orchestrator = RefactoringOrchestrator()
        >>> 
        >>> # Get supported languages
        >>> languages = orchestrator.get_supported_languages()
        >>> 
        >>> # Execute refactoring
        >>> request = RefactoringRequest(
        ...     operation="rename",
        ...     file_path=Path("app.py"),
        ...     language=RefactoringLanguage.PYTHON,
        ...     parameters={"offset": 100, "new_name": "process_data"}
        ... )
        >>> result = orchestrator.execute_refactoring(request)
    """
    
    def __init__(self) -> None:
        """Initialize RefactoringOrchestrator with all available adapters."""
        self.registry = RefactoringToolRegistry()
        self._registered_count = 0
        
        # Auto-register all available adapters
        self._register_adapters()
        
        logger.info(
            f"RefactoringOrchestrator initialized with {self._registered_count} adapters"
        )
    
    def _register_adapters(self) -> None:
        """Register all available refactoring tool adapters.
        
        Attempts to register:
            - RopeAdapter (Python)
            - RoslynAdapter (C#) - if available
            - TypeScriptAdapter (TypeScript/JavaScript)
        
        Gracefully handles registration failures.
        """
        adapters_to_register: List[RefactoringToolAdapter] = [
            RopeAdapter(),
            TypeScriptAdapter(),
        ]
        
        # Try to register RoslynAdapter (may not be imported in all environments)
        try:
            from cortex.refactoring.adapters.roslyn_adapter import RoslynAdapter
            adapters_to_register.append(RoslynAdapter())
        except ImportError:
            logger.debug("RoslynAdapter not available - skipping registration")
        
        for adapter in adapters_to_register:
            result = self.registry.register(adapter)
            if result.is_ok():
                self._registered_count += 1
            else:
                logger.warning(f"Failed to register adapter: {result.unwrap_err()}")
    
    def get_supported_languages(self) -> List[RefactoringLanguage]:
        """Get list of all supported languages (adapters registered).
        
        Returns:
            List of RefactoringLanguage enums for registered adapters
        """
        return self.registry.get_supported_languages()
    
    def get_available_languages(self) -> List[RefactoringLanguage]:
        """Get list of currently available languages (tools installed and accessible).
        
        Returns:
            List of RefactoringLanguage enums where adapter.is_available() is True
        """
        return self.registry.get_available_languages()
    
    def get_operations_for_language(
        self, language: RefactoringLanguage
    ) -> Union[Ok[List[str]], Err]:
        """Get supported operations for a specific language.
        
        Args:
            language: RefactoringLanguage to query
            
        Returns:
            Ok[List[str]] with operation names, or Err if language not supported
        """
        adapter_result = self.registry.get_adapter(language)
        
        if adapter_result.is_err():
            return adapter_result  # type: ignore
        
        adapter = adapter_result.unwrap()
        operations = adapter.get_supported_operations()
        
        return Ok(operations)
    
    def get_all_operations(self) -> Dict[RefactoringLanguage, List[str]]:
        """Get all operations for all supported languages.
        
        Returns:
            Dictionary mapping RefactoringLanguage to list of operation names
        """
        operations_map = {}
        
        for language in self.get_supported_languages():
            result = self.get_operations_for_language(language)
            if result.is_ok():
                operations_map[language] = result.unwrap()
        
        return operations_map
    
    def execute_refactoring(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute a refactoring operation.
        
        Routes the request to the appropriate adapter based on language,
        executes the refactoring, and returns the result.
        
        Args:
            request: RefactoringRequest containing operation details
            
        Returns:
            Ok[RefactoringResult] if successful, Err with error message if failed
            
        Example:
            >>> request = RefactoringRequest(
            ...     operation="extract_function",
            ...     file_path=Path("app.py"),
            ...     language=RefactoringLanguage.PYTHON,
            ...     parameters={
            ...         "start_offset": 100,
            ...         "end_offset": 200,
            ...         "new_name": "helper"
            ...     }
            ... )
            >>> result = orchestrator.execute_refactoring(request)
        """
        # Map JavaScript to TypeScript adapter (since TypeScript handles both)
        language = request.language
        if language == RefactoringLanguage.JAVASCRIPT:
            language = RefactoringLanguage.TYPESCRIPT
        
        # Get adapter for language
        adapter_result = self.registry.get_adapter(language)
        
        if adapter_result.is_err():
            error_msg = adapter_result.unwrap_err()
            logger.error(f"Adapter retrieval failed: {error_msg}")
            return Err(error_msg)
        
        adapter = adapter_result.unwrap()
        
        # Log refactoring attempt
        logger.info(
            f"Executing {request.operation} on {request.file_path.name} "
            f"(language={request.language.value})"
        )
        
        # Execute refactoring
        result = adapter.execute_refactoring(request)
        
        # Log result
        if result.is_ok():
            refactoring_result = result.unwrap()
            logger.info(
                f"Refactoring succeeded: {refactoring_result.description} "
                f"(modified {len(refactoring_result.modified_files)} file(s))"
            )
        else:
            error_msg = result.unwrap_err()
            logger.error(f"Refactoring failed: {error_msg}")
        
        return result
    
    def get_adapter_status(self) -> Dict[RefactoringLanguage, Dict[str, Any]]:
        """Get status information for all registered adapters.
        
        Returns:
            Dictionary mapping language to status dict with:
                - available: bool (is tool installed and accessible)
                - operations_count: int (number of supported operations)
                - operations: List[str] (operation names)
        """
        status = {}
        
        for language in self.get_supported_languages():
            adapter_result = self.registry.get_adapter(language)
            
            if adapter_result.is_ok():
                adapter = adapter_result.unwrap()
                operations = adapter.get_supported_operations()
                
                status[language] = {
                    "available": adapter.is_available(),
                    "operations_count": len(operations),
                    "operations": operations,
                }
        
        return status
    
    def get_total_operations_count(self) -> int:
        """Get total number of operations across all languages.
        
        Returns:
            Total count of unique operations
        """
        all_operations = self.get_all_operations()
        
        # Count all operations (may include duplicates across languages)
        total = sum(len(ops) for ops in all_operations.values())
        
        return total


# AC_COMPLETE: AC-PHASE24.6-002 ✅ RefactoringOrchestrator implementation complete
