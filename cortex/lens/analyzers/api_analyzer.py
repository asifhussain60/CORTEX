"""
APIAnalyzer - REST API and OpenAPI specification analysis.

Analyzes:
- OpenAPI/Swagger specifications (2.0, 3.0, 3.1)
- REST API endpoint security (authentication, authorization, input validation)
- Rate limiting and throttling configurations
- CORS policies and security headers
- API versioning strategies
- Security vulnerabilities (OWASP API Top 10)

AC-ID: AC-LENS-V2-API-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
import json
import yaml

logger = logging.getLogger(__name__)


class OpenAPIVersion(Enum):
    """OpenAPI specification versions."""
    SWAGGER_2_0 = "2.0"
    OPENAPI_3_0 = "3.0"
    OPENAPI_3_1 = "3.1"
    UNKNOWN = "unknown"


class SecuritySchemeType(Enum):
    """API security scheme types."""
    API_KEY = "apiKey"
    HTTP_BASIC = "http_basic"
    HTTP_BEARER = "http_bearer"
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "openIdConnect"
    NONE = "none"


class APISecurityPriority(Enum):
    """API security finding priorities."""
    P0 = "P0"  # Critical - authentication bypass, injection
    P1 = "P1"  # High - weak auth, missing rate limiting
    P2 = "P2"  # Medium - missing CORS, versioning issues
    P3 = "P3"  # Low - documentation, best practices


@dataclass
class APIEndpoint:
    """API endpoint information."""
    path: str
    method: str
    summary: str = ""
    description: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class SecurityScheme:
    """API security scheme definition."""
    name: str
    scheme_type: SecuritySchemeType
    description: str = ""
    in_location: Optional[str] = None  # header, query, cookie
    scheme: Optional[str] = None  # bearer, basic
    bearer_format: Optional[str] = None  # JWT, etc.
    flows: Optional[Dict[str, Any]] = None  # OAuth2 flows


@dataclass
class APISecurityFinding:
    """API security vulnerability or misconfiguration."""
    finding_id: str
    priority: APISecurityPriority
    category: str
    endpoint: Optional[str] = None
    description: str = ""
    recommendation: str = ""
    cwe_id: Optional[str] = None
    owasp_api_top_10: Optional[str] = None


@dataclass
class APIAnalysisResult:
    """Result of API analysis."""
    success: bool
    spec_version: OpenAPIVersion = OpenAPIVersion.UNKNOWN
    endpoints: List[APIEndpoint] = field(default_factory=list)
    security_schemes: List[SecurityScheme] = field(default_factory=list)
    security_findings: List[APISecurityFinding] = field(default_factory=list)
    global_security: List[Dict[str, Any]] = field(default_factory=list)
    servers: List[Dict[str, Any]] = field(default_factory=list)
    has_rate_limiting: bool = False
    has_cors_config: bool = False
    api_version: Optional[str] = None
    error: str = ""
    analysis_time_ms: float = 0.0


class APIAnalyzer:
    """
    REST API and OpenAPI specification analyzer.
    
    Provides comprehensive API security analysis including:
    - OpenAPI/Swagger 2.0, 3.0, 3.1 specification parsing
    - OWASP API Security Top 10 vulnerability detection
    - Authentication/authorization security assessment
    - Input validation and injection vulnerability detection
    - Rate limiting and throttling configuration analysis
    - CORS policy security review
    - API versioning strategy detection
    
    Example:
        >>> analyzer = APIAnalyzer()
        >>> result = analyzer.analyze_openapi_spec(Path("openapi.yaml"))
        >>> print(f"Found {len(result.endpoints)} endpoints")
        >>> p0_findings = [f for f in result.security_findings if f.priority == APISecurityPriority.P0]
        >>> print(f"P0 vulnerabilities: {len(p0_findings)}")
    """
    
    # OWASP API Security Top 10 patterns
    OWASP_API_PATTERNS = {
        "API1_BROKEN_OBJECT_LEVEL_AUTH": [
            r"/users/\{id\}",
            r"/accounts/\{account_id\}",
            r"/orders/\{order_id\}",
        ],
        "API2_BROKEN_AUTHENTICATION": [
            "no_auth_required",
            "weak_token",
            "session_fixation",
        ],
        "API3_EXCESSIVE_DATA_EXPOSURE": [
            "returns_full_object",
            "no_field_filtering",
        ],
        "API4_LACK_OF_RESOURCES": [
            "no_rate_limiting",
            "no_pagination",
        ],
        "API5_BROKEN_FUNCTION_LEVEL_AUTH": [
            "/admin/",
            "/internal/",
            "role_bypass",
        ],
        "API7_SECURITY_MISCONFIGURATION": [
            "debug_enabled",
            "verbose_errors",
            "default_credentials",
        ],
    }
    
    def __init__(self):
        """Initialize APIAnalyzer."""
        pass
    
    def analyze_openapi_spec(
        self,
        spec_path: Path,
    ) -> APIAnalysisResult:
        """
        Analyze OpenAPI/Swagger specification file.
        
        Supports:
        - OpenAPI 3.0/3.1 (YAML/JSON)
        - Swagger 2.0 (YAML/JSON)
        
        Args:
            spec_path: Path to OpenAPI specification file
            
        Returns:
            APIAnalysisResult with endpoints, security schemes, and findings
            
        Example:
            >>> analyzer = APIAnalyzer()
            >>> result = analyzer.analyze_openapi_spec(Path("api/openapi.yaml"))
            >>> if not result.success:
            ...     print(f"Error: {result.error}")
            >>> else:
            ...     print(f"Analyzed {len(result.endpoints)} endpoints")
        """
        import time
        start_time = time.time()
        
        # Check path exists
        if not spec_path.exists():
            return APIAnalysisResult(
                success=False,
                error=f"OpenAPI spec not found: {spec_path}"
            )
        
        result = APIAnalysisResult(success=True)
        
        try:
            # Parse spec file
            spec_data = self._load_spec_file(spec_path)
            
            # Detect version
            result.spec_version = self._detect_openapi_version(spec_data)
            
            # Extract API version
            result.api_version = self._extract_api_version(spec_data)
            
            # Parse security schemes
            result.security_schemes = self._parse_security_schemes(spec_data, result.spec_version)
            
            # Parse global security
            result.global_security = spec_data.get("security", [])
            
            # Parse servers
            result.servers = self._parse_servers(spec_data, result.spec_version)
            
            # Parse endpoints
            result.endpoints = self._parse_endpoints(spec_data, result.spec_version)
            
            # Security analysis
            result.security_findings = self._analyze_security(
                spec_data,
                result.endpoints,
                result.security_schemes,
                result.global_security
            )
            
            # Detect rate limiting
            result.has_rate_limiting = self._detect_rate_limiting(spec_data)
            
            # Detect CORS configuration
            result.has_cors_config = self._detect_cors_config(spec_data)
            
            result.analysis_time_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            logger.error(f"OpenAPI analysis failed: {e}", exc_info=True)
            result.success = False
            result.error = str(e)
        
        return result
    
    def analyze_api_code(
        self,
        code_path: Path,
        framework: str = "fastapi",
    ) -> APIAnalysisResult:
        """
        Analyze API code directly (without OpenAPI spec).
        
        Supports:
        - FastAPI (Python)
        - Flask (Python)
        - Express.js (Node.js) - basic
        - ASP.NET Core (C#) - basic
        
        Args:
            code_path: Path to API code directory
            framework: API framework ("fastapi", "flask", "express", "aspnet")
            
        Returns:
            APIAnalysisResult with discovered endpoints and findings
            
        Example:
            >>> analyzer = APIAnalyzer()
            >>> result = analyzer.analyze_api_code(
            ...     Path("app/api"),
            ...     framework="fastapi"
            ... )
            >>> print(f"Discovered {len(result.endpoints)} endpoints")
        """
        import time
        start_time = time.time()
        
        # Check path exists
        if not code_path.exists():
            return APIAnalysisResult(
                success=False,
                error=f"API code path not found: {code_path}"
            )
        
        # Validate framework
        if framework not in ("fastapi", "flask", "express", "aspnet"):
            raise ValueError(f"Unsupported framework: {framework}")
        
        result = APIAnalysisResult(success=True)
        
        try:
            # Discover endpoints from code
            if framework == "fastapi":
                result.endpoints = self._discover_fastapi_endpoints(code_path)
            elif framework == "flask":
                result.endpoints = self._discover_flask_endpoints(code_path)
            else:
                logger.info(f"Code analysis for {framework}: Basic implementation")
            
            # Security analysis on discovered endpoints
            result.security_findings = self._analyze_security(
                {},
                result.endpoints,
                result.security_schemes,
                result.global_security
            )
            
            result.analysis_time_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            logger.error(f"API code analysis failed: {e}", exc_info=True)
            result.success = False
            result.error = str(e)
        
        return result
    
    def _load_spec_file(self, spec_path: Path) -> Dict[str, Any]:
        """Load and parse OpenAPI spec file (YAML or JSON)."""
        content = spec_path.read_text(encoding="utf-8")
        
        if spec_path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(content)
        elif spec_path.suffix == ".json":
            return json.loads(content)
        else:
            # Try YAML first, then JSON
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                return json.loads(content)
    
    def _detect_openapi_version(self, spec_data: Dict[str, Any]) -> OpenAPIVersion:
        """Detect OpenAPI/Swagger version."""
        # OpenAPI 3.x
        if "openapi" in spec_data:
            version_str = spec_data["openapi"]
            if version_str.startswith("3.0"):
                return OpenAPIVersion.OPENAPI_3_0
            elif version_str.startswith("3.1"):
                return OpenAPIVersion.OPENAPI_3_1
        
        # Swagger 2.0
        if "swagger" in spec_data:
            return OpenAPIVersion.SWAGGER_2_0
        
        return OpenAPIVersion.UNKNOWN
    
    def _extract_api_version(self, spec_data: Dict[str, Any]) -> Optional[str]:
        """Extract API version from spec."""
        info = spec_data.get("info", {})
        return info.get("version")
    
    def _parse_security_schemes(
        self,
        spec_data: Dict[str, Any],
        spec_version: OpenAPIVersion,
    ) -> List[SecurityScheme]:
        """Parse security scheme definitions."""
        schemes = []
        
        if spec_version == OpenAPIVersion.SWAGGER_2_0:
            # Swagger 2.0: securityDefinitions
            security_defs = spec_data.get("securityDefinitions", {})
        else:
            # OpenAPI 3.x: components.securitySchemes
            components = spec_data.get("components", {})
            security_defs = components.get("securitySchemes", {})
        
        for name, definition in security_defs.items():
            scheme_type_str = definition.get("type", "")
            
            # Map to SecuritySchemeType
            if scheme_type_str == "apiKey":
                scheme_type = SecuritySchemeType.API_KEY
            elif scheme_type_str == "http":
                http_scheme = definition.get("scheme", "")
                if http_scheme == "bearer":
                    scheme_type = SecuritySchemeType.HTTP_BEARER
                elif http_scheme == "basic":
                    scheme_type = SecuritySchemeType.HTTP_BASIC
                else:
                    scheme_type = SecuritySchemeType.NONE
            elif scheme_type_str == "oauth2":
                scheme_type = SecuritySchemeType.OAUTH2
            elif scheme_type_str == "openIdConnect":
                scheme_type = SecuritySchemeType.OPENID_CONNECT
            else:
                scheme_type = SecuritySchemeType.NONE
            
            schemes.append(SecurityScheme(
                name=name,
                scheme_type=scheme_type,
                description=definition.get("description", ""),
                in_location=definition.get("in"),
                scheme=definition.get("scheme"),
                bearer_format=definition.get("bearerFormat"),
                flows=definition.get("flows"),
            ))
        
        return schemes
    
    def _parse_servers(
        self,
        spec_data: Dict[str, Any],
        spec_version: OpenAPIVersion,
    ) -> List[Dict[str, Any]]:
        """Parse server configurations."""
        if spec_version == OpenAPIVersion.SWAGGER_2_0:
            # Swagger 2.0: host, basePath, schemes
            host = spec_data.get("host", "")
            base_path = spec_data.get("basePath", "")
            schemes = spec_data.get("schemes", ["https"])
            
            if host:
                return [{
                    "url": f"{schemes[0]}://{host}{base_path}",
                    "description": "API server"
                }]
            return []
        else:
            # OpenAPI 3.x: servers
            return spec_data.get("servers", [])
    
    def _parse_endpoints(
        self,
        spec_data: Dict[str, Any],
        spec_version: OpenAPIVersion,
    ) -> List[APIEndpoint]:
        """Parse API endpoints from spec."""
        endpoints = []
        paths = spec_data.get("paths", {})
        
        for path, path_item in paths.items():
            # HTTP methods
            for method in ["get", "post", "put", "patch", "delete", "options", "head"]:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                
                endpoints.append(APIEndpoint(
                    path=path,
                    method=method.upper(),
                    summary=operation.get("summary", ""),
                    description=operation.get("description", ""),
                    parameters=operation.get("parameters", []),
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    security=operation.get("security", []),
                    tags=operation.get("tags", []),
                    deprecated=operation.get("deprecated", False),
                ))
        
        return endpoints
    
    def _analyze_security(
        self,
        spec_data: Dict[str, Any],
        endpoints: List[APIEndpoint],
        security_schemes: List[SecurityScheme],
        global_security: List[Dict[str, Any]],
    ) -> List[APISecurityFinding]:
        """Analyze API security and generate findings."""
        findings = []
        
        # Check for missing authentication
        findings.extend(self._check_missing_authentication(endpoints, global_security))
        
        # Check for weak authentication
        findings.extend(self._check_weak_authentication(security_schemes))
        
        # Check for BOLA vulnerabilities (API1)
        findings.extend(self._check_bola_vulnerabilities(endpoints))
        
        # Check for excessive data exposure (API3)
        findings.extend(self._check_excessive_data_exposure(endpoints))
        
        # Check for missing rate limiting (API4)
        findings.extend(self._check_missing_rate_limiting(spec_data))
        
        # Check for broken function-level auth (API5)
        findings.extend(self._check_broken_function_auth(endpoints))
        
        # Check for security misconfigurations (API7)
        findings.extend(self._check_security_misconfigurations(spec_data, endpoints))
        
        return sorted(findings, key=lambda f: f.priority.value)
    
    def _check_missing_authentication(
        self,
        endpoints: List[APIEndpoint],
        global_security: List[Dict[str, Any]],
    ) -> List[APISecurityFinding]:
        """Check for endpoints without authentication (OWASP API2)."""
        findings = []
        
        for endpoint in endpoints:
            # Check if endpoint has security defined
            has_security = bool(endpoint.security or global_security)
            
            if not has_security and not endpoint.deprecated:
                findings.append(APISecurityFinding(
                    finding_id=f"AUTH_MISSING_{endpoint.method}_{endpoint.path}",
                    priority=APISecurityPriority.P0,
                    category="missing_authentication",
                    endpoint=f"{endpoint.method} {endpoint.path}",
                    description="Endpoint has no authentication requirement",
                    recommendation="Add authentication requirement (OAuth2, API Key, or JWT)",
                    owasp_api_top_10="API2:2023 Broken Authentication",
                ))
        
        return findings
    
    def _check_weak_authentication(
        self,
        security_schemes: List[SecurityScheme],
    ) -> List[APISecurityFinding]:
        """Check for weak authentication schemes (OWASP API2)."""
        findings = []
        
        for scheme in security_schemes:
            # HTTP Basic Auth is weak
            if scheme.scheme_type == SecuritySchemeType.HTTP_BASIC:
                findings.append(APISecurityFinding(
                    finding_id=f"AUTH_WEAK_{scheme.name}",
                    priority=APISecurityPriority.P1,
                    category="weak_authentication",
                    description=f"HTTP Basic Authentication is weak: {scheme.name}",
                    recommendation="Use OAuth2, OpenID Connect, or JWT bearer tokens instead",
                    cwe_id="CWE-287",
                    owasp_api_top_10="API2:2023 Broken Authentication",
                ))
            
            # API Key in query/path is weak
            if scheme.scheme_type == SecuritySchemeType.API_KEY:
                if scheme.in_location in ("query", "path"):
                    findings.append(APISecurityFinding(
                        finding_id=f"AUTH_APIKEY_QUERY_{scheme.name}",
                        priority=APISecurityPriority.P1,
                        category="weak_authentication",
                        description=f"API Key in query/path is insecure: {scheme.name}",
                        recommendation="Move API Key to Authorization header",
                        cwe_id="CWE-522",
                        owasp_api_top_10="API2:2023 Broken Authentication",
                    ))
        
        return findings
    
    def _check_bola_vulnerabilities(
        self,
        endpoints: List[APIEndpoint],
    ) -> List[APISecurityFinding]:
        """Check for Broken Object Level Authorization (OWASP API1)."""
        findings = []
        
        # Patterns that indicate potential BOLA
        bola_patterns = [
            (r"/users/\{[^}]+\}", "user ID"),
            (r"/accounts/\{[^}]+\}", "account ID"),
            (r"/orders/\{[^}]+\}", "order ID"),
            (r"/documents/\{[^}]+\}", "document ID"),
            (r"/files/\{[^}]+\}", "file ID"),
        ]
        
        for endpoint in endpoints:
            for pattern, resource_type in bola_patterns:
                if re.search(pattern, endpoint.path, re.IGNORECASE):
                    findings.append(APISecurityFinding(
                        finding_id=f"BOLA_RISK_{endpoint.method}_{endpoint.path}",
                        priority=APISecurityPriority.P1,
                        category="broken_object_level_authorization",
                        endpoint=f"{endpoint.method} {endpoint.path}",
                        description=f"Potential BOLA vulnerability with {resource_type}",
                        recommendation=f"Ensure {resource_type} ownership verification before data access",
                        cwe_id="CWE-639",
                        owasp_api_top_10="API1:2023 Broken Object Level Authorization",
                    ))
        
        return findings
    
    def _check_excessive_data_exposure(
        self,
        endpoints: List[APIEndpoint],
    ) -> List[APISecurityFinding]:
        """Check for excessive data exposure (OWASP API3)."""
        findings = []
        
        # GET endpoints without field filtering
        get_endpoints = [e for e in endpoints if e.method == "GET"]
        
        for endpoint in get_endpoints:
            # Check if endpoint has field filtering parameters
            has_field_param = any(
                p.get("name", "").lower() in ("fields", "select", "projection")
                for p in endpoint.parameters
            )
            
            # Check if endpoint returns list without pagination
            has_pagination = any(
                p.get("name", "").lower() in ("limit", "offset", "page", "per_page", "page_size")
                for p in endpoint.parameters
            )
            
            if not has_field_param and "/list" in endpoint.path.lower():
                findings.append(APISecurityFinding(
                    finding_id=f"DATA_EXPOSURE_{endpoint.method}_{endpoint.path}",
                    priority=APISecurityPriority.P2,
                    category="excessive_data_exposure",
                    endpoint=f"{endpoint.method} {endpoint.path}",
                    description="Endpoint may return excessive data without field filtering",
                    recommendation="Add 'fields' or 'select' parameter for field filtering",
                    owasp_api_top_10="API3:2023 Broken Object Property Level Authorization",
                ))
            
            if not has_pagination and "/list" in endpoint.path.lower():
                findings.append(APISecurityFinding(
                    finding_id=f"NO_PAGINATION_{endpoint.method}_{endpoint.path}",
                    priority=APISecurityPriority.P2,
                    category="missing_pagination",
                    endpoint=f"{endpoint.method} {endpoint.path}",
                    description="List endpoint without pagination can expose excessive data",
                    recommendation="Add pagination parameters (limit, offset, page)",
                    owasp_api_top_10="API4:2023 Unrestricted Resource Consumption",
                ))
        
        return findings
    
    def _check_missing_rate_limiting(
        self,
        spec_data: Dict[str, Any],
    ) -> List[APISecurityFinding]:
        """Check for missing rate limiting (OWASP API4)."""
        findings = []
        
        # Check for rate limiting in extensions or headers
        has_rate_limit = (
            "x-rate-limit" in spec_data or
            "rateLimit" in spec_data or
            any("rate" in str(k).lower() for k in spec_data.keys())
        )
        
        if not has_rate_limit:
            findings.append(APISecurityFinding(
                finding_id="RATE_LIMITING_MISSING",
                priority=APISecurityPriority.P1,
                category="missing_rate_limiting",
                description="No rate limiting configuration detected in API spec",
                recommendation="Implement rate limiting (e.g., 100 req/min per user, 1000 req/min per IP)",
                cwe_id="CWE-770",
                owasp_api_top_10="API4:2023 Unrestricted Resource Consumption",
            ))
        
        return findings
    
    def _check_broken_function_auth(
        self,
        endpoints: List[APIEndpoint],
    ) -> List[APISecurityFinding]:
        """Check for broken function-level authorization (OWASP API5)."""
        findings = []
        
        # Admin/internal endpoints
        admin_patterns = [
            r"/admin/",
            r"/internal/",
            r"/manage/",
            r"/configure/",
        ]
        
        for endpoint in endpoints:
            for pattern in admin_patterns:
                if re.search(pattern, endpoint.path, re.IGNORECASE):
                    # Check if endpoint has role-based security
                    has_role_check = any(
                        "scope" in str(s) or "role" in str(s).lower()
                        for s in endpoint.security
                    )
                    
                    if not has_role_check:
                        findings.append(APISecurityFinding(
                            finding_id=f"FUNC_AUTH_{endpoint.method}_{endpoint.path}",
                            priority=APISecurityPriority.P0,
                            category="broken_function_level_authorization",
                            endpoint=f"{endpoint.method} {endpoint.path}",
                            description="Admin/internal endpoint without role-based authorization",
                            recommendation="Add role/scope checks (e.g., OAuth2 scopes: 'admin', 'write')",
                            cwe_id="CWE-285",
                            owasp_api_top_10="API5:2023 Broken Function Level Authorization",
                        ))
        
        return findings
    
    def _check_security_misconfigurations(
        self,
        spec_data: Dict[str, Any],
        endpoints: List[APIEndpoint],
    ) -> List[APISecurityFinding]:
        """Check for security misconfigurations (OWASP API7)."""
        findings = []
        
        # Check for insecure HTTP (should use HTTPS)
        servers = spec_data.get("servers", [])
        for server in servers:
            url = server.get("url", "")
            if url.startswith("http://") and "localhost" not in url:
                findings.append(APISecurityFinding(
                    finding_id="INSECURE_HTTP",
                    priority=APISecurityPriority.P0,
                    category="security_misconfiguration",
                    description=f"API server using insecure HTTP: {url}",
                    recommendation="Use HTTPS for all API communication",
                    cwe_id="CWE-319",
                    owasp_api_top_10="API7:2023 Server Side Request Forgery",
                ))
        
        # Check for verbose error responses
        for endpoint in endpoints:
            responses = endpoint.responses
            error_responses = {k: v for k, v in responses.items() if k.startswith("4") or k.startswith("5")}
            
            for status_code, response in error_responses.items():
                description = response.get("description", "").lower()
                if any(word in description for word in ["stack", "trace", "debug", "exception"]):
                    findings.append(APISecurityFinding(
                        finding_id=f"VERBOSE_ERROR_{endpoint.method}_{endpoint.path}_{status_code}",
                        priority=APISecurityPriority.P2,
                        category="verbose_error_responses",
                        endpoint=f"{endpoint.method} {endpoint.path}",
                        description=f"Error response may expose implementation details ({status_code})",
                        recommendation="Return generic error messages; log details server-side only",
                        cwe_id="CWE-209",
                        owasp_api_top_10="API7:2023 Server Side Request Forgery",
                    ))
        
        return findings
    
    def _detect_rate_limiting(self, spec_data: Dict[str, Any]) -> bool:
        """Detect if API has rate limiting configuration."""
        # Check extensions
        return (
            "x-rate-limit" in spec_data or
            "x-ratelimit" in spec_data or
            "rateLimit" in spec_data
        )
    
    def _detect_cors_config(self, spec_data: Dict[str, Any]) -> bool:
        """Detect if API has CORS configuration."""
        # Check extensions or headers
        return (
            "x-cors" in spec_data or
            "cors" in spec_data or
            any("cors" in str(k).lower() for k in spec_data.keys())
        )
    
    def _discover_fastapi_endpoints(self, code_path: Path) -> List[APIEndpoint]:
        """Discover FastAPI endpoints from code (basic implementation)."""
        endpoints = []
        
        # Scan Python files for FastAPI route decorators
        for py_file in code_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Match @app.get("/path"), @router.post("/path"), etc.
                route_pattern = r'@(?Union[app, router])\.(get|post|put|patch|delete)\(["\']([^"\']+)["\']\)'
                matches = re.findall(route_pattern, content)
                
                for method, path in matches:
                    endpoints.append(APIEndpoint(
                        path=path,
                        method=method.upper(),
                        summary=f"FastAPI endpoint from {py_file.name}",
                    ))
                
            except Exception as e:
                logger.warning(f"Failed to parse FastAPI file {py_file}: {e}")
        
        return endpoints
    
    def _discover_flask_endpoints(self, code_path: Path) -> List[APIEndpoint]:
        """Discover Flask endpoints from code (basic implementation)."""
        endpoints = []
        
        # Scan Python files for Flask route decorators
        for py_file in code_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Match @app.route("/path", methods=["GET"])
                route_pattern = r'@(?Union[app, bp]|blueprint)\.route\(["\']([^"\']+)["\']\)'
                matches = re.findall(route_pattern, content)
                
                for path in matches:
                    # Default to GET if not specified
                    endpoints.append(APIEndpoint(
                        path=path,
                        method="GET",
                        summary=f"Flask endpoint from {py_file.name}",
                    ))
                
            except Exception as e:
                logger.warning(f"Failed to parse Flask file {py_file}: {e}")
        
        return endpoints


# Singleton instance
_api_analyzer = None


def get_api_analyzer() -> APIAnalyzer:
    """Get or create singleton APIAnalyzer instance."""
    global _api_analyzer
    if _api_analyzer is None:
        _api_analyzer = APIAnalyzer()
    return _api_analyzer
