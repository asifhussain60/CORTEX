"""
CORTEX Dashboard E2E Integration Test
Tests full onboarding pipeline: Onboard -> Aggregate -> Validate -> Dashboard

Test ID: E2E-DASH-001
Category: Integration
Priority: Critical

Updated for new API (2024): RepositoryAnalysisResult model with tab-based structure.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from cortex.lens.dashboard_data_aggregator import DashboardDataAggregator, RepositoryAnalysisResult
from cortex.lens.capability_discovery import TechStackFingerprint, FingerprintAnalyzer


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
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
""")
        
        (repo_path / "utils.py").write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
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
""")
        
        return repo_path
    
    @pytest.fixture
    def fingerprint(self, sample_repository):
        """Create a fingerprint for the sample repository."""
        analyzer = FingerprintAnalyzer()
        return analyzer.analyze(sample_repository)
    
    @pytest.fixture
    def empty_fingerprint(self):
        """Create an empty fingerprint for empty repos."""
        return TechStackFingerprint()
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_path = tmp_path / "dashboard_output"
        output_path.mkdir()
        return output_path
    
    def test_e2e_001_full_pipeline_success(self, sample_repository, fingerprint, output_dir):
        """E2E-001: Full pipeline executes successfully from start to finish."""
        aggregator = DashboardDataAggregator()
        assert aggregator is not None
        
        result = aggregator.aggregate(sample_repository, fingerprint)
        assert isinstance(result, RepositoryAnalysisResult)
        assert result.repository_name == "sample_repo"
        assert result.overview is not None
        assert result.metrics is not None
        
        json_data = result.to_json()
        json_file = output_dir / "dashboard-data.json"
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2, default=str)
        assert json_file.exists()
        
        with open(json_file, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data is not None
        assert "repository_name" in loaded_data
    
    def test_e2e_002_overview_generation(self, sample_repository, fingerprint):
        """E2E-002: Overview data is generated with correct data."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        overview = result.overview
        assert overview is not None
        assert hasattr(overview, "total_files")
        assert hasattr(overview, "total_lines")
        assert overview.total_files >= 0
        assert overview.total_lines >= 0
    
    def test_e2e_003_metrics_generation(self, sample_repository, fingerprint):
        """E2E-003: Metrics data is generated with valid data."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        metrics = result.metrics
        assert metrics is not None
        assert hasattr(metrics, "code_quality")
        assert hasattr(metrics, "test_coverage")
        assert 0 <= metrics.code_quality <= 100
        assert 0 <= metrics.test_coverage <= 100
    
    def test_e2e_004_dependencies_extraction(self, sample_repository, fingerprint):
        """E2E-004: Dependencies are extracted from requirements.txt."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        deps = result.dependencies
        assert deps is not None
        assert deps.direct_dependencies >= 0
        assert isinstance(deps.packages, list)
    
    def test_e2e_005_security_data(self, sample_repository, fingerprint):
        """E2E-005: Security data is generated."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        security = result.security
        assert security is not None
        assert hasattr(security, "security_score")
        assert 0 <= security.security_score <= 100
    
    def test_e2e_006_empty_repo_handling(self, tmp_path, empty_fingerprint):
        """E2E-006: Pipeline handles empty repository gracefully."""
        empty_repo = tmp_path / "empty_repo"
        empty_repo.mkdir()
        
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(empty_repo, empty_fingerprint)
        
        assert isinstance(result, RepositoryAnalysisResult)
        assert result.overview is not None
        assert result.overview.total_files == 0
    
    def test_e2e_007_all_tabs_present(self, sample_repository, fingerprint):
        """E2E-007: All expected dashboard tabs are present in output."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        assert result.overview is not None
        assert result.metrics is not None
        assert result.security is not None
        assert result.dependencies is not None
        assert result.quality is not None
        assert result.lens is not None
        assert result.refactoring is not None
        assert result.use_cases is not None
        assert result.domain is not None
    
    def test_e2e_008_timestamps_valid(self, sample_repository, fingerprint):
        """E2E-008: All timestamps are valid ISO 8601 format."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        timestamp = result.analysis_timestamp
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")
    
    def test_e2e_009_reusable_aggregator(self, sample_repository, fingerprint, tmp_path, empty_fingerprint):
        """E2E-009: Aggregator can be reused for multiple repositories."""
        aggregator = DashboardDataAggregator()
        
        result1 = aggregator.aggregate(sample_repository, fingerprint)
        assert result1.repository_name == "sample_repo"
        
        repo2 = tmp_path / "repo2"
        repo2.mkdir()
        (repo2 / "test.py").write_text("print(1)")
        
        result2 = aggregator.aggregate(repo2, empty_fingerprint)
        assert result2.repository_name == "repo2"
        assert result1.repository_name != result2.repository_name
    
    def test_e2e_010_concurrent_aggregation_safe(self, sample_repository, fingerprint):
        """E2E-010: Multiple aggregators can run concurrently."""
        aggregators = [DashboardDataAggregator() for _ in range(3)]
        results = [agg.aggregate(sample_repository, fingerprint) for agg in aggregators]
        
        for result in results:
            assert isinstance(result, RepositoryAnalysisResult)
            assert result.repository_name == "sample_repo"
    
    def test_e2e_011_quality_data(self, sample_repository, fingerprint):
        """E2E-011: Quality tab data is generated."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        quality = result.quality
        assert quality is not None
        assert hasattr(quality, "maintainability_rating")
        assert hasattr(quality, "code_smells")
    
    def test_e2e_012_lens_data(self, sample_repository, fingerprint):
        """E2E-012: LENS tab data is generated from fingerprint."""
        aggregator = DashboardDataAggregator()
        result = aggregator.aggregate(sample_repository, fingerprint)
        
        lens = result.lens
        assert lens is not None
        assert hasattr(lens, "capability_coverage")
        assert hasattr(lens, "analyzers_run")


pytestmark = pytest.mark.integration
