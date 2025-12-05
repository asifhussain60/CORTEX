"""
Tests for Universal Dashboard Schema v2.0

Tests comprehensive schema structure supporting:
- Multiple project types (full-stack, API, frontend, database, microservices)
- Multi-language support (C#, TypeScript, Python, ColdFusion, SQL)
- Adaptive UI compatibility
- Backward compatibility with v1 schema

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

TDD Approach: RED → GREEN → REFACTOR
Phase: RED (Tests written first, expected to fail)
"""

import pytest
import json
from pathlib import Path
from datetime import datetime


class TestUniversalSchemaV2Structure:
    """Test schema structure and required fields"""
    
    def test_schema_has_version_2_0(self):
        """Schema must declare version 2.0.0"""
        # This will fail until schema file is created
        from src.dashboard.schema.universal_schema_v2 import SCHEMA_VERSION
        assert SCHEMA_VERSION == "2.0.0"
    
    def test_schema_has_all_required_sections(self):
        """Schema must include all 12 required sections"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        required_sections = [
            "schema_version",
            "metadata",
            "architecture",
            "frontend",
            "backend",
            "database",
            "infrastructure",
            "code_metrics",
            "security",
            "testing",
            "business_domain",
            "documentation",
            "health"
        ]
        
        schema = UniversalSchemaV2.get_schema()
        for section in required_sections:
            assert section in schema, f"Missing required section: {section}"
    
    def test_metadata_section_structure(self):
        """Metadata section must have project identification fields"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        schema = UniversalSchemaV2.get_schema()
        metadata = schema["metadata"]
        
        required_fields = [
            "project_name",
            "project_type",
            "primary_languages",
            "repository_url",
            "branch",
            "scan_timestamp",
            "scan_duration_seconds",
            "total_files_scanned"
        ]
        
        for field in required_fields:
            assert field in metadata, f"Metadata missing field: {field}"
    
    def test_architecture_section_has_layers_and_components(self):
        """Architecture section must support layers and components"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        schema = UniversalSchemaV2.get_schema()
        architecture = schema["architecture"]
        
        assert "type" in architecture
        assert "layers" in architecture
        assert "components" in architecture
        assert "microservices" in architecture
    
    def test_frontend_section_structure(self):
        """Frontend section must capture UI framework and components"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        schema = UniversalSchemaV2.get_schema()
        frontend = schema["frontend"]
        
        required_fields = [
            "framework",
            "version",
            "components_count",
            "routes_count",
            "state_management",
            "ui_library",
            "bundle_size_kb",
            "dependencies",
            "pages"
        ]
        
        for field in required_fields:
            assert field in frontend, f"Frontend missing field: {field}"
    
    def test_backend_section_structure(self):
        """Backend section must capture API and service details"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        schema = UniversalSchemaV2.get_schema()
        backend = schema["backend"]
        
        required_fields = [
            "framework",
            "version",
            "api_type",
            "endpoints",
            "services",
            "middleware",
            "background_jobs"
        ]
        
        for field in required_fields:
            assert field in backend, f"Backend missing field: {field}"
    
    def test_database_section_structure(self):
        """Database section must capture schema details"""
        from src.dashboard.schema.universal_schema_v2 import UniversalSchemaV2
        
        schema = UniversalSchemaV2.get_schema()
        database = schema["database"]
        
        required_fields = [
            "platform",
            "version",
            "schema",
            "orm",
            "migrations"
        ]
        
        for field in required_fields:
            assert field in database, f"Database missing field: {field}"
        
        # Schema subsection
        schema_section = database["schema"]
        assert "tables" in schema_section
        assert "views" in schema_section
        assert "stored_procedures" in schema_section
        assert "functions" in schema_section


class TestSchemaValidator:
    """Test schema validation logic"""
    
    def test_validator_accepts_valid_v2_data(self):
        """Validator should accept properly formatted v2 data"""
        from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2
        
        valid_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "project_name": "Test Project",
                "project_type": "full_stack",
                "primary_languages": ["C#", "TypeScript"],
                "repository_url": "https://github.com/test/repo",
                "branch": "main",
                "scan_timestamp": datetime.now().isoformat(),
                "scan_duration_seconds": 10.5,
                "total_files_scanned": 100
            },
            "architecture": {
                "type": "n-tier",
                "layers": [],
                "components": [],
                "microservices": []
            },
            "frontend": None,
            "backend": None,
            "database": None,
            "infrastructure": None,
            "code_metrics": {},
            "security": {},
            "testing": {},
            "business_domain": None,
            "documentation": {},
            "health": {
                "overall_score": 85,
                "trend": "stable",
                "status": "healthy"
            }
        }
        
        validator = SchemaValidatorV2()
        result = validator.validate(valid_data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validator_rejects_missing_required_fields(self):
        """Validator should reject data missing required fields"""
        from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2
        
        invalid_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "project_name": "Test Project"
                # Missing other required fields
            }
        }
        
        validator = SchemaValidatorV2()
        result = validator.validate(invalid_data)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validator_accepts_v1_schema_for_compatibility(self):
        """Validator should accept v1 schema for backward compatibility"""
        from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2
        
        v1_data = {
            "metadata": {
                "repo_name": "CORTEX",
                "branch": "main",
                "commit_hash": "abc123",
                "commit_date": datetime.now().isoformat(),
                "last_scan": datetime.now().isoformat()
            },
            "health": {
                "overall_score": 92,
                "trend": "improving",
                "status": "healthy"
            },
            "code_metrics": {
                "lines_of_code": 10000,
                "file_count": 100,
                "directory_count": 20
            },
            "code_quality": {
                "complexity_score": 75,
                "maintainability_index": 80
            }
        }
        
        validator = SchemaValidatorV2()
        result = validator.validate(v1_data, allow_v1=True)
        
        assert result.is_valid
        assert result.schema_version == "1.0.0"


class TestProjectTypeDetection:
    """Test automatic project type detection from data"""
    
    def test_detect_full_stack_project(self):
        """Detect full-stack when both frontend and backend present"""
        from src.dashboard.schema.project_type_detector import ProjectTypeDetector
        
        data = {
            "frontend": {"components_count": 45},
            "backend": {"endpoints": [{"path": "/api/test"}]},
            "database": None
        }
        
        detector = ProjectTypeDetector(data)
        assert detector.get_type() == "full_stack"
        assert detector.has_frontend()
        assert detector.has_backend()
    
    def test_detect_api_only_project(self):
        """Detect API-only when backend present but no frontend"""
        from src.dashboard.schema.project_type_detector import ProjectTypeDetector
        
        data = {
            "frontend": None,
            "backend": {"endpoints": [{"path": "/api/test"}]},
            "database": {"schema": {"tables": []}}
        }
        
        detector = ProjectTypeDetector(data)
        assert detector.get_type() == "api"
        assert not detector.has_frontend()
        assert detector.has_backend()
    
    def test_detect_frontend_only_project(self):
        """Detect frontend-only when UI present but no backend"""
        from src.dashboard.schema.project_type_detector import ProjectTypeDetector
        
        data = {
            "frontend": {"components_count": 30, "framework": "React"},
            "backend": None,
            "database": None
        }
        
        detector = ProjectTypeDetector(data)
        assert detector.get_type() == "frontend"
        assert detector.has_frontend()
        assert not detector.has_backend()
    
    def test_detect_database_project(self):
        """Detect database-only when schema present but no UI/API"""
        from src.dashboard.schema.project_type_detector import ProjectTypeDetector
        
        data = {
            "frontend": None,
            "backend": None,
            "database": {"schema": {"tables": [{"name": "Users"}]}}
        }
        
        detector = ProjectTypeDetector(data)
        assert detector.get_type() == "database"
        assert not detector.has_frontend()
        assert not detector.has_backend()
        assert detector.has_database()
    
    def test_detect_microservices_architecture(self):
        """Detect microservices when architecture type indicates it"""
        from src.dashboard.schema.project_type_detector import ProjectTypeDetector
        
        data = {
            "architecture": {"type": "microservices"},
            "backend": {"endpoints": []},
            "frontend": None,
            "database": None
        }
        
        detector = ProjectTypeDetector(data)
        assert detector.get_type() == "microservices"


class TestSchemaMigration:
    """Test migration from v1 to v2 schema"""
    
    def test_migrate_v1_to_v2_preserves_data(self):
        """Migration should preserve all v1 data in v2 format"""
        from src.dashboard.schema.schema_migrator import SchemaMigrator
        
        v1_data = {
            "metadata": {
                "repo_name": "CORTEX",
                "branch": "main",
                "commit_hash": "abc123",
                "last_scan": "2025-12-05T10:00:00"
            },
            "health": {
                "overall_score": 92,
                "trend": "improving",
                "status": "healthy"
            },
            "code_metrics": {
                "lines_of_code": 10000,
                "file_count": 100
            }
        }
        
        migrator = SchemaMigrator()
        v2_data = migrator.migrate_v1_to_v2(v1_data)
        
        assert v2_data["schema_version"] == "2.0.0"
        assert v2_data["metadata"]["project_name"] == "CORTEX"
        assert v2_data["health"]["overall_score"] == 92
    
    def test_migration_adds_new_v2_sections(self):
        """Migration should add new v2 sections with defaults"""
        from src.dashboard.schema.schema_migrator import SchemaMigrator
        
        v1_data = {
            "metadata": {"repo_name": "Test"},
            "health": {"overall_score": 80}
        }
        
        migrator = SchemaMigrator()
        v2_data = migrator.migrate_v1_to_v2(v1_data)
        
        # New sections should exist but be None/empty
        assert "frontend" in v2_data
        assert "backend" in v2_data
        assert "database" in v2_data
        assert "infrastructure" in v2_data
        assert "business_domain" in v2_data


class TestSchemaExamples:
    """Test schema with real-world project examples"""
    
    def test_luum_fresh_full_stack_schema(self):
        """Test schema structure for luum-fresh (full-stack MVC)"""
        from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2
        
        luum_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "project_name": "luum-fresh",
                "project_type": "full_stack",
                "primary_languages": ["C#", "JavaScript", "SQL"],
                "repository_url": "file:///C:/PROJECTS/luum-fresh",
                "branch": "main",
                "scan_timestamp": datetime.now().isoformat(),
                "scan_duration_seconds": 45.2,
                "total_files_scanned": 9657
            },
            "architecture": {
                "type": "n-tier",
                "layers": [
                    {"name": "Presentation", "path": "Luum.Web", "file_count": 443},
                    {"name": "Business", "path": "Luum", "file_count": 4835},
                    {"name": "Data", "path": "Luum.Database", "file_count": 4822}
                ],
                "components": [],
                "microservices": []
            },
            "frontend": {
                "framework": "MVC Razor",
                "version": "5.2.7",
                "components_count": 443,
                "routes_count": 150,
                "state_management": None,
                "ui_library": "jQuery",
                "bundle_size_kb": 0,
                "dependencies": [],
                "pages": []
            },
            "backend": {
                "framework": "ASP.NET MVC + Web API",
                "version": "4.7.2",
                "api_type": "REST",
                "endpoints": [],
                "services": [],
                "middleware": ["CORS", "JWT", "ExceptionFilter"],
                "background_jobs": []
            },
            "database": {
                "platform": "SQL Azure",
                "version": "12.0",
                "schema": {
                    "tables": [],
                    "views": [],
                    "stored_procedures": [],
                    "functions": []
                },
                "orm": "Entity Framework 6.4",
                "migrations": {"count": 0, "pending": 0}
            },
            "infrastructure": {
                "cloud_provider": "Azure",
                "deployment_type": "App Service",
                "ci_cd": "Azure DevOps",
                "iac_tool": "ARM Templates",
                "monitoring": ["Application Insights"],
                "configuration": {
                    "files": ["web.config", "appsettings.json"],
                    "secrets_management": "Key Vault"
                }
            },
            "code_metrics": {},
            "security": {},
            "testing": {},
            "business_domain": None,
            "documentation": {},
            "health": {
                "overall_score": 85,
                "trend": "stable",
                "status": "healthy"
            }
        }
        
        validator = SchemaValidatorV2()
        result = validator.validate(luum_data)
        
        assert result.is_valid
        assert luum_data["metadata"]["project_type"] == "full_stack"
    
    def test_tcbulk_angular_schema(self):
        """Test schema structure for TCBULK (Angular + .NET Core)"""
        from src.dashboard.schema.schema_validator_v2 import SchemaValidatorV2
        
        tcbulk_data = {
            "schema_version": "2.0.0",
            "metadata": {
                "project_name": "TCBULK",
                "project_type": "full_stack",
                "primary_languages": ["TypeScript", "C#", "SQL"],
                "repository_url": "file:///C:/PROJECTS/TCBULK",
                "branch": "main",
                "scan_timestamp": datetime.now().isoformat(),
                "scan_duration_seconds": 15.8,
                "total_files_scanned": 792
            },
            "architecture": {
                "type": "n-tier",
                "layers": [],
                "components": [],
                "microservices": []
            },
            "frontend": {
                "framework": "Angular",
                "version": "12.2.0",
                "components_count": 45,
                "routes_count": 28,
                "state_management": "NgRx",
                "ui_library": "Angular Material",
                "bundle_size_kb": 2400,
                "dependencies": [],
                "pages": []
            },
            "backend": {
                "framework": ".NET Core",
                "version": "5.0",
                "api_type": "REST",
                "endpoints": [],
                "services": [],
                "middleware": [],
                "background_jobs": []
            },
            "database": {
                "platform": "SQL Server",
                "version": "2019",
                "schema": {"tables": [], "views": [], "stored_procedures": [], "functions": []},
                "orm": "Entity Framework Core",
                "migrations": {"count": 0, "pending": 0}
            },
            "infrastructure": None,
            "code_metrics": {},
            "security": {},
            "testing": {},
            "business_domain": None,
            "documentation": {},
            "health": {
                "overall_score": 80,
                "trend": "stable",
                "status": "healthy"
            }
        }
        
        validator = SchemaValidatorV2()
        result = validator.validate(tcbulk_data)
        
        assert result.is_valid
        assert tcbulk_data["frontend"]["framework"] == "Angular"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
