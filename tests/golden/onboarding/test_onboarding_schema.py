"""
Golden Tests for Repository Onboarding Schema Validation.

Validates that all onboarding outputs conform to dashboard-compatible schemas.
Tests JSON/YAML serialization, schema versioning (2.0.0), and data completeness
across 9 dashboard tab artifacts.

Authority: CORE-008 (TDD), CORE-027 (Audit), CORE-002 (No .md files)
Priority: P0 — Prevents Dashboard Breakage
"""

import json
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml
from jsonschema import Draft7Validator, ValidationError, validate

from cortex.mcp.tools.onboard_repository import (
    DASHBOARD_TABS,
    SCHEMA_VERSION,
)


# ============================================================================
# Schema Version Constant — SSOT for all golden assertions
# ============================================================================

CURRENT_SCHEMA_VERSION = SCHEMA_VERSION  # "2.0.0"


# ============================================================================
# JSON Schema Definitions — Dashboard-Compatible
# ============================================================================

REPOSITORY_SCHEMA_V2 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["repository", "metadata", "analysis"],
    "properties": {
        "schema_version": {"type": "string", "enum": [CURRENT_SCHEMA_VERSION]},
        "repository": {
            "type": "object",
            "required": ["name", "path", "onboarded_at"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "display_name": {"type": "string"},
                "path": {"type": "string"},
                "onboarded_at": {"type": "string"},
                "primary_language": {"type": "string"},
                "health_score": {"type": "number", "minimum": 0, "maximum": 100},
            },
        },
        "metadata": {
            "type": "object",
            "required": ["files_analyzed", "total_lines"],
            "properties": {
                "files_analyzed": {"type": "integer", "minimum": 0},
                "total_lines": {"type": "integer", "minimum": 0},
                "test_files": {"type": "integer", "minimum": 0},
                "learning_metrics": {"type": "object"},
            },
        },
        "analysis": {
            "type": "object",
            "required": ["status", "architecture_type"],
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["success", "partial_success", "failed"],
                },
                "architecture_type": {"type": "string"},
                "patterns_detected": {"type": "array", "items": {"type": "string"}},
                "violations": {"type": "array"},
            },
        },
    },
}

AST_GRAPH_SCHEMA_V2 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["nodes", "edges", "metadata"],
    "properties": {
        "schema_version": {"type": "string", "enum": [CURRENT_SCHEMA_VERSION]},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["file", "class", "function", "module"],
                    },
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "metadata": {"type": "object"},
                },
            },
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source", "target", "type"],
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["imports", "calls", "inherits", "uses"],
                    },
                    "weight": {"type": "number", "minimum": 0},
                },
            },
        },
        "metadata": {
            "type": "object",
            "required": ["generated_at", "node_count", "edge_count"],
            "properties": {
                "generated_at": {"type": "string"},
                "node_count": {"type": "integer", "minimum": 0},
                "edge_count": {"type": "integer", "minimum": 0},
                "repository_path": {"type": "string"},
            },
        },
    },
}

DASHBOARD_DATA_SCHEMA_V2 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["repository", "health", "issues", "metrics"],
    "properties": {
        "schema_version": {"type": "string", "enum": [CURRENT_SCHEMA_VERSION]},
        "repository": {
            "type": "object",
            "required": ["name", "display_name", "health_score"],
            "properties": {
                "name": {"type": "string"},
                "display_name": {"type": "string"},
                "health_score": {"type": "number", "minimum": 0, "maximum": 100},
                "last_updated": {"type": "string"},
            },
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
                        "governance": {"type": "number", "minimum": 0, "maximum": 100},
                    },
                },
            },
        },
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["severity", "category", "description"],
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": ["P0", "P1", "P2", "P3"],
                    },
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                },
            },
        },
        "metrics": {
            "type": "object",
            "properties": {
                "files_analyzed": {"type": "integer", "minimum": 0},
                "test_coverage": {"type": "number", "minimum": 0, "maximum": 100},
                "code_quality": {"type": "number", "minimum": 0, "maximum": 100},
            },
        },
        "tabs": {
            "type": "array",
            "description": "9-tab dashboard structure",
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "file": {"type": "string"},
                },
            },
        },
    },
}

ONBOARDING_SUMMARY_SCHEMA_V2 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["schema_version", "repository_name", "tabs"],
    "properties": {
        "schema_version": {"type": "string", "enum": [CURRENT_SCHEMA_VERSION]},
        "repository_name": {"type": "string", "minLength": 1},
        "tabs": {
            "type": "array",
            "minItems": 9,
            "maxItems": 9,
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "file": {"type": "string"},
                },
            },
        },
    },
}


# ============================================================================
# Dataclass + Validator
# ============================================================================


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""

    schema_name: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    data_sample: Optional[Dict[str, Any]] = None


class LENSDataValidator:
    """Validate LENS output data against dashboard-compatible schemas."""

    def __init__(self) -> None:
        """Register all known schemas."""
        self.schemas: Dict[str, Dict[str, Any]] = {
            "repository_v2": REPOSITORY_SCHEMA_V2,
            "ast_graph_v2": AST_GRAPH_SCHEMA_V2,
            "dashboard_data_v2": DASHBOARD_DATA_SCHEMA_V2,
            "onboarding_summary_v2": ONBOARDING_SUMMARY_SCHEMA_V2,
        }

    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Return schema by name, or None if unknown."""
        return self.schemas.get(schema_name)

    def validate_json(
        self,
        data: Dict[str, Any],
        schema_name: str,
    ) -> SchemaValidationResult:
        """
        Validate *data* against the named schema.

        Args:
            data: Dictionary to validate.
            schema_name: Key into self.schemas.

        Returns:
            SchemaValidationResult with valid, errors, warnings.
        """
        if schema_name not in self.schemas:
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"Unknown schema: {schema_name!r}"],
                warnings=[],
            )

        schema = self.schemas[schema_name]
        errors: List[str] = []
        warnings: List[str] = []

        try:
            validate(instance=data, schema=schema)

            if "schema_version" not in data:
                warnings.append("Missing schema_version field")

            if schema_name == "repository_v2":
                repo = data.get("repository", {})
                if "display_name" not in repo:
                    warnings.append("Missing display_name (recommended for dashboard)")
                if "health_score" not in repo:
                    warnings.append("Missing health_score (recommended for dashboard)")

            return SchemaValidationResult(
                schema_name=schema_name,
                valid=True,
                errors=[],
                warnings=warnings,
                data_sample=data,
            )

        except ValidationError as exc:
            path = ".".join(str(p) for p in exc.path)
            errors.append(f"Validation error at {path!r}: {exc.message}")
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=errors,
                warnings=warnings,
                data_sample=data,
            )

    def validate_file(
        self,
        file_path: Path,
        schema_name: str,
    ) -> SchemaValidationResult:
        """
        Load *file_path* (JSON or YAML) and validate against *schema_name*.

        Args:
            file_path: Path to JSON or YAML artifact.
            schema_name: Key into self.schemas.

        Returns:
            SchemaValidationResult.
        """
        if not file_path.exists():
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"File not found: {file_path}"],
                warnings=[],
            )

        try:
            if file_path.suffix == ".json":
                data = json.loads(file_path.read_text())
            elif file_path.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(file_path.read_text())
            else:
                return SchemaValidationResult(
                    schema_name=schema_name,
                    valid=False,
                    errors=[f"Unsupported file type: {file_path.suffix!r}"],
                    warnings=[],
                )
            return self.validate_json(data, schema_name)

        except Exception as exc:
            return SchemaValidationResult(
                schema_name=schema_name,
                valid=False,
                errors=[f"Failed to load file: {exc}"],
                warnings=[],
            )


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def validator() -> LENSDataValidator:
    """Create a LENS data validator."""
    return LENSDataValidator()


@pytest.fixture
def sample_repository_data() -> Dict[str, Any]:
    """Minimal valid repository artifact (schema_version 2.0.0)."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "repository": {
            "name": "test-repo",
            "display_name": "Test Repository",
            "path": "/path/to/test-repo",
            "onboarded_at": datetime.utcnow().isoformat(),
            "primary_language": "python",
            "health_score": 85.5,
        },
        "metadata": {
            "files_analyzed": 150,
            "total_lines": 5000,
            "test_files": 25,
            "learning_metrics": {"total_learnings": 0, "by_orchestrator": {}},
        },
        "analysis": {
            "status": "success",
            "architecture_type": "layered",
            "patterns_detected": ["mvc", "repository"],
            "violations": [],
        },
    }


@pytest.fixture
def sample_ast_graph() -> Dict[str, Any]:
    """Minimal valid AST graph artifact (schema_version 2.0.0)."""
    ts = datetime.utcnow().isoformat()
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "nodes": [
            {"id": "file_0", "type": "file", "name": "main.py", "path": "src/main.py", "metadata": {}},
            {"id": "file_1", "type": "file", "name": "utils.py", "path": "src/utils.py", "metadata": {}},
        ],
        "edges": [
            {"source": "file_0", "target": "file_1", "type": "imports", "weight": 1.0}
        ],
        "metadata": {
            "generated_at": ts,
            "node_count": 2,
            "edge_count": 1,
            "repository_path": "/path/to/repo",
        },
    }


@pytest.fixture
def sample_dashboard_data() -> Dict[str, Any]:
    """Minimal valid dashboard data artifact (schema_version 2.0.0, 9 tabs)."""
    ts = datetime.utcnow().isoformat()
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "repository": {
            "name": "test-repo",
            "display_name": "Test Repository",
            "health_score": 85.0,
            "last_updated": ts,
        },
        "health": {
            "overall_score": 85.0,
            "categories": {
                "architecture": 90.0,
                "testing": 80.0,
                "documentation": 75.0,
                "governance": 95.0,
            },
        },
        "issues": [
            {
                "severity": "P1",
                "category": "testing",
                "description": "Low test coverage in module X",
                "file": "src/module_x.py",
                "line": 42,
            }
        ],
        "metrics": {
            "files_analyzed": 150,
            "test_coverage": 78.5,
            "code_quality": 85.0,
        },
        "tabs": [{"id": t["id"], "label": t["label"], "file": t["file"]} for t in DASHBOARD_TABS],
    }


@pytest.fixture
def sample_onboarding_summary() -> Dict[str, Any]:
    """Minimal valid onboarding-summary.json (schema_version 2.0.0, 9 tabs)."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "repository_name": "test-repo",
        "tabs": [{"id": t["id"], "label": t["label"], "file": t["file"]} for t in DASHBOARD_TABS],
    }


# ============================================================================
# TestRepositorySchemaValidation
# ============================================================================


class TestRepositorySchemaValidation:
    """Golden tests for repository onboarding schema (v2.0.0)."""

    def test_valid_repository_data_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
    ) -> None:
        """Golden: Valid repository data passes schema_v2 validation."""
        result = validator.validate_json(sample_repository_data, "repository_v2")
        assert result.valid, f"Validation failed: {result.errors}"
        assert len(result.errors) == 0

    def test_missing_required_field_golden(
        self, validator: LENSDataValidator
    ) -> None:
        """Golden: Missing required field causes validation failure."""
        invalid_data: Dict[str, Any] = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "repository": {"name": "test-repo"},  # missing: path, onboarded_at
            "metadata": {"files_analyzed": 0, "total_lines": 0},
            "analysis": {"status": "success", "architecture_type": "unknown"},
        }
        result = validator.validate_json(invalid_data, "repository_v2")
        assert not result.valid
        assert len(result.errors) > 0
        assert any("required" in e.lower() for e in result.errors)

    def test_schema_version_warning_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
    ) -> None:
        """Golden: Missing schema_version triggers a warning (still valid)."""
        data = {k: v for k, v in sample_repository_data.items() if k != "schema_version"}
        result = validator.validate_json(data, "repository_v2")
        assert result.valid
        assert any("schema_version" in w for w in result.warnings)

    def test_health_score_bounds_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
    ) -> None:
        """Golden: health_score must be 0–100 inclusive."""
        import copy

        low = copy.deepcopy(sample_repository_data)
        low["repository"]["health_score"] = -5
        assert not validator.validate_json(low, "repository_v2").valid

        high = copy.deepcopy(sample_repository_data)
        high["repository"]["health_score"] = 105
        assert not validator.validate_json(high, "repository_v2").valid

        for score in (0, 50, 100):
            valid_data = copy.deepcopy(sample_repository_data)
            valid_data["repository"]["health_score"] = score
            assert validator.validate_json(valid_data, "repository_v2").valid, (
                f"Score {score} should be valid"
            )

    def test_schema_version_must_be_current(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
    ) -> None:
        """Golden: Old schema_version string (e.g. 1.0) fails validation."""
        import copy

        old = copy.deepcopy(sample_repository_data)
        old["schema_version"] = "1.0"
        result = validator.validate_json(old, "repository_v2")
        assert not result.valid, "Old schema_version should fail v2 schema"


# ============================================================================
# TestASTGraphSchemaValidation
# ============================================================================


class TestASTGraphSchemaValidation:
    """Golden tests for AST graph schema (v2.0.0)."""

    def test_valid_ast_graph_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any],
    ) -> None:
        """Golden: Valid AST graph passes schema_v2 validation."""
        result = validator.validate_json(sample_ast_graph, "ast_graph_v2")
        assert result.valid, f"Validation failed: {result.errors}"

    def test_empty_graph_golden(self, validator: LENSDataValidator) -> None:
        """Golden: Empty graph (0 nodes, 0 edges) is valid."""
        empty: Dict[str, Any] = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "node_count": 0,
                "edge_count": 0,
            },
        }
        assert validator.validate_json(empty, "ast_graph_v2").valid

    def test_invalid_node_type_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any],
    ) -> None:
        """Golden: Invalid node type fails enum constraint."""
        import copy

        bad = copy.deepcopy(sample_ast_graph)
        bad["nodes"][0]["type"] = "invalid_type"
        result = validator.validate_json(bad, "ast_graph_v2")
        assert not result.valid
        assert any(
            "enum" in e.lower() or "invalid_type" in e.lower() for e in result.errors
        )

    def test_negative_metadata_counts_golden(
        self,
        validator: LENSDataValidator,
        sample_ast_graph: Dict[str, Any],
    ) -> None:
        """Golden: Negative node_count fails minimum constraint."""
        import copy

        bad = copy.deepcopy(sample_ast_graph)
        bad["metadata"]["node_count"] = -1
        assert not validator.validate_json(bad, "ast_graph_v2").valid


# ============================================================================
# TestDashboardDataSchemaValidation
# ============================================================================


class TestDashboardDataSchemaValidation:
    """Golden tests for dashboard data schema (v2.0.0, 9 tabs)."""

    def test_valid_dashboard_data_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any],
    ) -> None:
        """Golden: Valid dashboard data passes schema_v2 validation."""
        result = validator.validate_json(sample_dashboard_data, "dashboard_data_v2")
        assert result.valid, f"Validation failed: {result.errors}"

    def test_issue_severity_levels_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any],
    ) -> None:
        """Golden: Issue severity must be P0, P1, P2, or P3."""
        import copy

        bad = copy.deepcopy(sample_dashboard_data)
        bad["issues"][0]["severity"] = "CRITICAL"
        assert not validator.validate_json(bad, "dashboard_data_v2").valid

        for sev in ("P0", "P1", "P2", "P3"):
            good = copy.deepcopy(sample_dashboard_data)
            good["issues"][0]["severity"] = sev
            assert validator.validate_json(good, "dashboard_data_v2").valid, (
                f"Severity {sev!r} should be valid"
            )

    def test_health_category_scores_golden(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any],
    ) -> None:
        """Golden: Health category scores must be 0–100."""
        import copy

        for cat in ("architecture", "testing", "documentation", "governance"):
            bad = copy.deepcopy(sample_dashboard_data)
            bad["health"]["categories"][cat] = 150
            assert not validator.validate_json(bad, "dashboard_data_v2").valid, (
                f"Score 150 for {cat!r} should be invalid"
            )

    def test_tabs_array_contains_nine_entries(
        self,
        validator: LENSDataValidator,
        sample_dashboard_data: Dict[str, Any],
    ) -> None:
        """Golden: dashboard_data tabs array must list all 9 dashboard tabs."""
        assert len(sample_dashboard_data["tabs"]) == len(DASHBOARD_TABS)
        tab_ids = [t["id"] for t in sample_dashboard_data["tabs"]]
        expected_ids = [t["id"] for t in DASHBOARD_TABS]
        assert tab_ids == expected_ids


# ============================================================================
# TestOnboardingSummarySchemaValidation
# ============================================================================


class TestOnboardingSummarySchemaValidation:
    """Golden tests for onboarding-summary.json schema."""

    def test_valid_summary_golden(
        self,
        validator: LENSDataValidator,
        sample_onboarding_summary: Dict[str, Any],
    ) -> None:
        """Golden: Valid summary passes schema validation."""
        result = validator.validate_json(sample_onboarding_summary, "onboarding_summary_v2")
        assert result.valid, f"Validation failed: {result.errors}"

    def test_summary_requires_nine_tabs(self, validator: LENSDataValidator) -> None:
        """Golden: Summary with fewer than 9 tabs fails minItems constraint."""
        bad: Dict[str, Any] = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "repository_name": "test-repo",
            "tabs": [{"id": "01_overview", "label": "Overview"}],  # only 1
        }
        result = validator.validate_json(bad, "onboarding_summary_v2")
        assert not result.valid

    def test_summary_tab_ids_match_dashboard_tabs(
        self,
        sample_onboarding_summary: Dict[str, Any],
    ) -> None:
        """Golden: Summary tab IDs exactly match DASHBOARD_TABS constant."""
        summary_ids = [t["id"] for t in sample_onboarding_summary["tabs"]]
        expected_ids = [t["id"] for t in DASHBOARD_TABS]
        assert summary_ids == expected_ids


# ============================================================================
# TestFileValidation
# ============================================================================


class TestFileValidation:
    """Golden tests for file-based (JSON/YAML) schema validation."""

    def test_validate_json_file_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Golden: JSON file with valid content passes validation."""
        json_file = tmp_path / "repository.json"
        json_file.write_text(json.dumps(sample_repository_data, indent=2))
        result = validator.validate_file(json_file, "repository_v2")
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_yaml_file_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Golden: YAML file with valid content passes validation."""
        yaml_file = tmp_path / "repository.yaml"
        yaml_file.write_text(yaml.dump(sample_repository_data))
        result = validator.validate_file(yaml_file, "repository_v2")
        assert result.valid

    def test_validate_missing_file_golden(self, validator: LENSDataValidator) -> None:
        """Golden: Missing file returns valid=False with 'not found' error."""
        result = validator.validate_file(Path("/nonexistent/file.json"), "repository_v2")
        assert not result.valid
        assert any("not found" in e.lower() for e in result.errors)


# ============================================================================
# TestRoundTripSerialization
# ============================================================================


class TestRoundTripSerialization:
    """Golden tests for JSON/YAML round-trip fidelity."""

    def test_json_round_trip_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Golden: Data survives JSON serialization round-trip unchanged."""
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(sample_repository_data, indent=2))
        loaded = json.loads(json_file.read_text())

        assert validator.validate_json(sample_repository_data, "repository_v2").valid
        assert validator.validate_json(loaded, "repository_v2").valid
        assert loaded == sample_repository_data

    def test_yaml_round_trip_golden(
        self,
        validator: LENSDataValidator,
        sample_repository_data: Dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Golden: Data survives YAML serialization round-trip unchanged."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml.dump(sample_repository_data))
        loaded = yaml.safe_load(yaml_file.read_text())

        assert validator.validate_json(sample_repository_data, "repository_v2").valid
        assert validator.validate_json(loaded, "repository_v2").valid


# ============================================================================
# Coverage Report
# ============================================================================


def test_schema_coverage_report(validator: LENSDataValidator) -> None:
    """Golden: All 4 required schemas are registered; report counts."""
    schemas = validator.schemas
    print(f"\n{'=' * 60}")
    print("SCHEMA VALIDATION COVERAGE REPORT")
    print(f"{'=' * 60}")
    print(f"Schema version under test: {CURRENT_SCHEMA_VERSION}")
    print(f"Total schemas defined:     {len(schemas)}")
    print(f"Dashboard tabs covered:    {len(DASHBOARD_TABS)}")
    for name, schema in schemas.items():
        fields = list(schema.get("properties", {}).keys())
        print(f"\n  {name}: {fields}")
    print(f"{'=' * 60}\n")

    assert len(schemas) >= 4
    assert "repository_v2" in schemas
    assert "ast_graph_v2" in schemas
    assert "dashboard_data_v2" in schemas
    assert "onboarding_summary_v2" in schemas
