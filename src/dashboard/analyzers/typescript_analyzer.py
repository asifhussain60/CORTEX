"""
TypeScript/Angular Language Analyzer for dashboard data collection.
Extracts Angular components, services, routing, RxJS patterns, NgRx state management, and HTTP calls.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from .language_analyzer_base import LanguageAnalyzer, AnalysisResult


class TypeScriptAnalyzer(LanguageAnalyzer):
    """
    Analyzer for TypeScript source files (.ts).
    
    Extracts:
    - Classes, interfaces, types
    - Angular components (@Component decorator)
    - Angular services (@Injectable decorator)
    - Angular modules (@NgModule decorator)
    - Routes (RouterModule.forRoot/forChild)
    - RxJS observables and operators
    - NgRx store usage (actions, reducers, effects)
    - HTTP calls (HttpClient methods)
    - Dependency injection
    """
    
    SUPPORTED_EXTENSIONS = {'.ts'}
    
    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(encoding)
        
        # Regex patterns for TypeScript/Angular constructs
        self.class_pattern = re.compile(
            r'export\s+(abstract\s+)?class\s+(\w+)',
            re.MULTILINE
        )
        self.interface_pattern = re.compile(
            r'export\s+interface\s+(\w+)',
            re.MULTILINE
        )
        self.component_pattern = re.compile(
            r'@Component\s*\(\s*\{([^}]+)\}\s*\)',
            re.DOTALL
        )
        self.service_pattern = re.compile(
            r'@Injectable\s*\(\s*\{([^}]*)\}\s*\)',
            re.DOTALL
        )
        self.module_pattern = re.compile(
            r'@NgModule\s*\(\s*\{([^}]+)\}\s*\)',
            re.DOTALL
        )
        self.method_pattern = re.compile(
            r'(public|private|protected)?\s*(async\s+)?(\w+)\s*\([^)]*\)\s*:\s*([^{]+)\s*\{',
            re.MULTILINE
        )
        self.rxjs_pattern = re.compile(
            r'(Observable|Subject|BehaviorSubject|ReplaySubject)<([^>]+)>',
            re.MULTILINE
        )
        self.http_pattern = re.compile(
            r'this\.http\.(get|post|put|delete|patch)<([^>]+)>\s*\(\s*[`"\']([^`"\']+)',
            re.MULTILINE
        )
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if file is a TypeScript source file."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze TypeScript source file.
        
        Args:
            file_path: Path to .ts file
            
        Returns:
            AnalysisResult with TypeScript/Angular metrics
        """
        content = self.read_file(file_path)
        
        if not content:
            return AnalysisResult(
                file_path=str(file_path),
                language='typescript',
                classes=[],
                methods=[],
                complexity={},
                dependencies=[],
                patterns={},
                metrics={},
                errors=self.errors.copy()
            )
        
        # Extract TypeScript constructs
        classes = self._extract_classes(content)
        interfaces = self._extract_interfaces(content)
        methods = self._extract_methods(content)
        
        # Detect Angular patterns
        component_patterns = self._detect_component(content, file_path)
        service_patterns = self._detect_service(content)
        module_patterns = self._detect_module(content)
        routing_patterns = self._detect_routing(content)
        
        # Detect RxJS patterns
        rxjs_patterns = self._detect_rxjs(content)
        
        # Detect NgRx patterns
        ngrx_patterns = self._detect_ngrx(content)
        
        # Detect HTTP calls
        http_patterns = self._detect_http_calls(content)
        
        # Calculate complexity
        complexity = self._calculate_complexity(content, methods)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(content)
        
        # Combine patterns
        patterns = {
            'component': component_patterns,
            'service': service_patterns,
            'module': module_patterns,
            'routing': routing_patterns,
            'rxjs': rxjs_patterns,
            'ngrx': ngrx_patterns,
            'http': http_patterns
        }
        
        # Calculate metrics
        metrics = self._calculate_metrics(content, classes, interfaces, methods)
        
        return AnalysisResult(
            file_path=str(file_path),
            language='typescript',
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
            is_abstract = match.group(1) is not None
            class_name = match.group(2)
            
            # Extract implements/extends
            inheritance = self._extract_inheritance(content, class_name)
            
            classes.append({
                'name': class_name,
                'type': 'class',
                'is_abstract': is_abstract,
                'extends': inheritance.get('extends'),
                'implements': inheritance.get('implements', []),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract interface definitions."""
        interfaces = []
        
        for match in self.interface_pattern.finditer(content):
            interface_name = match.group(1)
            
            # Extract extends
            extends_pattern = re.compile(
                rf'interface\s+{interface_name}\s+extends\s+([^{{]+)',
                re.MULTILINE
            )
            extends_match = extends_pattern.search(content)
            extends_list = []
            if extends_match:
                extends_list = [e.strip() for e in extends_match.group(1).split(',')]
            
            interfaces.append({
                'name': interface_name,
                'type': 'interface',
                'extends': extends_list,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return interfaces
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method definitions."""
        methods = []
        
        for match in self.method_pattern.finditer(content):
            visibility = match.group(1) or 'public'
            is_async = match.group(2) is not None
            method_name = match.group(3)
            return_type = match.group(4).strip()
            
            # Skip constructor
            if method_name == 'constructor':
                continue
            
            methods.append({
                'name': method_name,
                'visibility': visibility,
                'is_async': is_async,
                'return_type': return_type,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _extract_inheritance(self, content: str, class_name: str) -> Dict[str, Any]:
        """Extract class inheritance information."""
        inheritance = {
            'extends': None,
            'implements': []
        }
        
        # Look for extends/implements
        pattern = re.compile(
            rf'class\s+{class_name}\s+(?:extends\s+(\w+)\s+)?(?:implements\s+([^{{]+))?',
            re.MULTILINE
        )
        match = pattern.search(content)
        
        if match:
            if match.group(1):
                inheritance['extends'] = match.group(1)
            if match.group(2):
                inheritance['implements'] = [i.strip() for i in match.group(2).split(',')]
        
        return inheritance
    
    def _detect_component(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Detect Angular component patterns."""
        component_data = {
            'is_component': False,
            'selector': None,
            'template_url': None,
            'style_urls': [],
            'standalone': False,
            'inputs': [],
            'outputs': []
        }
        
        match = self.component_pattern.search(content)
        if match:
            component_data['is_component'] = True
            decorator_content = match.group(1)
            
            # Extract selector
            selector_match = re.search(r"selector:\s*['\"]([^'\"]+)", decorator_content)
            if selector_match:
                component_data['selector'] = selector_match.group(1)
            
            # Extract template/templateUrl
            template_url_match = re.search(r"templateUrl:\s*['\"]([^'\"]+)", decorator_content)
            if template_url_match:
                component_data['template_url'] = template_url_match.group(1)
            
            # Extract styleUrls
            style_urls_match = re.search(r"styleUrls:\s*\[([^\]]+)\]", decorator_content)
            if style_urls_match:
                styles = style_urls_match.group(1)
                component_data['style_urls'] = [
                    s.strip().strip("'\"") for s in styles.split(',')
                ]
            
            # Check for standalone
            if 'standalone: true' in decorator_content:
                component_data['standalone'] = True
            
            # Extract @Input decorators
            input_pattern = re.compile(r'@Input\(\)\s+(\w+)', re.MULTILINE)
            component_data['inputs'] = [m.group(1) for m in input_pattern.finditer(content)]
            
            # Extract @Output decorators
            output_pattern = re.compile(r'@Output\(\)\s+(\w+)', re.MULTILINE)
            component_data['outputs'] = [m.group(1) for m in output_pattern.finditer(content)]
        
        return component_data
    
    def _detect_service(self, content: str) -> Dict[str, Any]:
        """Detect Angular service patterns."""
        service_data = {
            'is_service': False,
            'provided_in': None,
            'injected_dependencies': []
        }
        
        match = self.service_pattern.search(content)
        if match:
            service_data['is_service'] = True
            decorator_content = match.group(1)
            
            # Extract providedIn
            provided_match = re.search(r"providedIn:\s*['\"]([^'\"]+)", decorator_content)
            if provided_match:
                service_data['provided_in'] = provided_match.group(1)
            
            # Extract constructor dependencies
            ctor_pattern = re.compile(
                r'constructor\s*\(([^)]+)\)',
                re.MULTILINE
            )
            ctor_match = ctor_pattern.search(content)
            if ctor_match:
                params = ctor_match.group(1)
                # Parse parameters
                param_list = params.split(',')
                for param in param_list:
                    param = param.strip()
                    if ':' in param:
                        parts = param.split(':')
                        if len(parts) >= 2:
                            service_type = parts[1].strip()
                            service_data['injected_dependencies'].append(service_type)
        
        return service_data
    
    def _detect_module(self, content: str) -> Dict[str, Any]:
        """Detect Angular module patterns."""
        module_data = {
            'is_module': False,
            'declarations': [],
            'imports': [],
            'providers': [],
            'exports': []
        }
        
        match = self.module_pattern.search(content)
        if match:
            module_data['is_module'] = True
            decorator_content = match.group(1)
            
            # Extract declarations
            decl_match = re.search(r'declarations:\s*\[([^\]]+)\]', decorator_content, re.DOTALL)
            if decl_match:
                module_data['declarations'] = [
                    d.strip() for d in decl_match.group(1).split(',') if d.strip()
                ]
            
            # Extract imports
            imports_match = re.search(r'imports:\s*\[([^\]]+)\]', decorator_content, re.DOTALL)
            if imports_match:
                module_data['imports'] = [
                    i.strip() for i in imports_match.group(1).split(',') if i.strip()
                ]
            
            # Extract providers
            providers_match = re.search(r'providers:\s*\[([^\]]+)\]', decorator_content, re.DOTALL)
            if providers_match:
                module_data['providers'] = [
                    p.strip() for p in providers_match.group(1).split(',') if p.strip()
                ]
        
        return module_data
    
    def _detect_routing(self, content: str) -> Dict[str, Any]:
        """Detect Angular routing patterns."""
        routing_data = {
            'has_routing': False,
            'routes': []
        }
        
        # Check for RouterModule
        if 'RouterModule' in content:
            routing_data['has_routing'] = True
            
            # Extract routes array
            routes_pattern = re.compile(
                r'const\s+routes:\s*Routes\s*=\s*\[([^\]]+)\]',
                re.DOTALL
            )
            match = routes_pattern.search(content)
            if match:
                routes_content = match.group(1)
                
                # Extract individual routes
                route_pattern = re.compile(
                    r"\{\s*path:\s*['\"]([^'\"]*)['\"].*?component:\s*(\w+)",
                    re.DOTALL
                )
                for route_match in route_pattern.finditer(routes_content):
                    path = route_match.group(1)
                    component = route_match.group(2)
                    
                    routing_data['routes'].append({
                        'path': path,
                        'component': component
                    })
        
        return routing_data
    
    def _detect_rxjs(self, content: str) -> Dict[str, Any]:
        """Detect RxJS usage patterns."""
        rxjs_data = {
            'has_rxjs': False,
            'observable_count': 0,
            'subject_types': [],
            'operators': []
        }
        
        # Check for RxJS types
        matches = list(self.rxjs_pattern.finditer(content))
        if matches:
            rxjs_data['has_rxjs'] = True
            rxjs_data['observable_count'] = len(matches)
            
            # Count subject types
            subject_types = {}
            for match in matches:
                subject_type = match.group(1)
                if subject_type not in subject_types:
                    subject_types[subject_type] = 0
                subject_types[subject_type] += 1
            
            rxjs_data['subject_types'] = [
                {'type': k, 'count': v} for k, v in subject_types.items()
            ]
        
        # Detect RxJS operators
        common_operators = [
            'map', 'filter', 'tap', 'switchMap', 'mergeMap', 'concatMap',
            'catchError', 'debounceTime', 'distinctUntilChanged', 'takeUntil',
            'take', 'first', 'combineLatest', 'forkJoin', 'zip'
        ]
        
        operators_found = {}
        for operator in common_operators:
            # Look for pipe operator usage
            pattern = rf'\.pipe\([^)]*{operator}\('
            if re.search(pattern, content):
                operators_found[operator] = content.count(f'{operator}(')
        
        if operators_found:
            rxjs_data['operators'] = [
                {'name': k, 'count': v} for k, v in operators_found.items()
            ]
        
        return rxjs_data
    
    def _detect_ngrx(self, content: str) -> Dict[str, Any]:
        """Detect NgRx state management patterns."""
        ngrx_data = {
            'has_ngrx': False,
            'has_store': False,
            'has_actions': False,
            'has_effects': False,
            'has_reducers': False
        }
        
        # Check for NgRx imports
        if '@ngrx/store' in content:
            ngrx_data['has_ngrx'] = True
            ngrx_data['has_store'] = True
        
        if '@ngrx/effects' in content:
            ngrx_data['has_ngrx'] = True
            ngrx_data['has_effects'] = True
        
        # Check for action creators
        if 'createAction' in content or 'props<' in content:
            ngrx_data['has_actions'] = True
        
        # Check for reducers
        if 'createReducer' in content or 'on(' in content:
            ngrx_data['has_reducers'] = True
        
        return ngrx_data
    
    def _detect_http_calls(self, content: str) -> Dict[str, Any]:
        """Detect HTTP client usage."""
        http_data = {
            'has_http': False,
            'calls': []
        }
        
        # Check for HttpClient
        if 'HttpClient' in content:
            http_data['has_http'] = True
            
            # Extract HTTP calls
            for match in self.http_pattern.finditer(content):
                method = match.group(1).upper()
                response_type = match.group(2)
                url = match.group(3)
                
                http_data['calls'].append({
                    'method': method,
                    'url': url,
                    'response_type': response_type
                })
        
        return http_data
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract import statements."""
        dependencies = []
        
        # Extract from imports
        import_pattern = re.compile(
            r"import\s+(?:\{[^}]+\}|[\w]+)\s+from\s+['\"]([^'\"]+)",
            re.MULTILINE
        )
        
        for match in import_pattern.finditer(content):
            module = match.group(1)
            dependencies.append(module)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_complexity(self, content: str, methods: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate complexity metrics."""
        cyclomatic = self.calculate_cyclomatic_complexity(content, 'typescript')
        
        # Calculate average method complexity
        avg_method_complexity = 0
        if methods:
            # Simplified approximation
            avg_method_complexity = cyclomatic / max(len(methods), 1)
        
        return {
            'cyclomatic': cyclomatic,
            'avg_method_complexity': avg_method_complexity,
            'cognitive': cyclomatic * 1.2  # Approximation
        }
    
    def _calculate_metrics(
        self,
        content: str,
        classes: List[Dict[str, Any]],
        interfaces: List[Dict[str, Any]],
        methods: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate general metrics."""
        lines = content.split('\n')
        
        return {
            'loc': len(lines),
            'sloc': len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
            'class_count': len(classes),
            'interface_count': len(interfaces),
            'method_count': len(methods),
            'public_method_count': len([m for m in methods if m['visibility'] == 'public']),
            'private_method_count': len([m for m in methods if m['visibility'] == 'private']),
            'async_method_count': len([m for m in methods if m.get('is_async')])
        }
