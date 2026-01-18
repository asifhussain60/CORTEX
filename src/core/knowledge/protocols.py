"""
KnowledgeProvider Protocol Definition (AC-IKP-001-01).

Defines a typing.Protocol for structural subtyping of knowledge provider backends.
Allows duck-typing validation of any backend that implements the required interface.

Governance:
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from typing import Protocol, List, Dict, Any, runtime_checkable


@runtime_checkable
class KnowledgeProvider(Protocol):
    """
    Structural protocol for knowledge backend implementations.
    
    Any class implementing these methods and properties satisfies the protocol.
    This uses structural subtyping (duck typing) rather than nominal subtyping,
    allowing flexible backend implementations without explicit inheritance.
    
    This protocol is marked with @runtime_checkable to enable isinstance() checks
    at runtime, though this is primarily used for type hints in static analysis.
    """

    @property
    def is_loaded(self) -> bool:
        """
        Check if knowledge base is loaded and ready for queries.
        
        Returns:
            bool: True if knowledge base is loaded, False otherwise.
            
        Raises:
            RuntimeError: If check fails unexpectedly.
        """
        ...

    @property
    def entry_count(self) -> int:
        """
        Get number of knowledge entries in the backend.
        
        Returns:
            int: Count of knowledge entries, >= 0.
            
        Raises:
            RuntimeError: If count cannot be determined.
        """
        ...

    @property
    def domains(self) -> List[str]:
        """
        Get list of knowledge domains available.
        
        Returns:
            List[str]: List of domain names (e.g., ['technical', 'business', 'policy']).
                      Empty list if no domains available.
            
        Raises:
            RuntimeError: If domains cannot be retrieved.
        """
        ...

    def query(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Query knowledge with natural language text.
        
        Args:
            query_text: Natural language query string (non-empty).
            
        Returns:
            List[Dict[str, Any]]: List of matching knowledge entries.
                                 Empty list if no matches found.
                                 Each dict contains knowledge data.
            
        Raises:
            ValueError: If query_text is empty or invalid.
            RuntimeError: If query cannot be executed.
        """
        ...

    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all knowledge entries for a specific domain.
        
        Args:
            domain: Domain name to retrieve knowledge for.
            
        Returns:
            List[Dict[str, Any]]: List of knowledge entries in domain.
                                 Empty list if domain not found or empty.
            
        Raises:
            ValueError: If domain is empty.
            KeyError: If domain does not exist.
            RuntimeError: If retrieval fails.
        """
        ...

    def get_relevant_knowledge(
        self,
        intent_type: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get knowledge relevant to current operation context.
        
        Smart retrieval based on operation intent and surrounding context.
        Used by MasterOrchestrator to provide contextual knowledge suggestions.
        
        Args:
            intent_type: Type of operation intent (e.g., 'debug_issue', 'configure_system').
            context: Dictionary with context information:
                - 'user': username or identifier
                - 'operation': operation type or category
                - 'domain': current domain context
                - 'error_type': error classification (if applicable)
                - 'resource': resource being operated on
                - Other context-specific keys
            
        Returns:
            List[Dict[str, Any]]: List of relevant knowledge entries.
                                 Empty list if no relevant knowledge found.
                                 Sorted by relevance (most relevant first).
            
        Raises:
            ValueError: If intent_type is empty.
            TypeError: If context is not a dict.
            RuntimeError: If retrieval fails.
        """
        ...


__all__ = ['KnowledgeProvider']
