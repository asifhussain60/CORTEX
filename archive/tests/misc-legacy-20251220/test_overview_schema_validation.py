"""
Tests for Overview Schema Validation

Test suite for validating overview.json data against the schema.
TDD Phase: RED - Write failing tests first.
"""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError


@pytest.fixture
def overview_schema():
    """Load the overview schema."""
    schema_path = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "schema" / "overview-schema-v1.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def valid_overview_data():
    """Valid overview data for testing."""
    return {
        "project_name": "CORTEX",
        "overall_health": {
            "score": 92,
            "status": "healthy",
            "trend": "improving",
            "last_scan": "2025-12-06T15:30:00.000000"
        },
        "key_metrics": {
            "total_files": 994,
            "total_loc": 45678,
            "test_coverage": 78.5,
            "maintainability_index": 85
        },
        "health_categories": [
            {
                "name": "code_quality",
                "score": 88,
                "status": "healthy",
                "trend": "improving",
                "issues_count": 3,
                "details": "3 minor code quality issues"
            }
        ],
        "critical_issues": [],
        "composition": {
            "languages": [
                {
                    "name": "Python",
                    "percentage": 75.2,
                    "loc": 34340
                }
            ],
            "components": [
                {
                    "type": "backend",
                    "count": 4,
                    "technologies": ["SQLite", "Python"]
                }
            ]
        },
        "trends": {
            "health_trend": "improving",
            "velocity_trend": "stable",
            "quality_trend": "improving"
        }
    }


def test_valid_overview_data_passes_validation(overview_schema, valid_overview_data):
    """Test that valid overview data passes schema validation."""
    validate(instance=valid_overview_data, schema=overview_schema)


def test_missing_required_field_fails_validation(overview_schema, valid_overview_data):
    """Test that missing required fields fail validation."""
    del valid_overview_data["project_name"]
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_invalid_health_score_fails_validation(overview_schema, valid_overview_data):
    """Test that health score outside 0-100 range fails validation."""
    valid_overview_data["overall_health"]["score"] = 150
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_invalid_status_enum_fails_validation(overview_schema, valid_overview_data):
    """Test that invalid status value fails validation."""
    valid_overview_data["overall_health"]["status"] = "invalid"
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_invalid_trend_enum_fails_validation(overview_schema, valid_overview_data):
    """Test that invalid trend value fails validation."""
    valid_overview_data["overall_health"]["trend"] = "unknown"
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_negative_metrics_fail_validation(overview_schema, valid_overview_data):
    """Test that negative metric values fail validation."""
    valid_overview_data["key_metrics"]["total_files"] = -1
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_test_coverage_over_100_fails_validation(overview_schema, valid_overview_data):
    """Test that test coverage over 100% fails validation."""
    valid_overview_data["key_metrics"]["test_coverage"] = 150
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_empty_health_categories_fails_validation(overview_schema, valid_overview_data):
    """Test that empty health categories array fails validation."""
    valid_overview_data["health_categories"] = []
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_invalid_health_category_name_fails_validation(overview_schema, valid_overview_data):
    """Test that invalid health category name fails validation."""
    valid_overview_data["health_categories"][0]["name"] = "invalid_category"
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_critical_issue_with_invalid_severity_fails_validation(overview_schema, valid_overview_data):
    """Test that critical issue with invalid severity fails validation."""
    valid_overview_data["critical_issues"] = [
        {
            "severity": "low",  # Only 'critical' and 'high' are valid
            "category": "security",
            "message": "Test issue",
            "count": 1
        }
    ]
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_empty_languages_array_fails_validation(overview_schema, valid_overview_data):
    """Test that empty languages array fails validation."""
    valid_overview_data["composition"]["languages"] = []
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_language_percentage_over_100_fails_validation(overview_schema, valid_overview_data):
    """Test that language percentage over 100 fails validation."""
    valid_overview_data["composition"]["languages"][0]["percentage"] = 150
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_invalid_component_type_fails_validation(overview_schema, valid_overview_data):
    """Test that invalid component type fails validation."""
    valid_overview_data["composition"]["components"][0]["type"] = "invalid_type"
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_missing_trends_field_fails_validation(overview_schema, valid_overview_data):
    """Test that missing trends object fails validation."""
    del valid_overview_data["trends"]
    with pytest.raises(ValidationError):
        validate(instance=valid_overview_data, schema=overview_schema)


def test_optional_technical_debt_field_allowed(overview_schema, valid_overview_data):
    """Test that optional technical_debt_hours field is allowed."""
    valid_overview_data["key_metrics"]["technical_debt_hours"] = 12.5
    validate(instance=valid_overview_data, schema=overview_schema)
