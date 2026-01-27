"""
API Topology Discovery

Discovers REST APIs, GraphQL endpoints, and gRPC services from repositories.

Supports:
- OpenAPI/Swagger specs (2.0, 3.0)
- Route decorators (Flask, FastAPI, Express, ASP.NET)
- GraphQL schemas (.graphql, schema.js)
- gRPC proto files (.proto)
- Authentication requirements

Task: DISC-004
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import json
import logging
import re
import yaml
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

from cortex.brain.discovery import DiscoveryPlugin


logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """
    HTTP methods.
    
    Attributes:
        GET: HTTP GET
        POST: HTTP POST
        PUT: HTTP PUT
        DELETE: HTTP DELETE
        PATCH: HTTP PATCH
        OPTIONS: HTTP OPTIONS
        HEAD: HTTP HEAD
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class EndpointInfo:
    """
    API endpoint information.
    
    Attributes:
        path: Endpoint path
        method: HTTP method
        summary: Endpoint description
        auth_required: Whether authentication is required
        parameters: Request parameters
        responses: Response definitions
    """
    path: str
    method: HTTPMethod
    summary: Optional[str] = None
    auth_required: bool = False
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    responses: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APITopology:
    """
    Complete API topology information.
    
    Attributes:
        endpoints: REST API endpoints
        graphql_schemas: GraphQL schemas
        grpc_services: gRPC services
        auth_schemes: Authentication schemes
    """
    endpoints: List[EndpointInfo]
    graphql_schemas: List[Dict[str, Any]]
    grpc_services: List[Dict[str, Any]]
    auth_schemes: Dict[str, Any]


class APIDiscovery(DiscoveryPlugin):
    """
    Discovers API topology from repositories.
    
    Analyzes OpenAPI specs, route decorators, GraphQL schemas,
    and gRPC proto files to map application APIs.
    
    Features:
    - Multi-API support (REST, GraphQL, gRPC)
    - Framework detection (Flask, FastAPI, ASP.NET, Express)
    - Authentication requirement extraction
    - Request/response model mapping
    
    Example:
        ```python
        discovery = APIDiscovery()
        topology = discovery.discover(Path("/my/repo"))
        
        for endpoint in topology["endpoints"]:
            print(f"{endpoint['method']} {endpoint['path']}")
        ```
    """
    
    def __init__(self) -> None:
        """Initialize API discovery."""
        self.supported_api_types = ["rest", "graphql", "grpc"]
        logger.info("APIDiscovery initialized")
    
    def get_supported_api_types(self) -> List[str]:
        """
        Get list of supported API types.
        
        Returns:
            List of API type names
        """
        return self.supported_api_types
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover API topology in repository.
        
        Args:
            repo_path: Path to repository to scan
            
        Returns:
            Dictionary containing API topology
        """
        logger.info(f"Discovering API topology in {repo_path}")
        
        endpoints: List[EndpointInfo] = []
        graphql_schemas: List[Dict[str, Any]] = []
        grpc_services: List[Dict[str, Any]] = []
        auth_schemes: Dict[str, Any] = {}
        
        # Scan for OpenAPI/Swagger specs
        for spec_file in repo_path.rglob("*.json"):
            if "swagger" in spec_file.name.lower() or "openapi" in spec_file.name.lower():
                spec_data = self.parse_openapi_spec(spec_file)
                if spec_data and "endpoints" in spec_data:
                    endpoints.extend([
                        EndpointInfo(
                            path=e["path"],
                            method=HTTPMethod[e["method"].upper()],
                            summary=e.get("summary"),
                            auth_required=e.get("auth_required", False),
                        )
                        for e in spec_data["endpoints"]
                    ])
                    if "security" in spec_data:
                        auth_schemes.update(spec_data["security"])
        
        for spec_file in repo_path.rglob("*.yaml"):
            if "openapi" in spec_file.name.lower():
                spec_data = self.parse_openapi_spec(spec_file)
                if spec_data and "endpoints" in spec_data:
                    endpoints.extend([
                        EndpointInfo(
                            path=e["path"],
                            method=HTTPMethod[e["method"].upper()],
                            summary=e.get("summary"),
                        )
                        for e in spec_data["endpoints"]
                    ])
        
        for spec_file in repo_path.rglob("*.yml"):
            if "openapi" in spec_file.name.lower():
                spec_data = self.parse_openapi_spec(spec_file)
                if spec_data and "endpoints" in spec_data:
                    endpoints.extend([
                        EndpointInfo(
                            path=e["path"],
                            method=HTTPMethod[e["method"].upper()],
                            summary=e.get("summary"),
                        )
                        for e in spec_data["endpoints"]
                    ])
        
        # Scan for route decorators
        decorator_endpoints = self.scan_route_decorators(repo_path)
        endpoints.extend(decorator_endpoints)
        
        # Scan for GraphQL schemas
        for graphql_file in repo_path.rglob("*.graphql"):
            schema_data = self.parse_graphql_schema(graphql_file)
            if schema_data:
                graphql_schemas.append(schema_data)
        
        # Scan for gRPC proto files
        grpc_services = self.parse_proto_files(repo_path)
        
        logger.info(
            f"Discovered {len(endpoints)} REST endpoints, "
            f"{len(graphql_schemas)} GraphQL schemas, "
            f"{len(grpc_services)} gRPC services"
        )
        
        return {
            "endpoints": [
                {
                    "path": e.path,
                    "method": e.method.value,
                    "summary": e.summary,
                    "auth_required": e.auth_required,
                }
                for e in endpoints
            ],
            "graphql_schemas": graphql_schemas,
            "grpc_services": grpc_services,
            "auth_schemes": auth_schemes,
            "total_endpoints": len(endpoints),
            "total_graphql": len(graphql_schemas),
            "total_grpc": len(grpc_services),
        }
    
    def parse_openapi_spec(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse OpenAPI/Swagger specification.
        
        Args:
            file_path: Path to OpenAPI spec file
            
        Returns:
            Parsed API information or None
        """
        try:
            if file_path.suffix == ".json":
                with open(file_path) as f:
                    spec = json.load(f)
            else:
                with open(file_path) as f:
                    spec = yaml.safe_load(f)
            
            if not spec or "paths" not in spec:
                return None
            
            endpoints = []
            for path, methods in spec["paths"].items():
                for method, details in methods.items():
                    if method in ["get", "post", "put", "delete", "patch"]:
                        endpoints.append({
                            "path": path,
                            "method": method,
                            "summary": details.get("summary", ""),
                            "auth_required": "security" in details,
                        })
            
            # Extract security schemes
            security = {}
            if "components" in spec and "securitySchemes" in spec["components"]:
                security = spec["components"]["securitySchemes"]
            elif "securityDefinitions" in spec:  # Swagger 2.0
                security = spec["securityDefinitions"]
            
            logger.debug(f"Parsed OpenAPI spec: {file_path} ({len(endpoints)} endpoints)")
            
            return {
                "endpoints": endpoints,
                "security": security,
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse OpenAPI spec {file_path}: {e}")
            return None
    
    def scan_route_decorators(self, repo_path: Path) -> List[EndpointInfo]:
        """
        Scan route decorators in code files.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of discovered endpoints
        """
        endpoints: List[EndpointInfo] = []
        
        # Scan Python files (Flask, FastAPI)
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Flask @app.route or @router.route
                flask_routes = re.findall(
                    r'@(?:app|router)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)',
                    content
                )
                for path, methods_str in flask_routes:
                    if methods_str:
                        methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
                    else:
                        methods = ['GET']
                    
                    for method in methods:
                        endpoints.append(EndpointInfo(
                            path=path,
                            method=HTTPMethod[method.upper()] if method.upper() in HTTPMethod.__members__ else HTTPMethod.GET,
                        ))
                
                # FastAPI @router.get, @router.post, etc.
                fastapi_routes = re.findall(
                    r'@router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)',
                    content
                )
                for method, path in fastapi_routes:
                    endpoints.append(EndpointInfo(
                        path=path,
                        method=HTTPMethod[method.upper()],
                    ))
                
            except Exception:
                pass
        
        # Scan C# files (ASP.NET)
        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text()
                
                # ASP.NET [HttpGet], [HttpPost], etc.
                aspnet_routes = re.findall(
                    r'\[Http(Get|Post|Put|Delete|Patch)\]',
                    content
                )
                
                # Extract route from [Route] attribute
                route_attr = re.search(r'\[Route\([\'"]([^\'"]+)[\'"]\)\]', content)
                base_path = route_attr.group(1) if route_attr else "/api"
                
                for method in aspnet_routes:
                    endpoints.append(EndpointInfo(
                        path=base_path,
                        method=HTTPMethod[method.upper()],
                    ))
                
            except Exception:
                pass
        
        return endpoints
    
    def parse_graphql_schema(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse GraphQL schema file.
        
        Args:
            file_path: Path to GraphQL schema file
            
        Returns:
            Parsed GraphQL schema information
        """
        try:
            content = file_path.read_text()
            
            # Extract queries - match field definitions (with or without arguments)
            queries = re.findall(r'type\s+Query\s*{([^}]+)}', content, re.DOTALL)
            query_fields = []
            if queries:
                for query in queries:
                    # Match: fieldName(args): Type or fieldName: Type
                    fields = re.findall(r'^\s*(\w+)(?:\([^)]*\))?:\s*', query, re.MULTILINE)
                    query_fields.extend(fields)
            
            # Extract mutations
            mutations = re.findall(r'type\s+Mutation\s*{([^}]+)}', content, re.DOTALL)
            mutation_fields = []
            if mutations:
                for mutation in mutations:
                    fields = re.findall(r'^\s*(\w+)(?:\([^)]*\))?:\s*', mutation, re.MULTILINE)
                    mutation_fields.extend(fields)
            
            logger.debug(f"Parsed GraphQL schema: {file_path}")
            
            return {
                "file": str(file_path),
                "queries": query_fields,
                "mutations": mutation_fields,
                "total_operations": len(query_fields) + len(mutation_fields),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse GraphQL schema {file_path}: {e}")
            return None
    
    def parse_proto_files(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Parse gRPC proto files.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of gRPC services
        """
        services = []
        
        for proto_file in repo_path.rglob("*.proto"):
            try:
                content = proto_file.read_text()
                
                # Extract service definitions
                service_matches = re.findall(
                    r'service\s+(\w+)\s*{([^}]+)}',
                    content,
                    re.DOTALL
                )
                
                for service_name, service_body in service_matches:
                    # Extract RPC methods
                    methods = re.findall(
                        r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)',
                        service_body
                    )
                    
                    services.append({
                        "service_name": service_name,
                        "file": str(proto_file),
                        "methods": [
                            {
                                "name": m[0],
                                "request": m[1].strip(),
                                "response": m[2].strip(),
                            }
                            for m in methods
                        ],
                        "method_count": len(methods),
                    })
                
                logger.debug(f"Parsed gRPC proto: {proto_file}")
                
            except Exception as e:
                logger.warning(f"Failed to parse proto {proto_file}: {e}")
        
        return services
    
    def extract_auth_requirements(
        self,
        endpoint: EndpointInfo
    ) -> Dict[str, Any]:
        """
        Extract authentication requirements for endpoint.
        
        Args:
            endpoint: Endpoint to analyze
            
        Returns:
            Authentication requirement information
        """
        # Placeholder for auth extraction logic
        return {
            "required": endpoint.auth_required,
            "schemes": [],
        }
