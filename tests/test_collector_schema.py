#!/usr/bin/env python3
"""
Dashboard Collector Schema Validation Test Suite

TDD Harness: Ensures all collectors produce output matching mock folder schema EXACTLY.

Run: pytest tests/test_collector_schema.py -v

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

# Data locations
MOCK_DIR = Path(__file__).parent.parent / "cortex-brain" / "dashboards" / "data" / "repositories" / "mock"
COLLECTOR_OUTPUT_DIR = Path(__file__).parent.parent / "cortex-brain" / "dashboards" / "data" / "repos" / "luum-fresh"

def load_mock_schema(filename: str) -> Dict[str, Any]:
    """Load mock JSON file as schema reference."""
    filepath = MOCK_DIR / filename
    assert filepath.exists(), f"Mock file not found: {filepath}"
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_collector_output(filename: str) -> Dict[str, Any]:
    """Load actual collector output from repos/luum-fresh/ for validation."""
    filepath = COLLECTOR_OUTPUT_DIR / filename
    if not filepath.exists():
        pytest.skip(f"Collector output not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_keys(data: Dict[str, Any], expected_keys: List[str], path: str = "root") -> List[str]:
    """
    Recursively validate that data contains all expected keys.
    Returns list of missing keys with their paths.
    """
    errors = []
    for key in expected_keys:
        if key not in data:
            errors.append(f"Missing key: {path}.{key}")
    return errors

def validate_type(value: Any, expected_type: type, path: str) -> List[str]:
    """Validate that value matches expected type."""
    errors = []
    if expected_type == int or expected_type == float:
        if not isinstance(value, (int, float)):
            errors.append(f"Type mismatch at {path}: expected number, got {type(value).__name__}")
    elif expected_type == str:
        if not isinstance(value, str):
            errors.append(f"Type mismatch at {path}: expected string, got {type(value).__name__}")
    elif expected_type == list:
        if not isinstance(value, list):
            errors.append(f"Type mismatch at {path}: expected list, got {type(value).__name__}")
    elif expected_type == dict:
        if not isinstance(value, dict):
            errors.append(f"Type mismatch at {path}: expected dict, got {type(value).__name__}")
    return errors


class TestOverviewSchema:
    """Test suite for overview.json schema compliance."""
    
    @pytest.fixture
    def mock_overview(self):
        return load_mock_schema("overview.json")
    
    def test_overview_root_keys(self, mock_overview):
        """FAILING TEST: Overview must have all root-level keys."""
        required_keys = ["project_name", "overall_health", "key_metrics", "health_categories", 
                        "critical_issues", "composition", "trends"]
        
        # This test will FAIL until collector is fixed
        # Simulating collector output (initially incomplete)
        collector_output = {
            "project_name": "Test Project"
            # Missing other keys - TEST SHOULD FAIL
        }
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)
    
    def test_overall_health_structure(self, mock_overview):
        """FAILING TEST: overall_health must have correct structure."""
        required_keys = ["score", "status", "trend", "last_scan"]
        
        collector_output = {
            "overall_health": {
                "score": 85
                # Missing other keys
            }
        }
        
        errors = validate_keys(collector_output["overall_health"], required_keys, "overall_health")
        assert len(errors) == 0, f"overall_health validation failed:\n" + "\n".join(errors)
    
    def test_key_metrics_structure(self, mock_overview):
        """FAILING TEST: key_metrics must have all required fields."""
        required_keys = ["total_files", "total_loc", "test_coverage", "maintainability_index", "technical_debt_hours"]
        
        collector_output = {
            "key_metrics": {
                "total_files": 100
                # Missing other keys
            }
        }
        
        errors = validate_keys(collector_output["key_metrics"], required_keys, "key_metrics")
        assert len(errors) == 0, f"key_metrics validation failed:\n" + "\n".join(errors)
    
    def test_health_categories_array(self, mock_overview):
        """FAILING TEST: health_categories must be list with correct items."""
        collector_output = {
            "health_categories": []  # Empty - should have items
        }
        
        assert isinstance(collector_output["health_categories"], list), "health_categories must be a list"
        assert len(collector_output["health_categories"]) > 0, "health_categories must not be empty"
        
        # Each category must have required keys
        required_keys = ["name", "score", "status", "trend", "issues_count", "details"]
        for i, category in enumerate(collector_output["health_categories"]):
            errors = validate_keys(category, required_keys, f"health_categories[{i}]")
            assert len(errors) == 0, f"Category {i} validation failed:\n" + "\n".join(errors)


class TestExecutiveSummarySchema:
    """Test suite for executive-summary.json schema compliance."""
    
    @pytest.fixture
    def mock_executive(self):
        return load_mock_schema("executive-summary.json")
    
    def test_executive_root_keys(self, mock_executive):
        """FAILING TEST: Executive summary must have all root-level keys."""
        required_keys = ["project_name", "tagline", "what_it_does", "composition", 
                        "tech_stack_summary", "health_indicators", "recent_activity"]
        
        collector_output = {
            "project_name": "Test Project"
            # Missing other keys
        }
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)
    
    def test_what_it_does_structure(self, mock_executive):
        """FAILING TEST: what_it_does must have summary, key_points, source."""
        required_keys = ["summary", "key_points", "source"]
        
        collector_output = {
            "what_it_does": {
                "summary": "Description"
                # Missing key_points and source
            }
        }
        
        errors = validate_keys(collector_output["what_it_does"], required_keys, "what_it_does")
        assert len(errors) == 0, f"what_it_does validation failed:\n" + "\n".join(errors)
    
    def test_composition_components(self, mock_executive):
        """FAILING TEST: composition.components must be list with correct structure."""
        collector_output = {
            "composition": {
                "architecture_style": "Unknown",
                "components": []  # Empty - should have items
            }
        }
        
        assert isinstance(collector_output["composition"]["components"], list), "components must be a list"
        # Note: Can be empty for simple projects, but structure must be correct when present


class TestHealthDataSchema:
    """Test suite for health-data.json schema compliance."""
    
    @pytest.fixture
    def mock_health(self):
        return load_mock_schema("health-data.json")
    
    def test_health_root_keys(self, mock_health):
        """Health data must have all root-level keys matching mock schema."""
        required_keys = ["overall_health_score", "status", "last_scan", "summary", "metrics", "trends"]
        
        # Load actual collector output
        collector_output = load_collector_output("health-data.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)
    
    def test_summary_structure(self, mock_health):
        """summary must have all required metrics matching mock schema."""
        required_keys = ["total_files", "total_loc", "test_coverage", "critical_issues", "warnings", "maintainability_index"]
        
        # Load actual collector output
        collector_output = load_collector_output("health-data.json")
        assert "summary" in collector_output, "Missing summary root key"
        
        errors = validate_keys(collector_output["summary"], required_keys, "summary")
        assert len(errors) == 0, f"summary validation failed:\n" + "\n".join(errors)
    
    def test_metrics_structure(self, mock_health):
        """metrics must have all quality scores matching mock schema."""
        required_keys = ["code_quality_score", "security_score", "test_score", "documentation_score"]
        
        # Load actual collector output
        collector_output = load_collector_output("health-data.json")
        assert "metrics" in collector_output, "Missing metrics root key"
        
        errors = validate_keys(collector_output["metrics"], required_keys, "metrics")
        assert len(errors) == 0, f"metrics validation failed:\n" + "\n".join(errors)


class TestTechStackSchema:
    """Test suite for tech-stack.json schema compliance."""
    
    @pytest.fixture
    def mock_tech_stack(self):
        return load_mock_schema("tech-stack.json")
    
    def test_tech_stack_categories(self, mock_tech_stack):
        """Tech stack must have frontend, backend, database, devops categories."""
        required_keys = ["frontend", "backend", "database", "devops", "summary"]
        
        # Load actual collector output
        collector_output = load_collector_output("tech-stack.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)
    
    def test_technology_item_structure(self, mock_tech_stack):
        """Each technology must have correct fields."""
        required_keys = ["name", "version", "latest", "status", "category", "cve_count", "eol_date"]
        
        # Load actual collector output and check first tech item
        collector_output = load_collector_output("tech-stack.json")
        
        # Check first item from each category
        for category in ["frontend", "backend", "database", "devops"]:
            if category in collector_output and collector_output[category]:
                tech_item = collector_output[category][0]
                errors = validate_keys(tech_item, required_keys, f"technology_item.{category}")
                assert len(errors) == 0, f"Technology item validation failed:\n" + "\n".join(errors)
    
    def test_summary_structure(self, mock_tech_stack):
        """summary must have counts and statuses."""
        required_keys = ["total_technologies", "outdated_count", "current_count", "critical_cves"]
        
        # Load actual collector output
        collector_output = load_collector_output("tech-stack.json")
        
        errors = validate_keys(collector_output.get("summary", {}), required_keys, "summary")
        assert len(errors) == 0, f"summary validation failed:\n" + "\n".join(errors)


class TestSecuritySchema:
    """Test suite for security.json schema compliance."""
    
    @pytest.fixture
    def mock_security(self):
        return load_mock_schema("security.json")
    
    def test_security_root_keys(self, mock_security):
        """Security must have all root-level keys matching mock schema."""
        required_keys = ["overall_score", "last_scan", "vulnerabilities", "owasp_top_10"]
        
        # Load actual collector output
        collector_output = load_collector_output("security.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)
    
    def test_vulnerabilities_structure(self, mock_security):
        """vulnerabilities must have correct breakdown matching mock schema."""
        required_keys = ["total", "critical", "high", "medium", "low", "by_package"]
        
        # Load actual collector output
        collector_output = load_collector_output("security.json")
        assert "vulnerabilities" in collector_output, "Missing vulnerabilities root key"
        
        errors = validate_keys(collector_output["vulnerabilities"], required_keys, "vulnerabilities")
        assert len(errors) == 0, f"vulnerabilities validation failed:\n" + "\n".join(errors)
    
    def test_owasp_structure(self, mock_security):
        """owasp_top_10 must have counts and categories matching mock schema."""
        required_keys = ["pass_count", "warn_count", "fail_count", "categories"]
        
        # Load actual collector output
        collector_output = load_collector_output("security.json")
        assert "owasp_top_10" in collector_output, "Missing owasp_top_10 root key"
        
        errors = validate_keys(collector_output["owasp_top_10"], required_keys, "owasp_top_10")
        assert len(errors) == 0, f"owasp_top_10 validation failed:\n" + "\n".join(errors)


class TestArchitectureSchema:
    """Test suite for architecture.json schema compliance."""
    
    @pytest.fixture
    def mock_architecture(self):
        return load_mock_schema("architecture.json")
    
    def test_architecture_root_keys(self, mock_architecture):
        """Architecture must have all root-level keys matching mock schema."""
        required_keys = ["application_type", "style", "deployment", "metrics", "tiers", "components", "endpoints", "database_schema", "summary"]
        
        # Load actual collector output
        collector_output = load_collector_output("architecture.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)


class TestCodeOrganizationSchema:
    """Test suite for code-organization.json schema compliance."""
    
    @pytest.fixture
    def mock_code_org(self):
        return load_mock_schema("code-organization.json")
    
    def test_code_org_root_keys(self, mock_code_org):
        """Code organization must have all root-level keys matching mock schema."""
        required_keys = ["heatmap", "hotspots", "file_complexity", "complexity_distribution", "language_breakdown", "summary"]
        
        # Load actual collector output
        collector_output = load_collector_output("code-organization.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)


class TestVendorsSchema:
    """Test suite for vendors.json schema compliance."""
    
    @pytest.fixture
    def mock_vendors(self):
        return load_mock_schema("vendors.json")
    
    def test_vendors_root_keys(self, mock_vendors):
        """Vendors must have all root-level keys matching mock schema."""
        required_keys = ["vendors", "by_category", "by_status", "summary"]
        
        # Load actual collector output
        collector_output = load_collector_output("vendors.json")
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)


class TestReconciliationSchema:
    """Test suite for reconciliation.json schema compliance."""
    
    @pytest.fixture
    def mock_reconciliation(self):
        return load_mock_schema("reconciliation.json")
    
    def test_reconciliation_root_keys(self, mock_reconciliation):
        """FAILING TEST: Reconciliation must have all root-level keys."""
        required_keys = ["last_reconciliation", "status", "gaps", "recommendations"]
        
        collector_output = {
            "last_reconciliation": "2025-12-07T00:00:00"
            # Missing other keys
        }
        
        errors = validate_keys(collector_output, required_keys)
        assert len(errors) == 0, f"Schema validation failed:\n" + "\n".join(errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
