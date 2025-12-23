"""
Universal Dashboard Schema v2.0

Comprehensive schema definition supporting all project types:
- Full-Stack applications
- API-only projects
- Frontend-only projects
- Database projects
- Microservices architectures
- Class libraries

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


SCHEMA_VERSION = "2.0.0"


class UniversalSchema:
    """Universal dashboard schema v2.0 definition"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Get complete schema structure.
        
        Returns:
            Dictionary with all schema sections
        """
        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": UniversalSchema._get_metadata_schema(),
            "architecture": UniversalSchema._get_architecture_schema(),
            "frontend": UniversalSchema._get_frontend_schema(),
            "backend": UniversalSchema._get_backend_schema(),
            "database": UniversalSchema._get_database_schema(),
            "infrastructure": UniversalSchema._get_infrastructure_schema(),
            "code_metrics": UniversalSchema._get_code_metrics_schema(),
            "security": UniversalSchema._get_security_schema(),
            "testing": UniversalSchema._get_testing_schema(),
            "business_domain": UniversalSchema._get_business_domain_schema(),
            "documentation": UniversalSchema._get_documentation_schema(),
            "health": UniversalSchema._get_health_schema()
        }
    
    @staticmethod
    def _get_metadata_schema() -> Dict[str, Any]:
        """Metadata section schema"""
        return {
            "project_name": str,
            "project_type": str,  # full_stack, api, frontend, database, microservices, library
            "primary_languages": list,
            "repository_url": str,
            "branch": str,
            "scan_timestamp": str,
            "scan_duration_seconds": float,
            "total_files_scanned": int
        }
    
    @staticmethod
    def _get_architecture_schema() -> Dict[str, Any]:
        """Architecture section schema"""
        return {
            "type": str,  # n-tier, microservices, monolith, soa, serverless
            "layers": list,
            "components": list,
            "microservices": list
        }
    
    @staticmethod
    def _get_frontend_schema() -> Dict[str, Any]:
        """Frontend section schema"""
        return {
            "framework": Optional[str],
            "version": Optional[str],
            "components_count": int,
            "routes_count": int,
            "state_management": Optional[str],
            "ui_library": Optional[str],
            "bundle_size_kb": int,
            "dependencies": list,
            "pages": list
        }
    
    @staticmethod
    def _get_backend_schema() -> Dict[str, Any]:
        """Backend section schema"""
        return {
            "framework": Optional[str],
            "version": Optional[str],
            "api_type": Optional[str],  # REST, SOAP, GraphQL, gRPC
            "endpoints": list,
            "services": list,
            "middleware": list,
            "background_jobs": list
        }
    
    @staticmethod
    def _get_database_schema() -> Dict[str, Any]:
        """Database section schema"""
        return {
            "platform": Optional[str],
            "version": Optional[str],
            "schema": {
                "tables": list,
                "views": list,
                "stored_procedures": list,
                "functions": list,
                "user_defined_types": list
            },
            "orm": Optional[str],
            "migrations": {
                "count": int,
                "pending": int
            }
        }
    
    @staticmethod
    def _get_infrastructure_schema() -> Dict[str, Any]:
        """Infrastructure section schema"""
        return {
            "cloud_provider": Optional[str],
            "deployment_type": Optional[str],
            "ci_cd": Optional[str],
            "iac_tool": Optional[str],
            "monitoring": list,
            "configuration": dict
        }
    
    @staticmethod
    def _get_code_metrics_schema() -> Dict[str, Any]:
        """Code metrics section schema"""
        return {
            "languages": dict,
            "complexity": dict,
            "quality": dict,
            "hotspots": list
        }
    
    @staticmethod
    def _get_security_schema() -> Dict[str, Any]:
        """Security section schema"""
        return {
            "overall_score": int,
            "vulnerabilities": dict,
            "owasp_top_10": list,
            "dependency_vulnerabilities": list,
            "secrets_exposed": int,
            "ssl_tls_issues": int
        }
    
    @staticmethod
    def _get_testing_schema() -> Dict[str, Any]:
        """Testing section schema"""
        return {
            "unit_tests": dict,
            "integration_tests": dict,
            "e2e_tests": dict,
            "test_quality": dict
        }
    
    @staticmethod
    def _get_business_domain_schema() -> Dict[str, Any]:
        """Business domain section schema"""
        return {
            "entities": list,
            "workflows": list,
            "business_rules": int
        }
    
    @staticmethod
    def _get_documentation_schema() -> Dict[str, Any]:
        """Documentation section schema"""
        return {
            "readme_present": bool,
            "api_documentation": Optional[str],
            "architecture_diagrams": int,
            "inline_comments_pct": float,
            "documentation_score": int
        }
    
    @staticmethod
    def _get_health_schema() -> Dict[str, Any]:
        """Health section schema"""
        return {
            "overall_score": int,
            "trend": str,  # improving, stable, degrading
            "status": str,  # healthy, warning, critical
            "last_deployment": Optional[str],
            "incidents_30d": int
        }
