"""Integration Tests for Health Agent Architecture

Tests all agents working together to detect issues.
Validates health score calculation and report generation.

Author: CORTEX Framework
Phase: PHASE-95
"""

import tempfile
from pathlib import Path

import pytest

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents import (
    DuplicateDetectionAgent,
    StubDetectionAgent,
    PathIntegrityAgent,
    VersionCleanupAgent,
    TestCoverageAgent,
    RegistryConsistencyAgent,
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        
        # Create basic structure
        (workspace / "cortex").mkdir()
        (workspace / "tests").mkdir()
        (workspace / "cortex-registry").mkdir()
        
        yield workspace


@pytest.fixture
def health_orchestrator(temp_workspace):
    """Create health orchestrator with all agents."""
    orchestrator = HealthOrchestrator(temp_workspace)
    
    # Register all agents
    orchestrator.register_agent(DuplicateDetectionAgent())
    orchestrator.register_agent(StubDetectionAgent())
    orchestrator.register_agent(PathIntegrityAgent())
    orchestrator.register_agent(VersionCleanupAgent())
    orchestrator.register_agent(TestCoverageAgent())
    orchestrator.register_agent(RegistryConsistencyAgent())
    
    return orchestrator


def test_integration_clean_workspace(health_orchestrator, temp_workspace):
    """Test health check on clean workspace."""
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should have no issues
    assert result.metrics.health_score == 100.0
    assert result.metrics.total_issues == 0
    assert len(result.agent_results) == 6


def test_integration_with_duplicates(health_orchestrator, temp_workspace):
    """Test detection of duplicate files."""
    # Create duplicate files
    file1 = temp_workspace / "cortex" / "test.py"
    file2 = temp_workspace / "cortex" / "brain" / "test.py"
    
    (temp_workspace / "cortex" / "brain").mkdir(parents=True)
    
    content = "def test(): pass"
    file1.write_text(content)
    file2.write_text(content)
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should detect duplicate
    assert result.metrics.total_issues > 0
    assert result.metrics.health_score < 100.0
    
    # Verify duplicate issue exists
    duplicate_issues = [
        issue for issue in result.all_issues
        if issue.category.value == "duplicate"
    ]
    assert len(duplicate_issues) > 0


def test_integration_with_stub(health_orchestrator, temp_workspace):
    """Test detection of stub files."""
    # Create stub file
    stub_file = temp_workspace / "cortex" / "stub.py"
    stub_file.write_text("import sys\nfrom pathlib import Path")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should detect stub
    assert result.metrics.total_issues > 0
    
    # Verify stub issue exists
    stub_issues = [
        issue for issue in result.all_issues
        if issue.category.value == "stub"
    ]
    assert len(stub_issues) > 0


def test_integration_with_version_artifacts(health_orchestrator, temp_workspace):
    """Test detection of version artifacts."""
    # Create versioned file
    versioned_file = temp_workspace / "cortex" / "test_v1.0.py"
    versioned_file.write_text("def test(): pass")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should detect version issue
    assert result.metrics.total_issues > 0
    
    # Verify version issue exists
    version_issues = [
        issue for issue in result.all_issues
        if issue.category.value == "version_artifact"
    ]
    assert len(version_issues) > 0


def test_integration_with_missing_tests(health_orchestrator, temp_workspace):
    """Test detection of missing test coverage."""
    # Create file without tests
    source_file = temp_workspace / "cortex" / "untested.py"
    source_file.write_text("def important_function(): pass")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should detect missing test
    assert result.metrics.total_issues > 0
    
    # Verify test issue exists
    test_issues = [
        issue for issue in result.all_issues
        if issue.category.value == "missing_test"
    ]
    assert len(test_issues) > 0


def test_integration_with_misplaced_yaml(health_orchestrator, temp_workspace):
    """Test detection of YAML files outside registry."""
    # Create YAML outside registry
    yaml_file = temp_workspace / "cortex" / "config.yaml"
    yaml_file.write_text("orchestrator:\n  name: test")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should detect registry issue
    assert result.metrics.total_issues > 0
    
    # Verify registry issue exists
    registry_issues = [
        issue for issue in result.all_issues
        if issue.category.value == "config_misplaced"
    ]
    assert len(registry_issues) > 0


def test_integration_health_score_calculation(health_orchestrator, temp_workspace):
    """Test health score calculation with multiple issues."""
    # Create multiple issues of different severities
    
    # Critical: Duplicate files
    file1 = temp_workspace / "cortex" / "dup.py"
    file2 = temp_workspace / "cortex" / "brain" / "dup.py"
    (temp_workspace / "cortex" / "brain").mkdir(parents=True)
    file1.write_text("content")
    file2.write_text("content")
    
    # High: Stub file
    stub = temp_workspace / "cortex" / "stub.py"
    stub.write_text("import sys")
    
    # Medium: Version artifact
    versioned = temp_workspace / "cortex" / "test_v1.py"
    versioned.write_text("def test(): pass")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should have reduced health score
    assert result.metrics.health_score < 100.0
    
    # Score should reflect severity weights
    expected_deduction = (
        result.metrics.critical_issues * 20 +
        result.metrics.high_issues * 10 +
        result.metrics.medium_issues * 5 +
        result.metrics.low_issues * 2
    )
    expected_score = max(0, 100 - expected_deduction)
    assert result.metrics.health_score == expected_score


def test_integration_summary_generation(health_orchestrator, temp_workspace):
    """Test summary generation."""
    # Create some issues
    stub = temp_workspace / "cortex" / "stub.py"
    stub.write_text("import sys")
    
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Get summary
    summary = health_orchestrator.get_summary()
    
    # Should include workspace root
    assert "workspace_root" in summary
    
    # Should include agent count
    assert summary["agents_registered"] == 6
    
    # Should include agent names
    assert len(summary["agent_names"]) == 6


def test_integration_report_generation(health_orchestrator, temp_workspace):
    """Test report generation and markdown export."""
    # Create issues
    stub = temp_workspace / "cortex" / "stub.py"
    stub.write_text("import sys")
    
    # Run health check
    report = health_orchestrator.run_health_check()
    
    # Generate recommendations
    recommendations = report.generate_recommendations()
    assert len(recommendations) > 0
    
    # Export to markdown
    markdown = report.to_markdown()
    
    # Should contain report sections
    assert "Health Score" in markdown
    assert "Metrics Summary" in markdown
    assert "Recommendations" in markdown


def test_integration_agent_execution_order(health_orchestrator, temp_workspace):
    """Test that agents execute in registration order."""
    # Run health check
    result = health_orchestrator.run_health_check()
    
    # Should have results from all agents
    assert len(result.agent_results) == 6
    
    # Verify agent names in results
    agent_names = [r.agent_name for r in result.agent_results]
    expected_names = [
        "DuplicateDetectionAgent",
        "StubDetectionAgent",
        "PathIntegrityAgent",
        "VersionCleanupAgent",
        "TestCoverageAgent",
        "RegistryConsistencyAgent",
    ]
    
    assert agent_names == expected_names


def test_integration_error_recovery(health_orchestrator, temp_workspace):
    """Test error recovery when agent fails."""
    # Create file that might cause parsing errors
    bad_file = temp_workspace / "cortex" / "bad.py"
    bad_file.write_text("def incomplete(")  # Syntax error
    
    # Run health check - should not crash
    result = health_orchestrator.run_health_check()
    
    # Should still complete and have results
    assert len(result.agent_results) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
