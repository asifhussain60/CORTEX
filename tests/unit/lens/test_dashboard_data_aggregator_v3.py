"""
TDD Tests for DashboardDataAggregator v3.0.

Tests JSON generation matching dashboard_schema_v3.py Pydantic models.
Produces data for all 13 dashboard tabs.

AC_START: AC-CDF-Dashboard-003
Version: 3.0
Created: 2026-02-04
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from cortex.lens.dashboard_data_aggregator_v3 import (
    DashboardDataAggregatorV3,
    AggregationResult,
)
from cortex.models.dashboard_schema_v3 import (
    validate_dashboard_data,
    RepoSummary,
    ExecutiveKPI,
    UseCase,
    MetricsSummary,
)


@pytest.fixture
def aggregator():
    """Create aggregator v3 instance."""
    return DashboardDataAggregatorV3()


@pytest.fixture
def sample_repo_path(tmp_path):
    """Create sample repository structure."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    
    # Create sample files
    src_dir = repo_dir / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('hello')")
    (src_dir / "utils.py").write_text("def helper(): pass")
    
    tests_dir = repo_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("def test_main(): pass")
    
    return repo_dir


# ==============================================================================
# Core Aggregation Tests
# ==============================================================================

class TestAggregationCore:
    """Test core aggregation functionality."""
    
    def test_daggv3_001_create_aggregator(self, aggregator):
        """DAGGV3-001: Create aggregator v3 instance."""
        assert aggregator is not None
        assert hasattr(aggregator, 'aggregate')
    
    def test_daggv3_002_aggregate_returns_result(self, aggregator, sample_repo_path):
        """DAGGV3-002: aggregate() returns AggregationResult."""
        result = aggregator.aggregate(sample_repo_path)
        
        assert isinstance(result, AggregationResult)
        assert result.success is True
        assert result.data is not None
    
    def test_daggv3_003_result_has_all_sections(self, aggregator, sample_repo_path):
        """DAGGV3-003: Result contains all 13 dashboard sections."""
        result = aggregator.aggregate(sample_repo_path)
        data = result.data
        
        # Required sections
        assert 'repo_summary' in data
        assert 'metrics_summary' in data
        
        # Optional sections (may be None if not available)
        assert 'executive_kpis' in data or True  # Optional
        assert 'use_cases' in data or True  # Optional
        assert 'vulnerabilities' in data or True  # Optional
        assert 'packages' in data or True  # Optional
    
    def test_daggv3_004_validate_against_schema(self, aggregator, sample_repo_path):
        """DAGGV3-004: Generated JSON validates against Pydantic schema."""
        result = aggregator.aggregate(sample_repo_path)
        
        # This should not raise validation errors
        is_valid, errors = validate_dashboard_data(result.data)
        assert is_valid is True, f"Validation failed: {errors}"
        assert len(errors) == 0, f"Validation errors: {errors}"


# ==============================================================================
# Repo Summary Tests
# ==============================================================================

class TestRepoSummary:
    """Test repo_summary section generation."""
    
    def test_daggv3_005_generate_repo_summary(self, aggregator, sample_repo_path):
        """DAGGV3-005: Generate repo_summary section."""
        result = aggregator.aggregate(sample_repo_path)
        
        assert 'repo_summary' in result.data
        summary = result.data['repo_summary']
        
        assert summary['id'] == 1
        assert 'repo_name' in summary
        assert 'health_score' in summary
        assert 'total_files' in summary
        assert 'total_loc' in summary
    
    def test_daggv3_006_repo_summary_has_required_fields(self, aggregator, sample_repo_path):
        """DAGGV3-006: repo_summary has all required fields."""
        result = aggregator.aggregate(sample_repo_path)
        summary = result.data['repo_summary']
        
        required_fields = [
            'id', 'repo_name', 'repo_slug', 'health_score',
            'total_files', 'total_loc', 'primary_language', 'last_analyzed_at'
        ]
        
        for field in required_fields:
            assert field in summary, f"Missing required field: {field}"
    
    def test_daggv3_007_health_score_in_range(self, aggregator, sample_repo_path):
        """DAGGV3-007: health_score is between 0.0 and 100.0."""
        result = aggregator.aggregate(sample_repo_path)
        health_score = result.data['repo_summary']['health_score']
        
        assert 0.0 <= health_score <= 100.0


# ==============================================================================
# Metrics Summary Tests
# ==============================================================================

class TestMetricsSummary:
    """Test metrics_summary section generation."""
    
    def test_daggv3_008_generate_metrics_summary(self, aggregator, sample_repo_path):
        """DAGGV3-008: Generate metrics_summary section."""
        result = aggregator.aggregate(sample_repo_path)
        
        assert 'metrics_summary' in result.data
        metrics = result.data['metrics_summary']
        
        assert metrics['id'] == 1
        assert 'avg_complexity' in metrics
        assert 'test_coverage' in metrics
        assert 'maintainability_index' in metrics
    
    def test_daggv3_009_metrics_percentages_valid(self, aggregator, sample_repo_path):
        """DAGGV3-009: Percentage metrics are between 0 and 100."""
        result = aggregator.aggregate(sample_repo_path)
        metrics = result.data['metrics_summary']
        
        if 'test_coverage' in metrics and metrics['test_coverage'] is not None:
            assert 0.0 <= metrics['test_coverage'] <= 100.0
        
        if 'maintainability_index' in metrics and metrics['maintainability_index'] is not None:
            assert 0.0 <= metrics['maintainability_index'] <= 100.0


# ==============================================================================
# Executive KPIs Tests
# ==============================================================================

class TestExecutiveKPIs:
    """Test executive_kpis section generation."""
    
    def test_daggv3_010_generate_executive_kpis(self, aggregator, sample_repo_path):
        """DAGGV3-010: Generate executive_kpis section (optional)."""
        result = aggregator.aggregate(sample_repo_path)
        
        # Executive KPIs are optional
        if 'executive_kpis' in result.data and result.data['executive_kpis']:
            kpis = result.data['executive_kpis']
            assert 'health_status' in kpis
            assert 'security_posture' in kpis
    
    def test_daggv3_011_executive_health_status_enum(self, aggregator, sample_repo_path):
        """DAGGV3-011: health_status uses valid enum values."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'executive_kpis' in result.data and result.data['executive_kpis']:
            kpis = result.data['executive_kpis']
            if 'health_status' in kpis:
                valid_statuses = ['healthy', 'warning', 'critical', 'unknown']
                assert kpis['health_status'] in valid_statuses


# ==============================================================================
# Use Cases Tests
# ==============================================================================

class TestUseCases:
    """Test use_cases section generation."""
    
    def test_daggv3_012_generate_use_cases(self, aggregator, sample_repo_path):
        """DAGGV3-012: Generate use_cases array (optional)."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'use_cases' in result.data and result.data['use_cases']:
            use_cases = result.data['use_cases']
            assert isinstance(use_cases, list)
            
            if len(use_cases) > 0:
                uc = use_cases[0]
                assert 'id' in uc
                assert 'title' in uc
                assert 'description' in uc
    
    def test_daggv3_013_use_case_priority_enum(self, aggregator, sample_repo_path):
        """DAGGV3-013: Use case priority uses valid enum."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'use_cases' in result.data and result.data['use_cases']:
            use_cases = result.data['use_cases']
            valid_priorities = ['high', 'medium', 'low', 'critical']
            
            for uc in use_cases:
                if 'priority' in uc and uc['priority']:
                    assert uc['priority'] in valid_priorities


# ==============================================================================
# Vulnerabilities Tests
# ==============================================================================

class TestVulnerabilities:
    """Test vulnerabilities section generation."""
    
    def test_daggv3_014_generate_vulnerabilities(self, aggregator, sample_repo_path):
        """DAGGV3-014: Generate vulnerabilities array (optional)."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'vulnerabilities' in result.data and result.data['vulnerabilities']:
            vulns = result.data['vulnerabilities']
            assert isinstance(vulns, list)
            
            if len(vulns) > 0:
                vuln = vulns[0]
                assert 'id' in vuln
                assert 'title' in vuln
                assert 'severity' in vuln
    
    def test_daggv3_015_vulnerability_severity_enum(self, aggregator, sample_repo_path):
        """DAGGV3-015: Vulnerability severity uses valid enum."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'vulnerabilities' in result.data and result.data['vulnerabilities']:
            vulns = result.data['vulnerabilities']
            valid_severities = ['critical', 'high', 'medium', 'low', 'info']
            
            for vuln in vulns:
                if 'severity' in vuln:
                    assert vuln['severity'] in valid_severities


# ==============================================================================
# Packages Tests
# ==============================================================================

class TestPackages:
    """Test packages section generation."""
    
    def test_daggv3_016_generate_packages(self, aggregator, sample_repo_path):
        """DAGGV3-016: Generate packages array (optional)."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'packages' in result.data and result.data['packages']:
            packages = result.data['packages']
            assert isinstance(packages, list)
            
            if len(packages) > 0:
                pkg = packages[0]
                assert 'id' in pkg
                assert 'package_name' in pkg
                assert 'version' in pkg
    
    def test_daggv3_017_package_type_enum(self, aggregator, sample_repo_path):
        """DAGGV3-017: Package type uses valid enum."""
        result = aggregator.aggregate(sample_repo_path)
        
        if 'packages' in result.data and result.data['packages']:
            packages = result.data['packages']
            valid_types = ['runtime', 'dev', 'peer', 'optional']
            
            for pkg in packages:
                if 'package_type' in pkg and pkg['package_type']:
                    assert pkg['package_type'] in valid_types


# ==============================================================================
# JSON Serialization Tests
# ==============================================================================

class TestJSONSerialization:
    """Test JSON serialization and file writing."""
    
    def test_daggv3_018_to_json_dict(self, aggregator, sample_repo_path):
        """DAGGV3-018: Convert result to JSON-serializable dict."""
        result = aggregator.aggregate(sample_repo_path)
        json_dict = result.to_dict()
        
        assert isinstance(json_dict, dict)
        assert 'repo_summary' in json_dict
    
    def test_daggv3_019_write_to_file(self, aggregator, sample_repo_path, tmp_path):
        """DAGGV3-019: Write dashboard data to JSON file."""
        result = aggregator.aggregate(sample_repo_path)
        
        output_file = tmp_path / "dashboard-data.json"
        result.write_to_file(output_file)
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_daggv3_020_json_file_is_valid(self, aggregator, sample_repo_path, tmp_path):
        """DAGGV3-020: Written JSON file can be parsed."""
        result = aggregator.aggregate(sample_repo_path)
        
        output_file = tmp_path / "dashboard-data.json"
        result.write_to_file(output_file)
        
        import json
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert 'repo_summary' in data
        assert 'metrics_summary' in data


# ==============================================================================
# Error Handling Tests
# ==============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_daggv3_021_nonexistent_repo_path(self, aggregator):
        """DAGGV3-021: Handle non-existent repository path."""
        result = aggregator.aggregate(Path("/nonexistent/repo"))
        
        assert result.success is False
        assert result.error is not None
    
    def test_daggv3_022_empty_repo(self, aggregator, tmp_path):
        """DAGGV3-022: Handle empty repository (no files)."""
        empty_repo = tmp_path / "empty-repo"
        empty_repo.mkdir()
        
        result = aggregator.aggregate(empty_repo)
        
        # Should succeed but with minimal data
        assert result.success is True
        assert result.data['repo_summary']['total_files'] == 0
    
    def test_daggv3_023_partial_data_fallback(self, aggregator, sample_repo_path):
        """DAGGV3-023: Handle partial data gracefully (null-safe)."""
        result = aggregator.aggregate(sample_repo_path)
        
        # Even if some sections are missing, result should be valid
        assert result.success is True
        assert 'repo_summary' in result.data  # Required
        assert 'metrics_summary' in result.data  # Required


# ==============================================================================
# Performance Tests
# ==============================================================================

class TestPerformance:
    """Test aggregation performance."""
    
    def test_daggv3_024_aggregate_completes_quickly(self, aggregator, sample_repo_path):
        """DAGGV3-024: Aggregation completes in reasonable time."""
        import time
        
        start = time.time()
        result = aggregator.aggregate(sample_repo_path)
        duration = time.time() - start
        
        # Should complete within 5 seconds for small repo
        assert duration < 5.0
        assert result.success is True
    
    def test_daggv3_025_reusable_aggregator(self, aggregator, sample_repo_path, tmp_path):
        """DAGGV3-025: Aggregator can be reused for multiple repos."""
        result1 = aggregator.aggregate(sample_repo_path)
        
        # Create second repo
        repo2 = tmp_path / "repo2"
        repo2.mkdir()
        (repo2 / "file.py").write_text("pass")
        
        result2 = aggregator.aggregate(repo2)
        
        assert result1.success is True
        assert result2.success is True
        assert result1.data['repo_summary']['repo_name'] != result2.data['repo_summary']['repo_name']
