"""
ColdFusion CFScript Analyzer
=============================

Minimal implementation to pass RED phase tests.
Analyzes ColdFusion CFScript syntax (.cfc files).

GREEN Phase Implementation - Minimal Viable Product
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class ColdFusionAnalyzer:
    """Analyzer for ColdFusion CFScript syntax (.cfc files)"""
    
    def __init__(self):
        """Initialize analyzer with regex patterns"""
        # Component pattern (CFScript style)
        self.component_pattern = re.compile(
            r'component\s+([^{]*)\{(.*?)\}(?:\s*$)',
            re.DOTALL | re.IGNORECASE
        )
        
        # Function pattern (CFScript style)
        self.function_pattern = re.compile(
            r'(?:(public|private|remote|package)\s+)?(?:(\w+)\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s+([^{]*))?(?:\s*\{([^}]*)\})?',
            re.DOTALL | re.IGNORECASE
        )
        
        # Property pattern (CFScript style)
        self.property_pattern = re.compile(
            r'property\s+([^;]+);',
            re.IGNORECASE
        )
        
        # Variable declaration pattern
        self.var_pattern = re.compile(
            r'(?:var|local\.|variables\.)\s+(\w+)\s*=',
            re.IGNORECASE
        )
        
        # Return statement pattern
        self.return_pattern = re.compile(
            r'\breturn\b',
            re.IGNORECASE
        )
        
        # JavaDoc comment pattern
        self.javadoc_pattern = re.compile(
            r'/\*\*(.*?)\*/',
            re.DOTALL
        )
        
        # Tag-based component pattern (for mixed syntax)
        self.tag_component_pattern = re.compile(
            r'<cfcomponent\s+([^>]*)>(.*?)</cfcomponent>',
            re.DOTALL | re.IGNORECASE
        )
        
        # Tag-based function pattern (for mixed syntax)
        self.tag_function_pattern = re.compile(
            r'<cffunction\s+([^>]*)>(.*?)</cffunction>',
            re.DOTALL | re.IGNORECASE
        )
        
        # CFScript block pattern
        self.cfscript_pattern = re.compile(
            r'<cfscript>(.*?)</cfscript>',
            re.DOTALL | re.IGNORECASE
        )
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze ColdFusion file and extract structure
        
        Args:
            file_path: Path to .cfc or .cfm file
            
        Returns:
            Dictionary with analyzed structure
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        result = self.analyze_code(code)
        result['file_path'] = str(file_path)
        return result
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze ColdFusion code string
        
        Args:
            code: ColdFusion source code
            
        Returns:
            Dictionary with analyzed structure
        """
        result = {
            'language': 'coldfusion',
            'components': [],
            'errors': [],
            'warnings': []
        }
        
        if not code or not code.strip():
            return result
        
        try:
            # Check for syntax errors (basic validation)
            self._validate_syntax(code, result)
            
            # Extract CFScript components
            cfscript_components = self._extract_cfscript_components(code)
            
            # Extract tag-based components (mixed syntax)
            tag_components = self._extract_tag_components(code)
            
            # Combine both
            result['components'] = cfscript_components + tag_components
            
            # If no components found, try to extract standalone functions
            if not result['components']:
                result['components'] = [{
                    'name': 'Anonymous',
                    'functions': self._extract_cfscript_functions(code)
                }]
            
        except Exception as e:
            result['errors'].append({
                'message': str(e),
                'type': 'analysis_error'
            })
        
        return result
    
    def _validate_syntax(self, code: str, result: Dict[str, Any]):
        """Basic syntax validation"""
        # Check for common syntax errors
        
        # Check for mismatched braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            result['errors'].append({
                'message': 'Mismatched braces detected',
                'type': 'syntax_error'
            })
        
        # Check for incomplete assignments (var x = ;)
        if re.search(r'=\s*;', code):
            result['errors'].append({
                'message': 'Incomplete assignment detected',
                'type': 'syntax_error'
            })
    
    def _extract_cfscript_components(self, code: str) -> List[Dict[str, Any]]:
        """Extract CFScript component definitions"""
        components = []
        
        for match in self.component_pattern.finditer(code):
            attrs_str = match.group(1)
            body = match.group(2)
            
            # Parse component attributes
            attrs = self._parse_cfscript_attributes(attrs_str)
            
            component = {
                'displayname': attrs.get('displayname', ''),
                'hint': attrs.get('hint', ''),
                'output': self._parse_boolean(attrs.get('output', 'true')),
                'persistent': self._parse_boolean(attrs.get('persistent', 'false')),
                'properties': self._extract_cfscript_properties(body),
                'functions': self._extract_cfscript_functions(body)
            }
            
            # Clean up empty optional fields
            if not component['displayname']:
                del component['displayname']
            if not component['hint']:
                del component['hint']
            
            components.append(component)
        
        return components
    
    def _extract_tag_components(self, code: str) -> List[Dict[str, Any]]:
        """Extract tag-based component definitions (mixed syntax)"""
        components = []
        
        for match in self.tag_component_pattern.finditer(code):
            attrs_str = match.group(1)
            body = match.group(2)
            
            # Parse tag attributes
            attrs = self._parse_tag_attributes(attrs_str)
            
            component = {
                'name': attrs.get('displayname', 'Component'),
                'functions': []
            }
            
            # Extract tag-based functions FIRST (before removing cfscript blocks)
            component['functions'].extend(self._extract_tag_functions(body))
            
            # Then extract CFScript functions from <cfscript> blocks
            for cfscript_match in self.cfscript_pattern.finditer(body):
                cfscript_code = cfscript_match.group(1)
                component['functions'].extend(self._extract_cfscript_functions(cfscript_code))
            
            components.append(component)
        
        return components
    
    def _extract_cfscript_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract CFScript function definitions"""
        functions = []
        
        # Look for JavaDoc comments before functions
        doc_comments = {}
        for match in self.javadoc_pattern.finditer(code):
            doc_text = match.group(1).strip()
            # Store doc at position for later matching
            doc_comments[match.end()] = doc_text
        
        for match in self.function_pattern.finditer(code):
            access = match.group(1) or 'public'
            returntype = match.group(2) or 'any'
            name = match.group(3)
            params_str = match.group(4) or ''
            attrs_str = match.group(5) or ''
            body = match.group(6) or ''
            
            # Parse additional attributes (hint, returnformat, etc.)
            attrs = self._parse_cfscript_attributes(attrs_str)
            
            function = {
                'name': name,
                'access': access.lower() if access else 'public',
                'returntype': returntype,
                'parameters': self._parse_cfscript_parameters(params_str)
            }
            
            # Add optional attributes
            if 'hint' in attrs:
                function['hint'] = attrs['hint']
            if 'returnformat' in attrs:
                function['returnformat'] = attrs['returnformat']
            
            # Check for JavaDoc comment
            for doc_pos, doc_text in doc_comments.items():
                if doc_pos < match.start() and match.start() - doc_pos < 100:
                    function['documentation'] = doc_text
                    break
            
            # Check if this is a constructor (init function)
            if name.lower() == 'init':
                function['is_constructor'] = True
            
            # Count return points
            if body:
                return_count = len(self.return_pattern.findall(body))
                if return_count > 1:
                    function['return_points'] = return_count
                
                # Add body if it contains variable declarations
                if self.var_pattern.search(body):
                    function['body'] = body.strip()
            
            functions.append(function)
        
        return functions
    
    def _extract_tag_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract tag-based function definitions"""
        functions = []
        
        for match in self.tag_function_pattern.finditer(code):
            attrs_str = match.group(1)
            body = match.group(2) or ''
            attrs = self._parse_tag_attributes(attrs_str)
            
            function = {
                'name': attrs.get('name', 'unnamed'),
                'access': attrs.get('access', 'public'),
                'returntype': attrs.get('returntype', 'any'),
                'parameters': []  # Add empty parameters list for consistency
            }
            
            functions.append(function)
        
        return functions
    
    def _extract_cfscript_properties(self, code: str) -> List[Dict[str, Any]]:
        """Extract CFScript property definitions"""
        properties = []
        
        for match in self.property_pattern.finditer(code):
            prop_str = match.group(1)
            attrs = self._parse_cfscript_attributes(prop_str)
            
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
            
            properties.append(prop)
        
        return properties
    
    def _parse_cfscript_parameters(self, params_str: str) -> List[Dict[str, Any]]:
        """Parse CFScript function parameters"""
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
    
    def _parse_cfscript_attributes(self, attrs_str: str) -> Dict[str, str]:
        """
        Parse CFScript attribute string
        
        Example: 'displayname="Test" hint="My hint" output=false'
        """
        attrs = {}
        
        # Pattern: attr="value" or attr='value' or attr=value
        attr_pattern = re.compile(r'(\w+)\s*=\s*(?:["\']([^"\']*)["\']|(\w+))')
        
        for match in attr_pattern.finditer(attrs_str):
            key = match.group(1).lower()
            value = match.group(2) or match.group(3) or ''
            attrs[key] = value
        
        return attrs
    
    def _parse_tag_attributes(self, attrs_str: str) -> Dict[str, str]:
        """Parse tag-based attribute string"""
        attrs = {}
        
        # Pattern: attribute="value" or attribute='value'
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
