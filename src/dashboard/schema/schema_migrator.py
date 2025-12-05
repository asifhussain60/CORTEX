"""
Schema Migrator

Migrates v1 schema data to v2 schema format.
Ensures backward compatibility and data preservation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any
from datetime import datetime


class SchemaMigrator:
    """Migrates dashboard data between schema versions"""
    
    def migrate_v1_to_v2(self, v1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate v1 schema to v2 schema.
        
        Args:
            v1_data: Data in v1 format
        
        Returns:
            Data in v2 format with all original data preserved
        """
        v2_data = {
            "schema_version": "2.0.0",
            "metadata": self._migrate_metadata(v1_data.get("metadata", {})),
            "architecture": {
                "type": "unknown",
                "layers": [],
                "components": [],
                "microservices": []
            },
            "frontend": None,
            "backend": None,
            "database": None,
            "infrastructure": None,
            "code_metrics": self._migrate_code_metrics(v1_data.get("code_metrics", {})),
            "security": self._migrate_security(v1_data.get("security", {})),
            "testing": self._migrate_testing(v1_data.get("testing", {})),
            "business_domain": None,
            "documentation": self._migrate_documentation(v1_data.get("documentation", {})),
            "health": self._migrate_health(v1_data.get("health", {}))
        }
        
        return v2_data
    
    def _migrate_metadata(self, v1_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate metadata section"""
        return {
            "project_name": v1_metadata.get("repo_name", "Unknown"),
            "project_type": "unknown",
            "primary_languages": [],
            "repository_url": v1_metadata.get("repo_url", ""),
            "branch": v1_metadata.get("branch", "main"),
            "scan_timestamp": v1_metadata.get("last_scan", datetime.now().isoformat()),
            "scan_duration_seconds": v1_metadata.get("scan_duration_seconds", 0),
            "total_files_scanned": 0
        }
    
    def _migrate_code_metrics(self, v1_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate code_metrics section"""
        return {
            "languages": v1_metrics.get("language_breakdown", {}),
            "complexity": {
                "cyclomatic_avg": v1_metrics.get("cyclomatic_complexity_avg", 0),
                "cognitive_avg": v1_metrics.get("cognitive_complexity_avg", 0),
                "maintainability_index": v1_metrics.get("maintainability_index", 0)
            },
            "quality": {
                "code_smells": 0,
                "technical_debt_hours": 0,
                "duplication_pct": v1_metrics.get("code_duplication_pct", 0),
                "comment_ratio": v1_metrics.get("comment_ratio_pct", 0)
            },
            "hotspots": []
        }
    
    def _migrate_security(self, v1_security: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate security section"""
        return {
            "overall_score": v1_security.get("overall_score", 70),
            "vulnerabilities": v1_security.get("vulnerabilities", {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }),
            "owasp_top_10": [],
            "dependency_vulnerabilities": [],
            "secrets_exposed": 0,
            "ssl_tls_issues": 0
        }
    
    def _migrate_testing(self, v1_testing: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate testing section"""
        return {
            "unit_tests": {
                "count": v1_testing.get("unit_test_count", 0),
                "coverage_pct": v1_testing.get("coverage_pct", 0),
                "pass_rate": v1_testing.get("test_pass_rate_pct", 100)
            },
            "integration_tests": {
                "count": v1_testing.get("integration_test_count", 0),
                "coverage_pct": 0
            },
            "e2e_tests": {
                "count": 0,
                "framework": None
            },
            "test_quality": {
                "assertion_density": 0,
                "test_smells": 0
            }
        }
    
    def _migrate_documentation(self, v1_docs: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate documentation section"""
        return {
            "readme_present": v1_docs.get("readme_present", False),
            "api_documentation": None,
            "architecture_diagrams": 0,
            "inline_comments_pct": 0,
            "documentation_score": v1_docs.get("documentation_score", 0)
        }
    
    def _migrate_health(self, v1_health: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate health section"""
        return {
            "overall_score": v1_health.get("overall_score", 70),
            "trend": v1_health.get("trend", "stable"),
            "status": v1_health.get("status", "healthy"),
            "last_deployment": None,
            "incidents_30d": 0
        }
