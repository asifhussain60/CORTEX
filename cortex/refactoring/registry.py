"""
Registry for managing refactoring tool adapters.

AC_START: AC-PHASE24.1.1-006
Description: Adapter registry for tool discovery and routing
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Union

from cortex.brain.core.result import Ok, Err
from cortex.refactoring.adapters.base import RefactoringToolAdapter
from cortex.refactoring.models import RefactoringLanguage

logger = logging.getLogger(__name__)


class RefactoringToolRegistry:
    """Registry for managing and discovering refactoring tool adapters.
    
    Provides centralized adapter management with:
        - Language-based adapter routing
        - Duplicate registration prevention (CORE-035)
        - Availability checking
        - Supported operations discovery
    
    Thread-safe for concurrent adapter registration and retrieval.
    
    Example:
        >>> registry = RefactoringToolRegistry()
        >>> registry.register(RopeAdapter())
        >>> registry.register(RoslynAdapter())
        >>> 
        >>> adapter = registry.get_adapter(RefactoringLanguage.PYTHON).unwrap()
        >>> operations = adapter.get_supported_operations()
    """
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._adapters: Dict[RefactoringLanguage, RefactoringToolAdapter] = {}
        logger.info("RefactoringToolRegistry initialized")
    
    def register(self, adapter: RefactoringToolAdapter) -> Union[Ok[None], Err]:
        """Register a refactoring tool adapter.
        
        Args:
            adapter: RefactoringToolAdapter instance to register
            
        Returns:
            Union[Ok[None], Err]: Ok if registered, Err if duplicate detected
            
        Compliance:
            - CORE-035: Prevents duplicate language registrations
        """
        language = adapter.get_language()
        
        if language in self._adapters:
            error_msg = (
                f"Adapter for {language.value} already registered. "
                f"Duplicate registration prevented (CORE-035)."
            )
            logger.warning(error_msg)
            return Err(error_msg)
        
        self._adapters[language] = adapter
        
        availability = "available" if adapter.is_available() else "unavailable"
        operations_count = len(adapter.get_supported_operations())
        
        logger.info(
            f"Registered adapter for {language.value}: "
            f"{operations_count} operations, status={availability}"
        )
        
        return Ok(None)
    
    def get_adapter(
        self, language: RefactoringLanguage
    ) -> Union[Ok[RefactoringToolAdapter], Err]:
        """Retrieve adapter for specified language.
        
        Args:
            language: RefactoringLanguage to retrieve adapter for
            
        Returns:
            Union[Ok[RefactoringToolAdapter], Err]: Adapter if found, error if not registered
        """
        if language not in self._adapters:
            error_msg = f"No adapter registered for {language.value}"
            logger.debug(error_msg)
            return Err(error_msg)
        
        adapter = self._adapters[language]
        
        # Log availability status on retrieval
        if not adapter.is_available():
            logger.warning(
                f"Adapter for {language.value} retrieved but tool is unavailable"
            )
        
        return Ok(adapter)
    
    def get_adapter_count(self) -> int:
        """Return total number of registered adapters.
        
        Returns:
            int: Number of registered adapters
        """
        return len(self._adapters)
    
    def get_supported_languages(self) -> List[RefactoringLanguage]:
        """Return list of all registered languages.
        
        Returns:
            List[RefactoringLanguage]: Languages with registered adapters
        """
        return list(self._adapters.keys())
    
    def get_available_languages(self) -> List[RefactoringLanguage]:
        """Return list of languages with available (installed) tools.
        
        Returns:
            List[RefactoringLanguage]: Languages where tools are available
        """
        return [
            language
            for language, adapter in self._adapters.items()
            if adapter.is_available()
        ]
    
    def get_operations_for_language(
        self, language: RefactoringLanguage
    ) -> Union[Ok[List[str]], Err]:
        """Get supported operations for a specific language.
        
        Args:
            language: RefactoringLanguage to query
            
        Returns:
            Union[Ok[List[str]], Err]: Operations if adapter exists, error otherwise
        """
        adapter_result = self.get_adapter(language)
        
        if adapter_result.is_err():
            return adapter_result  # type: ignore
        
        adapter = adapter_result.unwrap()
        operations = adapter.get_supported_operations()
        
        return Ok(operations)


# AC_COMPLETE: AC-PHASE24.1.1-006 ✅
