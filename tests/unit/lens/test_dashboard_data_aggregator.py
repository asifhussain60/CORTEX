"""
TDD Tests for DashboardDataAggregator.

Tests comprehensive dashboard JSON generation for all tabs.

AC_START: AC-CDF-Dashboard-001
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from cortex.lens.dashboard_data_aggregator import (
    DashboardDataAggregator,
    RepositoryAnalysisResult,
    OverviewData,
    MetricsData,
    SecurityData,
    DependencyData,
)


@pytest.fixture
def aggregator():
    """Create aggregator instance."""
    return DashboardDataAggregator()


@pytest.fixture
def sample_fingerprint():
    """Create sample tech stack fingerprint."""
    from cortex.lens.capability_discovery import TechStackFingerprint
    return TechStackFingerprint(
        primary_language="Python",
        languages=["Python", "JavaScript", "TypeScript"],
        frameworks=["flask", "react"],
        has_database=True,
        database_types=["PostgreSQL"],
        has_api=True,
        api_types=["REST", "GraphQL"],
    )


class TestRepositoryAnalysisResult:
    """Test RepositoryAnalysisResult model."""
    
    def test_dagg_001_create_result_model(self):
        """DAGG-001: Create analysis result with all tabs."""
        result = RepositoryAnalysisResult(
            repository_name="test-repo",
            repository_path="/path/to/repo",
        )
        
        assert result.repository_name == "test-repo"
        # Tabs start as None until populated by aggregator
        assert result.overview is None
        assert result.metrics is None
        assert result.security is None
    
    def test_dagg_002_to_json(self):
        """DAGG-002: Convert result to JSON."""
        result = RepositoryAnalysisResult(
            repository_name="test-repo",
            repository_path="/path/to/repo",
        )
        
        json_data = result.to_json()
        assert isinstance(json_data, dict)
        assert "repository_name" in json_data
        assert "overview" in json_data
        assert "metrics" in json_data


class TestOverviewGeneration:
    """Test overview tab data generation."""
    
    def test_dagg_003_generate_overview(self, aggregator, sample_fingerprint):
        """DAGG-003: Generate overview tab data."""
        overview = aggregator.generate_overview(
            repo_path=Path("/test/repo"),
            fingerprint=sample_fingerprint,
        )
        
        assert overview is not None
        assert overview.total_files > 0
        assert overview.total_lines > 0
        assert len(overview.languages) > 0
    
    def test_dagg_004_overview_has_summary_stats(self, aggregator, sample_fingerprint):
        """DAGG-004: Overview includes summary statistics."""
        overview = aggregator.generate_overview(
            repo_path=Path("/test/repo"),
            fingerprint=sample_fingerprint,
        )
        
        assert hasattr(overview, 'total_commits')
        assert hasattr(overview, 'contributors')
        assert hasattr(overview, 'last_updated')


class TestMetricsGeneration:
    """Test metrics tab data generation."""
    
    def test_dagg_005_generate_metrics(self, aggregator):
        """DAGG-005: Generate metrics tab data."""
        metrics = aggregator.generate_metrics(Path("/test/repo"))
        
        assert metrics is not None
        assert metrics.code_quality is not None
        assert metrics.test_coverage is not None
    
    def test_dagg_006_metrics_time_series(self, aggregator):
        """DAGG-006: Metrics include time series data."""
        metrics = aggregator.generate_metrics(Path("/test/repo"))
        
        assert hasattr(metrics, 'coverage_trend')
        assert hasattr(metrics, 'complexity_trend')


class TestSecurityGeneration:
    """Test security tab data generation."""
    
    def test_dagg_007_generate_security(self, aggregator):
        """DAGG-007: Generate security tab data."""
        security = aggregator.generate_security(Path("/test/repo"))
        
        assert security is not None
        assert hasattr(security, 'vulnerabilities')
        assert hasattr(security, 'security_score')


class TestDependencyGeneration:
    """Test dependencies tab data generation."""
    
    def test_dagg_008_generate_dependencies(self, aggregator, sample_fingerprint):
        """DAGG-008: Generate dependencies tab data."""
        deps = aggregator.generate_dependencies(
            repo_path=Path("/test/repo"),
            fingerprint=sample_fingerprint,
        )
        
        assert deps is not None
        assert hasattr(deps, 'direct_dependencies')
        assert hasattr(deps, 'outdated_count')


class TestFullAggregation:
    """Test full dashboard data aggregation."""
    
    def test_dagg_009_aggregate_full_dashboard(self, aggregator, sample_fingerprint):
        """DAGG-009: Aggregate all tabs into single result."""
        result = aggregator.aggregate(
            repo_path=Path("/test/repo"),
            fingerprint=sample_fingerprint,
        )
        
        assert isinstance(result, RepositoryAnalysisResult)
        assert result.overview is not None
        assert result.metrics is not None
        assert result.security is not None
        assert result.dependencies is not None
    
    def test_dagg_010_write_json_file(self, aggregator, sample_fingerprint, tmp_path):
        """DAGG-010: Write dashboard JSON to file."""
        result = aggregator.aggregate(
            repo_path=Path("/test/repo"),
            fingerprint=sample_fingerprint,
        )
        
        output_file = tmp_path / "dashboard-data.json"
        aggregator.write_json(result, output_file)
        
        assert output_file.exists()
        import json
        data = json.loads(output_file.read_text())
        assert "repository_name" in data


# AC_COMPLETE: AC-CDF-Dashboard-001
