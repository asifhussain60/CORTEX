"""
Golden Tests for Repository Onboarding with Schema Validation

Validates that all onboarding outputs conform to dashboard-compatible schemas.
Tests JSON/YAML serialization, schema versioning, and data completeness.

Based on audit analysis showing:
- 215+ onboarding operations logged
- Multiple output locations (registry, intelligence DB, dashboard data)
- Schema drift risk between v1.0 and v3.0

Authority: CORE-008 (TDD), CORE-027 (Audit), CORE-002 (No .md files)
Priority: P0 - Prevents Dashboard Breakage
"""

import json
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml
from jsonschema import validate, ValidationError, Draft7Validator


# ============================================================================
# SCHEMA DEFINITIONS (Dashboard-Compatible)
# ============================================================================

REPOSITORY_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["repository", "metadata", "analysis"],
    "properties": {
        "schema_version": {"type": "string", "enum": ["1.0"]},
        "repository": {
            "type": "object",
            "required": ["name", "path", "onboarded_at"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "display_name": {"type": "string"},
                "path": {"type": "string"},
                "onboarded_at": {"type": "string", "format": "date-time"},
                "primary_language": {"type": "string"},
                "health_score": {"type": "number", "minimum": 0, "maximum": 100}
            }
        },
        "metadata": {
            "type": "object",
            "required": ["files_analyzed", "total_lines"],
            "properties": {
                "files_analyzed": {"type": "integer", "minimum": 0},
                "total_lines": {"type": "integer", "minimum": 0},
                "test_files": {"type": "integer", "minimum": 0},
                "learning_metrics": {"type": "object"}
            }
        },
        "analysis": {
            "type": "object",
            "required": ["status", "architecture_type"],
            "properties": {
                "status": {"type": "string", "enum": ["success", "partial_success", "failed"]},
                "architecture_type": {"type": "string"},
                "patterns_detected": {"type": "array", "items": {"type": "string"}},
                "violations": {"type": "array"}
            }
        }
    }
}

AST_GRAPH_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["nodes", "edges", "metadata"],
    "properties": {
        "schema_version": {"type": "string", "enum": ["1.0"]},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": ["file", "class", "function", "module"]},
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "metadata": {"type": "object"}
                }
            }
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source", "target", "type"],
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "type": {"type": "string", "enum": ["imports", "calls", "inherits", "uses"]},
                    "weight": {"type": "number", "minimum": 0}
                }
            }
        },
        "metadata": {
            "type": "object",
            "required": ["generated_at", "node_count", "edge_count"],
            "properties": {
                "generated_at": {"type": "string", "format": "date-time"},
                "node_count": {"type": "integer", "minimum": 0},
                "edge_count": {"type": "integer", "minimum": 0},
                "repository_path": {"type": "string"}
            }
        }
    }
}

DASHBOARD_DATA_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["repository", "health", "issues", "metrics"],
    "properties": {
        "schema_version": {"type": "string", "enum": ["1.0"]},
        "repository": {
            "type": "object",
            "required": ["name", "display_name", "health_score"],
            "properties": {
                "name": {"type": "string"},
                "display_name": {"type": "string"},
                "health_score": {"type": "number", "minimum": 0, "maximum": 100},
                "last_updated": {"type": "string", "format": "date-time"}
            }
        },
        "health": {
            "type": "object",
            "required": ["overall_score", "categories"],
            "properties": {
                "overall_score": {"type": "number", "minimum": 0, "maximum": 100},
                "categories": {
                    "type": "object",
                    "properties": {
                        "architecture": {"type": "number", "minimum": 0, "maximum": 100},
                        "testing": {"type": "number", "minimum": 0, "maximum": 100},
                        "documentation": {"type": "number", "minimum": 0, "maximum": 100},
                        "governance": {"type": "number", "minimum": 0, "maximum": 100}
                    }
                }
            }
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["severity", "category", "description"],
                "properties": {
                    "severity": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"}
                }
            }
        },
        "metrics": {
            "type": "object",
            "properties": {
                "files_analyzed": {"type": "integer", "minimum": 0},
                "test_coverage": {"type": "number", "minimum": 0, "maximum": 100},
                "code_quality": {"type": "number", "minimum": 0, "maximum": 100}
            }
        }
    }
}


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""
    schema_name: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    data_sample: Optional[Dict[str, Any]] = None


class LENSDataValidator:
    """Validates LENS output data against schemas."""
    
    def __init__(self):
        self.schemas = {
            "repository_v1": REPOSITORY_SCHEMA_V1,
            "ast_graph_v1": AST_GRAPH_SCHEMA_V1,
            "dashboard_data_v1": DASHBOARD_DATA_SCHEMA_V1
        }
    
    def validate_json(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> SchemaValidationResult:
        """
        Validate JSON data against named schema.
        
        Args:
            data: Data to validate
            schema_name: Schema name (e.g., "repository_v1")
        
        Returns:
            Validation result
        """
        if schema_name not in self.schemas:
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"Unknown schema: {schema_name}"],
                warnings=[]
            )
        
        schema = self.schemas[schema_name]
        errors = []
        warnings = []
        
        try:
            # Validate structure
            validate(instance=data, schema=schema)
            
            # Check for schema version
            if "schema_version" not in data:
                warnings.append("Missing schema_version field")
            
            # Check for required dashboard fields
            if schema_name == "repository_v1":
                if "repository" in data and "display_name" not in data["repository"]:
                    warnings.append("Missing display_name (recommended for dashboard)")
                if "repository" in data and "health_score" not in data["repository"]:
                    warnings.append("Missing health_score (recommended for dashboard)")
            
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=True,
                errors=[],
                warnings=warnings,
                data_sample=data
            )
        
        except ValidationError as e:
            errors.append(f"Validation error at {'.'.join(str(p) for p in e.path)}: {e.message}")
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=errors,
                warnings=warnings,
                data_sample=data
            )
    
    def validate_file(
        self,
        file_path: Path,
        schema_name: str
    ) -> SchemaValidationResult:
        """
        Validate file content against schema.
        
        Args:
            file_path: Path to JSON/YAML file
            schema_name: Schema to validate against
        
        Returns:
            Validation result
        """
        if not file_path.exists():
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"File not found: {file_path}"],
                warnings=[]
            )
        
        try:
            # Load file
            if file_path.suffix == ".json":
                with open(file_path) as f:
                    data = json.load(f)
            elif file_path.suffix in [".yaml", ".yml"]:
                with open(file_path) as f:
                    data = yaml.safe_load(f)
            else:
                return SchemaValidationResult(
                    schema_name=schema_name,
                    valid=False,
                    errors=[f"Unsupported file type: {file_path.suffix}"],
                    warnings=[]
                )
            
            return self.validate_json(data, schema_name)
        
        except Exception as e:
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"Failed to load file: {str(e)}"],
                warnings=[]
            )
    
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get schema by name."""
        return self.schemas.get(schema_name)


@pytest.fixture
def validator():
    """Create LENS data validator."""
    return LENSDataValidator()


@pytest.fixture
def sample_repository_data():
    """Create sample repository data."""
    return {
        "schema_version": "1.0",
        "repository": {
            "name": "test-repo",
            "display_name": "Test Repository",
            "path": "/path/to/test-repo",
            "onboarded_at": datetime.utcnow().isoformat(),
            "primary_language": "python",
            "health_score": 85.5
        },
        "metadata": {
            "files_analyzed": 150,
            "total_lines": 5000,
            "test_files": 25,
            "learning_metrics": {
                "total_learnings": 0,
                "by_orchestrator": {}
            }
        },
        "analysis": {
            "status": "success",
            "architecture_type": "layered",
            "patterns_detected": ["mvc", "repository"],
            "violations": []
        }
    }


@pytest.fixture
def sample_ast_graph():
    """Create sample AST graph."""
    return {
        "schema_version": "1.0",
        "nodes": [
            {
                "id": "file_0",
                "type": "file",
                "name": "main.py",
                "path": "src/main.py",
                "metadata": {}
            },
            {
                "id": "file_1",
                "type": "file",
                "name": "utils.py",
                "path": "src/utils.py",
                "metadata": {}
            }
        ],
        "edges": [
            {
                "source": "file_0",
                "target": "file_1",
                "type": "imports",
                "weight": 1.0
            }
        ],
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "node_count": 2,
            "edge_count": 1,
            "repository_path": "/path/to/repo"
        }
    }


@pytest.fixture
def sample_dashboard_data():
    """Create sample dashboard data."""
    return {
        "schema_version": "1.0",
        "repository": {
            "name": "test-repo",
            "display_name": "Test Repository",
            "health_score": 85.0,
            "last_updated": datetime.utcnow().isoformat()
        },
        "health": {
            "overall_score": 85.0,
            "categories": {
                "architecture": 90.0,
                "testing": 80.0,
                "documentation": 75.0,
                "governance": 95.0
            }
        },
        "issues": [
            {
                "severity": "P1",
                "category": "testing",
                "description": "Low test coverage in module X",
                "file": "src/module_x.py",
                "line": 42
            }
        ],
        "metrics": {
            "files_analyzed": 150,
            "test_coverage": 78.5,
            "code_quality": 85.0
        }
    }


# ============================================================================
# GOLDEN TESTS - Schema Validation
# ============================================================================

class TestRepositorySchemaValidation:
    """Golden tests for repository onboarding schema."""
    
    def test_valid_repository_data_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any]
    ):
        """
        Golden test: Valid repository data passes schema validation.
        """
        result = validator.validate_json(sample_repository_data, "repository_v1")
        
        assert result.valid, f"Validation failed: {result.errors}"
        assert len(result.errors) == 0
        assert result.schema_name == "repository_v1"
    
    def test_missing_required_field_golden(
        self,
        validator: LENSDataValidator
    ):
        """
        Golden test: Missing required field causes validation failure.
        """
        invalid_data = {
            "schema_version": "1.0",
            "repository": {
                "name": "test-repo"
                # Missing: path, onboarded_at
            },
            "metadata": {
                "files_analyzed": 0,
                "total_lines": 0
            },
            "analysis": {
                "status": "success",
                "architecture_type": "unknown"
            }
        }
        
        result = validator.validate_json(invalid_data, "repository_v1")
        
        assert not result.valid
        assert len(result.errors) > 0
        assert any("required" in err.lower() for err in result.errors)
    
    def test_schema_version_warning_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any]
    ):
        """
        Golden test: Missing schema_version triggers warning.
        """
        data_without_version = sample_repository_data.copy()
        del data_without_version["schema_version"]
        
        result = validator.validate_json(data_without_version, "repository_v1")
        
        # Should still be valid but with warning
        assert result.valid
        assert any("schema_version" in warn for warn in result.warnings)
    
    def test_health_score_bounds_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any]
    ):
        """
        Golden test: Health score must be between 0 and 100.
        """
        # Test lower bound
        data_low = sample_repository_data.copy()
        data_low["repository"]["health_score"] = -5
        
        result_low = validator.validate_json(data_low, "repository_v1")
        assert not result_low.valid
        
        # Test upper bound
        data_high = sample_repository_data.copy()
        data_high["repository"]["health_score"] = 105
        
        result_high = validator.validate_json(data_high, "repository_v1")
        assert not result_high.valid
        
        # Test valid bounds
        for score in [0, 50, 100]:
            data_valid = sample_repository_data.copy()
            data_valid["repository"]["health_score"] = score
            result_valid = validator.validate_json(data_valid, "repository_v1")
            assert result_valid.valid, f"Score {score} should be valid"


class TestASTGraphSchemaValidation:
    """Golden tests for AST graph schema."""
    
    def test_valid_ast_graph_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any]
    ):
        """
        Golden test: Valid AST graph passes schema validation.
        """
        result = validator.validate_json(sample_ast_graph, "ast_graph_v1")
        
        assert result.valid, f"Validation failed: {result.errors}"
        assert len(result.errors) == 0
    
    def test_empty_graph_golden(
        self,
        validator: LENSDataValidator
    ):
        """
        Golden test: Empty graph (no nodes/edges) is valid.
        """
        empty_graph = {
            "schema_version": "1.0",
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "node_count": 0,
                "edge_count": 0
            }
        }
        
        result = validator.validate_json(empty_graph, "ast_graph_v1")
        assert result.valid
    
    def test_invalid_node_type_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any]
    ):
        """
        Golden test: Invalid node type causes validation failure.
        """
        invalid_graph = sample_ast_graph.copy()
        invalid_graph["nodes"][0]["type"] = "invalid_type"
        
        result = validator.validate_json(invalid_graph, "ast_graph_v1")
        
        assert not result.valid
        assert any("enum" in err.lower() or "invalid_type" in err.lower() for err in result.errors)
    
    def test_metadata_counts_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any]
    ):
        """
        Golden test: Metadata counts must be non-negative integers.
        """
        # Test negative count
        invalid_graph = sample_ast_graph.copy()
        invalid_graph["metadata"]["node_count"] = -1
        
        result = validator.validate_json(invalid_graph, "ast_graph_v1")
        assert not result.valid


class TestDashboardDataSchemaValidation:
    """Golden tests for dashboard data schema."""
    
    def test_valid_dashboard_data_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any]
    ):
        """
        Golden test: Valid dashboard data passes schema validation.
        """
        result = validator.validate_json(sample_dashboard_data, "dashboard_data_v1")
        
        assert result.valid, f"Validation failed: {result.errors}"
        assert len(result.errors) == 0
    
    def test_issue_severity_levels_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any]
    ):
        """
        Golden test: Issue severity must be P0, P1, P2, or P3.
        """
        # Test invalid severity
        invalid_data = sample_dashboard_data.copy()
        invalid_data["issues"][0]["severity"] = "CRITICAL"
        
        result = validator.validate_json(invalid_data, "dashboard_data_v1")
        assert not result.valid
        
        # Test valid severities
        for severity in ["P0", "P1", "P2", "P3"]:
            valid_data = sample_dashboard_data.copy()
            valid_data["issues"][0]["severity"] = severity
            
            result = validator.validate_json(valid_data, "dashboard_data_v1")
            assert result.valid, f"Severity {severity} should be valid"
    
    def test_health_category_scores_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any]
    ):
        """
        Golden test: Health category scores must be 0-100.
        """
        categories = ["architecture", "testing", "documentation", "governance"]
        
        for category in categories:
            # Test invalid score
            invalid_data = sample_dashboard_data.copy()
            invalid_data["health"]["categories"][category] = 150
            
            result = validator.validate_json(invalid_data, "dashboard_data_v1")
            assert not result.valid, f"Score 150 for {category} should be invalid"


class TestFileValidation:
    """Golden tests for file-based validation."""
    
    def test_validate_json_file_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path
    ):
        """
        Golden test: Validate JSON file content.
        """
        # Write sample data to file
        json_file = tmp_path / "repository.json"
        with open(json_file, "w") as f:
            json.dump(sample_repository_data, f, indent=2)
        
        # Validate file
        result = validator.validate_file(json_file, "repository_v1")
        
        assert result.valid
        assert len(result.errors) == 0
    
    def test_validate_yaml_file_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path
    ):
        """
        Golden test: Validate YAML file content.
        """
        # Write sample data to file
        yaml_file = tmp_path / "repository.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(sample_repository_data, f)
        
        # Validate file
        result = validator.validate_file(yaml_file, "repository_v1")
        
        assert result.valid
        assert len(result.errors) == 0
    
    def test_validate_missing_file_golden(
        self,
        validator: LENSDataValidator
    ):
        """
        Golden test: Missing file causes validation failure.
        """
        result = validator.validate_file(Path("/nonexistent/file.json"), "repository_v1")
        
        assert not result.valid
        assert any("not found" in err.lower() for err in result.errors)


class TestRoundTripSerialization:
    """Golden tests for round-trip JSON/YAML serialization."""
    
    def test_json_round_trip_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path
    ):
        """
        Golden test: Data survives JSON serialization round-trip.
        """
        # Write to JSON
        json_file = tmp_path / "test.json"
        with open(json_file, "w") as f:
            json.dump(sample_repository_data, f, indent=2)
        
        # Read back
        with open(json_file) as f:
            loaded_data = json.load(f)
        
        # Validate both original and loaded
        result_original = validator.validate_json(sample_repository_data, "repository_v1")
        result_loaded = validator.validate_json(loaded_data, "repository_v1")
        
        assert result_original.valid
        assert result_loaded.valid
        assert loaded_data == sample_repository_data
    
    def test_yaml_round_trip_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path
    ):
        """
        Golden test: Data survives YAML serialization round-trip.
        """
        # Write to YAML
        yaml_file = tmp_path / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(sample_repository_data, f)
        
        # Read back
        with open(yaml_file) as f:
            loaded_data = yaml.safe_load(f)
        
        # Validate both
        result_original = validator.validate_json(sample_repository_data, "repository_v1")
        result_loaded = validator.validate_json(loaded_data, "repository_v1")
        
        assert result_original.valid
        assert result_loaded.valid


# ============================================================================
# SUMMARY & COVERAGE REPORT
# ============================================================================

def test_schema_coverage_report(validator: LENSDataValidator):
    """
    Test: Report schema coverage statistics.
    """
    schemas = validator.schemas
    
    print(f"\n{'='*60}")
    print("SCHEMA VALIDATION COVERAGE REPORT")
    print(f"{'='*60}")
    print(f"Total Schemas Defined: {len(schemas)}")
    
    for name, schema in schemas.items():
        required_fields = schema.get("properties", {}).keys()
        print(f"\n{name}:")
        print(f"  - Required top-level fields: {len(required_fields)}")
        print(f"  - Fields: {', '.join(required_fields)}")
    
    print(f"{'='*60}\n")
    
    # Assertions
    assert len(schemas) >= 3, "Should have at least 3 schemas defined"
    assert "repository_v1" in schemas
    assert "ast_graph_v1" in schemas
    assert "dashboard_data_v1" in schemas
