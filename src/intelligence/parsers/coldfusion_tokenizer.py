"""
ColdFusion Tokenizer
====================

Shared tokenization logic for ColdFusion parser and analyzer.
Extracts and processes ColdFusion tag attributes and CFScript syntax elements.

REFACTOR Phase - Extract common tokenization logic
"""

import re
from typing import Dict, List, Tuple, Optional, Any


class ColdFusionTokenizer:
    """Shared tokenizer for ColdFusion syntax parsing"""
    
    # Compiled regex patterns (shared across instances for performance)
    ATTR_PATTERN = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']')
    CFSCRIPT_ATTR_PATTERN = re.compile(r'(\w+)\s*=\s*(?:["\']([^"\']*)["\']|(\w+))')
    
    @staticmethod
    def parse_tag_attributes(attrs_str: str) -> Dict[str, str]:
        """
        Parse tag-based attribute string into dictionary
        
        Example: 'name="test" type="string" required="true"'
        Returns: {'name': 'test', 'type': 'string', 'required': 'true'}
        
        Args:
            attrs_str: Attribute string from tag
            
        Returns:
            Dictionary of lowercase attribute keys to values
        """
        attrs = {}
        
        for match in ColdFusionTokenizer.ATTR_PATTERN.finditer(attrs_str):
            key = match.group(1).lower()
            value = match.group(2)
            attrs[key] = value
        
        return attrs
    
    @staticmethod
    def parse_cfscript_attributes(attrs_str: str) -> Dict[str, str]:
        """
        Parse CFScript attribute string
        
        Example: 'displayname="Test" hint="My hint" output=false'
        Returns: {'displayname': 'Test', 'hint': 'My hint', 'output': 'false'}
        
        Args:
            attrs_str: Attribute string from CFScript
            
        Returns:
            Dictionary of lowercase attribute keys to values
        """
        attrs = {}
        
        for match in ColdFusionTokenizer.CFSCRIPT_ATTR_PATTERN.finditer(attrs_str):
            key = match.group(1).lower()
            value = match.group(2) or match.group(3) or ''
            attrs[key] = value
        
        return attrs
    
    @staticmethod
    def parse_boolean(value: str) -> bool:
        """
        Parse string boolean value
        
        Args:
            value: String representation of boolean
            
        Returns:
            Boolean value
        """
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', 'yes', '1')
    
    @staticmethod
    def parse_cfscript_parameters(params_str: str) -> List[Dict[str, Any]]:
        """
        Parse CFScript function parameters
        
        Example: 'required numeric id, boolean includeDetails=false'
        Returns: [
            {'name': 'id', 'type': 'numeric', 'required': True},
            {'name': 'includeDetails', 'type': 'boolean', 'required': False, 'default': 'false'}
        ]
        
        Args:
            params_str: Parameter string from function definition
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        if not params_str.strip():
            return parameters
        
        # Split by comma (basic approach)
        param_parts = params_str.split(',')
        
        for part in param_parts:
            part = part.strip()
            if not part:
                continue
            
            # Pattern: [required] [type] name[=default]
            param = {'name': '', 'type': 'any', 'required': False}
            
            # Check for 'required'
            if 'required' in part.lower():
                param['required'] = True
                part = re.sub(r'\brequired\b', '', part, flags=re.IGNORECASE).strip()
            
            # Check for default value
            if '=' in part:
                part, default = part.split('=', 1)
                param['default'] = default.strip()
                part = part.strip()
            
            # Split remaining into type and name
            tokens = part.split()
            if len(tokens) >= 2:
                param['type'] = tokens[0]
                param['name'] = tokens[1]
            elif len(tokens) == 1:
                param['name'] = tokens[0]
            
            if param['name']:
                parameters.append(param)
        
        return parameters
    
    @staticmethod
    def extract_javadoc_comments(code: str) -> Dict[int, str]:
        """
        Extract JavaDoc-style comments and their positions
        
        Args:
            code: Source code to scan
            
        Returns:
            Dictionary mapping end position to comment text
        """
        javadoc_pattern = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
        doc_comments = {}
        
        for match in javadoc_pattern.finditer(code):
            doc_text = match.group(1).strip()
            doc_comments[match.end()] = doc_text
        
        return doc_comments
