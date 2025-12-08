"""
Swagger/OpenAPI Parser for Complexity Estimation

Parses Swagger 2.0 and OpenAPI 3.0 files to extract API complexity metrics
for integration with Planning System 2.0 estimation.

Author: CORTEX Development Team
Version: 1.0.0
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class APIComplexity(Enum):
    """API complexity levels based on endpoint analysis."""
    TRIVIAL = 1      # 1-5 endpoints, simple CRUD
    LOW = 2          # 6-15 endpoints, standard REST
    MEDIUM = 3       # 16-30 endpoints, multiple resources
    HIGH = 5         # 31-50 endpoints, complex integrations
    VERY_HIGH = 8    # 50+ endpoints, microservices


@dataclass
class APIMetrics:
    """Extracted API metrics from Swagger/OpenAPI spec."""
    total_endpoints: int
    get_operations: int
    post_operations: int
    put_operations: int
    patch_operations: int
    delete_operations: int
    unique_resources: int
    has_authentication: bool
    has_pagination: bool
    has_filtering: bool
    has_file_uploads: bool
    request_body_schemas: int
    response_schemas: int
    complexity_score: float
    complexity_level: APIComplexity


class SwaggerParser:
    """Parse Swagger/OpenAPI specifications for complexity estimation."""
    
    def __init__(self):
        self.spec_version = None
        self.spec_data = None
    
    def parse_file(self, file_path: str) -> Optional[APIMetrics]:
        """
        Parse Swagger/OpenAPI file and extract metrics.
        
        Args:
            file_path: Path to swagger.json, swagger.yaml, or openapi.yaml
            
        Returns:
            APIMetrics or None if parsing fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            # Load file
            if path.suffix in ['.yaml', '.yml']:
                with open(path, 'r') as f:
                    self.spec_data = yaml.safe_load(f)
            elif path.suffix == '.json':
                with open(path, 'r') as f:
                    self.spec_data = json.load(f)
            else:
                return None
            
            # Detect version
            if 'swagger' in self.spec_data:
                self.spec_version = 'swagger2'
                return self._parse_swagger2()
            elif 'openapi' in self.spec_data:
                self.spec_version = 'openapi3'
                return self._parse_openapi3()
            else:
                return None
                
        except Exception as e:
            print(f"Error parsing Swagger/OpenAPI file: {e}")
            return None
    
    def _parse_swagger2(self) -> APIMetrics:
        """Parse Swagger 2.0 specification."""
        paths = self.spec_data.get('paths', {})
        
        # Count operations
        total_endpoints = 0
        operations = {'get': 0, 'post': 0, 'put': 0, 'patch': 0, 'delete': 0}
        unique_resources = set()
        request_schemas = set()
        response_schemas = set()
        
        has_auth = 'securityDefinitions' in self.spec_data
        has_pagination = False
        has_filtering = False
        has_uploads = False
        
        for path, methods in paths.items():
            # Extract resource name
            resource = path.split('/')[1] if '/' in path else path
            unique_resources.add(resource)
            
            for method, details in methods.items():
                if method.lower() in operations:
                    operations[method.lower()] += 1
                    total_endpoints += 1
                    
                    # Check for pagination
                    params = details.get('parameters', [])
                    if any(p.get('name') in ['page', 'limit', 'offset'] for p in params):
                        has_pagination = True
                    
                    # Check for filtering
                    if any(p.get('name') in ['filter', 'query', 'search'] for p in params):
                        has_filtering = True
                    
                    # Check for file uploads
                    if any(p.get('type') == 'file' for p in params):
                        has_uploads = True
                    
                    # Count schemas
                    if 'parameters' in details:
                        for param in details['parameters']:
                            if 'schema' in param:
                                schema_ref = param['schema'].get('$ref', '')
                                if schema_ref:
                                    request_schemas.add(schema_ref)
                    
                    if 'responses' in details:
                        for response in details['responses'].values():
                            if 'schema' in response:
                                schema_ref = response['schema'].get('$ref', '')
                                if schema_ref:
                                    response_schemas.add(schema_ref)
        
        # Calculate complexity
        complexity_score = self._calculate_complexity_score(
            total_endpoints, len(unique_resources), has_auth, has_pagination
        )
        
        complexity_level = self._determine_complexity_level(total_endpoints)
        
        return APIMetrics(
            total_endpoints=total_endpoints,
            get_operations=operations['get'],
            post_operations=operations['post'],
            put_operations=operations['put'],
            patch_operations=operations['patch'],
            delete_operations=operations['delete'],
            unique_resources=len(unique_resources),
            has_authentication=has_auth,
            has_pagination=has_pagination,
            has_filtering=has_filtering,
            has_file_uploads=has_uploads,
            request_body_schemas=len(request_schemas),
            response_schemas=len(response_schemas),
            complexity_score=complexity_score,
            complexity_level=complexity_level
        )
    
    def _parse_openapi3(self) -> APIMetrics:
        """Parse OpenAPI 3.0 specification."""
        paths = self.spec_data.get('paths', {})
        components = self.spec_data.get('components', {})
        
        # Count operations
        total_endpoints = 0
        operations = {'get': 0, 'post': 0, 'put': 0, 'patch': 0, 'delete': 0}
        unique_resources = set()
        request_schemas = set()
        response_schemas = set()
        
        has_auth = 'securitySchemes' in components
        has_pagination = False
        has_filtering = False
        has_uploads = False
        
        for path, methods in paths.items():
            # Extract resource name
            resource = path.split('/')[1] if '/' in path else path
            unique_resources.add(resource)
            
            for method, details in methods.items():
                if method.lower() in operations:
                    operations[method.lower()] += 1
                    total_endpoints += 1
                    
                    # Check for pagination
                    params = details.get('parameters', [])
                    if any(p.get('name') in ['page', 'limit', 'offset'] for p in params):
                        has_pagination = True
                    
                    # Check for filtering
                    if any(p.get('name') in ['filter', 'query', 'search'] for p in params):
                        has_filtering = True
                    
                    # Check for file uploads
                    if 'requestBody' in details:
                        content = details['requestBody'].get('content', {})
                        if 'multipart/form-data' in content:
                            has_uploads = True
                    
                    # Count request schemas
                    if 'requestBody' in details:
                        content = details['requestBody'].get('content', {})
                        for media_type, media_details in content.items():
                            if 'schema' in media_details:
                                schema_ref = media_details['schema'].get('$ref', '')
                                if schema_ref:
                                    request_schemas.add(schema_ref)
                    
                    # Count response schemas
                    if 'responses' in details:
                        for response in details['responses'].values():
                            content = response.get('content', {})
                            for media_type, media_details in content.items():
                                if 'schema' in media_details:
                                    schema_ref = media_details['schema'].get('$ref', '')
                                    if schema_ref:
                                        response_schemas.add(schema_ref)
        
        # Calculate complexity
        complexity_score = self._calculate_complexity_score(
            total_endpoints, len(unique_resources), has_auth, has_pagination
        )
        
        complexity_level = self._determine_complexity_level(total_endpoints)
        
        return APIMetrics(
            total_endpoints=total_endpoints,
            get_operations=operations['get'],
            post_operations=operations['post'],
            put_operations=operations['put'],
            patch_operations=operations['patch'],
            delete_operations=operations['delete'],
            unique_resources=len(unique_resources),
            has_authentication=has_auth,
            has_pagination=has_pagination,
            has_filtering=has_filtering,
            has_file_uploads=has_uploads,
            request_body_schemas=len(request_schemas),
            response_schemas=len(response_schemas),
            complexity_score=complexity_score,
            complexity_level=complexity_level
        )
    
    def _calculate_complexity_score(
        self,
        endpoints: int,
        resources: int,
        has_auth: bool,
        has_pagination: bool
    ) -> float:
        """
        Calculate normalized complexity score (0-100).
        
        Formula:
        - Base: endpoints * 2
        - Resource diversity: resources * 3
        - Auth complexity: +10 if present
        - Pagination complexity: +5 if present
        """
        score = (endpoints * 2) + (resources * 3)
        
        if has_auth:
            score += 10
        
        if has_pagination:
            score += 5
        
        # Normalize to 0-100 (cap at 100)
        return min(score, 100)
    
    def _determine_complexity_level(self, endpoints: int) -> APIComplexity:
        """Determine complexity level from endpoint count."""
        if endpoints <= 5:
            return APIComplexity.TRIVIAL
        elif endpoints <= 15:
            return APIComplexity.LOW
        elif endpoints <= 30:
            return APIComplexity.MEDIUM
        elif endpoints <= 50:
            return APIComplexity.HIGH
        else:
            return APIComplexity.VERY_HIGH


def estimate_from_swagger(file_path: str) -> Optional[Dict[str, any]]:
    """
    Main entry point for Swagger-based estimation.
    
    Args:
        file_path: Path to Swagger/OpenAPI file
        
    Returns:
        Estimation dict with complexity, hours, and metrics
    """
    parser = SwaggerParser()
    metrics = parser.parse_file(file_path)
    
    if not metrics:
        return None
    
    # Estimate hours based on complexity
    # Rule of thumb: 4-8 hours per endpoint (average 6)
    base_hours = metrics.total_endpoints * 6
    
    # Adjust for complexity factors
    multiplier = 1.0
    
    if metrics.has_authentication:
        multiplier += 0.3  # +30% for auth
    
    if metrics.has_file_uploads:
        multiplier += 0.2  # +20% for file handling
    
    if metrics.has_pagination:
        multiplier += 0.1  # +10% for pagination
    
    if metrics.has_filtering:
        multiplier += 0.15  # +15% for filtering
    
    estimated_hours = base_hours * multiplier
    
    return {
        'complexity': metrics.complexity_level.value,
        'complexity_name': metrics.complexity_level.name,
        'estimated_hours': round(estimated_hours, 1),
        'estimated_days': round(estimated_hours / 8, 1),
        'total_endpoints': metrics.total_endpoints,
        'unique_resources': metrics.unique_resources,
        'complexity_score': metrics.complexity_score,
        'features': {
            'authentication': metrics.has_authentication,
            'pagination': metrics.has_pagination,
            'filtering': metrics.has_filtering,
            'file_uploads': metrics.has_file_uploads
        },
        'operations': {
            'GET': metrics.get_operations,
            'POST': metrics.post_operations,
            'PUT': metrics.put_operations,
            'PATCH': metrics.patch_operations,
            'DELETE': metrics.delete_operations
        },
        'schemas': {
            'requests': metrics.request_body_schemas,
            'responses': metrics.response_schemas
        }
    }
