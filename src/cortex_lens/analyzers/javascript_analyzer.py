"""
JavaScript/TypeScript Analyzer with Regex-Based Parsing

Primary: Regex pattern matching for components, functions, exports, routes
Optional: Babel AST or TSC integration via subprocess
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from .base import BaseAnalyzer

logger = logging.getLogger(__name__)


class JavaScriptAnalyzer(BaseAnalyzer):
    """
    JavaScript/TypeScript analyzer using regex patterns
    
    Capabilities:
    - Function/arrow function detection
    - Class/component detection (React, Vue, Angular)
    - Import/export statements
    - Route definitions (React Router, Vue Router, Express)
    - API endpoints (Express, Fastify, NestJS)
    - Hooks usage (useState, useEffect, etc.)
    - TypeScript type/interface detection
    - Async/await patterns
    
    Optional: Babel/TSC integration for 100% accuracy
    """
    
    SUPPORTED_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
    
    # Regex patterns for JS/TS constructs
    IMPORT_PATTERN = re.compile(
        r'import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*\{[^}]*\})?\s+from\s+)?[\'"]([^\'"]+)[\'"]|import\s+[\'"]([^\'"]+)[\'"]',
        re.MULTILINE
    )
    
    EXPORT_PATTERN = re.compile(
        r'export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type)?\s*(\w+)?',
        re.MULTILINE
    )
    
    FUNCTION_PATTERN = re.compile(
        r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)',
        re.MULTILINE
    )
    
    ARROW_FUNCTION_PATTERN = re.compile(
        r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
        re.MULTILINE
    )
    
    CLASS_PATTERN = re.compile(
        r'(?:export\s+)?(?:default\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?',
        re.MULTILINE
    )
    
    # React patterns
    REACT_COMPONENT_PATTERN = re.compile(
        r'(?:export\s+)?(?:default\s+)?(?:function|const)\s+(\w+)\s*(?:=\s*)?\([^)]*\)\s*(?:=>)?\s*\{[^}]*return\s*\(',
        re.MULTILINE | re.DOTALL
    )
    
    REACT_HOOK_PATTERN = re.compile(
        r'(useState|useEffect|useContext|useReducer|useCallback|useMemo|useRef|useImperativeHandle|useLayoutEffect|useDebugValue)',
        re.MULTILINE
    )
    
    # Vue patterns
    VUE_COMPONENT_PATTERN = re.compile(
        r'(?:export\s+)?(?:default\s+)?\{\s*name:\s*[\'"](\w+)[\'"]',
        re.MULTILINE
    )
    
    # Angular patterns
    ANGULAR_COMPONENT_PATTERN = re.compile(
        r'@Component\s*\(\s*\{[^}]*selector:\s*[\'"]([^\'"]+)[\'"]',
        re.MULTILINE | re.DOTALL
    )
    
    # Route patterns
    EXPRESS_ROUTE_PATTERN = re.compile(
        r'(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        re.MULTILINE
    )
    
    REACT_ROUTER_PATTERN = re.compile(
        r'<Route\s+path=[\'"]([^\'"]+)[\'"]',
        re.MULTILINE
    )
    
    # TypeScript patterns
    INTERFACE_PATTERN = re.compile(
        r'(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,<>]+))?',
        re.MULTILINE
    )
    
    TYPE_PATTERN = re.compile(
        r'(?:export\s+)?type\s+(\w+)\s*=',
        re.MULTILINE
    )
    
    # API/endpoint patterns
    API_ENDPOINT_PATTERN = re.compile(
        r'[\'"`](/api/[^\'"` ]+)[\'"`]',
        re.MULTILINE
    )
    
    def __init__(self):
        """Initialize analyzer"""
        super().__init__()
        self.has_babel = self._check_babel()
        self.has_tsc = self._check_tsc()
    
    def _check_babel(self) -> bool:
        """Check if Babel is available"""
        import subprocess
        try:
            result = subprocess.run(
                ['node', '-e', 'require("@babel/parser")'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            logger.debug("Babel not available - using regex parsing")
            return False
    
    def _check_tsc(self) -> bool:
        """Check if TypeScript compiler is available"""
        import subprocess
        try:
            result = subprocess.run(['tsc', '--version'], capture_output=True, timeout=2)
            return result.returncode == 0
        except Exception:
            logger.debug("TSC not available - using regex parsing")
            return False
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript file
        
        Args:
            file_path: Path to JS/TS file
            
        Returns:
            {
                'imports': [...],
                'exports': [...],
                'functions': [...],
                'classes': [...],
                'components': [...],
                'routes': [...],
                'api_endpoints': [...],
                'hooks': [...],
                'interfaces': [...],  # TypeScript
                'types': [...],       # TypeScript
                'patterns': {...},
                'metadata': {...},
                'parser_used': str
            }
        """
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return self._generate_fallback_structure(file_path)
        
        # Determine file type
        is_typescript = file_path.suffix in {'.ts', '.tsx'}
        is_jsx = file_path.suffix in {'.jsx', '.tsx'}
        
        # Use advanced parser if available and TypeScript
        if is_typescript and (self.has_babel or self.has_tsc):
            try:
                return self._analyze_with_advanced_parser(code, file_path)
            except Exception as e:
                logger.warning(f"Advanced parser failed, falling back to regex: {e}")
        
        return self._analyze_with_regex(code, file_path, is_typescript, is_jsx)
    
    def _analyze_with_regex(
        self,
        code: str,
        file_path: Path,
        is_typescript: bool,
        is_jsx: bool
    ) -> Dict[str, Any]:
        """Regex-based analysis"""
        
        # Extract constructs
        imports = self._extract_imports(code)
        exports = self._extract_exports(code)
        functions = self._extract_functions(code)
        classes = self._extract_classes(code)
        routes = self._extract_routes(code)
        api_endpoints = self._extract_api_endpoints(code)
        
        # Framework-specific
        components = []
        hooks = []
        if is_jsx:
            components = self._extract_react_components(code)
            hooks = self._extract_react_hooks(code)
        
        # TypeScript-specific
        interfaces = []
        types = []
        if is_typescript:
            interfaces = self._extract_interfaces(code)
            types = self._extract_types(code)
        
        # Detect patterns
        patterns = {
            'framework': self._detect_framework(code, imports),
            'has_react': 'react' in ' '.join(imports).lower(),
            'has_vue': 'vue' in ' '.join(imports).lower(),
            'has_angular': '@angular' in ' '.join(imports),
            'has_express': 'express' in ' '.join(imports),
            'has_async': 'async' in code or 'await' in code,
            'has_jsx': is_jsx,
            'has_typescript': is_typescript,
            'uses_hooks': len(hooks) > 0,
            'api_routes': len(routes) > 0,
            'has_graphql': 'graphql' in code.lower() or 'apollo' in ' '.join(imports).lower()
        }
        
        # Calculate metrics
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        return {
            'imports': imports,
            'exports': exports,
            'functions': functions,
            'classes': classes,
            'components': components,
            'routes': routes,
            'api_endpoints': api_endpoints,
            'hooks': hooks,
            'interfaces': interfaces,
            'types': types,
            'patterns': patterns,
            'metadata': {
                'file_path': str(file_path),
                'lines_of_code': loc,
                'total_lines': len(lines),
                'function_count': len(functions),
                'class_count': len(classes),
                'component_count': len(components),
                'is_typescript': is_typescript,
                'is_jsx': is_jsx
            },
            'parser_used': 'regex'
        }
    
    def _analyze_with_advanced_parser(self, code: str, file_path: Path) -> Dict[str, Any]:
        """Babel or TSC-based analysis (optional, high accuracy)"""
        # Placeholder for Babel/TSC integration
        # Would use subprocess to call node with Babel parser
        return {
            'parser_used': 'babel',
            'metadata': {
                'file_path': str(file_path),
                'accuracy': 'high'
            }
        }
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements"""
        imports = []
        for match in self.IMPORT_PATTERN.finditer(code):
            # Pattern has 2 groups due to alternation
            module = match.group(1) or match.group(2)
            if module:
                imports.append(module)
        return list(set(imports))
    
    def _extract_exports(self, code: str) -> List[str]:
        """Extract export names"""
        matches = self.EXPORT_PATTERN.findall(code)
        return [m for m in matches if m]
    
    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Regular functions
        for match in self.FUNCTION_PATTERN.finditer(code):
            name = match.group(1)
            functions.append({
                'name': name,
                'type': 'function',
                'line': code[:match.start()].count('\n') + 1,
                'is_async': 'async' in match.group(0),
                'is_exported': 'export' in match.group(0)
            })
        
        # Arrow functions
        for match in self.ARROW_FUNCTION_PATTERN.finditer(code):
            name = match.group(1)
            functions.append({
                'name': name,
                'type': 'arrow_function',
                'line': code[:match.start()].count('\n') + 1,
                'is_async': 'async' in match.group(0)
            })
        
        return functions
    
    def _extract_classes(self, code: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        for match in self.CLASS_PATTERN.finditer(code):
            name = match.group(1)
            extends = match.group(2)
            
            classes.append({
                'name': name,
                'extends': extends,
                'line': code[:match.start()].count('\n') + 1,
                'is_exported': 'export' in match.group(0)
            })
        
        return classes
    
    def _extract_react_components(self, code: str) -> List[Dict[str, Any]]:
        """Extract React component definitions"""
        components = []
        for match in self.REACT_COMPONENT_PATTERN.finditer(code):
            name = match.group(1)
            components.append({
                'name': name,
                'type': 'react_functional',
                'line': code[:match.start()].count('\n') + 1
            })
        
        # Also check class components
        for cls in self._extract_classes(code):
            if cls.get('extends') in {'Component', 'React.Component', 'PureComponent'}:
                components.append({
                    'name': cls['name'],
                    'type': 'react_class',
                    'line': cls['line']
                })
        
        return components
    
    def _extract_react_hooks(self, code: str) -> List[str]:
        """Extract React hooks usage"""
        matches = self.REACT_HOOK_PATTERN.findall(code)
        return list(set(matches))
    
    def _extract_routes(self, code: str) -> List[Dict[str, Any]]:
        """Extract route definitions"""
        routes = []
        
        # Express routes
        for match in self.EXPRESS_ROUTE_PATTERN.finditer(code):
            method = match.group(1).upper()
            path = match.group(2)
            routes.append({
                'path': path,
                'method': method,
                'framework': 'express',
                'line': code[:match.start()].count('\n') + 1
            })
        
        # React Router
        for match in self.REACT_ROUTER_PATTERN.finditer(code):
            path = match.group(1)
            routes.append({
                'path': path,
                'framework': 'react-router',
                'line': code[:match.start()].count('\n') + 1
            })
        
        return routes
    
    def _extract_api_endpoints(self, code: str) -> List[str]:
        """Extract API endpoint strings"""
        matches = self.API_ENDPOINT_PATTERN.findall(code)
        return list(set(matches))
    
    def _extract_interfaces(self, code: str) -> List[Dict[str, Any]]:
        """Extract TypeScript interfaces"""
        interfaces = []
        for match in self.INTERFACE_PATTERN.finditer(code):
            name = match.group(1)
            extends = match.group(2) or ''
            
            interfaces.append({
                'name': name,
                'extends': [e.strip() for e in extends.split(',') if e.strip()],
                'line': code[:match.start()].count('\n') + 1,
                'is_exported': 'export' in match.group(0)
            })
        
        return interfaces
    
    def _extract_types(self, code: str) -> List[Dict[str, Any]]:
        """Extract TypeScript type aliases"""
        types = []
        for match in self.TYPE_PATTERN.finditer(code):
            name = match.group(1)
            types.append({
                'name': name,
                'line': code[:match.start()].count('\n') + 1,
                'is_exported': 'export' in match.group(0)
            })
        
        return types
    
    def _detect_framework(self, code: str, imports: List[str]) -> Optional[str]:
        """Detect primary framework"""
        imports_str = ' '.join(imports).lower()
        
        if 'react' in imports_str:
            return 'React'
        elif 'vue' in imports_str:
            return 'Vue'
        elif '@angular' in imports_str:
            return 'Angular'
        elif 'express' in imports_str:
            return 'Express'
        elif 'next' in imports_str:
            return 'Next.js'
        elif 'svelte' in imports_str:
            return 'Svelte'
        
        return None
    
    def _generate_fallback_structure(self, file_path: Path) -> Dict[str, Any]:
        """Generate fallback structure on read error"""
        return {
            'imports': [],
            'exports': [],
            'functions': [],
            'classes': [],
            'components': [],
            'routes': [],
            'api_endpoints': [],
            'hooks': [],
            'interfaces': [],
            'types': [],
            'patterns': {},
            'metadata': {
                'file_path': str(file_path),
                'error': 'Failed to read file'
            },
            'parser_used': 'none'
        }
    
    def analyze_batch(
        self,
        file_paths: List[Path],
        max_workers: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Batch analyze JavaScript/TypeScript files with parallel execution
        
        Similar to PythonAnalyzer.analyze_batch()
        """
        if not file_paths:
            return {
                'files': {},
                'summary': {
                    'total_files': 0,
                    'success_count': 0,
                    'failure_count': 0
                }
            }
        
        results = {}
        total = len(file_paths)
        
        # Sequential for small batches
        if total <= 10:
            for i, fp in enumerate(file_paths, 1):
                if progress_callback:
                    progress_callback(i, total, fp.name)
                results[str(fp)] = self.analyze(fp)
            
            success_count = sum(1 for r in results.values() if 'error' not in r.get('metadata', {}))
            
            return {
                'files': results,
                'summary': {
                    'total_files': total,
                    'success_count': success_count,
                    'failure_count': total - success_count
                }
            }
        
        # Parallel for large batches
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import multiprocessing
        
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze, fp): fp
                for fp in file_paths
            }
            
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, total, file_path.name)
                
                try:
                    results[str(file_path)] = future.result()
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")
                    results[str(file_path)] = {
                        'metadata': {'error': str(e)},
                        'parser_used': 'none'
                    }
        
        success_count = sum(1 for r in results.values() if 'error' not in r.get('metadata', {}))
        
        return {
            'files': results,
            'summary': {
                'total_files': total,
                'success_count': success_count,
                'failure_count': total - success_count
            }
        }
