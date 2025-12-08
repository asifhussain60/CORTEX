"""
ColdFusion Tag-Based Parser
============================

Minimal implementation to pass RED phase tests.
Parses ColdFusion tag-based syntax (.cfm files).

GREEN Phase Implementation - Minimal Viable Product
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class ColdFusionParser:
    """Parser for ColdFusion tag-based syntax (.cfm files)"""
    
    def __init__(self):
        """Initialize parser with regex patterns"""
        # Component extraction pattern (handles both with and without attributes)
        self.component_pattern = re.compile(
            r'<cfcomponent(?:\s+([^>]*))?\s*>(.*?)</cfcomponent>',
            re.DOTALL | re.IGNORECASE
        )
        
        # Function extraction pattern
        self.function_pattern = re.compile(
            r'<cffunction\s+([^>]*)>(.*?)</cffunction>',
            re.DOTALL | re.IGNORECASE
        )
        
        # Argument extraction pattern
        self.argument_pattern = re.compile(
            r'<cfargument\s+([^/>]*)/?>',
            re.IGNORECASE
        )
        
        # Property extraction pattern
        self.property_pattern = re.compile(
            r'<cfproperty\s+([^/>]*)/?>',
            re.IGNORECASE
        )
        
        # Generic tag pattern for basic parsing
        self.tag_pattern = re.compile(
            r'<(cf\w+)\s+([^>]*)(?:>(.*?)</\1>|/>)',
            re.DOTALL | re.IGNORECASE
        )
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse ColdFusion file and extract structure
        
        Args:
            file_path: Path to .cfm or .cfc file
            
        Returns:
            Dictionary with parsed structure
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        result = self.parse_code(code)
        result['file_path'] = str(file_path)
        return result
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        Parse ColdFusion code string
        
        Args:
            code: ColdFusion source code
            
        Returns:
            Dictionary with parsed structure
        """
        result = {
            'language': 'coldfusion',
            'components': [],
            'functions': [],
            'tags': [],
            'errors': [],
            'warnings': []
        }
        
        if not code or not code.strip():
            return result
        
        try:
            # Extract components
            result['components'] = self._extract_components(code)
            
            # Extract standalone functions (outside components)
            result['functions'] = self._extract_standalone_functions(code)
            
            # Extract generic tags for basic parsing
            result['tags'] = self._extract_tags(code)
            
        except Exception as e:
            result['errors'].append({
                'message': str(e),
                'type': 'parsing_error'
            })
        
        return result
    
    def _extract_components(self, code: str) -> List[Dict[str, Any]]:
        """Extract component definitions from code"""
        components = []
        
        for match in self.component_pattern.finditer(code):
            attrs_str = match.group(1) or ''
            body = match.group(2)
            
            # Parse component attributes
            attrs = self._parse_attributes(attrs_str)
            
            component = {
                'name': attrs.get('displayname', 'Component'),
                'hint': attrs.get('hint', ''),
                'output': self._parse_boolean(attrs.get('output', 'true')),
                'persistent': self._parse_boolean(attrs.get('persistent', 'false')),
                'properties': self._extract_properties(body),
                'functions': self._extract_functions(body)
            }
            
            components.append(component)
        
        return components
    
    def _extract_standalone_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract functions that are outside components"""
        # Remove component blocks first
        code_without_components = self.component_pattern.sub('', code)
        return self._extract_functions(code_without_components)
    
    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code"""
        functions = []
        
        for match in self.function_pattern.finditer(code):
            attrs_str = match.group(1)
            body = match.group(2)
            
            # Parse function attributes
            attrs = self._parse_attributes(attrs_str)
            
            function = {
                'name': attrs.get('name', 'unnamed'),
                'access': attrs.get('access', 'public'),
                'returntype': attrs.get('returntype', 'any'),
                'hint': attrs.get('hint', ''),
                'returnformat': attrs.get('returnformat', ''),
                'parameters': self._extract_parameters(body)
            }
            
            # Clean up empty optional fields
            if not function['hint']:
                del function['hint']
            if not function['returnformat']:
                del function['returnformat']
            
            functions.append(function)
        
        return functions
    
    def _extract_parameters(self, code: str) -> List[Dict[str, Any]]:
        """Extract function parameters from cfargument tags"""
        parameters = []
        
        for match in self.argument_pattern.finditer(code):
            attrs_str = match.group(1)
            attrs = self._parse_attributes(attrs_str)
            
            param = {
                'name': attrs.get('name', 'unnamed'),
                'type': attrs.get('type', 'any'),
                'required': self._parse_boolean(attrs.get('required', 'false'))
            }
            
            # Add optional attributes if present
            if 'default' in attrs:
                param['default'] = attrs['default']
            
            parameters.append(param)
        
        return parameters
    
    def _extract_properties(self, code: str) -> List[Dict[str, Any]]:
        """Extract property definitions from code"""
        properties = []
        
        for match in self.property_pattern.finditer(code):
            attrs_str = match.group(1)
            attrs = self._parse_attributes(attrs_str)
            
            prop = {
                'name': attrs.get('name', 'unnamed'),
                'type': attrs.get('type', 'any')
            }
            
            # Add optional attributes
            if 'required' in attrs:
                prop['required'] = self._parse_boolean(attrs['required'])
            if 'default' in attrs:
                prop['default'] = attrs['default']
            if 'pattern' in attrs:
                prop['pattern'] = attrs['pattern']
            if 'fieldtype' in attrs:
                prop['fieldtype'] = attrs['fieldtype']
            if 'generator' in attrs:
                prop['generator'] = attrs['generator']
            if 'length' in attrs:
                prop['length'] = attrs['length']
            
            properties.append(prop)
        
        return properties
    
    def _extract_tags(self, code: str) -> List[Dict[str, Any]]:
        """Extract generic CF tags for basic parsing"""
        tags = []
        
        # Simple extraction - just detect presence of tags
        for match in self.tag_pattern.finditer(code):
            tag_name = match.group(1)
            tags.append({
                'name': tag_name.lower(),
                'type': 'tag'
            })
        
        return tags
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """
        Parse attribute string into dictionary
        
        Example: 'name="test" type="string" required="true"'
        Returns: {'name': 'test', 'type': 'string', 'required': 'true'}
        """
        attrs = {}
        
        # Pattern to match attribute="value" or attribute='value'
        attr_pattern = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']')
        
        for match in attr_pattern.finditer(attrs_str):
            key = match.group(1).lower()
            value = match.group(2)
            attrs[key] = value
        
        return attrs
    
    def _parse_boolean(self, value: str) -> bool:
        """Parse string boolean value"""
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', 'yes', '1')
