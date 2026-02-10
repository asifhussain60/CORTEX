"""
Integration Tests for MCP API Endpoints (Phase 21)
===================================================

Comprehensive test suite for all MCP tools and API endpoints.

Test Coverage:
- Repository Onboarding v3 (cortex_onboard_repository_v3)
- Schema Enhancement Check
- LENS Analysis
- LLM Business Language Generation
- SQLite Aggregation
- Registry Management
- Dashboard Validation
- Data Format Conversion
- Error Handling
- Performance Benchmarks

AC-ID: AC-P21-API-TESTS-001
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time

from cortex.mcp.tools.repository_onboarding_v3_tool import (
    cortex_onboard_repository_v3,
    _check_schema_enhancement,
    _run_lens_analysis,
    _generate_business_language,
    _aggregate_to_sqlite,
    _update_registry,
    _validate_dashboard,
)

# Check if SQLite data generator is available
try:
    from cortex.visualization.sqlite_data_generator import SQLiteDataGenerator
    SQLITE_GENERATOR_AVAILABLE = True
except ImportError:
    SQLITE_GENERATOR_AVAILABLE = False

# Skip marker for tests requiring SQLite generator
requires_sqlite_generator = pytest.mark.skipif(
    not SQLITE_GENERATOR_AVAILABLE,
    reason="SQLite data generator not implemented (cortex.visualization.sqlite_data_generator)"
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_workspace():
    """Create temporary workspace."""
    workspace = Path(tempfile.mkdtemp(prefix="cortex_api_test_"))
    yield workspace
    shutil.rmtree(workspace, ignore_errors=True)


@pytest.fixture
def sample_repo(temp_workspace):
    """Create sample repository."""
    repo_dir = temp_workspace / "test_repo"
    repo_dir.mkdir(parents=True)
    
    # Python files
    (repo_dir / "main.py").write_text("""
def main():
    \"\"\"Main entry point.\"\"\"
    print("Hello World")
    
if __name__ == "__main__":
    main()
""")
    
    (repo_dir / "utils.py").write_text("""
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
""")
    
    # README
    (repo_dir / "README.md").write_text("# Test Repository\nTest repository for API tests")
    
    return repo_dir


@pytest.fixture
def output_dir(temp_workspace):
    """Create output directory."""
    output = temp_workspace / "output"
    output.mkdir(parents=True)
    return output


# ============================================================================
# ENDPOINT: cortex_onboard_repository_v3
# ============================================================================

@requires_sqlite_generator
def test_api_onboard_repository_complete(sample_repo, output_dir):
    """Test complete repository onboarding via API."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="test_repo",
        generate_business_language=True,
        update_registry=False,
        validate=True,
    )
    
    assert result["success"] is True
    assert result["slug"] == "test_repo"
    assert "dashboard_path" in result
    assert "metadata_path" in result
    assert "stats" in result
    assert "validation_results" in result
    assert "elapsed_seconds" in result
    
    # Verify files created
    assert Path(result["dashboard_path"]).exists()
    assert Path(result["metadata_path"]).exists()
    
    # Verify stats
    assert result["stats"]["repo_summary"] == 1
    assert result["stats"]["metrics_summary"] == 1
    assert result["stats"]["use_cases"] >= 1


@requires_sqlite_generator
def test_api_onboard_repository_minimal(sample_repo, output_dir):
    """Test minimal onboarding (no LLM, no registry, no validation)."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="test_minimal",
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    assert result["success"] is True
    assert result["registry_updated"] is False


def test_api_onboard_repository_invalid_path(output_dir):
    """Test onboarding with invalid repository path."""
    result = cortex_onboard_repository_v3(
        repo_path="/nonexistent/path",
        output_dir=str(output_dir),
        slug="invalid",
    )
    
    assert result["success"] is False
    assert "error" in result


@requires_sqlite_generator
def test_api_onboard_repository_auto_slug(sample_repo, output_dir):
    """Test onboarding with auto-generated slug."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug=None,  # Auto-generate
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    assert result["success"] is True
    assert result["slug"] == "test_repo"  # From directory name


@requires_sqlite_generator
def test_api_onboard_repository_performance(sample_repo, output_dir):
    """Test onboarding performance."""
    start_time = time.time()
    
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="perf_test",
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    elapsed = time.time() - start_time
    
    assert result["success"] is True
    assert elapsed < 10.0  # Should complete in < 10 seconds for small repo
    assert result["elapsed_seconds"] > 0


# ============================================================================
# ENDPOINT: _check_schema_enhancement
# ============================================================================

def test_api_schema_check_valid():
    """Test schema enhancement check with valid schema."""
    result = _check_schema_enhancement()
    
    assert result["valid"] is True
    assert result["missing_models"] == []


def test_api_schema_check_structure():
    """Test schema check return structure."""
    result = _check_schema_enhancement()
    
    assert "valid" in result
    assert "missing_models" in result
    assert isinstance(result["valid"], bool)
    assert isinstance(result["missing_models"], list)


# ============================================================================
# ENDPOINT: _run_lens_analysis
# ============================================================================

def test_api_lens_analysis_basic(sample_repo):
    """Test LENS analysis on basic repository."""
    result = _run_lens_analysis(sample_repo)
    
    assert result["success"] is True
    assert "data" in result
    assert "files_analyzed" in result["data"]
    assert result["data"]["files_analyzed"] >= 2  # main.py, utils.py


def test_api_lens_analysis_structure(sample_repo):
    """Test LENS analysis return structure."""
    result = _run_lens_analysis(sample_repo)
    
    assert result["success"] is True
    data = result["data"]
    
    assert "files_analyzed" in data
    assert "total_vulnerabilities" in data
    assert "vulnerabilities" in data
    assert "holistic_context" in data
    
    assert isinstance(data["files_analyzed"], int)
    assert isinstance(data["total_vulnerabilities"], int)
    assert isinstance(data["vulnerabilities"], dict)


def test_api_lens_analysis_invalid_path():
    """Test LENS analysis with invalid path."""
    result = _run_lens_analysis(Path("/nonexistent"))
    
    # Should handle gracefully
    assert "success" in result
    if not result["success"]:
        assert "error" in result


# ============================================================================
# ENDPOINT: _generate_business_language
# ============================================================================

def test_api_llm_generation_basic(sample_repo):
    """Test LLM business language generation."""
    lens_data = {
        "files_analyzed": 3,
        "total_vulnerabilities": 0,
        "holistic_context": {},
    }
    
    result = _generate_business_language(lens_data, sample_repo)
    
    assert result["success"] is True
    assert "data" in result
    assert "use_cases" in result["data"]
    assert len(result["data"]["use_cases"]) > 0


def test_api_llm_generation_structure(sample_repo):
    """Test LLM generation return structure."""
    lens_data = {"files_analyzed": 5}
    
    result = _generate_business_language(lens_data, sample_repo)
    
    assert result["success"] is True
    data = result["data"]
    
    assert "use_cases" in data
    assert isinstance(data["use_cases"], list)
    
    if len(data["use_cases"]) > 0:
        use_case = data["use_cases"][0]
        assert "title" in use_case
        assert "category" in use_case
        assert "business_value" in use_case


# ============================================================================
# ENDPOINT: _aggregate_to_sqlite
# ============================================================================

@requires_sqlite_generator
def test_api_sqlite_aggregation_complete(sample_repo, output_dir):
    """Test SQLite aggregation with complete data."""
    lens_data = {
        "files_analyzed": 2,
        "total_vulnerabilities": 0,
        "vulnerabilities": {"p0_risks": [], "p1_risks": [], "p2_risks": []},
        "holistic_context": {"code_analysis": {"total_lines": 20}},
    }
    
    llm_data = {
        "use_cases": [{
            "title": "Test Use Case",
            "category": "Testing",
            "business_value": "Test value",
            "user_stories": [],
            "acceptance_criteria": [],
            "priority": "medium",
            "status": "planned",
            "related_files": [],
        }]
    }
    
    dashboard_path = output_dir / "dashboard.sqlite"
    
    result = _aggregate_to_sqlite(
        lens_data=lens_data,
        llm_data=llm_data,
        repo_path=sample_repo,
        dashboard_path=dashboard_path,
        slug="test",
    )
    
    assert result["success"] is True
    assert "stats" in result
    assert dashboard_path.exists()


@requires_sqlite_generator
def test_api_sqlite_aggregation_minimal(sample_repo, output_dir):
    """Test SQLite aggregation with minimal data."""
    lens_data = {
        "files_analyzed": 1,
        "total_vulnerabilities": 0,
        "vulnerabilities": {},
        "holistic_context": {},
    }
    
    dashboard_path = output_dir / "minimal.sqlite"
    
    result = _aggregate_to_sqlite(
        lens_data=lens_data,
        llm_data=None,  # No LLM data
        repo_path=sample_repo,
        dashboard_path=dashboard_path,
        slug="minimal",
    )
    
    assert result["success"] is True
    assert dashboard_path.exists()


# ============================================================================
# ENDPOINT: _validate_dashboard
# ============================================================================

@requires_sqlite_generator
def test_api_dashboard_validation_valid(output_dir):
    """Test dashboard validation with valid database."""
    from cortex.visualization.sqlite_data_generator import SQLiteDataGenerator
    from cortex.models.dashboard_schema_v3 import RepoSummary, MetricsSummary
    
    dashboard_path = output_dir / "valid.sqlite"
    
    # Generate valid database
    dashboard_data = {
        "repo_summary": RepoSummary(
            id=1,
            repo_name="Test",
            repo_slug="test",
            description="Test",
            primary_language="Python",
            tech_stack=["Python"],
            total_loc=100,
            file_count=5,
            contributor_count=1,
            health_score=80,
            last_commit_date=datetime.now(),
        ).model_dump(),
        "metrics_summary": MetricsSummary(
            id=1,
            total_loc=100,
            code_loc=80,
            comment_loc=20,
            avg_complexity=3.0,
            max_complexity=10,
            maintainability_index=75.0,
            technical_debt_hours=5,
        ).model_dump(),
        "use_cases": [],
        "vulnerabilities": [],
        "packages": [],
        "code_smells": [],
        "entities": [],
        "relationships": [],
        "components": [],
        "files": [],
        "test_results": [],
        "lens_insights": [],
        "refactoring_suggestions": [],
    }
    
    generator = SQLiteDataGenerator()
    generator.generate(output_path=dashboard_path, data=dashboard_data)
    
    # Validate
    result = _validate_dashboard(dashboard_path)
    
    assert result["database_valid"] is True
    assert len(result["tables_present"]) > 10
    assert len(result["missing_tables"]) <= 1  # refactoring_suggestions optional
    assert result["fts_functional"] is True
    assert result["views_functional"] is True
    assert len(result["foreign_key_violations"]) == 0


def test_api_dashboard_validation_missing():
    """Test validation with missing database file."""
    result = _validate_dashboard(Path("/nonexistent/dashboard.sqlite"))
    
    assert result["database_valid"] is False
    assert "error" in result


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_api_error_handling_empty_output_dir(sample_repo):
    """Test error handling with empty output directory string."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir="",
        slug="test",
    )
    
    # Should handle gracefully
    assert "success" in result


@requires_sqlite_generator
def test_api_error_handling_special_characters(sample_repo, output_dir):
    """Test error handling with special characters in slug."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="test-repo-123_special",
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    assert result["success"] is True
    assert result["slug"] == "test-repo-123_special"


# ============================================================================
# DATA FORMAT TESTS
# ============================================================================

@requires_sqlite_generator
def test_api_metadata_json_format(sample_repo, output_dir):
    """Test metadata.json format."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="format_test",
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    assert result["success"] is True
    
    # Read and validate metadata.json
    metadata_path = Path(result["metadata_path"])
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    assert "slug" in metadata
    assert "repo_path" in metadata
    assert "generated_at" in metadata
    assert "lens_analysis" in metadata
    assert "stats" in metadata
    
    # Validate ISO 8601 timestamp
    datetime.fromisoformat(metadata["generated_at"])


@requires_sqlite_generator
def test_api_stats_structure(sample_repo, output_dir):
    """Test stats dictionary structure."""
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="stats_test",
        generate_business_language=False,
        update_registry=False,
        validate=False,
    )
    
    assert result["success"] is True
    stats = result["stats"]
    
    # Required stat keys
    required_keys = [
        "repo_summary",
        "use_cases",
        "metrics_summary",
        "vulnerabilities",
        "packages",
        "code_smells",
    ]
    
    for key in required_keys:
        assert key in stats
        assert isinstance(stats[key], int)
        assert stats[key] >= 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@requires_sqlite_generator
def test_api_full_pipeline_integration(sample_repo, output_dir):
    """Test complete pipeline integration."""
    # Step 1: Onboard repository
    result = cortex_onboard_repository_v3(
        repo_path=str(sample_repo),
        output_dir=str(output_dir),
        slug="integration_test",
        generate_business_language=True,
        update_registry=False,
        validate=True,
    )
    
    assert result["success"] is True
    
    # Step 2: Verify dashboard.sqlite
    dashboard_path = Path(result["dashboard_path"])
    assert dashboard_path.exists()
    assert dashboard_path.stat().st_size > 1000  # Non-empty
    
    # Step 3: Verify metadata.json
    metadata_path = Path(result["metadata_path"])
    assert metadata_path.exists()
    
    # Step 4: Verify validation results
    validation = result["validation_results"]
    assert validation["database_valid"] is True
    assert validation["fts_functional"] is True
    assert validation["views_functional"] is True


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@requires_sqlite_generator
def test_api_performance_large_dataset(output_dir):
    """Test performance with large dataset."""
    # Create large test dataset
    lens_data = {
        "files_analyzed": 1000,
        "total_vulnerabilities": 50,
        "vulnerabilities": {
            "p0_risks": [{"package_name": f"pkg{i}", "package_version": "1.0"} for i in range(10)],
            "p1_risks": [{"package_name": f"pkg{i}", "package_version": "1.0"} for i in range(20)],
            "p2_risks": [{"package_name": f"pkg{i}", "package_version": "1.0"} for i in range(20)],
        },
        "holistic_context": {"code_analysis": {"total_lines": 50000}},
    }
    
    llm_data = {
        "use_cases": [
            {
                "title": f"Use Case {i}",
                "category": "Testing",
                "business_value": "Value",
                "user_stories": [],
                "acceptance_criteria": [],
                "priority": "medium",
                "status": "planned",
                "related_files": [],
            }
            for i in range(100)
        ]
    }
    
    dashboard_path = output_dir / "large.sqlite"
    
    start_time = time.time()
    result = _aggregate_to_sqlite(
        lens_data=lens_data,
        llm_data=llm_data,
        repo_path=Path("."),
        dashboard_path=dashboard_path,
        slug="large",
    )
    elapsed = time.time() - start_time
    
    assert result["success"] is True
    assert elapsed < 5.0  # Should complete in < 5 seconds
    assert result["stats"]["use_cases"] == 100
    assert result["stats"]["vulnerabilities"] == 50


# ============================================================================
# CONCURRENCY TESTS
# ============================================================================

@requires_sqlite_generator
def test_api_concurrent_onboarding(sample_repo, temp_workspace):
    """Test concurrent onboarding operations."""
    import concurrent.futures
    
    def onboard_with_slug(slug):
        output = temp_workspace / slug
        output.mkdir(parents=True)
        return cortex_onboard_repository_v3(
            repo_path=str(sample_repo),
            output_dir=str(output),
            slug=slug,
            generate_business_language=False,
            update_registry=False,
            validate=False,
        )
    
    slugs = [f"concurrent_{i}" for i in range(3)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(onboard_with_slug, slug) for slug in slugs]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All should succeed
    for result in results:
        assert result["success"] is True
