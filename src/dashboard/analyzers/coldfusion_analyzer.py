"""
ColdFusion Language Analyzer for dashboard data collection.
Extracts CFM pages, CFC components, CFQuery, CFInclude, functions, and ColdFusion ORM usage.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .language_analyzer_base import LanguageAnalyzer, AnalysisResult


class ColdFusionAnalyzer(LanguageAnalyzer):
    """
    Analyzer for ColdFusion source files (.cfm, .cfc).
    
    Extracts:
    - CFM pages (presentation layer)
    - CFC components (business logic)
    - CFQuery database calls
    - CFInclude dependencies
    - CFFunction definitions
    - CFProperty (ORM entities)
    - CFScript blocks
    - Email workflows (CFMail)
    """
    
    SUPPORTED_EXTENSIONS = {'.cfm', '.cfc'}
    
    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(encoding)
        
        # Regex patterns for ColdFusion constructs
        self.component_pattern = re.compile(
            r'<cfcomponent\s+([^>]*)>',
            re.IGNORECASE | re.DOTALL
        )
        self.function_pattern = re.compile(
            r'<cffunction\s+([^>]*)>',
            re.IGNORECASE | re.DOTALL
        )
        self.query_pattern = re.compile(
            r'<cfquery\s+([^>]*)>',
            re.IGNORECASE | re.DOTALL
        )
        self.include_pattern = re.compile(
            r'<cfinclude\s+template\s*=\s*["\']([^"\']+)["\']',
            re.IGNORECASE
        )
        self.property_pattern = re.compile(
            r'<cfproperty\s+([^>]*)>',
            re.IGNORECASE | re.DOTALL
        )
        self.mail_pattern = re.compile(
            r'<cfmail\s+([^>]*)>',
            re.IGNORECASE | re.DOTALL
        )
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a ColdFusion source file."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze ColdFusion source file.
        
        Args:
            file_path: Path to .cfm or .cfc file
            
        Returns:
            AnalysisResult with ColdFusion metrics
        """
        content = self.read_file(file_path)
        
        if not content:
            return AnalysisResult(
                file_path=str(file_path),
                language='coldfusion',
                classes=[],
                methods=[],
                complexity={},
                dependencies=[],
                patterns={},
                metrics={},
                errors=self.errors.copy()
            )
        
        # Determine file type
        is_cfc = file_path.suffix.lower() == '.cfc'
        is_cfm = file_path.suffix.lower() == '.cfm'
        
        # Extract ColdFusion constructs
        components = self._extract_components(content) if is_cfc else []
        functions = self._extract_functions(content)
        properties = self._extract_properties(content) if is_cfc else []
        
        # Detect patterns
        query_patterns = self._detect_queries(content)
        include_patterns = self._detect_includes(content)
        orm_patterns = self._detect_orm(content) if is_cfc else {}
        email_patterns = self._detect_email(content)
        cfscript_patterns = self._detect_cfscript(content)
        
        # Calculate complexity
        complexity = self._calculate_complexity(content, functions)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(content)
        
        # Combine patterns
        patterns = {
            'cfquery': query_patterns,
            'cfinclude': include_patterns,
            'orm': orm_patterns,
            'cfmail': email_patterns,
            'cfscript': cfscript_patterns,
            'file_type': 'cfc' if is_cfc else 'cfm'
        }
        
        # Calculate metrics
        metrics = self._calculate_metrics(content, components, functions, properties)
        
        return AnalysisResult(
            file_path=str(file_path),
            language='coldfusion',
            classes=components,
            methods=functions,
            complexity=complexity,
            dependencies=dependencies,
            patterns=patterns,
            metrics=metrics,
            errors=self.errors.copy()
        )
    
    def _extract_components(self, content: str) -> List[Dict[str, Any]]:
        """Extract CFC component definitions."""
        components = []
        
        for match in self.component_pattern.finditer(content):
            attrs = self._parse_attributes(match.group(1))
            
            components.append({
                'name': attrs.get('name', 'Unknown'),
                'type': 'component',
                'extends': attrs.get('extends'),
                'implements': attrs.get('implements', '').split(',') if attrs.get('implements') else [],
                'persistent': attrs.get('persistent') == 'true',
                'accessors': attrs.get('accessors') == 'true',
                'line': content[:match.start()].count('\n') + 1
            })
        
        return components
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract CFFunction definitions."""
        functions = []
        
        for match in self.function_pattern.finditer(content):
            attrs = self._parse_attributes(match.group(1))
            
            functions.append({
                'name': attrs.get('name', 'Unknown'),
                'access': attrs.get('access', 'public'),
                'return_type': attrs.get('returntype', 'any'),
                'output': attrs.get('output') == 'true',
                'line': content[:match.start()].count('\n') + 1
            })
        
        return functions
    
    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract CFProperty definitions (ORM entities)."""
        properties = []
        
        for match in self.property_pattern.finditer(content):
            attrs = self._parse_attributes(match.group(1))
            
            properties.append({
                'name': attrs.get('name', 'Unknown'),
                'type': attrs.get('type', 'any'),
                'required': attrs.get('required') == 'true',
                'default': attrs.get('default'),
                'field_type': attrs.get('fieldtype'),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return properties
    
    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """Parse ColdFusion tag attributes."""
        attrs = {}
        
        # Pattern to match name="value" or name='value'
        pattern = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
        
        for match in pattern.finditer(attr_string):
            name = match.group(1).lower()
            value = match.group(2)
            attrs[name] = value
        
        return attrs
    
    def _detect_queries(self, content: str) -> Dict[str, Any]:
        """Detect CFQuery database calls."""
        query_data = {
            'has_queries': False,
            'query_count': 0,
            'queries': []
        }
        
        matches = list(self.query_pattern.finditer(content))
        if matches:
            query_data['has_queries'] = True
            query_data['query_count'] = len(matches)
            
            for match in matches:
                attrs = self._parse_attributes(match.group(1))
                
                # Extract SQL statement
                end_pos = content.find('</cfquery>', match.end())
                sql = ''
                if end_pos > match.end():
                    sql = content[match.end():end_pos].strip()
                
                query_data['queries'].append({
                    'name': attrs.get('name', 'unnamed'),
                    'datasource': attrs.get('datasource'),
                    'sql_preview': sql[:100] if sql else '',
                    'has_params': '<cfqueryparam' in sql
                })
        
        return query_data
    
    def _detect_includes(self, content: str) -> Dict[str, Any]:
        """Detect CFInclude dependencies."""
        include_data = {
            'has_includes': False,
            'include_count': 0,
            'templates': []
        }
        
        matches = list(self.include_pattern.finditer(content))
        if matches:
            include_data['has_includes'] = True
            include_data['include_count'] = len(matches)
            include_data['templates'] = [m.group(1) for m in matches]
        
        return include_data
    
    def _detect_orm(self, content: str) -> Dict[str, Any]:
        """Detect ColdFusion ORM usage."""
        orm_data = {
            'has_orm': False,
            'is_entity': False,
            'table_name': None,
            'properties': []
        }
        
        # Check for persistent component
        if 'persistent="true"' in content.lower() or 'persistent=true' in content.lower():
            orm_data['has_orm'] = True
            orm_data['is_entity'] = True
            
            # Extract table name
            table_pattern = re.compile(r'table\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
            match = table_pattern.search(content)
            if match:
                orm_data['table_name'] = match.group(1)
            
            # Count ORM properties
            orm_data['properties'] = len(self.property_pattern.findall(content))
        
        return orm_data
    
    def _detect_email(self, content: str) -> Dict[str, Any]:
        """Detect CFMail email workflows."""
        email_data = {
            'has_email': False,
            'email_count': 0,
            'emails': []
        }
        
        matches = list(self.mail_pattern.finditer(content))
        if matches:
            email_data['has_email'] = True
            email_data['email_count'] = len(matches)
            
            for match in matches:
                attrs = self._parse_attributes(match.group(1))
                
                email_data['emails'].append({
                    'to': attrs.get('to'),
                    'from': attrs.get('from'),
                    'subject': attrs.get('subject'),
                    'type': attrs.get('type', 'text')
                })
        
        return email_data
    
    def _detect_cfscript(self, content: str) -> Dict[str, Any]:
        """Detect CFScript blocks."""
        cfscript_data = {
            'has_cfscript': False,
            'cfscript_count': 0
        }
        
        # Check for cfscript tags or .cfc files (which are mostly script)
        cfscript_pattern = re.compile(r'<cfscript>', re.IGNORECASE)
        matches = list(cfscript_pattern.finditer(content))
        
        if matches:
            cfscript_data['has_cfscript'] = True
            cfscript_data['cfscript_count'] = len(matches)
        
        return cfscript_data
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies (includes and component invocations)."""
        dependencies = []
        
        # Extract includes
        for match in self.include_pattern.finditer(content):
            dependencies.append(match.group(1))
        
        # Extract createObject calls
        create_pattern = re.compile(
            r'createObject\s*\(\s*["\']component["\'],\s*["\']([^"\']+)["\']',
            re.IGNORECASE
        )
        for match in create_pattern.finditer(content):
            dependencies.append(match.group(1))
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_complexity(self, content: str, functions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate complexity metrics."""
        cyclomatic = self.calculate_cyclomatic_complexity(content, 'coldfusion')
        
        # Calculate average function complexity
        avg_function_complexity = 0
        if functions:
            avg_function_complexity = cyclomatic / max(len(functions), 1)
        
        return {
            'cyclomatic': cyclomatic,
            'avg_function_complexity': avg_function_complexity,
            'cognitive': cyclomatic * 1.1  # Approximation
        }
    
    def _calculate_metrics(
        self,
        content: str,
        components: List[Dict[str, Any]],
        functions: List[Dict[str, Any]],
        properties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate general metrics."""
        lines = content.split('\n')
        
        # Count different tag types
        cf_tags = len(re.findall(r'<cf\w+', content, re.IGNORECASE))
        html_tags = len(re.findall(r'<(?!cf)\w+', content, re.IGNORECASE))
        
        return {
            'loc': len(lines),
            'sloc': len([l for l in lines if l.strip() and not l.strip().startswith('<!---')]),
            'component_count': len(components),
            'function_count': len(functions),
            'property_count': len(properties),
            'cf_tag_count': cf_tags,
            'html_tag_count': html_tags,
            'public_function_count': len([f for f in functions if f['access'] == 'public']),
            'private_function_count': len([f for f in functions if f['access'] == 'private'])
        }
