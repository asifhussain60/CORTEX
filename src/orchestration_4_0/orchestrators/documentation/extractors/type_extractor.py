"""
Type Extractor - Analyze type hints and generate type documentation

Extracts and formats Python type hints for documentation.
"""

import ast
from typing import Any, Dict, List, Optional, Set


class TypeExtractor:
    """
    Extracts and formats type information from Python code
    
    Handles:
    - Basic types (int, str, bool, etc.)
    - Generic types (List[int], Dict[str, Any], etc.)
    - Optional types (Optional[str], Union[str, None])
    - Custom class types
    - Type aliases
    """
    
    def __init__(self):
        self.type_aliases: Dict[str, str] = {}
    
    def extract_type_info(self, annotation: Optional[ast.expr]) -> Dict[str, Any]:
        """
        Extract detailed type information from an annotation
        
        Args:
            annotation: AST annotation node
            
        Returns:
            Dictionary with type information:
            - 'raw': Raw string representation
            - 'base': Base type name
            - 'args': Type arguments (for generics)
            - 'optional': Whether type is Optional
            - 'complexity': Type complexity score (0-10)
        """
        if annotation is None:
            return {
                'raw': 'Any',
                'base': 'Any',
                'args': [],
                'optional': False,
                'complexity': 0
            }
        
        raw_type = ast.unparse(annotation)
        
        # Parse the type structure
        base_type = self._get_base_type(annotation)
        type_args = self._get_type_args(annotation)
        is_optional = self._is_optional(annotation)
        complexity = self._calculate_complexity(annotation)
        
        return {
            'raw': raw_type,
            'base': base_type,
            'args': type_args,
            'optional': is_optional,
            'complexity': complexity
        }
    
    def _get_base_type(self, annotation: ast.expr) -> str:
        """Extract the base type name"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr
        elif isinstance(annotation, ast.Subscript):
            return self._get_base_type(annotation.value)
        elif isinstance(annotation, ast.Constant):
            return type(annotation.value).__name__
        return 'Unknown'
    
    def _get_type_args(self, annotation: ast.expr) -> List[str]:
        """Extract type arguments from generic types"""
        if not isinstance(annotation, ast.Subscript):
            return []
        
        args = []
        slice_value = annotation.slice
        
        if isinstance(slice_value, ast.Tuple):
            for elt in slice_value.elts:
                args.append(ast.unparse(elt))
        else:
            args.append(ast.unparse(slice_value))
        
        return args
    
    def _is_optional(self, annotation: ast.expr) -> bool:
        """Check if type is Optional"""
        raw = ast.unparse(annotation)
        return 'Optional[' in raw or 'Union[' in raw and 'None' in raw
    
    def _calculate_complexity(self, annotation: ast.expr) -> int:
        """
        Calculate type complexity score (0-10)
        
        - Simple types (int, str): 0
        - Generic with one arg (List[int]): 2
        - Generic with multiple args (Dict[str, int]): 3
        - Nested generics (List[Dict[str, Any]]): 5+
        - Complex unions: 7+
        """
        if isinstance(annotation, ast.Name):
            return 0
        elif isinstance(annotation, ast.Attribute):
            return 1
        elif isinstance(annotation, ast.Subscript):
            base_complexity = 2
            
            # Add complexity for each type argument
            args = self._get_type_args(annotation)
            arg_complexity = len(args) - 1
            
            # Check for nested generics
            for arg in args:
                if '[' in arg:
                    arg_complexity += 2
            
            return min(base_complexity + arg_complexity, 10)
        
        return 0
    
    def format_type_for_docs(self, type_info: Dict[str, Any]) -> str:
        """
        Format type information for documentation
        
        Args:
            type_info: Type information dict from extract_type_info
            
        Returns:
            Formatted type string suitable for documentation
        """
        raw_type = type_info['raw']
        
        # Simplify common patterns
        simplified = raw_type.replace('typing.', '')
        simplified = simplified.replace('Union[', '')
        simplified = simplified.replace(', None]', ' | None')
        
        if type_info['optional'] and not ('|' in simplified or 'Optional' in simplified):
            simplified = f"Optional[{simplified}]"
        
        return simplified
    
    def extract_return_type_description(self, docstring: Optional[str]) -> Optional[str]:
        """
        Extract return type description from docstring
        
        Looks for Returns: section in Google-style docstrings
        
        Args:
            docstring: Method or function docstring
            
        Returns:
            Description of return type, or None if not found
        """
        if not docstring:
            return None
        
        lines = docstring.split('\n')
        in_returns_section = False
        description_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('Returns:'):
                in_returns_section = True
                continue
            elif in_returns_section:
                # Check if we hit another section
                if stripped.endswith(':') and len(stripped.split()) == 1:
                    break
                if stripped:
                    description_lines.append(stripped)
        
        return ' '.join(description_lines) if description_lines else None
    
    def extract_param_descriptions(self, docstring: Optional[str]) -> Dict[str, str]:
        """
        Extract parameter descriptions from docstring
        
        Parses Args: section in Google-style docstrings
        
        Args:
            docstring: Method or function docstring
            
        Returns:
            Dict mapping parameter names to descriptions
        """
        if not docstring:
            return {}
        
        lines = docstring.split('\n')
        in_args_section = False
        param_descriptions = {}
        current_param = None
        current_desc = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('Args:'):
                in_args_section = True
                continue
            elif in_args_section:
                # Check if we hit another section
                if stripped.endswith(':') and len(stripped.split()) == 1:
                    if current_param:
                        param_descriptions[current_param] = ' '.join(current_desc)
                    break
                
                # Check if this is a parameter line (param_name: description)
                if ':' in stripped and not stripped.startswith(' '):
                    # Save previous parameter
                    if current_param:
                        param_descriptions[current_param] = ' '.join(current_desc)
                    
                    # Start new parameter
                    parts = stripped.split(':', 1)
                    current_param = parts[0].strip()
                    current_desc = [parts[1].strip()] if len(parts) > 1 else []
                elif current_param and stripped:
                    # Continuation of current parameter description
                    current_desc.append(stripped)
        
        # Save last parameter
        if current_param:
            param_descriptions[current_param] = ' '.join(current_desc)
        
        return param_descriptions
