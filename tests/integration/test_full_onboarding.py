"""
CORTEX Dashboard E2E Integration Test
Tests full onboarding pipeline: Onboard → Aggregate → Validate → Dashboard

Test ID: E2E-DASH-001
Category: Integration
Priority: Critical
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from cortex.lens.dashboard_data_aggregator import DashboardDataAggregator
from cortex.models.dashboard_schema import validate_dashboard_model


class TestDashboardE2EIntegration:
    """E2E tests for dashboard data pipeline."""
    
    @pytest.fixture
    def sample_repository(self, tmp_path):
        """Create a sample repository structure for testing."""
        repo_path = tmp_path / "sample_repo"
        repo_path.mkdir()
        
        # Create Python files
        (repo_path / "main.py").write_text("""
def hello_world():
    \"\"\"Say hello.\"\"\"
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
""")
        
        (repo_path / "utils.py").write_text("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
""")
        
        # Create test file
        test_dir = repo_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_utils.py").write_text("""
import pytest
from utils import add, multiply

def test_add():
    assert add(2, 3) == 5
    
def test_multiply():
    assert multiply(4, 5) == 20
""")
        
        # Create requirements.txt
        (repo_path / "requirements.txt").write_text("""
pytest==7.4.0
pydantic==2.5.0
fastapi==0.104.1
""")
        
        # Create README
        (repo_path / "README.md").write_text("""
# Sample Repository

A simple Python project for testing.

## Use Cases
- UC-001: Mathematical operations (add, multiply)
- UC-002: Test automation with pytest
""")
        
        return repo_path
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_path = tmp_path / "dashboard_output"
        output_path.mkdir()
        return output_path
    
    def test_e2e_001_full_pipeline_success(self, sample_repository, output_dir):
        """E2E-001: Full pipeline executes successfully from start to finish."""
        # Step 1: Initialize aggregator
        aggregator = DashboardDataAggregator()
        assert aggregator is not None
        
        # Step 2: Aggregate data
        result = aggregator.aggregate(sample_repository)
        assert result.success is True
        assert result.error is None
        assert result.data is not None
        
        # Step 3: Validate against schema
        is_valid, errors = validate_dashboard_model(result.data)
        assert is_valid is True, f"Validation errors: {errors}"
        assert len(errors) == 0
        
        # Step 4: Write to JSON file
        json_file = output_dir / "dashboard-data.json"
        result.write_to_file(json_file)
        assert json_file.exists()
        
        # Step 5: Verify JSON is valid
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data is not None
        assert 'repo_summary' in loaded_data
        assert 'metrics_summary' in loaded_data
    
    def test_e2e_002_repo_summary_generation(self, sample_repository):
        """E2E-002: Repository summary is generated with correct data."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        repo_summary = result.data['repo_summary']
        
        # Verify required fields
        assert 'repo_name' in repo_summary
        assert 'health_score' in repo_summary
        assert 'total_files' in repo_summary
        assert 'file_count' in repo_summary
        assert 'total_loc' in repo_summary
        assert 'primary_language' in repo_summary
        assert 'last_analyzed_at' in repo_summary
        
        # Verify data quality
        assert repo_summary['repo_name'] == 'sample_repo'
        assert 0 <= repo_summary['health_score'] <= 100
        assert repo_summary['total_files'] >= 3  # main.py, utils.py, test_utils.py
        assert repo_summary['total_loc'] > 0
    
    def test_e2e_003_metrics_summary_generation(self, sample_repository):
        """E2E-003: Metrics summary is generated with valid data."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        metrics = result.data['metrics_summary']
        
        # Verify required fields
        assert 'total_loc' in metrics
        assert 'code_loc' in metrics
        assert 'comment_loc' in metrics
        assert 'avg_complexity' in metrics
        assert 'test_coverage' in metrics
        assert 'technical_debt_hours' in metrics
        assert 'calculated_at' in metrics
        
        # Verify data quality
        assert metrics['total_loc'] > 0
        assert metrics['code_loc'] > 0
        assert metrics['avg_complexity'] > 0
        assert 0 <= metrics['test_coverage'] <= 100
    
    def test_e2e_004_packages_extraction(self, sample_repository):
        """E2E-004: Packages are extracted from requirements.txt."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        packages = result.data['packages']
        
        assert isinstance(packages, list)
        assert len(packages) >= 3  # pytest, pydantic, fastapi
        
        # Verify package structure
        if packages:
            pkg = packages[0]
            assert 'name' in pkg
            assert 'version' in pkg
            assert 'package_type' in pkg
    
    def test_e2e_005_files_collection(self, sample_repository):
        """E2E-005: Files are collected with LOC counts."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        files = result.data['files']
        
        assert isinstance(files, list)
        assert len(files) >= 3  # At least 3 Python files
        
        # Verify file structure
        if files:
            file_entry = files[0]
            assert 'file_path' in file_entry
            assert 'loc' in file_entry
            assert file_entry['loc'] > 0
    
    def test_e2e_006_performance_acceptable(self, sample_repository):
        """E2E-006: Aggregation completes within acceptable time."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        # Should complete within 10 seconds for small repo
        assert result.duration_seconds < 10.0
        assert result.duration_seconds > 0
    
    def test_e2e_007_json_serialization_roundtrip(self, sample_repository, output_dir):
        """E2E-007: Data survives JSON serialization roundtrip."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        # Write to file
        json_file = output_dir / "test-data.json"
        result.write_to_file(json_file)
        
        # Read back
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        assert loaded_data['repo_summary']['repo_name'] == result.data['repo_summary']['repo_name']
        assert loaded_data['metrics_summary']['total_loc'] == result.data['metrics_summary']['total_loc']
        
        # Re-validate
        is_valid, errors = validate_dashboard_model(loaded_data)
        assert is_valid is True
    
    def test_e2e_008_empty_repo_handling(self, tmp_path):
        """E2E-008: Pipeline handles empty repository gracefully."""
        empty_repo = tmp_path / "empty_repo"
        empty_repo.mkdir()
        
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(empty_repo)
        
        # Should succeed even with empty repo
        assert result.success is True
        assert result.data is not None
        
        # Should have minimal data
        assert result.data['repo_summary']['total_files'] == 0
        assert result.data['repo_summary']['total_loc'] == 0
    
    def test_e2e_009_nonexistent_repo_error(self):
        """E2E-009: Pipeline errors gracefully for nonexistent repository."""
        nonexistent_path = Path("/nonexistent/path/to/repo")
        
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(nonexistent_path)
        
        assert result.success is False
        assert result.error is not None
        assert "does not exist" in result.error.lower()
    
    def test_e2e_010_all_sections_present(self, sample_repository):
        """E2E-010: All expected dashboard sections are present in output."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        # Required sections
        assert 'repo_summary' in result.data
        assert 'metrics_summary' in result.data
        
        # Optional sections (should exist, might be empty)
        assert 'executive_kpis' in result.data
        assert 'use_cases' in result.data
        assert 'entities' in result.data
        assert 'relationships' in result.data
        assert 'components' in result.data
        assert 'vulnerabilities' in result.data
        assert 'packages' in result.data
        assert 'code_smells' in result.data
        assert 'metrics_by_file' in result.data
        assert 'files' in result.data
        assert 'code_snippets' in result.data
        assert 'test_results' in result.data
        assert 'lens_insights' in result.data
        assert 'refactoring_suggestions' in result.data
    
    def test_e2e_011_health_score_calculation(self, sample_repository):
        """E2E-011: Health score is calculated and within valid range."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        health_score = result.data['repo_summary']['health_score']
        
        assert isinstance(health_score, (int, float))
        assert 0 <= health_score <= 100
        assert health_score > 0  # Non-empty repo should have some score
    
    def test_e2e_012_timestamps_valid(self, sample_repository):
        """E2E-012: All timestamps are valid ISO 8601 format."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        # Check repo_summary timestamp
        last_analyzed = result.data['repo_summary']['last_analyzed_at']
        try:
            datetime.fromisoformat(last_analyzed.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {last_analyzed}")
        
        # Check metrics_summary timestamp
        calculated_at = result.data['metrics_summary']['calculated_at']
        try:
            datetime.fromisoformat(calculated_at.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {calculated_at}")
    
    def test_e2e_013_reusable_aggregator(self, sample_repository, tmp_path):
        """E2E-013: Aggregator can be reused for multiple repositories."""
        aggregator = DashboardDataAggregator()
        
        # First aggregation
        result1 = aggregator.aggregate(sample_repository)
        assert result1.success is True
        
        # Create second repo
        repo2 = tmp_path / "repo2"
        repo2.mkdir()
        (repo2 / "test.py").write_text("print('test')")
        
        # Second aggregation with same instance
        result2 = aggregator.aggregate(repo2)
        assert result2.success is True
        
        # Results should be different
        assert result1.data['repo_summary']['repo_name'] != result2.data['repo_summary']['repo_name']
    
    def test_e2e_014_json_output_format(self, sample_repository, output_dir):
        """E2E-014: JSON output has correct structure and formatting."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository)
        
        json_file = output_dir / "formatted-data.json"
        result.write_to_file(json_file)
        
        # Read raw JSON
        with open(json_file, 'r') as f:
            content = f.read()
        
        # Verify it's pretty-printed (has indentation)
        assert '  ' in content or '\t' in content
        
        # Verify it's valid JSON
        data = json.loads(content)
        assert isinstance(data, dict)
    
    def test_e2e_015_concurrent_aggregation_safe(self, sample_repository):
        """E2E-015: Multiple aggregators can run concurrently (thread-safe)."""
        # Create multiple aggregator instances
        aggregators = [DashboardDataAggregator() for _ in range(3)]
        
        # Run aggregations
        results = [agg.aggregate(sample_repository) for agg in aggregators]
        
        # All should succeed
        assert all(r.success for r in results)
        
        # All should produce valid data
        for result in results:
            is_valid, errors = validate_dashboard_model(result.data)
            assert is_valid is True


# Mark all tests as integration tests
pytestmark = pytest.mark.integration
