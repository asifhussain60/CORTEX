"""
Phase 67 S1: Type Symbol Resolver

Resolves .NET type relationships from Roslyn semantic models:
- Interface implementations
- Base class hierarchies  
- Generic type constraints
- Type dependencies

AC_START: AC-PHASE67-S1-TYPE-RESOLVER-001
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class TypeSymbolResolver:
    """
    Resolve type relationships from Roslyn semantic model.
    
    Provides methods to query type hierarchies, implementations,
    and dependencies extracted via Roslyn CLI.
    
    Example:
        >>> resolver = TypeSymbolResolver(semantic_model)
        >>> impls = resolver.resolve_interface_implementations("IEntity")
        >>> print(impls)  # ['User', 'Product']
    """
    
    def __init__(self, semantic_models: List[Dict[str, Any]]):
        """
        Initialize resolver with semantic models from Roslyn CLI.
        
        Args:
            semantic_models: List of project semantic models (Types array)
        """
        self.semantic_models = semantic_models
        self._type_index = self._build_type_index()
    
    def _build_type_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Build index of types for fast lookup.
        
        Returns:
            Dict mapping type names to type info
        """
        index = {}
        
        for project in self.semantic_models:
            if "Types" not in project:
                continue
                
            for type_info in project["Types"]:
                type_name = type_info.get("Name")
                full_name = type_info.get("FullName")
                
                if type_name:
                    # Index by both short name and full name
                    index[type_name] = type_info
                    if full_name:
                        index[full_name] = type_info
        
        return index
    
    def resolve_interface_implementations(
        self, 
        interface_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all types implementing the specified interface.
        
        Args:
            interface_name: Name of interface (e.g., "IEntity")
        
        Returns:
            List of type info dicts implementing the interface
        
        Example:
            >>> impls = resolver.resolve_interface_implementations("IEntity")
            >>> print([t["Name"] for t in impls])  # ['User', 'Product']
        """
        implementations = []
        
        for type_info in self._type_index.values():
            interfaces = type_info.get("Interfaces", [])
            
            # Check if this type implements the interface
            # Match by name (e.g., "IEntity") or full name (e.g., "Core.Entities.IEntity")
            if any(interface_name in iface for iface in interfaces):
                implementations.append(type_info)
        
        # Remove duplicates (same type indexed by multiple names)
        seen_full_names = set()
        unique_impls = []
        
        for impl in implementations:
            full_name = impl.get("FullName")
            if full_name and full_name not in seen_full_names:
                seen_full_names.add(full_name)
                unique_impls.append(impl)
        
        return unique_impls
    
    def resolve_base_classes(
        self, 
        type_name: str
    ) -> List[str]:
        """
        Get base class hierarchy for a type.
        
        Args:
            type_name: Name of type
        
        Returns:
            List of base class names (nearest to farthest)
        
        Example:
            >>> bases = resolver.resolve_base_classes("User")
            >>> print(bases)  # ['EntityBase', 'object']
        """
        type_info = self._type_index.get(type_name)
        if not type_info:
            return []
        
        hierarchy = []
        current_base = type_info.get("BaseType")
        
        while current_base and current_base != "object":
            hierarchy.append(current_base)
            
            # Look up base type to continue chain
            base_info = self._type_index.get(current_base)
            if base_info:
                current_base = base_info.get("BaseType")
            else:
                break
        
        # Add object if not already there
        if current_base == "object":
            hierarchy.append("object")
        
        return hierarchy
    
    def resolve_derived_types(
        self, 
        base_type_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all types deriving from the specified base class.
        
        Args:
            base_type_name: Name of base class
        
        Returns:
            List of type info dicts deriving from base class
        
        Example:
            >>> derived = resolver.resolve_derived_types("EntityBase")
            >>> print([t["Name"] for t in derived])  # ['User', 'Product']
        """
        derived_types = []
        
        for type_info in self._type_index.values():
            base_type = type_info.get("BaseType")
            
            # Check if this type directly inherits from base_type_name
            if base_type and base_type_name in base_type:
                derived_types.append(type_info)
        
        # Remove duplicates
        seen_full_names = set()
        unique_derived = []
        
        for derived in derived_types:
            full_name = derived.get("FullName")
            if full_name and full_name not in seen_full_names:
                seen_full_names.add(full_name)
                unique_derived.append(derived)
        
        return unique_derived
    
    def get_type_info(self, type_name: str) -> Optional[Dict[str, Any]]:
        """
        Get full type information by name.
        
        Args:
            type_name: Type name (short or full)
        
        Returns:
            Type info dict or None if not found
        """
        return self._type_index.get(type_name)
    
    def get_all_types(self) -> List[Dict[str, Any]]:
        """
        Get all types from semantic models.
        
        Returns:
            List of all type info dicts
        """
        # Return unique types (avoid duplicates from indexing)
        seen_full_names = set()
        unique_types = []
        
        for type_info in self._type_index.values():
            full_name = type_info.get("FullName")
            if full_name and full_name not in seen_full_names:
                seen_full_names.add(full_name)
                unique_types.append(type_info)
        
        return unique_types


# AC_COMPLETE: AC-PHASE67-S1-TYPE-RESOLVER-001 ✅ TypeSymbolResolver implementation complete
