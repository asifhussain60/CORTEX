"""
Python Language Analyzer - Extract architecture from Python source files.

Detects:
- Classes and methods
- Functions and decorators
- Import dependencies
- Complexity metrics
- Flask/Django/FastAPI patterns

Author: Asif Hussain
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Any, Set
import re

from src.dashboard.analyzers.language_analyzer_base import LanguageAnalyzer, AnalysisResult


class PythonAnalyzer(LanguageAnalyzer):
    """
    Python source code analyzer.
    
    Capabilities:
    - Class and method extraction
    - Function detection with decorators
    - Import analysis
    - Flask/Django/FastAPI framework detection
    - Complexity calculation
    - Type hint parsing
    """
    
    def __init__(self):
        super().__init__()
        
        # Regex patterns
        self.class_pattern = re.compile(
            r'class\s+(\w+)(?:\(([^)]*)\))?:',
            re.MULTILINE
        )
        
        self.method_pattern = re.compile(
            r'^\s+def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?:',
            re.MULTILINE
        )
        
        self.function_pattern = re.compile(
            r'^def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?:',
            re.MULTILINE
        )
        
        self.decorator_pattern = re.compile(
            r'^\s*@(\w+(?:\.\w+)*)',
            re.MULTILINE
        )
        
        self.import_pattern = re.compile(
            r'^(?:from\s+([\w.]+)\s+)?import\s+(.+?)(?:\s+as\s+\w+)?$',
            re.MULTILINE
        )
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if file is Python."""
        return file_path.suffix.lower() == '.py'
    
    def analyze(self, file_path: Path) -> AnalysisResult:
        """
        Analyze Python source file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            AnalysisResult with Python-specific data
        """
        result = AnalysisResult(
            file_path=str(file_path),
            language='python',
            classes=[],
            methods=[],
            complexity={},
            dependencies=[],
            patterns={},
            metrics={},
            errors=[]
        )
        
        try:
            content = self.read_file(file_path)
            
            if not content:
                return result
            
            # Extract components
            result.classes = self._extract_classes(content)
            result.methods = self._extract_methods(content)
            result.dependencies = self._extract_imports(content)
            
            # Detect patterns
            result.patterns = self._detect_patterns(content, result)
            
            # Calculate metrics
            result.metrics = self._calculate_metrics(content, result)
            
            # Calculate complexity
            result.complexity = self._calculate_complexity(content, result)
            
        except Exception as e:
            result.errors.append(f"Analysis error: {str(e)}")
        
        return result
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions."""
        classes = []
        
        for match in self.class_pattern.finditer(content):
            class_name = match.group(1)
            base_classes_str = match.group(2) or ""
            
            # Parse base classes
            base_classes = []
            if base_classes_str:
                base_classes = [b.strip() for b in base_classes_str.split(',')]
            
            # Find decorators before class
            decorators = self._find_decorators_before(content, match.start())
            
            classes.append({
                'name': class_name,
                'type': 'class',
                'base_classes': base_classes,
                'decorators': decorators,
                'line': content[:match.start()].count('\n') + 1
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract all functions and methods."""
        methods = []
        
        # Module-level functions
        for match in self.function_pattern.finditer(content):
            func_name = match.group(1)
            params = match.group(2)
            return_type = match.group(3)
            
            # Skip if inside class (indented)
            line_start = content.rfind('\n', 0, match.start()) + 1
            indent = match.start() - line_start
            if indent > 0:
                continue
            
            decorators = self._find_decorators_before(content, match.start())
            
            methods.append({
                'name': func_name,
                'type': 'function',
                'parameters': self._parse_parameters(params),
                'return_type': return_type.strip() if return_type else None,
                'decorators': decorators,
                'is_async': 'async def' in content[max(0, match.start()-10):match.start()],
                'line': content[:match.start()].count('\n') + 1
            })
        
        # Class methods
        for match in self.method_pattern.finditer(content):
            method_name = match.group(1)
            params = match.group(2)
            return_type = match.group(3)
            
            decorators = self._find_decorators_before(content, match.start())
            
            # Determine method type
            method_type = 'method'
            if '@staticmethod' in decorators:
                method_type = 'staticmethod'
            elif '@classmethod' in decorators:
                method_type = 'classmethod'
            elif '@property' in decorators:
                method_type = 'property'
            
            methods.append({
                'name': method_name,
                'type': method_type,
                'parameters': self._parse_parameters(params),
                'return_type': return_type.strip() if return_type else None,
                'decorators': decorators,
                'is_async': 'async def' in content[max(0, match.start()-10):match.start()],
                'line': content[:match.start()].count('\n') + 1
            })
        
        return methods
    
    def _find_decorators_before(self, content: str, position: int) -> List[str]:
        """Find decorators before a class/function."""
        decorators = []
        
        # Look backwards for decorators
        lines_before = content[:position].split('\n')
        
        for line in reversed(lines_before[-10:]):  # Check last 10 lines
            stripped = line.strip()
            if stripped.startswith('@'):
                decorator = stripped[1:]  # Remove @
                decorators.insert(0, decorator)
            elif stripped and not stripped.startswith('#'):
                break
        
        return decorators
    
    def _parse_parameters(self, params_str: str) -> List[Dict[str, Any]]:
        """Parse function parameters."""
        if not params_str.strip():
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if not param:
                continue
            
            # Parse name, type hint, default
            param_info = {'name': param}
            
            if ':' in param:
                name, type_hint = param.split(':', 1)
                param_info['name'] = name.strip()
                
                if '=' in type_hint:
                    type_part, default = type_hint.split('=', 1)
                    param_info['type'] = type_part.strip()
                    param_info['default'] = default.strip()
                else:
                    param_info['type'] = type_hint.strip()
            elif '=' in param:
                name, default = param.split('=', 1)
                param_info['name'] = name.strip()
                param_info['default'] = default.strip()
            
            params.append(param_info)
        
        return params
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports: Set[str] = set()
        
        for match in self.import_pattern.finditer(content):
            from_module = match.group(1)
            import_items = match.group(2)
            
            if from_module:
                imports.add(from_module)
            
            # Parse imported items
            for item in import_items.split(','):
                item = item.strip()
                if item and not item.startswith('('):
                    # Get module name (before any 'as')
                    module = item.split()[0]
                    imports.add(module)
        
        return sorted(list(imports))
    
    def _detect_patterns(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Detect framework and design patterns."""
        patterns = {
            'flask': self._detect_flask(content, result),
            'django': self._detect_django(content, result),
            'fastapi': self._detect_fastapi(content, result),
            'dataclass': self._detect_dataclass(result),
            'async_patterns': self._detect_async(result)
        }
        
        return patterns
    
    def _detect_flask(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Detect Flask framework usage."""
        flask_data = {
            'is_flask': False,
            'routes': [],
            'blueprints': []
        }
        
        # Check for Flask imports
        if not any('flask' in imp.lower() for imp in result.dependencies):
            return flask_data
        
        flask_data['is_flask'] = True
        
        # Find routes
        route_pattern = re.compile(r"@(?:app|bp|blueprint)\.route\(['\"]([^'\"]+)['\"]")
        for match in route_pattern.finditer(content):
            flask_data['routes'].append(match.group(1))
        
        # Find blueprints
        if 'Blueprint' in content:
            flask_data['blueprints'].append('Blueprint detected')
        
        return flask_data
    
    def _detect_django(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Detect Django framework usage."""
        django_data = {
            'is_django': False,
            'models': [],
            'views': []
        }
        
        # Check for Django imports
        if not any('django' in imp.lower() for imp in result.dependencies):
            return django_data
        
        django_data['is_django'] = True
        
        # Find models
        for cls in result.classes:
            if any('Model' in base for base in cls.get('base_classes', [])):
                django_data['models'].append(cls['name'])
        
        # Find views
        for cls in result.classes:
            if any('View' in base for base in cls.get('base_classes', [])):
                django_data['views'].append(cls['name'])
        
        return django_data
    
    def _detect_fastapi(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Detect FastAPI framework usage."""
        fastapi_data = {
            'is_fastapi': False,
            'endpoints': []
        }
        
        # Check for FastAPI imports
        if not any('fastapi' in imp.lower() for imp in result.dependencies):
            return fastapi_data
        
        fastapi_data['is_fastapi'] = True
        
        # Find endpoints
        for method in result.methods:
            decorators = method.get('decorators', [])
            for dec in decorators:
                if any(http in dec.lower() for http in ['get', 'post', 'put', 'delete', 'patch']):
                    fastapi_data['endpoints'].append({
                        'name': method['name'],
                        'decorator': dec
                    })
        
        return fastapi_data
    
    def _detect_dataclass(self, result: AnalysisResult) -> Dict[str, Any]:
        """Detect dataclass usage."""
        dataclass_info = {
            'has_dataclass': False,
            'count': 0
        }
        
        for cls in result.classes:
            if 'dataclass' in cls.get('decorators', []):
                dataclass_info['has_dataclass'] = True
                dataclass_info['count'] += 1
        
        return dataclass_info
    
    def _detect_async(self, result: AnalysisResult) -> Dict[str, Any]:
        """Detect async/await patterns."""
        async_info = {
            'has_async': False,
            'async_function_count': 0
        }
        
        for method in result.methods:
            if method.get('is_async'):
                async_info['has_async'] = True
                async_info['async_function_count'] += 1
        
        return async_info
    
    def _calculate_metrics(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Calculate Python-specific metrics."""
        lines = content.split('\n')
        
        return {
            'loc': len(lines),
            'sloc': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'class_count': len(result.classes),
            'function_count': len([m for m in result.methods if m['type'] == 'function']),
            'method_count': len([m for m in result.methods if m['type'] in ['method', 'staticmethod', 'classmethod']]),
            'import_count': len(result.dependencies),
            'decorator_count': sum(len(m.get('decorators', [])) for m in result.methods)
        }
    
    def _calculate_complexity(self, content: str, result: AnalysisResult) -> Dict[str, Any]:
        """Calculate complexity metrics."""
        # Simple cyclomatic complexity
        complexity_keywords = ['if', 'elif', 'for', 'while', 'and', 'or', 'except']
        
        total_complexity = 1  # Base complexity
        for keyword in complexity_keywords:
            # Count keyword occurrences
            pattern = rf'\b{keyword}\b'
            total_complexity += len(re.findall(pattern, content))
        
        function_count = len(result.methods)
        avg_complexity = total_complexity / function_count if function_count > 0 else 0
        
        return {
            'cyclomatic': total_complexity,
            'average': round(avg_complexity, 2),
            'functions_analyzed': function_count
        }
