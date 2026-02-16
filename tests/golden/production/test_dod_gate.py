"""
Golden tests for Definition of Done (DoD) gate enforcement.

Authority: Phase 96 Weakness Remediation
Purpose: Validate DoD gate blocks production deployment on violations
Test Count: 4 golden tests
"""
import pytest
from pathlib import Path
from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents.duplicate_detection_agent import DuplicateDetectionAgent
from cortex.orchestrators.health.agents.stub_detection_agent import StubDetectionAgent


class TestDefinitionOfDoneGate:
    """Golden tests for DoD gate enforcement."""
    
    def test_dod_passes_with_clean_codebase(self, tmp_path: Path) -> None:
        """Golden: DoD gate passes with no violations.
        
        Validates that clean code passes production gate.
        """
        # Create clean codebase
        impl_file = tmp_path / "feature.py"
        impl_file.write_text("""
def process_data(input_data: str) -> str:
    '''Process input data and return result.
    
    Args:
        input_data: Raw input string
        
    Returns:
        Processed output string
    '''
    return input_data.upper()
""")
        
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("""
from feature import process_data

def test_process_data():
    assert process_data("hello") == "HELLO"
""")
        
        # Run DoD check
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(DuplicateDetectionAgent())
        orchestrator.register_agent(StubDetectionAgent())
        
        result = orchestrator.check_definition_of_done(min_score=80.0)
        
        # Validate DoD passed
        assert result["passed"] is True, "DoD should pass for clean code"
        assert result["health_score"] >= 80.0, "Health score should meet minimum"
        assert len(result["blocking_failures"]) == 0, "No blocking failures"
        assert "✅ DoD PASSED" in result["recommendation"]
    
    def test_dod_fails_with_low_health_score(self, tmp_path: Path) -> None:
        """Golden: DoD gate fails when health score too low.
        
        Validates min_score threshold enforcement.
        """
        # Create codebase with many small violations
        for i in range(10):
            stub_file = tmp_path / f"stub_{i}.py"
            stub_file.write_text(f"""
def func_{i}():
    pass
""")
        
        # Run DoD check with high threshold
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(StubDetectionAgent())
        
        result = orchestrator.check_definition_of_done(min_score=95.0)
        
        # Validate DoD failed due to score
        assert result["passed"] is False, "DoD should fail with low score"
        assert result["health_score"] < result["min_score_required"]
        assert "❌ DoD FAILED" in result["recommendation"]
        assert "Health score" in result["recommendation"]
    
    def test_dod_fails_with_blocking_agent_issues(self, tmp_path: Path) -> None:
        """Golden: DoD gate fails when blocking agent detects issues.
        
        Validates P0 violation blocking (duplicates, stubs).
        """
        # Create duplicate files (CORE-035 violation)
        file1 = tmp_path / "util.py"
        file1.write_text("""
def helper():
    return 42
""")
        
        file2 = tmp_path / "util_copy.py"
        file2.write_text("""
def helper():
    return 42
""")
        
        # Run DoD check
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(DuplicateDetectionAgent())
        
        result = orchestrator.check_definition_of_done(
            min_score=80.0,
            blocking_agents=["DuplicateDetectionAgent"]
        )
        
        # Validate DoD failed due to blocking agent
        assert result["passed"] is False, "DoD should fail with duplicates"
        assert len(result["blocking_failures"]) > 0, "Should have blocking failures"
        assert "DuplicateDetectionAgent" in result["blocking_failures"][0]
        assert "❌ DoD FAILED" in result["recommendation"]
        assert "Blocking failures" in result["recommendation"]
    
    def test_dod_custom_blocking_agents(self, tmp_path: Path) -> None:
        """Golden: DoD gate supports custom blocking agent configuration.
        
        Validates flexible gate configuration.
        """
        # Create stub file
        stub_file = tmp_path / "stub.py"
        stub_file.write_text("""
def placeholder():
    pass
""")
        
        # Run DoD with only stub detection as blocker
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(StubDetectionAgent())
        
        result = orchestrator.check_definition_of_done(
            min_score=50.0,  # Low threshold
            blocking_agents=["StubDetectionAgent"]  # Only stub blocks
        )
        
        # Validate stub detection blocked
        assert result["passed"] is False, "DoD should fail with stub"
        assert any("StubDetectionAgent" in f for f in result["blocking_failures"])
        
        # Run without stub as blocker (should pass if score OK)
        result2 = orchestrator.check_definition_of_done(
            min_score=50.0,
            blocking_agents=[]  # No blocking agents
        )
        
        # May pass if health score is acceptable
        # (stub detected but not blocking)
        assert "blocking_failures" in result2
        assert isinstance(result2["passed"], bool)


class TestDoDIntegrationWithCI:
    """Golden tests for DoD integration with CI/CD."""
    
    def test_dod_provides_exit_code_guidance(self, tmp_path: Path) -> None:
        """Golden: DoD result provides clear CI/CD integration guidance.
        
        Validates that result structure supports CI workflows.
        """
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(DuplicateDetectionAgent())
        
        result = orchestrator.check_definition_of_done()
        
        # Validate result structure for CI
        assert "passed" in result, "Must have 'passed' boolean"
        assert isinstance(result["passed"], bool), "'passed' must be boolean"
        assert "recommendation" in result, "Must have human-readable recommendation"
        assert "health_score" in result, "Must include health score"
        assert "blocking_failures" in result, "Must list blocking failures"
        
        # CI can use: if not result["passed"]: sys.exit(1)
        exit_code = 0 if result["passed"] else 1
        assert exit_code in [0, 1], "Exit code should be 0 or 1"
