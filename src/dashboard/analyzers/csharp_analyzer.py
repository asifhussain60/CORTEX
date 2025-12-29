"""
C# Language Analyzer for dashboard data collection.
Extracts classes, methods, MVC patterns, Web API endpoints, DI patterns, Entity Framework usage, and LINQ queries.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .language_analyzer_base import LanguageAnalyzer, AnalysisResult


class CSharpAnalyzer(LanguageAnalyzer):
    """
    Analyzer for C# source files (.cs).
    
    Extracts:
    - Classes, interfaces, enums, structs
    - Methods (public, private, protected)
    - Properties and fields
    - MVC controllers and actions
    - Web API endpoints (routes, HTTP methods)
    - Dependency injection patterns
    - Entity Framework usage (DbContext, entities)
    - LINQ queries
    - Async/await patterns
    - Complexity metrics
    """
    
    SUPPORTED_EXTENSIONS = {'.cs'}
    
    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(encoding)
        
        # Regex patterns for C# constructs
        self.class_pattern = re.compile(
            r'(public|private|protected|internal)?\s*(static)?\s*(partial)?\s*class\s+(\w+)',
            re.MULTILINE
        )
        self.interface_pattern = re.compile(
            r'(public|private|protected|internal)?\s*interface\s+(\w+)',
            re.MULTILINE
        )
        self.method_pattern = re.compile(
            r'(public|private|protected|internal)?\s*(static|virtual|override|async)?\s*'
            r'(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
        self.property_pattern = re.compile(
            r'(public|private|protected|internal)?\s*(static|virtual|override)?\s*'
            r'(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*\{\s*get',
            re.MULTILINE
        )
        self.controller_pattern = re.compile(
            r'class\s+(\w+Controller)\s*:\s*(\w+)',
            re.MULTILINE
        )
        self.api_route_pattern = re.compile(
            r'\[(?:Http(?:Get|Post|Put|Delete|Patch)|Route)\s*\(?\s*"?([^"\)]*)"?\s*\)?\]',
            re.MULTILINE
        )
        self.dbcontext_pattern = re.compile(
            r'class\s+(\w+)\s*:\s*DbContext',
            re.MULTILINE
        )
        self.linq_pattern = re.compile(
            r'\.(Where|Select|OrderBy|GroupBy|Join|FirstOrDefault|SingleOrDefault|Any|All|Count)\s*\(',
            re.MULTILINE
        )
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a C# source file."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze C# source file.
        
        Args:
            file_path: Path to .cs file
            
        Returns:
            AnalysisResult with C# metrics
        """
        content = self.read_file(file_path)
        
        if not content:
            return AnalysisResult(
                file_path=str(file_path),
                language='csharp',
                classes=[],
                methods=[],
                complexity={},
                dependencies=[],
                patterns={},
                metrics={},
                errors=self.errors.copy()
            )
        
        # Extract C# constructs
        classes = self._extract_classes(content)
        interfaces = self._extract_interfaces(content)
        methods = self._extract_methods(content)
        properties = self._extract_properties(content)
        
        # Detect patterns
        mvc_patterns = self._detect_mvc_patterns(content, file_path)
        web_api_patterns = self._detect_web_api_patterns(content, file_path)
        di_patterns = self._detect_di_patterns(content)
        ef_patterns = self._detect_entity_framework(content)
        linq_usage = self._detect_linq_queries(content)
        async_patterns = self._detect_async_patterns(content)
        
        # Calculate complexity
        complexity = self._calculate_complexity(content, methods)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(content)
        
        # Combine patterns
        patterns = {
            'mvc': mvc_patterns,
            'web_api': web_api_patterns,
            'dependency_injection': di_patterns,
            'entity_framework': ef_patterns,
            'linq': linq_usage,
            'async_await': async_patterns
        }
        
        # Calculate metrics
        metrics = self._calculate_metrics(content, classes, methods, properties)
        
        return AnalysisResult(
            file_path=str(file_path),
            language='csharp',
            classes=classes + interfaces,
            methods=methods,
            complexity=complexity,
            dependencies=dependencies,
            patterns=patterns,
            metrics=metrics,
            errors=self.errors.copy()
        )
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions."""
        classes = []
        
        for match in self.class_pattern.finditer(content):
            visibility = match.group(1) or 'internal'
            is_static = match.group(2) is not None
            is_partial = match.group(3) is not None
            class_name = match.group(4)
            
            # Extract base class/interfaces
            base_classes = self._extract_base_classes(content, class_name)
            
            classes.append({
                'name': class_name,
                'type': 'class',
                'visibility': visibility,
                'is_static': is_static,
                'is_partial': is_partial,
                'base_classes': base_classes,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract interface definitions."""
        interfaces = []
        
        for match in self.interface_pattern.finditer(content):
            visibility = match.group(1) or 'internal'
            interface_name = match.group(2)
            
            interfaces.append({
                'name': interface_name,
                'type': 'interface',
                'visibility': visibility,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return interfaces
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method definitions."""
        methods = []
        
        for match in self.method_pattern.finditer(content):
            visibility = match.group(1) or 'private'
            modifiers = match.group(2) or ''
            return_type = match.group(3)
            method_name = match.group(4)
            
            # Skip property getters/setters
            if method_name in ['get', 'set']:
                continue
            
            # Extract parameters
            param_start = match.end()
            param_end = content.find(')', param_start)
            params = content[param_start:param_end] if param_end > param_start else ''
            
            methods.append({
                'name': method_name,
                'visibility': visibility,
                'modifiers': modifiers.split(),
                'return_type': return_type,
                'parameters': params.strip(),
                'is_async': 'async' in modifiers,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract property definitions."""
        properties = []
        
        for match in self.property_pattern.finditer(content):
            visibility = match.group(1) or 'private'
            modifiers = match.group(2) or ''
            prop_type = match.group(3)
            prop_name = match.group(4)
            
            properties.append({
                'name': prop_name,
                'type': prop_type,
                'visibility': visibility,
                'modifiers': modifiers.split(),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return properties
    
    def _extract_base_classes(self, content: str, class_name: str) -> List[str]:
        """Extract base class and implemented interfaces."""
        base_classes = []
        
        # Look for class definition with inheritance
        pattern = re.compile(
            rf'class\s+{class_name}\s*:\s*([^{{]+)',
            re.MULTILINE
        )
        match = pattern.search(content)
        
        if match:
            inheritance = match.group(1).strip()
            base_classes = [bc.strip() for bc in inheritance.split(',')]
        
        return base_classes
    
    def _detect_mvc_patterns(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Detect ASP.NET MVC patterns."""
        mvc_data = {
            'is_controller': False,
            'controller_name': None,
            'base_controller': None,
            'actions': []
        }
        
        # Check if this is a controller
        controller_match = self.controller_pattern.search(content)
        if controller_match:
            mvc_data['is_controller'] = True
            mvc_data['controller_name'] = controller_match.group(1)
            mvc_data['base_controller'] = controller_match.group(2)
            
            # Extract action methods (public methods in controller)
            action_pattern = re.compile(
                r'public\s+((?:async\s+)?(?:ActionResult|IActionResult|Task<[^>]+>|JsonResult|ViewResult))\s+(\w+)\s*\([^)]*\)',
                re.MULTILINE
            )
            
            for match in action_pattern.finditer(content):
                return_type = match.group(1)
                action_name = match.group(2)
                
                # Extract HTTP method attributes
                http_methods = self._extract_http_methods(content, match.start())
                
                mvc_data['actions'].append({
                    'name': action_name,
                    'return_type': return_type,
                    'http_methods': http_methods,
                    'is_async': 'async' in return_type.lower()
                })
        
        return mvc_data
    
    def _detect_web_api_patterns(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Detect Web API patterns."""
        api_data = {
            'is_api_controller': False,
            'routes': [],
            'endpoints': []
        }
        
        # Check for API controller
        if 'ApiController' in content or '[ApiController]' in content:
            api_data['is_api_controller'] = True
            
            # Extract routes
            for match in self.api_route_pattern.finditer(content):
                route = match.group(1) or ''
                api_data['routes'].append(route)
            
            # Extract API endpoints
            endpoint_pattern = re.compile(
                r'\[(Http(?:Get|Post|Put|Delete|Patch))\s*(?:\("([^"]*)"\))?\]\s*'
                r'public\s+((?:async\s+)?(?:Task<)?(?:IActionResult|ActionResult|[^>\s]+)(?:>)?)\s+(\w+)',
                re.MULTILINE
            )
            
            for match in endpoint_pattern.finditer(content):
                http_method = match.group(1)
                route = match.group(2) or ''
                return_type = match.group(3)
                method_name = match.group(4)
                
                api_data['endpoints'].append({
                    'method': http_method.replace('Http', ''),
                    'route': route,
                    'handler': method_name,
                    'return_type': return_type,
                    'is_async': 'async' in return_type.lower()
                })
        
        return api_data
    
    def _detect_di_patterns(self, content: str) -> Dict[str, Any]:
        """Detect dependency injection patterns."""
        di_data = {
            'has_constructor_injection': False,
            'injected_services': []
        }
        
        # Look for constructor with parameters
        ctor_pattern = re.compile(
            r'public\s+\w+\s*\(([^)]+)\)',
            re.MULTILINE
        )
        
        matches = list(ctor_pattern.finditer(content))
        if matches:
            for match in matches:
                params = match.group(1)
                if params.strip():
                    di_data['has_constructor_injection'] = True
                    
                    # Extract service types
                    param_list = params.split(',')
                    for param in param_list:
                        param = param.strip()
                        if param:
                            # Extract type name (before variable name)
                            parts = param.split()
                            if len(parts) >= 2:
                                service_type = parts[0]
                                # Filter out common non-service types
                                if service_type not in ['string', 'int', 'bool', 'DateTime']:
                                    di_data['injected_services'].append(service_type)
        
        return di_data
    
    def _detect_entity_framework(self, content: str) -> Dict[str, Any]:
        """Detect Entity Framework usage."""
        ef_data = {
            'has_dbcontext': False,
            'dbcontext_name': None,
            'dbsets': [],
            'has_migrations': False
        }
        
        # Check for DbContext
        dbcontext_match = self.dbcontext_pattern.search(content)
        if dbcontext_match:
            ef_data['has_dbcontext'] = True
            ef_data['dbcontext_name'] = dbcontext_match.group(1)
            
            # Extract DbSets
            dbset_pattern = re.compile(
                r'public\s+DbSet<(\w+)>\s+(\w+)',
                re.MULTILINE
            )
            
            for match in dbset_pattern.finditer(content):
                entity_type = match.group(1)
                property_name = match.group(2)
                
                ef_data['dbsets'].append({
                    'entity': entity_type,
                    'property': property_name
                })
        
        # Check for migrations
        if 'Migration' in content and 'Up(' in content and 'Down(' in content:
            ef_data['has_migrations'] = True
        
        return ef_data
    
    def _detect_linq_queries(self, content: str) -> Dict[str, Any]:
        """Detect LINQ query usage."""
        linq_data = {
            'has_linq': False,
            'query_count': 0,
            'operators': []
        }
        
        matches = list(self.linq_pattern.finditer(content))
        if matches:
            linq_data['has_linq'] = True
            linq_data['query_count'] = len(matches)
            
            # Count unique operators
            operators = {}
            for match in matches:
                operator = match.group(1)
                operators[operator] = operators.get(operator, 0) + 1
            
            linq_data['operators'] = [
                {'name': op, 'count': count}
                for op, count in operators.items()
            ]
        
        return linq_data
    
    def _detect_async_patterns(self, content: str) -> Dict[str, Any]:
        """Detect async/await patterns."""
        async_data = {
            'has_async': False,
            'async_method_count': 0,
            'await_count': 0
        }
        
        async_count = content.count('async ')
        await_count = content.count('await ')
        
        if async_count > 0:
            async_data['has_async'] = True
            async_data['async_method_count'] = async_count
            async_data['await_count'] = await_count
        
        return async_data
    
    def _extract_http_methods(self, content: str, position: int) -> List[str]:
        """Extract HTTP method attributes before a method."""
        # Look back from position for HTTP attributes
        snippet = content[max(0, position - 200):position]
        
        http_methods = []
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            if f'[Http{method}]' in snippet or f'[Http{method}(' in snippet:
                http_methods.append(method)
        
        return http_methods if http_methods else ['GET']  # Default to GET
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract using statements."""
        dependencies = []
        
        using_pattern = re.compile(r'using\s+([\w\.]+);', re.MULTILINE)
        
        for match in using_pattern.finditer(content):
            namespace = match.group(1)
            dependencies.append(namespace)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_complexity(self, content: str, methods: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate complexity metrics."""
        cyclomatic = self.calculate_cyclomatic_complexity(content, 'csharp')
        
        # Calculate average method complexity
        avg_method_complexity = 0
        if methods:
            method_complexities = []
            for method in methods:
                # Simplified: count decision points in method name vicinity
                method_name = method['name']
                method_pattern = re.compile(rf'{method_name}\s*\([^)]*\)\s*{{([^}}]*?)}}', re.DOTALL)
                match = method_pattern.search(content)
                if match:
                    method_body = match.group(1)
                    complexity = self.calculate_cyclomatic_complexity(method_body, 'csharp')
                    method_complexities.append(complexity)
            
            if method_complexities:
                avg_method_complexity = sum(method_complexities) / len(method_complexities)
        
        return {
            'cyclomatic': cyclomatic,
            'avg_method_complexity': avg_method_complexity,
            'cognitive': cyclomatic * 1.2  # Approximation
        }
    
    def _calculate_metrics(
        self,
        content: str,
        classes: List[Dict[str, Any]],
        methods: List[Dict[str, Any]],
        properties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate general metrics."""
        lines = content.split('\n')
        
        return {
            'loc': len(lines),
            'sloc': len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
            'class_count': len([c for c in classes if c['type'] == 'class']),
            'interface_count': len([c for c in classes if c['type'] == 'interface']),
            'method_count': len(methods),
            'property_count': len(properties),
            'public_method_count': len([m for m in methods if m['visibility'] == 'public']),
            'private_method_count': len([m for m in methods if m['visibility'] == 'private']),
            'async_method_count': len([m for m in methods if m.get('is_async')])
        }
