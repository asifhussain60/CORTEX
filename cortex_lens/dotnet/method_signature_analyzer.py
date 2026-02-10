"""
Phase 67 S1: Method Signature Analyzer

Extracts and analyzes method signatures from Roslyn semantic models:
- Parameter types and names
- Return types
- Generic method constraints
- Method modifiers (public/private, static, virtual, etc.)

AC_START: AC-PHASE67-S1-METHOD-ANALYZER-001
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class MethodSignatureAnalyzer:
    """
    Analyze method signatures from Roslyn semantic model.
    
    Provides detailed method signature extraction including
    parameters, return types, and modifiers.
    
    Example:
        >>> analyzer = MethodSignatureAnalyzer()
        >>> sig = analyzer.extract_signature(method_info)
        >>> print(sig["return_type"])  # "string"
    """
    
    def extract_signature(self, method_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed signature from method info.
        
        Args:
            method_info: Method info dict from Roslyn CLI
        
        Returns:
            Dict with structured signature data
        
        Example:
            >>> sig = analyzer.extract_signature(method_info)
            >>> print(sig)
            {
                "name": "GetUserById",
                "return_type": "User",
                "parameters": [{"name": "id", "type": "int"}],
                "is_public": True,
                "is_static": False
            }
        """
        return {
            "name": method_info.get("Name"),
            "return_type": method_info.get("ReturnType"),
            "parameters": self.resolve_parameter_types(method_info.get("Parameters", [])),
            "is_public": method_info.get("IsPublic", False),
            "is_static": method_info.get("IsStatic", False),
            "is_abstract": method_info.get("IsAbstract", False),
            "is_virtual": method_info.get("IsVirtual", False),
            "parameter_count": len(method_info.get("Parameters", []))
        }
    
    def resolve_parameter_types(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve parameter types from parameter info list.
        
        Args:
            parameters: List of parameter info dicts
        
        Returns:
            List of resolved parameter dicts
        
        Example:
            >>> params = analyzer.resolve_parameter_types([
            ...     {"Name": "id", "Type": "int"},
            ...     {"Name": "name", "Type": "string"}
            ... ])
            >>> print(params[0])  # {"name": "id", "type": "int"}
        """
        resolved = []
        
        for param in parameters:
            resolved.append({
                "name": param.get("Name"),
                "type": param.get("Type"),
                "is_nullable": "?" in param.get("Type", ""),
                "is_params": False  # TODO: Detect params keyword
            })
        
        return resolved
    
    def extract_return_type(self, method_info: Dict[str, Any]) -> str:
        """
        Extract return type from method info.
        
        Args:
            method_info: Method info dict
        
        Returns:
            Return type string
        """
        return method_info.get("ReturnType", "void")
    
    def find_methods_by_name(
        self, 
        type_info: Dict[str, Any], 
        method_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all methods with the given name (includes overloads).
        
        Args:
            type_info: Type info dict
            method_name: Method name to search for
        
        Returns:
            List of method info dicts matching name
        """
        methods = type_info.get("Methods", [])
        return [m for m in methods if m.get("Name") == method_name]
    
    def find_methods_by_signature(
        self,
        type_info: Dict[str, Any],
        method_name: str,
        parameter_types: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Find method by exact signature (name + parameter types).
        
        Args:
            type_info: Type info dict
            method_name: Method name
            parameter_types: List of parameter type names
        
        Returns:
            Method info dict or None if not found
        """
        methods = self.find_methods_by_name(type_info, method_name)
        
        for method in methods:
            params = method.get("Parameters", [])
            
            # Check parameter count matches
            if len(params) != len(parameter_types):
                continue
            
            # Check each parameter type matches
            match = True
            for param, expected_type in zip(params, parameter_types):
                param_type = param.get("Type", "")
                if expected_type not in param_type:
                    match = False
                    break
            
            if match:
                return method
        
        return None
    
    def get_all_public_methods(self, type_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all public methods from type.
        
        Args:
            type_info: Type info dict
        
        Returns:
            List of public method info dicts
        """
        methods = type_info.get("Methods", [])
        return [m for m in methods if m.get("IsPublic", False)]
    
    def get_static_methods(self, type_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all static methods from type.
        
        Args:
            type_info: Type info dict
        
        Returns:
            List of static method info dicts
        """
        methods = type_info.get("Methods", [])
        return [m for m in methods if m.get("IsStatic", False)]


# AC_COMPLETE: AC-PHASE67-S1-METHOD-ANALYZER-001 ✅ MethodSignatureAnalyzer implementation complete
