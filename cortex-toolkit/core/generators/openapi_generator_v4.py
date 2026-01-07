#!/usr/bin/env python3
"""
CORTEX Toolkit - OpenAPI Generator v4
Enhanced OpenAPI specification generator with complete schema integration.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 4.0.0
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .schema_extractor import SchemaExtractor
from .schema_registry import SchemaRegistry


class OpenAPIGeneratorV4:
    """
    Enhanced OpenAPI 3.0 specification generator.
    
    Improvements over v3:
    - Complete schema extraction from C# entities
    - Request/response body schemas (not just placeholders)
    - Security scheme templates
    - Comprehensive error responses
    - Realistic examples
    - Enterprise overlays (health checks, correlation IDs)
    """
    
    def __init__(
        self,
        legacy_file: Path,
        output_dir: Path,
        security_template: str = "oauth2-client-credentials",
        include_health_endpoints: bool = True
    ):
        """
        Initialize OpenAPI generator v4.
        
        Args:
            legacy_file: Path to legacy C# file
            output_dir: Output directory
            security_template: Security scheme template name
            include_health_endpoints: Add /health and /ready endpoints
        """
        self.legacy_file = Path(legacy_file)
        self.output_dir = Path(output_dir)
        self.security_template = security_template
        self.include_health_endpoints = include_health_endpoints
        
        # Initialize extractors
        self.schema_extractor = SchemaExtractor(
            source_file=self.legacy_file,
            output_dir=self.output_dir / "schemas",
            format="json"
        )
        
        self.registry = SchemaRegistry(
            registry_path=self.output_dir / "schema-registry.json"
        )
        
        self.spec: Dict[str, Any] = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI specification.
        
        Returns:
            Complete OpenAPI 3.0 specification
        """
        # Step 1: Extract schemas
        schemas = self.schema_extractor.extract()
        
        # Step 2: Register schemas
        for schema_name, schema_def in schemas.items():
            self.registry.register(
                schema_name=schema_name,
                schema_definition=schema_def,
                source_file=str(self.legacy_file),
                namespace=self.schema_extractor.classes[0].namespace if self.schema_extractor.classes else "Unknown"
            )
        
        # Step 3: Build OpenAPI spec
        self.spec = self._build_spec()
        
        # Step 4: Add security
        self._add_security()
        
        # Step 5: Add enterprise features
        if self.include_health_endpoints:
            self._add_health_endpoints()
        
        # Step 6: Write outputs
        self._write_spec()
        
        # Step 7: Save registry
        self.registry.save()
        
        return self.spec
    
    def _build_spec(self) -> Dict[str, Any]:
        """Build base OpenAPI specification"""
        api_name = self.legacy_file.stem
        
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": f"{api_name} API",
                "description": f"Production-ready API specification for {api_name}",
                "version": "1.0.0",
                "contact": {
                    "name": "CORTEX Lens v4",
                    "url": "https://github.com/asifhussain60/CORTEX"
                },
                "x-legacy-source": {
                    "file": str(self.legacy_file),
                    "generated": datetime.now().isoformat(),
                    "generator": "CORTEX Toolkit OpenAPI Generator v4.0"
                }
            },
            "servers": [
                {
                    "url": "https://api.{environment}.example.com/v1",
                    "description": "API server (replace {environment} with dev/staging/prod)",
                    "variables": {
                        "environment": {
                            "default": "dev",
                            "enum": ["dev", "staging", "prod"]
                        }
                    }
                }
            ],
            "paths": {},
            "components": {
                "schemas": self.registry.get_all_schemas(),
                "responses": self._build_standard_responses(),
                "parameters": self._build_standard_parameters()
            },
            "tags": [
                {"name": "RA Operations", "description": "Reimbursement Account operations"}
            ]
        }
        
        # Add operation paths
        spec["paths"] = self._build_paths(api_name)
        
        return spec
    
    def _build_paths(self, api_name: str) -> Dict[str, Any]:
        """Build API paths/operations"""
        paths = {}
        
        # Infer HTTP method from API name
        method, path = self._infer_operation(api_name)
        
        # Get schemas for request/response
        schemas = self.registry.get_all_schemas()
        request_schema = None
        response_schema = None
        
        # Try to find appropriate schemas
        for schema_name in schemas:
            if "Request" in schema_name or "Input" in schema_name:
                request_schema = schema_name
            if "Response" in schema_name or "Result" in schema_name:
                response_schema = schema_name
        
        # If not found, use first schema as response
        if not response_schema and schemas:
            response_schema = list(schemas.keys())[0]
        
        # Build operation
        operation = {
            "operationId": api_name,
            "summary": f"{api_name.replace('_', ' ').title()} operation",
            "tags": ["RA Operations"],
            "parameters": [
                {"$ref": "#/components/parameters/CorrelationId"}
            ],
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "headers": {
                        "X-Correlation-ID": {
                            "schema": {"type": "string"},
                            "description": "Correlation ID for request tracing"
                        }
                    },
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{response_schema}"
                            } if response_schema else {"type": "object"}
                        }
                    }
                },
                "400": {"$ref": "#/components/responses/BadRequest"},
                "401": {"$ref": "#/components/responses/Unauthorized"},
                "403": {"$ref": "#/components/responses/Forbidden"},
                "404": {"$ref": "#/components/responses/NotFound"},
                "500": {"$ref": "#/components/responses/InternalServerError"}
            }
        }
        
        # Add request body for POST/PUT/PATCH
        if method in ["post", "put", "patch"]:
            operation["parameters"].append(
                {"$ref": "#/components/parameters/IdempotencyKey"}
            )
            
            if request_schema:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{request_schema}"
                            }
                        }
                    }
                }
        
        # Add security requirement
        operation["security"] = [{"oauth2": ["ra:funding:write" if method in ["post", "put", "patch", "delete"] else "ra:funding:read"]}]
        
        paths[path] = {method: operation}
        
        return paths
    
    def _infer_operation(self, api_name: str) -> tuple[str, str]:
        """Infer HTTP method and path from API name"""
        name_lower = api_name.lower()
        
        if "create" in name_lower or "generate" in name_lower:
            return "post", f"/api/ra/{api_name.lower().replace('_', '-')}"
        elif "update" in name_lower or "modify" in name_lower:
            return "put", f"/api/ra/{api_name.lower().replace('_', '-')}"
        elif "delete" in name_lower or "remove" in name_lower:
            return "delete", f"/api/ra/{api_name.lower().replace('_', '-')}"
        elif "get" in name_lower or "find" in name_lower or "query" in name_lower:
            return "get", f"/api/ra/{api_name.lower().replace('_', '-')}"
        else:
            # Default to POST for unknown operations
            return "post", f"/api/ra/{api_name.lower().replace('_', '-')}"
    
    def _build_standard_responses(self) -> Dict[str, Any]:
        """Build standard error response definitions"""
        return {
            "BadRequest": {
                "description": "Invalid request parameters or validation failure",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "error": "VALIDATION_ERROR",
                            "message": "Invalid request parameters",
                            "field": "amount",
                            "timestamp": "2025-12-16T10:30:00Z",
                            "traceId": "550e8400-e29b-41d4-a716-446655440000"
                        }
                    }
                }
            },
            "Unauthorized": {
                "description": "Missing or invalid authentication credentials",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "error": "UNAUTHORIZED",
                            "message": "Invalid or expired access token",
                            "timestamp": "2025-12-16T10:30:00Z",
                            "traceId": "550e8400-e29b-41d4-a716-446655440001"
                        }
                    }
                }
            },
            "Forbidden": {
                "description": "Insufficient permissions to access resource",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "error": "FORBIDDEN",
                            "message": "Insufficient permissions for this operation",
                            "timestamp": "2025-12-16T10:30:00Z",
                            "traceId": "550e8400-e29b-41d4-a716-446655440002"
                        }
                    }
                }
            },
            "NotFound": {
                "description": "Requested resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "error": "NOT_FOUND",
                            "message": "Resource not found",
                            "timestamp": "2025-12-16T10:30:00Z",
                            "traceId": "550e8400-e29b-41d4-a716-446655440003"
                        }
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                        "example": {
                            "error": "INTERNAL_ERROR",
                            "message": "An unexpected error occurred",
                            "timestamp": "2025-12-16T10:30:00Z",
                            "traceId": "550e8400-e29b-41d4-a716-446655440004"
                        }
                    }
                }
            }
        }
    
    def _build_standard_parameters(self) -> Dict[str, Any]:
        """Build standard parameter definitions"""
        return {
            "CorrelationId": {
                "name": "X-Correlation-ID",
                "in": "header",
                "required": False,
                "schema": {"type": "string", "format": "uuid"},
                "description": "Client-provided correlation ID for request tracing"
            },
            "IdempotencyKey": {
                "name": "Idempotency-Key",
                "in": "header",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
                "description": "Unique key to prevent duplicate processing (required for POST/PUT/PATCH)"
            }
        }
    
    def _add_security(self):
        """Add security schemes to specification"""
        # Add ErrorResponse schema if not present
        if "ErrorResponse" not in self.spec["components"]["schemas"]:
            self.spec["components"]["schemas"]["ErrorResponse"] = {
                "type": "object",
                "required": ["error", "message", "timestamp", "traceId"],
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error code (e.g., VALIDATION_ERROR, NOT_FOUND)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Human-readable error message"
                    },
                    "field": {
                        "type": "string",
                        "description": "Field that caused error (for validation errors)"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Error timestamp"
                    },
                    "traceId": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Correlation ID for troubleshooting"
                    }
                }
            }
        
        # Add security schemes
        self.spec["components"]["securitySchemes"] = {
            "oauth2": {
                "type": "oauth2",
                "description": "OAuth2 client credentials flow for machine-to-machine authentication",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": "https://auth.{environment}.example.com/oauth/token",
                        "scopes": {
                            "ra:funding:read": "Read funding data",
                            "ra:funding:write": "Create/update funding data",
                            "ra:funding:admin": "Administrative operations"
                        }
                    }
                }
            }
        }
    
    def _add_health_endpoints(self):
        """Add health check and readiness endpoints"""
        self.spec["paths"]["/health"] = {
            "get": {
                "operationId": "healthCheck",
                "summary": "Service health check",
                "tags": ["System"],
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "enum": ["healthy", "degraded", "unhealthy"]
                                        },
                                        "timestamp": {
                                            "type": "string",
                                            "format": "date-time"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        self.spec["paths"]["/ready"] = {
            "get": {
                "operationId": "readinessCheck",
                "summary": "Service readiness check",
                "tags": ["System"],
                "responses": {
                    "200": {
                        "description": "Service is ready to accept requests"
                    },
                    "503": {
                        "description": "Service is not ready"
                    }
                }
            }
        }
        
        # Add System tag
        if "System" not in [tag["name"] for tag in self.spec.get("tags", [])]:
            self.spec.setdefault("tags", []).append({
                "name": "System",
                "description": "System health and monitoring endpoints"
            })
    
    def _write_spec(self):
        """Write OpenAPI specification to files"""
        # Write YAML
        yaml_file = self.output_dir / "openapi.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.spec, f, default_flow_style=False, sort_keys=False)
        
        # Write JSON
        json_file = self.output_dir / "openapi.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.spec, f, indent=2)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate production-ready OpenAPI specifications (v4)"
    )
    parser.add_argument(
        "legacy_file",
        help="Path to legacy C# file"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for specification"
    )
    parser.add_argument(
        "--security",
        default="oauth2-client-credentials",
        help="Security template (default: oauth2-client-credentials)"
    )
    parser.add_argument(
        "--no-health-endpoints",
        action="store_true",
        help="Exclude health check endpoints"
    )
    
    args = parser.parse_args()
    
    generator = OpenAPIGeneratorV4(
        legacy_file=Path(args.legacy_file),
        output_dir=Path(args.output_dir),
        security_template=args.security,
        include_health_endpoints=not args.no_health_endpoints
    )
    
    try:
        spec = generator.generate()
        schemas_count = len(spec["components"]["schemas"])
        paths_count = len(spec["paths"])
        
        print(f"✅ Generated OpenAPI v4 specification")
        print(f"   Schemas: {schemas_count}")
        print(f"   Paths: {paths_count}")
        print(f"   Security: {args.security}")
        print(f"\n📁 Output: {generator.output_dir}")
        print(f"   - openapi.yaml")
        print(f"   - openapi.json")
        print(f"   - schemas/ ({schemas_count} files)")
        print(f"   - schema-registry.json")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
