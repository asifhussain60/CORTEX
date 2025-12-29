"""
API Endpoint Collector

Discovers and catalogs REST API endpoints from various frameworks.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from .base import BaseCollector

logger = logging.getLogger(__name__)


class APIEndpointCollector(BaseCollector):
    """
    Collect API endpoint information
    
    Detects:
    - REST API endpoints (GET, POST, PUT, DELETE, PATCH)
    - Route patterns and parameters
    - Controller/handler mappings
    - Authentication decorators
    - Response types
    
    Supported Frameworks:
    - Python: Flask, FastAPI, Django REST
    - C#: ASP.NET Core, Web API
    - JavaScript/TypeScript: Express, NestJS, Koa
    """
    
    # HTTP methods
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    
    # Framework-specific patterns
    FRAMEWORK_PATTERNS = {
        # Flask patterns
        'flask': {
            'route': r'@(?:app|blueprint|bp)\.route\s*\(\s*[\'"]([^\'"]+)[\'"](?:.*?methods\s*=\s*\[([^\]]+)\])?',
            'method': r'@(?:app|blueprint|bp)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        },
        # FastAPI patterns
        'fastapi': {
            'route': r'@(?:app|router)\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            'router': r'APIRouter\s*\(',
        },
        # Django REST patterns
        'django': {
            'path': r'path\s*\(\s*[\'"]([^\'"]+)[\'"]',
            'route': r're_path\s*\(\s*r?[\'"]([^\'"]+)[\'"]',
            'viewset': r'class\s+(\w+ViewSet|ViewSet)',
        },
        # ASP.NET Core patterns
        'aspnet': {
            'route': r'\[(?:Http(?:Get|Post|Put|Delete|Patch)|Route)\s*\(\s*[\'"]?([^\'")\]]+)?[\'"]?\s*\)\]',
            'controller': r'\[ApiController\]',
            'action': r'\[Http(Get|Post|Put|Delete|Patch)(?:\s*\(\s*[\'"]?([^\'")\]]+)?[\'"]?\s*\)?\]',
        },
        # Express patterns
        'express': {
            'route': r'(?:app|router)\.(get|post|put|delete|patch|all)\s*\(\s*[\'"`]([^\'"]+)[\'"`]',
            'use': r'(?:app|router)\.use\s*\(\s*[\'"`]([^\'"]+)[\'"`]',
        },
        # NestJS patterns
        'nestjs': {
            'controller': r'@Controller\s*\(\s*[\'"]?([^\'")\]]*)?[\'"]?\s*\)',
            'method': r'@(Get|Post|Put|Delete|Patch)\s*\(\s*[\'"]?([^\'")\]]*)?[\'"]?\s*\)',
        },
    }
    
    # Auth decorator patterns
    AUTH_PATTERNS = [
        r'@(?:login_required|auth_required|authenticated|jwt_required)',
        r'@(?:Authorize|AllowAnonymous)',
        r'\[Authorize(?:\([^\)]*\))?\]',
        r'@UseGuards\s*\(',
        r'@RequireAuth',
    ]
    
    @property
    def name(self) -> str:
        return 'api_endpoint'
    
    @property
    def description(self) -> str:
        return 'Discovers and catalogs REST API endpoints'
    
    @property
    def required_for(self) -> list:
        return ['fullstack_web', 'api_service', 'microservices']
    
    def collect(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect API endpoint information
        
        Args:
            repo_path: Repository root
            classification: Classification results
            
        Returns:
            {
                'endpoints': [...],
                'summary': {...},
                'controllers': [...],
                'auth_patterns': [...],
                'metrics': {...}
            }
        """
        logger.info("Collecting API endpoints...")
        
        endpoints = []
        controllers = []
        auth_patterns_found = set()
        detected_frameworks = set()
        
        # Scan Python files
        for py_file in repo_path.rglob('*.py'):
            if self._should_skip(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                file_endpoints, file_framework = self._extract_python_endpoints(
                    content, py_file, repo_path
                )
                endpoints.extend(file_endpoints)
                if file_framework:
                    detected_frameworks.add(file_framework)
                
                # Check for auth patterns
                auth_patterns_found.update(self._find_auth_patterns(content))
                
            except Exception as e:
                logger.debug(f"Error processing {py_file}: {e}")
        
        # Scan C# files
        for cs_file in repo_path.rglob('*.cs'):
            if self._should_skip(cs_file):
                continue
            
            try:
                content = cs_file.read_text(encoding='utf-8', errors='ignore')
                file_endpoints, controller_info = self._extract_csharp_endpoints(
                    content, cs_file, repo_path
                )
                endpoints.extend(file_endpoints)
                if controller_info:
                    controllers.append(controller_info)
                    detected_frameworks.add('aspnet')
                
                auth_patterns_found.update(self._find_auth_patterns(content))
                
            except Exception as e:
                logger.debug(f"Error processing {cs_file}: {e}")
        
        # Scan JavaScript/TypeScript files
        for js_file in list(repo_path.rglob('*.js')) + list(repo_path.rglob('*.ts')):
            if self._should_skip(js_file):
                continue
            
            try:
                content = js_file.read_text(encoding='utf-8', errors='ignore')
                file_endpoints, file_framework = self._extract_js_endpoints(
                    content, js_file, repo_path
                )
                endpoints.extend(file_endpoints)
                if file_framework:
                    detected_frameworks.add(file_framework)
                
            except Exception as e:
                logger.debug(f"Error processing {js_file}: {e}")
        
        # Build summary
        summary = self._build_summary(endpoints)
        
        # Calculate metrics
        metrics = {
            'total_endpoints': len(endpoints),
            'unique_routes': len(set(e['path'] for e in endpoints)),
            'method_distribution': self._count_methods(endpoints),
            'detected_frameworks': list(detected_frameworks),
            'auth_coverage': self._calculate_auth_coverage(endpoints),
            'versioned_apis': self._count_versioned_apis(endpoints)
        }
        
        result = {
            'endpoints': endpoints[:200],  # Limit to 200 endpoints
            'summary': summary,
            'controllers': controllers[:50],  # Limit to 50 controllers
            'auth_patterns': list(auth_patterns_found),
            'metrics': metrics
        }
        
        logger.info(f"✅ API endpoints collected: {len(endpoints)} endpoints, "
                   f"{len(detected_frameworks)} frameworks detected")
        
        return result
    
    def collect_safe(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Safe wrapper with error handling"""
        try:
            return self.collect(repo_path, classification)
        except Exception as e:
            logger.error(f"API endpoint collection failed: {e}")
            return {
                'endpoints': [],
                'summary': {},
                'controllers': [],
                'auth_patterns': [],
                'metrics': {},
                'error': str(e)
            }
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            'node_modules', '__pycache__', 'venv', '.venv',
            'dist', 'build', 'test', 'tests', 'spec', '.git'
        ]
        return any(p in str(file_path) for p in skip_patterns)
    
    def _extract_python_endpoints(
        self,
        content: str,
        file_path: Path,
        repo_path: Path
    ) -> tuple:
        """Extract endpoints from Python files"""
        endpoints = []
        detected_framework = None
        
        # Check for Flask
        if 'flask' in content.lower() or '@app.route' in content:
            detected_framework = 'flask'
            
            # Flask route decorator
            for match in re.finditer(self.FRAMEWORK_PATTERNS['flask']['route'], content):
                route = match.group(1)
                methods_str = match.group(2)
                methods = self._parse_methods(methods_str) if methods_str else ['GET']
                
                for method in methods:
                    endpoints.append(self._create_endpoint(
                        method, route, file_path, repo_path, 'flask'
                    ))
            
            # Flask method decorators (app.get, app.post, etc.)
            for match in re.finditer(self.FRAMEWORK_PATTERNS['flask']['method'], content):
                method = match.group(1).upper()
                route = match.group(2)
                endpoints.append(self._create_endpoint(
                    method, route, file_path, repo_path, 'flask'
                ))
        
        # Check for FastAPI
        if 'fastapi' in content.lower() or 'from fastapi' in content:
            detected_framework = 'fastapi'
            
            for match in re.finditer(self.FRAMEWORK_PATTERNS['fastapi']['route'], content):
                method = match.group(1).upper()
                route = match.group(2)
                endpoints.append(self._create_endpoint(
                    method, route, file_path, repo_path, 'fastapi'
                ))
        
        # Check for Django
        if 'django' in content.lower() or 'path(' in content:
            detected_framework = 'django'
            
            for match in re.finditer(self.FRAMEWORK_PATTERNS['django']['path'], content):
                route = '/' + match.group(1)
                endpoints.append(self._create_endpoint(
                    'ALL', route, file_path, repo_path, 'django'
                ))
        
        return endpoints, detected_framework
    
    def _extract_csharp_endpoints(
        self,
        content: str,
        file_path: Path,
        repo_path: Path
    ) -> tuple:
        """Extract endpoints from C# files"""
        endpoints = []
        controller_info = None
        
        # Check for ApiController attribute
        if '[ApiController]' in content or 'ControllerBase' in content:
            # Extract controller name and route
            class_match = re.search(r'class\s+(\w+)\s*:', content)
            route_match = re.search(r'\[Route\s*\(\s*[\'"]([^\'"]+)[\'"]', content)
            
            if class_match:
                controller_name = class_match.group(1)
                base_route = route_match.group(1) if route_match else ''
                
                controller_info = {
                    'name': controller_name,
                    'file': str(file_path.relative_to(repo_path)),
                    'base_route': base_route
                }
                
                # Extract action methods
                for match in re.finditer(self.FRAMEWORK_PATTERNS['aspnet']['action'], content):
                    method = match.group(1).upper()
                    route_suffix = match.group(2) or ''
                    
                    full_route = self._combine_routes(base_route, route_suffix)
                    endpoints.append(self._create_endpoint(
                        method, full_route, file_path, repo_path, 'aspnet', controller_name
                    ))
        
        return endpoints, controller_info
    
    def _extract_js_endpoints(
        self,
        content: str,
        file_path: Path,
        repo_path: Path
    ) -> tuple:
        """Extract endpoints from JavaScript/TypeScript files"""
        endpoints = []
        detected_framework = None
        
        # Check for Express
        if 'express' in content.lower() or 'app.get(' in content or 'router.get(' in content:
            detected_framework = 'express'
            
            for match in re.finditer(self.FRAMEWORK_PATTERNS['express']['route'], content):
                method = match.group(1).upper()
                route = match.group(2)
                endpoints.append(self._create_endpoint(
                    method, route, file_path, repo_path, 'express'
                ))
        
        # Check for NestJS
        if '@Controller' in content or '@nestjs' in content:
            detected_framework = 'nestjs'
            
            # Get controller base path
            controller_match = re.search(self.FRAMEWORK_PATTERNS['nestjs']['controller'], content)
            base_path = controller_match.group(1) if controller_match else ''
            
            for match in re.finditer(self.FRAMEWORK_PATTERNS['nestjs']['method'], content):
                method = match.group(1).upper()
                route_suffix = match.group(2) or ''
                
                full_route = self._combine_routes(base_path, route_suffix)
                endpoints.append(self._create_endpoint(
                    method, full_route, file_path, repo_path, 'nestjs'
                ))
        
        return endpoints, detected_framework
    
    def _create_endpoint(
        self,
        method: str,
        path: str,
        file_path: Path,
        repo_path: Path,
        framework: str,
        controller: str = None
    ) -> Dict[str, Any]:
        """Create standardized endpoint entry"""
        # Normalize path
        path = path.strip()
        if not path.startswith('/'):
            path = '/' + path
        
        return {
            'method': method,
            'path': path,
            'file': str(file_path.relative_to(repo_path)),
            'framework': framework,
            'controller': controller,
            'parameters': self._extract_parameters(path),
            'requires_auth': False  # Will be updated by auth check
        }
    
    def _combine_routes(self, base: str, suffix: str) -> str:
        """Combine base route with suffix"""
        base = base.strip('/')
        suffix = suffix.strip('/')
        
        if base and suffix:
            return f"/{base}/{suffix}"
        elif base:
            return f"/{base}"
        elif suffix:
            return f"/{suffix}"
        else:
            return "/"
    
    def _extract_parameters(self, path: str) -> List[Dict[str, str]]:
        """Extract route parameters from path"""
        params = []
        
        # Match {param}, :param, <param>, [param] patterns
        for match in re.finditer(r'[{<:\[](\w+)[}>:\]]', path):
            params.append({
                'name': match.group(1),
                'type': 'path'
            })
        
        return params
    
    def _parse_methods(self, methods_str: str) -> List[str]:
        """Parse methods from Flask-style string"""
        methods = []
        for method in self.HTTP_METHODS:
            if method in methods_str.upper():
                methods.append(method)
        return methods if methods else ['GET']
    
    def _find_auth_patterns(self, content: str) -> Set[str]:
        """Find authentication patterns in content"""
        found = set()
        for pattern in self.AUTH_PATTERNS:
            if re.search(pattern, content):
                found.add(pattern.replace(r'\\', '').replace('(?:', '').replace(')', ''))
        return found
    
    def _build_summary(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build endpoint summary"""
        return {
            'total': len(endpoints),
            'by_method': self._count_methods(endpoints),
            'by_framework': self._group_by_key(endpoints, 'framework'),
            'unique_controllers': len(set(e.get('controller') for e in endpoints if e.get('controller')))
        }
    
    def _count_methods(self, endpoints: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count endpoints by HTTP method"""
        counts = defaultdict(int)
        for endpoint in endpoints:
            counts[endpoint['method']] += 1
        return dict(counts)
    
    def _group_by_key(self, endpoints: List[Dict[str, Any]], key: str) -> Dict[str, int]:
        """Group endpoints by a key"""
        groups = defaultdict(int)
        for endpoint in endpoints:
            groups[endpoint.get(key, 'unknown')] += 1
        return dict(groups)
    
    def _calculate_auth_coverage(self, endpoints: List[Dict[str, Any]]) -> float:
        """Calculate percentage of endpoints with auth"""
        if not endpoints:
            return 0.0
        auth_count = sum(1 for e in endpoints if e.get('requires_auth'))
        return round((auth_count / len(endpoints)) * 100, 1)
    
    def _count_versioned_apis(self, endpoints: List[Dict[str, Any]]) -> int:
        """Count endpoints with API versioning"""
        version_pattern = r'/v\d+|/api/v\d+'
        return sum(1 for e in endpoints if re.search(version_pattern, e['path']))
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate collected data"""
        return 'endpoints' in data and 'summary' in data
