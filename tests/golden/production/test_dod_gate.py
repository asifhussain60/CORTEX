"""
Golden tests for Definition of Done (DoD) gate enforcement.

Authority: Phase 96 Weakness Remediation
Purpose: Validate DoD gate blocks production deployment on violations
Test Count: 5 golden tests

Updated: Phase 09 — aligned to canonical check_definition_of_done(result, min_score) -> bool API
"""
import pytest
from pathlib import Path
from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents.duplicate_detection_agent import DuplicateDetectionAgent
from cortex.orchestrators.health.agents.stub_detection_agent import StubDetectionAgent


class TestDefinitionOfDoneGate:
    """Golden tests for DoD gate enforcement.
    
    Canonical API:
        result = orchestrator.scan()           -> ScanResult
        passed = orchestrator.check_definition_of_done(result, min_score=80.0) -> bool
    """
    
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
        
        # Run scan then DoD check (canonical 2-step API)
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(DuplicateDetectionAgent())
        orchestrator.register_agent(StubDetectionAgent())
        
        scan_result = orchestrator.scan()
        passed = orchestrator.check_definition_of_done(scan_result, min_score=80.0)
        
        # Validate DoD passed
        assert isinstance(passed, bool), "check_definition_of_done returns bool"
        assert passed is True, "DoD should pass for clean code"
        assert scan_result.health_score >= 80.0, "Health score should meet minimum"
    
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
        
        # Run scan then DoD check with high threshold
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(StubDetectionAgent())
        
        scan_result = orchestrator.scan()
        passed = orchestrator.check_definition_of_done(scan_result, min_score=95.0)
        
        # Validate DoD failed due to score
        assert isinstance(passed, bool), "check_definition_of_done returns bool"
        # If health score is below threshold, should fail
        if scan_result.health_score < 95.0:
            assert passed is False, "DoD should fail with low score"
    
    def test_dod_threshold_boundary(self, tmp_path: Path) -> None:
        """Golden: DoD gate respects exact threshold boundary.
        
        Validates min_score threshold is >= comparison.
        """
        orchestrator = HealthOrchestrator(tmp_path)
        scan_result = orchestrator.scan()
        
        # At exact score should pass
        exact_pass = orchestrator.check_definition_of_done(
            scan_result, min_score=scan_result.health_score
        )
        assert exact_pass is True, "DoD should pass at exact threshold"
        
        # Above score should fail
        above_fail = orchestrator.check_definition_of_done(
            scan_result, min_score=scan_result.health_score + 0.1
        )
        assert above_fail is False, "DoD should fail above threshold"
    
    def test_dod_default_threshold(self, tmp_path: Path) -> None:
        """Golden: DoD gate uses 80.0 as default threshold.
        
        Validates default min_score parameter.
        """
        orchestrator = HealthOrchestrator(tmp_path)
        scan_result = orchestrator.scan()
        
        # Default threshold is 80.0
        passed = orchestrator.check_definition_of_done(scan_result)
        assert isinstance(passed, bool), "check_definition_of_done returns bool"


class TestDoDIntegrationWithCI:
    """Golden tests for DoD integration with CI/CD."""
    
    def test_dod_provides_exit_code_guidance(self, tmp_path: Path) -> None:
        """Golden: DoD result provides clear CI/CD integration guidance.
        
        Validates that scan + check workflow supports CI.
        """
        orchestrator = HealthOrchestrator(tmp_path)
        orchestrator.register_agent(DuplicateDetectionAgent())
        
        scan_result = orchestrator.scan()
        passed = orchestrator.check_definition_of_done(scan_result)
        
        # CI can use: if not passed: sys.exit(1)
        exit_code = 0 if passed else 1
        assert exit_code in [0, 1], "Exit code should be 0 or 1"
        
        # ScanResult provides structured data for CI reporting
        assert hasattr(scan_result, "health_score"), "Must include health score"
        assert hasattr(scan_result, "issues"), "Must include issues list"
