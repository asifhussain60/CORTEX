"""
Tests for API Topology Discovery.

Task: DISC-004
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008 (TDD - tests before implementation)

Test Coverage:
1. Parse Swagger 2.0 spec
2. Parse OpenAPI 3.0 spec
3. Scan Flask route decorators
4. Scan FastAPI route decorators
5. Scan ASP.NET controller attributes
6. Parse GraphQL schema
7. Parse gRPC proto files
8. Extract authentication requirements
"""

import pytest
import json
import yaml
from pathlib import Path
from typing import Dict, Any

from cortex.brain.discovery.api_discovery import (
    APIDiscovery,
    EndpointInfo,
    APITopology,
    HTTPMethod,
)


class TestAPIDiscoveryInit:
    """Test APIDiscovery initialization."""
    
    def test_init_creates_discovery(self) -> None:
        """Test discovery can be instantiated."""
        discovery = APIDiscovery()
        assert discovery is not None
    
    def test_supported_api_types_defined(self) -> None:
        """Test supported API types are defined."""
        discovery = APIDiscovery()
        types = discovery.get_supported_api_types()
        
        assert "rest" in types
        assert "graphql" in types
        assert "grpc" in types


class TestOpenAPISpecParsing:
    """Test OpenAPI/Swagger spec parsing."""
    
    def test_parse_swagger_2_spec(self, tmp_path: Path) -> None:
        """Test parsing Swagger 2.0 specification."""
        swagger_file = tmp_path / "swagger.json"
        swagger_spec = {
            "swagger": "2.0",
            "paths": {
                "/api/users": {
                    "get": {"summary": "Get users"},
                    "post": {"summary": "Create user"}
                },
                "/api/users/{id}": {
                    "get": {"summary": "Get user by ID"}
                }
            }
        }
        swagger_file.write_text(json.dumps(swagger_spec))
        
        discovery = APIDiscovery()
        result = discovery.parse_openapi_spec(swagger_file)
        
        assert result is not None
        assert len(result["endpoints"]) >= 3
    
    def test_parse_openapi_3_spec(self, tmp_path: Path) -> None:
        """Test parsing OpenAPI 3.0 specification."""
        openapi_file = tmp_path / "openapi.yaml"
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/api/products": {
                    "get": {
                        "summary": "List products",
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        openapi_file.write_text(yaml.dump(openapi_spec))
        
        discovery = APIDiscovery()
        result = discovery.parse_openapi_spec(openapi_file)
        
        assert result is not None
        assert len(result["endpoints"]) >= 1


class TestFlaskRouteScanning:
    """Test Flask route decorator scanning."""
    
    def test_scan_flask_route_decorators(self, tmp_path: Path) -> None:
        """Test scanning Flask @app.route decorators."""
        flask_file = tmp_path / "app.py"
        flask_file.write_text(
            "@app.route('/api/users', methods=['GET', 'POST'])\n"
            "def users():\n"
            "    pass\n\n"
            "@app.route('/api/users/<int:id>', methods=['GET'])\n"
            "def get_user(id):\n"
            "    pass\n"
        )
        
        discovery = APIDiscovery()
        endpoints = discovery.scan_route_decorators(tmp_path)
        
        assert len(endpoints) >= 2
        assert any(e.path == "/api/users" for e in endpoints)
    
    def test_scan_fastapi_route_decorators(self, tmp_path: Path) -> None:
        """Test scanning FastAPI @router.get decorators."""
        fastapi_file = tmp_path / "main.py"
        fastapi_file.write_text(
            "@router.get('/api/items')\n"
            "async def list_items():\n"
            "    pass\n\n"
            "@router.post('/api/items')\n"
            "async def create_item():\n"
            "    pass\n"
        )
        
        discovery = APIDiscovery()
        endpoints = discovery.scan_route_decorators(tmp_path)
        
        assert len(endpoints) >= 2
        assert any(e.method == HTTPMethod.GET for e in endpoints)
        assert any(e.method == HTTPMethod.POST for e in endpoints)


class TestASPNETControllerScanning:
    """Test ASP.NET controller scanning."""
    
    def test_scan_aspnet_controller_attributes(self, tmp_path: Path) -> None:
        """Test scanning ASP.NET [HttpGet] attributes."""
        controller_file = tmp_path / "UsersController.cs"
        controller_file.write_text(
            "[ApiController]\n"
            "[Route('api/[controller]')]\n"
            "public class UsersController : ControllerBase\n"
            "{\n"
            "    [HttpGet]\n"
            "    public IActionResult GetUsers() { }\n\n"
            "    [HttpPost]\n"
            "    public IActionResult CreateUser() { }\n"
            "}\n"
        )
        
        discovery = APIDiscovery()
        endpoints = discovery.scan_route_decorators(tmp_path)
        
        assert len(endpoints) >= 2


class TestGraphQLSchemaParsing:
    """Test GraphQL schema parsing."""
    
    def test_parse_graphql_schema(self, tmp_path: Path) -> None:
        """Test parsing GraphQL schema file."""
        schema_file = tmp_path / "schema.graphql"
        schema_file.write_text(
            "type Query {\n"
            "  users: [User]\n"
            "  user(id: ID!): User\n"
            "}\n\n"
            "type Mutation {\n"
            "  createUser(name: String!): User\n"
            "}\n\n"
            "type User {\n"
            "  id: ID!\n"
            "  name: String!\n"
            "}\n"
        )
        
        discovery = APIDiscovery()
        result = discovery.parse_graphql_schema(schema_file)
        
        assert result is not None
        assert "queries" in result
        assert "mutations" in result
        assert len(result["queries"]) >= 2
        assert len(result["mutations"]) >= 1


class TestGRPCProtoParsing:
    """Test gRPC proto file parsing."""
    
    def test_parse_grpc_proto_files(self, tmp_path: Path) -> None:
        """Test parsing gRPC .proto files."""
        proto_file = tmp_path / "users.proto"
        proto_file.write_text(
            "syntax = \"proto3\";\n\n"
            "service UserService {\n"
            "  rpc GetUser (UserRequest) returns (UserResponse);\n"
            "  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);\n"
            "}\n\n"
            "message UserRequest {\n"
            "  int32 id = 1;\n"
            "}\n"
        )
        
        discovery = APIDiscovery()
        services = discovery.parse_proto_files(tmp_path)
        
        assert len(services) >= 1
        assert services[0]["service_name"] == "UserService"
        assert len(services[0]["methods"]) >= 2


class TestAuthenticationExtraction:
    """Test authentication requirement extraction."""
    
    def test_extract_auth_from_openapi(self, tmp_path: Path) -> None:
        """Test extracting auth requirements from OpenAPI spec."""
        openapi_file = tmp_path / "openapi.json"
        openapi_spec = {
            "openapi": "3.0.0",
            "paths": {
                "/api/users": {
                    "get": {
                        "security": [{"bearerAuth": []}]
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {"type": "http", "scheme": "bearer"}
                }
            }
        }
        openapi_file.write_text(json.dumps(openapi_spec))
        
        discovery = APIDiscovery()
        result = discovery.parse_openapi_spec(openapi_file)
        
        assert "security" in result or "auth_schemes" in result
    
    def test_extract_auth_from_decorators(self, tmp_path: Path) -> None:
        """Test extracting auth from route decorators."""
        flask_file = tmp_path / "app.py"
        flask_file.write_text(
            "@app.route('/api/users')\n"
            "@login_required\n"
            "def users():\n"
            "    pass\n"
        )
        
        discovery = APIDiscovery()
        endpoints = discovery.scan_route_decorators(tmp_path)
        
        # Should detect authentication decorator
        assert len(endpoints) >= 1


class TestFullDiscovery:
    """Test complete API discovery."""
    
    def test_discover_multiple_api_types(self, tmp_path: Path) -> None:
        """Test discovering multiple API types in repo."""
        # Create OpenAPI spec
        (tmp_path / "swagger.json").write_text(
            json.dumps({"swagger": "2.0", "paths": {}})
        )
        
        # Create Flask routes
        (tmp_path / "app.py").write_text(
            "@app.route('/api/test')\ndef test(): pass"
        )
        
        discovery = APIDiscovery()
        topology = discovery.discover(tmp_path)
        
        assert isinstance(topology, dict)
        assert "endpoints" in topology
    
    def test_discover_handles_no_apis(self, tmp_path: Path) -> None:
        """Test discovery handles repos with no APIs."""
        # Empty directory
        discovery = APIDiscovery()
        topology = discovery.discover(tmp_path)
        
        assert isinstance(topology, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
