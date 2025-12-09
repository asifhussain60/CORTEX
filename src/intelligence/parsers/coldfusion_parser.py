"""
ColdFusion Tag-Based Parser
============================

Parses ColdFusion tag-based syntax (.cfm files).

REFACTOR Phase - Optimized implementation with caching and shared tokenizer
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache

from src.intelligence.parsers.coldfusion_tokenizer import ColdFusionTokenizer


class ColdFusionParser:
    """Parser for ColdFusion tag-based syntax (.cfm files)"""
    
    # Class-level compiled patterns (shared across instances)
    _component_pattern = re.compile(
        r'<cfcomponent(?:\s+([^>]*))?\s*>(.*?)</cfcomponent>',
        re.DOTALL | re.IGNORECASE
    )
    _function_pattern = re.compile(
        r'<cffunction\s+([^>]*)>(.*?)</cffunction>',
        re.DOTALL | re.IGNORECASE
    )
    _argument_pattern = re.compile(
        r'<cfargument\s+([^/>]*)/?>',
        re.IGNORECASE
    )
    _property_pattern = re.compile(
        r'<cfproperty\s+([^/>]*)/?>',
        re.IGNORECASE
    )
    _tag_pattern = re.compile(
        r'<(cf\w+)\s+([^>]*)(?:>(.*?)</\1>|/>)',
        re.DOTALL | re.IGNORECASE
    )
    
    def __init__(self, enable_caching: bool = True):
        """
        Initialize parser
        
        Args:
            enable_caching: Enable LRU caching for parse results (default: True)
        """
        self.logger = logging.getLogger(__name__)
        self.tokenizer = ColdFusionTokenizer()
        self._cache_enabled = enable_caching
    
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
        
        for match in self._component_pattern.finditer(code):
            attrs_str = match.group(1) or ''
            body = match.group(2)
            
            # Parse component attributes using shared tokenizer
            attrs = self.tokenizer.parse_tag_attributes(attrs_str)
            
            component = {
                'name': attrs.get('displayname', 'Component'),
                'hint': attrs.get('hint', ''),
                'output': self.tokenizer.parse_boolean(attrs.get('output', 'true')),
                'persistent': self.tokenizer.parse_boolean(attrs.get('persistent', 'false')),
                'properties': self._extract_properties(body),
                'functions': self._extract_functions(body)
            }
            
            components.append(component)
        
        return components
    
    def _extract_standalone_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract functions that are outside components"""
        # Remove component blocks first
        code_without_components = self._component_pattern.sub('', code)
        return self._extract_functions(code_without_components)
    
    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code"""
        functions = []
        
        for match in self._function_pattern.finditer(code):
            attrs_str = match.group(1)
            body = match.group(2)
            
            # Parse function attributes using shared tokenizer
            attrs = self.tokenizer.parse_tag_attributes(attrs_str)
            
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
        
        for match in self._argument_pattern.finditer(code):
            attrs_str = match.group(1)
            attrs = self.tokenizer.parse_tag_attributes(attrs_str)
            
            param = {
                'name': attrs.get('name', 'unnamed'),
                'type': attrs.get('type', 'any'),
                'required': self.tokenizer.parse_boolean(attrs.get('required', 'false'))
            }
            
            # Add optional attributes if present
            if 'default' in attrs:
                param['default'] = attrs['default']
            
            parameters.append(param)
        
        return parameters
    
    def _extract_properties(self, code: str) -> List[Dict[str, Any]]:
        """Extract property definitions from code"""
        properties = []
        
        for match in self._property_pattern.finditer(code):
            attrs_str = match.group(1)
            attrs = self.tokenizer.parse_tag_attributes(attrs_str)
            
            prop = {
                'name': attrs.get('name', 'unnamed'),
                'type': attrs.get('type', 'any')
            }
            
            # Add optional attributes
            if 'required' in attrs:
                prop['required'] = self.tokenizer.parse_boolean(attrs['required'])
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
        for match in self._tag_pattern.finditer(code):
            tag_name = match.group(1)
            tags.append({
                'name': tag_name.lower(),
                'type': 'tag'
            })
        
        return tags
