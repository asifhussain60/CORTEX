"""
Use Case Inference Engine for Intelligent Dashboard

Infers use cases from API endpoints, controller actions, and service methods.

Features:
- API endpoint analysis (Flask, FastAPI, Express, ASP.NET)
- Controller action detection
- Service layer analysis
- Confidence scoring (0.95 API → 0.70 inferred)

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class UseCaseSource(Enum):
    """Source of use case inference."""
    API_ENDPOINT = "api_endpoint"
    CONTROLLER_ACTION = "controller_action"
    SERVICE_METHOD = "service_method"
    INFERRED = "inferred"


class HttpMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


@dataclass
class UseCase:
    """Use case extracted from code."""
    name: str
    description: str
    source: UseCaseSource
    location: str  # file_path:line_number
    confidence: float
    http_method: Optional[HttpMethod]
    endpoint_path: Optional[str]
    parameters: List[str]
    domain: str  # user, payment, order, etc.


class UseCaseInferenceEngine:
    """
    Infers use cases from source code analysis.
    
    Detection Methods:
    1. API Endpoints (highest confidence: 0.95)
    2. Controller Actions (high confidence: 0.90)
    3. Service Methods (medium confidence: 0.85)
    4. Inferred from patterns (lower confidence: 0.70)
    """
    
    # API framework patterns
    FLASK_ROUTE_PATTERN = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)'
    FASTAPI_ROUTE_PATTERN = r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)'
    EXPRESS_ROUTE_PATTERN = r'app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
    ASPNET_ROUTE_PATTERN = r'\[Http(Get|Post|Put|Delete|Patch)\([\'"]?([^\'")\]]+)?[\'"]?\)\]'
    
    # Controller patterns
    CONTROLLER_CLASS_PATTERN = r'class\s+(\w+)Controller'
    CONTROLLER_METHOD_PATTERN = r'def\s+(\w+)\s*\('
    
    # Service patterns
    SERVICE_CLASS_PATTERN = r'class\s+(\w+)Service'
    SERVICE_METHOD_PATTERN = r'def\s+(\w+)\s*\('
    
    # Domain keywords
    DOMAIN_KEYWORDS = {
        'user': ['user', 'account', 'profile', 'auth', 'login', 'register'],
        'payment': ['payment', 'transaction', 'charge', 'refund', 'invoice'],
        'order': ['order', 'cart', 'checkout', 'purchase'],
        'product': ['product', 'item', 'catalog', 'inventory'],
        'admin': ['admin', 'manage', 'config', 'settings']
    }
    
    def __init__(self):
        """Initialize use case inference engine."""
        self.use_cases_found = 0
    
    def infer_use_cases(
        self,
        ast_tree: Any,
        source_code: str,
        file_path: str
    ) -> List[UseCase]:
        """
        Infer use cases from source code.
        
        Args:
            ast_tree: Tree-sitter AST tree
            source_code: Original source code
            file_path: File path for location tracking
            
        Returns:
            List of UseCase objects with metadata
        """
        use_cases = []
        
        # Try API endpoint detection first (highest confidence)
        use_cases.extend(self._detect_api_endpoints(source_code, file_path))
        
        # Try controller action detection
        use_cases.extend(self._detect_controller_actions(source_code, file_path))
        
        # Try service method detection
        use_cases.extend(self._detect_service_methods(source_code, file_path))
        
        self.use_cases_found += len(use_cases)
        return use_cases
    
    def _detect_api_endpoints(
        self,
        source_code: str,
        file_path: str
    ) -> List[UseCase]:
        """Detect API endpoints from decorators."""
        use_cases = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Flask routes
            match = re.search(self.FLASK_ROUTE_PATTERN, line)
            if match:
                endpoint_path = match.group(1)
                methods_str = match.group(2) if match.group(2) else 'GET'
                
                # Get function name from next line
                func_name = self._get_function_name(lines, line_num)
                
                use_case = self._create_api_use_case(
                    func_name or "unknown",
                    endpoint_path,
                    methods_str,
                    file_path,
                    line_num,
                    "Flask"
                )
                use_cases.append(use_case)
            
            # FastAPI routes
            match = re.search(self.FASTAPI_ROUTE_PATTERN, line)
            if match:
                http_method = match.group(1).upper()
                endpoint_path = match.group(2)
                
                func_name = self._get_function_name(lines, line_num)
                
                use_case = self._create_api_use_case(
                    func_name or "unknown",
                    endpoint_path,
                    http_method,
                    file_path,
                    line_num,
                    "FastAPI"
                )
                use_cases.append(use_case)
            
            # Express routes
            match = re.search(self.EXPRESS_ROUTE_PATTERN, line)
            if match:
                http_method = match.group(1).upper()
                endpoint_path = match.group(2)
                
                use_case = self._create_api_use_case(
                    endpoint_path.split('/')[-1] or "unknown",
                    endpoint_path,
                    http_method,
                    file_path,
                    line_num,
                    "Express"
                )
                use_cases.append(use_case)
            
            # ASP.NET routes
            match = re.search(self.ASPNET_ROUTE_PATTERN, line)
            if match:
                http_method = match.group(1).upper()
                endpoint_path = match.group(2) or ""
                
                func_name = self._get_function_name(lines, line_num)
                
                use_case = self._create_api_use_case(
                    func_name or "unknown",
                    endpoint_path,
                    http_method,
                    file_path,
                    line_num,
                    "ASP.NET"
                )
                use_cases.append(use_case)
        
        return use_cases
    
    def _detect_controller_actions(
        self,
        source_code: str,
        file_path: str
    ) -> List[UseCase]:
        """Detect controller actions."""
        use_cases = []
        lines = source_code.split('\n')
        
        # Check if this is a controller file
        controller_match = re.search(self.CONTROLLER_CLASS_PATTERN, source_code)
        if not controller_match:
            return use_cases
        
        controller_name = controller_match.group(1)
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(self.CONTROLLER_METHOD_PATTERN, line)
            if match:
                method_name = match.group(1)
                
                # Skip private methods
                if method_name.startswith('_'):
                    continue
                
                use_case = UseCase(
                    name=f"{controller_name}.{method_name}",
                    description=self._generate_description(method_name, "controller action"),
                    source=UseCaseSource.CONTROLLER_ACTION,
                    location=f"{file_path}:{line_num}",
                    confidence=0.90,
                    http_method=None,
                    endpoint_path=None,
                    parameters=self._extract_parameters(lines, line_num),
                    domain=self._infer_domain(method_name)
                )
                use_cases.append(use_case)
        
        return use_cases
    
    def _detect_service_methods(
        self,
        source_code: str,
        file_path: str
    ) -> List[UseCase]:
        """Detect service layer methods."""
        use_cases = []
        lines = source_code.split('\n')
        
        # Check if this is a service file
        service_match = re.search(self.SERVICE_CLASS_PATTERN, source_code)
        if not service_match:
            return use_cases
        
        service_name = service_match.group(1)
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(self.SERVICE_METHOD_PATTERN, line)
            if match:
                method_name = match.group(1)
                
                # Skip private methods
                if method_name.startswith('_'):
                    continue
                
                use_case = UseCase(
                    name=f"{service_name}.{method_name}",
                    description=self._generate_description(method_name, "service method"),
                    source=UseCaseSource.SERVICE_METHOD,
                    location=f"{file_path}:{line_num}",
                    confidence=0.85,
                    http_method=None,
                    endpoint_path=None,
                    parameters=self._extract_parameters(lines, line_num),
                    domain=self._infer_domain(method_name)
                )
                use_cases.append(use_case)
        
        return use_cases
    
    def _create_api_use_case(
        self,
        func_name: str,
        endpoint_path: str,
        http_method_str: str,
        file_path: str,
        line_num: int,
        framework: str
    ) -> UseCase:
        """Create UseCase from API endpoint."""
        # Parse HTTP method
        if 'GET' in http_method_str.upper():
            http_method = HttpMethod.GET
        elif 'POST' in http_method_str.upper():
            http_method = HttpMethod.POST
        elif 'PUT' in http_method_str.upper():
            http_method = HttpMethod.PUT
        elif 'DELETE' in http_method_str.upper():
            http_method = HttpMethod.DELETE
        elif 'PATCH' in http_method_str.upper():
            http_method = HttpMethod.PATCH
        else:
            http_method = HttpMethod.GET
        
        # Generate description from endpoint path
        description = self._generate_api_description(http_method, endpoint_path)
        
        return UseCase(
            name=func_name,
            description=description,
            source=UseCaseSource.API_ENDPOINT,
            location=f"{file_path}:{line_num}",
            confidence=0.95,
            http_method=http_method,
            endpoint_path=endpoint_path,
            parameters=[],
            domain=self._infer_domain(endpoint_path)
        )
    
    def _get_function_name(self, lines: List[str], decorator_line: int) -> Optional[str]:
        """Get function name from line after decorator."""
        if decorator_line < len(lines):
            next_line = lines[decorator_line].strip()
            match = re.search(r'def\s+(\w+)\s*\(', next_line)
            if match:
                return match.group(1)
        return None
    
    def _generate_api_description(self, http_method: HttpMethod, endpoint_path: str) -> str:
        """Generate human-readable description from API endpoint."""
        # Extract resource from path
        parts = [p for p in endpoint_path.split('/') if p and not p.startswith('<')]
        resource = parts[-1] if parts else "resource"
        
        if http_method == HttpMethod.GET:
            return f"Retrieve {resource}"
        elif http_method == HttpMethod.POST:
            return f"Create {resource}"
        elif http_method == HttpMethod.PUT:
            return f"Update {resource}"
        elif http_method == HttpMethod.DELETE:
            return f"Delete {resource}"
        elif http_method == HttpMethod.PATCH:
            return f"Partially update {resource}"
        else:
            return f"Process {resource}"
    
    def _generate_description(self, method_name: str, context: str) -> str:
        """Generate description from method name."""
        # Convert camelCase/snake_case to words
        words = re.sub(r'([A-Z])', r' \1', method_name).split('_')
        words = [w.strip() for w in words if w.strip()]
        return f"{' '.join(words)} ({context})"
    
    def _extract_parameters(self, lines: List[str], line_num: int) -> List[str]:
        """Extract function parameters."""
        if line_num < 1 or line_num > len(lines):
            return []
        
        line = lines[line_num - 1]
        match = re.search(r'\(([^)]+)\)', line)
        if match:
            params_str = match.group(1)
            params = [p.split(':')[0].strip() for p in params_str.split(',')]
            # Filter out 'self', 'cls'
            params = [p for p in params if p not in ['self', 'cls', '']]
            return params
        
        return []
    
    def _infer_domain(self, text: str) -> str:
        """Infer domain from text."""
        text_lower = text.lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        
        return 'general'
    
    def get_statistics(self) -> Dict[str, int]:
        """Get inference statistics."""
        return {
            'use_cases_found': self.use_cases_found
        }
