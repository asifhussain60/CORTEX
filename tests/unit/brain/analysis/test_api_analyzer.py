"""
Tests for APIAnalyzer - REST API and OpenAPI analysis.

AC-ID: AC-LENS-V2-API-TEST-001
Authority: CORE-008 (TDD)
"""

import pytest
import json
import yaml
from pathlib import Path
from cortex.lens.analyzers.api_analyzer import (
    APIAnalyzer,
    get_api_analyzer,
    OpenAPIVersion,
    SecuritySchemeType,
    APISecurityPriority,
    APIEndpoint,
    SecurityScheme,
    APISecurityFinding,
    APIAnalysisResult,
)


class TestAPIAnalyzer:
    """Test suite for APIAnalyzer."""
    
    def test_initialization(self):
        """Test APIAnalyzer initialization."""
        analyzer = APIAnalyzer()
        assert analyzer is not None
    
    def test_singleton_pattern(self):
        """Test singleton pattern for get_api_analyzer()."""
        analyzer1 = get_api_analyzer()
        analyzer2 = get_api_analyzer()
        assert analyzer1 is analyzer2
    
    def test_openapi_version_enum(self):
        """Test OpenAPIVersion enum values."""
        assert OpenAPIVersion.SWAGGER_2_0.value == "2.0"
        assert OpenAPIVersion.OPENAPI_3_0.value == "3.0"
        assert OpenAPIVersion.OPENAPI_3_1.value == "3.1"
        assert OpenAPIVersion.UNKNOWN.value == "unknown"
    
    def test_security_scheme_type_enum(self):
        """Test SecuritySchemeType enum values."""
        assert SecuritySchemeType.API_KEY.value == "apiKey"
        assert SecuritySchemeType.HTTP_BEARER.value == "http_bearer"
        assert SecuritySchemeType.OAUTH2.value == "oauth2"
    
    def test_api_security_priority_enum(self):
        """Test APISecurityPriority enum values."""
        assert APISecurityPriority.P0.value == "P0"
        assert APISecurityPriority.P1.value == "P1"
        assert APISecurityPriority.P2.value == "P2"
        assert APISecurityPriority.P3.value == "P3"
    
    def test_api_endpoint_dataclass(self):
        """Test APIEndpoint dataclass."""
        endpoint = APIEndpoint(
            path="/users/{id}",
            method="GET",
            summary="Get user by ID",
            parameters=[{"name": "id", "in": "path"}],
            security=[{"bearerAuth": []}]
        )
        assert endpoint.path == "/users/{id}"
        assert endpoint.method == "GET"
        assert len(endpoint.parameters) == 1
        assert len(endpoint.security) == 1
    
    def test_security_scheme_dataclass(self):
        """Test SecurityScheme dataclass."""
        scheme = SecurityScheme(
            name="bearerAuth",
            scheme_type=SecuritySchemeType.HTTP_BEARER,
            description="JWT Bearer token",
            in_location="header",
            bearer_format="JWT"
        )
        assert scheme.name == "bearerAuth"
        assert scheme.scheme_type == SecuritySchemeType.HTTP_BEARER
        assert scheme.bearer_format == "JWT"
    
    def test_api_security_finding_dataclass(self):
        """Test APISecurityFinding dataclass."""
        finding = APISecurityFinding(
            finding_id="AUTH_001",
            priority=APISecurityPriority.P0,
            category="missing_authentication",
            endpoint="GET /api/users",
            description="No authentication required",
            recommendation="Add OAuth2 authentication",
            owasp_api_top_10="API2:2023 Broken Authentication"
        )
        assert finding.priority == APISecurityPriority.P0
        assert "API2:2023" in finding.owasp_api_top_10
    
    def test_analyze_nonexistent_spec(self):
        """Test analyze_openapi_spec with nonexistent file."""
        analyzer = APIAnalyzer()
        result = analyzer.analyze_openapi_spec(Path("C:/___NONEXISTENT___/openapi.yaml"))
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_detect_openapi_3_0_version(self):
        """Test OpenAPI 3.0 version detection."""
        spec_data = {"openapi": "3.0.0"}
        analyzer = APIAnalyzer()
        version = analyzer._detect_openapi_version(spec_data)
        assert version == OpenAPIVersion.OPENAPI_3_0
    
    def test_detect_openapi_3_1_version(self):
        """Test OpenAPI 3.1 version detection."""
        spec_data = {"openapi": "3.1.0"}
        analyzer = APIAnalyzer()
        version = analyzer._detect_openapi_version(spec_data)
        assert version == OpenAPIVersion.OPENAPI_3_1
    
    def test_detect_swagger_2_0_version(self):
        """Test Swagger 2.0 version detection."""
        spec_data = {"swagger": "2.0"}
        analyzer = APIAnalyzer()
        version = analyzer._detect_openapi_version(spec_data)
        assert version == OpenAPIVersion.SWAGGER_2_0
    
    def test_detect_unknown_version(self):
        """Test unknown version detection."""
        spec_data = {"version": "1.0"}
        analyzer = APIAnalyzer()
        version = analyzer._detect_openapi_version(spec_data)
        assert version == OpenAPIVersion.UNKNOWN
    
    def test_extract_api_version(self):
        """Test API version extraction."""
        spec_data = {"info": {"version": "1.2.3"}}
        analyzer = APIAnalyzer()
        version = analyzer._extract_api_version(spec_data)
        assert version == "1.2.3"
    
    def test_parse_openapi_3_security_schemes(self):
        """Test parsing OpenAPI 3.x security schemes."""
        spec_data = {
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    },
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            }
        }
        analyzer = APIAnalyzer()
        schemes = analyzer._parse_security_schemes(spec_data, OpenAPIVersion.OPENAPI_3_0)
        
        assert len(schemes) == 2
        bearer_scheme = next(s for s in schemes if s.name == "bearerAuth")
        assert bearer_scheme.scheme_type == SecuritySchemeType.HTTP_BEARER
        assert bearer_scheme.bearer_format == "JWT"
    
    def test_parse_swagger_2_security_definitions(self):
        """Test parsing Swagger 2.0 security definitions."""
        spec_data = {
            "securityDefinitions": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic"
                },
                "apiKey": {
                    "type": "apiKey",
                    "in": "query",
                    "name": "api_key"
                }
            }
        }
        analyzer = APIAnalyzer()
        schemes = analyzer._parse_security_schemes(spec_data, OpenAPIVersion.SWAGGER_2_0)
        
        assert len(schemes) == 2
        basic_scheme = next(s for s in schemes if s.name == "basicAuth")
        assert basic_scheme.scheme_type == SecuritySchemeType.HTTP_BASIC
    
    def test_parse_openapi_3_servers(self):
        """Test parsing OpenAPI 3.x servers."""
        spec_data = {
            "servers": [
                {"url": "https://api.example.com/v1", "description": "Production"},
                {"url": "https://staging-api.example.com/v1", "description": "Staging"}
            ]
        }
        analyzer = APIAnalyzer()
        servers = analyzer._parse_servers(spec_data, OpenAPIVersion.OPENAPI_3_0)
        
        assert len(servers) == 2
        assert servers[0]["url"] == "https://api.example.com/v1"
    
    def test_parse_swagger_2_servers(self):
        """Test parsing Swagger 2.0 host/basePath."""
        spec_data = {
            "host": "api.example.com",
            "basePath": "/v1",
            "schemes": ["https"]
        }
        analyzer = APIAnalyzer()
        servers = analyzer._parse_servers(spec_data, OpenAPIVersion.SWAGGER_2_0)
        
        assert len(servers) == 1
        assert servers[0]["url"] == "https://api.example.com/v1"
    
    def test_parse_endpoints(self):
        """Test parsing API endpoints."""
        spec_data = {
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "parameters": [],
                        "responses": {"200": {"description": "Success"}}
                    },
                    "post": {
                        "summary": "Create user",
                        "requestBody": {"required": True},
                        "responses": {"201": {"description": "Created"}}
                    }
                },
                "/users/{id}": {
                    "get": {
                        "summary": "Get user",
                        "parameters": [{"name": "id", "in": "path"}],
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        analyzer = APIAnalyzer()
        endpoints = analyzer._parse_endpoints(spec_data, OpenAPIVersion.OPENAPI_3_0)
        
        assert len(endpoints) == 3
        get_users = next(e for e in endpoints if e.path == "/users" and e.method == "GET")
        assert get_users.summary == "List users"
    
    def test_check_missing_authentication(self):
        """Test missing authentication detection."""
        endpoints = [
            APIEndpoint(path="/users", method="GET", security=[]),
            APIEndpoint(path="/admin", method="POST", security=[])
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_missing_authentication(endpoints, global_security=[])
        
        assert len(findings) == 2
        assert all(f.priority == APISecurityPriority.P0 for f in findings)
        assert all(f.category == "missing_authentication" for f in findings)
    
    def test_check_weak_authentication_basic(self):
        """Test weak authentication detection (HTTP Basic)."""
        schemes = [
            SecurityScheme(
                name="basicAuth",
                scheme_type=SecuritySchemeType.HTTP_BASIC
            )
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_weak_authentication(schemes)
        
        assert len(findings) == 1
        assert findings[0].priority == APISecurityPriority.P1
        assert "weak" in findings[0].category.lower()
    
    def test_check_weak_authentication_apikey_query(self):
        """Test weak authentication detection (API Key in query)."""
        schemes = [
            SecurityScheme(
                name="apiKey",
                scheme_type=SecuritySchemeType.API_KEY,
                in_location="query"
            )
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_weak_authentication(schemes)
        
        assert len(findings) == 1
        assert findings[0].priority == APISecurityPriority.P1
        assert "query" in findings[0].description.lower()
    
    def test_check_bola_vulnerabilities(self):
        """Test BOLA vulnerability detection."""
        endpoints = [
            APIEndpoint(path="/users/{id}", method="GET"),
            APIEndpoint(path="/accounts/{account_id}", method="PUT"),
            APIEndpoint(path="/orders/{order_id}", method="DELETE"),
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_bola_vulnerabilities(endpoints)
        
        assert len(findings) == 3
        assert all(f.priority == APISecurityPriority.P1 for f in findings)
        assert all(f.category == "broken_object_level_authorization" for f in findings)
        assert all("API1:2023" in f.owasp_api_top_10 for f in findings)
    
    def test_check_excessive_data_exposure(self):
        """Test excessive data exposure detection."""
        endpoints = [
            APIEndpoint(
                path="/users/list",
                method="GET",
                parameters=[]  # No field filtering or pagination
            )
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_excessive_data_exposure(endpoints)
        
        assert len(findings) >= 1
        assert any(f.category == "excessive_data_exposure" for f in findings)
        assert any(f.category == "missing_pagination" for f in findings)
    
    def test_check_missing_rate_limiting(self):
        """Test missing rate limiting detection."""
        spec_data = {}  # No rate limiting config
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_missing_rate_limiting(spec_data)
        
        assert len(findings) == 1
        assert findings[0].priority == APISecurityPriority.P1
        assert findings[0].category == "missing_rate_limiting"
        assert "API4:2023" in findings[0].owasp_api_top_10
    
    def test_check_broken_function_auth(self):
        """Test broken function-level authorization detection."""
        endpoints = [
            APIEndpoint(path="/admin/users", method="DELETE", security=[]),
            APIEndpoint(path="/internal/config", method="PUT", security=[])
        ]
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_broken_function_auth(endpoints)
        
        assert len(findings) == 2
        assert all(f.priority == APISecurityPriority.P0 for f in findings)
        assert all("API5:2023" in f.owasp_api_top_10 for f in findings)
    
    def test_check_insecure_http(self):
        """Test insecure HTTP detection."""
        spec_data = {
            "servers": [
                {"url": "http://api.example.com"}
            ]
        }
        endpoints = []
        
        analyzer = APIAnalyzer()
        findings = analyzer._check_security_misconfigurations(spec_data, endpoints)
        
        assert len(findings) >= 1
        insecure_http = [f for f in findings if f.finding_id == "INSECURE_HTTP"]
        assert len(insecure_http) == 1
        assert insecure_http[0].priority == APISecurityPriority.P0
    
    def test_detect_rate_limiting(self):
        """Test rate limiting detection."""
        spec_data_with_rl = {"x-rate-limit": {"limit": 100}}
        spec_data_without_rl = {}
        
        analyzer = APIAnalyzer()
        assert analyzer._detect_rate_limiting(spec_data_with_rl) is True
        assert analyzer._detect_rate_limiting(spec_data_without_rl) is False
    
    def test_detect_cors_config(self):
        """Test CORS configuration detection."""
        spec_data_with_cors = {"x-cors": {"allow-origin": "*"}}
        spec_data_without_cors = {}
        
        analyzer = APIAnalyzer()
        assert analyzer._detect_cors_config(spec_data_with_cors) is True
        assert analyzer._detect_cors_config(spec_data_without_cors) is False
    
    def test_analyze_openapi_spec_yaml(self, tmp_path):
        """Test analyzing valid OpenAPI YAML spec."""
        spec_content = """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      security:
        - bearerAuth: []
      responses:
        '200':
          description: Success
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
"""
        spec_file = tmp_path / "openapi.yaml"
        spec_file.write_text(spec_content)
        
        analyzer = APIAnalyzer()
        result = analyzer.analyze_openapi_spec(spec_file)
        
        assert result.success
        assert result.spec_version == OpenAPIVersion.OPENAPI_3_0
        assert len(result.endpoints) == 1
        assert len(result.security_schemes) == 1
        assert result.analysis_time_ms > 0
    
    def test_analyze_openapi_spec_json(self, tmp_path):
        """Test analyzing valid OpenAPI JSON spec."""
        spec_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        spec_file = tmp_path / "openapi.json"
        spec_file.write_text(json.dumps(spec_data))
        
        analyzer = APIAnalyzer()
        result = analyzer.analyze_openapi_spec(spec_file)
        
        assert result.success
        assert result.spec_version == OpenAPIVersion.OPENAPI_3_0
        assert len(result.endpoints) == 1
    
    def test_analyze_api_code_nonexistent_path(self):
        """Test analyze_api_code with nonexistent path."""
        analyzer = APIAnalyzer()
        result = analyzer.analyze_api_code(Path("C:/___NONEXISTENT___/api"), framework="fastapi")
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_analyze_api_code_unsupported_framework(self, tmp_path):
        """Test analyze_api_code with unsupported framework."""
        analyzer = APIAnalyzer()
        
        with pytest.raises(ValueError, match="Unsupported framework"):
            analyzer.analyze_api_code(tmp_path, framework="unknown")
    
    def test_discover_fastapi_endpoints(self, tmp_path):
        """Test FastAPI endpoint discovery."""
        code_content = '''
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def list_users():
    return []

@app.post("/users")
async def create_user():
    return {}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {}
'''
        code_file = tmp_path / "main.py"
        code_file.write_text(code_content)
        
        analyzer = APIAnalyzer()
        endpoints = analyzer._discover_fastapi_endpoints(tmp_path)
        
        assert len(endpoints) >= 3
        assert any(e.path == "/users" and e.method == "GET" for e in endpoints)
        assert any(e.path == "/users" and e.method == "POST" for e in endpoints)
    
    def test_discover_flask_endpoints(self, tmp_path):
        """Test Flask endpoint discovery."""
        code_content = '''
from flask import Flask

app = Flask(__name__)

@app.route("/users")
def list_users():
    return []

@app.route("/users/<int:user_id>")
def get_user(user_id):
    return {}
'''
        code_file = tmp_path / "app.py"
        code_file.write_text(code_content)
        
        analyzer = APIAnalyzer()
        endpoints = analyzer._discover_flask_endpoints(tmp_path)
        
        assert len(endpoints) >= 2
        assert any(e.path == "/users" for e in endpoints)
    
    def test_api_analysis_result_default_values(self):
        """Test APIAnalysisResult default values."""
        result = APIAnalysisResult(success=True)
        
        assert result.success
        assert result.spec_version == OpenAPIVersion.UNKNOWN
        assert result.endpoints == []
        assert result.security_findings == []
        assert not result.has_rate_limiting
        assert not result.has_cors_config
        assert result.error == ""


class TestAPIAnalysisResult:
    """Test APIAnalysisResult dataclass."""
    
    def test_full_analysis_result(self):
        """Test APIAnalysisResult with all fields."""
        endpoint = APIEndpoint(path="/test", method="GET")
        scheme = SecurityScheme(name="bearer", scheme_type=SecuritySchemeType.HTTP_BEARER)
        finding = APISecurityFinding(
            finding_id="TEST_001",
            priority=APISecurityPriority.P1,
            category="test"
        )
        
        result = APIAnalysisResult(
            success=True,
            spec_version=OpenAPIVersion.OPENAPI_3_0,
            endpoints=[endpoint],
            security_schemes=[scheme],
            security_findings=[finding],
            has_rate_limiting=True,
            has_cors_config=True,
            api_version="1.0.0",
            analysis_time_ms=123.45
        )
        
        assert result.success
        assert len(result.endpoints) == 1
        assert len(result.security_schemes) == 1
        assert len(result.security_findings) == 1
        assert result.has_rate_limiting
        assert result.api_version == "1.0.0"
